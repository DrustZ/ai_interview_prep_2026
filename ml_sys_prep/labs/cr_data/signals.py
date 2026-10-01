"""**制造可验证性**：从 git 历史里算出两种自动 ground truth。

code review 没有测试可跑。所以第一件事不是训模型，是**找到一个能自动算、
且和「有没有用」相关的信号**。业界收敛到的两个：

  ① **采纳信号**（BitsAI-CR 叫 Outdated Rate，Atlassian 叫 Code Resolution Rate）
     评论指向的代码行，在后续 commit 里被改了吗？
     · ByteDance：Go 语言上做到 26.7%；**人类 reviewer 的基线是 35–46%**
     · Atlassian：CRR 做到 40–45%，**人类约 45%**
     两家独立地选了同一个信号 —— 因为它是**唯一能在生产里零成本、全量拿到的**。

  ② **SZZ**：bug-fix commit → git blame 被修的行 → 找到**引入 bug 的 commit**
     产出 `(历史版本的代码, 这一行确实有缺陷)` —— 一条**可验证的正样本**。
     ⚠️ 它有硬限制，见 `szz()` 的 docstring。

    python signals.py
"""
from __future__ import annotations

import json
import re
from pathlib import Path

import toyreview
from toyreview import sh

HUNK = re.compile(r"^@@ -(\d+)(?:,(\d+))? \+(\d+)(?:,(\d+))? @@")


# ─────────────────────────────────────────── ① 采纳信号
def changed_old_lines(root: Path, a: str, b: str, path: str) -> set:
    """`git diff a..b -- path` 中**旧文件（a 版本）里被删改的行号集合**。

    关键在于读 hunk 头 `@@ -old_start,old_len +new_start,new_len @@` 的**左边**：
    右边是新文件的行号，用错了就会把采纳信号算歪。
    """
    out = sh(f"git diff -U0 {a} {b} -- {path}", root, check=False).stdout
    touched = set()
    for line in out.splitlines():
        m = HUNK.match(line)
        if m:
            start, ln = int(m.group(1)), int(m.group(2) or 1)
            touched |= set(range(start, start + max(ln, 1)))
            if ln == 0:                        # 纯新增：把插入点前后各算一行
                touched |= {start, start + 1}
    return touched


def next_commit_touching(root: Path, after: str, path: str):
    """`after` 之后第一个改动了 `path` 的 commit。"""
    out = sh(f"git log --reverse --format=%H {after}..HEAD -- {path}",
             root, check=False).stdout.split()
    return out[0] if out else None


def resolution_signal(root: Path, comment: dict, window_commits: int = 3) -> dict:
    """这条评论指向的行，之后被改了吗？

    `window_commits` 是时间窗 —— BitsAI-CR 用的是**一周**。
    窗口太长会把无关的重构算成「采纳」，太短会漏掉慢反应的作者。
    **这是个必须扫的超参，不是常数。**
    """
    cur, seen = comment["commit"], 0
    while seen < window_commits:
        nxt = next_commit_touching(root, cur, comment["path"])
        if not nxt:
            break
        touched = changed_old_lines(root, cur, nxt, comment["path"])
        if comment["line"] in touched:
            return {"resolved": 1, "by": nxt[:7], "n_hops": seen + 1}
        cur, seen = nxt, seen + 1
    return {"resolved": 0, "by": None, "n_hops": seen}


# ─────────────────────────────────────────── ② SZZ
def szz(root: Path, fix_commit: str) -> list:
    """给一个 bug-fix commit，回溯**引入 bug 的 commit**。

    做法：取 fix 删改掉的行 → 在 fix 的父提交上 `git blame` 这些行 →
    最后碰过它们的 commit 就是嫌疑人。

    ⚠️ **诚实说清 SZZ 的边界**（这是学界反复量化过的）：
      * **ghost commit**：fix 只新增不删改 → blame 无从下手。
        Linux kernel 上占 **17.47%**
      * **跨文件**：bug 的成因在别的文件里，占 **7.20%**
      * 综合起来 **超过 40% 的 case 光靠 blame 解决不了**
        （28% 需要往上翻更多历史，14% 完全 blameless）
      * 纯格式化/重构 commit 会被误认成 inducing —— 要用
        「忽略空白改动」的 blame（`-w`）+ 重构检测来缓解

    所以 SZZ 给的是**高精度但低召回**的正样本。它适合当种子，不适合当全集。
    """
    parent = sh(f"git rev-parse {fix_commit}~1", root).stdout.strip()
    files = sh(f"git diff --name-only {parent} {fix_commit}", root).stdout.split()
    out = []
    for path in files:
        old_lines = sorted(changed_old_lines(root, parent, fix_commit, path))
        if not old_lines:
            out.append({"path": path, "ghost": True, "inducing": []})
            continue
        inducing = {}
        for ln in old_lines:
            # -w 忽略纯空白改动，避免把格式化 commit 当成 bug 的来源
            b = sh(f"git blame -w -L {ln},{ln} --porcelain {parent} -- {path}",
                   root, check=False).stdout
            if b:
                sha = b.split()[0]
                inducing.setdefault(sha, []).append(ln)
        out.append({"path": path, "ghost": False,
                    "inducing": [{"commit": s, "lines": ls}
                                 for s, ls in inducing.items()]})
    return out


