#!/usr/bin/env python3
"""Content-addressed training-set manifests with lineage + incremental runs.

Manifest identity
-----------------
``manifest_id = sha256("\n".join(sorted(selected_demo_ids)))`` -- the id is a
function of *what is in the training set*, nothing else. Re-running on the
same inputs with the same config reproduces the same id, whether the data
arrived in one shot or incrementally.

Lineage
-------
Each manifest records its parent manifest id, a full pipeline-config
snapshot, and the sha256 of every input file that fed it, so any training
set can be traced back to raw batches and the exact knobs used.

Incremental runs
----------------
``run_incremental`` keeps a state file per workdir:
  * input files already processed (by name + sha256)  -> skipped on rerun
  * dedup indices (content hash / near-dup bucket)    -> new batches are
    deduped against everything already kept, without re-reading old batches
  * post-dedup survivors                              -> stages 3-4 (quality,
    stratification) are cheap global recomputations over the survivor pool
Only stages 1-2 ever touch raw data, so a rerun processes *only new files*;
a rerun with no new files is a no-op returning the existing manifest.

Interpreter: Python 3.9 (no 3.10+ syntax). Standard library only.
"""

import argparse
import datetime
import glob
import hashlib
import json
import os
from dataclasses import dataclass
from typing import Dict, Iterable, List, Optional, Set, Tuple

from pipeline import (
    DemoRecord,
    PipelineConfig,
    dedup_records,
    filter_by_quality,
    stratify,
    validate_lines,
)

STATE_FILENAME = "state.json"
MANIFEST_DIRNAME = "manifests"
LATEST_FILENAME = "MANIFEST_LATEST"
_STATE_SCHEMA_VERSION = 1
_MANIFEST_SCHEMA_VERSION = 1


