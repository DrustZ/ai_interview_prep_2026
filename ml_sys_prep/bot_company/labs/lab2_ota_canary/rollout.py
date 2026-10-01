"""Fleet rollout simulator: OTA canary with automatic rollback.

Simulates a 10,000-robot home fleet receiving a new policy over the air:

    staged -> canary_1pct (100 robots) -> canary_10pct (1,000 robots) -> fleet

Each canary stage runs day-sized observation windows. Robots execute tasks in
two cohorts (floor types) with different baseline success rates; a matched
control arm of equal size keeps running the incumbent policy. After every day
the statistical gate (``gate.py``) reads the *accumulated* counts and says
PROMOTE / HOLD / ROLLBACK; the rollout controller translates that into
registry transitions (``registry.py``). If a stage exhausts its observation
budget without a decision, the controller **fails closed** and rolls back.

Three scenarios (fixed seeds, fully deterministic):

1. good   -- true +3pp everywhere       -> promotes step by step to fleet.
2. bad    -- carpet -15pp, overall -4pp -> caught at the 1% canary, rolled back.
3. masked -- overall ~flat, but carpet -8pp masked by a hardwood win.
             An aggregate-only gate PROMOTES this model; the per-cohort gate
             rolls it back. This is why the gate slices by cohort.

Run: ``/usr/bin/python3 rollout.py``
"""

import random
import tempfile
from dataclasses import dataclass, field
from typing import Callable, Dict, List, Optional, Tuple

from gate import (
    ArmCounts,
    Decision,
    GateConfig,
    GateReport,
    evaluate,
    merge_cohorts,
)
from registry import ModelRegistry, Stage

# ----------------------------------------------------------------------
# Fleet / cohort model
# ----------------------------------------------------------------------

FLEET_SIZE = 10_000
TASKS_PER_ROBOT_PER_DAY = 4
MAX_DAYS_PER_STAGE = 12

#: Robots assigned to the canary arm at each gated stage (control arm is a
#: matched set of the same size running the incumbent policy).
STAGE_ARM_SIZE: Dict[Stage, int] = {
    Stage.CANARY_1PCT: FLEET_SIZE // 100,   # 100 robots
    Stage.CANARY_10PCT: FLEET_SIZE // 10,   # 1,000 robots
}

#: Stages that require a gate decision, in rollout order.
GATED_STAGES: List[Stage] = [Stage.CANARY_1PCT, Stage.CANARY_10PCT]


@dataclass(frozen=True)
class CohortSpec:
    """A task cohort with its share of daily tasks and baseline success rate."""

    name: str
    weight: float
    baseline_rate: float


COHORTS: List[CohortSpec] = [
    CohortSpec(name="hardwood", weight=0.75, baseline_rate=0.90),
    CohortSpec(name="carpet", weight=0.25, baseline_rate=0.70),
]


@dataclass(frozen=True)
class ModelProfile:
    """Ground-truth behaviour of a candidate model (unknown to the gate).

    ``deltas`` maps cohort name -> true change in success rate vs baseline.
    """

    name: str
    deltas: Dict[str, float]

    def true_rate(self, cohort: CohortSpec) -> float:
        rate = cohort.baseline_rate + self.deltas.get(cohort.name, 0.0)
        return min(1.0, max(0.0, rate))


GOOD_MODEL = ModelProfile(
    name="good", deltas={"hardwood": +0.03, "carpet": +0.03}
)
# carpet -15pp, weighted overall = 0.75*(-0.005) + 0.25*(-0.15) ~= -4pp
BAD_MODEL = ModelProfile(
    name="bad", deltas={"hardwood": -0.005, "carpet": -0.15}
)
# overall = 0.75*(+0.027) + 0.25*(-0.08) ~= +0.03pp: flat in aggregate,
# badly regressed on carpet.
MASKED_MODEL = ModelProfile(
    name="masked", deltas={"hardwood": +0.027, "carpet": -0.08}
)


# ----------------------------------------------------------------------
# Simulator
# ----------------------------------------------------------------------


