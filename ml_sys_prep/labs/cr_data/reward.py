"""Reward 设计：**分层 + 精度优先 + 防 hack**。

和 math/SWE 的 RL 最大的不同：

    math：reward = 答案对不对         → 对称，找不到只是没得分
    SWE ：reward = 测试过不过         → 对称
    CR  ：**误报会主动造成伤害**       → **不对称**

一条错误的 review 评论不是「没得分」，它消耗 reviewer 的信任。
ByteDance 的数据：只有 30% 的 review 会被立刻看；一旦机器人开始说废话，
开发者就整体屏蔽它 —— **一次误报的代价远大于一次漏报**。

所以 reward 的第一原则是**精度优先**，而不是 F1 最大化。
BitsAI-CR 因此上了两段式：RuleChecker 先找，**ReviewFilter 再砍**。

    python reward.py
"""
from __future__ import annotations

import re

import numpy as np


# ══════════════════════════════════════════ 分层 reward
def r1_deterministic(comment: dict, ctx: dict) -> dict:
    """**第一层：确定性硬闸门**。免费、不漂移、不需要校准。

    能被静态分析/编译器/规则确定的东西，就不要交给模型判断：
      * 评论指向的行号存在吗？（越界 = 直接判 0）
      * 评论声称的 API/符号在这个版本里存在吗？（防「过期引用」）
      * 有没有对应的 linter/SAST 规则命中？（命中 = 强证据）
    """
    reasons = []
    if not (1 <= comment["line"] <= ctx["n_lines"]):
        return {"score": 0.0, "hard_fail": True, "reasons": ["行号越界"]}
    code = ctx["lines"][comment["line"] - 1]
    for sym in re.findall(r"`([A-Za-z_][\w.]*)`", comment["body"]):
        if sym not in ctx["source"]:
            reasons.append(f"引用了不存在的符号 `{sym}` → 疑似过期/幻觉")
            return {"score": 0.0, "hard_fail": True, "reasons": reasons}
    hit = any(rule in code for rule in ctx.get("sast_patterns", []))
    if hit:
        reasons.append("命中静态分析规则（强证据）")
    return {"score": 1.0 if hit else 0.5, "hard_fail": False, "reasons": reasons}


def r2_evidence(comment: dict, ctx: dict) -> dict:
    """**第二层：来自历史的证据**（本 lab 前面算出来的两个信号）。

    强证据（SZZ 证实这一行后来真的被 fix 了）> 弱证据（作者改了这一行）。
    """
    if comment.get("szz_confirmed"):
        return {"score": 1.0, "kind": "strong", "why": "后来真的被 bug-fix 修了"}
    if comment.get("resolved"):
        return {"score": 0.5, "kind": "weak", "why": "作者改了这一行（有 30% 假阳性）"}
    return {"score": 0.0, "kind": "none", "why": "无历史证据"}


def r3_judge(comment: dict, ctx: dict, judge_precision: float = 0.77) -> dict:
    """**第三层：LLM judge**。最贵、最会漂、**必须用人工标注校准**。

    BitsAI-CR 的一个反直觉发现值得抄（他们比了三种推理格式）：

        Direct Conclusion   （只出结论）        1.7s    63.27%
        Reasoning-First     （先推理后结论）    31.0s   65.80%   ← 慢 18 倍只多 2.5 个点
        Conclusion-First    （先结论后理由）    1.7s    **77.09%**  ← 选它

    **先给结论再给理由，比先推理再给结论精度更高而且快 18 倍。**
    一个可能的解释：先写结论迫使模型基于证据表态，而不是被自己
    生成的推理链带跑（推理链会为一个不成立的结论找补）。
    """
    return {"score": judge_precision, "cost": 1.0,
            "note": "分数要用人工标注校准过才可信"}


