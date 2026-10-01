"""Tests for the OTA canary lab. Plain asserts, no pytest.

Run: /usr/bin/python3 test_ota.py
"""

import os
import tempfile

from gate import (
    ArmCounts,
    Decision,
    GateConfig,
    evaluate,
    evaluate_cohort,
    merge_cohorts,
    two_proportion_z,
    wilson_interval,
)
from registry import (
    DuplicateVersionError,
    IllegalTransitionError,
    ModelRegistry,
    Stage,
    UnknownVersionError,
)
from rollout import (
    BAD_MODEL,
    GOOD_MODEL,
    demo_cohort_masking,
    run_rollout,
)


def _quiet(_msg: str) -> None:
    """Silent logger for rollout runs inside tests."""


# ----------------------------------------------------------------------
# registry.py
# ----------------------------------------------------------------------


def test_registry_happy_path_and_lineage() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        path = os.path.join(tmp, "reg.jsonl")
        reg = ModelRegistry(path)
        reg.register("v1", "manifest-a", None)
        assert reg.get("v1").stage is Stage.STAGED
        assert reg.promote("v1") is Stage.CANARY_1PCT
        assert reg.promote("v1") is Stage.CANARY_10PCT
        assert reg.promote("v1") is Stage.FLEET
        assert reg.current_fleet_version() == "v1"

        reg.register("v2", "manifest-b", parent_version="v1")
        assert reg.lineage("v2") == ["v2", "v1"]
        assert reg.get("v2").train_manifest_id == "manifest-b"

        # Persistence: replaying the JSONL reproduces identical state.
        reg2 = ModelRegistry(path)
        assert reg2.get("v1").stage is Stage.FLEET
        assert reg2.get("v2").stage is Stage.STAGED
        assert reg2.lineage("v2") == ["v2", "v1"]
        assert len(reg2.get("v1").history) == 3


def test_registry_illegal_transitions_raise() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        reg = ModelRegistry(os.path.join(tmp, "reg.jsonl"))
        reg.register("v1", "manifest-a", None)

        # Rollback from staged: nothing is deployed -> illegal.
        try:
            reg.rollback("v1", "nope")
            assert False, "expected IllegalTransitionError"
        except IllegalTransitionError:
            pass

        # Promote past fleet -> illegal.
        reg.promote("v1")
        reg.promote("v1")
        reg.promote("v1")
        try:
            reg.promote("v1")
            assert False, "expected IllegalTransitionError"
        except IllegalTransitionError:
            pass

        # rolled_back is terminal: no promote, no second rollback.
        reg.rollback("v1", "post-mortem: bad release")
        assert reg.get("v1").stage is Stage.ROLLED_BACK
        try:
            reg.promote("v1")
            assert False, "expected IllegalTransitionError"
        except IllegalTransitionError:
            pass
        try:
            reg.rollback("v1", "again")
            assert False, "expected IllegalTransitionError"
        except IllegalTransitionError:
            pass

        # Duplicate register / unknown version / unknown parent.
        try:
            reg.register("v1", "manifest-x", None)
            assert False, "expected DuplicateVersionError"
        except DuplicateVersionError:
            pass
        try:
            reg.promote("ghost")
            assert False, "expected UnknownVersionError"
        except UnknownVersionError:
            pass
        try:
            reg.register("v2", "manifest-b", parent_version="ghost")
            assert False, "expected UnknownVersionError"
        except UnknownVersionError:
            pass

        # Rollback must carry a reason.
        reg.register("v3", "manifest-c", None)
        reg.promote("v3")
        try:
            reg.rollback("v3", "")
            assert False, "expected ValueError"
        except ValueError:
            pass


# ----------------------------------------------------------------------
# gate.py
# ----------------------------------------------------------------------


def test_wilson_interval_sanity() -> None:
    low, high = wilson_interval(85, 100)
    assert 0.0 <= low < 0.85 < high <= 1.0
    # Tighter with more data.
    low2, high2 = wilson_interval(850, 1000)
    assert (high2 - low2) < (high - low)
    # Sane at the edges (Wald would collapse to a zero-width interval).
    low0, high0 = wilson_interval(0, 20)
    assert low0 == 0.0 and high0 > 0.0
    lowN, highN = wilson_interval(20, 20)
    assert highN == 1.0 and lowN < 1.0
    try:
        wilson_interval(1, 0)
        assert False, "expected ValueError"
    except ValueError:
        pass


def test_two_proportion_z_signs() -> None:
    better = two_proportion_z(ArmCounts(90, 100), ArmCounts(80, 100))
    worse = two_proportion_z(ArmCounts(80, 100), ArmCounts(90, 100))
    assert better > 0 and worse < 0
    assert abs(better + worse) < 1e-12  # antisymmetric
    # Degenerate pooled rate -> "no evidence", not a crash.
    assert two_proportion_z(ArmCounts(100, 100), ArmCounts(100, 100)) == 0.0


def test_arm_counts_validation() -> None:
    try:
        ArmCounts(successes=5, trials=3)
        assert False, "expected ValueError"
    except ValueError:
        pass
    try:
        ArmCounts(successes=-1, trials=3)
        assert False, "expected ValueError"
    except ValueError:
        pass


