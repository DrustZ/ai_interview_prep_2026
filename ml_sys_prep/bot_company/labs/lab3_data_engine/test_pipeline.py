#!/usr/bin/env python3
"""Tests for lab3_data_engine (plain assert, no pytest).

Run:  /usr/bin/python3 test_pipeline.py

Covers: generator determinism, per-stage counts, dedup correctness,
quality filtering, stratification + collection requests, manifest
reproducibility, incremental idempotency, and lineage.
"""

import json
import os
import shutil
import tempfile
from typing import Dict, List, Set, Tuple

import generate_demos as gen
import manifest as mf
import pipeline as pl

CONFIG = pl.PipelineConfig()


# --------------------------------------------------------------------------
# Fixtures (generated once, deterministic)
# --------------------------------------------------------------------------


def build_fixtures() -> Tuple[
    List[str], gen.GenerationSummary, List[str], gen.GenerationSummary
]:
    lines1, summary1 = gen.generate_batch(gen.BATCH1, config=CONFIG)
    cross_sources = gen.eligible_cross_sources(lines1, summary1, CONFIG)
    lines2, summary2 = gen.generate_batch(
        gen.BATCH2, cross_sources=cross_sources, config=CONFIG
    )
    return lines1, summary1, lines2, summary2


LINES1, SUMMARY1, LINES2, SUMMARY2 = build_fixtures()


def write_data_dir(base: str, batches: List[Tuple[List[str], gen.GenerationSummary]]) -> str:
    data_dir = os.path.join(base, "data")
    os.makedirs(data_dir, exist_ok=True)
    for lines, summary in batches:
        path = os.path.join(data_dir, "demos_batch%d.jsonl" % summary.batch)
        gen.write_batch(lines, summary, path)
    return data_dir


# --------------------------------------------------------------------------
# Generator
# --------------------------------------------------------------------------


def test_generator_deterministic() -> None:
    lines_a, summary_a = gen.generate_batch(gen.BATCH1, config=CONFIG)
    lines_b, summary_b = gen.generate_batch(gen.BATCH1, config=CONFIG)
    assert lines_a == lines_b, "same spec+seed must produce identical bytes"
    assert summary_a.to_dict() == summary_b.to_dict()
    assert summary_a.total_lines == 807, summary_a.total_lines  # ~800 by design
    assert len(summary_a.schema_bad_lines) == gen.BATCH1.n_schema_bad
    assert len(summary_a.exact_dup_ids) == gen.BATCH1.n_exact_dups
    assert len(summary_a.near_dup_ids) == gen.BATCH1.n_near_dups
    assert len(summary_a.bad_quality_ids) == gen.BATCH1.n_bad_quality


# --------------------------------------------------------------------------
# Stage 1: schema validation
# --------------------------------------------------------------------------


def test_stage1_schema_validation() -> None:
    records, quarantined = pl.validate_lines(LINES1, CONFIG, source="b1")
    assert len(quarantined) == gen.BATCH1.n_schema_bad, len(quarantined)
    assert len(records) == SUMMARY1.n_schema_valid, len(records)
    assert len(records) + len(quarantined) == SUMMARY1.total_lines

    # Quarantine points at exactly the injected bad line numbers, with reasons.
    assert sorted(entry.line_no for entry in quarantined) == SUMMARY1.schema_bad_lines
    reasons = {entry.reason for entry in quarantined}
    assert "malformed_json" in reasons, reasons
    assert "missing_field:task" in reasons, reasons
    assert "bad_type:duration_s" in reasons, reasons
    assert "out_of_range:duration_s" in reasons, reasons
    assert "unknown_task:juggle_chainsaws" in reasons, reasons
    assert "missing_field:operator_id" in reasons, reasons  # null operator
    for entry in quarantined:
        assert entry.reason and entry.raw_prefix and entry.source == "b1"

    # demo_id collision with an already-seen batch is quarantined, not merged.
    dup_line = json.dumps(records[0].to_dict(), sort_keys=True)
    more, quar = pl.validate_lines(
        [dup_line], CONFIG, seen_ids={records[0].demo_id}, source="b1_again"
    )
    assert not more and len(quar) == 1
    assert quar[0].reason.startswith("duplicate_demo_id:")


