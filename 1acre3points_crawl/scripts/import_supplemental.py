#!/usr/bin/env python3
"""Normalize supplemental OpenAI/Anthropic interview research.

The source file is user-owned and remains read-only.  This importer selects only
OpenAI and Anthropic records, normalizes their shape, conservatively deduplicates
records by company/category/title, and writes a separately labelled data file.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
import unicodedata
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Iterable, List, MutableMapping, Sequence, Tuple


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_INPUT = Path(
    "/Users/mingrui/Documents/codes/interview/"
    "my_interview_prep/new/raw/crawl_all_items.json"
)
DEFAULT_OUTPUT = PROJECT_ROOT / "data" / "supplemental.json"

TARGET_COMPANIES = {"openai", "anthropic"}
SOURCE_TYPE = "supplemental-research"

DISPLAY_TITLE_OVERRIDES = {
    "[目标帖 1179374 已完全旁路] Memory Allocator：75min 店面设计内存分配器（malloc/free + coalescing）": (
        "Memory Allocator：75min 店面设计内存分配器（关联帖 1179374）"
    ),
    "[目标帖 1181416] 2026-06-26 开放爱店面挂经（'回复可见'帖，部分旁路）": (
        "OpenAI 2026-06-26 店面记录（关联帖 1181416，公开信息有限）"
    ),
}

CAPTURE_PREFIX_PATTERNS = (
    (
        re.compile(r"^LOCKED\s*\([^)]*captured[^)]*\)\.\s*", re.I),
        "资料范围：公开预览与可核实要点。\n\n",
    ),
    (
        re.compile(r"^UNLOCKED\s*-\s*.*?captured(?:\s*\([^)]*\))?\.\s*", re.I),
        "资料范围：公开题面或公开解法。\n\n",
    ),
    (
        re.compile(r"^FULL article captured\.\s*", re.I),
        "资料范围：公开文章摘要。\n\n",
    ),
)

STACK_TRACE_TITLE = "Anthropic SDE 编码真题（近3个月高频）：从调用栈快照重建函数 start/end 事件"

READABILITY_OVERRIDES: Dict[str, Dict[str, Any]] = {
    STACK_TRACE_TITLE: {
        "frequency": "高频（2 个独立来源，近 3 个月）",
        "tags": ["coding", "stack", "simulation", "parsing"],
        "roles": ["swe"],
        "summary": (
            "根据周期性调用栈快照，按时间生成函数 start/end 事件。"
            "核心是比较相邻调用栈的最长公共前缀。"
        ),
        "detail": """\
## 题目说明

给定一组按时间排序的调用栈快照。你需要比较相邻快照，重建函数的开始（`start`）和结束（`end`）事件。

> 题目来源说明：OfferEngineering 于 2026-07 收录；InterviewCoderHQ 也独立提到过“把 profiler 的调用栈快照转换为函数开始/结束事件”。

## 输入格式

每条快照的格式为：

```text
<timestamp>:<callPath>
```

- `timestamp` 严格递增。
- `callPath` 按“外层函数 → 内层函数”排列，例如 `app->load->parse`。
- 空路径表示当时没有函数正在运行，例如 `6:`。
- 递归调用中的同名函数要按不同栈帧处理。

## 事件生成规则

比较前后两次快照的调用栈：

1. 两个栈的共同前缀表示仍在运行的函数，不生成事件。
2. 旧栈中从共同前缀之后消失的函数生成 `end` 事件，顺序为“从最内层到最外层”。
3. 新栈中从共同前缀之后出现的函数生成 `start` 事件，顺序为“从最外层到最内层”。
4. 第一条快照中的所有函数都生成 `start` 事件。
5. 处理完最后一条快照后，不要自动结束仍然活跃的函数。

## 函数签名

```java
List<String> buildEvents(List<String> snapshots)
```

事件格式：

```text
start:<time>:<function>
end:<time>:<function>
```

## 示例

