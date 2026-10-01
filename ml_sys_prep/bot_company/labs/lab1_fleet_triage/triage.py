#!/usr/bin/env python3
"""Fleet triage toolkit -- reference solution for lab1_fleet_triage.

A small, reusable cohort-analysis library (numpy + stdlib only) plus a
``main()`` that runs the full triage workflow on ``data/episodes.jsonl``
and pins every conclusion with an ``assert``.

The workflow it demonstrates is the one to narrate in a fleet-debug
interview ("a batch of bots stopped working"):

    1. Aggregate first     -- overall success rate, is it really down?
    2. Slice by one dim    -- model / fw / task / floor / lighting / home.
    3. Cross two dims      -- interactions that single slices hide.
    4. Align with rollout  -- same robots before vs after their OTA.
    5. Per-robot outliers  -- z-scores + physical-signal trends (drift).
    6. Control confounders -- stratify before blaming a correlated dim.

Usage:
    python triage.py [--data PATH]
"""

import argparse
import json
import sys
from collections import defaultdict
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Callable, Dict, Hashable, List, Optional, Sequence, Tuple

import numpy as np

DEFAULT_DATA = Path(__file__).resolve().parent / "data" / "episodes.jsonl"

REQUIRED_FIELDS = (
    "robot_id", "fw_version", "model_version", "task_type", "home_id",
    "floor_type", "lighting", "battery_pct", "cpu_temp", "grip_current",
    "policy_latency_ms", "success", "error_code", "ts",
)

GRIP_TASKS = ("pick", "place")


# ---------------------------------------------------------------------------
# Data model & loading
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class Episode:
    """Analysis-side view of one telemetry record."""

    robot_id: str
    fw_version: str
    model_version: str
    task_type: str
    home_id: str
    floor_type: str
    lighting: str
    battery_pct: int
    cpu_temp: float
    grip_current: float
    policy_latency_ms: float
    success: bool
    error_code: Optional[str]
    ts: datetime

    @property
    def day(self) -> int:
        """Absolute day ordinal (only differences between days matter)."""
        return self.ts.date().toordinal()


@dataclass(frozen=True)
class CohortStat:
    """Success statistics for one cohort of episodes."""

    n: int
    successes: int

    @property
    def rate(self) -> float:
        return self.successes / self.n if self.n else float("nan")

    def __str__(self) -> str:
        return "{:>5d} eps  {:6.1%}".format(self.n, self.rate)


def load_episodes(path: Path) -> List[Episode]:
    """Load and validate a JSONL telemetry file.

    Raises FileNotFoundError with a helpful hint, or ValueError with the
    offending line number for malformed records.
    """
    if not path.exists():
        raise FileNotFoundError(
            "{} not found -- run `python generate_logs.py` first".format(path)
        )
    episodes: List[Episode] = []
    with path.open("r", encoding="utf-8") as fh:
        for lineno, line in enumerate(fh, start=1):
            line = line.strip()
            if not line:
                continue
            try:
                raw = json.loads(line)
                missing = [k for k in REQUIRED_FIELDS if k not in raw]
                if missing:
                    raise KeyError("missing fields: {}".format(missing))
                episodes.append(
                    Episode(
                        robot_id=str(raw["robot_id"]),
                        fw_version=str(raw["fw_version"]),
                        model_version=str(raw["model_version"]),
                        task_type=str(raw["task_type"]),
                        home_id=str(raw["home_id"]),
                        floor_type=str(raw["floor_type"]),
                        lighting=str(raw["lighting"]),
                        battery_pct=int(raw["battery_pct"]),
                        cpu_temp=float(raw["cpu_temp"]),
                        grip_current=float(raw["grip_current"]),
                        policy_latency_ms=float(raw["policy_latency_ms"]),
                        success=bool(raw["success"]),
                        error_code=raw["error_code"],
                        ts=datetime.strptime(str(raw["ts"]), "%Y-%m-%dT%H:%M:%SZ"),
                    )
                )
            except (KeyError, TypeError, ValueError, json.JSONDecodeError) as exc:
                raise ValueError(
                    "{}:{}: malformed record ({})".format(path, lineno, exc)
                ) from exc
    if not episodes:
        raise ValueError("{}: file contains no episodes".format(path))
    return episodes