# --------------------------------------------------------------------------
# Stage 2: dedup
# --------------------------------------------------------------------------


def _validated_batch1() -> List[pl.DemoRecord]:
    records, _ = pl.validate_lines(LINES1, CONFIG)
    return records


def test_stage2_dedup() -> None:
    records = _validated_batch1()
    result = pl.dedup_records(records, CONFIG)

    assert len(result.kept) + len(result.dropped) == len(records)

    dropped_by_reason: Dict[str, Set[str]] = {"exact_duplicate": set(), "near_duplicate": set()}
    for entry in result.dropped:
        dropped_by_reason[entry.reason].add(entry.demo_id)
        assert entry.duplicate_of, "every drop must name its kept twin"
        assert entry.duplicate_of != entry.demo_id

    # Every injected duplicate is caught, with the right reason.
    assert set(SUMMARY1.exact_dup_ids) <= dropped_by_reason["exact_duplicate"]
    assert set(SUMMARY1.near_dup_ids) <= dropped_by_reason["near_duplicate"]

    # Survivors are unique under both identity definitions.
    hashes = [pl.content_hash(r.to_dict()) for r in result.kept]
    buckets = [pl.near_dup_key(r.to_dict(), CONFIG) for r in result.kept]
    assert len(set(hashes)) == len(hashes), "exact dup survived"
    assert len(set(buckets)) == len(buckets), "near dup survived"

    # duplicate_of must reference a surviving record.
    kept_ids = {record.demo_id for record in result.kept}
    for entry in result.dropped:
        assert entry.duplicate_of in kept_ids, entry

    # Incremental form: feeding the same records against the returned indices
    # drops everything as exact duplicates.
    again = pl.dedup_records(result.kept, CONFIG, result.exact_index, result.bucket_index)
    assert not again.kept
    assert all(entry.reason == "exact_duplicate" for entry in again.dropped)


# --------------------------------------------------------------------------
# Stage 3: quality
# --------------------------------------------------------------------------


def test_stage3_quality_filter() -> None:
    records = _validated_batch1()
    dedup = pl.dedup_records(records, CONFIG)
    kept, rejected = pl.filter_by_quality(dedup.kept, CONFIG)

    assert len(kept) + len(rejected) == len(dedup.kept)
    rejected_ids = {assessment.demo_id for assessment in rejected}
    survivor_ids = {record.demo_id for record in dedup.kept}

    # Exactly the injected bad-quality demos (that survived dedup) fail.
    assert rejected_ids == set(SUMMARY1.bad_quality_ids) & survivor_ids

    for assessment in rejected:
        assert assessment.penalties, "rejections must be explainable"
        assert assessment.score < CONFIG.quality_threshold
    for record in kept:
        assert pl.assess_quality(record, CONFIG).score >= CONFIG.quality_threshold

    # Each defect mode produces its named penalty.
    all_penalties = ";".join(";".join(a.penalties) for a in rejected)
    assert "incomplete" in all_penalties
    assert "longest_pause_s=" in all_penalties
    assert "mean_jerk=" in all_penalties

    # Threshold is a config knob: raising it to 1.0 must not reject clean demos
    # (clean generator output scores exactly 1.0).
    strict = pl.PipelineConfig(quality_threshold=1.0)
    strict_kept, strict_rejected = pl.filter_by_quality(dedup.kept, strict)
    assert {a.demo_id for a in strict_rejected} == rejected_ids
    assert len(strict_kept) == len(kept)


# --------------------------------------------------------------------------
# Stage 4: stratification + collection requests
# --------------------------------------------------------------------------