def total_reward(comment: dict, ctx: dict, w=(0.3, 0.5, 0.2),
                 fp_penalty: float = 3.0) -> dict:
    """**硬闸门在前，加权在后，误报单独重罚。**

    `fp_penalty=3.0` 是这套设计的核心：一次误报抵三次正确。
    这个数不是拍的 —— 它应该由「一次误报让用户少看多少条后续评论」估出来。
    """
    r1 = r1_deterministic(comment, ctx)
    if r1["hard_fail"]:
        return {"reward": -fp_penalty, "breakdown": {"r1": r1}, "gated": True}
    r2, r3 = r2_evidence(comment, ctx), r3_judge(comment, ctx)
    base = w[0] * r1["score"] + w[1] * r2["score"] + w[2] * r3["score"]
    verbosity = max(0, len(comment["body"]) - 400) / 400 * 0.1     # 啰嗦轻罚
    return {"reward": round(base - verbosity, 3), "gated": False,
            "breakdown": {"r1": r1, "r2": r2, "r3": r3, "verbosity": -verbosity}}


# ══════════════════════════════════════════ 精度优先：两段式
def two_stage(checker_recall: float = 0.62, checker_precision: float = 0.28,
              filter_thresholds=None, trust_decay: float = 0.75):
    """模拟 RuleChecker → ReviewFilter 两段式，扫 filter 阈值。

    参数取自 BitsAI-CR 上线初期的真实数字：
    RuleChecker 精度 27.9%（后来优化到 62.6%），ReviewFilter 把它拉到 75.0%。

    **要看的不是 F1，是「用户还愿不愿意读」。**
    这里用一个简单的信任模型：一个 PR 上误报越多，用户读后续评论的概率越低。
    """
    thresholds = filter_thresholds or [0.0, 0.3, 0.5, 0.7, 0.85, 0.95]
    n_real = 3.0                                   # 假设每个 PR 平均 3 个真问题
    tp0 = n_real * checker_recall
    fp0 = tp0 * (1 - checker_precision) / max(checker_precision, 1e-9)
    rows = []
    for t in thresholds:
        # filter 阈值越高，砍掉的误报越多，但也会误伤真问题
        keep_fp = fp0 * (1 - t) ** 1.6
        keep_tp = tp0 * (1 - t) ** 0.35
        prec = keep_tp / max(keep_tp + keep_fp, 1e-9)
        # 信任模型：每多一条误报，用户继续读后续评论的概率乘 trust_decay
        trust = trust_decay ** keep_fp
        adopted = keep_tp * trust                  # 实际被采纳的真问题数
        rows.append({"thr": t, "comments_per_pr": keep_tp + keep_fp,
                     "precision": prec, "recall": keep_tp / n_real,
                     "f1": 2 * prec * (keep_tp / n_real)
                           / max(prec + keep_tp / n_real, 1e-9),
                     "trust": trust, "adopted_per_pr": adopted})
    return rows


# ══════════════════════════════════════════ 防 hack
def hack_signals(comments: list) -> dict:
    """reward hacking 在 code review 上的三个典型形态。"""
    n = max(1, len(comments))
    lens = [len(c["body"]) for c in comments]
    hedged = sum(1 for c in comments if re.search(
        r"\b(might|may|could|consider|possibly|perhaps)\b", c["body"], re.I))
    generic = sum(1 for c in comments if re.search(
        r"\b(add (a )?(unit )?tests?|add error handling|add (a )?docstring|"
        r"consider refactoring)\b", c["body"], re.I))
    per_line = {}
    for c in comments:
        per_line.setdefault((c["path"], c["line"]), 0)
        per_line[(c["path"], c["line"])] += 1
    return {
        "① 模糊化（用 might/could 规避被判错）": hedged / n,
        "② 万能话术（『加个测试』适用于任何代码）": generic / n,
        "③ 散弹枪（同一行堆多条以提高命中率）":
            sum(v - 1 for v in per_line.values()) / n,
        "平均长度": float(np.mean(lens)),
    }