# ---------------------------------------------------------------------------
# Generic cohort analytics
# ---------------------------------------------------------------------------

KeyFn = Callable[[Episode], Hashable]


def cohort_stat(episodes: Sequence[Episode]) -> CohortStat:
    """Aggregate success stats over a list of episodes."""
    return CohortStat(n=len(episodes), successes=sum(1 for e in episodes if e.success))


def slice_by(episodes: Sequence[Episode], key: KeyFn) -> Dict[Hashable, CohortStat]:
    """Success stats grouped by one key function."""
    groups: Dict[Hashable, List[Episode]] = defaultdict(list)
    for ep in episodes:
        groups[key(ep)].append(ep)
    return {k: cohort_stat(v) for k, v in groups.items()}


def crosstab(
    episodes: Sequence[Episode], key_a: KeyFn, key_b: KeyFn
) -> Dict[Tuple[Hashable, Hashable], CohortStat]:
    """Success stats grouped by the cross of two key functions."""
    return slice_by(episodes, lambda e: (key_a(e), key_b(e)))


def worst_cell(
    table: Dict[Hashable, CohortStat], min_n: int
) -> Tuple[Hashable, CohortStat]:
    """The lowest-success cell among cells with at least ``min_n`` episodes."""
    eligible = {k: v for k, v in table.items() if v.n >= min_n}
    if not eligible:
        raise ValueError("no cell has >= {} episodes".format(min_n))
    key = min(eligible, key=lambda k: eligible[k].rate)
    return key, eligible[key]


def before_after_upgrade(
    episodes: Sequence[Episode],
    cohort_filter: Callable[[Episode], bool],
    new_version: str,
) -> Tuple[CohortStat, CohortStat]:
    """Compare a cohort's success before vs after OTA, on the *same* robots.

    Only robots observed running ``new_version`` at least once are included,
    so fleet composition cannot confound the before/after comparison.
    """
    upgraded_robots = {e.robot_id for e in episodes if e.model_version == new_version}
    before = [
        e for e in episodes
        if e.robot_id in upgraded_robots
        and e.model_version != new_version
        and cohort_filter(e)
    ]
    after = [
        e for e in episodes
        if e.robot_id in upgraded_robots
        and e.model_version == new_version
        and cohort_filter(e)
    ]
    return cohort_stat(before), cohort_stat(after)


# ---------------------------------------------------------------------------
# Per-robot anomaly detection
# ---------------------------------------------------------------------------

def robot_success_zscores(
    episodes: Sequence[Episode],
    task_types: Optional[Sequence[str]] = None,
    min_n: int = 8,
) -> Dict[str, float]:
    """Z-score of each robot's success rate vs the fleet distribution.

    Robots with fewer than ``min_n`` qualifying episodes are excluded
    (their rates are too noisy to rank).
    """
    pool = [e for e in episodes if task_types is None or e.task_type in task_types]
    per_robot = slice_by(pool, lambda e: e.robot_id)
    rates = {str(rid): st.rate for rid, st in per_robot.items() if st.n >= min_n}
    if len(rates) < 3:
        raise ValueError("need >= 3 robots with >= {} episodes".format(min_n))
    values = np.array(list(rates.values()), dtype=np.float64)
    mean, std = float(values.mean()), float(values.std())
    if std == 0.0:
        return {rid: 0.0 for rid in rates}
    return {rid: (rate - mean) / std for rid, rate in rates.items()}


