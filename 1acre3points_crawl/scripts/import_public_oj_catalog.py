#!/usr/bin/env python3
"""Merge the saved complete public OJ catalog into questions.json."""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable, Mapping, Sequence


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_INPUT = PROJECT_ROOT / "data" / "public_oj_catalog.json"
DEFAULT_OUTPUT = PROJECT_ROOT / "data" / "questions.json"
DEFAULT_COVERAGE = PROJECT_ROOT / "data" / "catalog_coverage.json"
EXPECTED_QBANK = {"openai": 45, "anthropic": 35}
EXPECTED_OJ = {"openai": 139, "anthropic": 64}
OFFICIAL_TARGET = {company: EXPECTED_QBANK[company] + EXPECTED_OJ[company] for company in EXPECTED_QBANK}


TAG_PATTERNS: tuple[tuple[str, str], ...] = (
    ("pytorch", r"\bpytorch\b|\btorch\b"),
    ("transformer", r"transformer|attention|\bgpt\b|\bllm\b|tokeni[sz]"),
    ("machine-learning", r"machine learning|classifier|regression|training|model|gradient|neural|extratrees"),
    ("debugging", r"\bdebug|buggy|fix (?:a|an|the)"),
    ("distributed-systems", r"distributed|cluster|shard|multi-node|topology|consensus"),
    ("concurrency", r"concurren|thread|async|parallel|deadlock|race condition"),
    ("caching", r"\bcach(?:e|ing)\b|\blru\b|memoization"),
    ("database", r"database|\bsql\b|key-value|\bkv\b|storage system"),
    ("graph", r"\bgraph\b|network|topolog|\bbfs\b|\bdfs\b|path"),
    ("dynamic-programming", r"dynamic programming|falling path|\bdp\b"),
    ("simulation", r"simulation|simulate|game of life|infection|battle|game"),
    ("data-structures", r"linked list|hash ?map|heap|queue|stack|tree|trie|iterator"),
    ("string-processing", r"string|parser|parsing|tokeni[sz]|regex|template"),
    ("file-systems", r"file|filesystem|directory|dedup"),
    ("networking", r"\bdns\b|\bip(?:v4)?\b|cidr|crawler|http|rate limit"),
    ("frontend", r"react|typescript|frontend|user interface|\bui\b|figma|ios"),
    ("image-processing", r"image|pixel|grayscale|resize|stroke"),
    ("statistics", r"entropy|statistic|a/b test|median|probability"),
    ("system-design", r"\bdesign\b|scheduler|message bus|rate limiter"),
)


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, default=DEFAULT_INPUT)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--coverage", type=Path, default=DEFAULT_COVERAGE)
    return parser.parse_args(argv)


def clean(value: Any) -> str:
    return value.strip() if isinstance(value, str) else ""


def count_by(records: Iterable[Mapping[str, Any]], key: str) -> dict[str, int]:
    return dict(sorted(Counter(clean(row.get(key)) or "unknown" for row in records).items()))


def inferred_tags(title: str) -> list[str]:
    lowered = title.casefold()
    return [tag for tag, pattern in TAG_PATTERNS if re.search(pattern, lowered, re.I)][:8]


def snapshot_items(snapshot: Mapping[str, Any]) -> list[dict[str, Any]]:
    companies = snapshot.get("companies")
    if not isinstance(companies, list):
        raise ValueError("public OJ catalog has no companies array")
    result: list[dict[str, Any]] = []
    for company_payload in companies:
        if not isinstance(company_payload, Mapping):
            raise ValueError("public OJ catalog contains a non-object company")
        company = clean(company_payload.get("company")).lower()
        if company not in EXPECTED_OJ:
            raise ValueError(f"unexpected company in public OJ catalog: {company!r}")
        pages = company_payload.get("pages")
        if not isinstance(pages, list):
            raise ValueError(f"{company} public OJ catalog has no pages array")
        company_rows: list[dict[str, Any]] = []
        for page in pages:
            rows = page.get("items") if isinstance(page, Mapping) else None
            if not isinstance(rows, list):
                raise ValueError(f"{company} public OJ catalog page has no items")
            normalized_rows = [dict(row) for row in rows if isinstance(row, Mapping)]
            if len(normalized_rows) != len(rows):
                raise ValueError(f"{company} public OJ catalog contains a non-object row")
            company_rows.extend(normalized_rows)
        if len(company_rows) != EXPECTED_OJ[company]:
            raise ValueError(
                f"expected {EXPECTED_OJ[company]} {company} OJ rows, found {len(company_rows)}"
            )
        result.extend(company_rows)
    if len({(clean(row.get("company")).lower(), clean(row.get("id"))) for row in result}) != len(result):
        raise ValueError("public OJ catalog has duplicate company/id rows")
    return result


