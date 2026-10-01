"""造 code review 的训练语料：git 历史 + review 评论 + **可计算的采纳信号**。

和 SWE agent 数据最大的不同：**这里没有测试可以跑。**
「这条评论有没有用」没有执行 oracle。所以造数据的核心工作变成了
**制造可验证性** —— 从历史里挖出两种能自动计算的 ground truth：

  ① **采纳信号（resolution / outdated）**
     评论指向的代码行，在后续 commit 里被改了吗？
     改了 → 作者认可了这条评论。
     ByteDance BitsAI-CR 叫 Outdated Rate，Atlassian 叫 Code Resolution Rate ——
     **两家独立地收敛到了同一个信号**，这不是巧合。

  ② **SZZ：真实缺陷的位置**
     一个 bug-fix commit 修了哪几行 → git blame 那几行 → 找到**引入 bug 的 commit**。
     于是你得到 `(某个历史版本的代码, 这一行确实有缺陷)` —— 一条**可验证的正样本**。

本文件产出（全部落到 /tmp/cr_toyrepo）：
  * 一个 git 仓库：feature commit 引入缺陷 → review → 部分被采纳的 follow-up → 后来的 bug-fix
  * `comments.jsonl`：42 条 review 评论，混着真信号和五类噪声
  * `groundtruth.json`：我知道正确答案，用来给 pipeline 写断言
"""
from __future__ import annotations

import json
import shutil
import subprocess
import textwrap
from pathlib import Path

DEFAULT = Path("/tmp/cr_toyrepo")

# 评论类型：前四类是 BitsAI-CR 的四个 review dimension，后五类是必须被过滤掉的噪声
SIGNAL_TYPES = ("code_defect", "security", "maintainability", "performance")
NOISE_TYPES = ("nit_style", "question", "praise", "bot", "obsolete")


def sh(cmd, cwd, check=True):
    return subprocess.run(cmd, cwd=str(cwd), shell=True, capture_output=True,
                          text=True, check=check)


def _w(root: Path, rel: str, body: str):
    p = root / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(textwrap.dedent(body).lstrip())


def _commit(root: Path, msg: str, date: str) -> str:
    sh("git add -A", root)
    sh(f'GIT_AUTHOR_DATE="{date}" GIT_COMMITTER_DATE="{date}" '
       f'git commit -q -m {msg!r}', root)
    return sh("git rev-parse HEAD", root).stdout.strip()


# ─────────────────────────────────────────────────────────────
V1_ORDERS = '''
    import json

    DISCOUNT = 0.15

    def load_orders(path):
        with open(path) as f:
            return json.load(f)

    def total(order):
        s = 0
        for it in order["items"]:
            s += it["price"] * it["qty"]
        return s * (1 - DISCOUNT)

    def find_order(orders, oid):
        for o in orders:
            if o["id"] == oid:
                return o

    def apply_coupon(order, code):
        if code == "SAVE10":
            order["total"] = total(order) * 0.9
        return order["total"]
'''

# follow-up：作者采纳了两条评论（find_order 加了 None 处理、DISCOUNT 抽成参数）
V2_ORDERS = '''
    import json

    DEFAULT_DISCOUNT = 0.15

    def load_orders(path):
        with open(path) as f:
            return json.load(f)

    def total(order, discount=DEFAULT_DISCOUNT):
        s = 0
        for it in order["items"]:
            s += it["price"] * it["qty"]
        return s * (1 - discount)

    def find_order(orders, oid):
        for o in orders:
            if o["id"] == oid:
                return o
        raise KeyError(f"no order {oid}")

    def apply_coupon(order, code):
        if code == "SAVE10":
            order["total"] = total(order) * 0.9
        return order["total"]
'''

