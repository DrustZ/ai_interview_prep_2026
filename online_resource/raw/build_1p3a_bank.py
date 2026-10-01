#!/usr/bin/env python3
"""组装 1p3a 会员题库为 ../1p3a-openai.md / ../1p3a-anthropic.md

输入: raw/{company}_clean.json (SSR 提取的 briefings/qbank/external/oj)
      raw/1p3a_html/{tid}.html (解锁工具下载的编辑版)
输出: ../1p3a-openai.md, ../1p3a-anthropic.md
"""
import html
import json
import os
import re

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.environ.get("ONE_P3A_OUTPUT_DIR", os.path.join(HERE, ".."))
HTML_DIR = os.path.join(HERE, "1p3a_html")


def clean_inline(s):
    s = re.sub(r'<code[^>]*>(.*?)</code>', lambda m: '`'+re.sub('<[^>]+>','',m.group(1))+'`', s, flags=re.S)
    s = re.sub(r'<a[^>]*href="([^"]*)"[^>]*>(.*?)</a>', lambda m: '['+re.sub('<[^>]+>','',m.group(2)).strip()+']('+m.group(1)+')', s, flags=re.S)
    s = re.sub(r'<(strong|b)>(.*?)</\1>', lambda m: '**'+re.sub('<[^>]+>','',m.group(2))+'**', s, flags=re.S)
    s = re.sub(r'<(em|i)>(.*?)</\1>', lambda m: '*'+re.sub('<[^>]+>','',m.group(2))+'*', s, flags=re.S)
    s = re.sub(r'<[^>]+>', '', s)
    return html.unescape(s).strip()


def html_to_md(path, list_title):
    with open(path, encoding='utf-8', errors='replace') as handle:
        h = handle.read()

    # The saved page contains the complete React shell before the actual
    # editorial.  Parsing from the first page-level <h1> allowed a sidebar <li>
    # to swallow minified CSS, Sentry attributes, user credits, and eventually
    # the real article.  Restrict extraction to the final markdown-body root.
    roots = [
        h.rfind('<div class=markdown-body>'),
        h.rfind('<div class="markdown-body">'),
    ]
    root = max(roots)
    if root >= 0:
        start = h.find('>', root) + 1
    else:
        # Fallback for older snapshots without the article wrapper.
        title_m = re.search(r'<h1[^>]*>(.*?)</h1>', h, re.S)
        start = title_m.end() if title_m else 0
    body = h[start:]

    for stop in [
        '</article>',
        '在代码编辑器中练习',
        '评论',
        '回复 (',
        'Related Problems',
        '相关题目',
        'window.dataLayer',
        '<footer',
    ]:
        idx = body.find(stop)
        if 0 < idx:
            body = body[:idx]
    body = re.sub(
        r'<(style|script|nav|aside)\b[^>]*>.*?</\1>',
        '',
        body,
        flags=re.I | re.S,
    )

    pres = []

    def stash(m):
        lang = 'python'
        lm = re.search(r'language-(\w+)', m.group(0))
        if lm: lang = lm.group(1)
        code = html.unescape(re.sub(r'<[^>]+>', '', m.group(1)))
        pres.append((lang, code)); return f'\x00PRE{len(pres)-1}\x00'

    body = re.sub(r'<pre[^>]*>(.*?)</pre>', stash, body, flags=re.S)
    out = []
    for m in re.finditer(r'<h([1-4])[^>]*>(.*?)</h\1>|<p[^>]*>(.*?)</p>|<li[^>]*>(.*?)</li>|\x00PRE(\d+)\x00', body, re.S):
        if m.group(1):
            txt = clean_inline(m.group(2))
            if txt in ('目录', 'Table of Contents', 'Contents') or not txt: continue
            # Preserve the generator's existing h2-h4 rendering.  A few saved
            # articles use h1 internally; render only those as a nested h3 so
            # they do not become a second document title.
            source_level = int(m.group(1))
            level = 3 if source_level == 1 else source_level
            out += ['', '#'*level + ' ' + txt, '']
        elif m.group(3) is not None:
            txt = clean_inline(m.group(3))
            if txt: out += [txt, '']
        elif m.group(4) is not None:
            txt = clean_inline(m.group(4))
            if txt: out += ['- ' + txt]
        else:
            lang, code = pres[int(m.group(5))]
            out += ['', '```'+lang, code.rstrip(), '```', '']
    md = re.sub(r'\n{3,}', '\n\n', '\n'.join(out)).strip()

    # A <pre> can sit inside a larger list element and therefore be consumed by
    # that element's regex match.  Resolve every stashed token after rendering
    # as a final safety net; no NUL/PRE placeholders should reach Markdown.
    def restore_stash(match):
        lang, code = pres[int(match.group(1))]
        return f'\n\n```{lang}\n{code.rstrip()}\n```\n\n'

    md = re.sub(r'(?:-\s*)?\x00PRE(\d+)\x00', restore_stash, md)
    md = re.sub(r'\n{3,}', '\n\n', md).strip()
    return f'## {list_title}\n\n{md}'


