#!/usr/bin/env python3
"""Teleop demonstration curation pipeline (lab3_data_engine).

Four independently testable stages, mirroring a fleet-learning data engine:

    Stage 1  validate_lines      raw JSONL -> DemoRecord | quarantine(reason)
    Stage 2  dedup_records       exact dups (content hash) + near dups
                                 (feature bucketing), keep-first, full audit
    Stage 3  filter_by_quality   explainable heuristic score vs. threshold
    Stage 4  stratify            per-task target mix -> train selection +
                                 collection request sheet for missing cohorts

Design notes
------------
* Standard library only; every stage is a pure function of (records, config)
  so each is unit-testable in isolation.
* Determinism: no wall clock in any decision, stable sort keys everywhere,
  keep-first dedup preserves input order semantics across incremental runs.
* This module owns the canonical schema, content hashing and bucketing keys;
  ``generate_demos.py`` imports them so injected duplicates are guaranteed to
  collide, and ``manifest.py`` imports them for incremental state.

Interpreter: Python 3.9 (no 3.10+ syntax).
"""

import argparse
import glob
import hashlib
import json
import os
from collections import defaultdict
from dataclasses import dataclass, field
from typing import Dict, Iterable, List, Optional, Sequence, Set, Tuple

# --------------------------------------------------------------------------
# Domain vocabulary (single source of truth, shared with the generator).
# --------------------------------------------------------------------------

KNOWN_TASKS = (
    "fold_towel",
    "load_dishwasher",
    "open_drawer",
    "pick_up_toys",
    "sort_laundry",
    "water_plants",
    "wipe_table",
)
ROOMS = ("bedroom", "kitchen", "laundry_room", "living_room")
LIGHTING_LEVELS = ("bright", "dark", "dim")
CLUTTER_LEVELS = ("high", "low", "medium")


class SchemaError(ValueError):
    """Raised when a raw payload violates the demo schema.

    The exception message doubles as the machine-readable quarantine reason,
    e.g. ``missing_field:task`` or ``bad_type:duration_s``.
    """


# --------------------------------------------------------------------------
# Configuration
# --------------------------------------------------------------------------


@dataclass(frozen=True)
class PipelineConfig:
    """All tunable knobs for the four stages.

    Frozen so a config snapshot stored in a manifest cannot drift from the
    config that actually produced the run.
    """

    known_tasks: Tuple[str, ...] = KNOWN_TASKS

    # Stage 1: schema bounds.
    min_duration_s: float = 1.0
    max_duration_s: float = 600.0

    # Stage 2: near-dup bucketing granularity.
    duration_bucket_s: float = 5.0
    steps_bucket: int = 50
    path_bucket_m: float = 1.0

    # Stage 3: quality heuristics (penalty weights are explainable on purpose).
    max_longest_pause_s: float = 20.0
    max_mean_jerk: float = 6.0
    max_retries: int = 3
    penalty_incomplete: float = 0.5
    penalty_pause: float = 0.35
    penalty_jerk: float = 0.35
    penalty_retries: float = 0.3
    quality_threshold: float = 0.75

    # Stage 4: stratified selection.
    train_budget: int = 420
    target_mix: Optional[Dict[str, float]] = None  # None -> uniform over tasks

    def resolved_target_mix(self) -> Dict[str, float]:
        """Return the task -> fraction target mix (uniform if unset)."""
        if self.target_mix is not None:
            return dict(self.target_mix)
        share = 1.0 / len(self.known_tasks)
        return {task: share for task in self.known_tasks}

    def to_dict(self) -> Dict[str, object]:
        """JSON-serializable snapshot for manifest lineage."""
        return {
            "known_tasks": list(self.known_tasks),
            "min_duration_s": self.min_duration_s,
            "max_duration_s": self.max_duration_s,
            "duration_bucket_s": self.duration_bucket_s,
            "steps_bucket": self.steps_bucket,
            "path_bucket_m": self.path_bucket_m,
            "max_longest_pause_s": self.max_longest_pause_s,
            "max_mean_jerk": self.max_mean_jerk,
            "max_retries": self.max_retries,
            "penalty_incomplete": self.penalty_incomplete,
            "penalty_pause": self.penalty_pause,
            "penalty_jerk": self.penalty_jerk,
            "penalty_retries": self.penalty_retries,
            "quality_threshold": self.quality_threshold,
            "train_budget": self.train_budget,
            "target_mix": self.resolved_target_mix(),
        }


