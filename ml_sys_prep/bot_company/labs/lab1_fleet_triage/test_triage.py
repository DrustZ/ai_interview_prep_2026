#!/usr/bin/env python3
"""Plain-assert test suite for lab1_fleet_triage (no pytest).

Run:
    python test_triage.py

Covers:
    - deterministic generation (same seed -> byte-identical JSONL)
    - schema / shape of the generated dataset
    - root cause (a): v2.4 x carpet x dim cohort regression is detectable
    - root cause (b): the grip-drift robot is detectable by two signals
    - red herring (c): the "bad home" correlation collapses under control
    - end-to-end: triage report runs and its own asserts pass
"""

import hashlib
import sys
import tempfile
from pathlib import Path

LAB_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(LAB_DIR))

import generate_logs as gl  # noqa: E402
import triage  # noqa: E402


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _generate_dataset(tmp_dir: Path) -> Path:
    """Generate the canonical dataset into tmp_dir and return its path."""
    out = tmp_dir / "episodes.jsonl"
    gl.write_jsonl(gl.generate_episodes(seed=gl.DEFAULT_SEED), out)
    return out


def test_determinism(tmp_dir: Path) -> None:
    a, b = tmp_dir / "run_a.jsonl", tmp_dir / "run_b.jsonl"
    gl.write_jsonl(gl.generate_episodes(seed=gl.DEFAULT_SEED), a)
    gl.write_jsonl(gl.generate_episodes(seed=gl.DEFAULT_SEED), b)
    assert _sha256(a) == _sha256(b), "same seed must produce byte-identical output"

    c = tmp_dir / "run_c.jsonl"
    gl.write_jsonl(gl.generate_episodes(seed=gl.DEFAULT_SEED + 1), c)
    assert _sha256(a) != _sha256(c), "different seeds should differ"


def test_schema_and_shape(data_path: Path) -> None:
    episodes = triage.load_episodes(data_path)  # load_episodes validates schema
    assert len(episodes) == gl.N_ROBOTS * gl.EPISODES_PER_ROBOT, (
        "expected {} episodes, got {}".format(
            gl.N_ROBOTS * gl.EPISODES_PER_ROBOT, len(episodes)))

    robots = {e.robot_id for e in episodes}
    assert len(robots) == gl.N_ROBOTS, "expected {} robots".format(gl.N_ROBOTS)

    assert {e.model_version for e in episodes} == {"v2.3", "v2.4"}
    assert {e.lighting for e in episodes} == {"bright", "dim"}
    assert {e.floor_type for e in episodes} == set(gl.FLOOR_TYPES)
    assert {e.task_type for e in episodes} == set(gl.TASK_TYPES)
    for ep in episodes:
        assert 0 <= ep.battery_pct <= 100, "battery_pct out of range"
        assert ep.grip_current > 0.0, "grip_current must be positive"
        assert ep.success or ep.error_code is not None, (
            "failed episodes must carry an error_code")
        assert not (ep.success and ep.error_code is not None), (
            "successful episodes must not carry an error_code")

    # Timestamps span the configured window.
    days = {e.ts.date() for e in episodes}
    assert len(days) == gl.N_DAYS, "expected {} distinct days".format(gl.N_DAYS)


def test_cohort_regression_detected(data_path: Path) -> None:
    episodes = triage.load_episodes(data_path)
    v24 = [e for e in episodes if e.model_version == gl.REGRESSED_MODEL_VERSION]
    v23 = [e for e in episodes if e.model_version == "v2.3"]

    tab24 = triage.crosstab(v24, lambda e: e.floor_type, lambda e: e.lighting)
    tab23 = triage.crosstab(v23, lambda e: e.floor_type, lambda e: e.lighting)

    cell, stat = triage.worst_cell(tab24, min_n=40)
    assert cell == (gl.REGRESSED_FLOOR_TYPE, gl.REGRESSED_LIGHTING), (
        "worst v2.4 cell should be (carpet, dim), got {}".format(cell))
    assert stat.n >= 80, "broken cohort needs decent support, got n={}".format(stat.n)
    assert stat.rate < 0.45, "broken cohort rate {:.1%} not low enough".format(stat.rate)
    assert tab23[cell].rate > 0.75, "same cohort must be healthy on v2.3"
    for other, other_stat in tab24.items():
        if other != cell and other_stat.n >= 40:
            assert other_stat.rate > 0.75, (
                "v2.4 cell {} should be healthy, got {:.1%}".format(
                    other, other_stat.rate))

    # OTA alignment: the same robots were fine on this cohort before upgrade.
    before, after = triage.before_after_upgrade(
        episodes,
        cohort_filter=lambda e: (
            e.floor_type == gl.REGRESSED_FLOOR_TYPE
            and e.lighting == gl.REGRESSED_LIGHTING
        ),
        new_version=gl.REGRESSED_MODEL_VERSION,
    )
    assert before.n >= 40 and after.n >= 40, "need support on both sides of OTA"
    assert before.rate > 0.75, "pre-OTA cohort should be healthy"
    assert after.rate < 0.45, "post-OTA cohort should be broken"