class FleetSimulator:
    """Draws daily per-cohort task outcomes for a canary arm and its control.

    Deterministic given the seed. Pure stdlib ``random`` -- sample sizes are
    small enough that O(n) Bernoulli draws are instant.
    """

    def __init__(self, seed: int) -> None:
        self._rng = random.Random(seed)

    def sample_day(
        self, arm_robots: int, candidate: ModelProfile
    ) -> Dict[str, Tuple[ArmCounts, ArmCounts]]:
        """One observation day; returns cohort -> (canary, control) counts."""
        total_tasks = arm_robots * TASKS_PER_ROBOT_PER_DAY
        day: Dict[str, Tuple[ArmCounts, ArmCounts]] = {}
        remaining = total_tasks
        for i, cohort in enumerate(COHORTS):
            if i == len(COHORTS) - 1:
                n_tasks = remaining  # keep the split exact
            else:
                n_tasks = int(round(total_tasks * cohort.weight))
                remaining -= n_tasks
            canary = self._binomial(n_tasks, candidate.true_rate(cohort))
            control = self._binomial(n_tasks, cohort.baseline_rate)
            day[cohort.name] = (
                ArmCounts(successes=canary, trials=n_tasks),
                ArmCounts(successes=control, trials=n_tasks),
            )
        return day

    def _binomial(self, n: int, p: float) -> int:
        rng = self._rng
        return sum(1 for _ in range(n) if rng.random() < p)


def _accumulate(
    total: Dict[str, Tuple[ArmCounts, ArmCounts]],
    day: Dict[str, Tuple[ArmCounts, ArmCounts]],
) -> Dict[str, Tuple[ArmCounts, ArmCounts]]:
    """Merge one day of counts into the running per-cohort totals."""
    merged: Dict[str, Tuple[ArmCounts, ArmCounts]] = dict(total)
    for name, (canary_day, control_day) in day.items():
        canary_old, control_old = merged.get(
            name, (ArmCounts(0, 0), ArmCounts(0, 0))
        )
        merged[name] = (
            ArmCounts(
                successes=canary_old.successes + canary_day.successes,
                trials=canary_old.trials + canary_day.trials,
            ),
            ArmCounts(
                successes=control_old.successes + control_day.successes,
                trials=control_old.trials + control_day.trials,
            ),
        )
    return merged


# ----------------------------------------------------------------------
# Rollout controller
# ----------------------------------------------------------------------


@dataclass
class RolloutResult:
    """Outcome of one candidate rollout, with a full decision audit trail."""

    version_id: str
    terminal_stage: Stage
    decision_log: List[Dict[str, object]] = field(default_factory=list)

    def had_insufficient_sample_hold(self) -> bool:
        """True if any HOLD was caused by the minimum-sample guard."""
        for entry in self.decision_log:
            reasons: Dict[str, str] = entry["reasons"]  # type: ignore[assignment]
            if entry["decision"] == Decision.HOLD.value and any(
                "insufficient" in reason for reason in reasons.values()
            ):
                return True
        return False


def run_rollout(
    candidate: ModelProfile,
    registry: ModelRegistry,
    version_id: str,
    train_manifest_id: str,
    parent_version: Optional[str],
    seed: int,
    gate_config: Optional[GateConfig] = None,
    log: Callable[[str], None] = print,
) -> RolloutResult:
    """Drive one candidate through the staged rollout under gate control.

    Returns a :class:`RolloutResult`; the registry ends at ``fleet`` or
    ``rolled_back`` (never stuck mid-canary: budget exhaustion fails closed).
    """
    config = gate_config if gate_config is not None else GateConfig()
    simulator = FleetSimulator(seed=seed)
    result = RolloutResult(version_id=version_id, terminal_stage=Stage.STAGED)

    registry.register(version_id, train_manifest_id, parent_version)
    registry.promote(version_id, reason="start 1%% canary for %s" % candidate.name)
    log("[%s] registered (manifest=%s, parent=%s) -> canary_1pct"
        % (version_id, train_manifest_id, parent_version))

    for stage in GATED_STAGES:
        arm_robots = STAGE_ARM_SIZE[stage]
        counts: Dict[str, Tuple[ArmCounts, ArmCounts]] = {}
        decided = False
        for day in range(1, MAX_DAYS_PER_STAGE + 1):
            counts = _accumulate(
                counts, simulator.sample_day(arm_robots, candidate)
            )
            report = evaluate(counts, config)
            _log_report(result, log, stage, day, report)
            if report.decision is Decision.PROMOTE:
                new_stage = registry.promote(
                    version_id,
                    reason="gate promote at %s day %d" % (stage.value, day),
                )
                log("  -> PROMOTE to %s" % new_stage.value)
                decided = True
                break
            if report.decision is Decision.ROLLBACK:
                registry.rollback(
                    version_id,
                    reason="gate rollback at %s day %d" % (stage.value, day),
                )
                log("  -> ROLLBACK (auto)")
                result.terminal_stage = Stage.ROLLED_BACK
                return result
            # HOLD: keep observing.
        if not decided:
            registry.rollback(
                version_id,
                reason="no decision within %d days at %s (fail closed)"
                % (MAX_DAYS_PER_STAGE, stage.value),
            )
            log("  -> ROLLBACK (observation budget exhausted, fail closed)")
            result.terminal_stage = Stage.ROLLED_BACK
            return result

    result.terminal_stage = registry.get(version_id).stage
    log("[%s] terminal stage: %s" % (version_id, result.terminal_stage.value))
    return result


