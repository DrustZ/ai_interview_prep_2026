#!/usr/bin/env python3
"""配额重置后，补解锁被题目引用但还没拿到的帖子。
用法: python3 resume_unlock.py   (在 new/ 目录下运行)
之后重跑: cd interactive_1p3acre && python3 build_app.py
"""
import json, urllib.request, urllib.parse, time, os, re, glob
CODE = "AGI30S2Z8GX1Y2J7PMER"  # 换成你的新解锁码
xr = json.load(open('interactive_1p3acre/../raw/../interactive_1p3acre/../raw/qbank_xref.json')) if os.path.exists('raw/qbank_xref.json') else json.load(open('/tmp/qbank_xref.json'))
ref_ids = set()
for v in xr.values():
    for r in v.get('refs', []):
        for u in re.findall(r'1point3acres\.com/(?:bbs/thread-|interview/thread/)(\d+)', r.get('url', '')):
            ref_ids.add(u)
have = set(os.path.basename(x)[:-5] for x in glob.glob('raw/1p3a_html/*.html'))
todo = sorted(ref_ids - have)
print(f'待解锁 {len(todo)} 个')
def unlock(q):
    data = urllib.parse.urlencode({'code': CODE, 'q': str(q)}).encode()
    req = urllib.request.Request("http://117.72.46.162/index.php?m=api&c=api&a=url", data=data, headers={'User-Agent': 'Mozilla/5.0'})
    return json.load(urllib.request.urlopen(req, timeout=30))
for tid in todo:
    time.sleep(4)
    try:
        r = unlock(tid)
        if r.get('code'):
            urllib.request.urlretrieve("http://117.72.46.162" + r['id'], f'raw/1p3a_html/{tid}.html'); print('ok', tid)
        else:
            print('skip', tid, r.get('msg'))
    except Exception as e:
        print('err', tid, e)