if __name__ == "__main__":
    import gate, signals, toyreview
    built = toyreview.build()
    root, gt = built["root"], built["gt"]
    comments = signals.annotate(root, built["comments"])
    szz = {(p["path"], p["line"]) for p in
           signals.szz_positives(root, gt["commits"]["orders_bugfix"])}

    src = toyreview.sh(f"git show {gt['commits']['auth_v1']}:shop/auth.py",
                       root).stdout
    ctx = {"source": src, "lines": src.splitlines(), "n_lines": len(src.splitlines()),
           "sast_patterns": ["md5(", '" + ', "SELECT"]}

    print("═══ 分层 reward（shop/auth.py 上的评论）═══\n")
    for c in [x for x in comments if x["path"] == "shop/auth.py"][:6]:
        c2 = {**c, "resolved": c["signal"]["resolved"],
              "szz_confirmed": (c["path"], c["line"]) in szz}
        r = total_reward(c2, ctx)
        tag = "⛔ 硬闸门" if r["gated"] else f"{r['reward']:+.3f}"
        print(f"  {c['comment_id']} [{c['type']:<15}] {tag:<12} 「{c['body'][:44]}…」")
        for k in ("r1", "r2"):
            if k in r["breakdown"]:
                b = r["breakdown"][k]
                extra = b.get("why") or "；".join(b.get("reasons", [])) or "—"
                print(f"        {k}={b['score']:.2f}  {extra}")

    print("\n═══ 精度优先：为什么不能最大化 F1 ⭐ ═══\n")
    print("  {:<6} {:>8} {:>9} {:>8} {:>7} {:>7} {:>12}".format(
        "阈值", "条/PR", "precision", "recall", "F1", "信任", "**实际采纳**"))
    rows = two_stage()
    for r in rows:
        print("  {:<6.2f} {:>8.2f} {:>8.0%} {:>8.0%} {:>7.2f} {:>7.0%} {:>12.2f}"
              .format(r["thr"], r["comments_per_pr"], r["precision"], r["recall"],
                      r["f1"], r["trust"], r["adopted_per_pr"]))
    best_f1 = max(rows, key=lambda r: r["f1"])
    best_ad = max(rows, key=lambda r: r["adopted_per_pr"])
    print(f"\n  这组参数下 F1 最优和采纳最优**都在 {best_f1['thr']:.2f}** —— 它们没有分离。")
    print("  ⚠️ 我原本想在这里演示「F1 最优 ≠ 产品最优」，但数据不支持这个说法。")
    print("     正确的问题不是「它们是否分离」，而是**「误报多贵时才分离」**：\n")

    fine = [i / 40 for i in range(0, 40)]
    print("  {:<12} {:>12} {:>14} {:>10}".format(
        "每条误报的信任衰减", "F1 最优阈值", "实际采纳最优阈值", "差距"))
    for decay in (0.95, 0.85, 0.75, 0.60, 0.45):
        rs = two_stage(filter_thresholds=fine, trust_decay=decay)
        tf = max(rs, key=lambda r: r["f1"])["thr"]
        ta = max(rs, key=lambda r: r["adopted_per_pr"])["thr"]
        print("  {:<12.2f} {:>12.3f} {:>14.3f} {:>10.3f}".format(
            decay, tf, ta, ta - tf))
    print("\n  → **差距随误报代价单调变化，而 F1 最优阈值岿然不动（永远 0.675）。**")
    print("     衰减 0.95（误报几乎无害）→ 产品最优 0.075，**比 F1 宽松 0.6**")
    print("       （既然误报不疼，就该把召回拉满）")
    print("     衰减 0.75 → 恰好重合（这只是巧合，不是规律）")
    print("     衰减 0.45（一条误报让用户少读一半）→ 产品最优 0.825，比 F1 更严")
    print("  ⭐ **F1 根本不知道一次误报值多少钱** —— 它在任何代价下都给同一个答案。")
    print("  ⭐ 所以要问的不是「用不用 F1」，是**「一条误报到底让用户少看了多少条」** ——")
    print("     这个数要从线上量（BitsAI-CR 的 Outdated Rate 就是干这个的），")
    print("     量出来之后，阈值不是调参调出来的，是**算出来的**。")
    print("     顺带解释了他们为什么把 ReviewFilter 做成独立一段：")
    print("     它的阈值要按产品目标单独定，不该和 RuleChecker 的召回耦合。")

    print("\n═══ reward hacking 监控 ═══\n")
    for k, v in hack_signals(comments).items():
        print(f"  {k:<38} {v:.2f}")
    print("\n  这三个指标要**按周画趋势**。任何一个开始上涨，")
    print("  就说明模型在学「怎么让 grader 满意」而不是「怎么发现问题」。")
    print("  配套的硬护栏：每条评论必须给出**可定位的行号 + 可证伪的断言**，")
    print("  『考虑加个测试』这种既不可定位也不可证伪的话直接在 r1 层砍掉。")
