#!/usr/bin/env python3
"""Build a searchable, file-complete index of my_interview_prep.

The output groups physical files into useful reading units (document sections,
Deep-ML bundles, saved forum pages, code exercises, and raw datasets) while a
manifest proves which physical files were accounted for.
"""

from __future__ import annotations

import hashlib
import html
import json
import re
from collections import Counter, defaultdict
from datetime import datetime, timezone
from html.parser import HTMLParser
from pathlib import Path
from typing import Any


PROJECT_ROOT = Path(__file__).resolve().parents[1]
WORKSPACE_ROOT = PROJECT_ROOT.parent
PREP_ROOT = WORKSPACE_ROOT / "my_interview_prep"
OUTPUT = PROJECT_ROOT / "data" / "local_materials.json"
LINKS_OUTPUT = PROJECT_ROOT / "data" / "local_material_links.json"
QUESTIONS_FILE = PROJECT_ROOT / "data" / "questions.json"

TEXT_LIMIT = 16_000
IGNORED_NAMES = {".DS_Store"}
TOKEN_STOP = {
    "the", "and", "for", "with", "from", "into", "using", "use", "build",
    "design", "implement", "implementation", "question", "problem", "round",
    "interview", "openai", "anthropic", "coding", "system", "part", "guide",
    "solution", "solutions", "notes", "题目", "问题", "实现", "设计", "面试",
}
KIND_ORDER = {
    "一亩三分地整理": 0,
    "一亩三分地本地原帖": 1,
    "公司笔记": 2,
    "公司编程练习": 3,
    "手写训练": 4,
    "题库汇编": 5,
    "冲刺资料": 6,
    "Deep-ML 练习": 7,
    "报告与计划": 8,
    "原始数据": 9,
    "旧版本地工具": 10,
    "其他资料": 11,
}


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace")


def clean_heading(value: str) -> str:
    value = re.sub(r"[`*_#]+", "", value)
    value = re.sub(r"\s+", " ", value).strip(" -|:：")
    return value or "未命名章节"


def stable_id(*parts: str) -> str:
    digest = hashlib.sha1("\x1f".join(parts).encode("utf-8")).hexdigest()[:16]
    return f"material-{digest}"


def relative(path: Path) -> str:
    return path.resolve().relative_to(PREP_ROOT.resolve()).as_posix()


def infer_company(path: Path, title: str = "") -> str:
    text = f"{relative(path).lower()} {title.lower()}"
    has_openai = "openai" in text
    has_anthropic = "anthropic" in text
    if has_openai and not has_anthropic:
        return "openai"
    if has_anthropic and not has_openai:
        return "anthropic"
    if "gdm" in text or "deepmind" in text:
        return "gdm"
    return "all"


def classify(path: Path) -> str:
    rel = relative(path)
    if rel.startswith("new/deepml-problems/"):
        return "Deep-ML 练习"
    if rel.startswith("new/raw/1p3a_html/"):
        return "一亩三分地本地原帖"
    if rel.startswith("new/raw/"):
        return "原始数据"
    if rel.startswith("02_coding_practice/"):
        return "公司编程练习"
    if rel.startswith("new/drills/"):
        return "手写训练"
    if rel.startswith("01_company_notes/"):
        return "公司笔记"
    if rel.startswith("00_reports_and_plans/"):
        return "报告与计划"
    if "/question-bank/" in f"/{rel}":
        return "题库汇编"
    if path.name.startswith("1p3a-"):
        return "一亩三分地整理"
    if rel.startswith("new/interactive_1p3acre/"):
        return "旧版本地工具"
    if rel.startswith("new/") and path.suffix == ".md":
        return "冲刺资料"
    return "其他资料"


def excerpt(value: str, limit: int = TEXT_LIMIT) -> str:
    value = value.replace("\x00", "").strip()
    if len(value) <= limit:
        return value
    return value[:limit].rstrip() + "\n\n…（本地索引已截断；完整内容请打开源文件。）"


