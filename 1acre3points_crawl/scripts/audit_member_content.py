#!/usr/bin/env python3
"""Generate an explicit audit of members-only qbank content coverage.

This script does not fetch protected pages.  It records which entries already
have readable local preparation material, which have a post URL compatible
with the user-provided viewer, and which canonical member bodies have actually
been verified.  Keeping those states separate prevents a preparation guide
from being mislabeled as recovered member text.
"""

from __future__ import annotations

import json
import re
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from urllib.parse import parse_qs, urlparse


ROOT = Path(__file__).resolve().parents[1]
QUESTIONS_PATH = ROOT / "data" / "questions.json"
OUTPUT_PATH = ROOT / "data" / "member_content_audit.json"
VIEWER_URL = "http://117.72.46.162/?code=AGI30S2Z8GX1Y2J7PMER"
VIEWER_ID_PATTERN = re.compile(
    r"(?:^|/)(?:thread-|thread/|post/|pins/)(\d+)",
    re.IGNORECASE,
)


def clean(value: Any) -> str:
    return value.strip() if isinstance(value, str) else ""


def source_urls(question: dict[str, Any]) -> list[str]:
    values: list[str] = []
    for key in ("sourceUrls", "contentSourceUrls"):
        raw = question.get(key, [])
        if isinstance(raw, str):
            values.append(raw)
        elif isinstance(raw, list):
            values.extend(item for item in raw if isinstance(item, str))
    for source in question.get("sources", []):
        if isinstance(source, dict) and clean(source.get("url")):
            values.append(clean(source.get("url")))
    for key in ("sourceUrl", "url"):
        if clean(question.get(key)):
            values.append(clean(question.get(key)))
    return list(dict.fromkeys(values))


def viewer_compatible(url: str) -> bool:
    parsed = urlparse(url)
    hostname = parsed.hostname or ""
    if hostname != "1point3acres.com" and not hostname.endswith(".1point3acres.com"):
        return False
    return bool(VIEWER_ID_PATTERN.search(parsed.path)) or parse_qs(parsed.query).get(
        "tid", [""]
    )[0].isdigit()


def main() -> None:
    payload = json.loads(QUESTIONS_PATH.read_text(encoding="utf-8"))
    questions = payload.get("questions")
    if not isinstance(questions, list):
        raise ValueError("data/questions.json has no questions array")

    members = [
        question
        for question in questions
        if isinstance(question, dict) and clean(question.get("access")) == "members-only"
    ]
    records: list[dict[str, Any]] = []
    for question in members:
        urls = source_urls(question)
        viewer_urls = [url for url in urls if viewer_compatible(url)]
        local_paths = [
            path
            for path in question.get("contentSourceLocalPaths", [])
            if isinstance(path, str) and Path(path).exists()
        ]
        content = clean(question.get("content"))
        verified_member_body = clean(question.get("contentKind")) == "verified-member-canonical-body"
        records.append(
            {
                "id": clean(question.get("id")),
                "company": clean(question.get("company")),
                "slug": clean(question.get("slug")),
                "title": clean(question.get("title")),
                "officialUrl": clean(question.get("sourceUrl")),
                "contentAvailable": bool(content),
                "contentCharacters": len(content),
                "contentKind": clean(question.get("contentKind")),
                "contentQuality": clean(question.get("contentQuality")),
                "contentMatch": clean(question.get("contentMatch")),
                "canonicalMemberBodyVerified": verified_member_body,
                "canonicalVerificationStatus": (
                    "verified" if verified_member_body else "waiting-for-authorized-source"
                ),
                "viewerReady": bool(viewer_urls),
                "viewerCompatibleUrls": viewer_urls,
                "allSourceUrls": urls,
                "localSourcePaths": local_paths,
            }
        )

    kind_counts = Counter(record["contentKind"] for record in records)
    verified = sum(record["canonicalMemberBodyVerified"] for record in records)
    viewer_ready = sum(record["viewerReady"] for record in records)
    readable = sum(record["contentAvailable"] for record in records)
    checked_at = datetime.now(timezone.utc).replace(microsecond=0).isoformat()
    report = {
        "generatedAt": checked_at,
        "questionsGeneratedAt": payload.get("generatedAt") or payload.get("metadata", {}).get(
            "generatedAt"
        ),
        "summary": {
            "memberRecords": len(records),
            "recordsWithReadableLocalContent": readable,
            "recordsWithVerifiedCanonicalMemberBody": verified,
            "recordsWithViewerCompatiblePostUrl": viewer_ready,
            "recordsWithoutViewerCompatiblePostUrl": len(records) - viewer_ready,
            "byContentKind": dict(sorted(kind_counts.items())),
        },
        "thirdPartyTool": {
            "url": VIEWER_URL,
            "checkedAt": checked_at,
            "available": False,
            "quotaLimit": 250,
            "quotaUsed": 250,
            "apiMessage": "访问限制为250次卡,当前已经使用250次",
            "supportedUrlForms": ["thread-<id>", "/thread/<id>", "/post/<id>", "/pins/<id>", "?tid=<id>"],
        },
        "limitations": [
            "Readable preparation content is not evidence that a members-only canonical body was recovered.",
            "The user-provided viewer code is exhausted, so no member body can currently be verified through it.",
            "Entries without a viewer-compatible post ID retain their official qbank URL instead of using a guessed related post.",
        ],
        "records": records,
    }
    OUTPUT_PATH.write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(
        json.dumps(
            {
                "memberRecords": len(records),
                "readableLocalContent": readable,
                "verifiedCanonicalMemberBodies": verified,
                "viewerReady": viewer_ready,
                "viewerMissing": len(records) - viewer_ready,
                "output": str(OUTPUT_PATH),
            },
            ensure_ascii=False,
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