def grip_current_slopes(
    episodes: Sequence[Episode],
    task_types: Sequence[str] = GRIP_TASKS,
    min_points: int = 6,
) -> Dict[str, float]:
    """Per-robot linear trend (amps/day) of grip_current over time.

    Fits ``grip_current ~ day`` per robot on grip-loaded tasks. A healthy
    gripper trends flat; mechanical degradation shows as a positive slope.
    """
    by_robot: Dict[str, List[Episode]] = defaultdict(list)
    for ep in episodes:
        if ep.task_type in task_types:
            by_robot[ep.robot_id].append(ep)
    slopes: Dict[str, float] = {}
    for rid, eps in by_robot.items():
        days = np.array([e.day for e in eps], dtype=np.float64)
        amps = np.array([e.grip_current for e in eps], dtype=np.float64)
        if len(eps) < min_points or len(set(days.tolist())) < 3:
            continue
        slopes[rid] = float(np.polyfit(days, amps, 1)[0])
    return slopes


# ---------------------------------------------------------------------------
# Confounder control (red-herring analysis)
# ---------------------------------------------------------------------------

def raw_and_adjusted_gap(
    episodes: Sequence[Episode],
    group_filter: Callable[[Episode], bool],
    strata_key: KeyFn,
    min_stratum_n: int = 5,
) -> Tuple[float, float]:
    """How much worse the group is than the rest, raw vs stratified.

    Returns ``(raw_gap, adjusted_gap)`` where gap = rest_rate - group_rate.
    The adjusted gap is the within-stratum gap averaged with the *group's*
    stratum weights (direct standardization). A causal group effect
    survives adjustment; a confounded one collapses toward zero.
    """
    group = [e for e in episodes if group_filter(e)]
    rest = [e for e in episodes if not group_filter(e)]
    if not group or not rest:
        raise ValueError("group_filter must split episodes into two non-empty sets")
    raw_gap = cohort_stat(rest).rate - cohort_stat(group).rate

    group_by = slice_by(group, strata_key)
    rest_by = slice_by(rest, strata_key)
    weighted_sum, weight_total = 0.0, 0.0
    for stratum, g_stat in group_by.items():
        r_stat = rest_by.get(stratum)
        if r_stat is None or g_stat.n < min_stratum_n or r_stat.n < min_stratum_n:
            continue
        weighted_sum += g_stat.n * (r_stat.rate - g_stat.rate)
        weight_total += g_stat.n
    if weight_total == 0.0:
        raise ValueError("no stratum has enough support on both sides")
    return raw_gap, weighted_sum / weight_total


# ---------------------------------------------------------------------------
# Report
# ---------------------------------------------------------------------------

def _print_table(title: str, table: Dict[Hashable, CohortStat]) -> None:
    print("\n  {}".format(title))
    for key in sorted(table, key=lambda k: table[k].rate):
        print("    {!s:<28} {}".format(key, table[key]))


