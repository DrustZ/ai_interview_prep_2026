#!/usr/bin/env python3
"""把爬取的原始数据编译成可读题库 markdown。

输入: raw/crawl_all_items.json, raw/h2h_questions_full.json, raw/h2h_api/post_*.json
输出: ../question-bank/{openai,anthropic,gdm,theory-and-mlsd,hack2hire-premium}.md
可重复运行（幂等覆盖）。
"""
import json
import glob
import os
import re

RAW = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(RAW, "..", "question-bank")
os.makedirs(OUT, exist_ok=True)

CAT_ORDER = ["process", "coding", "ml_coding", "ml_theory", "system_design", "ml_system_design", "behavioral"]
CAT_NAME = {
    "process": "流程与情报",
    "coding": "Coding 题",
    "ml_coding": "ML Coding 题",
    "ml_theory": "ML 理论",
    "system_design": "System Design",
    "ml_system_design": "ML System Design",
    "behavioral": "BQ / Culture",
}


def freq_rank(f):
    f = (f or "").lower()
    if "very high" in f or "最高" in f:
        return 0
    if "high" in f or "高" in f:
        return 1
    if "medium" in f or "中" in f:
        return 2
    return 3


def render_items(items, title):
    lines = [f"# {title}", "", "> 由 raw/build_question_bank.py 从爬取数据自动生成（2026-07 抓取）。每条含来源 URL 可回查原文。", ""]
    by_cat = {}
    seen = set()
    for it in items:
        key = (it.get("category"), (it.get("title") or "")[:40].lower())
        if key in seen:
            continue
        seen.add(key)
        by_cat.setdefault(it.get("category", "other"), []).append(it)
    for cat in CAT_ORDER + [c for c in by_cat if c not in CAT_ORDER]:
        if cat not in by_cat:
            continue
        lines.append(f"## {CAT_NAME.get(cat, cat)}")
        lines.append("")
        for it in sorted(by_cat[cat], key=lambda x: freq_rank(x.get("frequency"))):
            meta = " · ".join(
                x for x in [
                    it.get("difficulty") or None,
                    f"频率: {it['frequency']}" if it.get("frequency") else None,
                    it.get("date") or None,
                ] if x
            )
            lines.append(f"### {it.get('title', '(无标题)')}")
            if meta:
                lines.append(f"*{meta}*")
            lines.append("")
            if it.get("detail"):
                lines.append(it["detail"].strip())
            if it.get("solution_hint"):
                lines.append("")
                lines.append(f"**解法**: {it['solution_hint'].strip()}")
            if it.get("url"):
                lines.append("")
                lines.append(f"来源: <{it['url']}>")
            lines.append("")
    return "\n".join(lines)


def main():
    d = json.load(open(os.path.join(RAW, "crawl_all_items.json")))
    items = d["items"]

    for comp, fname, title in [
        ("openai", "openai.md", "OpenAI 题库（爬取全量）"),
        ("anthropic", "anthropic.md", "Anthropic 题库（爬取全量）"),
        ("gdm", "gdm.md", "Google DeepMind 题库（爬取全量）"),
        ("general", "theory-and-mlsd.md", "通用 ML 理论 + ML System Design 资源库"),
    ]:
        sub = [it for it in items if it.get("company") == comp]
        with open(os.path.join(OUT, fname), "w") as f:
            f.write(render_items(sub, title))
        print(f"{fname}: {len(sub)} 条")

    # hack2hire premium content (descriptions + explanations + insights + solutions)
    h2h = json.load(open(os.path.join(RAW, "h2h_questions_full.json")))
    post_meta = {}
    for p in glob.glob(os.path.join(RAW, "h2h_api", "post_*.json")):
        try:
            pd = json.load(open(p))
            data = pd.get("data") or pd
            if isinstance(data, list):
                data = data[0] if data else {}
            pid = data.get("id") or os.path.basename(p)[5:-5]
            post_meta[pid] = data
        except Exception:
            pass

    by_post = {}
    for rec in h2h.values():
        by_post.setdefault(rec["postId"], []).append(rec)

    lines = ["# hack2hire 完整题解（抓取的解锁内容）", "",
             "> 含题面、官方讲解、insights（考点/提示/follow-up）与参考解。论坛内容不可信，但题库与一亩三分地真实面经交叉验证一致。", ""]
    for pid, recs in by_post.items():
        meta = post_meta.get(pid, {})
        title = recs[0].get("postTitle", pid).strip()
        tags = meta.get("companyTags") or meta.get("companyFrequencies") or ""
        lines.append(f"## {title}")
        if tags:
            lines.append(f"*公司标签: {json.dumps(tags, ensure_ascii=False)[:300]}*")
        lines.append("")
        for i, rec in enumerate(recs):
            if len(recs) > 1:
                lines.append(f"### Part {i+1}")
            desc = re.sub(r"<!--.*?-->", "", rec.get("description") or "", flags=re.S).strip()
            if desc:
                lines.append(desc)
                lines.append("")
            if rec.get("explanation"):
                lines.append(f"**讲解**: {rec['explanation'].strip()}")
                lines.append("")
            ins = rec.get("insights") or {}
            for k, label in [("quickSummary", "概要"), ("whatThisTests", "考察点"),
                             ("commonPatterns", "常用模式"), ("hints", "提示"),
                             ("likelyInterviewFollowUps", "可能的 follow-up")]:
                v = ins.get(k)
                if v:
                    if isinstance(v, list):
                        lines.append(f"**{label}**:")
                        lines.extend(f"- {x}" for x in v)
                    else:
                        lines.append(f"**{label}**: {v}")
                    lines.append("")
            sols = rec.get("solutions") or {}
            py = sols.get("python") or sols.get("python3")
            if py:
                lines.append("<details><summary>参考解 (Python)</summary>")
                lines.append("")
                lines.append("```python")
                lines.append(py.strip())
                lines.append("```")
                lines.append("</details>")
                lines.append("")
            st = rec.get("stats") or {}
            if st.get("acceptRate"):
                lines.append(f"*通过率: {st['acceptRate']:.0%}*")
                lines.append("")
    with open(os.path.join(OUT, "hack2hire-premium.md"), "w") as f:
        f.write("\n".join(lines))
    print(f"hack2hire-premium.md: {len(by_post)} 题 / {len(h2h)} 子题")


if __name__ == "__main__":
    main()
