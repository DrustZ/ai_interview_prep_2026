#!/usr/bin/env python3
"""Attach user-owned local problem/solution text to canonical catalog rows.

This importer is offline.  It extracts the already-saved editorial sections in
``my_interview_prep/new/1p3a-{openai,anthropic}.md`` and maps them to canonical
qbank slugs with an explicit allow-list.  Closely matching OJ rows may inherit
the text as a labelled same-topic preparation reference; they are never claimed
to be an exact copy of the OJ statement.
"""

from __future__ import annotations

import argparse
import html as html_module
import json
import os
import re
import sys
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping, Sequence


PROJECT_ROOT = Path(__file__).resolve().parents[1]
PREP_ROOT = PROJECT_ROOT.parent / "my_interview_prep" / "new"
DEFAULT_QUESTIONS = PROJECT_ROOT / "data" / "questions.json"
DEFAULT_REPORT = PROJECT_ROOT / "data" / "content_coverage.json"
SUPPLEMENTAL_PATH = PROJECT_ROOT / "data" / "supplemental.json"
INTERACTIVE_DATA_PATH = PREP_ROOT / "interactive_1p3acre" / "data.js"
H2H_FULL_PATH = PREP_ROOT / "raw" / "h2h_questions_full.json"
PUBLIC_BODIES_PATH = PROJECT_ROOT / "data" / "qbank_public_bodies.json"
OJ_PUBLIC_SUMMARIES_PATH = PROJECT_ROOT / "data" / "oj_public_summaries.json"
OJ_ORIGINAL_GUIDES_PATH = PROJECT_ROOT / "data" / "oj_original_guides.md"
EXPECTED_ORIGINAL_GUIDE_COUNT = 212

COMPANY_FILES = {
    "openai": {
        "markdown": PREP_ROOT / "1p3a-openai.md",
        "clean": PREP_ROOT / "raw" / "openai_clean.json",
    },
    "anthropic": {
        "markdown": PREP_ROOT / "1p3a-anthropic.md",
        "clean": PREP_ROOT / "raw" / "anthropic_clean.json",
    },
}


TITLE_TO_SLUG: dict[str, dict[str, str]] = {
    "openai": {
        "ModalLock and FairModalLock": "modal-lock-fair-modal-lock",
        "Data Labeling Task Scheduler": "data-labeling-task-scheduler",
        "Multi-Tenant CI/CD Workflow System": "multi-tenant-ci-cd-workflow",
        "Design a Cloud IDE": "design-cloud-ide",
        "Social Network with Snapshots": "social-network-follow-graph",
        "Design Chess.com (Online Chess Game)": "design-chess-game",
        "Design Google Calendar": "design-google-calendar",
        "Design a URL Shortener": "design-url-shortener",
        "Vectorized 1-NN and Neural Network Forward Pass": "numpy-1nn-wx-b",
        "Infection Spread Simulation": "infection-spread-cellular-automata",
        "Design Sora Video Generation Scheduling": "design-sora-video-generation",
        "Design a Crossword Puzzle Solver": "crossword-puzzle-solver",
        "Shard Rebalancing": "shard-rebalance",
        "Monster Battle System": "monster-battle-system",
        "Resumable Iterator with Multi-Dimensional Support": "resumable-iterator",
        "IPv4 Address Iterator with CIDR Support": "ip-address-cidr-iterator",
        "OpenSheet: Spreadsheet with Cell Dependencies": "opensheet-spreadsheet",
        "Webhook Delivery System": "webhook-delivery-system",
        "Mining Novel Data from Large Unlabeled Corpus": "mining-novel-data-unlabeled-corpus",
        "Toy Language Type System": "toy-language-type-inference",
        "Chat Bot System Refactoring": "chat-bot-system-refactoring",
        "Memory Allocator": "memory-allocator",
        "Durable Key-Value Store Serialization": "durable-kv-store-serialization",
        "In-Memory Database with SQL Operations": "in-memory-database-sql",
        "Payment Processing System (Stripe-like)": "payment-coffee-shop",
        "Implement a CD Command": "implement-cd-command",
    },
    "anthropic": {
        "Design a 1-to-1 Chat System": "sd-q4-1to1-chat-system",
        "Task Management System (Online Assessment)": "oa-task-management",
        "Banking System (Online Assessment)": "oa-bank-system",
        "Cloud Storage System (Online Assessment)": "oa-file-systems",
        "Web Crawler": "coding-q1-web-crawler",
        "Culture & Behavioral Interview Questions": "onsite-culture-ai-safety",
        "Employee Management System (Online Assessment)": "oa-worker-management",
        "Inference API System Design": "sd-q1-inference-api",
        "Prompt Playground System Design": "sd-q2-prompt-playground",
        "Recipe Manager (Online Assessment)": "oa-recipe-manager",
        "LRU Cache (Python)": "coding-q2-lru-cache-durability",
        "Distributed Model Deployment System Design": "sd-q3-model-distribution",
        "Deduplicate Files": "coding-q2-file-deduplication",
        "Hiring Manager Interview Questions": "onsite-hm-behavioral",
        "Batch Image Processor": "coding-q1-image-processing",
        "Tokenize (Python)": "coding-q6-tokenizer",
        "LLM Request Batching API System Design": "sd-q1-inference-api",
        "Converting Stack Samples to Trace Events": "coding-q3-stack-trace",
        "Distributed Mode and Median": "coding-q4-distributed-mode-median",
        "In-memory Database (Online Assessment)": "oa-in-memory-database",
        "Bootloader": "coding-bootloader",
    },
}


# Conservative links from canonical qbank slugs to research notes that already
# exist in data/supplemental.json.  These are used only when no full local
# editorial section was available.
SUPPLEMENTAL_BY_SLUG: dict[str, dict[str, list[str]]] = {
    "openai": {
        "hm-bq-why-openai": ["supp-openai-09808751773de45b"],
        "distributed-cluster-count-topology": ["supp-openai-bebbb8e3bef0ed57"],
        "transformer-bug-hunt": ["supp-openai-b692e26dc517c763"],
        "technical-deep-dive": ["supp-openai-88fa830fe0cc26fd"],
        "recruiter-hr-screen-bq": ["supp-openai-292a0dfe7351d212"],
        "payment-coffee-shop": ["supp-openai-d92824437da3b396"],
        "design-slack": ["supp-openai-52c9d79bad2ecd59"],
        "gpu-credits": ["supp-openai-82f72f04fa5c2956", "supp-openai-a80a1e466e53f4c2"],
        "points-of-interest-yelp": ["supp-openai-52c9d79bad2ecd59"],
        "streaming-entropy": ["supp-openai-9c8435c5d61fa79d", "supp-openai-73e92ada799af1e4"],
        "time-based-kv-store": ["supp-openai-88cd45bbe9fb03ed"],
        "autograd-hillis-steele-scan": ["supp-openai-3a69380ee4d5975e", "supp-openai-c6a67539d8279d7d"],
        "gpt-3-playground": ["supp-openai-e3139fdb4ddb290d"],
        "classifier-noisy-annotators": ["supp-openai-5b9e6a1d95180247"],
        "chatgpt-enterprise-rag": ["supp-openai-ba770fa6ec9b58cf"],
        "rag-search-ml-design": ["supp-openai-ba770fa6ec9b58cf"],
        "implement-cd-command": ["supp-openai-d35ed96f240d20d7"],
    },
    "anthropic": {
        "performance-engineer-modeling": ["supp-anthropic-e64a9c3470b64d8a"],
        "ml-configuration-system": ["supp-anthropic-3d3af6f5bd510e8f"],
        "sd-q5-data-infrastructure": ["supp-anthropic-07170f29397fdfb8"],
        "rl-fundamentals-grpo-debug": ["supp-anthropic-fb92a92fc2db75bf"],
        "performance-engineer-take-home": ["supp-anthropic-abac7468b7edaafd"],
        "coding-design-data-batcher": ["supp-anthropic-5bd449afaa2bda2b"],
        "onsite-project-deep-dive": ["supp-anthropic-cc457bde56f3264d"],
        "prompting-engineering-with-llms": ["supp-anthropic-20ca0dd72faab793"],
        "oa-fellows-dns-resolver": ["supp-anthropic-e36bd64fca7e5b23"],
        "agents-coding-llm-tool-use": ["supp-anthropic-ef989a4345347bde"],
        "recruiter-screen-why-anthropic": ["supp-anthropic-872cf8a087c899ce"],
        "coding-bootloader": ["supp-anthropic-ac1f9017b0277338"],
        "ml-take-home-research": ["supp-anthropic-6116c672dd25f304"],
    },
}