# 后来的 bug-fix：apply_coupon 在 code 不匹配时返回未设置的 key → KeyError
V3_ORDERS_FIX = '''
    import json

    DEFAULT_DISCOUNT = 0.15

    def load_orders(path):
        with open(path) as f:
            return json.load(f)

    def total(order, discount=DEFAULT_DISCOUNT):
        s = 0
        for it in order["items"]:
            s += it["price"] * it["qty"]
        return s * (1 - discount)

    def find_order(orders, oid):
        for o in orders:
            if o["id"] == oid:
                return o
        raise KeyError(f"no order {oid}")

    def apply_coupon(order, code):
        order.setdefault("total", total(order))
        if code == "SAVE10":
            order["total"] = total(order) * 0.9
        return order["total"]
'''

V1_AUTH = '''
    import hashlib

    def hash_pw(pw):
        return hashlib.md5(pw.encode()).hexdigest()

    def check(user, pw, db):
        row = db.execute("SELECT pw FROM users WHERE name = '" + user + "'")
        return row and row[0] == hash_pw(pw)
'''

V2_AUTH = '''
    import hashlib

    def hash_pw(pw, salt):
        return hashlib.sha256((salt + pw).encode()).hexdigest()

    def check(user, pw, db):
        row = db.execute("SELECT pw, salt FROM users WHERE name = ?", (user,))
        return bool(row) and row[0] == hash_pw(pw, row[1])
'''


def build(root: Path = DEFAULT) -> dict:
    if root.exists():
        shutil.rmtree(root)
    root.mkdir(parents=True)
    sh("git init -q -b main", root)
    sh('git config user.email dev@x.io && git config user.name Dev', root)

    _w(root, "README.md", "# shop\n")
    c0 = _commit(root, "init", "2025-03-03T09:00:00")

    _w(root, "shop/orders.py", V1_ORDERS)
    c1 = _commit(root, "feat: order totals and coupons", "2025-03-04T10:00:00")

    _w(root, "shop/auth.py", V1_AUTH)
    c2 = _commit(root, "feat: password check", "2025-03-05T11:00:00")

    # 作者采纳部分评论后的 follow-up
    _w(root, "shop/orders.py", V2_ORDERS)
    c3 = _commit(root, "review: handle missing order, make discount a param",
                 "2025-03-06T14:00:00")
    _w(root, "shop/auth.py", V2_AUTH)
    c4 = _commit(root, "review: salted sha256 + parameterised query",
                 "2025-03-06T15:30:00")

    # 三周后的 bug-fix —— SZZ 要从这里回溯到 c1
    _w(root, "shop/orders.py", V3_ORDERS_FIX)
    c5 = _commit(root, "fix: apply_coupon raises KeyError when code does not match",
                 "2025-03-27T16:00:00")

    comments = _comments(c1, c2)
    (root / "comments.jsonl").write_text(
        "\n".join(json.dumps(c, ensure_ascii=False) for c in comments))

    gt = {
        "commits": {"init": c0, "orders_v1": c1, "auth_v1": c2,
                    "orders_review": c3, "auth_review": c4, "orders_bugfix": c5},
        # SZZ 期望结果：c5 修的那一行，是 c1 引入的
        "szz_expected": {"fix_commit": c5, "inducing_commit": c1,
                         "file": "shop/orders.py"},
        "n_comments": len(comments),
        "n_signal": sum(c["_gt_useful"] for c in comments),
    }
    (root / "groundtruth.json").write_text(json.dumps(gt, indent=2))
    return {"root": root, "comments": comments, "gt": gt}


def _c(cid, commit, path, line, ctype, author, body, useful, addressed):
    """一条 review 评论。`_gt_*` 前缀的字段是**我造数据时知道的真值**，
    真实数据里没有 —— pipeline 不许用它们，只能用来写断言。"""
    return {"comment_id": cid, "commit": commit, "path": path, "line": line,
            "type": ctype, "author": author, "body": body,
            "_gt_useful": useful, "_gt_addressed": addressed}


