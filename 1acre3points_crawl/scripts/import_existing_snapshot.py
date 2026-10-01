#!/usr/bin/env python3
"""Import the user's pre-existing OpenAI question snapshots.

This importer is deliberately offline. It reads only the two local JSON files
named below, retains catalog metadata, and never attempts to retrieve question
bodies or any other remote resource.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable, Mapping, Sequence
from urllib.parse import quote


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_QBANK_INPUT = Path("/tmp/oai_questions.json")
DEFAULT_NEXT_INPUT = Path("/tmp/oai_problems.json")
DEFAULT_OUTPUT = PROJECT_ROOT / "data" / "questions.json"

COMPANY = "openai"
SOURCE_TYPE = "preexisting-user-snapshot"
OFFICIAL_BASE_URL = "https://www.1point3acres.com/interview/problems"
EXPECTED_QBANK_COUNT = 45


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--qbank-input",
        type=Path,
        default=DEFAULT_QBANK_INPUT,
        help=f"pre-existing qbank metadata JSON (default: {DEFAULT_QBANK_INPUT})",
    )
    parser.add_argument(
        "--next-input",
        type=Path,
        default=DEFAULT_NEXT_INPUT,
        help=f"pre-existing company-page Next data (default: {DEFAULT_NEXT_INPUT})",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=DEFAULT_OUTPUT,
        help=f"normalized output JSON (default: {DEFAULT_OUTPUT})",
    )
    return parser.parse_args(argv)


def load_json(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as source:
        return json.load(source)


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for chunk in iter(lambda: source.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def file_timestamp(path: Path) -> str:
    return datetime.fromtimestamp(path.stat().st_mtime, timezone.utc).isoformat(
        timespec="seconds"
    )


def clean_scalar(value: Any) -> Any:
    if isinstance(value, str):
        return value.strip()
    return value


def clean_string(value: Any) -> str:
    value = clean_scalar(value)
    return value if isinstance(value, str) else ""


def clean_string_list(value: Any) -> list[str]:
    if not isinstance(value, list):
        return []
    seen: set[str] = set()
    result: list[str] = []
    for item in value:
        text = clean_string(item)
        if text and text not in seen:
            seen.add(text)
            result.append(text)
    return result


def qbank_detail_url(slug: str) -> str:
    return f"{OFFICIAL_BASE_URL}/company/{COMPANY}/{quote(slug, safe='-._~')}"


def oj_detail_url(question_id: str) -> str:
    return f"{OFFICIAL_BASE_URL}/{quote(question_id, safe='-._~')}"


def normalize_qbank(raw_questions: Any) -> list[dict[str, Any]]:
    if not isinstance(raw_questions, list):
        raise ValueError("qbank input must be a JSON array")
    if len(raw_questions) != EXPECTED_QBANK_COUNT:
        raise ValueError(
            f"expected {EXPECTED_QBANK_COUNT} qbank records, found {len(raw_questions)}"
        )

    normalized: list[dict[str, Any]] = []
    seen_ids: set[str] = set()
    seen_slugs: set[str] = set()
    for index, raw in enumerate(raw_questions):
        if not isinstance(raw, Mapping):
            raise ValueError(f"qbank record {index} is not an object")

        question_id = clean_string(raw.get("id"))
        slug = clean_string(raw.get("slug"))
        if not question_id or not slug:
            raise ValueError(f"qbank record {index} is missing id or slug")
        if question_id in seen_ids:
            raise ValueError(f"duplicate qbank id: {question_id}")
        if slug in seen_slugs:
            raise ValueError(f"duplicate qbank slug: {slug}")
        seen_ids.add(question_id)
        seen_slugs.add(slug)

        is_locked = bool(raw.get("is_locked"))
        is_public = bool(raw.get("is_public"))
        access = "members-only" if is_locked and not is_public else "free-preview"
        source_title = clean_string(raw.get("title"))
        title = source_title or f"会员专享题目 · {slug}"

        # The only available overview belongs to the public preview. Locked
        # entries intentionally retain no body or summary text.
        overview = "" if is_locked else clean_string(raw.get("overview"))
        reported_from = clean_string(raw.get("reported_from"))
        reported_to = clean_string(raw.get("reported_to"))
        last_asked = clean_string(raw.get("last_asked"))
        duration_minutes = raw.get("duration_minutes")
        if duration_minutes is not None and not isinstance(duration_minutes, int):
            raise ValueError(
                f"qbank record {index} has non-integer duration_minutes"
            )
        source_count = raw.get("source_count")
        if source_count is not None and not isinstance(source_count, int):
            raise ValueError(f"qbank record {index} has non-integer source_count")

        normalized.append(
            {
                "id": question_id,
                "company": COMPANY,
                "sourceKind": "qbank",
                "slug": slug,
                "title": title,
                "category": clean_string(raw.get("category")) or "uncategorized",
                "tags": clean_string_list(raw.get("tags")),
                "roles": clean_string_list(raw.get("roles")),
                "stages": clean_string_list(raw.get("stages")),
                "access": access,
                "frequency": clean_string(raw.get("frequency")) or "unknown",
                "date": last_asked,
                "duration": duration_minutes,
                "source_count": source_count,
                "reported_from": reported_from,
                "reported_to": reported_to,
                "last_asked": last_asked,
                "duration_minutes": duration_minutes,
                "is_new": bool(raw.get("is_new")),
                "is_public": is_public,
                "is_locked": is_locked,
                "status": clean_string(raw.get("status")),
                "overview": overview,
                "summary": overview,
                "content": "",
                "sourceUrl": qbank_detail_url(slug),
                "sourceType": SOURCE_TYPE,
                "officialSnapshot": False,
            }
        )

    return normalized


def query_operation(query: Mapping[str, Any]) -> tuple[list[Any], Mapping[str, Any]]:
    key = query.get("queryKey")
    if not isinstance(key, list) or len(key) < 2 or not isinstance(key[0], list):
        return [], {}
    options = key[1] if isinstance(key[1], Mapping) else {}
    query_input = options.get("input")
    return key[0], query_input if isinstance(query_input, Mapping) else {}


def find_page_one_oj_data(next_data: Any) -> Mapping[str, Any]:
    try:
        queries = next_data["props"]["pageProps"]["trpcState"]["json"]["queries"]
    except (KeyError, TypeError) as exc:
        raise ValueError("Next data does not contain the expected tRPC query list") from exc
    if not isinstance(queries, list):
        raise ValueError("Next data tRPC queries value is not an array")

    matches: list[Mapping[str, Any]] = []
    for query in queries:
        if not isinstance(query, Mapping):
            continue
        operation, query_input = query_operation(query)
        if (
            operation == ["interview", "getOJProblemList"]
            and query_input.get("page") == 1
            and query_input.get("company") == COMPANY
            and query_input.get("type") == "oj"
        ):
            state = query.get("state")
            data = state.get("data") if isinstance(state, Mapping) else None
            if isinstance(data, Mapping):
                matches.append(data)

    if len(matches) != 1:
        raise ValueError(
            "expected exactly one page-1 OpenAI OJ query, "
            f"found {len(matches)}"
        )
    return matches[0]


def normalize_oj(next_data: Any) -> tuple[list[dict[str, Any]], int | None, int]:
    oj_data = find_page_one_oj_data(next_data)
    items = oj_data.get("items")
    if not isinstance(items, list):
        raise ValueError("page-1 OpenAI OJ query has no items array")
    declared_total = oj_data.get("total")
    if declared_total is not None and not isinstance(declared_total, int):
        raise ValueError("page-1 OpenAI OJ query has a non-integer total")

    normalized: list[dict[str, Any]] = []
    seen_ids: set[str] = set()
    duplicates_removed = 0
    for index, raw in enumerate(items):
        if not isinstance(raw, Mapping):
            raise ValueError(f"OJ record {index} is not an object")
        question_id = clean_string(raw.get("id"))
        title = clean_string(raw.get("title"))
        if not question_id or not title:
            raise ValueError(f"OJ record {index} is missing id or title")
        if question_id in seen_ids:
            duplicates_removed += 1
            continue
        seen_ids.add(question_id)

        item_company = clean_string(raw.get("company")) or COMPANY
        normalized.append(
            {
                "id": question_id,
                "company": item_company,
                "sourceKind": "oj-page-1",
                "slug": clean_string(raw.get("slug")),
                "title": title,
                "category": "oj",
                "tags": [],
                "roles": [],
                "stages": [],
                "access": "link-only",
                "frequency": "unknown",
                "date": "",
                "duration": None,
                "source_count": None,
                "difficulty": clean_scalar(raw.get("difficulty")),
                "employment_type": clean_scalar(raw.get("employment_type")),
                "isExternalThread": bool(raw.get("isExternalThread")),
                "summary": "",
                "content": "",
                "sourceUrl": oj_detail_url(question_id),
                "sourceType": SOURCE_TYPE,
                "officialSnapshot": False,
            }
        )

    return normalized, declared_total, duplicates_removed


def count_by(records: Iterable[Mapping[str, Any]], key: str) -> dict[str, int]:
    counts = Counter(str(record.get(key) or "unknown") for record in records)
    return dict(sorted(counts.items()))


def source_description(path: Path, role: str) -> dict[str, Any]:
    return {
        "path": str(path.resolve()),
        "role": role,
        "sha256": sha256_file(path),
        "lastModifiedUtc": file_timestamp(path),
    }


def build_payload(qbank_path: Path, next_path: Path) -> dict[str, Any]:
    qbank_questions = normalize_qbank(load_json(qbank_path))
    oj_questions, oj_declared_total, oj_duplicates_removed = normalize_oj(
        load_json(next_path)
    )
    questions = [*qbank_questions, *oj_questions]

    if len({question["id"] for question in questions}) != len(questions):
        raise ValueError("normalized qbank and OJ records contain a cross-source id collision")

    generated_at = datetime.now(timezone.utc).isoformat(timespec="seconds")
    return {
        "schemaVersion": 1,
        "generatedAt": generated_at,
        "meta": {
            "company": COMPANY,
            "description": (
                "Offline catalog metadata imported from two pre-existing user "
                "snapshot files; question bodies were not retrieved."
            ),
            "officialSnapshot": False,
            "completeOfficialMirror": False,
        },
        "provenance": {
            "sourceType": SOURCE_TYPE,
            "officialSnapshot": False,
            "networkAccessed": False,
            "completeOfficialMirror": False,
            "notice": (
                "No network requests were made. This is not a complete official "
                "1point3acres mirror: it contains 45 OpenAI qbank metadata records "
                "and only the OJ items embedded in page 1 of the saved Next data. "
                "Locked question bodies remain empty."
            ),
            "inputs": [
                source_description(qbank_path, "OpenAI qbank metadata"),
                source_description(next_path, "saved company-page Next data"),
            ],
            "ojSelection": {
                "operation": "interview.getOJProblemList",
                "company": COMPANY,
                "type": "oj",
                "page": 1,
                "pageSize": len(oj_questions) + oj_duplicates_removed,
                "declaredTotalAcrossPages": oj_declared_total,
            },
        },
        "counts": {
            "qbankRecords": len(qbank_questions),
            "qbankMembersOnly": sum(
                question["access"] == "members-only" for question in qbank_questions
            ),
            "qbankFreePreview": sum(
                question["access"] == "free-preview" for question in qbank_questions
            ),
            "ojPage1InputRecords": len(oj_questions) + oj_duplicates_removed,
            "ojPage1Records": len(oj_questions),
            "ojDuplicatesRemovedById": oj_duplicates_removed,
            "ojDeclaredTotalAcrossPages": oj_declared_total,
            "outputRecords": len(questions),
            "bySourceKind": count_by(questions, "sourceKind"),
            "byCategory": count_by(questions, "category"),
            "byAccess": count_by(questions, "access"),
        },
        "questions": questions,
    }


def write_json_atomic(path: Path, payload: Mapping[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(f".{path.name}.{os.getpid()}.tmp")
    try:
        with temporary.open("w", encoding="utf-8") as destination:
            json.dump(payload, destination, ensure_ascii=False, indent=2)
            destination.write("\n")
        temporary.replace(path)
    finally:
        if temporary.exists():
            temporary.unlink()


def main(argv: Sequence[str] | None = None) -> int:
    args = parse_args(argv)
    try:
        payload = build_payload(args.qbank_input, args.next_input)
        write_json_atomic(args.output, payload)
    except (OSError, json.JSONDecodeError, ValueError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1

    counts = payload["counts"]
    print(f"wrote {args.output}")
    print(
        "qbank={qbankRecords} (members-only={qbankMembersOnly}, "
        "free-preview={qbankFreePreview}); OJ page 1={ojPage1Records}; "
        "total={outputRecords}".format(**counts)
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