def normalize_oj(raw: Mapping[str, Any], existing: Mapping[str, Any] | None) -> dict[str, Any]:
    company = clean(raw.get("company")).lower()
    question_id = clean(raw.get("id"))
    title = clean(raw.get("title"))
    slug = clean(raw.get("slug"))
    if not company or not question_id or not title:
        raise ValueError("public OJ catalog row is missing company/id/title")
    row = dict(existing or {})
    previous_tags = row.get("tags") if isinstance(row.get("tags"), list) else []
    tags = [clean(tag) for tag in previous_tags if clean(tag)] or inferred_tags(title)
    row.update(
        {
            "id": question_id,
            "company": company,
            "sourceKind": "oj-public-catalog",
            "slug": slug,
            "title": title,
            "category": "oj",
            "tags": tags,
            "roles": row.get("roles") if isinstance(row.get("roles"), list) else [],
            "stages": row.get("stages") if isinstance(row.get("stages"), list) else [],
            "access": "public-problem-link",
            "frequency": clean(row.get("frequency")) or "unknown",
            "date": clean(row.get("date")),
            "duration": row.get("duration"),
            "source_count": row.get("source_count"),
            "difficulty": raw.get("difficulty"),
            "employment_type": raw.get("employment_type"),
            "isExternalThread": bool(raw.get("isExternalThread")),
            "catalogPage": raw.get("catalogPage"),
            "catalogPosition": raw.get("catalogPosition"),
            "summary": clean(row.get("summary")),
            "content": clean(row.get("content")),
            "sourceUrl": clean(raw.get("sourceUrl")),
            "sourceType": "public-official-catalog-api",
            "officialSnapshot": True,
            "catalogMetadataPublic": True,
            "tagsSource": "existing-snapshot" if previous_tags else "title-inference",
        }
    )
    return row