def run_triage(data_path: Path) -> Dict[str, object]:
    """Run the full triage workflow, print the report, return the findings."""
    episodes = load_episodes(data_path)
    findings: Dict[str, object] = {}

    print("=" * 72)
    print("FLEET TRIAGE REPORT  ({} episodes from {})".format(len(episodes), data_path.name))
    print("=" * 72)

    # -- Step 1: aggregate ---------------------------------------------------
    overall = cohort_stat(episodes)
    findings["overall"] = overall
    print("\n[1] Overall: {}".format(overall))

    # -- Step 2: single-dimension slices --------------------------------------
    print("\n[2] Single-dimension slices (sorted worst-first)")
    for name, key in (
        ("model_version", lambda e: e.model_version),
        ("fw_version", lambda e: e.fw_version),
        ("task_type", lambda e: e.task_type),
        ("floor_type", lambda e: e.floor_type),
        ("lighting", lambda e: e.lighting),
    ):
        _print_table("by {}".format(name), slice_by(episodes, key))
    homes = slice_by(episodes, lambda e: e.home_id)
    big_homes = {h: st for h, st in homes.items() if st.n >= 80}
    _print_table("by home_id (only homes with >= 80 eps)", big_homes)
    worst_home, worst_home_stat = worst_cell(big_homes, min_n=80)
    findings["worst_home"] = worst_home
    print("    -> worst big home: {} ({})".format(worst_home, worst_home_stat))

    # -- Step 3: two-dimension crosstab, per model version --------------------
    print("\n[3] floor_type x lighting, split by model_version")
    v24 = [e for e in episodes if e.model_version == "v2.4"]
    v23 = [e for e in episodes if e.model_version == "v2.3"]
    tab24 = crosstab(v24, lambda e: e.floor_type, lambda e: e.lighting)
    tab23 = crosstab(v23, lambda e: e.floor_type, lambda e: e.lighting)
    _print_table("v2.4", tab24)
    _print_table("v2.3", tab23)
    bad_cell, bad_stat = worst_cell(tab24, min_n=40)
    findings["worst_v24_cell"] = bad_cell
    findings["worst_v24_rate"] = bad_stat.rate
    findings["v23_same_cell_rate"] = tab23[bad_cell].rate
    findings["other_v24_min_rate"] = min(
        st.rate for k, st in tab24.items() if k != bad_cell and st.n >= 40
    )
    print("    -> worst v2.4 cell: {} at {:.1%} (same cell on v2.3: {:.1%})".format(
        bad_cell, bad_stat.rate, tab23[bad_cell].rate))

    # -- Step 4: align with the OTA timeline ----------------------------------
    print("\n[4] Same-robot before/after OTA, inside the suspect cohort")
    floor, light = bad_cell
    before, after = before_after_upgrade(
        episodes,
        cohort_filter=lambda e: e.floor_type == floor and e.lighting == light,
        new_version="v2.4",
    )
    findings["cohort_before"] = before
    findings["cohort_after"] = after
    print("    upgraded robots, {}+{} episodes: before {} | after {}".format(
        floor, light, before, after))
    cohort_codes = sorted(
        slice_by(
            [e for e in v24
             if e.floor_type == floor and e.lighting == light and not e.success],
            lambda e: e.error_code,
        ).items(),
        key=lambda kv: -kv[1].n,
    )
    print("    top error codes in broken cohort: {}".format(
        [(code, st.n) for code, st in cohort_codes[:3]]))

    # -- Step 5: per-robot outliers -------------------------------------------
    print("\n[5] Per-robot anomaly detection (grip-loaded tasks: pick/place)")
    zscores = robot_success_zscores(episodes, task_types=GRIP_TASKS, min_n=8)
    suspect_z = min(zscores, key=lambda r: zscores[r])
    slopes = grip_current_slopes(episodes)
    ranked = sorted(slopes, key=lambda r: slopes[r], reverse=True)
    suspect_slope, runner_up = ranked[0], ranked[1]
    findings["suspect_robot_z"] = suspect_z
    findings["suspect_z_value"] = zscores[suspect_z]
    findings["suspect_robot_slope"] = suspect_slope
    findings["suspect_slope_value"] = slopes[suspect_slope]
    findings["runner_up_slope_value"] = slopes[runner_up]
    print("    lowest success z-score : {} (z = {:+.2f})".format(
        suspect_z, zscores[suspect_z]))
    print("    steepest grip drift    : {} ({:+.3f} A/day; runner-up {} {:+.3f})".format(
        suspect_slope, slopes[suspect_slope], runner_up, slopes[runner_up]))
    suspect_fail_codes = slice_by(
        [e for e in episodes if e.robot_id == suspect_z and not e.success],
        lambda e: e.error_code,
    )
    print("    suspect's failure codes: {}".format(
        sorted(((c, st.n) for c, st in suspect_fail_codes.items()),
               key=lambda kv: -kv[1])))

    # -- Step 6: control the confounder ---------------------------------------
    print("\n[6] Red-herring check: is {} causally bad?".format(worst_home))
    raw_gap, adjusted_gap = raw_and_adjusted_gap(
        episodes,
        group_filter=lambda e: e.home_id == worst_home,
        strata_key=lambda e: (e.model_version, e.floor_type, e.lighting),
    )
    findings["raw_gap"] = raw_gap
    findings["adjusted_gap"] = adjusted_gap
    print("    raw gap vs rest of fleet      : {:+.1%}".format(raw_gap))
    print("    after stratifying on (model,  ")
    print("    floor, lighting)              : {:+.1%}".format(adjusted_gap))
    print("    -> the home effect {} under stratification".format(
        "collapses" if abs(adjusted_gap) < raw_gap / 2 else "PERSISTS"))

    print("\n" + "=" * 72)
    return findings