def test_bad_robot_detected(data_path: Path) -> None:
    episodes = triage.load_episodes(data_path)

    zscores = triage.robot_success_zscores(
        episodes, task_types=triage.GRIP_TASKS, min_n=8)
    suspect = min(zscores, key=lambda r: zscores[r])
    assert suspect == gl.BAD_ROBOT_ID, (
        "z-score should flag {}, got {}".format(gl.BAD_ROBOT_ID, suspect))
    assert zscores[suspect] < -3.0, "suspect must be a hard outlier"

    slopes = triage.grip_current_slopes(episodes)
    ranked = sorted(slopes, key=lambda r: slopes[r], reverse=True)
    assert ranked[0] == gl.BAD_ROBOT_ID, (
        "grip drift should flag {}, got {}".format(gl.BAD_ROBOT_ID, ranked[0]))
    assert slopes[ranked[0]] > 0.10, "planted drift is 0.13 A/day; must be visible"
    assert slopes[ranked[1]] < 0.05, "second-steepest robot should look flat"

    # The failure signature is mechanical (grip), not perception (vision).
    bad_failures = [
        e for e in episodes if e.robot_id == gl.BAD_ROBOT_ID and not e.success]
    grip_coded = [e for e in bad_failures if e.error_code in ("GRIP_SLIP", "GRIP_STALL")]
    assert len(grip_coded) >= 0.5 * len(bad_failures), (
        "the bad robot's failures should be dominated by grip error codes")


def test_red_herring_rejected(data_path: Path) -> None:
    episodes = triage.load_episodes(data_path)

    homes = triage.slice_by(episodes, lambda e: e.home_id)
    big_homes = {h: st for h, st in homes.items() if st.n >= 80}
    worst_home, _ = triage.worst_cell(big_homes, min_n=80)
    assert worst_home == gl.RED_HERRING_HOME_ID, (
        "the planted home should look worst in raw slices, got {}".format(worst_home))

    raw_gap, adjusted_gap = triage.raw_and_adjusted_gap(
        episodes,
        group_filter=lambda e: e.home_id == gl.RED_HERRING_HOME_ID,
        strata_key=lambda e: (e.model_version, e.floor_type, e.lighting),
    )
    assert raw_gap > 0.08, (
        "red herring must look real before control (raw gap {:+.1%})".format(raw_gap))
    assert abs(adjusted_gap) < 0.05, (
        "home effect must vanish under stratification (adjusted {:+.1%})".format(
            adjusted_gap))
    assert abs(adjusted_gap) < raw_gap / 2, "adjustment must collapse the gap"

    # Sanity: the home's robots are NOT hardware outliers -- their pick/place
    # success inside healthy strata is normal.
    healthy = [
        e for e in episodes
        if e.home_id == gl.RED_HERRING_HOME_ID
        and not (
            e.model_version == gl.REGRESSED_MODEL_VERSION
            and e.floor_type == gl.REGRESSED_FLOOR_TYPE
            and e.lighting == gl.REGRESSED_LIGHTING
        )
    ]
    assert triage.cohort_stat(healthy).rate > 0.75, (
        "outside the broken cohort the red-herring home is healthy")


def test_end_to_end(data_path: Path) -> None:
    findings = triage.run_triage(data_path)
    triage.verify_findings(findings)  # raises AssertionError on any mismatch


def main() -> int:
    with tempfile.TemporaryDirectory(prefix="lab1_fleet_triage_") as tmp:
        tmp_dir = Path(tmp)
        data_path = _generate_dataset(tmp_dir)

        tests = [
            ("determinism", lambda: test_determinism(tmp_dir)),
            ("schema_and_shape", lambda: test_schema_and_shape(data_path)),
            ("cohort_regression_detected",
             lambda: test_cohort_regression_detected(data_path)),
            ("bad_robot_detected", lambda: test_bad_robot_detected(data_path)),
            ("red_herring_rejected", lambda: test_red_herring_rejected(data_path)),
            ("end_to_end", lambda: test_end_to_end(data_path)),
        ]
        for name, fn in tests:
            fn()
            print("PASS  {}".format(name))

    print("\nALL {} TESTS PASSED".format(len(tests)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