CUSTOM_QBANK_APPENDIX: dict[tuple[str, str], str] = {
    (
        "anthropic",
        "performance-engineer-modeling",
    ): """\
### 本地面经中的具体追问

现有本地笔记把该轮与 thread-1157758 对应，并记录了两个明确 follow-up：

1. 给定一个输入 activation（例如 m×k）、一个输出 activation（例如 m×n）和模型权重（k×n），判断它们能否同时放进 VRAM，并解释计算与通信成本。
2. 比较两张 GPU 上的 Pipeline Parallelism 与 Tensor Parallelism：端到端耗时、每卡内存占用以及两种方案的 trade-off。

准备时应能从矩阵乘 FLOPs、参数/activation 字节数、显存容量与互连带宽估算瓶颈，并说明 arithmetic intensity、流水线 bubble、tensor-parallel all-reduce 成本。以上来自用户本地 `questions_and_solutions.md` 的既有笔记，不代表未公开的逐字题面。""",
    (
        "anthropic",
        "coding-design-data-batcher",
    ): """\
### 三阶段题意与可运行主解

公开 OJ 条目把要求分成三步：(1) `batch_size` 可被权重和整除时，按正整数权重混合多个 DataRegistry iterator；(2) `offset` 表示全局混合样本流中已经跳过的 sample 数，并支持可序列化的 save/load；(3) 去掉整除条件，仍需固定 batch 大小、长期满足权重比例并能确定性恢复。

最直接的做法不是随机抽样，而是先定义一个与 batch 边界无关的无限确定性流。权重 `A:B=2:1` 对应周期 `A,A,B`，全局流是 `A,A,B,A,A,B,...`，batch 只是对这个流连续切片。当 batch size 不整除 3 时，余数会自动落入下一批，不会永久偏向某个 source。

全局位置 `p` 决定调度 phase：`p % sum(weights)`；用权重前缀和二分找到 source。初始化到任意 offset 时，设 `q,r = divmod(offset, sum(weights))`，每个 source 的已消费数等于 `q * weight + 该 source 在周期前 r 个位置中的出现数`。因此若 registry 支持 `get_iterator(name, offset=...)`，无需重放全局流即可恢复；只有 `get_iterator(name)` 时则必须逐个 `next()` 重放到每源 offset。

checkpoint 保存算法/状态版本、datasets 的稳定顺序、weights、batch size、下一全局 offset、每源 offset 和 registry version。恢复时必须校验这些字段；registry 已变化时静默继续会破坏确定性。完整 Python 实现还处理了输入校验、有限 source 耗尽不返回半批、JSON checkpoint、配置篡改和 registry 版本漂移。随机 categorical sampling 只有在面试官明确要求概率随机时才需要 seeded/counter-based RNG。""",
}


CUSTOM_QBANK_APPENDIX_PATHS: dict[tuple[str, str], list[Path]] = {
    (
        "anthropic",
        "performance-engineer-modeling",
    ): [
        PROJECT_ROOT.parent
        / "my_interview_prep"
        / "01_company_notes"
        / "anthropic"
        / "questions_and_solutions.md"
    ],
    (
        "anthropic",
        "coding-design-data-batcher",
    ): [
        PROJECT_ROOT / "practice" / "anthropic" / "weighted_data_batcher.py",
        PROJECT_ROOT / "tests" / "test_weighted_data_batcher.py",
    ],
}


LOCAL_PRACTICE_BY_SLUG: dict[tuple[str, str], list[str]] = {
    ("anthropic", "oa-bank-system"): ["practice/anthropic/banking_system_full.py"],
    ("anthropic", "coding-design-data-batcher"): [
        "practice/anthropic/weighted_data_batcher.py"
    ],
    ("anthropic", "coding-q2-lru-cache-durability"): [
        "practice/anthropic/durable_function_call_cache.py"
    ],
    ("anthropic", "agents-coding-llm-tool-use"): [
        "practice/anthropic/agent_tool_use/agent.py",
        "practice/anthropic/agent_tool_use/README.md",
    ],
    ("anthropic", "coding-bootloader"): [
        "practice/anthropic/bootloader_repair.py"
    ],
    ("anthropic", "oa-file-systems"): [
        "practice/anthropic/cloud_storage_full.py"
    ],
    ("anthropic", "oa-worker-management"): [
        "practice/anthropic/employee_management.py"
    ],
    ("anthropic", "oa-in-memory-database"): ["practice/anthropic/in_memory_db.py"],
    ("anthropic", "oa-recipe-manager"): ["practice/anthropic/recipe_manager.py"],
    ("anthropic", "oa-task-management"): ["practice/anthropic/task_manager.py"],
}


LOCAL_PRACTICE_TESTS_BY_SLUG: dict[tuple[str, str], str] = {
    ("anthropic", "oa-bank-system"): "tests/test_banking_system_full.py",
    ("anthropic", "coding-design-data-batcher"): "tests/test_weighted_data_batcher.py",
    ("anthropic", "coding-q2-lru-cache-durability"): (
        "tests/test_durable_function_call_cache.py"
    ),
    ("anthropic", "agents-coding-llm-tool-use"): (
        "tests/test_claude_stock_agent.py"
    ),
    ("anthropic", "coding-bootloader"): "tests/test_bootloader_repair.py",
    ("anthropic", "oa-file-systems"): "tests/test_cloud_storage_full.py",
    ("anthropic", "oa-worker-management"): "tests/test_employee_management.py",
}


OJ_SUPPLEMENTAL_BY_ID: dict[str, list[str]] = {
    "9783914a-7d86-5a41-94e1-af1b1f9fb063": ["supp-openai-0765e25ba98a5834"],
    "a4cd6a8e-afaa-5155-9e02-d089c0210493": ["supp-openai-6f2dacfeed92c0c4"],
    "b4ff5eff-1541-5da7-b251-598d75a41f06": ["supp-openai-e3ce7763f049155f"],
    "ee08a6d0-0eac-4767-86af-19287ae5af50": ["supp-openai-6f2dacfeed92c0c4"],
    "fbde06cd-0253-4b64-a01a-9ea551c06435": ["supp-openai-0765e25ba98a5834"],
    "e27c0df7-1849-4946-8f9d-70773e7d96e3": ["supp-openai-0765e25ba98a5834"],
    "549736b2-61b8-48ae-aa7f-45dbce76c46b": ["supp-anthropic-8e08f7c98a3176c3"],
}


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--questions", type=Path, default=DEFAULT_QUESTIONS)
    parser.add_argument("--report", type=Path, default=DEFAULT_REPORT)
    return parser.parse_args(argv)


def clean_text(value: Any) -> str:
    return value.strip() if isinstance(value, str) else ""


def normalize_display_title(title: str) -> str:
    """Restore common technical/company acronyms lost by title-casing."""
    replacements = {
        "Hm": "HM",
        "Bq": "BQ",
        "Openai": "OpenAI",
        "Oa": "OA",
        "Ai": "AI",
        "Api": "API",
        "Llm": "LLM",
        "Llms": "LLMs",
        "Lru": "LRU",
        "Ci": "CI",
        "Cd": "CD",
        "Dns": "DNS",
        "Gpu": "GPU",
        "Kv": "KV",
        "Ip": "IP",
        "Cidr": "CIDR",
        "Sql": "SQL",
        "Sse": "SSE",
        "Sd": "SD",
        "Grpo": "GRPO",
        "Numpy": "NumPy",
        "Pytorch": "PyTorch",
        "1Nn": "1-NN",
    }
    result = title
    for original, replacement in replacements.items():
        result = re.sub(rf"\b{re.escape(original)}\b", replacement, result)
    return result


def sanitize_markdown(text: str) -> str:
    text = text.replace("\x00", "")
    kept: list[str] = []
    for line in text.splitlines():
        stripped = line.strip()
        # Saved HTML occasionally leaked an entire minified stylesheet into a
        # single Markdown line.  It is not question content and can be safely
        # discarded while retaining the surrounding editorial.
        if len(line) > 8000:
            continue
        if line.count("--tw-") >= 8 or ("@keyframes" in line and "{" in line):
            continue
        if stripped.startswith("window.__") and len(stripped) > 500:
            continue
        kept.append(line.rstrip())

    result = "\n".join(kept)
    result = result.replace("在代码编辑器中练习练习", "")
    result = result.replace("在代码编辑器中练习", "")
    result = re.sub(r"\n{4,}", "\n\n\n", result).strip()
    return result