def test_gate_insufficient_samples_holds() -> None:
    config = GateConfig(min_trials_per_arm=200)
    # 50 trials of catastrophic regression: still HOLD, never a verdict on noise.
    verdict = evaluate_cohort(
        "carpet", ArmCounts(10, 50), ArmCounts(45, 50), config
    )
    assert verdict.decision is Decision.HOLD
    assert "insufficient" in verdict.reason
    # Same rates with real sample size -> ROLLBACK.
    verdict2 = evaluate_cohort(
        "carpet", ArmCounts(200, 1000), ArmCounts(900, 1000), config
    )
    assert verdict2.decision is Decision.ROLLBACK


def test_gate_promote_hold_rollback() -> None:
    config = GateConfig()
    # Clearly better -> promote.
    up = evaluate_cohort(
        "hardwood", ArmCounts(930, 1000), ArmCounts(900, 1000), config
    )
    assert up.decision is Decision.PROMOTE
    # Clearly worse -> rollback.
    down = evaluate_cohort(
        "carpet", ArmCounts(550, 1000), ArmCounts(700, 1000), config
    )
    assert down.decision is Decision.ROLLBACK
    # Slightly worse, inconclusive at this n -> hold, keep observing.
    mid = evaluate_cohort(
        "carpet", ArmCounts(158, 250), ArmCounts(175, 250), config
    )
    assert mid.decision is Decision.HOLD
    assert "insufficient" not in mid.reason
    # Empty input must not silently promote.
    try:
        evaluate({}, config)
        assert False, "expected ValueError"
    except ValueError:
        pass


def test_gate_cohort_masking_deterministic_counts() -> None:
    """Aggregate flat -> aggregate gate promotes; carpet cohort -> rollback."""
    config = GateConfig()
    cohorts = {
        "hardwood": (ArmCounts(1667, 1800), ArmCounts(1620, 1800)),  # +2.6pp
        "carpet": (ArmCounts(372, 600), ArmCounts(420, 600)),        # -8pp
    }
    agg_canary, agg_control = merge_cohorts(cohorts)
    assert agg_canary.trials == 2400 and agg_control.trials == 2400
    aggregate = evaluate({"all": (agg_canary, agg_control)}, config)
    assert aggregate.decision is Decision.PROMOTE  # the trap
    sliced = evaluate(cohorts, config)
    assert sliced.decision is Decision.ROLLBACK
    assert sliced.verdict_for("carpet").decision is Decision.ROLLBACK
    assert sliced.verdict_for("hardwood").decision is Decision.PROMOTE


# ----------------------------------------------------------------------
# rollout.py -- the three scenarios, end to end
# ----------------------------------------------------------------------


def test_scenario_good_model_reaches_fleet() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        reg = ModelRegistry(os.path.join(tmp, "reg.jsonl"))
        result = run_rollout(
            GOOD_MODEL, reg, "v-good", "manifest-good", None,
            seed=11, log=_quiet,
        )
        assert result.terminal_stage is Stage.FLEET
        assert reg.get("v-good").stage is Stage.FLEET
        # Day 1 at the 1% canary has only ~100 carpet trials/arm: the gate
        # must have HELD for insufficient samples instead of guessing.
        assert result.had_insufficient_sample_hold()
        # It went through both canary stages (no stage skipping).
        stages = [e["stage"] for e in result.decision_log]
        assert "canary_1pct" in stages and "canary_10pct" in stages


def test_scenario_bad_model_rolled_back_at_canary() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        reg = ModelRegistry(os.path.join(tmp, "reg.jsonl"))
        result = run_rollout(
            BAD_MODEL, reg, "v-bad", "manifest-bad", None,
            seed=13, log=_quiet,
        )
        assert result.terminal_stage is Stage.ROLLED_BACK
        assert reg.get("v-bad").stage is Stage.ROLLED_BACK
        # Caught at the FIRST canary stage: blast radius stayed at 1%.
        stages = {e["stage"] for e in result.decision_log}
        assert stages == {"canary_1pct"}
        # The audit trail shows why.
        last = result.decision_log[-1]
        assert last["decision"] == Decision.ROLLBACK.value
        assert "significantly worse" in last["reasons"]["carpet"]


def test_scenario_masked_regression_needs_cohort_gate() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        reg = ModelRegistry(os.path.join(tmp, "reg.jsonl"))
        aggregate, sliced = demo_cohort_masking(
            reg, "v-masked", parent_version=None, seed=17, log=_quiet,
        )
        # The trap: aggregate-only gate would NOT have rolled this back.
        assert aggregate.decision is not Decision.ROLLBACK
        # The per-cohort gate catches the carpet regression.
        assert sliced.decision is Decision.ROLLBACK
        assert sliced.verdict_for("carpet").decision is Decision.ROLLBACK
        assert reg.get("v-masked").stage is Stage.ROLLED_BACK


def main() -> None:
    tests = [
        test_registry_happy_path_and_lineage,
        test_registry_illegal_transitions_raise,
        test_wilson_interval_sanity,
        test_two_proportion_z_signs,
        test_arm_counts_validation,
        test_gate_insufficient_samples_holds,
        test_gate_promote_hold_rollback,
        test_gate_cohort_masking_deterministic_counts,
        test_scenario_good_model_reaches_fleet,
        test_scenario_bad_model_rolled_back_at_canary,
        test_scenario_masked_regression_needs_cohort_gate,
    ]
    for test in tests:
        test()
        print("PASS %s" % test.__name__)
    print("\n%d/%d tests passed" % (len(tests), len(tests)))


if __name__ == "__main__":
    main()