def szz_positives(root: Path, fix_commit: str) -> list:
    """把 SZZ 的结果变成**训练用的正样本**：
    「在 inducing commit 的这个版本上，这一行有缺陷，缺陷描述来自 fix 的 message」。

    这是 code review 数据里**唯一一类真正可验证的正样本** ——
    因为它由后来真实发生的修复所证明，不依赖任何人的主观判断。
    """
    msg = sh(f"git log -1 --format=%s {fix_commit}", root).stdout.strip()
    pos = []
    for f in szz(root, fix_commit):
        for ind in f["inducing"]:
            snippet = sh(f"git show {ind['commit']}:{f['path']}",
                         root, check=False).stdout.splitlines()
            for ln in ind["lines"]:
                pos.append({
                    "kind": "szz_verified_defect",
                    "commit": ind["commit"], "path": f["path"], "line": ln,
                    "code": snippet[ln - 1].strip() if ln <= len(snippet) else "",
                    "defect_description": msg,
                    "evidence": f"fixed in {fix_commit[:7]}",
                })
    return pos


# ─────────────────────────────────────────── 汇总
def annotate(root: Path, comments: list) -> list:
    for c in comments:
        c["signal"] = resolution_signal(root, c)
    return comments


if __name__ == "__main__":
    built = toyreview.build()
    root, comments, gt = built["root"], built["comments"], built["gt"]

    print("═══ ① 采纳信号（真的用 git diff 算的）═══\n")
    annotate(root, comments)
    print("{:<6} {:<16} {:<5} {:<9} {:>8} {:>8}".format(
        "id", "type", "line", "resolved", "真值采纳", "真值有用"))
    for c in comments:
        print("{:<6} {:<16} {:<5} {:<9} {:>8} {:>8}".format(
            c["comment_id"], c["type"], c["line"],
            "✅ " + (c["signal"]["by"] or "") if c["signal"]["resolved"] else "❌",
            c["_gt_addressed"], c["_gt_useful"]))

    n = len(comments)
    res = sum(c["signal"]["resolved"] for c in comments)
    agree = sum(c["signal"]["resolved"] == c["_gt_addressed"] for c in comments)
    print(f"\n采纳率（Outdated Rate 类比）= {res}/{n} = {res/n:.0%}")
    print(f"和真值一致 {agree}/{n} = {agree/n:.0%}")
    print("参考：ByteDance Go 26.7%（人类 35–46%）；Atlassian CRR 40–45%（人类 ~45%）")

    print("\n═══ ② SZZ（真的用 git blame 回溯的）═══\n")
    fix = gt["commits"]["orders_bugfix"]
    print(f"bug-fix commit：{fix[:7]}  "
          f"{sh(f'git log -1 --format=%s {fix}', root).stdout.strip()}")
    for f in szz(root, fix):
        for ind in f["inducing"]:
            exp = gt["szz_expected"]["inducing_commit"]
            ok = "✅ 命中期望" if ind["commit"].startswith(exp[:7]) else "⚠️ 与期望不符"
            print(f"  {f['path']}  行 {ind['lines']} ← 由 {ind['commit'][:7]} 引入  {ok}")

    print("\n可验证正样本：")
    for p in szz_positives(root, fix):
        print(f"  {p['path']}:{p['line']}  `{p['code'][:52]}`")
        print(f"    缺陷：{p['defect_description'][:70]}")
        print(f"    证据：{p['evidence']}")