def _comments(c1: str, c2: str) -> list:
    o, a = "shop/orders.py", "shop/auth.py"
    rows = [
        # ── orders.py 上的评论 ─────────────────────────────────────
        _c("cm01", c1, o, 18, "code_defect", "alice",
           "find_order returns None when the id is missing; every caller will "
           "hit an AttributeError. Raise KeyError or return a sentinel.", 1, 1),
        _c("cm02", c1, o, 3, "maintainability", "bob",
           "DISCOUNT as a module constant makes total() untestable. "
           "Pass it as a parameter with this as the default.", 1, 1),
        _c("cm03", c1, o, 23, "code_defect", "alice",
           "apply_coupon reads order['total'] even when the code does not match, "
           "so it KeyErrors for any other coupon.", 1, 0),   # ← 真信号但当时没被采纳
        _c("cm04", c1, o, 10, "nit_style", "carol",
           "nit: `s` -> `subtotal`", 0, 0),
        _c("cm05", c1, o, 1, "nit_style", "carol",
           "nit: stdlib imports should be in their own group", 0, 0),
        _c("cm06", c1, o, 12, "question", "dave",
           "Is qty ever a float here?", 0, 0),
        _c("cm07", c1, o, 9, "praise", "bob", "Nice, this is much cleaner 👍", 0, 0),
        _c("cm08", c1, o, 1, "bot", "codecov[bot]",
           "Coverage decreased (-0.4%) to 87.2%", 0, 0),
        _c("cm09", c1, o, 11, "performance", "dave",
           "This loop is O(n) — consider sum() with a generator.", 0, 0),  # 技术正确但无价值
        _c("cm10", c1, o, 5, "obsolete", "erin",
           "This references the old `read_orders` helper that was removed last week.",
           0, 0),
        # ── auth.py 上的评论 ───────────────────────────────────────
        _c("cm11", c2, a, 4, "security", "alice",
           "MD5 for password hashing is broken. Use a salted KDF "
           "(sha256+salt at minimum, argon2/bcrypt preferably).", 1, 1),
        _c("cm12", c2, a, 7, "security", "alice",
           "String-concatenated SQL — this is injectable. Use a parameterised query.",
           1, 1),
        _c("cm13", c2, a, 8, "code_defect", "bob",
           "`row and row[0] == ...` returns the row object when row is falsy; "
           "wrap in bool().", 1, 1),
        _c("cm14", c2, a, 3, "nit_style", "carol", "nit: two blank lines here", 0, 0),
        _c("cm15", c2, a, 1, "bot", "sonarqube[bot]",
           "1 Code Smell, 0 Bugs, 0 Vulnerabilities", 0, 0),
        _c("cm16", c2, a, 6, "question", "dave", "which db driver is this?", 0, 0),
        # ── 一条「看起来专业但是错的」—— 最难过滤的那类 ────────────────
        _c("cm17", c2, a, 4, "security", "frank",
           "hashlib is not thread-safe, wrap the call in a lock.", 0, 0),
    ]
    # 复制几条造出重复评论（真实 PR 里多人重复指出同一问题非常常见）
    rows.append(_c("cm18", c2, a, 4, "security", "grace",
                   "Please don't use MD5 for passwords, it's not secure.", 1, 1))
    rows.append(_c("cm19", c1, o, 18, "code_defect", "heidi",
                   "find_order can return None -> callers crash.", 1, 1))
    return rows


if __name__ == "__main__":
    out = build()
    gt = out["gt"]
    print(f"仓库 {out['root']}，{len(gt['commits'])} 个 commit")
    for k, v in gt["commits"].items():
        print(f"  {v[:7]}  {k}")
    print(f"\n评论 {gt['n_comments']} 条，其中真正有价值的 {gt['n_signal']} 条 "
          f"（{gt['n_signal']/gt['n_comments']:.0%}）")
    print("\n样例（前两条）：")
    for c in out["comments"][:2]:
        print(json.dumps(c, ensure_ascii=False, indent=2)[:340])