def _log_report(
    result: RolloutResult,
    log: Callable[[str], None],
    stage: Stage,
    day: int,
    report: GateReport,
) -> None:
    reasons = {v.cohort: v.reason for v in report.verdicts}
    result.decision_log.append(
        {
            "stage": stage.value,
            "day": day,
            "decision": report.decision.value,
            "reasons": reasons,
        }
    )
    log("  %s day %d: %s" % (stage.value, day, report.decision.value.upper()))
    for verdict in report.verdicts:
        log("      %-8s %-8s %s"
            % (verdict.cohort, verdict.decision.value, verdict.reason))


# ----------------------------------------------------------------------
# Scenario 3: why the gate must slice by cohort
# ----------------------------------------------------------------------


def demo_cohort_masking(
    registry: ModelRegistry,
    version_id: str,
    parent_version: Optional[str],
    seed: int,
    days: int = 6,
    log: Callable[[str], None] = print,
) -> Tuple[GateReport, GateReport]:
    """Run the masked model at the 1% canary and gate it two ways.

    Returns ``(aggregate_report, cohort_report)`` computed on the *same*
    accumulated counts. The aggregate gate promotes; the per-cohort gate
    rolls back, and the registry records the rollback.
    """
    config = GateConfig()
    simulator = FleetSimulator(seed=seed)
    registry.register(version_id, "manifest-masked-001", parent_version)
    registry.promote(version_id, reason="start 1% canary (masking demo)")

    counts: Dict[str, Tuple[ArmCounts, ArmCounts]] = {}
    arm_robots = STAGE_ARM_SIZE[Stage.CANARY_1PCT]
    for _ in range(days):
        counts = _accumulate(
            counts, simulator.sample_day(arm_robots, MASKED_MODEL)
        )

    agg_canary, agg_control = merge_cohorts(counts)
    aggregate_report = evaluate(
        {"all_tasks": (agg_canary, agg_control)}, config
    )
    cohort_report = evaluate(counts, config)

    log("[%s] %d days at 1%% canary, same data, two gates:" % (version_id, days))
    log("  aggregate-only gate: %s" % aggregate_report.decision.value.upper())
    for verdict in aggregate_report.verdicts:
        log("      %-8s %-8s %s"
            % (verdict.cohort, verdict.decision.value, verdict.reason))
    log("  per-cohort gate:     %s" % cohort_report.decision.value.upper())
    for verdict in cohort_report.verdicts:
        log("      %-8s %-8s %s"
            % (verdict.cohort, verdict.decision.value, verdict.reason))

    if cohort_report.decision is Decision.ROLLBACK:
        registry.rollback(
            version_id, reason="per-cohort gate: carpet regression"
        )
        log("  -> ROLLBACK recorded (aggregate gate would have shipped this)")
    return aggregate_report, cohort_report


# ----------------------------------------------------------------------
# Entry point
# ----------------------------------------------------------------------


def _setup_baseline(registry: ModelRegistry) -> str:
    """Register + fully promote the incumbent policy; return its version id."""
    baseline = "policy-v1"
    registry.register(baseline, "manifest-base-000", None)
    registry.promote(baseline, reason="baseline bootstrap")
    registry.promote(baseline, reason="baseline bootstrap")
    registry.promote(baseline, reason="baseline bootstrap")
    return baseline


def main() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        registry = ModelRegistry(tmp + "/registry.jsonl")
        baseline = _setup_baseline(registry)
        print("incumbent fleet version: %s" % registry.current_fleet_version())

        print("\n=== scenario 1: good model (+3pp everywhere) ===")
        good = run_rollout(
            GOOD_MODEL, registry, "policy-v2-good", "manifest-good-001",
            parent_version=baseline, seed=11,
        )
        print("terminal: %s\n" % good.terminal_stage.value)

        print("=== scenario 2: bad model (carpet -15pp, overall -4pp) ===")
        bad = run_rollout(
            BAD_MODEL, registry, "policy-v2-bad", "manifest-bad-001",
            parent_version=baseline, seed=13,
        )
        print("terminal: %s\n" % bad.terminal_stage.value)

        print("=== scenario 3: flat overall, carpet regression (masking) ===")
        demo_cohort_masking(
            registry, "policy-v2-masked", parent_version=baseline, seed=17
        )

        print("\nfleet version after all three rollouts: %s"
              % registry.current_fleet_version())
        print("lineage of policy-v2-good: %s"
              % " <- ".join(registry.lineage("policy-v2-good")))


if __name__ == "__main__":
    main()