输入：

```text
["1:app->load", "3:app->load->parse", "5:app->load", "8:app"]
```

输出：

```text
["start:1:app", "start:1:load", "start:3:parse", "end:5:parse", "end:8:load"]
```

过程解释：

- `t=1`：`app` 和 `load` 第一次出现，因此依次开始。
- `t=3`：共同前缀是 `app->load`，只有 `parse` 是新函数。
- `t=5`：`parse` 消失，因此结束。
- `t=8`：`load` 消失，因此结束；`app` 仍活跃，不产生 `end`。""",
        "solutionHint": """\
## 解题思路

对每一对相邻调用栈，求它们的最长公共前缀长度 `common`：

1. 将旧栈中下标 `[common, oldSize)` 的栈帧逆序输出为 `end`。
2. 将新栈中下标 `[common, newSize)` 的栈帧正序输出为 `start`。
3. 用新栈替换旧栈，继续处理下一条快照。

按“位置”比较栈帧，所以递归调用即使函数名相同，也仍然是不同深度的独立栈帧。

## Java 参考实现

```java
import java.util.ArrayList;
import java.util.Arrays;
import java.util.Collections;
import java.util.List;

public class StackSnapshotEvents {
    public static List<String> buildEvents(List<String> snapshots) {
        List<String> events = new ArrayList<>();
        List<String> previous = Collections.emptyList();

        for (String snapshot : snapshots) {
            int separator = snapshot.indexOf(':');
            if (separator < 0) {
                throw new IllegalArgumentException("Invalid snapshot: " + snapshot);
            }

            String time = snapshot.substring(0, separator);
            String path = snapshot.substring(separator + 1);
            List<String> current = path.isEmpty()
                    ? Collections.emptyList()
                    : Arrays.asList(path.split("->"));

            int common = 0;
            while (common < previous.size()
                    && common < current.size()
                    && previous.get(common).equals(current.get(common))) {
                common++;
            }

            // 先结束旧栈中消失的函数：最内层 -> 最外层。
            for (int i = previous.size() - 1; i >= common; i--) {
                events.add("end:" + time + ":" + previous.get(i));
            }

            // 再开始新栈中出现的函数：最外层 -> 最内层。
            for (int i = common; i < current.size(); i++) {
                events.add("start:" + time + ":" + current.get(i));
            }

            previous = new ArrayList<>(current);
        }

        // 不在结尾补 end；题目要求保留最后仍活跃的函数。
        return events;
    }
}
```

## 复杂度

- 时间复杂度：`O(F)`，其中 `F` 是所有快照中参与比较和事件生成的栈帧总数。
- 额外空间：`O(D)`，其中 `D` 是最大调用栈深度；不计输出数组。

## 建议补充测试