# --------------------------------------------------------------------------
# Schema (records)
# --------------------------------------------------------------------------


def _get_present(payload: Dict[str, object], key: str, ctx: str) -> object:
    if key not in payload or payload[key] is None:
        raise SchemaError("missing_field:%s%s" % (ctx, key))
    return payload[key]


def _get_str(payload: Dict[str, object], key: str, ctx: str = "") -> str:
    value = _get_present(payload, key, ctx)
    if not isinstance(value, str) or not value:
        raise SchemaError("bad_type:%s%s" % (ctx, key))
    return value


def _get_bool(payload: Dict[str, object], key: str, ctx: str = "") -> bool:
    value = _get_present(payload, key, ctx)
    if not isinstance(value, bool):
        raise SchemaError("bad_type:%s%s" % (ctx, key))
    return value


def _get_float(
    payload: Dict[str, object],
    key: str,
    ctx: str = "",
    lo: Optional[float] = None,
    hi: Optional[float] = None,
) -> float:
    value = _get_present(payload, key, ctx)
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise SchemaError("bad_type:%s%s" % (ctx, key))
    number = float(value)
    if (lo is not None and number < lo) or (hi is not None and number > hi):
        raise SchemaError("out_of_range:%s%s" % (ctx, key))
    return number


def _get_int(
    payload: Dict[str, object],
    key: str,
    ctx: str = "",
    lo: Optional[int] = None,
) -> int:
    value = _get_present(payload, key, ctx)
    if isinstance(value, bool) or not isinstance(value, int):
        raise SchemaError("bad_type:%s%s" % (ctx, key))
    if lo is not None and value < lo:
        raise SchemaError("out_of_range:%s%s" % (ctx, key))
    return value


def _get_obj(payload: Dict[str, object], key: str) -> Dict[str, object]:
    value = _get_present(payload, key, "")
    if not isinstance(value, dict):
        raise SchemaError("bad_type:%s" % key)
    return value


@dataclass(frozen=True)
class Scene:
    """Static scene context captured at collection time."""

    room: str
    lighting: str
    clutter: str
    num_objects: int

    @classmethod
    def from_dict(cls, payload: Dict[str, object]) -> "Scene":
        return cls(
            room=_get_str(payload, "room", "scene."),
            lighting=_get_str(payload, "lighting", "scene."),
            clutter=_get_str(payload, "clutter", "scene."),
            num_objects=_get_int(payload, "num_objects", "scene.", lo=0),
        )

    def to_dict(self) -> Dict[str, object]:
        return {
            "room": self.room,
            "lighting": self.lighting,
            "clutter": self.clutter,
            "num_objects": self.num_objects,
        }


@dataclass(frozen=True)
class TrajStats:
    """Summary statistics of one teleop trajectory (not the raw traces)."""

    num_steps: int
    mean_jerk: float
    max_jerk: float
    num_pauses: int
    longest_pause_s: float
    num_retries: int
    path_length_m: float

    @classmethod
    def from_dict(cls, payload: Dict[str, object]) -> "TrajStats":
        return cls(
            num_steps=_get_int(payload, "num_steps", "traj.", lo=1),
            mean_jerk=_get_float(payload, "mean_jerk", "traj.", lo=0.0),
            max_jerk=_get_float(payload, "max_jerk", "traj.", lo=0.0),
            num_pauses=_get_int(payload, "num_pauses", "traj.", lo=0),
            longest_pause_s=_get_float(payload, "longest_pause_s", "traj.", lo=0.0),
            num_retries=_get_int(payload, "num_retries", "traj.", lo=0),
            path_length_m=_get_float(payload, "path_length_m", "traj.", lo=0.0),
        )

    def to_dict(self) -> Dict[str, object]:
        return {
            "num_steps": self.num_steps,
            "mean_jerk": self.mean_jerk,
            "max_jerk": self.max_jerk,
            "num_pauses": self.num_pauses,
            "longest_pause_s": self.longest_pause_s,
            "num_retries": self.num_retries,
            "path_length_m": self.path_length_m,
        }


