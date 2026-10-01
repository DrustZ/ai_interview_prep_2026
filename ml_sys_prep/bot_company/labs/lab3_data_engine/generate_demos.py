#!/usr/bin/env python3
"""Deterministic generator of synthetic teleop demonstration JSONL batches.

Produces ~800 records (batch 1) with known, labeled defects so the pipeline
stages have ground truth to be tested against:

  * clean demos       -- realistic metadata + trajectory summaries
  * bad-quality demos -- overlong pauses / shaky (high jerk) / incomplete
  * exact duplicates  -- same content re-uploaded under a new demo_id
  * near duplicates   -- same operator re-doing the same scene, tiny deltas
  * schema-bad lines  -- malformed JSON, missing/typed-wrong fields, etc.

The generator intentionally imports ``content_hash`` / ``near_dup_key`` from
``pipeline`` so the injected duplicates are *guaranteed* to collide under the
pipeline's own definitions (honest test fixtures, no coincidences).

Interpreter: Python 3.9 (no 3.10+ syntax). Standard library only.
"""

import argparse
import copy
import json
import os
import random
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple

from pipeline import (
    CLUTTER_LEVELS,
    KNOWN_TASKS,
    LIGHTING_LEVELS,
    ROOMS,
    DemoRecord,
    PipelineConfig,
    SchemaError,
    content_hash,
    near_dup_key,
)

# Deliberately imbalanced so stage 4 has both surplus and deficit tasks.
TASK_WEIGHTS: Dict[str, float] = {
    "wipe_table": 0.24,
    "load_dishwasher": 0.22,
    "pick_up_toys": 0.20,
    "fold_towel": 0.14,
    "open_drawer": 0.10,
    "water_plants": 0.06,
    "sort_laundry": 0.04,
}

_SCHEMA_BAD_KINDS = (
    "malformed_json",
    "missing_task",
    "duration_as_string",
    "negative_duration",
    "unknown_task",
    "null_operator",
)


@dataclass(frozen=True)
class BatchSpec:
    """Composition of one generated batch (all counts are exact)."""

    batch: int
    n_clean: int
    n_bad_quality: int
    n_exact_dups: int
    n_near_dups: int
    n_schema_bad: int
    n_cross_dups: int = 0
    seed: int = 7
    day_lo: int = 1
    day_hi: int = 5


BATCH1 = BatchSpec(
    batch=1,
    n_clean=700,
    n_bad_quality=40,
    n_exact_dups=25,
    n_near_dups=30,
    n_schema_bad=12,
)
BATCH2 = BatchSpec(
    batch=2,
    n_clean=100,
    n_bad_quality=6,
    n_exact_dups=5,
    n_near_dups=5,
    n_schema_bad=6,
    n_cross_dups=5,
    day_lo=6,
    day_hi=7,
)


@dataclass
class GenerationSummary:
    """Ground truth about what was injected (consumed by test_pipeline.py)."""

    batch: int
    total_lines: int
    n_clean: int
    bad_quality_ids: List[str] = field(default_factory=list)
    exact_dup_ids: List[str] = field(default_factory=list)
    near_dup_ids: List[str] = field(default_factory=list)
    cross_dup_ids: List[str] = field(default_factory=list)
    schema_bad_lines: List[int] = field(default_factory=list)  # 1-based

    @property
    def n_schema_valid(self) -> int:
        return self.total_lines - len(self.schema_bad_lines)

    def to_dict(self) -> Dict[str, object]:
        return {
            "batch": self.batch,
            "total_lines": self.total_lines,
            "n_clean": self.n_clean,
            "n_schema_valid": self.n_schema_valid,
            "bad_quality_ids": self.bad_quality_ids,
            "exact_dup_ids": self.exact_dup_ids,
            "near_dup_ids": self.near_dup_ids,
            "cross_dup_ids": self.cross_dup_ids,
            "schema_bad_lines": self.schema_bad_lines,
        }


