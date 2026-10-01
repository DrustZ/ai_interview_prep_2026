#!/usr/bin/env python3
"""Attach already-known 1Point3Acres post URLs to saved qbank metadata.

The mapping below was derived only from the user's pre-existing local research
notes.  This script performs no network requests and does not retrieve post
content.  Ambiguous topic matches are intentionally omitted.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
QUESTIONS_PATH = ROOT / "data" / "questions.json"


POSTS_BY_SLUG: dict[str, list[str]] = {
    "hm-bq-why-openai": [
        "https://www.1point3acres.com/bbs/thread-1174510-1-1.html",
    ],
    "memory-allocator": [
        "https://www.1point3acres.com/bbs/thread-1179374-1-1.html",
    ],
    "distributed-cluster-count-topology": [
        "https://www.1point3acres.com/bbs/thread-1171426-1-1.html",
        "https://www.1point3acres.com/bbs/thread-1180678-1-1.html",
    ],
    "toy-language-type-inference": [
        "https://www.1point3acres.com/bbs/thread-1172199-1-1.html",
    ],
    "design-url-shortener": [
        "https://www.1point3acres.com/bbs/thread-1174549-1-1.html",
    ],
    "monster-battle-system": [
        "https://www.1point3acres.com/bbs/thread-1176587-1-1.html",
        "https://www.1point3acres.com/bbs/thread-1180067-1-1.html",
    ],
    "numpy-1nn-wx-b": [
        "https://www.1point3acres.com/bbs/thread-1177444-1-1.html",
    ],
    "transformer-bug-hunt": [
        "https://www.1point3acres.com/bbs/thread-1171609-1-1.html",
        "https://www.1point3acres.com/bbs/thread-1179644-1-1.html",
        "https://www.1point3acres.com/bbs/thread-1168926-1-1.html",
    ],
    "design-chess-game": [
        "https://www.1point3acres.com/bbs/thread-1172810-1-1.html",
        "https://www.1point3acres.com/bbs/thread-1181839-1-1.html",
    ],
    "technical-deep-dive": [
        "https://www.1point3acres.com/bbs/thread-1174510-1-1.html",
        "https://www.1point3acres.com/bbs/thread-1181194-1-1.html",
        "https://www.1point3acres.com/bbs/thread-1180594-1-1.html",
    ],
    "multi-tenant-ci-cd-workflow": [
        "https://www.1point3acres.com/bbs/thread-1174549-1-1.html",
    ],
    "design-google-calendar": [
        "https://www.1point3acres.com/bbs/thread-1174549-1-1.html",
    ],
    "payment-coffee-shop": [
        "https://www.1point3acres.com/bbs/thread-1178674-1-1.html",
        "https://www.1point3acres.com/bbs/thread-1181247-1-1.html",
    ],
    "webhook-delivery-system": [
        "https://www.1point3acres.com/bbs/thread-1174549-1-1.html",
    ],
    "resumable-iterator": [
        "https://www.1point3acres.com/bbs/thread-1180787-1-1.html",
    ],
    "design-slack": [
        "https://www.1point3acres.com/bbs/thread-1174549-1-1.html",
    ],
    "gpu-credits": [
        "https://www.1point3acres.com/bbs/thread-1181418-1-1.html",
        "https://www.1point3acres.com/bbs/thread-1172810-1-1.html",
    ],
    "social-network-follow-graph": [
        "https://www.1point3acres.com/bbs/thread-1172554-1-1.html",
        "https://www.1point3acres.com/bbs/thread-1181536-1-1.html",
    ],
    "crossword-puzzle-solver": [
        "https://www.1point3acres.com/bbs/thread-1174549-1-1.html",
    ],
    "points-of-interest-yelp": [
        "https://www.1point3acres.com/bbs/thread-1174549-1-1.html",
    ],
    "time-based-kv-store": [
        "https://www.1point3acres.com/bbs/thread-1181536-1-1.html",
    ],
    "autograd-hillis-steele-scan": [
        "https://www.1point3acres.com/bbs/thread-1171922-1-1.html",
    ],
    "ip-address-cidr-iterator": [
        "https://www.1point3acres.com/bbs/thread-1181839-1-1.html",
    ],
    "classifier-noisy-annotators": [
        "https://www.1point3acres.com/bbs/thread-1178049-1-1.html",
    ],
    "design-cloud-ide": [
        "https://www.1point3acres.com/bbs/thread-1171984-1-1.html",
    ],
    "chatgpt-enterprise-rag": [
        "https://www.1point3acres.com/bbs/thread-1158070-1-1.html",
    ],
    "rag-search-ml-design": [
        "https://www.1point3acres.com/bbs/thread-1158070-1-1.html",
    ],
    "code-reading-pytorch-refactor": [
        "https://www.1point3acres.com/bbs/thread-1165833-1-1.html",
    ],
    "implement-cd-command": [
        "https://www.1point3acres.com/interview/thread/7100341",
    ],
    "ml-programming-screen": [
        "https://www.1point3acres.com/bbs/thread-1137418-1-1.html",
    ],
    "rl-fundamentals-grpo-debug": [
        "https://www.1point3acres.com/interview/thread/1167043",
    ],
    "recruiter-screen-why-anthropic": [
        "https://www.1point3acres.com/bbs/thread-1143118-1-1.html",
        "https://www.1point3acres.com/bbs/thread-1144012-1-1.html",
    ],
    "onsite-design-doc-review": [
        "https://www.1point3acres.com/bbs/thread-1162478-1-1.html",
    ],
    "design-sora-video-generation": [
        "https://www.1point3acres.com/bbs/thread-1180717-1-1.html",
        "https://www.1point3acres.com/bbs/thread-1177818-1-1.html",
    ],
}


# Useful related reports whose relationship is weaker than the direct/high-
# confidence mappings above.  Keep them clickable, but label the limitation so
# the UI never presents a related round or an older variant as the exact page.
RELATED_POSTS_BY_SLUG: dict[str, list[dict[str, str]]] = {
    "math-reasoning-stopping-time": [
        {
            "url": "https://www.1point3acres.com/bbs/thread-1173645-1-1.html",
            "title": "相关面经 · OpenAI Research Org math-reasoning 轮",
            "note": "该帖证明 math-reasoning 轮与 entropy 等题池背景；不证明当前 stopping-time 条目的精确题面。",
        }
    ],
    "streaming-entropy": [
        {
            "url": "https://www.1point3acres.com/bbs/thread-1173645-1-1.html",
            "title": "相关面经 · OpenAI Research Org entropy calculation",
            "note": "该帖确认 research 轨出现 entropy calculation；不证明 online/block-wise 接口就是当前条目的精确题面。",
        }
    ],
    "recruiter-hr-screen-bq": [
        {
            "url": "https://www.1point3acres.com/bbs/thread-1174510-1-1.html",
            "title": "相关面经 · OpenAI onsite HM/BQ",
            "note": "这是 onsite HM/BQ 相关帖，不是 recruiter screen 的精确原帖。",
        }
    ],
    "rl-fundamentals-grpo-debug": [
        {
            "url": "https://www.1point3acres.com/interview/thread/1166898",
            "title": "相关面经 · Anthropic RL Fundamentals",
            "note": "本地研究将其列为同一轮次的补充报告；当前条目的主匹配仍是 thread 1167043。",
        },
        {
            "url": "https://www.1point3acres.com/bbs/thread-1167940-1-1.html",
            "title": "相关面经 · Anthropic RL/GRPO 讨论",
            "note": "用于交叉核对轮次与追问，不声称是当前题库页的逐字来源。",
        },
    ],
    "performance-engineer-take-home": [
        {
            "url": "https://www.1point3acres.com/bbs/thread-1135727-1-1.html",
            "title": "相关旧版面经 · Accelerator/Performance take-home",
            "note": "该帖描述旧版多核模拟器 take-home；当前公开 performance challenge 已换版本。",
        }
    ],
    "ml-take-home-research": [
        {
            "url": "https://www.1point3acres.com/bbs/thread-1103094-1-1.html",
            "title": "相关面经 · Anthropic RS 四小时 take-home",
            "note": "只确认 RS take-home 的时长和形式；不代表当前条目的精确作业内容。",
        }
    ],
}


def main() -> None:
    payload: dict[str, Any] = json.loads(QUESTIONS_PATH.read_text(encoding="utf-8"))
    questions = payload.get("questions")
    if not isinstance(questions, list):
        raise ValueError("data/questions.json has no questions array")

    matched_records = 0
    assigned_urls = 0
    matched_slugs: set[str] = set()
    related_records = 0
    related_urls = 0
    matched_related_slugs: set[str] = set()
    for question in questions:
        if not isinstance(question, dict):
            continue
        slug = question.get("slug")
        urls = POSTS_BY_SLUG.get(slug)
        if urls:
            question["sourceUrls"] = urls
            question["relatedPostMatch"] = "high-confidence-from-preexisting-local-research"
            matched_records += 1
            assigned_urls += len(urls)
            matched_slugs.add(slug)
        else:
            question.pop("sourceUrls", None)
            question.pop("relatedPostMatch", None)

        sources = question.get("sources")
        if not isinstance(sources, list):
            sources = []
        sources = [
            source
            for source in sources
            if not (
                isinstance(source, dict)
                and source.get("generatedBy") == "add-related-posts"
            )
        ]
        related = RELATED_POSTS_BY_SLUG.get(slug, [])
        for source in related:
            sources.append(
                {
                    **source,
                    "relationship": "related-interview-thread",
                    "confidence": "medium",
                    "generatedBy": "add-related-posts",
                }
            )
        if related:
            related_records += 1
            related_urls += len(related)
            matched_related_slugs.add(slug)
        question["sources"] = sources

    missing = sorted(set(POSTS_BY_SLUG) - matched_slugs)
    if missing:
        raise ValueError(f"mapped slugs not found in questions.json: {missing}")
    missing_related = sorted(set(RELATED_POSTS_BY_SLUG) - matched_related_slugs)
    if missing_related:
        raise ValueError(f"related mapped slugs not found in questions.json: {missing_related}")

    counts = payload.setdefault("counts", {})
    counts["qbankRecordsWithRelatedPosts"] = matched_records
    counts["relatedPostUrlAssignments"] = assigned_urls
    counts["qbankRecordsWithMediumConfidenceRelatedPosts"] = related_records
    counts["mediumConfidenceRelatedPostUrlAssignments"] = related_urls
    provenance = payload.setdefault("provenance", {})
    provenance["relatedPostEnrichment"] = {
        "networkAccessed": False,
        "source": "pre-existing user-owned supplemental research",
        "matchingPolicy": "explicit high-confidence topic matches only; ambiguous matches omitted",
        "matchedRecords": matched_records,
        "assignedUrls": assigned_urls,
        "mediumConfidenceRelatedRecords": related_records,
        "mediumConfidenceRelatedUrls": related_urls,
    }

    QUESTIONS_PATH.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(
        f"Added {assigned_urls} direct post URLs to {matched_records} qbank records; "
        f"added {related_urls} labelled related URLs to {related_records} records"
    )


if __name__ == "__main__":
    main()
