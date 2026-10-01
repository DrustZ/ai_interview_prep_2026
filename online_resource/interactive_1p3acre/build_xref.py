#!/usr/bin/env python3
"""为 qbank 题目建立跨资源交叉引用（本地笔记 / 解锁外链帖 / hack2hire / deep-ml / 原始爬取 URL）。
输出 /tmp/qbank_xref.json ，供 build_app.py 合并进 data.js。
"""
import json, re, os, glob

BASE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..")  # my_interview_prep
NEW = os.path.join(BASE, "new")
RAW = os.path.join(NEW, "raw")

STOP = set("the a an of to and or for with in on is be your you we our using use implement design build "
           "system a1 q1 q2 q3 coding ml problem question interview based simple".split())


def toks(s):
    s = re.sub(r'[^a-z0-9 ]', ' ', (s or '').lower())
    return {w for w in s.split() if len(w) > 2 and w not in STOP}


def sim(a, b):
    if not a or not b: return 0.0
    return len(a & b) / len(a | b)


# ---- build candidate reference index ----
refs = []  # each: {title, url, kind, company, tok}

# 1. hack2hire premium (full solutions)
h2h = json.load(open(os.path.join(RAW, "h2h_questions_full.json")))
seen = set()
for rec in h2h.values():
    t = rec.get("postTitle", "").strip()
    if t in seen: continue
    seen.add(t)
    url = f"https://www.hack2hire.com/companies/anthropic/coding-questions/{rec['postId']}/practice"
    refs.append({"title": t, "url": url, "kind": "hack2hire(完整题解)", "company": "*", "tok": toks(t)})

# 2. deep-ml problems
for meta in glob.glob(os.path.join(NEW, "deepml-problems", "questions", "*", "meta.json")):
    try:
        m = json.load(open(meta))
        t = m.get("title", "")
        refs.append({"title": t, "url": f"https://www.deep-ml.com/problems/{m['id']}",
                     "kind": "deep-ml(可练手写)", "company": "*", "tok": toks(t)})
    except Exception:
        pass

# 3. crawl_all_items (1p3a bbs / blog / other-site source URLs)
for it in json.load(open(os.path.join(RAW, "crawl_all_items.json")))["items"]:
    if it.get("url") and it.get("title"):
        refs.append({"title": it["title"], "url": it["url"],
                     "kind": "爬取来源(" + it.get("category", "?") + ")", "company": it.get("company", "*"),
                     "tok": toks(it["title"])})

# 4. unlocked external editorials (local, have full content in the app + 1p3a-*.md)
for company in ("openai", "anthropic"):
    R = json.load(open(os.path.join(RAW, f"{company}_clean.json")))
    HTML_DIR = os.path.join(RAW, "1p3a_html")
    for it in R["external"]:
        tid = str(it["tid"])
        p = os.path.join(HTML_DIR, f"{tid}.html")
        if os.path.exists(p) and os.path.getsize(p) > 40000:
            refs.append({"title": it["title"],
                         "url": f"https://www.1point3acres.com/interview/thread/{tid}",
                         "kind": "本地已解锁(App 内有正文)", "company": company, "tok": toks(it["title"])})

# 5. local notes coverage (topic-keyword → file). Coarse: reference the whole file by keyword hits.
LOCAL_NOTES = {
    "Anthropic 面经笔记 (含解法)": os.path.join(BASE, "01_company_notes/anthropic/questions_and_solutions.md"),
    "OpenAI 面经笔记": os.path.join(BASE, "01_company_notes/openai/questions.md"),
    "三家面经总报告": os.path.join(BASE, "00_reports_and_plans/final_report_v2.md"),
}
note_text = {}
for name, path in LOCAL_NOTES.items():
    if os.path.exists(path):
        note_text[name] = open(path, encoding="utf-8", errors="replace").read().lower()

# ---- match each qbank problem ----
details = json.load(open("/tmp/qbank_details.json"))
slug_tags = {}
for company in ("openai", "anthropic"):
    for q in json.load(open(os.path.join(RAW, f"{company}_clean.json")))["qbank"]:
        if q.get("slug"):
            slug_tags[f'{company}/{q["slug"]}'] = q.get("tags") or []
for key, q in details.items():
    q["tags"] = slug_tags.get(key, [])

# also cross-ref OJ problems (they have no original thread either) — keyed by company/ojid
for company in ("openai", "anthropic"):
    for o in json.load(open(os.path.join(RAW, f"{company}_clean.json")))["oj"]:
        k = f'{company}/oj/{o["id"]}'
        details[k] = {"company": company, "slug": o.get("title", ""), "title": o.get("title", ""),
                      "overview": None, "related": [], "tags": o.get("tags") or []}
xref = {}
for key, q in details.items():
    company = q["company"]
    title = q.get("title") or q["slug"]
    qtok = toks(title) | toks(q["slug"])
    tagtok = {t for tag in (q.get("tags") or []) for t in toks(tag)}
    scored = []
    for r in refs:
        if r["company"] not in ("*", company): continue
        s = sim(qtok, r["tok"])
        if s < 0.34 and tagtok:  # tag overlap as a secondary booster, doesn't dilute title match
            s = max(s, 0.34 if len(tagtok & r["tok"]) >= 2 and sim(qtok, r["tok"]) >= 0.2 else 0)
        if s >= 0.34:
            scored.append((s, r))
    scored.sort(key=lambda x: -x[0])
    # dedupe by (kind,url), keep top 6
    picks, seenu = [], set()
    for s, r in scored:
        if r["url"] in seenu: continue
        seenu.add(r["url"])
        picks.append({"title": r["title"], "url": r["url"], "kind": r["kind"], "score": round(s, 2)})
        if len(picks) >= 6: break
    # local notes: which mention key tokens of this problem
    key_terms = [t for t in (toks(title) | toks(q["slug"])) if len(t) > 4][:4]
    notes_hit = []
    for name, txt in note_text.items():
        if sum(1 for t in key_terms if t in txt) >= 2:
            notes_hit.append(name)
    xref[key] = {"overview": q.get("overview"), "related": q.get("related", []),
                 "refs": picks, "notes": notes_hit}

json.dump(xref, open("/tmp/qbank_xref.json", "w"), ensure_ascii=False, indent=1)
tot = sum(len(v["refs"]) for v in xref.values())
withref = sum(1 for v in xref.values() if v["refs"])
print(f"qbank {len(xref)} 题, 有交叉引用 {withref} 题, 引用总数 {tot}, refs 索引 {len(refs)}")
# sample
for k in list(xref)[:3]:
    print("\n", k)
    print("  overview:", (xref[k]["overview"] or "")[:80])
    for r in xref[k]["refs"][:3]:
        print(f"   [{r['score']}] {r['kind']}: {r['title'][:40]}")