@dataclass(frozen=True)
class DemoRecord:
    """One validated teleop demonstration (metadata + trajectory summary)."""

    demo_id: str
    task: str
    operator_id: str
    scene: Scene
    traj: TrajStats
    duration_s: float
    completed: bool
    collected_at: str

    @classmethod
    def from_dict(
        cls, payload: Dict[str, object], config: PipelineConfig
    ) -> "DemoRecord":
        """Parse and validate a raw payload; raises SchemaError with reason."""
        task = _get_str(payload, "task")
        if task not in config.known_tasks:
            raise SchemaError("unknown_task:%s" % task)
        return cls(
            demo_id=_get_str(payload, "demo_id"),
            task=task,
            operator_id=_get_str(payload, "operator_id"),
            scene=Scene.from_dict(_get_obj(payload, "scene")),
            traj=TrajStats.from_dict(_get_obj(payload, "traj")),
            duration_s=_get_float(
                payload,
                "duration_s",
                lo=config.min_duration_s,
                hi=config.max_duration_s,
            ),
            completed=_get_bool(payload, "completed"),
            collected_at=_get_str(payload, "collected_at"),
        )

    def to_dict(self) -> Dict[str, object]:
        return {
            "demo_id": self.demo_id,
            "task": self.task,
            "operator_id": self.operator_id,
            "scene": self.scene.to_dict(),
            "traj": self.traj.to_dict(),
            "duration_s": self.duration_s,
            "completed": self.completed,
            "collected_at": self.collected_at,
        }


# --------------------------------------------------------------------------
# Content identity (shared by dedup, generator, and manifest state)
# --------------------------------------------------------------------------


