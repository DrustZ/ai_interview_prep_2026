#!/usr/bin/env python3
"""构建交互式题库网页 app（离线可用，双击 index.html 即可）。

数据源: ../raw/{openai,anthropic}_clean.json + ../raw/1p3a_html/{tid}.html
产物: data.js (window.DATA)。index.html / app.js / styles.css 为手写静态文件。
可重复运行。
"""
import html
import json
import os
import re

HERE = os.path.dirname(os.path.abspath(__file__))
RAW = os.path.join(HERE, "..", "raw")
HTML_DIR = os.path.join(RAW, "1p3a_html")
TOOL = "http://117.72.46.162/?code=AGI30S2Z8GX1Y2J7PMER"
DATA_PATH = os.path.join(HERE, 'data.js')
OUTPUT_PATH = os.environ.get('ONE_P3A_DATA_JS', DATA_PATH)


def clean_inline(s):
    s = re.sub(r'<code[^>]*>(.*?)</code>', lambda m: '`'+re.sub('<[^>]+>','',m.group(1))+'`', s, flags=re.S)
    s = re.sub(r'<a[^>]*href="([^"]*)"[^>]*>(.*?)</a>', lambda m: '['+re.sub('<[^>]+>','',m.group(2)).strip()+']('+m.group(1)+')', s, flags=re.S)
    s = re.sub(r'<(strong|b)>(.*?)</\1>', lambda m: '**'+re.sub('<[^>]+>','',m.group(2))+'**', s, flags=re.S)
    s = re.sub(r'<(em|i)>(.*?)</\1>', lambda m: '*'+re.sub('<[^>]+>','',m.group(2))+'*', s, flags=re.S)
    s = re.sub(r'<[^>]+>', '', s)
    return html.unescape(s).strip()


def thread_to_md(h):
    """一亩三分地普通面经帖格式：thread_subject + article_body(<br> 分行)。"""
    subj = re.search(r'<div class="thread_subject">(.*?)</div>', h, re.S)
    title = clean_inline(subj.group(1)) if subj else ''
    m = re.search(r'<div class="article_body">(.*?)(?=<div class="(?:t_f|attachments|pstatus)"|</body>)', h, re.S)
    if not m:
        return ''
    body = m.group(1)
    body = re.sub(r'<div id=1p3a-ad[^>]*>\s*</div>', '', body)  # 去广告
    codes = []
    body = re.sub(r'<pre[^>]*>(.*?)</pre>',
                  lambda x: codes.append(html.unescape(re.sub('<[^>]+>', '', x.group(1)))) or f'\x00C{len(codes)-1}\x00',
                  body, flags=re.S)
    body = re.sub(r'<code[^>]*>(.*?)</code>', lambda x: '`' + re.sub('<[^>]+>', '', x.group(1)) + '`', body, flags=re.S)
    body = re.sub(r'<br\s*/?>', '\n', body)
    body = re.sub(r'</?(b|strong)>', '**', body)
    body = re.sub(r'<a[^>]*href="([^"]*)"[^>]*>(.*?)</a>', lambda x: '[' + re.sub('<[^>]+>', '', x.group(2)).strip() + '](' + x.group(1) + ')', body, flags=re.S)
    body = re.sub(r'<img[^>]*>', '[图片]', body)
    body = re.sub(r'<[^>]+>', '', body)
    body = html.unescape(body)
    for i, c in enumerate(codes):
        body = body.replace(f'\x00C{i}\x00', f'\n```\n{c.strip()}\n```\n')
    body = re.sub(r'\n{3,}', '\n\n', body).strip()
    atts = re.findall(r'<div class="attachments">(.*?)</div>', h, re.S)
    att_md = ''
    if atts:
        links = re.findall(r'href="([^"]+)"[^>]*>(.*?)</a>', atts[0], re.S)
        if links:
            att_md = '\n\n**附件:** ' + ', '.join(f'[{clean_inline(t)}]({u})' for u, t in links)
    if not body and not att_md:
        return ''
    return (f'## {title}\n\n' if title else '') + body + att_md