def file_sha256(path: str) -> str:
    """sha256 of a file's bytes (input files are treated as immutable)."""
    digest = hashlib.sha256()
    with open(path, "rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def compute_manifest_id(record_ids: Iterable[str]) -> str:
    """Content address of a training set: sha256 over its sorted demo ids."""
    joined = "\n".join(sorted(record_ids))
    return hashlib.sha256(joined.encode("utf-8")).hexdigest()


@dataclass
class RunResult:
    """Outcome of one incremental run."""

    manifest: Dict[str, object]
    manifest_path: str
    new_files: List[str]  # basenames processed in *this* run
    noop: bool  # True when nothing changed (idempotent rerun)
    run_counts: Dict[str, int]  # stage counts for this run only

    @property
    def manifest_id(self) -> str:
        return str(self.manifest["manifest_id"])


def _empty_state(config: PipelineConfig) -> Dict[str, object]:
    return {
        "schema_version": _STATE_SCHEMA_VERSION,
        "config": config.to_dict(),
        "processed_files": {},  # basename -> {"sha256":, "lines":}
        "exact_index": {},  # content hash -> kept demo_id
        "bucket_index": {},  # near-dup bucket -> kept demo_id
        "survivors": [],  # post-dedup record dicts (stage 1-2 output)
        "latest_manifest_id": None,
        "cumulative": {
            "input_lines": 0,
            "quarantined": 0,
            "validated": 0,
            "dropped_exact": 0,
            "dropped_near": 0,
        },
    }


def _load_state(workdir: str, config: PipelineConfig) -> Dict[str, object]:
    path = os.path.join(workdir, STATE_FILENAME)
    if not os.path.exists(path):
        return _empty_state(config)
    with open(path, "r", encoding="utf-8") as handle:
        state = json.load(handle)
    if state.get("schema_version") != _STATE_SCHEMA_VERSION:
        raise ValueError("state schema version mismatch in %s" % path)
    if state.get("config") != config.to_dict():
        raise ValueError(
            "pipeline config drift detected in %s; incremental runs require the "
            "original config -- use a fresh workdir to rebuild with new knobs"
            % workdir
        )
    return state


def _atomic_write_json(path: str, obj: object) -> None:
    tmp_path = path + ".tmp"
    with open(tmp_path, "w", encoding="utf-8") as handle:
        json.dump(obj, handle, indent=2, sort_keys=True)
        handle.write("\n")
    os.replace(tmp_path, path)


def run_incremental(
    input_paths: List[str],
    config: PipelineConfig,
    workdir: str,
) -> RunResult:
    """Process any new input files, then rebuild the manifest.

    Files are keyed by basename; re-presenting an already-processed file is
    free (skipped by hash check), and mutating a processed file in place is
    an error, because it would silently invalidate lineage.
    """
    os.makedirs(os.path.join(workdir, MANIFEST_DIRNAME), exist_ok=True)
    state = _load_state(workdir, config)
    processed: Dict[str, Dict[str, object]] = state["processed_files"]

    new_files: List[Tuple[str, str, str]] = []  # (path, basename, sha256)
    for path in sorted(input_paths, key=os.path.basename):
        name = os.path.basename(path)
        digest = file_sha256(path)
        if name in processed:
            if processed[name]["sha256"] != digest:
                raise ValueError(
                    "input file %s changed since it was ingested; inputs are "
                    "immutable -- publish a new batch file instead" % name
                )
            continue
        new_files.append((path, name, digest))

    survivors: List[DemoRecord] = [
        DemoRecord.from_dict(payload, config) for payload in state["survivors"]
    ]
    seen_ids: Set[str] = set(record.demo_id for record in survivors)
    exact_index: Dict[str, str] = state["exact_index"]
    bucket_index: Dict[str, str] = state["bucket_index"]

    run_counts = {
        "input_lines": 0,
        "quarantined": 0,
        "validated": 0,
        "dropped_exact": 0,
        "dropped_near": 0,
        "new_survivors": 0,
    }
    run_quarantined = []
    run_dropped = []

    for path, name, digest in new_files:
        with open(path, "r", encoding="utf-8") as handle:
            lines = handle.read().splitlines()
        records, quarantined = validate_lines(
            lines, config, seen_ids=seen_ids, source=name
        )
        seen_ids.update(record.demo_id for record in records)
        dedup = dedup_records(records, config, exact_index, bucket_index)
        exact_index = dedup.exact_index
        bucket_index = dedup.bucket_index
        survivors.extend(dedup.kept)

        run_quarantined.extend(quarantined)
        run_dropped.extend(dedup.dropped)
        run_counts["input_lines"] += len(lines)
        run_counts["quarantined"] += len(quarantined)
        run_counts["validated"] += len(records)
        run_counts["dropped_exact"] += sum(
            1 for entry in dedup.dropped if entry.reason == "exact_duplicate"
        )
        run_counts["dropped_near"] += sum(
            1 for entry in dedup.dropped if entry.reason == "near_duplicate"
        )
        run_counts["new_survivors"] += len(dedup.kept)
        processed[name] = {"sha256": digest, "lines": len(lines)}

    # Stages 3-4 are global recomputations over the survivor pool: cheap,
    # deterministic, and independent of arrival order.
    kept_quality, rejected = filter_by_quality(survivors, config)
    strat = stratify(kept_quality, config)
    record_ids = sorted(record.demo_id for record in strat.selected)
    manifest_id = compute_manifest_id(record_ids)

    manifest_path = os.path.join(
        workdir, MANIFEST_DIRNAME, manifest_id + ".json"
    )
    if not new_files and state["latest_manifest_id"] == manifest_id:
        with open(manifest_path, "r", encoding="utf-8") as handle:
            manifest = json.load(handle)
        return RunResult(
            manifest=manifest,
            manifest_path=manifest_path,
            new_files=[],
            noop=True,
            run_counts=run_counts,
        )

    for key in ("input_lines", "quarantined", "validated", "dropped_exact", "dropped_near"):
        state["cumulative"][key] += run_counts[key]

    manifest = {
        "schema_version": _MANIFEST_SCHEMA_VERSION,
        "manifest_id": manifest_id,
        "num_records": len(record_ids),
        "record_ids": record_ids,
        "per_task_selected": strat.per_task_selected,
        "target_counts": strat.target_counts,
        "collection_requests": [request.to_dict() for request in strat.requests],
        "stage_counts": {
            "cumulative": dict(state["cumulative"]),
            "survivors_after_dedup": len(survivors),
            "rejected_quality": len(rejected),
            "after_quality": len(kept_quality),
            "selected": len(strat.selected),
        },
        "lineage": {
            "parent_manifest_id": state["latest_manifest_id"],
            "pipeline_config": config.to_dict(),
            "inputs": [
                {
                    "name": name,
                    "sha256": processed[name]["sha256"],
                    "lines": processed[name]["lines"],
                }
                for name in sorted(processed)
            ],
        },
        "created_utc": datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ"),
    }

    # Per-run reports + current training set (reports describe the last
    # mutating run; quarantine.jsonl is append-only across runs).
    _atomic_write_json(manifest_path, manifest)
    with open(os.path.join(workdir, LATEST_FILENAME), "w", encoding="utf-8") as handle:
        handle.write(manifest_id + "\n")
    with open(os.path.join(workdir, "quarantine.jsonl"), "a", encoding="utf-8") as handle:
        for entry in run_quarantined:
            handle.write(json.dumps(entry.to_dict(), sort_keys=True) + "\n")
    _atomic_write_json(
        os.path.join(workdir, "dedup_report.json"),
        [entry.to_dict() for entry in run_dropped],
    )
    _atomic_write_json(
        os.path.join(workdir, "quality_report.json"),
        [entry.to_dict() for entry in rejected],
    )
    _atomic_write_json(
        os.path.join(workdir, "collection_requests.json"),
        [request.to_dict() for request in strat.requests],
    )
    with open(os.path.join(workdir, "train_set.jsonl"), "w", encoding="utf-8") as handle:
        for record in sorted(strat.selected, key=lambda r: r.demo_id):
            handle.write(json.dumps(record.to_dict(), sort_keys=True) + "\n")

    state["exact_index"] = exact_index
    state["bucket_index"] = bucket_index
    state["survivors"] = [record.to_dict() for record in survivors]
    state["latest_manifest_id"] = manifest_id
    _atomic_write_json(os.path.join(workdir, STATE_FILENAME), state)

    return RunResult(
        manifest=manifest,
        manifest_path=manifest_path,
        new_files=[name for _, name, _ in new_files],
        noop=False,
        run_counts=run_counts,
    )


def main() -> None:
    lab_dir = os.path.dirname(os.path.abspath(__file__))
    parser = argparse.ArgumentParser(
        description="Incremental manifest build over a directory of demo batches."
    )
    parser.add_argument("--data-dir", default=os.path.join(lab_dir, "data"))
    parser.add_argument("--workdir", default=os.path.join(lab_dir, "out"))
    parser.add_argument("--budget", type=int, default=420)
    parser.add_argument("--quality-threshold", type=float, default=0.75)
    args = parser.parse_args()

    config = PipelineConfig(
        train_budget=args.budget, quality_threshold=args.quality_threshold
    )
    paths = sorted(glob.glob(os.path.join(args.data_dir, "*.jsonl")))
    if not paths:
        raise SystemExit(
            "no .jsonl files under %s (run generate_demos.py first)" % args.data_dir
        )

    result = run_incremental(paths, config, args.workdir)

    if result.noop:
        print("no new inputs; manifest unchanged (idempotent rerun)")
    else:
        print("processed new files: %s" % (result.new_files or "(none)"))
        print("this run: %s" % json.dumps(result.run_counts, sort_keys=True))
    print("manifest_id: %s" % result.manifest_id)
    print("parent:      %s" % result.manifest["lineage"]["parent_manifest_id"])
    print("num_records: %s" % result.manifest["num_records"])
    print("per-task selected:")
    for task, count in sorted(result.manifest["per_task_selected"].items()):
        target = result.manifest["target_counts"][task]
        print("  %-16s %4d / %d" % (task, count, target))
    requests = result.manifest["collection_requests"]
    print("collection requests (%d):" % len(requests))
    for request in requests:
        print(
            "  %-16s have=%-4d target=%-4d gap=%-4d %s"
            % (
                request["task"],
                request["have"],
                request["target"],
                request["gap"],
                request["note"],
            )
        )
    print("manifest file: %s" % result.manifest_path)


if __name__ == "__main__":
    main()
