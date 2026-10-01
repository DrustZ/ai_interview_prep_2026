"""正负样本怎么造 —— 以及**三个会毁掉数据集的陷阱**。

code review 的正负样本比 math 难，因为「负」有五种完全不同的含义：

    ① 这条评论是**错的**（事实错误）        → 训练目标：别编
    ② 这条评论是**对的但没价值**（nit）      → 训练目标：别啰嗦
    ③ 这条评论**位置指错了**                 → 训练目标：定位要准
    ④ 这段代码**没有任何评论**               → ⚠️ **这不是负样本**
    ⑤ 这条评论**重复了别人已经说过的**       → 训练目标：别重复

**把 ④ 当负样本是这个领域最经典的错误。** 没人评论只说明没人看，
不说明代码没问题 —— 这是 positive-unlabeled，不是二分类。

    python pairs.py
"""
from __future__ import annotations

import json
import random
from collections import Counter

import gate
import signals
import toyreview

RNG = random.Random(0)


# ─────────────────────────────────────────── 三类正样本
def positives(comments: list, szz_pos: list) -> list:
    """按**证据强度**分层，不是一视同仁。训练时可以按层加权。"""
    out = []
    for c in comments:
        if c["signal"]["resolved"]:
            out.append({"kind": "resolved_comment", "evidence": "weak",
                        "why": f"作者在 {c['signal']['by']} 改了这一行",
                        "path": c["path"], "line": c["line"], "text": c["body"],
                        "_gt_useful": c["_gt_useful"]})
    for p in szz_pos:
        out.append({"kind": "szz_verified_defect", "evidence": "strong",
                    "why": p["evidence"], "path": p["path"], "line": p["line"],
                    "text": p["defect_description"], "_gt_useful": 1})
    return out


# ─────────────────────────────────────────── 四类真负样本 + 一个陷阱
def negatives(comments: list, all_lines: dict) -> dict:
    """返回 {类别: [样本]}。注意 `unreviewed_line` 是**陷阱组**，默认不进训练集。"""
    neg = {"factually_wrong": [], "low_value_nit": [], "duplicate": [],
           "misplaced": [], "unreviewed_line": []}

    kept, dups = gate.dedup_comments(comments, thr=0.10)
    dup_ids = {d["comment_id"] for d in dups}

    for c in comments:
        t = gate.classify(c)
        item = {"path": c["path"], "line": c["line"], "text": c["body"],
                "comment_id": c["comment_id"], "_gt_useful": c["_gt_useful"]}
        if c["comment_id"] in dup_ids:
            neg["duplicate"].append(item)
        elif t in ("nit_style", "praise", "question", "bot"):
            neg["low_value_nit"].append(item)
        elif not c["_gt_useful"]:
            # 真实场景里这一类要靠人工/强模型判定「事实是否成立」
            neg["factually_wrong"].append(item)

    # ③ 位置指错：把一条真评论的行号随机挪开 —— **廉价且高价值的合成负例**
    for c in [x for x in comments if x["_gt_useful"]][:3]:
        n = len(all_lines.get(c["path"], []))
        wrong = RNG.choice([l for l in range(1, n + 1) if abs(l - c["line"]) > 4])
        neg["misplaced"].append({"path": c["path"], "line": wrong,
                                 "text": c["body"], "comment_id": c["comment_id"] + "-mis",
                                 "_gt_useful": 0})

    # ④ 陷阱组：没被评论过的行
    for path, lines in all_lines.items():
        for i, code in enumerate(lines, 1):
            if code.strip() and not any(c["path"] == path and c["line"] == i
                                        for c in comments):
                neg["unreviewed_line"].append({"path": path, "line": i,
                                               "text": None, "code": code.strip()})
    return neg


