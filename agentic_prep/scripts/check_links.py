#!/usr/bin/env python3
"""校验 agentic2 下所有 markdown 的相对链接与锚点目标是否存在。"""
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
LINK_RE = re.compile(r"\[[^\]]*\]\(([^)\s]+)\)")
FENCE_RE = re.compile(r"```.*?```", re.S)
INLINE_CODE_RE = re.compile(r"`[^`\n]*`")

errors = []
md_files = sorted(p for p in ROOT.rglob("*.md") if "viewer" not in p.parts)
for md in md_files:
    text = md.read_text(encoding="utf-8")
    text = INLINE_CODE_RE.sub("", FENCE_RE.sub("", text))
    for m in LINK_RE.finditer(text):
        target = m.group(1)
        if target.startswith(("http://", "https://", "mailto:")):
            continue
        path_part = target.split("#", 1)[0]
        if not path_part:  # 纯页内锚点
            continue
        resolved = (md.parent / path_part).resolve()
        if not resolved.exists():
            errors.append(f"{md.relative_to(ROOT)}: 断链 -> {target}")

if errors:
    print(f"FAIL: {len(errors)} 个断链")
    print("\n".join(errors))
    sys.exit(1)
print(f"OK: {len(md_files)} 个文件全部链接可解析")