def content_hash(payload: Dict[str, object]) -> str:
    """sha256 of the canonical record content, excluding the assigned id.

    Two uploads of the same demo differ only in ``demo_id``; everything else
    identical means the same content.
    """
    body = {key: value for key, value in payload.items() if key != "demo_id"}
    canonical = json.dumps(body, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def near_dup_key(payload: Dict[str, object], config: PipelineConfig) -> str:
    """Coarse feature bucket: same task/operator/scene + quantized geometry.

    Records landing in the same bucket are near-duplicates: they add almost
    no new information to the training set, so we keep only the first.
    """
    scene = payload["scene"]
    traj = payload["traj"]
    return "|".join(
        [
            str(payload["task"]),
            str(payload["operator_id"]),
            str(scene["room"]),
            str(scene["lighting"]),
            str(scene["clutter"]),
            str(int(float(payload["duration_s"]) // config.duration_bucket_s)),
            str(int(int(traj["num_steps"]) // config.steps_bucket)),
            str(int(round(float(traj["path_length_m"]) / config.path_bucket_m))),
        ]
    )


# --------------------------------------------------------------------------
# Stage 1: schema validation
# --------------------------------------------------------------------------


@dataclass(frozen=True)
class QuarantinedLine:
    """One rejected raw line, with provenance and a machine-readable reason."""

    source: str
    line_no: int
    reason: str
    raw_prefix: str

    def to_dict(self) -> Dict[str, object]:
        return {
            "source": self.source,
            "line_no": self.line_no,
            "reason": self.reason,
            "raw_prefix": self.raw_prefix,
        }


def validate_lines(
    lines: Iterable[str],
    config: PipelineConfig,
    seen_ids: Optional[Set[str]] = None,
    source: str = "<memory>",
) -> Tuple[List[DemoRecord], List[QuarantinedLine]]:
    """Stage 1: parse raw JSONL lines into DemoRecords.

    Bad lines are never dropped silently: each goes to quarantine with the
    line number, a reason, and a prefix of the raw payload for debugging.
    ``seen_ids`` lets incremental runs reject demo_id collisions with
    already-ingested batches.
    """
    seen: Set[str] = set(seen_ids) if seen_ids is not None else set()
    records: List[DemoRecord] = []
    quarantined: List[QuarantinedLine] = []

    for line_no, raw in enumerate(lines, start=1):
        stripped = raw.strip()
        if not stripped:
            continue

        def _quarantine(reason: str) -> None:
            quarantined.append(
                QuarantinedLine(
                    source=source,
                    line_no=line_no,
                    reason=reason,
                    raw_prefix=stripped[:120],
                )
            )

        try:
            payload = json.loads(stripped)
        except json.JSONDecodeError:
            _quarantine("malformed_json")
            continue
        if not isinstance(payload, dict):
            _quarantine("not_an_object")
            continue
        try:
            record = DemoRecord.from_dict(payload, config)
        except SchemaError as exc:
            _quarantine(str(exc))
            continue
        if record.demo_id in seen:
            _quarantine("duplicate_demo_id:%s" % record.demo_id)
            continue
        seen.add(record.demo_id)
        records.append(record)

    return records, quarantined


# --------------------------------------------------------------------------
# Stage 2: deduplication
# --------------------------------------------------------------------------


@dataclass(frozen=True)
class DropEntry:
    """Audit trail for one dropped duplicate."""

    demo_id: str
    reason: str  # "exact_duplicate" | "near_duplicate"
    duplicate_of: str

    def to_dict(self) -> Dict[str, object]:
        return {
            "demo_id": self.demo_id,
            "reason": self.reason,
            "duplicate_of": self.duplicate_of,
        }


@dataclass
class DedupResult:
    """Kept records plus updated indices (for incremental state carry-over)."""

    kept: List[DemoRecord]
    dropped: List[DropEntry]
    exact_index: Dict[str, str]  # content hash -> kept demo_id
    bucket_index: Dict[str, str]  # near-dup bucket key -> kept demo_id


def dedup_records(
    records: Sequence[DemoRecord],
    config: PipelineConfig,
    exact_index: Optional[Dict[str, str]] = None,
    bucket_index: Optional[Dict[str, str]] = None,
) -> DedupResult:
    """Stage 2: keep-first exact + near dedup.

    Exact dups (same content hash, only the id differs) are checked before
    near dups so the audit reason is as precise as possible. Passing the
    indices from a previous run makes this stage incremental: new records
    are deduped against everything already kept.
    """
    exact = dict(exact_index) if exact_index is not None else {}
    buckets = dict(bucket_index) if bucket_index is not None else {}
    kept: List[DemoRecord] = []
    dropped: List[DropEntry] = []

    for record in records:
        payload = record.to_dict()
        digest = content_hash(payload)
        if digest in exact:
            dropped.append(
                DropEntry(record.demo_id, "exact_duplicate", exact[digest])
            )
            continue
        bucket = near_dup_key(payload, config)
        if bucket in buckets:
            dropped.append(
                DropEntry(record.demo_id, "near_duplicate", buckets[bucket])
            )
            continue
        exact[digest] = record.demo_id
        buckets[bucket] = record.demo_id
        kept.append(record)

    return DedupResult(kept=kept, dropped=dropped, exact_index=exact, bucket_index=buckets)


# --------------------------------------------------------------------------
# Stage 3: quality filtering
# --------------------------------------------------------------------------


@dataclass(frozen=True)
class QualityAssessment:
    """Explainable score: 1.0 minus named penalties, clamped to [0, 1]."""

    demo_id: str
    score: float
    penalties: Tuple[str, ...]

    def to_dict(self) -> Dict[str, object]:
        return {
            "demo_id": self.demo_id,
            "score": self.score,
            "penalties": list(self.penalties),
        }


def assess_quality(record: DemoRecord, config: PipelineConfig) -> QualityAssessment:
    """Score one demo with human-readable penalty reasons.

    Heuristics (all thresholds live in the config, not in code):
      * incomplete demo        -> heavy penalty (label noise for BC)
      * very long pause        -> operator hesitation / distraction
      * high mean jerk         -> shaky teleoperation, poor action targets
      * too many retries       -> demonstrated strategy is unreliable
    """
    score = 1.0
    penalties: List[str] = []

    if not record.completed:
        score -= config.penalty_incomplete
        penalties.append("incomplete(-%.2f)" % config.penalty_incomplete)
    if record.traj.longest_pause_s > config.max_longest_pause_s:
        score -= config.penalty_pause
        penalties.append(
            "longest_pause_s=%.1f>%.1f(-%.2f)"
            % (
                record.traj.longest_pause_s,
                config.max_longest_pause_s,
                config.penalty_pause,
            )
        )
    if record.traj.mean_jerk > config.max_mean_jerk:
        score -= config.penalty_jerk
        penalties.append(
            "mean_jerk=%.1f>%.1f(-%.2f)"
            % (record.traj.mean_jerk, config.max_mean_jerk, config.penalty_jerk)
        )
    if record.traj.num_retries > config.max_retries:
        score -= config.penalty_retries
        penalties.append(
            "num_retries=%d>%d(-%.2f)"
            % (record.traj.num_retries, config.max_retries, config.penalty_retries)
        )

    return QualityAssessment(
        demo_id=record.demo_id,
        score=round(max(score, 0.0), 4),
        penalties=tuple(penalties),
    )


def filter_by_quality(
    records: Sequence[DemoRecord], config: PipelineConfig
) -> Tuple[List[DemoRecord], List[QualityAssessment]]:
    """Stage 3: keep records scoring >= threshold; return rejections with reasons."""
    kept: List[DemoRecord] = []
    rejected: List[QualityAssessment] = []
    for record in records:
        assessment = assess_quality(record, config)
        if assessment.score >= config.quality_threshold:
            kept.append(record)
        else:
            rejected.append(assessment)
    return kept, rejected


# --------------------------------------------------------------------------
# Stage 4: stratified selection + collection requests
# --------------------------------------------------------------------------


@dataclass(frozen=True)
class CollectionRequest:
    """One line of the collection request sheet handed back to teleop ops.

    This is the curation -> collection feedback loop: instead of silently
    shipping an unbalanced training set, the pipeline says exactly which
    cohort is short and what to prioritize next.
    """

    task: str
    have: int
    target: int
    gap: int
    scarcest_lighting: str
    scarcest_room: str
    note: str

    def to_dict(self) -> Dict[str, object]:
        return {
            "task": self.task,
            "have": self.have,
            "target": self.target,
            "gap": self.gap,
            "scarcest_lighting": self.scarcest_lighting,
            "scarcest_room": self.scarcest_room,
            "note": self.note,
        }


@dataclass
class StratifyResult:
    selected: List[DemoRecord]
    requests: List[CollectionRequest]
    per_task_selected: Dict[str, int]
    target_counts: Dict[str, int]


def compute_target_counts(config: PipelineConfig) -> Dict[str, int]:
    """Turn the fractional target mix into integer counts (largest remainder).

    Guarantees ``sum(counts) == train_budget`` with deterministic tie-breaks.
    """
    mix = config.resolved_target_mix()
    total = sum(mix.values())
    if abs(total - 1.0) > 1e-6:
        raise ValueError("target_mix fractions must sum to 1.0, got %.6f" % total)

    exact = {task: config.train_budget * frac for task, frac in mix.items()}
    counts = {task: int(value) for task, value in exact.items()}
    remainder = config.train_budget - sum(counts.values())
    by_fraction = sorted(mix, key=lambda task: (-(exact[task] - counts[task]), task))
    for task in by_fraction[:remainder]:
        counts[task] += 1
    return counts


def _scarcest(
    records: Sequence[DemoRecord], attr: str, domain: Sequence[str]
) -> str:
    """Least represented value of ``scene.<attr>`` (alphabetical tie-break)."""
    counts = {value: 0 for value in domain}
    for record in records:
        value = getattr(record.scene, attr)
        if value in counts:
            counts[value] += 1
    return min(sorted(counts), key=lambda value: counts[value])


def stratify(records: Sequence[DemoRecord], config: PipelineConfig) -> StratifyResult:
    """Stage 4: resample toward the target task mix.

    Surplus tasks: keep the top-``target`` demos by quality score (stable
    tie-break on demo_id). Deficit tasks: keep everything AND emit a
    collection request quantifying the gap plus scene-cohort hints.
    """
    scores = {r.demo_id: assess_quality(r, config).score for r in records}
    by_task: Dict[str, List[DemoRecord]] = defaultdict(list)
    for record in records:
        by_task[record.task].append(record)

    targets = compute_target_counts(config)
    selected: List[DemoRecord] = []
    requests: List[CollectionRequest] = []
    per_task_selected: Dict[str, int] = {}

    for task in sorted(targets):
        candidates = sorted(
            by_task.get(task, []),
            key=lambda r: (-scores[r.demo_id], r.demo_id),
        )
        target = targets[task]
        if len(candidates) >= target:
            chosen = candidates[:target]
        else:
            chosen = candidates
            scarcest_lighting = _scarcest(candidates, "lighting", LIGHTING_LEVELS)
            scarcest_room = _scarcest(candidates, "room", ROOMS)
            if candidates:
                note = (
                    "need %d more '%s' demos; prioritize %s lighting in %s"
                    % (target - len(candidates), task, scarcest_lighting, scarcest_room)
                )
            else:
                note = "no usable demos for '%s'; bootstrap collection" % task
            requests.append(
                CollectionRequest(
                    task=task,
                    have=len(candidates),
                    target=target,
                    gap=target - len(candidates),
                    scarcest_lighting=scarcest_lighting,
                    scarcest_room=scarcest_room,
                    note=note,
                )
            )
        selected.extend(chosen)
        per_task_selected[task] = len(chosen)

    requests.sort(key=lambda req: (-req.gap, req.task))
    return StratifyResult(
        selected=selected,
        requests=requests,
        per_task_selected=per_task_selected,
        target_counts=targets,
    )


# --------------------------------------------------------------------------
# One-shot CLI (no manifest/state; see manifest.py for incremental runs)
# --------------------------------------------------------------------------


def _write_json(path: str, obj: object) -> None:
    with open(path, "w", encoding="utf-8") as handle:
        json.dump(obj, handle, indent=2, sort_keys=True)
        handle.write("\n")


def main() -> None:
    lab_dir = os.path.dirname(os.path.abspath(__file__))
    parser = argparse.ArgumentParser(description="One-shot curation run (no state).")
    parser.add_argument(
        "--data-dir", default=os.path.join(lab_dir, "data"), help="dir with *.jsonl"
    )
    parser.add_argument(
        "--workdir", default=os.path.join(lab_dir, "out_oneshot"), help="output dir"
    )
    parser.add_argument("--budget", type=int, default=420)
    parser.add_argument("--quality-threshold", type=float, default=0.75)
    args = parser.parse_args()

    config = PipelineConfig(
        train_budget=args.budget, quality_threshold=args.quality_threshold
    )
    paths = sorted(glob.glob(os.path.join(args.data_dir, "*.jsonl")))
    if not paths:
        raise SystemExit("no .jsonl files under %s (run generate_demos.py first)" % args.data_dir)
    os.makedirs(args.workdir, exist_ok=True)

    all_records: List[DemoRecord] = []
    all_quarantined: List[QuarantinedLine] = []
    seen_ids: Set[str] = set()
    total_lines = 0
    for path in paths:
        with open(path, "r", encoding="utf-8") as handle:
            lines = handle.read().splitlines()
        total_lines += len(lines)
        records, quarantined = validate_lines(
            lines, config, seen_ids=seen_ids, source=os.path.basename(path)
        )
        seen_ids.update(record.demo_id for record in records)
        all_records.extend(records)
        all_quarantined.extend(quarantined)

    dedup = dedup_records(all_records, config)
    kept_quality, rejected = filter_by_quality(dedup.kept, config)
    strat = stratify(kept_quality, config)

    with open(os.path.join(args.workdir, "quarantine.jsonl"), "w", encoding="utf-8") as handle:
        for entry in all_quarantined:
            handle.write(json.dumps(entry.to_dict(), sort_keys=True) + "\n")
    _write_json(
        os.path.join(args.workdir, "dedup_report.json"),
        [entry.to_dict() for entry in dedup.dropped],
    )
    _write_json(
        os.path.join(args.workdir, "quality_report.json"),
        [entry.to_dict() for entry in rejected],
    )
    _write_json(
        os.path.join(args.workdir, "collection_requests.json"),
        [request.to_dict() for request in strat.requests],
    )
    with open(os.path.join(args.workdir, "train_set.jsonl"), "w", encoding="utf-8") as handle:
        for record in sorted(strat.selected, key=lambda r: r.demo_id):
            handle.write(json.dumps(record.to_dict(), sort_keys=True) + "\n")

    counts = {
        "input_lines": total_lines,
        "quarantined": len(all_quarantined),
        "validated": len(all_records),
        "dropped_exact": sum(1 for d in dedup.dropped if d.reason == "exact_duplicate"),
        "dropped_near": sum(1 for d in dedup.dropped if d.reason == "near_duplicate"),
        "after_dedup": len(dedup.kept),
        "rejected_quality": len(rejected),
        "after_quality": len(kept_quality),
        "selected": len(strat.selected),
    }
    _write_json(os.path.join(args.workdir, "stage_counts.json"), counts)

    print("stage funnel:")
    for key in [
        "input_lines",
        "quarantined",
        "validated",
        "dropped_exact",
        "dropped_near",
        "after_dedup",
        "rejected_quality",
        "after_quality",
        "selected",
    ]:
        print("  %-18s %d" % (key, counts[key]))
    print("collection requests (%d):" % len(strat.requests))
    for request in strat.requests:
        print(
            "  %-16s have=%-4d target=%-4d gap=%-4d %s"
            % (request.task, request.have, request.target, request.gap, request.note)
        )
    print("outputs -> %s" % args.workdir)


if __name__ == "__main__":
    main()
