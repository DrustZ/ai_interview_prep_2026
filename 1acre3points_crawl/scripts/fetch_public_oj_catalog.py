#!/usr/bin/env python3
"""Fetch the public OpenAI/Anthropic OJ catalog metadata.

The company pages load their paginated OJ index from a public tRPC query.  This
script saves only the catalog fields returned by that anonymous endpoint.  It
does not log in, retrieve member test cases, or use a third-party unlocker.
"""

from __future__ import annotations

import argparse
import json
import math
import os
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping, Sequence
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT = PROJECT_ROOT / "data" / "public_oj_catalog.json"
ENDPOINT = "https://trpc.1point3acres.com/trpc/interview.getOJProblemList"
DETAIL_BASE = "https://www.1point3acres.com/interview/problems"
PAGE_SIZE = 30
EXPECTED_TOTALS = {"openai": 139, "anthropic": 64}


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--timeout", type=float, default=20.0)
    parser.add_argument(
        "--delay",
        type=float,
        default=0.15,
        help="polite delay between public catalog requests (default: 0.15s)",
    )
    return parser.parse_args(argv)


def clean(value: Any) -> str:
    return value.strip() if isinstance(value, str) else ""


def fetch_page(company: str, page: int, timeout: float) -> Mapping[str, Any]:
    encoded = urlencode(
        {
            "input": json.dumps(
                {
                    "json": {
                        "page": page,
                        "pageSize": PAGE_SIZE,
                        "company": company,
                        "type": "oj",
                    }
                },
                separators=(",", ":"),
            )
        }
    )
    request = Request(
        f"{ENDPOINT}?{encoded}",
        headers={
            "Accept": "application/json",
            "User-Agent": "LocalInterviewCatalog/1.0 (personal snapshot; catalog metadata only)",
        },
    )
    with urlopen(request, timeout=timeout) as response:
        payload = json.load(response)
    try:
        result = payload["result"]["data"]["json"]
    except (KeyError, TypeError) as exc:
        raise ValueError(f"unexpected public catalog response for {company} page {page}") from exc
    if not isinstance(result, Mapping):
        raise ValueError(f"public catalog result is not an object for {company} page {page}")
    return result


def normalize_item(raw: Mapping[str, Any], company: str, page: int, position: int) -> dict[str, Any]:
    question_id = clean(raw.get("id"))
    title = clean(raw.get("title"))
    slug = clean(raw.get("slug"))
    if not question_id or not title:
        raise ValueError(f"{company} page {page} item {position} is missing id/title")
    item_company = clean(raw.get("company")).lower() or company
    if item_company != company:
        raise ValueError(
            f"{company} page {page} item {position} reports company={item_company!r}"
        )
    return {
        "id": question_id,
        "slug": slug,
        "title": title,
        "difficulty": raw.get("difficulty"),
        "company": company,
        "employment_type": raw.get("employment_type"),
        "isExternalThread": bool(raw.get("isExternalThread")),
        "catalogPage": page,
        "catalogPosition": position,
        "sourceUrl": f"{DETAIL_BASE}/{slug or question_id}",
    }


def fetch_company(company: str, timeout: float, delay: float) -> dict[str, Any]:
    first = fetch_page(company, 1, timeout)
    total = first.get("total")
    if not isinstance(total, int) or total < 1:
        raise ValueError(f"{company} public catalog returned invalid total={total!r}")
    expected = EXPECTED_TOTALS[company]
    if total != expected:
        raise ValueError(f"{company} public catalog changed: expected {expected}, received {total}")

    page_count = math.ceil(total / PAGE_SIZE)
    pages: list[dict[str, Any]] = []
    seen: set[str] = set()
    for page in range(1, page_count + 1):
        result = first if page == 1 else fetch_page(company, page, timeout)
        if result.get("total") != total:
            raise ValueError(f"{company} total changed while reading page {page}")
        rows = result.get("items")
        if not isinstance(rows, list):
            raise ValueError(f"{company} page {page} has no items array")
        normalized = [
            normalize_item(row, company, page, position)
            for position, row in enumerate(rows, start=1)
            if isinstance(row, Mapping)
        ]
        if len(normalized) != len(rows):
            raise ValueError(f"{company} page {page} contains a non-object item")
        for item in normalized:
            if item["id"] in seen:
                raise ValueError(f"duplicate {company} OJ id: {item['id']}")
            seen.add(item["id"])
        pages.append({"page": page, "count": len(normalized), "items": normalized})
        if page < page_count and delay > 0:
            time.sleep(delay)

    if len(seen) != total:
        raise ValueError(f"{company} expected {total} unique rows, received {len(seen)}")
    return {
        "company": company,
        "type": "oj",
        "pageSize": PAGE_SIZE,
        "pageCount": page_count,
        "total": total,
        "pages": pages,
    }


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
        companies = [
            fetch_company(company, args.timeout, args.delay)
            for company in ("openai", "anthropic")
        ]
        payload = {
            "schemaVersion": 1,
            "generatedAt": datetime.now(timezone.utc).isoformat(timespec="seconds"),
            "source": {
                "endpoint": ENDPOINT,
                "authentication": "anonymous",
                "contentScope": "public OJ catalog metadata only",
                "memberContentRetrieved": False,
                "thirdPartyUnlockerUsed": False,
            },
            "companies": companies,
            "counts": {
                "openai": companies[0]["total"],
                "anthropic": companies[1]["total"],
                "total": sum(company["total"] for company in companies),
            },
        }
        write_json_atomic(args.output, payload)
    except (HTTPError, URLError, TimeoutError, OSError, json.JSONDecodeError, ValueError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    print(
        f"wrote {args.output}: OpenAI {payload['counts']['openai']}, "
        f"Anthropic {payload['counts']['anthropic']}, total {payload['counts']['total']}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