def _weighted_task(rng: random.Random) -> str:
    tasks = list(TASK_WEIGHTS)
    weights = [TASK_WEIGHTS[task] for task in tasks]
    return rng.choices(tasks, weights=weights, k=1)[0]


def _make_clean(rng: random.Random, spec: BatchSpec, demo_id: str) -> Dict[str, object]:
    """One schema-valid, quality-passing record (score == 1.0 by construction)."""
    duration = round(rng.uniform(20.0, 180.0), 3)
    num_pauses = rng.randint(0, 5)
    mean_jerk = round(rng.uniform(0.5, 4.0), 3)
    return {
        "demo_id": demo_id,
        "task": _weighted_task(rng),
        "operator_id": "op_%02d" % rng.randint(1, 10),
        "scene": {
            "room": rng.choice(ROOMS),
            "lighting": rng.choices(LIGHTING_LEVELS, weights=[0.6, 0.1, 0.3], k=1)[0],
            "clutter": rng.choice(CLUTTER_LEVELS),
            "num_objects": rng.randint(2, 15),
        },
        "duration_s": duration,
        "traj": {
            "num_steps": int(duration * rng.uniform(8.0, 12.0)),
            "mean_jerk": mean_jerk,
            "max_jerk": round(mean_jerk * rng.uniform(1.5, 3.0), 3),
            "num_pauses": num_pauses,
            "longest_pause_s": round(rng.uniform(0.5, 12.0), 3) if num_pauses else 0.0,
            "num_retries": rng.randint(0, 2),
            "path_length_m": round(rng.uniform(1.0, 12.0), 3),
        },
        "completed": True,
        "collected_at": "2026-08-%02d" % rng.randint(spec.day_lo, spec.day_hi),
    }


def _make_bad_quality(
    rng: random.Random, spec: BatchSpec, demo_id: str, mode: int
) -> Dict[str, object]:
    """Clean record degraded by one decisive defect mode (cycled by caller)."""
    record = _make_clean(rng, spec, demo_id)
    defect = mode % 3
    if defect == 0:  # operator froze / got distracted
        record["traj"]["num_pauses"] = max(3, int(record["traj"]["num_pauses"]))
        record["traj"]["longest_pause_s"] = round(rng.uniform(45.0, 90.0), 3)
    elif defect == 1:  # shaky teleoperation
        mean_jerk = round(rng.uniform(9.0, 15.0), 3)
        record["traj"]["mean_jerk"] = mean_jerk
        record["traj"]["max_jerk"] = round(mean_jerk * 2.0, 3)
    else:  # gave up after many retries
        record["completed"] = False
        record["traj"]["num_retries"] = rng.randint(5, 8)
    return record


def _make_near_dup(
    rng: random.Random,
    source: Dict[str, object],
    demo_id: str,
    config: PipelineConfig,
) -> Dict[str, object]:
    """Same operator/scene/geometry, jitter only fine-grained trajectory stats.

    Guaranteed (and asserted) to land in the same near-dup bucket as the
    source while having a different content hash.
    """
    dup = copy.deepcopy(source)
    dup["demo_id"] = demo_id
    delta = rng.choice([-1.0, 1.0]) * round(rng.uniform(0.05, 0.25), 3)
    dup["traj"]["mean_jerk"] = round(float(source["traj"]["mean_jerk"]) + delta, 3)
    dup["traj"]["longest_pause_s"] = round(
        float(source["traj"]["longest_pause_s"]) + rng.uniform(0.0, 0.8), 3
    )
    if near_dup_key(dup, config) != near_dup_key(source, config):
        raise AssertionError("near-dup injection left its bucket: %s" % demo_id)
    if content_hash(dup) == content_hash(source):
        raise AssertionError("near-dup injection produced an exact dup: %s" % demo_id)
    return dup