- 第一条快照为空。
- 相邻两条快照完全相同，不应生成事件。
- 新快照变为空路径，需要按“内到外”结束全部旧栈帧。
- 出现递归调用，例如 `app->work->work`。
- 最后一条快照仍有函数运行，不应补结束事件。""",
    }
}

SPACE_RE = re.compile(r"[\t\v\f \u00a0]+")
BLANK_LINES_RE = re.compile(r"\n{3,}")
TITLE_KEY_RE = re.compile(r"[^\w\u3400-\u9fff]+", re.UNICODE)

CATEGORY_TAGS = {
    "behavioral": "behavioral",
    "coding": "coding",
    "ml_coding": "ml-coding",
    "ml_system_design": "ml-system-design",
    "ml_theory": "ml-theory",
    "process": "process",
    "system_design": "system-design",
}

# Ordered from specific signals to broader ones.  The category tag is always
# first, then at most seven of these rules are used.
TAG_RULES = (
    ("online-assessment", re.compile(r"\b(?:oa|codesignal)\b|online assessment|在线测评", re.I)),
    ("take-home", re.compile(r"take[ -]?home(?: assignment)?|home assignment|带回家|限时作业", re.I)),
    ("culture-values", re.compile(r"culture(?: fit| interview| round|/values)?|values (?:interview|round)|文化(?:面|轮)|价值观", re.I)),
    ("reference-check", re.compile(r"reference check|背调|推荐人", re.I)),
    ("hiring-committee", re.compile(r"hiring committee|招聘委员会", re.I)),
    ("agentic-ai", re.compile(r"agentic|agent loop|build an agent|ai agent|claude code|智能体", re.I)),
    ("rlhf", re.compile(r"\b(?:rlhf|ppo|dpo|grpo)\b|reinforcement learning|强化学习", re.I)),
    ("transformer", re.compile(r"transformer|\battention\b|\bmha\b|注意力", re.I)),
    ("prompt-engineering", re.compile(r"\bprompts?\b|\bprompting\b|提示词|提示工程", re.I)),
    ("rag-retrieval", re.compile(r"\brag\b|retriev|vector (?:db|database)|向量数据库|检索", re.I)),
    ("tokenization", re.compile(r"tokeni[sz](?:er|ation)|分词", re.I)),
    ("web-crawler", re.compile(r"web crawl|crawler|crawling|爬虫", re.I)),
    ("deduplication", re.compile(r"dedup|duplicate files?|重复文件|文件去重", re.I)),
    ("caching", re.compile(r"\bcach(?:e|ing)\b|memoization|缓存", re.I)),
    ("persistence", re.compile(r"persistent|durable|checkpoint|\bwal\b|backup.?restore|持久化|检查点|备份.?恢复", re.I)),
    ("key-value-store", re.compile(r"key[ -]?value|\bkv(?: store)?\b|键值", re.I)),
    ("database", re.compile(r"\bdatabase\b|\bsql\b|in-memory db|数据库", re.I)),
    ("concurrency", re.compile(r"concurren|multi[ -]?thread|thread[ -]?safe|race condition|并发|多线程|线程安全|竞态", re.I)),
    ("distributed-systems", re.compile(r"distributed|\bcluster\b|\bp2p\b|shard|分布式|集群|分片", re.I)),
    ("gpu", re.compile(r"\bgpu\b|\bcuda\b|显存", re.I)),
    ("inference-serving", re.compile(r"inference|model serving|token generation|推理服务|模型服务", re.I)),
    ("batching", re.compile(r"\bbatch(?:es|ing|er)?\b|dynamic batch|批处理|批次", re.I)),
    ("scheduling", re.compile(r"schedul|task assignment|job queue|调度", re.I)),
    ("streaming", re.compile(r"\bstream(?:ing)?\b|\bsse\b|online algorithm|流式|在线算法", re.I)),
    ("graph", re.compile(r"social graph|follow graph|graph algorithm|\b(?:bfs|dfs)\b|图算法|关注图|拓扑图", re.I)),
    ("trie", re.compile(r"\btrie\b|前缀树", re.I)),
    ("dynamic-programming", re.compile(r"dynamic programming|\bdp\b|动态规划", re.I)),
    ("binary-search", re.compile(r"binary search|二分", re.I)),
    ("api-design", re.compile(r"\bapi\b|接口设计", re.I)),
    ("rate-limiting", re.compile(r"rate limit|限流", re.I)),
    ("payments", re.compile(r"payment|支付", re.I)),
    ("games", re.compile(r"\bchess\b|\bgame\b|battle simulation|象棋|游戏|打怪", re.I)),
    ("memory-management", re.compile(r"memory alloc|\bmalloc\b|\bfree blocks?\b|内存分配|内存管理", re.I)),
    ("debugging", re.compile(r"\bdebug|bug hunt|抓虫|调试", re.I)),
    ("data-labeling", re.compile(r"data label|annotat|标注数据|数据标注", re.I)),
    ("probability-statistics", re.compile(r"entropy|probabilit|statistics|\bbayes|随机数|概率|统计|熵", re.I)),
    ("backpropagation", re.compile(r"backprop|autograd|gradient|反向传播|梯度", re.I)),
    ("file-systems", re.compile(r"file system|filesystem|file directory|文件系统|文件目录", re.I)),
    ("serialization", re.compile(r"seriali[sz]|反序列化|序列化", re.I)),
    ("networking", re.compile(r"\bdns\b|\bcidr\b|ip address|network protocol|网络协议", re.I)),
    ("frontend", re.compile(r"front[ -]?end|\breact\b|chat ui|前端|流式聊天 ui", re.I)),
    ("mobile", re.compile(r"\bios\b|\bandroid\b|mobile|移动端", re.I)),
    ("llm", re.compile(r"\bllm\b|large language model|\bchatgpt\b|\bgpt[- ]?\d*\b|\bclaude\b|大语言模型", re.I)),
)

# Roles are intentionally inferred from the title only.  A role mentioned deep
# in a comparison or follow-up should not make the whole record look role-specific.
ROLE_RULES = (
    ("swe", re.compile(r"\bswe\b|software engineer|软件工程师", re.I)),
    ("mle", re.compile(r"\bmle\b|machine learning engineer|机器学习工程师", re.I)),
    ("re", re.compile(r"\bre\b|research engineer|研究工程师", re.I)),
    ("rs", re.compile(r"\brs\b|research scientist|研究科学家", re.I)),
    ("data-scientist", re.compile(r"data scientist|数据科学家", re.I)),
    ("frontend", re.compile(r"front[ -]?end|前端", re.I)),
    ("mobile", re.compile(r"\bios\b|\bandroid\b|mobile|移动端", re.I)),
    ("infra", re.compile(r"\binfra(?:structure)?\b|基础设施", re.I)),
    ("applied-ai", re.compile(r"applied ai|\bfde\b|forward deployed", re.I)),
    ("product-engineer", re.compile(r"product engineer", re.I)),
    ("fellowship", re.compile(r"research fellow|fellowship|\bmats\b", re.I)),
)


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--input",
        type=Path,
        default=DEFAULT_INPUT,
        help=f"source crawl JSON (default: {DEFAULT_INPUT})",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=DEFAULT_OUTPUT,
        help=f"normalized supplemental JSON (default: {DEFAULT_OUTPUT})",
    )
    return parser.parse_args(argv)


def normalize_text(value: Any) -> str:
    """Return stable, readable Unicode text without changing its meaning."""
    if value is None:
        return ""
    # NFC keeps Chinese full-width punctuation readable.  NFKC used here in
    # the past collapsed `，。：（）` into ASCII punctuation and made long
    # Chinese notes look cramped.  Identity keys still use NFKC in title_key().
    text = unicodedata.normalize("NFC", str(value))
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    lines: List[str] = []
    in_code_fence = False
    for line in text.split("\n"):
        stripped = line.strip()
        if stripped.startswith("```"):
            lines.append(stripped)
            in_code_fence = not in_code_fence
        elif in_code_fence:
            lines.append(line.rstrip())
        else:
            lines.append(SPACE_RE.sub(" ", line).strip())
    return BLANK_LINES_RE.sub("\n\n", "\n".join(lines)).strip()


def clean_capture_artifacts(value: Any) -> str:
    """Remove importer-state wording and exact temporary paths from display text."""
    text = normalize_text(value)
    for pattern, replacement in CAPTURE_PREFIX_PATTERNS:
        text = pattern.sub(replacement, text, count=1)
    text = re.sub(
        r"\s*\((?:Python in|saved at)\s*/tmp/h2h_[^)]+\)",
        "",
        text,
        flags=re.I,
    )
    text = re.sub(
        r"^Official editorial \(captured\):\s*",
        "公开题解思路：",
        text,
        flags=re.I,
    )
    text = re.sub(r"/tmp/h2h_[\w.-]+", "本地研究快照", text)
    return BLANK_LINES_RE.sub("\n\n", text).strip()


def normalize_company(value: Any) -> str:
    return normalize_text(value).casefold().replace(" ", "")


def normalize_category(value: Any) -> str:
    category = normalize_text(value).casefold().replace("-", "_").replace(" ", "_")
    return re.sub(r"_+", "_", category).strip("_") or "uncategorized"


def normalize_source_url(value: Any) -> str:
    """Trim surrounding whitespace while preserving the source URL verbatim."""
    if value is None:
        return ""
    url = str(value).strip()
    return url


def title_key(title: str) -> str:
    normalized = unicodedata.normalize("NFKC", title).casefold()
    return TITLE_KEY_RE.sub("", normalized)


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for chunk in iter(lambda: source.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def stable_id(company: str, category: str, normalized_title: str) -> str:
    identity = "\x1f".join((company, category, normalized_title)).encode("utf-8")
    suffix = hashlib.sha256(identity).hexdigest()[:16]
    return f"supp-{company}-{suffix}"


def unique_nonempty(values: Iterable[str]) -> List[str]:
    seen = set()
    result = []
    for value in values:
        if value and value not in seen:
            seen.add(value)
            result.append(value)
    return result


def summarize_detail(detail: str, max_chars: int = 240) -> str:
    """Use the first paragraph, shortened at a readable boundary when needed."""
    paragraphs = [part for part in re.split(r"\n\s*\n", detail) if part.strip()]
    paragraph = paragraphs[0] if paragraphs else ""
    if paragraph.startswith("资料范围：") and len(paragraphs) > 1:
        paragraph = paragraphs[1]
    paragraph = SPACE_RE.sub(" ", paragraph.replace("\n", " ")).strip()
    if len(paragraph) <= max_chars:
        return paragraph

    prefix = paragraph[: max_chars - 1]
    boundary = max(prefix.rfind(mark) + len(mark) for mark in ("。", "!", "！", "?", "？", ";", "；"))
    if boundary >= int(max_chars * 0.65):
        prefix = prefix[:boundary]
    return prefix.rstrip(" ,，:：;；") + "…"


def infer_tags(category: str, title: str, detail: str, solution_hint: str) -> List[str]:
    generic = CATEGORY_TAGS.get(category, category.replace("_", "-"))
    tags = [generic]
    searchable = "\n".join((title, detail, solution_hint))
    for tag, pattern in TAG_RULES:
        if tag not in tags and pattern.search(searchable):
            tags.append(tag)
            if len(tags) == 8:
                break
    return tags


def infer_roles(title: str) -> List[str]:
    return [role for role, pattern in ROLE_RULES if pattern.search(title)]


def enrich_record(record: Dict[str, Any]) -> None:
    record["access"] = "link-only"
    record["status"] = "research"
    record["tags"] = infer_tags(
        record["category"], record["title"], record["detail"], record["solutionHint"]
    )
    record["roles"] = infer_roles(record["title"])
    record["summary"] = summarize_detail(record["detail"])


def merge_text(existing: str, incoming: str) -> str:
    """Merge distinct descriptions without losing either source's information."""
    if not incoming or incoming == existing:
        return existing
    if not existing:
        return incoming
    if incoming in existing:
        return existing
    if existing in incoming:
        return incoming
    return f"{existing}\n\n---\n\n{incoming}"