def test_stage4_stratify_and_requests() -> None:
    records = _validated_batch1()
    dedup = pl.dedup_records(records, CONFIG)
    kept, _ = pl.filter_by_quality(dedup.kept, CONFIG)
    result = pl.stratify(kept, CONFIG)

    targets = pl.compute_target_counts(CONFIG)
    assert sum(targets.values()) == CONFIG.train_budget

    have: Dict[str, int] = {task: 0 for task in CONFIG.known_tasks}
    for record in kept:
        have[record.task] += 1

    selected_by_task: Dict[str, int] = {task: 0 for task in CONFIG.known_tasks}
    for record in result.selected:
        selected_by_task[record.task] += 1

    requested_tasks = {request.task for request in result.requests}
    for task in CONFIG.known_tasks:
        expected = min(have[task], targets[task])
        assert selected_by_task[task] == expected, (task, selected_by_task[task], expected)
        if have[task] < targets[task]:
            assert task in requested_tasks, "deficit task %s missing a request" % task
        else:
            assert task not in requested_tasks, "surplus task %s got a request" % task

    # The imbalanced generator guarantees both surpluses and deficits.
    assert result.requests, "expected at least one collection request"
    assert any(have[task] > targets[task] for task in CONFIG.known_tasks)

    # Requests quantify the correct gap and point at the scarcest cohort.
    for request in result.requests:
        assert request.gap == targets[request.task] - have[request.task]
        assert request.gap > 0
        cohort = [r for r in kept if r.task == request.task]
        lighting_counts = {level: 0 for level in pl.LIGHTING_LEVELS}
        for record in cohort:
            lighting_counts[record.scene.lighting] += 1
        assert lighting_counts[request.scarcest_lighting] == min(lighting_counts.values())
        assert request.task in request.note

    # Requests are sorted most-urgent first.
    gaps = [request.gap for request in result.requests]
    assert gaps == sorted(gaps, reverse=True)

    # Surplus tasks keep their highest-quality demos (all clean here => 1.0),
    # and no selected demo is below threshold.
    for record in result.selected:
        assert pl.assess_quality(record, CONFIG).score >= CONFIG.quality_threshold


# --------------------------------------------------------------------------
# Manifest: reproducibility, incremental runs, lineage
# --------------------------------------------------------------------------


def test_manifest_reproducible_across_workdirs() -> None:
    base = tempfile.mkdtemp(prefix="lab3_repro_")
    try:
        data_dir = write_data_dir(base, [(LINES1, SUMMARY1)])
        paths = [os.path.join(data_dir, "demos_batch1.jsonl")]
        result_a = mf.run_incremental(paths, CONFIG, os.path.join(base, "wd_a"))
        result_b = mf.run_incremental(paths, CONFIG, os.path.join(base, "wd_b"))
        assert result_a.manifest_id == result_b.manifest_id
        assert result_a.manifest["record_ids"] == result_b.manifest["record_ids"]
        # The id really is the content address of the sorted ids.
        recomputed = mf.compute_manifest_id(result_a.manifest["record_ids"])
        assert recomputed == result_a.manifest_id
        assert os.path.exists(result_a.manifest_path)
    finally:
        shutil.rmtree(base, ignore_errors=True)


