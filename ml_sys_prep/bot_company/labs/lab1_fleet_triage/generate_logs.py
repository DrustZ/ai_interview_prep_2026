#!/usr/bin/env python3
"""Deterministic fleet-telemetry simulator for lab1_fleet_triage.

Generates episode-level telemetry for a simulated fleet of ~200 home robots
over a 14-day window and writes it as JSONL (one episode per line) to
``data/episodes.jsonl``.

Planted ground truth (SPOILERS -- candidates should run this script but not
read it before finishing EXERCISE.md):

  (a) Cohort regression: model ``v2.4`` fails hard on episodes where
      ``floor_type == "carpet"`` and ``lighting == "dim"`` (an
      out-of-distribution perception regression shipped via OTA).
  (b) Hardware fault: one specific robot's ``grip_current`` drifts upward
      day over day; once it crosses ``GRIP_FAULT_THRESHOLD_A`` its
      pick/place episodes fail almost every time.
  (c) Red herring: one home runs most of its episodes in the evening (dim
      lighting) on wall-to-wall carpet and was upgraded to v2.4 early, so
      its *raw* success rate looks terrible -- but the home itself has no
      causal effect. Controlling for (model_version, floor_type, lighting)
      makes the gap disappear.

Schema of each JSONL record (all keys always present):
    robot_id          str   e.g. "RB-042"
    fw_version        str   firmware, non-causal distractor ("5.1.0"/"5.2.0")
    model_version     str   policy model, "v2.3" or "v2.4" (per-robot OTA)
    task_type         str   pick | place | navigate | wipe | dock
    home_id           str   e.g. "home_003"
    floor_type        str   hardwood | carpet | tile
    lighting          str   bright | dim
    battery_pct       int   15..100
    cpu_temp          float degrees C
    grip_current      float amps (meaningful for pick/place, idle otherwise)
    policy_latency_ms float per-step policy latency
    success           bool  episode outcome
    error_code        str or null (null on success)
    ts                str   ISO-8601 UTC, e.g. "2026-07-24T19:41:00Z"

Determinism: a single ``random.Random(seed)`` instance drives all sampling
in a fixed iteration order, so identical seeds produce byte-identical files.

Usage:
    python generate_logs.py [--out PATH] [--seed N]
"""

import argparse
import json
import random
import sys
from dataclasses import dataclass
from datetime import date, timedelta
from pathlib import Path
from typing import Dict, List, Optional

# ---------------------------------------------------------------------------
# Fleet / simulation constants
# ---------------------------------------------------------------------------

DEFAULT_SEED = 20260810
DEFAULT_OUT = Path(__file__).resolve().parent / "data" / "episodes.jsonl"

N_ROBOTS = 200
EPISODES_PER_ROBOT = 25          # 200 * 25 = 5000 episodes total
N_DAYS = 14
START_DATE = date(2026, 7, 20)

TASK_TYPES = ["pick", "place", "navigate", "wipe", "dock"]
TASK_WEIGHTS = [0.30, 0.20, 0.20, 0.15, 0.15]
GRIP_TASKS = ("pick", "place")   # tasks where the gripper is load-bearing

FLOOR_TYPES = ["hardwood", "carpet", "tile"]
FLOOR_WEIGHTS_NORMAL = [0.40, 0.33, 0.27]
FLOOR_WEIGHTS_RED_HERRING = [0.20, 0.65, 0.15]

FW_VERSIONS = ["5.1.0", "5.2.0"]

# --- Ground truth for the three planted root causes (used by tests) --------

REGRESSED_MODEL_VERSION = "v2.4"
REGRESSED_FLOOR_TYPE = "carpet"
REGRESSED_LIGHTING = "dim"
COHORT_REGRESSION_SUCCESS_P = 0.25   # success prob inside the broken cohort

BAD_ROBOT_ID = "RB-042"              # the hardware-fault robot
GRIP_DRIFT_A_PER_DAY = 0.13          # amps of upward drift per day
GRIP_FAULT_THRESHOLD_A = 1.80        # above this, grasps slip
GRIP_FAULT_SUCCESS_P = 0.05

RED_HERRING_HOME_ID = "home_003"     # evening-heavy, carpeted, early OTA

BASE_SUCCESS_P = 0.92
OTA_DAY_RANGE = (5, 8)               # upgraded robots flip to v2.4 in here
UPGRADE_FRACTION = 0.60