def _make_exact_dup(source: Dict[str, object], demo_id: str) -> Dict[str, object]:
    """Identical content re-uploaded under a fresh demo_id."""
    dup = copy.deepcopy(source)
    dup["demo_id"] = demo_id
    if content_hash(dup) != content_hash(source):
        raise AssertionError("exact-dup injection changed content: %s" % demo_id)
    return dup


def _make_schema_bad(
    rng: random.Random, spec: BatchSpec, demo_id: str, kind: str
) -> str:
    """One raw line violating the schema in a specific, labeled way."""
    record = _make_clean(rng, spec, demo_id)
    if kind == "malformed_json":
        return '{"demo_id": "%s", "task": ' % demo_id  # truncated upload
    if kind == "missing_task":
        del record["task"]
    elif kind == "duration_as_string":
        record["duration_s"] = "%.1fs" % float(record["duration_s"])
    elif kind == "negative_duration":
        record["duration_s"] = -5.0
    elif kind == "unknown_task":
        record["task"] = "juggle_chainsaws"
    elif kind == "null_operator":
        record["operator_id"] = None
    else:
        raise ValueError("unknown schema-bad kind: %s" % kind)
    return json.dumps(record, sort_keys=True)


def eligible_cross_sources(
    lines: List[str], summary: GenerationSummary, config: PipelineConfig
) -> List[Dict[str, object]]:
    """Payloads from a previous batch that are safe exact-dup sources.

    Excludes that batch's own near/exact dup copies: near-dup copies were
    dropped at dedup, so their content hash never entered the kept index and
    a copy of them would surface as a *near* (not exact) duplicate.
    """
    excluded = set(summary.near_dup_ids) | set(summary.exact_dup_ids)
    sources: List[Dict[str, object]] = []
    for line in lines:
        try:
            payload = json.loads(line)
        except json.JSONDecodeError:
            continue
        if not isinstance(payload, dict):
            continue
        try:
            DemoRecord.from_dict(payload, config)
        except SchemaError:
            continue
        if payload["demo_id"] not in excluded:
            sources.append(payload)
    return sources


def generate_batch(
    spec: BatchSpec,
    cross_sources: Optional[List[Dict[str, object]]] = None,
    config: Optional[PipelineConfig] = None,
) -> Tuple[List[str], GenerationSummary]:
    """Generate one batch as raw JSONL lines plus its ground-truth summary.

    Layout: shuffled base (clean + bad-quality), then near dups, then exact
    dups, then cross-batch dups, then schema-bad lines. Duplicate copies
    always appear *after* their sources so keep-first dedup drops exactly
    the injected ids.
    """
    if spec.n_cross_dups and not cross_sources:
        raise ValueError("batch %d needs cross_sources for cross-batch dups" % spec.batch)
    config = config or PipelineConfig()
    rng = random.Random(spec.seed * 1000 + spec.batch)

    counter = {"next": 0}

    def next_id() -> str:
        counter["next"] += 1
        return "d%d_%05d" % (spec.batch, counter["next"])

    clean = [_make_clean(rng, spec, next_id()) for _ in range(spec.n_clean)]
    bad = [
        _make_bad_quality(rng, spec, next_id(), mode=index)
        for index in range(spec.n_bad_quality)
    ]
    base = clean + bad
    rng.shuffle(base)

    near_dups = [
        _make_near_dup(rng, source, next_id(), config)
        for source in rng.sample(clean, spec.n_near_dups)
    ]
    exact_dups = [
        _make_exact_dup(source, next_id())
        for source in rng.sample(clean, spec.n_exact_dups)
    ]
    cross_dups = []
    if spec.n_cross_dups:
        cross_dups = [
            _make_exact_dup(source, next_id())
            for source in rng.sample(list(cross_sources or []), spec.n_cross_dups)
        ]

    lines = [
        json.dumps(record, sort_keys=True)
        for record in base + near_dups + exact_dups + cross_dups
    ]
    schema_bad_lines: List[int] = []
    for index in range(spec.n_schema_bad):
        kind = _SCHEMA_BAD_KINDS[index % len(_SCHEMA_BAD_KINDS)]
        lines.append(_make_schema_bad(rng, spec, next_id(), kind))
        schema_bad_lines.append(len(lines))

    summary = GenerationSummary(
        batch=spec.batch,
        total_lines=len(lines),
        n_clean=spec.n_clean,
        bad_quality_ids=[record["demo_id"] for record in bad],
        exact_dup_ids=[record["demo_id"] for record in exact_dups],
        near_dup_ids=[record["demo_id"] for record in near_dups],
        cross_dup_ids=[record["demo_id"] for record in cross_dups],
        schema_bad_lines=schema_bad_lines,
    )
    return lines, summary