def html_to_md(path):
    with open(path, encoding='utf-8', errors='replace') as handle:
        h = handle.read()
    if 'class="article_body"' in h:
        return thread_to_md(h)

    roots = [
        h.rfind('<div class=markdown-body>'),
        h.rfind('<div class="markdown-body">'),
    ]
    root = max(roots)
    if root >= 0:
        start = h.find('>', root) + 1
    else:
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

    def restore_stash(match):
        lang, code = pres[int(match.group(1))]
        return f'\n\n```{lang}\n{code.rstrip()}\n```\n\n'

    md = re.sub(r'(?:-\s*)?\x00PRE(\d+)\x00', restore_stash, md)
    return re.sub(r'\n{3,}', '\n\n', md).strip()


def humanize(slug):
    return re.sub(r'\s+', ' ', slug.replace('-', ' ')).strip().title() if slug else '(untitled)'


HTML_DIR_G = os.path.join(RAW, "1p3a_html")


def existing_xref():
    """Recover enrichment from data.js when /tmp/qbank_xref.json is absent."""
    if not os.path.exists(DATA_PATH):
        return {}
    try:
        text = open(DATA_PATH, encoding='utf-8').read().strip()
        prefix = 'window.DATA = '
        if not text.startswith(prefix):
            return {}
        payload = json.loads(text[len(prefix):].removesuffix(';'))
    except Exception:
        return {}

    result = {}
    for problem in payload.get('problems', []):
        company = problem.get('company')
        source = problem.get('source')
        url = problem.get('url') or ''
        key = None
        if source == 'qbank':
            match = re.search(r'/company/[^/]+/([^/?#]+)', url)
            if match:
                key = f'{company}/{match.group(1)}'
        elif source == 'oj':
            match = re.search(r'/problems/([^/?#]+)', url)
            if match:
                key = f'{company}/oj/{match.group(1)}'
        if key:
            result[key] = {
                field: problem.get(field, [] if field != 'overview' else None)
                for field in ('overview', 'refs', 'related', 'notes')
            }
    return result


def attach_threads(refs):
    """把 refs 里指向已解锁 1p3a 帖子的正文抓成 md，返回 [{tid,title,md,url}]。"""
    out = []
    seen = set()
    for r in refs or []:
        m = re.search(r'1point3acres\.com/(?:bbs/thread-|interview/thread/)(\d+)', r.get('url', ''))
        if not m:
            continue
        tid = m.group(1)
        if tid in seen:
            continue
        p = os.path.join(HTML_DIR_G, f'{tid}.html')
        if os.path.exists(p):
            md = html_to_md(p)
            if len(md) > 150:
                seen.add(tid)
                out.append({'tid': tid, 'title': r.get('title', ''), 'url': r.get('url'), 'md': md})
        if len(out) >= 5:
            break
    return out


SD_KW = ('design', 'system', 'schedul', 'playground', 'serving', 'downloader',
         'platform', 'infrastructure', 'rate limit', 'crawler', 'webhook',
         'ci/cd', 'cd command', 'kv store', 'key-value', 'cloud ide', 'video generation',
         'chat', 'payment', 'shard', 'inference', 'rag', 'metrics')
ML_KW = ('transformer', 'attention', 'grpo', 'ppo', 'dpo', 'rlhf', 'sampling', 'entropy',
         'classifier', 'numpy', 'embedding', 'tokeniz', 'loss', 'autograd', 'gradient',
         'neural', 'model', 'batch inference', 'annotat', '1-nn', 'nn ', 'softmax')


def infer_category(title):
    t = (title or '').lower()
    if any(k in t for k in ML_KW):
        return 'ml-coding'
    if any(k in t for k in SD_KW):
        return 'system-design'
    return 'coding'