def restore_pre_blocks(markdown: str, html_path: Path) -> str:
    """Restore PRE0/PRE1 placeholders from the matching saved public HTML."""
    if "PRE" not in markdown or not html_path.exists():
        return markdown
    html_text = html_path.read_text(encoding="utf-8", errors="replace")
    start = html_text.rfind("<div class=markdown-body>")
    if start < 0:
        start = html_text.rfind('<div class="markdown-body">')
    if start >= 0:
        end_candidates = [
            html_text.find("在代码编辑器中练习", start),
            html_text.find("</article>", start),
        ]
        end_candidates = [value for value in end_candidates if value >= 0]
        html_text = html_text[start : min(end_candidates) if end_candidates else None]

    pattern = re.compile(
        r"<pre(?:\s[^>]*)?>\s*<code(?P<attrs>(?:\s[^>]*)?)>"
        r"(?P<body>.*?)</code>\s*</pre>",
        re.IGNORECASE | re.DOTALL,
    )
    blocks: list[str] = []
    for match in pattern.finditer(html_text):
        attrs = match.group("attrs") or ""
        language_match = re.search(r"language-([A-Za-z0-9_+-]+)", attrs)
        language = language_match.group(1) if language_match else ""
        body = re.sub(r"<[^>]+>", "", match.group("body"))
        body = html_module.unescape(body).strip("\n")
        fence = "````" if "```" in body else "```"
        blocks.append(f"{fence}{language}\n{body}\n{fence}")

    def replacement(match: re.Match[str]) -> str:
        index = int(match.group(1))
        if index < len(blocks):
            return blocks[index]
        return "`[本地 HTML 中未找到该代码片段]`"

    return re.sub(r"\bPRE(\d+)\b", replacement, markdown)