def choose_specific(existing: str, incoming: str) -> str:
    """Prefer a populated, more descriptive scalar during duplicate merges."""
    generic = {"", "unknown", "n/a", "none", "null"}
    existing_generic = existing.casefold() in generic
    incoming_generic = incoming.casefold() in generic
    if existing_generic and not incoming_generic:
        return incoming
    if incoming_generic:
        return existing
    return incoming if len(incoming) > len(existing) else existing


def normalize_record(raw: MutableMapping[str, Any], source_index: int) -> Dict[str, Any]:
    company = normalize_company(raw.get("company"))
    category = normalize_category(raw.get("category"))
    title = normalize_text(raw.get("title"))
    if not title:
        raise ValueError(f"record {source_index} has no title")

    source_url = normalize_source_url(raw.get("url"))
    normalized_title = title_key(title)
    if not normalized_title:
        raise ValueError(f"record {source_index} has no usable title key")

    return {
        "id": stable_id(company, category, normalized_title),
        "company": company,
        "category": category,
        "title": DISPLAY_TITLE_OVERRIDES.get(title, title),
        "detail": clean_capture_artifacts(raw.get("detail")),
        "difficulty": normalize_text(raw.get("difficulty")) or "unknown",
        "frequency": normalize_text(raw.get("frequency")) or "unknown",
        "date": normalize_text(raw.get("date")),
        "url": source_url,
        "sourceUrls": [source_url] if source_url else [],
        "solutionHint": clean_capture_artifacts(raw.get("solution_hint")),
        "sourceType": SOURCE_TYPE,
        "contentKind": "supplemental-research-note",
        "contentMatch": "supplemental-research-not-canonical",
        "contentMatchConfidence": "unverified",
        "contentQuality": "supplemental-research-note",
        "officialSnapshot": False,
        "sourceRecordIndexes": [source_index],
        "mergedRecordCount": 1,
        "_dedupeKey": (company, category, normalized_title),
    }