def build_problems():
    problems = []
    pid = 0
    try:
        XREF = json.load(open('/tmp/qbank_xref.json'))
    except Exception:
        XREF = existing_xref()
    for company in ('openai', 'anthropic'):
        R = json.load(open(os.path.join(RAW, f'{company}_clean.json')))
        # briefings
        for b in R['briefings']:
            pid += 1
            problems.append({
                'pid': pid, 'company': company, 'source': 'briefing',
                'title': b.get('title', ''), 'category': 'process', 'difficulty': None,
                'frequency': None, 'last_asked': None, 'duration': None,
                'roles': [], 'stages': ['情报'], 'tags': ['briefing'],
                'status': 'unlocked', 'content': (b.get('body') or '').strip(),
                'sources': [{'title': s.get('title', ''), 'url': s.get('url', '')} for s in (b.get('sources') or [])],
                'url': None, 'tid': None,
            })
        # external threads
        for it in R['external']:
            pid += 1
            tid = str(it['tid'])
            p = os.path.join(HTML_DIR, f'{tid}.html')
            md = html_to_md(p) if os.path.exists(p) else ''
            unlocked = len(md) > 150
            problems.append({
                'pid': pid, 'company': company, 'source': 'external',
                'title': it['title'], 'category': infer_category(it['title']), 'difficulty': None,
                'frequency': None, 'last_asked': None, 'duration': None,
                'roles': [], 'stages': ['外链帖'], 'tags': [],
                'status': 'unlocked' if unlocked else 'locked',
                'content': md if unlocked else '',
                'sources': [], 'url': f'https://www.1point3acres.com/interview/thread/{tid}', 'tid': tid,
            })
        # qbank
        for q in R['qbank']:
            pid += 1
            slug = q.get('slug')
            xr = XREF.get(f'{company}/{slug}', {})
            problems.append({
                'pid': pid, 'company': company, 'source': 'qbank',
                'title': q.get('title') or humanize(slug), 'category': q.get('category'),
                'difficulty': q.get('difficulty'), 'frequency': q.get('frequency'),
                'last_asked': q.get('last_asked'), 'duration': q.get('duration_minutes'),
                'roles': q.get('roles') or [], 'stages': q.get('stages') or [], 'tags': q.get('tags') or [],
                'status': 'locked', 'content': '',
                'overview': xr.get('overview'), 'refs': xr.get('refs', []),
                'related': xr.get('related', []), 'notes': xr.get('notes', []),
                'threads': attach_threads(xr.get('refs', [])),
                'sources': [], 'tid': None,
                'url': f'https://www.1point3acres.com/interview/problems/company/{company}/{slug}' if slug else None,
            })
        # oj
        for o in R['oj']:
            pid += 1
            xr = XREF.get(f'{company}/oj/{o["id"]}', {})
            problems.append({
                'pid': pid, 'company': company, 'source': 'oj',
                'title': o.get('title', ''), 'category': o.get('category') or infer_category(o.get('title')),
                'difficulty': o.get('difficulty'), 'frequency': None,
                'last_asked': None, 'duration': None,
                'roles': [], 'stages': ['OJ'], 'tags': o.get('tags') or [],
                'status': 'locked', 'content': '',
                'overview': xr.get('overview'), 'refs': xr.get('refs', []),
                'related': xr.get('related', []), 'notes': xr.get('notes', []),
                'threads': attach_threads(xr.get('refs', [])),
                'sources': [], 'tid': None,
                'url': f"https://www.1point3acres.com/interview/problems/{o['id']}",
            })
    return problems


def main():
    problems = build_problems()
    data = {'tool': TOOL, 'built': '2026-07-10', 'problems': problems}
    js = 'window.DATA = ' + json.dumps(data, ensure_ascii=False) + ';'
    with open(OUTPUT_PATH, 'w', encoding='utf-8') as handle:
        handle.write(js)
    from collections import Counter
    c = Counter((p['company'], p['source']) for p in problems)
    unlocked = sum(1 for p in problems if p['status'] == 'unlocked')
    print(f'problems: {len(problems)} (unlocked {unlocked})  data.js {os.path.getsize(OUTPUT_PATH)//1024}KB')
    for k, v in sorted(c.items()):
        print(f'  {k}: {v}')


if __name__ == '__main__':
    main()