def summary_from(value: str, limit: int = 320) -> str:
    value = re.sub(r"```[\s\S]*?```", " ", value)
    value = re.sub(r"^\s*#{1,6}\s+", "", value, flags=re.MULTILINE)
    value = re.sub(r"[*_`>|]", "", value)
    value = re.sub(r"\s+", " ", value).strip()
    return value if len(value) <= limit else value[:limit].rstrip() + "…"


def clean_markdown_artifacts(value: str) -> str:
    """Drop one-line stylesheet/script leaks without changing source line numbers."""
    kept: list[str] = []
    for line in value.splitlines():
        stripped = line.strip()
        if line.count("--tw-") >= 8 or ("@keyframes" in line and "{" in line):
            continue
        if len(line) > 8_000 and ("{display:" in line or "window.__" in line):
            continue
        kept.append(line)
    return "\n".join(kept).strip()


def tokens(value: str) -> set[str]:
    value = value.lower()
    words = {
        word for word in re.findall(r"[a-z0-9][a-z0-9+._-]{2,}", value)
        if word not in TOKEN_STOP and not word.isdigit()
    }
    for chunk in re.findall(r"[\u3400-\u9fff]{2,}", value):
        words.update(chunk[index:index + 2] for index in range(len(chunk) - 1))
    return words


