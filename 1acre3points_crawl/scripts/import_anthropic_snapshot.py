#!/usr/bin/env python3
"""Merge the user's saved Anthropic catalog metadata into questions.json.

The importer is intentionally offline.  It reads the already-existing local
``anthropic_clean.json`` snapshot, adds its 35 curated qbank rows and 30 saved
OJ rows, and links conservative same-topic sources.  It does not fetch remote
pages or invent records for catalog pages that were not saved locally.
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
DEFAULT_INPUT = (
    PROJECT_ROOT.parent / "my_interview_prep" / "new" / "raw" / "anthropic_clean.json"
)
DEFAULT_OUTPUT = PROJECT_ROOT / "data" / "questions.json"

COMPANY = "anthropic"
EXPECTED_QBANK = 35
EXPECTED_OJ_SAVED = 30
OFFICIAL_TARGET = {"openai": 184, "anthropic": 99}
QBANK_BASE = "https://www.1point3acres.com/interview/problems/company/anthropic"
PROBLEM_BASE = "https://www.1point3acres.com/interview/problems"


# Standalone problem/editorial pages saved in the user's local research set.
# These are same-topic references, not asserted to be the unique source BBS post.
POSTS_BY_SLUG: dict[str, list[tuple[int, str]]] = {
    "coding-bootloader": [(7100492, "Bootloader")],
    "sd-q4-1to1-chat-system": [(7100098, "Design a 1-to-1 Chat System")],
    "oa-task-management": [(7100097, "Task Management System")],
    "oa-bank-system": [(7100004, "Banking System")],
    "oa-file-systems": [(7100005, "Cloud Storage System")],
    "coding-q1-web-crawler": [(7100011, "Web Crawler")],
    "onsite-culture-ai-safety": [(7100007, "Culture & Behavioral Questions")],
    "oa-worker-management": [(7100008, "Employee Management System")],
    "sd-q1-inference-api": [
        (7100015, "Inference API System Design"),
        (7100012, "LLM Request Batching API"),
    ],
    "sd-q2-prompt-playground": [(7100017, "Prompt Playground System Design")],
    "oa-recipe-manager": [(7100006, "Recipe Manager")],
    "coding-q2-lru-cache-durability": [(7100002, "LRU Cache")],
    "sd-q3-model-distribution": [(7100001, "Distributed Model Deployment")],
    "coding-q2-file-deduplication": [(7100000, "Deduplicate Files")],
    "onsite-hm-behavioral": [(7100013, "Hiring Manager Questions")],
    "coding-q1-image-processing": [(7100010, "Batch Image Processor")],
    "coding-q6-tokenizer": [(7100003, "Tokenize")],
    "coding-q3-stack-trace": [(7100016, "Converting Stack Samples to Trace Events")],
    "coding-q4-distributed-mode-median": [(7100009, "Distributed Mode and Median")],
    "oa-in-memory-database": [(7100014, "In-memory Database")],
}


def source(
    url: str,
    title: str,
    relationship: str,
    confidence: str = "high",
    note: str = "",
) -> dict[str, str]:
    result = {
        "url": url,
        "title": title,
        "relationship": relationship,
        "confidence": confidence,
    }
    if note:
        result["note"] = note
    return result


IMAGE_SOURCES = [
    source(
        f"{PROBLEM_BASE}/post/7100010",
        "站内同题题解 · Batch Image Processor",
        "same-problem",
        note="用户本地资料中保存了该同题页。",
    ),
    source(
        f"{PROBLEM_BASE}/d5535584-0980-47fb-862d-6f9f7569791d",
        "站内同题 OJ · 六种 JSON 图像变换",
        "same-problem",
    ),
    source(
        f"{PROBLEM_BASE}/6d14e9e2-3f95-453c-aca6-3f04fcbb34f0",
        "站内同题 OJ · Image Processing Pipeline",
        "same-problem",
    ),
    source(
        "https://www.1point3acres.com/bbs/thread-1154439-1-1.html",
        "直接面经 · 图像处理（六种变换）",
        "direct-interview-report",
    ),
    source(
        "https://www.1point3acres.com/bbs/thread-1157730-1-1.html",
        "直接面经 · m 张图片 × n 个 pipelines",
        "direct-interview-report",
    ),
    source(
        "https://www.1point3acres.com/bbs/thread-1150952-1-1.html",
        "被多篇面经反向引用的同题帖",
        "referenced-report",
        "medium-high",
    ),
    source(
        "https://www.1point3acres.com/bbs/thread-1171459-1-1.html",
        "直接面经 · Anthropic 店面 Q1",
        "direct-interview-report",
    ),
    source(
        "https://www.1point3acres.com/bbs/thread-1171733-1-1.html",
        "直接面经 · single / multi processor",
        "direct-interview-report",
    ),
    source(
        "https://www.1point3acres.com/bbs/thread-1172486-1-1.html",
        "直接面经 · multithreading 变体",
        "direct-interview-report",
    ),
    source(
        "https://www.1point3acres.com/bbs/thread-1173701-1-1.html",
        "直接面经 · 小图到大图并行处理",
        "direct-interview-report",
    ),
    source(
        "https://www.1point3acres.com/bbs/thread-1174702-1-1.html",
        "直接面经 · PIL + ProcessPoolExecutor",
        "direct-interview-report",
    ),
    source(
        "https://www.1point3acres.com/bbs/thread-1158568-1-1.html",
        "相关加面 · blur / flip 图像处理",
        "related-interview-report",
        "medium-high",
    ),
    source(
        "https://www.1point3acres.com/bbs/thread-1161686-1-1.html",
        "相关面经 · Pillow 图片处理",
        "related-interview-report",
        "medium-high",
    ),
    source(
        "https://www.1point3acres.com/bbs/thread-1158153-1-1.html",
        "相关面经 · Q1 图像处理",
        "related-interview-report",
        "medium",
    ),
    source(
        "https://www.1point3acres.com/bbs/thread-1155853-1-1.html",
        "相关面经 · Pillow API",
        "related-interview-report",
        "medium",
    ),
    source(
        "https://www.1point3acres.com/bbs/thread-1161097-1-1.html",
        "相关讨论 · Q1 与 concurrency",
        "related-discussion",
        "medium",
    ),
    source(
        "https://www.1point3acres.com/bbs/thread-1171002-1-1.html",
        "相关讨论 · Q1 语言选择",
        "related-discussion",
        "medium",
    ),
    source(
        "https://www.hellointerview.com/community/questions/image-transform-pipeline/cmj4jzavk00je08adwpqygvow",
        "外站同题 · Image Transform Pipeline",
        "external-same-problem",
    ),
    source(
        "https://prachub.com/coding-questions/generate-outputs-for-images-and-pipelines",
        "外站同题解法 · Images × Pipelines",
        "external-solution",
    ),
    source(
        "https://prachub.com/coding-questions/implement-parallel-image-processing",
        "外站同题解法 · Parallel Image Processing",
        "external-solution",
    ),
    source(
        "https://www.reddit.com/r/OfferEngineering/comments/1ub6od5/anthropic_frontend_phone_screen_not_leetcode_but/",
        "公开候选人讨论 · Images + pipelines",
        "external-interview-report",
    ),
    source(
        "https://www.hack2hire.com/forum/6a3e17c0ca5951c782e59ae3",
        "公开面经 · grayscale / scale / resize",
        "external-interview-report",
    ),
    source(
        "https://www.reddit.com/r/DarkInterview/comments/1sqvv3s/anthropic_interview_questions_reviewed_and/",
        "公开讨论 · Coding Q1 编号映射",
        "mapping-corroboration",
        "medium",
    ),
]


# Public, topic-specific references already present in the user's research
# collection.  Entries are intentionally conservative: exact rounds are high
# confidence; broader track/process write-ups are labelled related/medium.
EXTRA_SOURCES_BY_SLUG: dict[str, list[dict[str, str]]] = {
    "performance-engineer-modeling": [
        source(
            "https://www.1point3acres.com/bbs/thread-1157758-1-1.html",
            "相关面经 · GPU Performance Modeling",
            "related-interview-report",
            "medium-high",
        )
    ],
    "coding-q2-lru-cache-durability": [
        source(
            "https://www.1point3acres.com/interview/thread/1152730",
            "站内面经 · Durable LRU Cache",
            "direct-interview-report",
        ),
        source(
            "https://www.hack2hire.com/question-bank/companies/anthropic/coding-questions/6a2db6215117d1b543565e12",
            "外站同题 · Durable Function Call Cache",
            "external-same-problem",
        ),
    ],
    "coding-q3-stack-trace": [
        source(
            "https://www.1point3acres.com/bbs/thread-1138904-1-1.html",
            "直接面经 · Stack Trace Q3",
            "direct-interview-report",
        ),
        source(
            "https://www.hack2hire.com/question-bank/companies/anthropic/coding-questions/69308191cd79766b0b310224",
            "外站同题 · Function Profiling Events",
            "external-same-problem",
        ),
    ],
    "coding-q6-tokenizer": [
        source(
            "https://www.1point3acres.com/interview/thread/1169657",
            "站内面经 · Coding Q6 Tokenizer",
            "direct-interview-report",
        )
    ],
    "coding-q1-web-crawler": [
        source(
            "https://www.1point3acres.com/bbs/thread-1157666-1-1.html",
            "相关面经 · Concurrent Web Crawler",
            "related-interview-report",
            "medium-high",
        ),
        source(
            "https://www.tryexponent.com/blog/anthropic-system-design-interview",
            "外站题型汇总 · Crawler / inference infra",
            "external-related-guide",
            "medium",
        ),
    ],
    "coding-q2-file-deduplication": [
        source(
            "https://www.1point3acres.com/bbs/thread-1144078-1-1.html",
            "相关面经 · File Dedup",
            "related-interview-report",
            "medium-high",
        )
    ],
    "ml-configuration-system": [
        source(
            "https://www.1point3acres.com/interview/thread/1164302",
            "站内面经 · ML Configuration System",
            "direct-interview-report",
        )
    ],
    "ml-programming-screen": [
        source(
            "https://reyzharkov.com/blog/posts/interviews-2025-ml-research-engineer-uk",
            "外站相关经历 · ML Research Engineer live screen",
            "external-interview-report",
            "medium",
        ),
        source(
            "https://www.finalroundai.com/blog/anthropic-interview-process",
            "外站聚合 · Anthropic ML interview track",
            "external-related-guide",
            "medium",
        ),
    ],
    "sd-q5-data-infrastructure": [
        source(
            "https://www.1point3acres.com/bbs/thread-1167658-1-1.html",
            "直接面经 · Anthropic SD Q5 Data Infrastructure",
            "direct-interview-report",
        ),
        source(
            "https://www.1point3acres.com/interview/thread/1167658",
            "站内摘要镜像 · Data Infrastructure Phone Screen",
            "same-report-mirror",
        ),
    ],
    "rl-fundamentals-grpo-debug": [
        source(
            "https://prachub.com/interview-questions/debug-a-grpo-training-loop-and-explain-ratios",
            "外站同题解法 · Debug GRPO Training Loop",
            "external-solution",
        )
    ],
    "performance-engineer-take-home": [
        source(
            "https://github.com/anthropics/original_performance_takehome",
            "Anthropic 公开仓库 · Original Performance Take-home",
            "official-public-material",
        ),
        source(
            "https://trirpi.github.io/posts/anthropic-performance-takehome/",
            "社区解题记录 · Performance Take-home",
            "external-solution",
        ),
    ],
    "coding-design-data-batcher": [
        source(
            f"{PROBLEM_BASE}/afa9e386-7de2-4dd2-8747-3810328a9c39",
            "站内同题 OJ · Weighted Data Batcher",
            "same-problem",
        ),
        source(
            "https://www.1point3acres.com/bbs/thread-1148586-2-1.html",
            "直接面经 · Weighted Data Batcher",
            "direct-interview-report",
        ),
    ],
    "onsite-project-deep-dive": [
        source(
            "https://www.reddit.com/r/OfferEngineering/comments/1umrpmp/anthropic_jun_2026_staff_swe_infra_interview/",
            "公开面经 · Technical Project Discussion",
            "external-interview-report",
        ),
        source(
            "https://www.1point3acres.com/interview/thread/1137418",
            "站内流程面经 · Project Deep Dive",
            "related-interview-report",
            "medium-high",
        ),
    ],
    "prompting-engineering-with-llms": [
        source(
            "https://www.1point3acres.com/interview/thread/1147266",
            "站内面经 · Prompting & Engineering with LLMs",
            "direct-interview-report",
        )
    ],
    "oa-fellows-dns-resolver": [
        source(
            "https://www.1point3acres.com/interview/thread/1177056",
            "站内面经 · Fellows DNS Resolver OA",
            "direct-interview-report",
        ),
        source(
            "https://www.reddit.com/r/Anthropic/comments/1qovmbs/assessment_for_anthropic_fellows_program_for_ai/",
            "公开讨论 · Fellows assessment",
            "external-interview-report",
            "medium-high",
        ),
    ],
    "agents-coding-llm-tool-use": [
        source(
            "https://www.1point3acres.com/interview/thread/1178346",
            "站内面经 · Claude API Agent Loop",
            "direct-interview-report",
        ),
        source(
            "https://www.reddit.com/r/OfferEngineering/comments/1upc38m/anthropic_jun_2026_forward_deployed_engineerfde/",
            "公开面经 · Build-an-agent track",
            "external-interview-report",
            "medium-high",
        ),
    ],
    "recruiter-screen-why-anthropic": [
        source(
            "https://www.reddit.com/r/Hack2Hire/comments/1t6ncgs/anthropic_interview_process_experience_megathread/",
            "公开流程汇总 · Mission / Why Anthropic",
            "external-related-guide",
            "medium",
        ),
        source(
            "https://interviewing.io/anthropic-interview-questions",
            "外站流程指南 · Recruiter screen",
            "external-related-guide",
            "medium",
        ),
    ],
    "onsite-culture-ai-safety": [
        source(
            "https://www.1point3acres.com/bbs/thread-1141359-1-1.html",
            "直接面经 · Culture / Values",
            "direct-interview-report",
        ),
        source(
            "https://ridhimakhurana.substack.com/p/inside-anthropics-culture-interview",
            "外站分析 · Anthropic Culture Interview",
            "external-related-guide",
            "medium-high",
        ),
        source(
            "https://www.tryexponent.com/experiences/anthropic-senior-software-engineer-interview-2ffa5f",
            "公开面经 · Values / Culture round",
            "external-interview-report",
        ),
    ],
    "mech-interp-take-home": [
        source(
            "https://www.anthropic.com/engineering/AI-resistant-technical-evaluations",
            "Anthropic 官方 · Technical evaluation design",
            "official-related-material",
            "medium",
        )
    ],
    "ml-take-home-research": [
        source(
            "https://blog.faillearnrepeat.net/blog/i-failed-my-anthropic-interview-and-came-to-tell-you-all-about-it-so-you-dont-have-to",
            "公开经历 · Research Fellowship take-home",
            "external-interview-report",
            "medium-high",
        ),
        source(
            "https://www.tryexponent.com/guides/anthropic-ai-safety-fellow-interview",
            "外站指南 · AI Safety Fellow research track",
            "external-related-guide",
            "medium",
        ),
    ],
    "onsite-design-doc-review": [
        source(
            "https://www.hack2hire.com/blog/anthropic-interview-process-rounds-format-timeline-2026",
            "外站流程汇总 · Anthropic interview rounds",
            "external-related-guide",
            "medium",
        )
    ],
}


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, default=DEFAULT_INPUT)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    return parser.parse_args(argv)


def load_json(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def clean(value: Any) -> str:
    return value.strip() if isinstance(value, str) else ""


def clean_list(value: Any) -> list[str]:
    if not isinstance(value, list):
        return []
    return list(dict.fromkeys(clean(item) for item in value if clean(item)))


def post_sources(slug: str) -> list[dict[str, str]]:
    if slug == "coding-q1-image-processing":
        combined = [dict(item) for item in IMAGE_SOURCES]
    else:
        combined = [
        source(
            f"{PROBLEM_BASE}/post/{tid}",
            f"站内同题题解 · {title}",
            "same-problem",
        )
        for tid, title in POSTS_BY_SLUG.get(slug, [])
        ]
    combined.extend(dict(item) for item in EXTRA_SOURCES_BY_SLUG.get(slug, []))
    deduplicated: list[dict[str, str]] = []
    seen: set[str] = set()
    for item in combined:
        if item["url"] not in seen:
            seen.add(item["url"])
            deduplicated.append(item)
    return deduplicated


def normalize_qbank(rows: Any) -> list[dict[str, Any]]:
    if not isinstance(rows, list) or len(rows) != EXPECTED_QBANK:
        raise ValueError(f"expected {EXPECTED_QBANK} Anthropic qbank rows")
    result: list[dict[str, Any]] = []
    for index, raw in enumerate(rows):
        if not isinstance(raw, Mapping):
            raise ValueError(f"qbank row {index} is not an object")
        question_id = clean(raw.get("id"))
        slug = clean(raw.get("slug"))
        if not question_id or not slug:
            raise ValueError(f"qbank row {index} is missing id or slug")
        locked = bool(raw.get("is_locked"))
        public = bool(raw.get("is_public"))
        overview = "" if locked else clean(raw.get("overview"))
        sources = post_sources(slug)
        result.append(
            {
                "id": question_id,
                "company": COMPANY,
                "sourceKind": "qbank",
                "slug": slug,
                "title": clean(raw.get("title")) or f"会员专享题目 · {slug}",
                "category": clean(raw.get("category")) or "uncategorized",
                "tags": clean_list(raw.get("tags")),
                "roles": clean_list(raw.get("roles")),
                "stages": clean_list(raw.get("stages")),
                "access": "members-only" if locked and not public else "free-preview",
                "frequency": clean(raw.get("frequency")) or "unknown",
                "date": clean(raw.get("last_asked")),
                "duration": raw.get("duration_minutes"),
                "source_count": raw.get("source_count"),
                "reported_from": clean(raw.get("reported_from")),
                "reported_to": clean(raw.get("reported_to")),
                "last_asked": clean(raw.get("last_asked")),
                "duration_minutes": raw.get("duration_minutes"),
                "is_new": bool(raw.get("is_new")),
                "is_public": public,
                "is_locked": locked,
                "status": clean(raw.get("status")),
                "overview": overview,
                "summary": overview,
                "content": "",
                "sources": sources,
                "sourceUrl": f"{QBANK_BASE}/{quote(slug, safe='-._~')}",
                "sourceTitle": "一亩三分地官方题库条目",
                "sourceType": "preexisting-user-snapshot",
                "officialSnapshot": False,
                "sourceMatchNote": (
                    "该题由多个相关讨论聚合，不存在已确认的唯一 BBS 原帖。"
                    if slug == "coding-q1-image-processing"
                    else "关联来源来自本地笔记与公开检索；关系和置信度已逐条标注，不声称是唯一原帖。"
                    if sources
                    else "尚未在本地资料中定位到可核验的原始面经。"
                ),
                "sourceCoverage": "related-sources" if sources else "official-only",
            }
        )
    return result


def related_slug_for_oj(title: str) -> str:
    text = title.lower()
    checks = [
        (("image processing",), "coding-q1-image-processing"),
        (("lru cache",), "coding-q2-lru-cache-durability"),
        (("duplicate file", "deduplicate"), "coding-q2-file-deduplication"),
        (("stack trace", "stack sample"), "coding-q3-stack-trace"),
        (("web crawler",), "coding-q1-web-crawler"),
        (("tokenizer", "string processing"), "coding-q6-tokenizer"),
        (("bootloader",), "coding-bootloader"),
        (("recipe",), "oa-recipe-manager"),
        (("task management",), "oa-task-management"),
        (("in-memory database", "in-memory db"), "oa-in-memory-database"),
        (("weighted data batcher",), "coding-design-data-batcher"),
        (("dns",), "oa-fellows-dns-resolver"),
    ]
    for needles, slug in checks:
        if any(needle in text for needle in needles):
            return slug
    return ""


def normalize_oj(rows: Any) -> list[dict[str, Any]]:
    if not isinstance(rows, list) or len(rows) != EXPECTED_OJ_SAVED:
        raise ValueError(f"expected {EXPECTED_OJ_SAVED} saved Anthropic OJ rows")
    result: list[dict[str, Any]] = []
    seen: set[str] = set()
    for index, raw in enumerate(rows):
        if not isinstance(raw, Mapping):
            raise ValueError(f"OJ row {index} is not an object")
        question_id = clean(raw.get("id"))
        title = clean(raw.get("title"))
        if not question_id or not title:
            raise ValueError(f"OJ row {index} is missing id or title")
        if question_id in seen:
            raise ValueError(f"duplicate Anthropic OJ id: {question_id}")
        seen.add(question_id)
        slug = related_slug_for_oj(title)
        sources = post_sources(slug) if slug else []
        result.append(
            {
                "id": question_id,
                "company": COMPANY,
                "sourceKind": "oj-page-1",
                "slug": clean(raw.get("slug")),
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
                "difficulty": raw.get("difficulty"),
                "employment_type": raw.get("employment_type"),
                "isExternalThread": bool(raw.get("isExternalThread")),
                "summary": "",
                "content": "",
                "sources": sources,
                "sourceUrl": f"{PROBLEM_BASE}/{quote(question_id, safe='-._~')}",
                "sourceTitle": "一亩三分地官方 OJ 条目",
                "sourceType": "preexisting-user-snapshot",
                "officialSnapshot": False,
                "sourceCoverage": "related-sources" if sources else "official-only",
                "relatedQbankSlug": slug,
            }
        )
    return result


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def count_by(rows: Iterable[Mapping[str, Any]], key: str) -> dict[str, int]:
    counts = Counter(str(row.get(key) or "unknown") for row in rows)
    return dict(sorted(counts.items()))


def build_payload(existing: Any, saved: Any, input_path: Path) -> dict[str, Any]:
    if not isinstance(existing, Mapping) or not isinstance(existing.get("questions"), list):
        raise ValueError("output JSON must contain a questions array")
    if not isinstance(saved, Mapping):
        raise ValueError("Anthropic snapshot must be an object")

    imported = [
        *normalize_qbank(saved.get("qbank")),
        *normalize_oj(saved.get("oj")),
    ]
    imported_ids = {row["id"] for row in imported}
    retained = [
        row
        for row in existing["questions"]
        if not (
            isinstance(row, Mapping)
            and clean(row.get("company")).lower() == COMPANY
            and clean(row.get("id")) in imported_ids
        )
    ]
    questions = [*retained, *imported]
    if len({(clean(row.get("company")).lower(), clean(row.get("id"))) for row in questions}) != len(
        questions
    ):
        raise ValueError("company/id collision after merge")

    canonical_by_company = count_by(questions, "company")
    canonical_total = len(questions)
    target_total = sum(OFFICIAL_TARGET.values())
    payload = dict(existing)
    payload["generatedAt"] = datetime.now(timezone.utc).isoformat(timespec="seconds")
    payload["meta"] = {
        "companies": ["openai", "anthropic"],
        "description": (
            "Offline canonical catalog metadata imported from pre-existing user snapshots; "
            "question bodies were not retrieved."
        ),
        "officialSnapshot": False,
        "completeOfficialMirror": canonical_total >= target_total,
        "canonicalCatalogRecords": canonical_total,
        "officialReportedRecords": target_total,
    }
    provenance = dict(payload.get("provenance") or {})
    inputs = list(provenance.get("inputs") or [])
    absolute = str(input_path.resolve())
    inputs = [item for item in inputs if not (isinstance(item, Mapping) and item.get("path") == absolute)]
    inputs.append(
        {
            "path": absolute,
            "role": "saved Anthropic qbank and OJ page-1 metadata",
            "sha256": sha256_file(input_path),
            "lastModifiedUtc": datetime.fromtimestamp(
                input_path.stat().st_mtime, timezone.utc
            ).isoformat(timespec="seconds"),
        }
    )
    provenance.update(
        {
            "sourceType": "preexisting-user-snapshot",
            "officialSnapshot": False,
            "networkAccessed": False,
            "completeOfficialMirror": canonical_total >= target_total,
            "notice": (
                f"No network requests were made. {canonical_total}/{target_total} official catalog "
                "records are individually identifiable from local snapshots. The remaining records "
                "are unsaved paginated OJ rows; no placeholder titles or URLs were invented."
            ),
            "inputs": inputs,
            "catalogCoverage": {
                "reportedTarget": OFFICIAL_TARGET,
                "savedByCompany": canonical_by_company,
                "savedTotal": canonical_total,
                "reportedTargetTotal": target_total,
                "missingUnsavedOjRows": target_total - canonical_total,
            },
        }
    )
    payload["provenance"] = provenance
    payload["counts"] = {
        "qbankRecords": sum(row.get("sourceKind") == "qbank" for row in questions),
        "ojSavedRecords": sum(str(row.get("sourceKind", "")).startswith("oj") for row in questions),
        "outputRecords": canonical_total,
        "byCompany": canonical_by_company,
        "bySourceKind": count_by(questions, "sourceKind"),
        "byCategory": count_by(questions, "category"),
        "byAccess": count_by(questions, "access"),
        "withRelatedSources": sum(bool(row.get("sources") or row.get("sourceUrls")) for row in questions),
        "officialReportedRecords": target_total,
        "missingUnsavedOjRows": target_total - canonical_total,
    }
    payload["questions"] = questions
    return payload


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
        existing = load_json(args.output)
        saved = load_json(args.input)
        payload = build_payload(existing, saved, args.input)
        write_json_atomic(args.output, payload)
    except (OSError, json.JSONDecodeError, ValueError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    print(
        f"wrote {args.output}: {payload['counts']['outputRecords']}/"
        f"{payload['counts']['officialReportedRecords']} canonical catalog records"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