# ─────────────────────────────────────────── 偏好对
def preference_pairs(pos: list, neg: dict, per_positive: int = 2) -> list:
    """给 DPO / reward model 用的 (chosen, rejected)。

    **关键：配对要在同一个 (文件, 行) 上下文里**。
    如果 chosen 来自 auth.py、rejected 来自 orders.py，模型学到的可能是
    「auth 相关的评论更好」这种和质量无关的捷径 —— 这是最常见的 pair 泄漏。
    """
    pool = (neg["factually_wrong"] + neg["low_value_nit"]
            + neg["duplicate"] + neg["misplaced"])
    pairs = []
    for p in pos:
        same_file = [n for n in pool if n["path"] == p["path"]] or pool
        for n in RNG.sample(same_file, min(per_positive, len(same_file))):
            pairs.append({
                "context": {"path": p["path"], "line": p["line"]},
                "chosen": p["text"], "rejected": n["text"],
                "chosen_kind": p["kind"], "rejected_kind": _kind_of(n, neg),
                "same_file": p["path"] == n["path"],
            })
    return pairs


def _kind_of(item, neg):
    for k, v in neg.items():
        if item in v:
            return k
    return "?"


if __name__ == "__main__":
    built = toyreview.build()
    root, gt = built["root"], built["gt"]
    comments = signals.annotate(root, built["comments"])
    szz_pos = signals.szz_positives(root, gt["commits"]["orders_bugfix"])

    all_lines = {}
    for path in ("shop/orders.py", "shop/auth.py"):
        sha = gt["commits"]["orders_v1" if "orders" in path else "auth_v1"]
        all_lines[path] = toyreview.sh(f"git show {sha}:{path}", root).stdout.splitlines()

    pos = positives(comments, szz_pos)
    neg = negatives(comments, all_lines)

    print("═══ 正样本（按证据强度分层）═══\n")
    for k, v in Counter(p["kind"] for p in pos).items():
        ev = next(p["evidence"] for p in pos if p["kind"] == k)
        bad = sum(1 for p in pos if p["kind"] == k and not p["_gt_useful"])
        print(f"  {k:<24} {v:>2} 条  证据={ev:<7} 其中实际没用的 {bad} 条")
    print("\n  ⭐ **强弱证据不能等权**：SZZ 的正样本由后来真实发生的修复所证明；")
    print("     采纳信号的正样本里混着 3 条假阳性（见 gate.py）。")
    print("     实践：强证据权重 1.0，弱证据 0.3–0.5，或者只用强证据训 reward model。")

    print("\n═══ 负样本（四真一假）═══\n")
    for k, v in neg.items():
        flag = "  ⚠️ 陷阱组，默认不进训练集" if k == "unreviewed_line" else ""
        print(f"  {k:<20} {len(v):>3} 条{flag}")
    print("\n  ⚠️ `unreviewed_line` 有 {} 条 —— 如果把它们当负样本，"
          "负例会瞬间淹没正例\n     （{}:{} 的比例），而且**它们里面有真问题**："
          .format(len(neg["unreviewed_line"]),
                  len(neg["unreviewed_line"]), len(pos)))
    # 证明：cm03 指出的那行确实有 bug，但当时没人再评论，SZZ 后来证实了
    bug_line = szz_pos[0]
    print(f"     例：{bug_line['path']}:{bug_line['line']} 当时没有有效评论，")
    print(f"     三周后被 fix 掉了 —— 它**本该是正样本**。")
    print("     → 「没有评论」是 positive-unlabeled，不是负类。")

    print("\n═══ 偏好对 ═══\n")
    pairs = preference_pairs(pos, neg)
    print(f"  生成 {len(pairs)} 对，同文件配对比例 "
          f"{sum(p['same_file'] for p in pairs)/len(pairs):.0%}")
    print("\n  样例：")
    ex = next(p for p in pairs if p["rejected_kind"] == "factually_wrong")
    print(json.dumps(ex, ensure_ascii=False, indent=2)[:600])
    print("\n  配对类型分布：")
    for k, v in Counter(p["rejected_kind"] for p in pairs).most_common():
        print(f"    rejected = {k:<20} {v}")