def humanize(slug):
    if not slug: return '(untitled)'
    return re.sub(r'\bQ(\d)', r'Q\1', slug.replace('-', ' ').title())


def build(company, cn):
    clean_path = os.path.join(HERE, f'{company}_clean.json')
    if not os.path.exists(clean_path):
        clean_path = f'/tmp/{company}_clean.json'
    with open(clean_path, encoding='utf-8') as handle:
        R = json.load(handle)
    L = [f'# {cn} 面试题库 · 一亩三分地会员版（完整）', '',
         f'> 2026-07 从 `interview/problems/company/{company}` 抓取。已尽量用解锁工具取正文；取不到的给出原帖 URL 供手动查看。',
         '> 原始 HTML 在 raw/1p3a_html/。', '']

    # Part 1 briefings
    L += ['', '# 一、面试情报 Briefings（会员版正文）', '']
    for b in R['briefings']:
        L += [f'## {b.get("title","")}', '', (b.get('body') or '').strip(), '']
        srcs = b.get('sources') or []
        if srcs:
            L.append('来源帖: ' + ' · '.join(f'[{s.get("title","link")[:30]}]({s.get("url","")})' for s in srcs))
        L.append('')

    # Part 2 + 3: external threads (unlocked / url)
    L += ['', '# 二、外链帖题解（解锁工具编辑版）', '']
    unlocked, locked = [], []
    for it in R['external']:
        tid = str(it['tid'])
        p = os.path.join(HTML_DIR, f'{tid}.html')
        if os.path.exists(p) and os.path.getsize(p) > 40000:
            unlocked.append((tid, it['title']))
        else:
            locked.append((tid, it['title']))
    for tid, title in unlocked:
        L += [html_to_md(os.path.join(HTML_DIR, f'{tid}.html'), title),
              '', f'*原帖: https://www.1point3acres.com/interview/thread/{tid}*', '', '---', '']
    if locked:
        L += ['', '## 未能解锁的外链帖（请自行打开查看）', '']
        for tid, title in locked:
            L.append(f'- [{title}](https://www.1point3acres.com/interview/thread/{tid})')
        L.append('')

    # Part 4: qbank
    L += ['', '# 三、会员题库 Qbank（元数据 + 链接，正文需在站内查看）', '',
          '| 题目 | 类别 | 频率 | 时长 | 轮次 | 最近考 | 标签 | 链接 |', '|---|---|---|---|---|---|---|---|']
    for q in sorted(R['qbank'], key=lambda x: (x.get('frequency') != 'high', x.get('last_asked') or '')):
        slug = q.get('slug')
        title = q.get('title') or humanize(slug)
        url = f'https://www.1point3acres.com/interview/problems/company/{company}/{slug}' if slug else ''
        tags = ', '.join(q.get('tags') or [])[:60]
        stages = ', '.join(q.get('stages') or [])
        dur = q.get('duration_minutes') or ''
        L.append(f"| {title} | {q.get('category','')} | {q.get('frequency','')} | {dur} | {stages} | {q.get('last_asked','')} | {tags} | [看题]({url}) |")

    # Part 5: OJ
    L += ['', '# 四、OJ 题库（站内原生题，链接自行查看）', '',
          '| 题目 | 链接 |', '|---|---|']
    for o in R['oj']:
        url = f"https://www.1point3acres.com/interview/problems/{o['id']}"
        L.append(f"| {o.get('title','')} | [看题]({url}) |")

    md = '\n'.join(L)
    outp = os.path.join(OUT, f'1p3a-{company}.md')
    os.makedirs(OUT, exist_ok=True)
    with open(outp, 'w', encoding='utf-8') as handle:
        handle.write(md)
    print(f'{company}: {len(md)//1024}KB | briefings {len(R["briefings"])} | 解锁 {len(unlocked)} | 未解锁 {len(locked)} | qbank {len(R["qbank"])} | oj {len(R["oj"])}')


for c, cn in [('openai', 'OpenAI'), ('anthropic', 'Anthropic')]:
    build(c, cn)