def test_incremental_runs_and_lineage() -> None:
    base = tempfile.mkdtemp(prefix="lab3_incr_")
    try:
        data_dir = write_data_dir(base, [(LINES1, SUMMARY1), (LINES2, SUMMARY2)])
        path1 = os.path.join(data_dir, "demos_batch1.jsonl")
        path2 = os.path.join(data_dir, "demos_batch2.jsonl")
        workdir = os.path.join(base, "wd")

        # Run 1: batch 1 only.
        run1 = mf.run_incremental([path1], CONFIG, workdir)
        assert run1.new_files == ["demos_batch1.jsonl"]
        assert run1.manifest["lineage"]["parent_manifest_id"] is None
        assert run1.run_counts["input_lines"] == SUMMARY1.total_lines

        # Run 2: both batches -> only batch 2 is processed.
        run2 = mf.run_incremental([path1, path2], CONFIG, workdir)
        assert run2.new_files == ["demos_batch2.jsonl"], run2.new_files
        assert run2.run_counts["input_lines"] == SUMMARY2.total_lines
        assert run2.run_counts["quarantined"] == gen.BATCH2.n_schema_bad
        assert not run2.noop
        assert run2.manifest["lineage"]["parent_manifest_id"] == run1.manifest_id
        assert run2.manifest_id != run1.manifest_id

        # Cross-batch exact dups were caught against run-1 state.
        with open(os.path.join(workdir, "dedup_report.json"), "r") as handle:
            drops2 = json.load(handle)
        drops2_by_id = {entry["demo_id"]: entry for entry in drops2}
        for cross_id in SUMMARY2.cross_dup_ids:
            entry = drops2_by_id[cross_id]
            assert entry["reason"] == "exact_duplicate", entry
            assert entry["duplicate_of"].startswith("d1_"), entry

        # Run 3: same inputs again -> idempotent no-op.
        run3 = mf.run_incremental([path1, path2], CONFIG, workdir)
        assert run3.noop
        assert run3.new_files == []
        assert run3.manifest_id == run2.manifest_id
        assert run3.run_counts["input_lines"] == 0

        # Full rebuild in a fresh workdir reproduces the incremental manifest.
        rebuild = mf.run_incremental([path1, path2], CONFIG, os.path.join(base, "wd_full"))
        assert rebuild.manifest_id == run2.manifest_id
        assert rebuild.manifest["record_ids"] == run2.manifest["record_ids"]

        # Lineage carries the config snapshot and hashed inputs.
        lineage = run2.manifest["lineage"]
        assert lineage["pipeline_config"] == CONFIG.to_dict()
        assert [entry["name"] for entry in lineage["inputs"]] == [
            "demos_batch1.jsonl",
            "demos_batch2.jsonl",
        ]
        for entry in lineage["inputs"]:
            assert len(entry["sha256"]) == 64

        # Guardrails: mutated input and config drift are hard errors.
        with open(path2, "a", encoding="utf-8") as handle:
            handle.write("\n")
        try:
            mf.run_incremental([path1, path2], CONFIG, workdir)
            raise AssertionError("mutated input file must be rejected")
        except ValueError as exc:
            assert "immutable" in str(exc)
        try:
            mf.run_incremental([path1], pl.PipelineConfig(train_budget=999), workdir)
            raise AssertionError("config drift must be rejected")
        except ValueError as exc:
            assert "config drift" in str(exc)

        # Train set on disk matches the manifest exactly.
        with open(os.path.join(workdir, "train_set.jsonl"), "r") as handle:
            train_ids = [json.loads(line)["demo_id"] for line in handle if line.strip()]
        assert train_ids == run2.manifest["record_ids"]
    finally:
        shutil.rmtree(base, ignore_errors=True)


def test_collection_requests_in_manifest() -> None:
    base = tempfile.mkdtemp(prefix="lab3_req_")
    try:
        data_dir = write_data_dir(base, [(LINES1, SUMMARY1)])
        paths = [os.path.join(data_dir, "demos_batch1.jsonl")]
        result = mf.run_incremental(paths, CONFIG, os.path.join(base, "wd"))
        requests = result.manifest["collection_requests"]
        assert requests, "imbalanced batch 1 must yield collection requests"
        per_task = result.manifest["per_task_selected"]
        targets = result.manifest["target_counts"]
        for request in requests:
            # The request points at a genuinely under-filled cohort.
            assert per_task[request["task"]] < targets[request["task"]]
            assert request["have"] + request["gap"] == request["target"]
        # And no non-requested task is under target.
        requested = {request["task"] for request in requests}
        for task, count in per_task.items():
            if task not in requested:
                assert count == targets[task], (task, count)
    finally:
        shutil.rmtree(base, ignore_errors=True)


# --------------------------------------------------------------------------
# Runner
# --------------------------------------------------------------------------


def run_all() -> None:
    tests = [
        test_generator_deterministic,
        test_stage1_schema_validation,
        test_stage2_dedup,
        test_stage3_quality_filter,
        test_stage4_stratify_and_requests,
        test_manifest_reproducible_across_workdirs,
        test_incremental_runs_and_lineage,
        test_collection_requests_in_manifest,
    ]
    for test in tests:
        test()
        print("PASS %s" % test.__name__)
    print("all %d tests passed" % len(tests))


if __name__ == "__main__":
    run_all()