def build_payload(
    existing_payload: Mapping[str, Any],
    snapshot: Mapping[str, Any],
    snapshot_path: Path,
) -> tuple[dict[str, Any], dict[str, Any]]:
    existing_questions = existing_payload.get("questions")
    if not isinstance(existing_questions, list):
        raise ValueError("questions payload has no questions array")
    public_rows = snapshot_items(snapshot)
    public_keys = {
        (clean(row.get("company")).lower(), clean(row.get("id"))) for row in public_rows
    }
    existing_by_key = {
        (clean(row.get("company")).lower(), clean(row.get("id"))): row
        for row in existing_questions
        if isinstance(row, Mapping)
    }

    retained = [
        dict(row)
        for row in existing_questions
        if isinstance(row, Mapping)
        and not (
            clean(row.get("company")).lower() in EXPECTED_OJ
            and clean(row.get("sourceKind")).startswith("oj")
        )
    ]
    merged_oj = [
        normalize_oj(raw, existing_by_key.get((clean(raw.get("company")).lower(), clean(raw.get("id")))))
        for raw in public_rows
    ]
    questions = [*retained, *merged_oj]
    keys = [(clean(row.get("company")).lower(), clean(row.get("id"))) for row in questions]
    if len(set(keys)) != len(keys):
        raise ValueError("company/id collision after public OJ merge")

    qbank_counts = Counter(
        clean(row.get("company")).lower()
        for row in questions
        if clean(row.get("sourceKind")) == "qbank"
    )
    for company, expected in EXPECTED_QBANK.items():
        if qbank_counts[company] != expected:
            raise ValueError(f"expected {expected} {company} qbank rows, found {qbank_counts[company]}")
    canonical_total = len(questions)
    official_total = sum(OFFICIAL_TARGET.values())
    if canonical_total != official_total:
        raise ValueError(f"expected {official_total} canonical rows, found {canonical_total}")

    result = dict(existing_payload)
    result["generatedAt"] = datetime.now(timezone.utc).isoformat(timespec="seconds")
    result["questions"] = questions
    meta = dict(result.get("meta") or {})
    meta.update(
        {
            "companies": ["openai", "anthropic"],
            "description": "Complete public catalog index; content provenance is tracked separately.",
            "officialSnapshot": False,
            "completeOfficialCatalogIndex": True,
            "completeOfficialMirror": False,
            "canonicalCatalogRecords": canonical_total,
            "officialReportedRecords": official_total,
        }
    )
    result["meta"] = meta
    provenance = dict(result.get("provenance") or {})
    provenance["publicOjCatalog"] = {
        "networkAccessedByFetchStep": True,
        "sourceType": "anonymous official public catalog endpoint",
        "endpoint": clean((snapshot.get("source") or {}).get("endpoint")) if isinstance(snapshot.get("source"), Mapping) else "",
        "snapshotPath": str(snapshot_path.resolve()),
        "snapshotGeneratedAt": clean(snapshot.get("generatedAt")),
        "ojByCompany": EXPECTED_OJ,
        "completePublicOjIndex": True,
        "memberContentRetrieved": False,
        "thirdPartyUnlockerUsed": False,
    }
    provenance["completeOfficialMirror"] = False
    provenance["catalogCoverage"] = {
        "reportedTarget": OFFICIAL_TARGET,
        "savedByCompany": OFFICIAL_TARGET,
        "savedTotal": canonical_total,
        "reportedTargetTotal": official_total,
        "missingUnsavedOjRows": 0,
    }
    result["provenance"] = provenance
    counts = dict(result.get("counts") or {})
    counts.update(
        {
            "qbankRecords": sum(clean(row.get("sourceKind")) == "qbank" for row in questions),
            "ojSavedRecords": sum(clean(row.get("sourceKind")).startswith("oj") for row in questions),
            "outputRecords": canonical_total,
            "byCompany": count_by(questions, "company"),
            "bySourceKind": count_by(questions, "sourceKind"),
            "byCategory": count_by(questions, "category"),
            "byAccess": count_by(questions, "access"),
            "officialReportedRecords": official_total,
            "missingUnsavedOjRows": 0,
        }
    )
    result["counts"] = counts

    coverage = {
        "checkedAt": result["generatedAt"],
        "reportedOfficialCatalog": {**OFFICIAL_TARGET, "total": official_total},
        "individuallyIdentifiedFromPublicCatalog": {
            "openai": {"qbank": 45, "oj": 139, "total": 184},
            "anthropic": {"qbank": 35, "oj": 64, "total": 99},
            "total": canonical_total,
        },
        "unidentifiedCatalogRecords": 0,
        "publicOjMetadataSnapshot": {
            "path": str(snapshot_path.resolve()),
            "endpoint": provenance["publicOjCatalog"]["endpoint"],
            "records": len(public_keys),
            "tagsNote": "OJ endpoint has no official tags; any non-empty OJ tags are title-derived and labelled tagsSource=title-inference.",
        },
        "notes": [
            "All 283 primary company-page catalog rows have real official IDs/slugs, titles, and detail URLs.",
            "The 207 supplemental research cards are not counted as official catalog rows.",
            "A complete catalog index is not a complete member-content mirror.",
            "No member test cases or paywalled bodies were retrieved by this import.",
        ],
    }
    return result, coverage


def write_json_atomic(path: Path, payload: Mapping[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(f".{path.name}.{os.getpid()}.tmp")
    try:
        with temporary.open("w", encoding="utf-8") as handle:
            json.dump(payload, handle, ensure_ascii=False, indent=2)
            handle.write("\n")
        temporary.replace(path)
    finally:
        if temporary.exists():
            temporary.unlink()


def main(argv: Sequence[str] | None = None) -> int:
    args = parse_args(argv)
    try:
        existing = json.loads(args.output.read_text(encoding="utf-8"))
        snapshot = json.loads(args.input.read_text(encoding="utf-8"))
        payload, coverage = build_payload(existing, snapshot, args.input)
        write_json_atomic(args.output, payload)
        write_json_atomic(args.coverage, coverage)
    except (OSError, json.JSONDecodeError, ValueError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    print(
        f"wrote {args.output}: {payload['counts']['outputRecords']}/"
        f"{payload['counts']['officialReportedRecords']} canonical catalog rows"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