@dataclass(frozen=True)
class RobotProfile:
    """Static per-robot attributes fixed at fleet-construction time."""

    robot_id: str
    home_id: str
    fw_version: str
    ota_day: Optional[int]   # day index the robot switched to v2.4; None = never
    grip_faulty: bool


# ---------------------------------------------------------------------------
# Fleet construction
# ---------------------------------------------------------------------------

def build_fleet(rng: random.Random) -> List[RobotProfile]:
    """Create the 200-robot fleet with home assignments and OTA schedule.

    Layout: homes 000..005 are "large" homes with 4 robots each (indices
    0..23); the remaining 176 robots live in 2-robot homes (006..093).
    home_003 is the red-herring home (robots RB-012..RB-015).
    """
    robots: List[RobotProfile] = []
    for idx in range(N_ROBOTS):
        robot_id = "RB-{:03d}".format(idx)
        if idx < 24:
            home_id = "home_{:03d}".format(idx // 4)
        else:
            home_id = "home_{:03d}".format(6 + (idx - 24) // 2)

        fw_version = rng.choice(FW_VERSIONS)

        # OTA schedule. The draw below happens for every robot so that the
        # RNG stream (and therefore the whole dataset) is stable even when
        # the special-case robots override the result.
        upgraded = rng.random() < UPGRADE_FRACTION
        ota_day_draw = rng.randint(*OTA_DAY_RANGE)
        ota_day: Optional[int] = ota_day_draw if upgraded else None

        if home_id == RED_HERRING_HOME_ID:
            ota_day = OTA_DAY_RANGE[0]       # early adopter home
        if robot_id == BAD_ROBOT_ID:
            ota_day = None                   # keep causes cleanly separable

        robots.append(
            RobotProfile(
                robot_id=robot_id,
                home_id=home_id,
                fw_version=fw_version,
                ota_day=ota_day,
                grip_faulty=(robot_id == BAD_ROBOT_ID),
            )
        )
    return robots


# ---------------------------------------------------------------------------
# Episode simulation
# ---------------------------------------------------------------------------

def _clamp(value: float, lo: float, hi: float) -> float:
    return max(lo, min(hi, value))


def _sample_context(rng: random.Random, robot: RobotProfile) -> Dict[str, object]:
    """Sample the environmental context (when/where) for one episode."""
    day = rng.randint(0, N_DAYS - 1)

    if robot.home_id == RED_HERRING_HOME_ID:
        # This household mostly runs the robot after dinner, on carpet.
        hour = rng.randint(19, 23) if rng.random() < 0.85 else rng.randint(9, 17)
        floor_type = rng.choices(FLOOR_TYPES, weights=FLOOR_WEIGHTS_RED_HERRING, k=1)[0]
    else:
        hour = rng.randint(8, 22)
        floor_type = rng.choices(FLOOR_TYPES, weights=FLOOR_WEIGHTS_NORMAL, k=1)[0]

    # Lighting is driven by time of day -- this is what makes the
    # "home_003 is broken" correlation spurious rather than causal.
    p_dim = 0.85 if hour >= 19 else 0.08
    lighting = "dim" if rng.random() < p_dim else "bright"

    return {"day": day, "hour": hour, "floor_type": floor_type, "lighting": lighting}


def _pick_error_code(
    rng: random.Random, cause: str
) -> str:
    """Sample an error code consistent with the failure cause."""
    if cause == "grip_fault":
        return rng.choices(["GRIP_SLIP", "GRIP_STALL"], weights=[0.8, 0.2], k=1)[0]
    if cause == "cohort_regression":
        return rng.choices(
            ["VISION_MISDETECT", "GRASP_PLAN_FAIL", "TIMEOUT"],
            weights=[0.55, 0.30, 0.15],
            k=1,
        )[0]
    return rng.choices(
        ["TIMEOUT", "NAV_STUCK", "PLAN_FAIL", "E_STOP", "LOW_BATTERY"],
        weights=[0.35, 0.25, 0.20, 0.10, 0.10],
        k=1,
    )[0]


def simulate_episode(rng: random.Random, robot: RobotProfile) -> Dict[str, object]:
    """Simulate one episode for ``robot`` and return the telemetry record."""
    ctx = _sample_context(rng, robot)
    day: int = ctx["day"]  # type: ignore[assignment]

    model_version = (
        REGRESSED_MODEL_VERSION
        if robot.ota_day is not None and day >= robot.ota_day
        else "v2.3"
    )
    task_type = rng.choices(TASK_TYPES, weights=TASK_WEIGHTS, k=1)[0]
    battery_pct = rng.randint(15, 100)
    cpu_temp = round(_clamp(rng.gauss(54.0, 5.0), 38.0, 85.0), 1)

    if task_type in GRIP_TASKS:
        if robot.grip_faulty:
            grip_current = 1.20 + GRIP_DRIFT_A_PER_DAY * day + rng.gauss(0.0, 0.05)
        else:
            grip_current = rng.gauss(1.20, 0.07)
    else:
        grip_current = rng.gauss(0.30, 0.05)
    grip_current = round(max(0.05, grip_current), 3)

    if model_version == REGRESSED_MODEL_VERSION:
        policy_latency_ms = round(max(25.0, rng.gauss(88.0, 14.0)), 1)
    else:
        policy_latency_ms = round(max(25.0, rng.gauss(75.0, 12.0)), 1)

    # --- Success model -----------------------------------------------------
    p = BASE_SUCCESS_P
    if ctx["lighting"] == "dim":
        p -= 0.03
    if ctx["floor_type"] == "carpet":
        p -= 0.02
    if battery_pct < 20:
        p -= 0.08

    cause = "nominal"
    if (
        model_version == REGRESSED_MODEL_VERSION
        and ctx["floor_type"] == REGRESSED_FLOOR_TYPE
        and ctx["lighting"] == REGRESSED_LIGHTING
    ):
        p = COHORT_REGRESSION_SUCCESS_P
        cause = "cohort_regression"
    if (
        robot.grip_faulty
        and task_type in GRIP_TASKS
        and grip_current > GRIP_FAULT_THRESHOLD_A
    ):
        p = GRIP_FAULT_SUCCESS_P
        cause = "grip_fault"

    success = rng.random() < _clamp(p, 0.01, 0.99)
    error_code: Optional[str] = None if success else _pick_error_code(rng, cause)

    ts = "{d}T{h:02d}:{m:02d}:00Z".format(
        d=(START_DATE + timedelta(days=day)).isoformat(),
        h=ctx["hour"],
        m=rng.randint(0, 59),
    )

    return {
        "robot_id": robot.robot_id,
        "fw_version": robot.fw_version,
        "model_version": model_version,
        "task_type": task_type,
        "home_id": robot.home_id,
        "floor_type": ctx["floor_type"],
        "lighting": ctx["lighting"],
        "battery_pct": battery_pct,
        "cpu_temp": cpu_temp,
        "grip_current": grip_current,
        "policy_latency_ms": policy_latency_ms,
        "success": success,
        "error_code": error_code,
        "ts": ts,
    }


def generate_episodes(seed: int = DEFAULT_SEED) -> List[Dict[str, object]]:
    """Generate the full dataset, sorted by timestamp then robot_id."""
    rng = random.Random(seed)
    fleet = build_fleet(rng)
    records: List[Dict[str, object]] = []
    for robot in fleet:
        for _ in range(EPISODES_PER_ROBOT):
            records.append(simulate_episode(rng, robot))
    records.sort(key=lambda r: (r["ts"], r["robot_id"]))
    return records


def write_jsonl(records: List[Dict[str, object]], path: Path) -> None:
    """Write records as JSONL, creating parent directories as needed."""
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as fh:
        for rec in records:
            fh.write(json.dumps(rec, separators=(", ", ": ")) + "\n")


def summarize(records: List[Dict[str, object]]) -> str:
    """One-paragraph, spoiler-free summary for the console."""
    n = len(records)
    robots = {str(r["robot_id"]) for r in records}
    homes = {str(r["home_id"]) for r in records}
    ok = sum(1 for r in records if r["success"])
    return (
        "wrote {n} episodes | {nr} robots | {nh} homes | "
        "{d0}..{d1} | overall success {sr:.1%}".format(
            n=n,
            nr=len(robots),
            nh=len(homes),
            d0=str(records[0]["ts"])[:10],
            d1=str(records[-1]["ts"])[:10],
            sr=ok / n,
        )
    )


def main(argv: Optional[List[str]] = None) -> int:
    parser = argparse.ArgumentParser(description="Generate fleet telemetry JSONL.")
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT,
                        help="output JSONL path (default: data/episodes.jsonl)")
    parser.add_argument("--seed", type=int, default=DEFAULT_SEED,
                        help="RNG seed (default: %(default)s)")
    args = parser.parse_args(argv)

    records = generate_episodes(seed=args.seed)
    write_jsonl(records, args.out)
    print("[generate_logs] " + summarize(records))
    print("[generate_logs] output: {}".format(args.out))
    return 0


if __name__ == "__main__":
    sys.exit(main())