def load_json(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def original_guide_index() -> dict[str, dict[str, Any]]:
    """Load human-authored, explicitly non-canonical OJ preparation guides."""
    text = OJ_ORIGINAL_GUIDES_PATH.read_text(encoding="utf-8")
    marker = re.compile(r"<!--\s*guide\s+(\{.*?\})\s*-->", re.DOTALL)
    matches = list(marker.finditer(text))
    result: dict[str, dict[str, Any]] = {}
    for index, match in enumerate(matches):
        metadata = json.loads(match.group(1))
        question_id = clean_text(metadata.get("id"))
        if not question_id:
            raise ValueError("original guide marker is missing id")
        if question_id in result:
            raise ValueError(f"duplicate original guide id: {question_id}")
        end = matches[index + 1].start() if index + 1 < len(matches) else len(text)
        content = text[match.end() : end].strip()
        if not content:
            raise ValueError(f"original guide {question_id} has no content")
        sources = metadata.get("sources")
        if not isinstance(sources, list):
            sources = []
        result[question_id] = {
            **metadata,
            "content": content,
            "sources": [source for source in sources if isinstance(source, Mapping)],
        }
    if len(result) != EXPECTED_ORIGINAL_GUIDE_COUNT:
        raise ValueError(
            f"expected {EXPECTED_ORIGINAL_GUIDE_COUNT} original preparation guides, found {len(result)}"
        )
    return result


def title_sources(clean_payload: Mapping[str, Any], html_dir: Path) -> dict[str, dict[str, Any]]:
    rows = clean_payload.get("external")
    if not isinstance(rows, list):
        raise ValueError("clean snapshot has no external array")
    result: dict[str, dict[str, Any]] = {}
    for raw in rows:
        if not isinstance(raw, Mapping):
            continue
        title = clean_text(raw.get("title"))
        tid = raw.get("tid")
        if not title or not isinstance(tid, int):
            continue
        candidate = {"title": title, "tid": tid, "hasHtml": (html_dir / f"{tid}.html").exists()}
        existing = result.get(title)
        if existing is None or (candidate["hasHtml"] and not existing["hasHtml"]):
            result[title] = candidate
    return result


def extract_external_sections(
    company: str,
    markdown_path: Path,
    clean_path: Path,
) -> dict[str, list[dict[str, Any]]]:
    markdown = markdown_path.read_text(encoding="utf-8", errors="replace").replace("\x00", "")
    external_start = markdown.find("# 二、外链帖题解")
    qbank_start = markdown.find("# 三、会员题库", external_start + 1)
    if external_start < 0 or qbank_start < 0:
        raise ValueError(f"{markdown_path} is missing expected section boundaries")
    external_text = markdown[external_start:qbank_start]

    sources = title_sources(load_json(clean_path), clean_path.parent / "1p3a_html")
    positions: list[tuple[int, str]] = []
    for title in sources:
        marker = f"## {title}\n"
        offset = external_text.find(marker)
        if offset >= 0:
            positions.append((offset, title))
    positions.sort()

    by_slug: dict[str, list[dict[str, Any]]] = defaultdict(list)
    allowed = TITLE_TO_SLUG[company]
    for index, (offset, title) in enumerate(positions):
        if title not in allowed:
            continue
        end = positions[index + 1][0] if index + 1 < len(positions) else len(external_text)
        section = sanitize_markdown(external_text[offset:end])
        # Tiny sections generally contain only a heading and an unavailable
        # message.  Do not mislabel those as full content.
        meaningful = re.sub(r"[`#>*_\-\s]", "", section)
        if len(meaningful) < 240:
            continue
        source_meta = sources[title]
        if source_meta["hasHtml"]:
            section = restore_pre_blocks(
                section,
                clean_path.parent / "1p3a_html" / f"{source_meta['tid']}.html",
            )
            section = sanitize_markdown(section)
        by_slug[allowed[title]].append(
            {
                "title": title,
                "tid": source_meta["tid"],
                "content": section,
                "sourceUrl": f"https://www.1point3acres.com/interview/problems/post/{source_meta['tid']}",
                "localPath": str(markdown_path.resolve()),
            }
        )
    return dict(by_slug)


def oj_topic_slug(company: str, title: str) -> str:
    text = title.lower()
    if company == "openai":
        checks = [
            (("memory allocator", "malloc and free", "malloc/free"), "memory-allocator"),
            (("incorrect data labeler", "human labeling", "label noise", "low-quality annotator", "bad annotation"), "classifier-noisy-annotators"),
            (("infection", "infectious disease", "infect all", "infect a network", "cell simulation"), "infection-spread-cellular-automata"),
            (("resumable iterator", "resumable list iterator", "resumable 2d iterator"), "resumable-iterator"),
            (("social network",), "social-network-follow-graph"),
            (("machine topology", "topology reconstruction", "count nodes in a distributed tree", "network topology message", "async message bus"), "distributed-cluster-count-topology"),
            (("monster fighting", "monster battle", "monster duel", "pokémon battle", "pokemon battle"), "monster-battle-system"),
            (("1-nearest neighbor", "1-nearest-neighbor", "1nn classifier", "np and nn layers"), "numpy-1nn-wx-b"),
            (("streaming entropy", "stable entropy from logits"), "streaming-entropy"),
            (("chatgpt chat interface", "chatgpt-like chat ui", "chatgpt integration"), "gpt-3-playground"),
            (("matrix multiplication forward and backward", "matrix multiplication vs autograd", "softmax cross-entropy", "backprop"), "autograd-hillis-steele-scan"),
            (("basic sql querying", "sql-like query engine", "basic sql features", "database with multi-condition query", "simple database class", "key-value database crud"), "in-memory-database-sql"),
            (("minigpt", "transformer implementation", "transformer model debugging", "transformer model training", "multi-head attention", "minimal neural network training loop", "ml debugging with transformer", "grpo rl training"), "transformer-bug-hunt"),
            (("ip address to cidr", "ip address iterator", "ipv4 iterator"), "ip-address-cidr-iterator"),
            (("ttl cache", "time-travel", "versioned snapshot"), "time-based-kv-store"),
            (("persistent key-value", "write-ahead log", "kv store with serialization", "kv store with shutdown", "file serialization", "serialization/deserialization", "serialization and de-serialization"), "durable-kv-store-serialization"),
            (("simple key-value store", "kv store implementation"), "durable-kv-store-serialization"),
            (("ai, human, task", "task scheduling for human labelers", "data labeling task scheduler"), "data-labeling-task-scheduler"),
            (("gpu credits", "gpu credit", "accountbalance", "time-based grants"), "gpu-credits"),
            (("type a language", "toy language", "type inference"), "toy-language-type-inference"),
            (("distribution of llm decoding stopping time",), "math-reasoning-stopping-time"),
            (("image classification with noise",), "classifier-noisy-annotators"),
            (("python dependency versions",), "version-dependency"),
            (("remote devbox", "remote ide"), "design-cloud-ide"),
            (("crossword puzzle",), "crossword-puzzle-solver"),
            (("cicd", "ci/cd"), "multi-tenant-ci-cd-workflow"),
            (("spreadsheet", "excel sheet"), "opensheet-spreadsheet"),
            (("slack",), "design-slack"),
            (("chatapp with bots", "chatbot channel", "chatbot codebase", "chatbot development"), "chat-bot-system-refactoring"),
            (("cd command", "`cd` command", "cd directory navigation", "unix-like `cd`"), "implement-cd-command"),
        ]
    else:
        checks = [
            (("lru cache",), "coding-q2-lru-cache-durability"),
            (("tokenizer", "tokenization", "llm-oriented string processing", "longest-match token"), "coding-q6-tokenizer"),
            (("in-memory database",), "oa-in-memory-database"),
            (("stack trace",), "coding-q3-stack-trace"),
            (("duplicate file", "deduplicate", "file deduplication"), "coding-q2-file-deduplication"),
            (("recipe",), "oa-recipe-manager"),
            (("task management",), "oa-task-management"),
            (("image processing", "image transformation", "process cat images"), "coding-q1-image-processing"),
            (("web crawler",), "coding-q1-web-crawler"),
            (("bootloader",), "coding-bootloader"),
            (("dns solver",), "oa-fellows-dns-resolver"),
            (("weighted data batcher", "design a data batcher"), "coding-design-data-batcher"),
            (("prompt template deduplication",), "prompting-engineering-with-llms"),
            (("extratrees", "numpy debugging"), "ml-programming-screen"),
            (("basic sql",), "oa-in-memory-database"),
            (("capacity management",), "sd-q5-data-infrastructure"),
            (("grpo", "rl training bug"), "rl-fundamentals-grpo-debug"),
            (("prompt calls", "gpt servers"), "sd-q1-inference-api"),
            (("model deployment in a cluster",), "sd-q3-model-distribution"),
            (("constant latency inference api",), "sd-q1-inference-api"),
            (("efficiency of distributed systems",), "performance-engineer-modeling"),
        ]
    for needles, slug in checks:
        if any(needle in text for needle in needles):
            return slug
    return ""


def source_object(section: Mapping[str, Any]) -> dict[str, str]:
    return {
        "url": clean_text(section.get("sourceUrl")),
        "title": f"本地已保存题面/解法 · {clean_text(section.get('title'))}",
        "relationship": "local-saved-editorial",
        "confidence": "high",
        "note": "正文来自用户工作区中已存在的本地 Markdown 快照。",
    }


def merge_source(question: dict[str, Any], new_source: Mapping[str, Any]) -> None:
    sources = question.get("sources")
    if not isinstance(sources, list):
        sources = []
    url = clean_text(new_source.get("url"))
    if url and not any(isinstance(item, Mapping) and clean_text(item.get("url")) == url for item in sources):
        sources.append(dict(new_source))
    question["sources"] = sources


def build_content(sections: list[Mapping[str, Any]]) -> str:
    chunks = [clean_text(section.get("content")) for section in sections]
    return "\n\n---\n\n".join(chunk for chunk in chunks if chunk)


def editorial_quality(slug: str, content: str) -> str:
    lower = content.lower()
    if len(content) < 1000:
        return "brief-topic-summary"
    if slug in {"onsite-culture-ai-safety", "onsite-hm-behavioral"}:
        return "question-set-and-advice"
    if slug.startswith("design-") or slug.startswith("sd-") or "system design" in lower:
        return "design-guide"
    if "```" in content and ("solution" in lower or "reference implementation" in lower):
        return "problem-and-solution"
    if any(token in slug for token in ("oa-", "in-memory-database")):
        return "requirements-examples-and-discussion"
    return "problem-and-discussion"


def supplemental_index() -> dict[str, dict[str, Any]]:
    payload = load_json(SUPPLEMENTAL_PATH)
    rows = payload.get("questions") if isinstance(payload, Mapping) else None
    if not isinstance(rows, list):
        raise ValueError("supplemental payload has no questions array")
    return {
        clean_text(row.get("id")): dict(row)
        for row in rows
        if isinstance(row, Mapping) and clean_text(row.get("id"))
    }


def qbank_preview_index() -> dict[str, dict[str, str]]:
    raw = INTERACTIVE_DATA_PATH.read_text(encoding="utf-8", errors="replace").strip()
    raw = re.sub(r"^window\.DATA\s*=\s*", "", raw, count=1)
    raw = re.sub(r";\s*$", "", raw, count=1)
    payload = json.loads(raw)
    rows = payload.get("problems") if isinstance(payload, Mapping) else None
    if not isinstance(rows, list):
        raise ValueError("interactive data has no problems array")
    result: dict[str, dict[str, str]] = {}
    for row in rows:
        if not isinstance(row, Mapping) or clean_text(row.get("source")) != "qbank":
            continue
        url = clean_text(row.get("url"))
        if not url:
            continue
        result[url] = {
            "title": normalize_display_title(clean_text(row.get("title"))),
            "overview": clean_text(row.get("overview")),
        }
    return result


def bootloader_local_content() -> str:
    payload = load_json(H2H_FULL_PATH)
    if not isinstance(payload, Mapping):
        return ""
    rows = [
        row
        for key, row in payload.items()
        if isinstance(key, str)
        and key.startswith("6a373b2b6849fecc81442861_")
        and isinstance(row, Mapping)
    ]
    if not rows:
        return ""
    description = next((clean_text(row.get("description")) for row in rows if clean_text(row.get("description"))), "")
    lines = ["## Repair Bootloader Program", "", description]
    for index, row in enumerate(rows, start=1):
        insights = row.get("insights")
        if not isinstance(insights, Mapping):
            continue
        lines.extend(["", f"### Part {index}：本地保存的提示与追问"])
        for label, key in (
            ("核心目标", "quickSummary"),
            ("解题提示", "hints"),
            ("常见追问", "likelyInterviewFollowUps"),
            ("考察点", "whatThisTests"),
        ):
            values = insights.get(key)
            if isinstance(values, list) and values:
                lines.extend(["", f"#### {label}"])
                lines.extend(f"- {clean_text(value)}" for value in values if clean_text(value))
    return sanitize_markdown("\n".join(lines))


def build_research_content(records: list[Mapping[str, Any]]) -> str:
    chunks: list[str] = []
    for record in records:
        title = clean_text(record.get("title"))
        detail = clean_text(record.get("detail")) or clean_text(record.get("summary"))
        hint = clean_text(record.get("solutionHint"))
        lines = [f"## {title}" if title else "## 本地研究笔记"]
        if detail:
            lines.extend(["", detail])
        if hint:
            lines.extend(["", "### 解题与准备提示", "", hint])
        chunks.append("\n".join(lines).strip())
    return "\n\n---\n\n".join(chunk for chunk in chunks if chunk)


def research_source(record: Mapping[str, Any]) -> dict[str, str]:
    return {
        "url": clean_text(record.get("url")),
        "title": f"本地研究笔记 · {clean_text(record.get('title'))}",
        "relationship": "local-research-note",
        "confidence": "medium-high",
        "note": "正文为用户工作区中已有的题目摘要与解题提示；不是付费页面逐字复制。",
    }


def title_derived_outline(title: str, source_url: str) -> str:
    lower = title.lower()
    if "falling path" in lower:
        approach = "使用动态规划：状态包含所在行/列以及剩余垂直跳跃次数；逐层转移普通移动、受限跳跃和 bonus，保存 predecessor 以便还原路径。"
    elif "sliding window" in lower or "message event aggregation" in lower:
        approach = "按时间维护 deque 或有序事件桶，并用哈希表维护窗口内聚合值；到来新事件时先驱逐过期项，再 O(1) 更新统计。讨论乱序事件、水位线和内存上限。"
    elif "chat interface" in lower or "figma" in lower:
        approach = "先拆分可测试组件与状态模型，再实现输入、消息列表、loading/error/streaming 状态；补充无障碍、断线重试、列表虚拟化和端到端测试。"
    elif "ipv4" in lower:
        approach = "使用回溯枚举 4 段，每段 1–3 位、0–255，禁止非法前导零；用剩余字符数剪枝，并用针对边界值的测试验证。"
    elif "double descent" in lower:
        approach = "生成可复现实验数据，遍历特征维度/样本比，分别计算训练和测试误差；控制随机种子与正则化，绘制插值阈值附近的误差曲线并解释 bias/variance。"
    elif "conway" in lower or "cell simulation" in lower or "infect" in lower:
        approach = "把每一轮更新建立在上一轮快照上，避免同轮连锁修改；感染传播用多源 BFS，通用细胞自动机用邻居计数与双缓冲。"
    elif "rate limiter" in lower:
        approach = "先实现 token bucket 或 sliding-window counter，再讨论 Redis Lua 原子更新、clock skew、分片、一致性与后端故障时的 fail-open/fail-closed。"
    elif "a/b test" in lower:
        approach = "逐项检查随机分流、样本独立性、指标分母、方差估计和统计检验；构造小型确定性数据验证均值、置信区间、p-value 与多重检验修正。"
    elif "sql" in lower:
        approach = "围绕过滤、聚合、JOIN 与窗口函数写出可运行查询；明确 NULL、重复行、分组粒度和排序稳定性，并讨论索引。"
    elif "draw paths" in lower or "strokes" in lower:
        approach = "先澄清点与线段的输入/输出模型；构图后寻找满足覆盖约束的路径，区分允许重复边/点的情形，并用连通性与奇度顶点分析可行性。"
    elif "extratrees" in lower:
        approach = "先用固定随机种子和极小数据集复现；逐层验证随机特征/阈值采样、split mask、叶节点终止条件和 ensemble 聚合，比较参考实现的 shape 与预测。"
    elif "prompt template deduplication" in lower:
        approach = "定义模板的 canonical key（规范化文本与参数顺序），用哈希表去重；高并发下用分片锁或原子 put-if-absent，并讨论碰撞、TTL 和跨机一致性。"
    elif "capacity management" in lower or "data analysis" in lower:
        approach = "完成数据质量检查、缺失/异常处理、分组容量趋势和峰值分析；建立可解释 baseline 预测，给出容量阈值、置信区间和可操作建议。"
    elif "job scheduler" in lower:
        approach = "先建立任务、依赖和状态机，再用有界 worker pool 调度；重点检查锁顺序、重复执行、取消、限流与失败重试，并用 deterministic scheduler 和故障注入测试死锁/竞态。"
    elif any(token in lower for token in ("jetpack compose", "android", "ios", "uikit", "swiftui")):
        approach = "按 UI 状态拆分 view model 与组件，覆盖输入校验、加载/成功/失败状态和生命周期；补充无障碍、旋转/恢复、网络取消以及单元与截图测试。"
    elif "read/write-optimized data structure" in lower:
        approach = "先量化读写比例、范围查询和持久化要求，再比较 hash index、B-tree 与 LSM-tree；说明写缓冲、compaction、缓存、并发控制和放大效应。"
    elif "attention" in lower or "transformer" in lower:
        approach = "逐项验证 Q/K/V shape、缩放点积、causal/padding mask、softmax 维度和残差连接；用小张量对照朴素实现，并检查 dtype、device、数值稳定性与缓存一致性。"
    elif "ml coding" in lower or "neural network" in lower or "inference with probability" in lower:
        approach = "先写清张量 shape 和数学公式，再用 NumPy/PyTorch 向量化实现；以有限差分或小型手算样例验证 forward/backward，并覆盖 batch、dtype 与数值稳定性。"
    elif "valid parentheses" in lower:
        approach = "用栈维护未匹配左括号并在遇到右括号时校验类型；若还要检测冗余括号，则在闭合时确认该层是否包含运算符/有效表达式，覆盖空组和嵌套边界。"
    elif "insert interval" in lower:
        approach = "顺序保留完全在新区间左侧的区间，合并所有相交区间，再追加右侧剩余项；明确端点相接是否算重叠，整体 O(n) 时间。"
    elif any(token in lower for token in ("maximize the hits", "count valid sequences", "rice units", "using dp")):
        approach = "先从小规模枚举识别状态与不变量，再设计 DP/记忆化搜索；状态需包含影响未来选择的最小信息，明确转移、边界与取模/不可达值，并用暴力解交叉验证。"
    elif "non-profit to for-profit" in lower:
        approach = "把回答组织成利益相关方、使命约束、融资/治理激励和风险缓解；同时陈述支持与反对证据、可逆决策和需要监控的领先指标，避免只做立场表态。"
    elif "token usage" in lower:
        approach = "先定义输入事件与计费口径，按 request/model/user 聚合 prompt、completion 与 cached tokens；处理重试、流式增量、重复事件和价格版本，并用整数/Decimal 避免金额误差。"
    elif "file profiler" in lower:
        approach = "递归或迭代遍历目录，按大小/类型/修改时间汇总；避免跟随符号链接形成环，流式处理大目录，并讨论权限错误、并发 I/O、哈希抽样和增量更新。"
    elif "debugging" in lower:
        approach = "先用最小输入稳定复现并锁定第一处不变量破坏，再加断言/日志和小步二分定位；修复后补回归、边界、并发和故障注入测试，区分根因与表面症状。"
    elif "python class" in lower:
        approach = "先定义对象职责、公开 API 与数据不变量，选择合适的 dict/list/set/heap 组合；实现 CRUD 后覆盖重复、缺失、排序、可变别名和异常语义，并分析复杂度。"
    else:
        approach = "先从标题澄清输入、输出、约束与失败语义；实现最小正确版本，分析复杂度，再覆盖空输入、重复值、极端规模与并发/持久化等工程边界。"
    return (
        "## 本地准备提纲（非官方逐字题面）\n\n"
        f"官方条目标题：{title}\n\n"
        f"建议准备方向：{approach}\n\n"
        f"请以官方条目核对精确约束和样例：{source_url}"
    )


def enrich(payload: Mapping[str, Any]) -> tuple[dict[str, Any], dict[str, Any]]:
    questions = payload.get("questions")
    if not isinstance(questions, list):
        raise ValueError("questions payload has no questions array")

    generated_kinds = {
        "locally-saved-problem-and-solution",
        "locally-saved-topic-editorial",
        "locally-saved-research-summary",
        "locally-saved-oj-research-summary",
        "locally-saved-public-oj-summary",
        "external-concept-guide",
        "locally-saved-same-problem-prompt-and-hints",
        "locally-saved-public-canonical-body",
        "same-topic-local-preparation-reference",
        "original-structured-preparation-guide",
        "title-derived-preparation-outline",
    }
    generated_relationships = {
        "local-saved-editorial",
        "same-topic-local-editorial",
        "related-variant-editorial",
        "local-research-note",
        "local-practice-solution",
    }
    for row in questions:
        if not isinstance(row, dict) or clean_text(row.get("contentKind")) not in generated_kinds:
            continue
        for key in (
            "content",
            "contentKind",
            "contentMatch",
            "contentMatchConfidence",
            "contentQuality",
            "contentSourceLocalPaths",
            "contentSourceUrls",
            "practiceSolutions",
            "practiceSolutionsVerified",
        ):
            row.pop(key, None)
        sources = row.get("sources")
        if isinstance(sources, list):
            row["sources"] = [
                item
                for item in sources
                if not (
                    isinstance(item, Mapping)
                    and (
                        clean_text(item.get("relationship")) in generated_relationships
                        or clean_text(item.get("generatedBy")) == "oj-original-guide"
                    )
                )
            ]

    previews = qbank_preview_index()
    preview_records = 0
    for row in questions:
        if not isinstance(row, dict) or clean_text(row.get("sourceKind")) != "qbank":
            continue
        preview = previews.get(clean_text(row.get("sourceUrl")))
        if not preview:
            continue
        title = clean_text(preview.get("title"))
        overview = clean_text(preview.get("overview"))
        if title:
            row["title"] = title
        if overview:
            row["overview"] = overview
            row["summary"] = overview
            row["publicPreview"] = overview
            row["publicPreviewTruncated"] = overview.endswith("...")
            preview_records += 1

    sections_by_company: dict[str, dict[str, list[dict[str, Any]]]] = {}
    for company, files in COMPANY_FILES.items():
        sections_by_company[company] = extract_external_sections(
            company,
            files["markdown"],
            files["clean"],
        )

    research_by_id = supplemental_index()
    oj_public_payload = load_json(OJ_PUBLIC_SUMMARIES_PATH)
    oj_public_rows = oj_public_payload.get("records") if isinstance(oj_public_payload, Mapping) else None
    if not isinstance(oj_public_rows, list):
        raise ValueError("OJ public summaries payload has no records array")
    oj_public_by_id = {
        clean_text(row.get("id")): row
        for row in oj_public_rows
        if isinstance(row, Mapping) and clean_text(row.get("id")) and clean_text(row.get("content"))
    }
    original_by_id = original_guide_index()
    canonical_ids = {
        clean_text(row.get("id"))
        for row in questions
        if isinstance(row, Mapping)
        and clean_text(row.get("id"))
    }
    unknown_original_guide_ids = sorted(set(original_by_id) - canonical_ids)
    if unknown_original_guide_ids:
        raise ValueError(
            "original preparation guide ids are not present in the canonical catalog: "
            + ", ".join(unknown_original_guide_ids)
        )
    public_payload = load_json(PUBLIC_BODIES_PATH)
    public_rows = public_payload.get("records") if isinstance(public_payload, Mapping) else None
    if not isinstance(public_rows, list):
        raise ValueError("public qbank body payload has no records array")
    public_by_topic = {
        (clean_text(row.get("company")).lower(), clean_text(row.get("slug"))): row
        for row in public_rows
        if isinstance(row, Mapping)
        and clean_text(row.get("company"))
        and clean_text(row.get("slug"))
        and clean_text(row.get("body"))
    }
    canonical_bodies = 0
    qbank_exact = 0
    qbank_research = 0
    oj_family = 0
    oj_research = 0
    oj_public_summaries = 0
    oj_original_guides = 0
    qbank_original_guides = 0
    original_guides_total = 0
    attached_original_guide_ids: set[str] = set()
    title_outlines = 0
    exact_sections = 0

    # Pass 1: exact-topic editorials extracted from user-owned local Markdown.
    for raw in questions:
        if not isinstance(raw, dict):
            continue
        company = clean_text(raw.get("company")).lower()
        if company not in sections_by_company:
            continue
        source_kind = clean_text(raw.get("sourceKind"))
        if source_kind == "qbank":
            slug = clean_text(raw.get("slug"))
            public_body = public_by_topic.get((company, slug))
            if public_body:
                raw["content"] = clean_text(public_body.get("body"))
                raw["contentKind"] = "locally-saved-public-canonical-body"
                raw["contentMatch"] = "exact-public-canonical-body"
                raw["contentMatchConfidence"] = "high"
                raw["contentQuality"] = "public-canonical-problem-body"
                raw["contentSourceLocalPaths"] = [str(PUBLIC_BODIES_PATH.resolve())]
                raw["contentSourceUrls"] = [clean_text(raw.get("sourceUrl"))]
                canonical_bodies += 1
                qbank_exact += 1
                continue
            sections = sections_by_company[company].get(slug, [])
            if not sections:
                continue
            raw["content"] = build_content(sections)
            raw["contentKind"] = "locally-saved-topic-editorial"
            is_stack_trace_variant = company == "anthropic" and slug == "coding-q3-stack-trace"
            raw["contentMatch"] = (
                "related-stack-trace-variant-not-canonical"
                if is_stack_trace_variant
                else "exact-topic-editorial"
            )
            raw["contentMatchConfidence"] = "medium-high" if is_stack_trace_variant else "high"
            raw["contentQuality"] = editorial_quality(slug, raw["content"])
            raw["contentSourceLocalPaths"] = list(
                dict.fromkeys(clean_text(section.get("localPath")) for section in sections)
            )
            raw["contentSourceUrls"] = list(
                dict.fromkeys(clean_text(section.get("sourceUrl")) for section in sections)
            )
            for section in sections:
                candidate = source_object(section)
                if is_stack_trace_variant:
                    candidate["relationship"] = "related-variant-editorial"
                    candidate["confidence"] = "medium-high"
                    candidate["note"] = (
                        "公开 overview 描述的是 enter/exit 流重建调用栈；本地材料描述的是"
                        "调用栈快照生成 start/end 事件。二者按相关变体展示，不声称是同一题面。"
                    )
                merge_source(raw, candidate)
            qbank_exact += 1
            exact_sections += len(sections)
        elif source_kind.startswith("oj"):
            slug = clean_text(raw.get("relatedQbankSlug")) or oj_topic_slug(
                company, clean_text(raw.get("title"))
            )
            sections = sections_by_company[company].get(slug, [])
            if not sections:
                continue
            raw["content"] = (
                "同题家族准备资料（具体约束与示例请以本条官方 OJ 页面为准）：\n\n"
                + build_content(sections)
            )
            raw["contentKind"] = "same-topic-local-preparation-reference"
            raw["contentMatch"] = "same-topic-not-asserted-exact"
            raw["contentMatchConfidence"] = "medium-high"
            raw["contentQuality"] = "related-family-preparation"
            raw["relatedQbankSlug"] = slug
            raw["contentSourceLocalPaths"] = list(
                dict.fromkeys(clean_text(section.get("localPath")) for section in sections)
            )
            raw["contentSourceUrls"] = list(
                dict.fromkeys(clean_text(section.get("sourceUrl")) for section in sections)
            )
            for section in sections:
                inherited = source_object(section)
                inherited["relationship"] = "same-topic-local-editorial"
                inherited["confidence"] = "medium-high"
                inherited["note"] = "同题家族准备资料；不声称与当前 OJ 的每项约束完全相同。"
                merge_source(raw, inherited)
            oj_family += 1

    # A structured same-problem Bootloader prompt/insight snapshot also exists
    # locally even though its 1p3a external HTML was not saved.
    bootloader_content = bootloader_local_content()
    if bootloader_content:
        for raw in questions:
            if not isinstance(raw, dict):
                continue
            if (
                clean_text(raw.get("company")).lower() == "anthropic"
                and clean_text(raw.get("sourceKind")) == "qbank"
                and clean_text(raw.get("slug")) == "coding-bootloader"
                and not clean_text(raw.get("content"))
            ):
                raw["content"] = bootloader_content
                raw["contentKind"] = "locally-saved-same-problem-prompt-and-hints"
                raw["contentMatch"] = "same-problem-external-not-canonical-body"
                raw["contentMatchConfidence"] = "high"
                raw["contentQuality"] = "problem-and-hints-no-reference-solution"
                raw["contentSourceLocalPaths"] = [str(H2H_FULL_PATH.resolve())]
                raw["contentSourceUrls"] = [
                    "https://www.hack2hire.com/question-bank/companies/anthropic/coding-questions/6a373b2b6849fecc81442861"
                ]
                merge_source(
                    raw,
                    {
                        "url": raw["contentSourceUrls"][0],
                        "title": "本地已保存同题提示 · Repair Bootloader Program",
                        "relationship": "local-saved-editorial",
                        "confidence": "high",
                        "note": "同题外站题面与提示；没有 reference solution，不是 canonical 会员页正文。",
                    },
                )
                qbank_exact += 1
                break

    # Pass 2: curated local research notes for qbank topics that have no saved
    # editorial body.  This keeps reconstructed notes visibly distinct from a
    # locally saved problem/solution page.
    for raw in questions:
        if not isinstance(raw, dict) or clean_text(raw.get("sourceKind")) != "qbank":
            continue
        if clean_text(raw.get("content")):
            continue
        company = clean_text(raw.get("company")).lower()
        slug = clean_text(raw.get("slug"))
        ids = SUPPLEMENTAL_BY_SLUG.get(company, {}).get(slug, [])
        records = [research_by_id[item_id] for item_id in ids if item_id in research_by_id]
        appendix = CUSTOM_QBANK_APPENDIX.get((company, slug), "")
        content = build_research_content(records)
        if appendix:
            content = f"{content}\n\n---\n\n{appendix}" if content else appendix
        if not content:
            continue
        raw["content"] = content
        raw["contentKind"] = "locally-saved-research-summary"
        raw["contentMatch"] = "curated-topic-reconstruction-not-verbatim"
        raw["contentMatchConfidence"] = "medium-high" if records else "medium"
        raw["contentQuality"] = "research-summary-and-solution-hints"
        raw["contentSourceLocalPaths"] = [str(SUPPLEMENTAL_PATH.resolve())]
        if appendix:
            raw["contentSourceLocalPaths"].extend(
                str(path.resolve())
                for path in CUSTOM_QBANK_APPENDIX_PATHS.get((company, slug), [])
            )
        raw["contentSourceUrls"] = list(
            dict.fromkeys(clean_text(record.get("url")) for record in records if clean_text(record.get("url")))
        )
        for record in records:
            candidate = research_source(record)
            if candidate["url"]:
                merge_source(raw, candidate)
        qbank_research += 1

    # Pass 3: OJ rows can reuse a populated qbank topic only as a clearly
    # labelled family reference.  Exact UUID constraints remain on the official
    # OJ URL.
    qbank_by_topic: dict[tuple[str, str], dict[str, Any]] = {
        (clean_text(row.get("company")).lower(), clean_text(row.get("slug"))): row
        for row in questions
        if isinstance(row, dict)
        and clean_text(row.get("sourceKind")) == "qbank"
        and clean_text(row.get("slug"))
        and clean_text(row.get("content"))
    }
    for raw in questions:
        if not isinstance(raw, dict) or not clean_text(raw.get("sourceKind")).startswith("oj"):
            continue
        if clean_text(raw.get("content")):
            continue
        company = clean_text(raw.get("company")).lower()
        slug = clean_text(raw.get("relatedQbankSlug")) or oj_topic_slug(
            company, clean_text(raw.get("title"))
        )
        topic = qbank_by_topic.get((company, slug))
        cross_company_topic = ""
        if (
            not topic
            and company == "anthropic"
            and "infection" in clean_text(raw.get("title")).lower()
        ):
            topic = qbank_by_topic.get(("openai", "infection-spread-cellular-automata"))
            if topic:
                slug = "infection-spread-cellular-automata"
                cross_company_topic = "openai/infection-spread-cellular-automata"
        if (
            not topic
            and company == "openai"
            and any(
                phrase in clean_text(raw.get("title")).lower()
                for phrase in ("duplicate files", "file deduplication")
            )
        ):
            topic = qbank_by_topic.get(("anthropic", "coding-q2-file-deduplication"))
            if topic:
                slug = "coding-q2-file-deduplication"
                cross_company_topic = "anthropic/coding-q2-file-deduplication"
        if not topic:
            continue
        raw["content"] = (
            "同题家族准备资料（不是当前 UUID 页面的逐字题面；精确约束以官方 OJ 为准）：\n\n"
            + clean_text(topic.get("content"))
        )
        raw["contentKind"] = "same-topic-local-preparation-reference"
        raw["contentMatch"] = "related-family-not-exact-oj"
        raw["contentMatchConfidence"] = "medium-high"
        raw["contentQuality"] = "related-family-preparation"
        raw["relatedQbankSlug"] = slug
        if cross_company_topic:
            raw["crossCompanyRelatedTopic"] = cross_company_topic
        raw["contentSourceLocalPaths"] = list(topic.get("contentSourceLocalPaths") or [])
        raw["contentSourceUrls"] = list(topic.get("contentSourceUrls") or [])
        oj_family += 1

    # Pass 4: attach curated local research to a small set of OJ titles that do
    # not have a sufficiently close qbank family.
    for raw in questions:
        if not isinstance(raw, dict) or not clean_text(raw.get("sourceKind")).startswith("oj"):
            continue
        if clean_text(raw.get("content")):
            continue
        ids = OJ_SUPPLEMENTAL_BY_ID.get(clean_text(raw.get("id")), [])
        records = [research_by_id[item_id] for item_id in ids if item_id in research_by_id]
        content = build_research_content(records)
        if not content:
            continue
        raw["content"] = (
            "本地研究重构（不是当前 UUID 页面的逐字题面；精确约束以官方 OJ 为准）：\n\n"
            + content
        )
        raw["contentKind"] = "locally-saved-oj-research-summary"
        raw["contentMatch"] = "curated-title-reconstruction-not-exact-oj"
        raw["contentMatchConfidence"] = "medium"
        raw["contentQuality"] = "research-summary-and-solution-hints"
        raw["contentSourceLocalPaths"] = [str(SUPPLEMENTAL_PATH.resolve())]
        raw["contentSourceUrls"] = list(
            dict.fromkeys(clean_text(record.get("url")) for record in records if clean_text(record.get("url")))
        )
        for record in records:
            candidate = research_source(record)
            candidate["confidence"] = "medium"
            if candidate["url"]:
                merge_source(raw, candidate)
        oj_research += 1

    # Pass 5: public OJ summaries and clearly labelled external concept guides.
    for raw in questions:
        if not isinstance(raw, dict) or not clean_text(raw.get("sourceKind")).startswith("oj"):
            continue
        if clean_text(raw.get("content")):
            continue
        record = oj_public_by_id.get(clean_text(raw.get("id")))
        if not record:
            continue
        match = clean_text(record.get("match"))
        exact_public = match == "exact-public-oj-summary"
        raw["content"] = clean_text(record.get("content"))
        raw["contentKind"] = (
            "locally-saved-public-oj-summary" if exact_public else "external-concept-guide"
        )
        raw["contentMatch"] = match
        raw["contentMatchConfidence"] = clean_text(record.get("confidence")) or "medium"
        raw["contentQuality"] = (
            "public-requirements-summary" if exact_public else "external-concept-preparation-guide"
        )
        raw["contentSourceLocalPaths"] = [str(OJ_PUBLIC_SUMMARIES_PATH.resolve())]
        raw["contentSourceUrls"] = [clean_text(record.get("sourceUrl"))]
        merge_source(
            raw,
            {
                "url": clean_text(record.get("sourceUrl")),
                "title": "公开 OJ 摘要" if exact_public else "外部概念准备资料",
                "relationship": "official-entry" if exact_public else "external-related-guide",
                "confidence": clean_text(record.get("confidence")) or "medium",
                "note": "公开页面的转述摘要；不包含会员区逐字内容。",
            },
        )
        oj_public_summaries += 1

    # Pass 6: attach original, structured preparation guides.  These guides are
    # deliberately labelled non-canonical and never presented as recovered
    # member text.
    for raw in questions:
        if not isinstance(raw, dict):
            continue
        record = original_by_id.get(clean_text(raw.get("id")))
        if not record:
            continue
        previous_kind = clean_text(raw.get("contentKind"))
        if previous_kind == "same-topic-local-preparation-reference":
            oj_family -= 1
        elif previous_kind == "locally-saved-oj-research-summary":
            oj_research -= 1
        elif previous_kind == "locally-saved-research-summary":
            qbank_research -= 1
        sources = raw.get("sources")
        if isinstance(sources, list):
            raw["sources"] = [
                source
                for source in sources
                if not (
                    isinstance(source, Mapping)
                    and (
                        clean_text(source.get("relationship")) in generated_relationships
                        or clean_text(source.get("generatedBy")) == "oj-original-guide"
                    )
                )
            ]
        raw["content"] = clean_text(record.get("content"))
        raw["contentKind"] = "original-structured-preparation-guide"
        raw["contentMatch"] = clean_text(record.get("match")) or "title-based-original-not-canonical"
        raw["contentMatchConfidence"] = clean_text(record.get("confidence")) or "low"
        raw["contentQuality"] = "structured-chinese-problem-and-solution-guide"
        guide_source_urls = [
            clean_text(source.get("url"))
            for source in record.get("sources", [])
            if clean_text(source.get("url"))
        ]
        guide_local_paths: list[str] = []
        guide_external_urls: list[str] = []
        for url in guide_source_urls:
            if re.match(r"^https?://", url, re.IGNORECASE):
                guide_external_urls.append(url)
                continue
            local_path = Path(url).expanduser()
            if not local_path.is_absolute():
                local_path = (PROJECT_ROOT / local_path).resolve()
            if local_path.exists():
                guide_local_paths.append(str(local_path.resolve()))

        raw["contentSourceLocalPaths"] = list(
            dict.fromkeys([str(OJ_ORIGINAL_GUIDES_PATH.resolve()), *guide_local_paths])
        )
        raw["contentSourceUrls"] = list(
            dict.fromkeys(
                url
                for url in [clean_text(raw.get("sourceUrl")), *guide_external_urls]
                if url
            )
        )
        for source in record.get("sources", []):
            url = clean_text(source.get("url"))
            if not re.match(r"^https?://", url, re.IGNORECASE):
                continue
            merge_source(
                raw,
                {
                    "url": url,
                    "title": clean_text(source.get("title")) or "公开相关资料",
                    "relationship": clean_text(source.get("relationship")) or "original-preparation-guide",
                    "confidence": clean_text(source.get("confidence")) or clean_text(record.get("confidence")) or "low",
                    "note": clean_text(source.get("note")) or "用于原创准备指南；不是当前 UUID 的 canonical 题面。",
                    "generatedBy": "oj-original-guide",
                },
            )
        original_guides_total += 1
        if clean_text(raw.get("sourceKind")) == "qbank":
            qbank_original_guides += 1
        else:
            oj_original_guides += 1
        attached_original_guide_ids.add(clean_text(raw.get("id")))

    unattached_original_guide_ids = sorted(set(original_by_id) - attached_original_guide_ids)
    if unattached_original_guide_ids:
        raise ValueError(
            "original preparation guides were not attached to their canonical OJ records: "
            + ", ".join(unattached_original_guide_ids)
        )

    # Pass 7: retain useful preparation content for every locally enumerated
    # record without pretending that a title-derived outline is the missing
    # official body.
    for raw in questions:
        if not isinstance(raw, dict) or clean_text(raw.get("content")):
            continue
        title = clean_text(raw.get("title")) or clean_text(raw.get("slug")) or "未命名条目"
        raw["content"] = title_derived_outline(title, clean_text(raw.get("sourceUrl")))
        raw["contentKind"] = "title-derived-preparation-outline"
        raw["contentMatch"] = "not-exact-source-body"
        raw["contentMatchConfidence"] = "low"
        raw["contentQuality"] = "title-derived-outline-only"
        raw["contentSourceLocalPaths"] = []
        raw["contentSourceUrls"] = [clean_text(raw.get("sourceUrl"))]
        title_outlines += 1

    # Pass 8: link local practice implementations already present in the user's
    # workspace.  A small verified subset has dedicated local unit tests; none
    # of these files is described as an official/reference solution.
    practice_records = 0
    for raw in questions:
        if not isinstance(raw, dict) or clean_text(raw.get("sourceKind")) != "qbank":
            continue
        company = clean_text(raw.get("company")).lower()
        slug = clean_text(raw.get("slug"))
        practice_key = (company, slug)
        relative_paths = LOCAL_PRACTICE_BY_SLUG.get(practice_key, [])
        existing_paths = [path for path in relative_paths if (PROJECT_ROOT / path).exists()]
        if not existing_paths:
            continue
        test_path = LOCAL_PRACTICE_TESTS_BY_SLUG.get(practice_key)
        verified = bool(test_path and (PROJECT_ROOT / test_path).exists())
        raw["practiceSolutions"] = existing_paths
        raw["practiceSolutionsVerified"] = verified
        heading = (
            "### 用户本地练习实现（已通过对应单元测试）"
            if verified
            else "### 用户本地练习实现（仅通过 Python 语法检查，未验证算法正确性）"
        )
        note_lines = [
            heading,
            "",
            *[f"- {path}" for path in existing_paths],
        ]
        if verified:
            note_lines.append(f"- 测试：{test_path}")
        raw["content"] = f"{clean_text(raw.get('content'))}\n\n---\n\n" + "\n".join(note_lines)
        for path in existing_paths:
            verification_note = (
                f"已通过 {test_path}；这是本地练习答案，不是官方答案。"
                if verified
                else "仅通过 Python 语法检查；未验证算法正确性，不是官方答案。"
            )
            merge_source(
                raw,
                {
                    "url": f"./{path}",
                    "title": f"本地练习实现 · {Path(path).name}",
                    "relationship": "local-practice-solution",
                    "confidence": "high" if verified else "unverified",
                    "note": verification_note,
                },
            )
        practice_records += 1

    result = dict(payload)
    result["questions"] = questions
    result["generatedAt"] = datetime.now(timezone.utc).isoformat(timespec="seconds")
    counts = dict(result.get("counts") or {})
    counts.update(
        {
            "recordsWithLocalFulltext": qbank_exact,
            "qbankRecordsWithLocalFulltext": qbank_exact,
            "canonicalSourceBodyRecords": canonical_bodies,
            "qbankDirectTopicContentRecords": qbank_exact - canonical_bodies,
            "qbankRecordsWithLocalResearchContent": qbank_research,
            "ojRecordsWithSameTopicLocalContent": oj_family,
            "ojRecordsWithLocalResearchContent": oj_research,
            "recordsWithTitleDerivedOutline": title_outlines,
            "ojRecordsWithPublicOrExternalSummary": oj_public_summaries,
            "ojRecordsWithOriginalPreparationGuide": oj_original_guides,
            "qbankRecordsWithOriginalPreparationGuide": qbank_original_guides,
            "recordsWithOriginalPreparationGuide": original_guides_total,
            "ojOriginalGuideMarkersLoaded": len(original_by_id),
            "qbankRecordsWithLocalPracticeSolutions": practice_records,
            "localEditorialSectionsUsed": exact_sections,
            "qbankRecordsWithPublicPreview": preview_records,
            "recordsWithAnyContent": sum(
                bool(clean_text(row.get("content"))) for row in questions if isinstance(row, Mapping)
            ),
            "recordsWithoutContent": sum(
                not clean_text(row.get("content")) for row in questions if isinstance(row, Mapping)
            ),
        }
    )
    result["counts"] = counts
    meta = dict(result.get("meta") or {})
    meta["description"] = (
        "Offline canonical catalog plus clearly labelled local public bodies, same-topic editorials, "
        "research reconstructions, original Chinese preparation guides, and fallback preparation outlines."
    )
    meta["recordsWithAnyContent"] = counts["recordsWithAnyContent"]
    meta["canonicalSourceBodyRecords"] = canonical_bodies
    meta["qbankDirectTopicContentRecords"] = qbank_exact - canonical_bodies
    meta["qbankResearchSummaryRecords"] = qbank_research
    meta["ojRecordsWithSameTopicLocalContent"] = oj_family
    meta["ojRecordsWithLocalResearchContent"] = oj_research
    meta["recordsWithTitleDerivedOutline"] = title_outlines
    meta["ojRecordsWithPublicOrExternalSummary"] = oj_public_summaries
    meta["ojRecordsWithOriginalPreparationGuide"] = oj_original_guides
    meta["qbankRecordsWithOriginalPreparationGuide"] = qbank_original_guides
    meta["recordsWithOriginalPreparationGuide"] = original_guides_total
    meta["ojOriginalGuideMarkersLoaded"] = len(original_by_id)
    meta["qbankRecordsWithLocalPracticeSolutions"] = practice_records
    result["meta"] = meta
    provenance = dict(result.get("provenance") or {})
    provenance["localFulltextEnrichment"] = {
        "networkAccessed": False,
        "sourceType": "pre-existing-user-owned-local-markdown",
        "canonicalSourceBodyRecords": canonical_bodies,
        "qbankDirectTopicContentRecords": qbank_exact - canonical_bodies,
        "qbankResearchSummaryRecords": qbank_research,
        "ojRecordsWithSameTopicReference": oj_family,
        "ojResearchSummaryRecords": oj_research,
        "titleDerivedOutlineRecords": title_outlines,
        "ojPublicOrExternalSummaryRecords": oj_public_summaries,
        "ojOriginalPreparationGuideRecords": oj_original_guides,
        "qbankOriginalPreparationGuideRecords": qbank_original_guides,
        "originalPreparationGuideRecords": original_guides_total,
        "ojOriginalGuideMarkersLoaded": len(original_by_id),
        "qbankRecordsWithLocalPracticeSolutions": practice_records,
        "editorialSectionsUsed": exact_sections,
        "qbankPublicPreviewRecords": preview_records,
        "notice": (
            "Exact-topic local editorials, curated research reconstructions, same-topic OJ references, "
            "original Chinese preparation guides, and title-derived outlines are separately labelled. "
            "Only canonical public bodies are treated as saved source text; other classes are preparation material. "
            "None is represented as a bypassed paywalled body."
        ),
    }
    result["provenance"] = provenance
    report = {
        "generatedAt": result["generatedAt"],
        "locallyEnumeratedCanonicalRecords": len(questions),
        "reportedOfficialCatalogRecords": int((result.get("meta") or {}).get("officialReportedRecords") or 0),
        "unidentifiedCatalogRecords": max(
            0,
            int((result.get("meta") or {}).get("officialReportedRecords") or 0) - len(questions),
        ),
        "canonicalSourceBodyRecords": canonical_bodies,
        "qbankDirectTopicContentRecords": qbank_exact - canonical_bodies,
        "qbankResearchSummaryRecords": qbank_research,
        "ojRecordsWithSameTopicReference": oj_family,
        "ojResearchSummaryRecords": oj_research,
        "titleDerivedOutlineRecords": title_outlines,
        "ojPublicOrExternalSummaryRecords": oj_public_summaries,
        "ojOriginalPreparationGuideRecords": oj_original_guides,
        "qbankOriginalPreparationGuideRecords": qbank_original_guides,
        "originalPreparationGuideRecords": original_guides_total,
        "ojOriginalGuideMarkersLoaded": len(original_by_id),
        "qbankRecordsWithLocalPracticeSolutions": practice_records,
        "editorialSectionsUsed": exact_sections,
        "qbankPublicPreviewRecords": preview_records,
        "recordsWithoutContent": counts["recordsWithoutContent"],
        "slugsWithLocalSections": {
            company: sorted(sections) for company, sections in sections_by_company.items()
        },
        "byContentKind": dict(
            sorted(
                Counter(
                    clean_text(row.get("contentKind")) or "none"
                    for row in questions
                    if isinstance(row, Mapping)
                ).items()
            )
        ),
        "limitations": [
            "Only unlocked/public canonical bodies are counted as canonicalSourceBodyRecords.",
            "Local topic editorials and research reconstructions are not represented as verbatim member-only canonical bodies.",
            "OJ related-family content is preparation material, not an exact UUID statement.",
            "Original Chinese guides are evidence-labelled preparation material, not verbatim member-only answers.",
            "Title-derived outlines explicitly indicate that no reliable local statement was available.",
        ],
        "records": [
            {
                "company": clean_text(row.get("company")),
                "id": clean_text(row.get("id")),
                "slug": clean_text(row.get("slug")),
                "title": clean_text(row.get("title")),
                "sourceKind": clean_text(row.get("sourceKind")),
                "contentKind": clean_text(row.get("contentKind")),
                "contentQuality": clean_text(row.get("contentQuality")),
                "contentMatch": clean_text(row.get("contentMatch")),
                "contentMatchConfidence": clean_text(row.get("contentMatchConfidence")),
                "contentLength": len(clean_text(row.get("content"))),
                "officialUrl": clean_text(row.get("sourceUrl")),
                "contentSourceUrls": list(row.get("contentSourceUrls") or []),
                "contentSourceLocalPaths": list(row.get("contentSourceLocalPaths") or []),
                "practiceSolutions": list(row.get("practiceSolutions") or []),
                "practiceSolutionsVerified": row.get("practiceSolutionsVerified"),
            }
            for row in questions
            if isinstance(row, Mapping)
        ],
    }
    return result, report


def write_json_atomic(path: Path, payload: Mapping[str, Any]) -> None:
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
        payload, report = enrich(load_json(args.questions))
        write_json_atomic(args.questions, payload)
        write_json_atomic(args.report, report)
    except (OSError, json.JSONDecodeError, ValueError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    print(
        json.dumps(
            {key: value for key, value in report.items() if key != "records"},
            ensure_ascii=False,
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