def merge_record(existing: Dict[str, Any], incoming: Dict[str, Any]) -> None:
    existing["detail"] = merge_text(existing["detail"], incoming["detail"])
    existing["solutionHint"] = merge_text(
        existing["solutionHint"], incoming["solutionHint"]
    )
    for field in ("difficulty", "frequency", "date"):
        existing[field] = choose_specific(existing[field], incoming[field])

    existing["sourceUrls"] = unique_nonempty(
        [*existing["sourceUrls"], *incoming["sourceUrls"]]
    )
    if not existing["url"] and incoming["url"]:
        existing["url"] = incoming["url"]
    existing["sourceRecordIndexes"].extend(incoming["sourceRecordIndexes"])
    existing["sourceRecordIndexes"] = sorted(set(existing["sourceRecordIndexes"]))
    existing["mergedRecordCount"] += incoming["mergedRecordCount"]


def count_by(records: Sequence[Dict[str, Any]], field: str) -> Dict[str, int]:
    return dict(sorted(Counter(record[field] for record in records).items()))


def build_payload(source_path: Path, source_data: Dict[str, Any]) -> Dict[str, Any]:
    raw_items = source_data.get("items")
    if not isinstance(raw_items, list):
        raise ValueError("source JSON must contain an 'items' array")

    selected: List[Tuple[int, MutableMapping[str, Any]]] = []
    excluded_companies: Counter[str] = Counter()
    for index, raw in enumerate(raw_items):
        if not isinstance(raw, MutableMapping):
            raise ValueError(f"record {index} is not an object")
        company = normalize_company(raw.get("company"))
        if company in TARGET_COMPANIES:
            selected.append((index, raw))
        else:
            excluded_companies[company or "(missing)"] += 1

    deduplicated: Dict[Tuple[str, str, str], Dict[str, Any]] = {}
    for source_index, raw in selected:
        record = normalize_record(raw, source_index)
        key = record.pop("_dedupeKey")
        if key in deduplicated:
            merge_record(deduplicated[key], record)
        else:
            deduplicated[key] = record

    questions = list(deduplicated.values())
    for question in questions:
        override = READABILITY_OVERRIDES.get(question["title"])
        if override:
            question["detail"] = normalize_text(override.get("detail"))
            question["solutionHint"] = normalize_text(override.get("solutionHint"))
            if normalize_text(override.get("frequency")):
                question["frequency"] = normalize_text(override.get("frequency"))
            question["readabilityEdited"] = True
        enrich_record(question)
        if override:
            if normalize_text(override.get("summary")):
                question["summary"] = normalize_text(override.get("summary"))
            if isinstance(override.get("tags"), list):
                question["tags"] = unique_nonempty(
                    [normalize_text(value) for value in override["tags"]]
                )
            if isinstance(override.get("roles"), list):
                question["roles"] = unique_nonempty(
                    [normalize_text(value) for value in override["roles"]]
                )
    questions.sort(
        key=lambda item: (item["company"], item["category"], item["title"].casefold()),
    )
    unique_source_urls = {
        url for question in questions for url in question.get("sourceUrls", []) if url
    }
    source_summaries = source_data.get("sources", [])
    if not isinstance(source_summaries, list):
        source_summaries = []

    selected_count = len(selected)
    output_count = len(questions)
    unique_tags = sorted({tag for question in questions for tag in question["tags"]})
    enrichment_counts = {
        "recordsWithTags": sum(bool(question["tags"]) for question in questions),
        "recordsWithTopicTags": sum(len(question["tags"]) > 1 for question in questions),
        "recordsWithRoles": sum(bool(question["roles"]) for question in questions),
        "recordsWithSummary": sum(bool(question["summary"]) for question in questions),
        "tagAssignments": sum(len(question["tags"]) for question in questions),
        "uniqueTags": len(unique_tags),
    }
    return {
        "schemaVersion": 2,
        "generatedAt": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "provenance": {
            "sourceType": SOURCE_TYPE,
            "officialSnapshot": False,
            "notice": (
                "User-owned, pre-existing supplemental research compilation; "
                "not an official per-question snapshot of the 1point3acres catalog."
            ),
            "inputFile": str(source_path.resolve()),
            "inputSha256": sha256_file(source_path),
            "sourceCrawlDate": normalize_text(source_data.get("crawl_date")),
            "sourceSummaryCount": len(source_summaries),
            "selection": "company is OpenAI or Anthropic (case-insensitive)",
            "deduplication": (
                "exact normalized company + category + NFKC/case-folded title key; "
                "merged records retain every distinct source URL"
            ),
            "enrichment": (
                "tags are conservative dictionary matches over title/detail/solutionHint; "
                "roles are inferred only from explicit title terms; summaries are derived "
                "from the first detail paragraph"
            ),
        },
        "counts": {
            "inputRecords": len(raw_items),
            "selectedRecords": selected_count,
            "excludedRecords": len(raw_items) - selected_count,
            "outputRecords": output_count,
            "duplicatesMerged": selected_count - output_count,
            "uniqueSourceUrls": len(unique_source_urls),
            "byCompany": count_by(questions, "company"),
            "byCategory": count_by(questions, "category"),
            "excludedByCompany": dict(sorted(excluded_companies.items())),
            "enrichment": enrichment_counts,
        },
        "questions": questions,
    }


def main(argv: Sequence[str] | None = None) -> int:
    args = parse_args(argv)
    source_path = args.input.expanduser().resolve()
    output_path = args.output.expanduser().resolve()

    try:
        with source_path.open("r", encoding="utf-8") as source:
            source_data = json.load(source)
        if not isinstance(source_data, dict):
            raise ValueError("source JSON root must be an object")
        payload = build_payload(source_path, source_data)
    except (OSError, json.JSONDecodeError, ValueError) as error:
        print(f"import_supplemental: {error}", file=sys.stderr)
        return 1

    output_path.parent.mkdir(parents=True, exist_ok=True)
    temporary_path = output_path.with_suffix(f"{output_path.suffix}.tmp")
    with temporary_path.open("w", encoding="utf-8") as output:
        json.dump(payload, output, ensure_ascii=False, indent=2)
        output.write("\n")
    temporary_path.replace(output_path)

    counts = payload["counts"]
    print(
        f"Wrote {counts['outputRecords']} records to {output_path} "
        f"({counts['duplicatesMerged']} duplicates merged)."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