def write_batch(lines: List[str], summary: GenerationSummary, out_path: str) -> str:
    """Write the JSONL plus a ``<name>.summary.json`` ground-truth sidecar."""
    out_dir = os.path.dirname(os.path.abspath(out_path))
    os.makedirs(out_dir, exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as handle:
        handle.write("\n".join(lines) + "\n")
    sidecar = os.path.splitext(out_path)[0] + ".summary.json"
    with open(sidecar, "w", encoding="utf-8") as handle:
        json.dump(summary.to_dict(), handle, indent=2, sort_keys=True)
        handle.write("\n")
    return sidecar


def main() -> None:
    lab_dir = os.path.dirname(os.path.abspath(__file__))
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--batch", type=int, choices=(1, 2), default=1)
    parser.add_argument("--out", default=None, help="output .jsonl path")
    parser.add_argument("--seed", type=int, default=7)
    parser.add_argument(
        "--cross-dup-from",
        default=None,
        help="batch-1 jsonl (with .summary.json sidecar) for cross-batch dups",
    )
    args = parser.parse_args()

    config = PipelineConfig()
    spec = BATCH1 if args.batch == 1 else BATCH2
    spec = BatchSpec(**{**spec.__dict__, "seed": args.seed})

    cross_sources: Optional[List[Dict[str, object]]] = None
    if spec.n_cross_dups:
        if not args.cross_dup_from:
            raise SystemExit("--cross-dup-from is required for batch 2")
        with open(args.cross_dup_from, "r", encoding="utf-8") as handle:
            source_lines = handle.read().splitlines()
        sidecar_path = os.path.splitext(args.cross_dup_from)[0] + ".summary.json"
        with open(sidecar_path, "r", encoding="utf-8") as handle:
            sidecar = json.load(handle)
        source_summary = GenerationSummary(
            batch=sidecar["batch"],
            total_lines=sidecar["total_lines"],
            n_clean=sidecar["n_clean"],
            bad_quality_ids=sidecar["bad_quality_ids"],
            exact_dup_ids=sidecar["exact_dup_ids"],
            near_dup_ids=sidecar["near_dup_ids"],
            cross_dup_ids=sidecar["cross_dup_ids"],
            schema_bad_lines=sidecar["schema_bad_lines"],
        )
        cross_sources = eligible_cross_sources(source_lines, source_summary, config)

    out_path = args.out or os.path.join(
        lab_dir, "data", "demos_batch%d.jsonl" % spec.batch
    )
    lines, summary = generate_batch(spec, cross_sources=cross_sources, config=config)
    sidecar = write_batch(lines, summary, out_path)

    print("wrote %d lines -> %s" % (summary.total_lines, out_path))
    print("ground truth   -> %s" % sidecar)
    print(
        "  clean=%d bad_quality=%d near_dups=%d exact_dups=%d cross_dups=%d schema_bad=%d"
        % (
            summary.n_clean,
            len(summary.bad_quality_ids),
            len(summary.near_dup_ids),
            len(summary.exact_dup_ids),
            len(summary.cross_dup_ids),
            len(summary.schema_bad_lines),
        )
    )


if __name__ == "__main__":
    main()