def verify_findings(findings: Dict[str, object]) -> None:
    """Pin the triage conclusions against the simulator's ground truth.

    A real on-call triage obviously has no ground truth to import; this
    block exists so the lab is self-checking.
    """
    import generate_logs as gt

    # (a) Cohort regression: v2.4 x carpet x dim.
    assert findings["worst_v24_cell"] == (
        gt.REGRESSED_FLOOR_TYPE, gt.REGRESSED_LIGHTING
    ), "worst v2.4 cell should be (carpet, dim), got {}".format(
        findings["worst_v24_cell"])
    assert findings["worst_v24_rate"] < 0.45, "broken cohort should be < 45% success"
    assert findings["v23_same_cell_rate"] > 0.75, "same cohort on v2.3 should be healthy"
    assert findings["other_v24_min_rate"] > 0.75, "all other v2.4 cells should be healthy"
    before = findings["cohort_before"]
    after = findings["cohort_after"]
    assert before.rate > 0.75 and after.rate < 0.45, (
        "same robots must be healthy pre-OTA and broken post-OTA "
        "(before {:.1%}, after {:.1%})".format(before.rate, after.rate))

    # (b) Hardware fault: one robot, found by two independent signals.
    assert findings["suspect_robot_z"] == gt.BAD_ROBOT_ID, (
        "z-score suspect should be {}, got {}".format(
            gt.BAD_ROBOT_ID, findings["suspect_robot_z"]))
    assert findings["suspect_robot_slope"] == gt.BAD_ROBOT_ID, (
        "grip-drift suspect should be {}, got {}".format(
            gt.BAD_ROBOT_ID, findings["suspect_robot_slope"]))
    assert findings["suspect_z_value"] < -3.0, "suspect z should be a hard outlier"
    assert findings["suspect_slope_value"] > 0.10, "drift should be > 0.10 A/day"
    assert findings["runner_up_slope_value"] < 0.05, "healthy grippers should be flat"

    # (c) Red herring: the worst home is the planted one, and its effect
    #     disappears once the real drivers are controlled for.
    assert findings["worst_home"] == gt.RED_HERRING_HOME_ID, (
        "worst big home should be {}, got {}".format(
            gt.RED_HERRING_HOME_ID, findings["worst_home"]))
    raw_gap = float(findings["raw_gap"])  # type: ignore[arg-type]
    adjusted_gap = float(findings["adjusted_gap"])  # type: ignore[arg-type]
    assert raw_gap > 0.08, "red herring must look real in raw data"
    assert abs(adjusted_gap) < 0.05, "home effect must vanish under stratification"
    assert abs(adjusted_gap) < raw_gap / 2, "adjustment must collapse the gap"

    print("[verify] all triage conclusions match planted ground truth")


def main(argv: Optional[List[str]] = None) -> int:
    parser = argparse.ArgumentParser(description="Run the fleet triage workflow.")
    parser.add_argument("--data", type=Path, default=DEFAULT_DATA,
                        help="episodes JSONL (default: data/episodes.jsonl)")
    args = parser.parse_args(argv)
    findings = run_triage(args.data)
    verify_findings(findings)
    return 0


if __name__ == "__main__":
    sys.exit(main())