class VisibleHTML(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.hidden = 0
        self.parts: list[str] = []
        self.title_parts: list[str] = []
        self.in_title = False

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag in {"script", "style", "noscript", "svg"}:
            self.hidden += 1
        if tag == "title":
            self.in_title = True
        if tag in {"p", "div", "li", "br", "h1", "h2", "h3", "tr"} and not self.hidden:
            self.parts.append("\n")

    def handle_endtag(self, tag: str) -> None:
        if tag in {"script", "style", "noscript", "svg"} and self.hidden:
            self.hidden -= 1
        if tag == "title":
            self.in_title = False

    def handle_data(self, data: str) -> None:
        if self.hidden:
            return
        if self.in_title:
            self.title_parts.append(data)
        self.parts.append(data)

    @property
    def text(self) -> str:
        value = html.unescape(" ".join(self.parts))
        value = re.sub(r"[ \t]+", " ", value)
        value = re.sub(r"\n\s*\n+", "\n\n", value)
        return value.strip()

    @property
    def title(self) -> str:
        return clean_heading(" ".join(self.title_parts))


materials: list[dict[str, Any]] = []
covered_by_file: dict[str, set[str]] = defaultdict(set)


def add_material(
    *,
    title: str,
    kind: str,
    source_files: list[Path],
    content: str = "",
    summary: str = "",
    company: str = "all",
    line_start: int | None = None,
    line_end: int | None = None,
    source_url: str = "",
    tags: list[str] | None = None,
) -> None:
    existing_files = [path for path in source_files if path.exists()]
    if not existing_files:
        return
    rels = [relative(path) for path in existing_files]
    identity = f"{rels[0]}:{line_start or 0}:{title}"
    material_id = stable_id(identity)
    content = excerpt(content)
    row = {
        "id": material_id,
        "title": clean_heading(title),
        "kind": kind,
        "company": company,
        "summary": summary or summary_from(content),
        "content": content,
        "sourceFiles": rels,
        "absoluteSourcePaths": [str(path.resolve()) for path in existing_files],
        "lineStart": line_start,
        "lineEnd": line_end,
        "sourceUrl": source_url,
        "tags": sorted(set(tags or [])),
        "relatedQuestions": [],
    }
    materials.append(row)
    for rel in rels:
        covered_by_file[rel].add(material_id)


def index_markdown(path: Path) -> None:
    lines = read_text(path).splitlines()
    headings: list[tuple[int, int, str]] = []
    for index, line in enumerate(lines):
        match = re.match(r"^(#{1,3})\s+(.+?)\s*$", line)
        if match:
            headings.append((index, len(match.group(1)), clean_heading(match.group(2))))

    if not headings:
        content = "\n".join(lines)
        add_material(
            title=path.stem.replace("_", " "),
            kind=classify(path),
            source_files=[path],
            content=content,
            company=infer_company(path),
            line_start=1,
            line_end=len(lines),
        )
        return

    selected = [heading for heading in headings if heading[1] in {2, 3}]
    if not selected:
        selected = [headings[0]]
    for selected_index, (start, level, title) in enumerate(selected):
        end = len(lines)
        for candidate_start, candidate_level, _ in headings:
            if candidate_start > start and candidate_level <= level:
                end = candidate_start
                break
        body = clean_markdown_artifacts("\n".join(lines[start:end]))
        if len(summary_from(body)) < 30:
            continue
        add_material(
            title=title,
            kind=classify(path),
            source_files=[path],
            content=body,
            company=infer_company(path, title),
            line_start=start + 1,
            line_end=end,
        )


def index_deepml() -> None:
    root = PREP_ROOT / "new" / "deepml-problems" / "questions"
    for folder in sorted(path for path in root.iterdir() if path.is_dir()):
        files = sorted(path for path in folder.rglob("*") if path.is_file())
        meta_path = folder / "meta.json"
        meta: dict[str, Any] = {}
        if meta_path.exists():
            try:
                meta = json.loads(read_text(meta_path))
            except json.JSONDecodeError:
                pass
        title = str(meta.get("title") or folder.name.replace("_", " "))
        chunks = []
        for name in ["description.md", "learn.md", "starter_code.py", "solution.py"]:
            candidate = folder / name
            if candidate.exists():
                chunks.append(f"## {name}\n\n{read_text(candidate)}")
        source_url = ""
        problem_id = meta.get("id")
        if problem_id is not None:
            source_url = f"https://www.deep-ml.com/problems/{problem_id}"
        add_material(
            title=title,
            kind="Deep-ML 练习",
            source_files=files,
            content="\n\n".join(chunks),
            source_url=source_url,
            tags=["deep-ml", "可运行练习"],
        )

    legacy_root = PREP_ROOT / "new" / "deepml-problems" / "Problems"
    for folder in sorted(path for path in legacy_root.iterdir() if path.is_dir()):
        files = sorted(path for path in folder.rglob("*") if path.is_file())
        content = "\n\n".join(
            f"## {path.name}\n\n{read_text(path)}"
            for path in files if path.suffix in {".md", ".py"}
        )
        add_material(
            title=f"Deep-ML legacy · {folder.name.replace('_', ' ')}",
            kind="Deep-ML 练习",
            source_files=files,
            content=content,
            tags=["deep-ml", "legacy"],
        )


def index_saved_forum_html() -> None:
    root = PREP_ROOT / "new" / "raw" / "1p3a_html"
    for path in sorted(root.glob("*.html")):
        parser = VisibleHTML()
        parser.feed(read_text(path))
        thread_id = re.search(r"\d+", path.stem)
        source_url = (
            f"https://www.1point3acres.com/bbs/thread-{thread_id.group()}-1-1.html"
            if thread_id else ""
        )
        add_material(
            title=parser.title or f"一亩三分地帖子 {path.stem}",
            kind="一亩三分地本地原帖",
            source_files=[path],
            content=parser.text,
            company=infer_company(path, parser.text[:1000]),
            source_url=source_url,
            tags=["1point3acres", "本地快照"],
        )


def index_code_file(path: Path) -> None:
    text = read_text(path)
    docstring = re.match(r"\s*(?:[rubfRUBF]*)?([\"']{3})([\s\S]*?)\1", text)
    symbols = re.findall(r"^(?:class|def|async def)\s+([A-Za-z_][A-Za-z0-9_]*)", text, re.MULTILINE)
    title = path.stem.replace("_", " ").title()
    if docstring:
        first = summary_from(docstring.group(2), 110)
        if first:
            title = first
    add_material(
        title=title,
        kind=classify(path),
        source_files=[path],
        content=text,
        company=infer_company(path),
        tags=symbols[:12] + ["Python", "可运行代码"],
    )


def record_count(value: Any) -> int:
    if isinstance(value, list):
        return len(value)
    if isinstance(value, dict):
        candidates = [len(item) for item in value.values() if isinstance(item, (list, dict))]
        return max(candidates, default=len(value))
    return 1


def index_raw_data(path: Path) -> None:
    rel = relative(path)
    title = path.stem.replace("_", " ").title()
    summary = "本地原始数据文件。"
    content = ""
    if path.suffix == ".json":
        try:
            payload = json.loads(read_text(path))
            count = record_count(payload)
            summary = f"本地 JSON 数据集；估算包含 {count} 条顶层或主记录。"
            if path.stat().st_size <= 220_000:
                content = json.dumps(payload, ensure_ascii=False, indent=2)
        except json.JSONDecodeError:
            summary = "本地 JSON 文件，但当前内容无法完整解析。"
    elif path.suffix in {".md", ".txt"}:
        content = read_text(path)
    add_material(
        title=title,
        kind="原始数据",
        source_files=[path],
        content=content,
        summary=summary,
        company=infer_company(path, title),
        tags=["raw", path.suffix.lstrip(".") or "file"],
    )


def index_tool_bundle() -> None:
    root = PREP_ROOT / "new" / "interactive_1p3acre"
    files = sorted(
        path for path in root.rglob("*")
        if path.is_file() and "vendor" not in path.parts
    )
    readme = root / "README.md"
    add_material(
        title="旧版交互式 1P3A 本地题库工具",
        kind="旧版本地工具",
        source_files=files,
        content=read_text(readme) if readme.exists() else "",
        tags=["本地网站", "交叉引用", "归档"],
    )
    vendor_files = sorted(path for path in (root / "vendor").rglob("*") if path.is_file())
    if vendor_files:
        add_material(
            title="旧版工具前端依赖",
            kind="旧版本地工具",
            source_files=vendor_files,
            summary="旧版离线题库使用的前端依赖文件；作为构建归档保留。",
            tags=["vendor", "归档"],
        )


def index_repo_metadata() -> None:
    root = PREP_ROOT / "new" / "deepml-problems"
    files = [
        path for path in root.iterdir()
        if path.is_file() and path.name not in IGNORED_NAMES
    ]
    files.extend(path for path in (root / ".github").rglob("*") if path.is_file())
    files.extend(path for path in (root / "utils").rglob("*") if path.is_file())
    if files:
        add_material(
            title="Deep-ML 本地仓库说明与构建工具",
            kind="Deep-ML 练习",
            source_files=sorted(set(files)),
            content=read_text(root / "README.md") if (root / "README.md").exists() else "",
            tags=["deep-ml", "构建工具"],
        )


def load_questions() -> list[dict[str, Any]]:
    payload = json.loads(read_text(QUESTIONS_FILE))
    return payload.get("questions") or payload.get("items") or payload


def relate_questions() -> None:
    questions = load_questions()
    material_tokens = {
        row["id"]: tokens(
            f"{row['title']} {' '.join(row['tags'])} "
            + " ".join(Path(path).stem.replace('_', ' ') for path in row["sourceFiles"][:3])
        )
        for row in materials
    }
    by_id = {row["id"]: row for row in materials}
    for question in questions:
        question_id = str(question.get("id") or "")
        if not question_id:
            continue
        company = str(question.get("company") or "").lower()
        qtext = " ".join(
            str(value) for value in [
                question.get("title", ""), question.get("slug", ""),
                " ".join(question.get("tags") or []),
            ]
        )
        qtokens = tokens(qtext)
        if not qtokens:
            continue
        scored: list[tuple[float, str]] = []
        for row in materials:
            if row["company"] not in {"all", company}:
                continue
            rtokens = material_tokens[row["id"]]
            overlap = qtokens & rtokens
            local_paths = {
                str(Path(path).expanduser().resolve())
                for path in question.get("contentSourceLocalPaths") or []
            }
            same_source = bool(local_paths & set(row["absoluteSourcePaths"]))
            if len(overlap) < 2 and not (same_source and overlap):
                continue
            containment = len(overlap) / max(1, min(len(qtokens), len(rtokens)))
            jaccard = len(overlap) / max(1, len(qtokens | rtokens))
            score = 0.72 * containment + 0.28 * jaccard
            if same_source:
                score += 0.18
            if score >= 0.28:
                scored.append((min(score, 1.0), row["id"]))
        scored.sort(reverse=True)
        seen: set[str] = set()
        for score, material_id in scored:
            if material_id in seen:
                continue
            seen.add(material_id)
            by_id[material_id]["relatedQuestions"].append(
                {
                    "id": question_id,
                    "title": question.get("title") or question.get("slug") or question_id,
                    "company": company,
                    "score": round(score, 3),
                }
            )
            if len(seen) >= 6:
                break


def main() -> None:
    all_files = sorted(
        path for path in PREP_ROOT.rglob("*")
        if path.is_file() and ".git" not in path.parts and "__pycache__" not in path.parts
    )

    index_deepml()
    index_saved_forum_html()
    index_tool_bundle()
    index_repo_metadata()

    for path in all_files:
        rel = relative(path)
        if rel in covered_by_file or path.name in IGNORED_NAMES:
            continue
        if path.suffix == ".md" and not rel.startswith("new/raw/"):
            index_markdown(path)
        elif path.suffix == ".py" and (
            rel.startswith("02_coding_practice/") or rel.startswith("new/drills/")
        ):
            index_code_file(path)
        elif rel.startswith("new/raw/"):
            index_raw_data(path)

    # Account for the few remaining config, notebook, and helper files as one-file records.
    for path in all_files:
        rel = relative(path)
        if rel in covered_by_file or path.name in IGNORED_NAMES:
            continue
        add_material(
            title=path.name,
            kind=classify(path),
            source_files=[path],
            summary=f"本地文件：{rel}",
            tags=[path.suffix.lstrip(".") or "file"],
        )

    relate_questions()
    materials.sort(
        key=lambda row: (
            KIND_ORDER.get(row["kind"], 99),
            row["company"],
            row["title"].lower(),
        )
    )

    manifest = []
    ignored = 0
    for path in all_files:
        rel = relative(path)
        material_ids = sorted(covered_by_file.get(rel, set()))
        status = "indexed" if material_ids else "ignored-metadata"
        if status != "indexed":
            ignored += 1
        manifest.append(
            {
                "path": rel,
                "absolutePath": str(path.resolve()),
                "size": path.stat().st_size,
                "status": status,
                "materialIds": material_ids,
            }
        )

    kind_counts = Counter(row["kind"] for row in materials)
    company_counts = Counter(row["company"] for row in materials)
    related_count = sum(bool(row["relatedQuestions"]) for row in materials)
    related_question_keys = {
        f"{relation['company']}:{relation['id']}"
        for row in materials
        for relation in row["relatedQuestions"]
    }
    payload = {
        "generatedAt": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "sourceRoot": str(PREP_ROOT.resolve()),
        "metadata": {
            "physicalFiles": len(all_files),
            "indexedPhysicalFiles": len(all_files) - ignored,
            "ignoredMetadataFiles": ignored,
            "logicalMaterials": len(materials),
            "materialsRelatedToQuestions": related_count,
            "questionsWithRelatedMaterials": len(related_question_keys),
            "byKind": dict(sorted(kind_counts.items())),
            "byCompany": dict(sorted(company_counts.items())),
        },
        "materials": materials,
        "fileManifest": manifest,
    }
    OUTPUT.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    link_payload = {
        "generatedAt": payload["generatedAt"],
        "materials": [
            {
                key: row[key]
                for key in ["id", "title", "kind", "company", "summary", "sourceFiles", "relatedQuestions"]
            }
            for row in materials
            if row["relatedQuestions"]
        ],
    }
    LINKS_OUTPUT.write_text(
        json.dumps(link_payload, ensure_ascii=False, separators=(",", ":")) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(payload["metadata"], ensure_ascii=False, indent=2))
    if ignored:
        print(f"warning: {ignored} metadata-only files were not grouped")


if __name__ == "__main__":
    main()
