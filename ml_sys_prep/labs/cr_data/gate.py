"""质量把关：**过滤噪声 + 校准你的自动信号**。

两步，顺序不能反：

  第一步 **过滤**：机器人、纯风格、提问、夸奖、过期引用、重复。
    这些在真实 PR 语料里占大头 —— 不滤掉，模型学到的是「怎么写 nit」。

  第二步 **校准**：你的自动信号（采纳率）到底有多准？
    ⭐ **这一步大多数人跳过，而它决定了后面所有训练的上限。**
    「代码后来变了」≠「因为你的评论才变的」——
    评论恰好落在一行因别的原因被改的代码上，就会被记成采纳。

    python gate.py
"""
from __future__ import annotations

import re
from collections import Counter

import numpy as np

import signals
import toyreview

BOT_SUFFIXES = ("[bot]", "-bot", "_bot")
KNOWN_BOTS = {"codecov", "sonarqube", "dependabot", "renovate", "coveralls",
              "github-actions", "stale", "greptile", "coderabbitai"}
NIT_RE = re.compile(r"^\s*(nit|nitpick|minor|style)\s*[:\-]", re.I)
PRAISE_RE = re.compile(r"^\s*(nice|great|lgtm|looks good|👍|awesome|thanks)", re.I)
QUESTION_ONLY = re.compile(r"^[^.!]*\?\s*$")


# ─────────────────────────────────────────── 第一步：过滤
def is_bot(author: str) -> bool:
    a = author.lower()
    return (any(a.endswith(s) for s in BOT_SUFFIXES)
            or a.split("[")[0] in KNOWN_BOTS)


def classify(c: dict) -> str:
    """**只用评论本身**判类型（真实场景里这一层可以是个小分类器）。

    Atlassian 的 comment ranker 就是这么做的：**只喂评论文本**给 ModernBERT，
    标签是二元的 code-resolution outcome，就把 CRR 拉到 40–45%（人类 ~45%）。
    说明**评论的措辞本身就高度预测它会不会被采纳** —— 你甚至不需要看代码。
    """
    if is_bot(c["author"]):
        return "bot"
    b = c["body"].strip()
    if NIT_RE.match(b):
        return "nit_style"
    if PRAISE_RE.match(b):
        return "praise"
    if QUESTION_ONLY.match(b):
        return "question"
    return "substantive"


def dedup_comments(comments: list, thr: float = 0.35) -> tuple:
    """同一个 (文件, 行附近) 上语义重复的评论只留一条。

    **真实 PR 里多人重复指出同一问题非常常见** —— 不去重的话，
    高频问题会在训练集里被过度加权，模型学会反复说同一句话。
    这里用词袋 Jaccard；真实规模用 embedding + LSH。
    """
    def toks(s):
        return set(re.findall(r"[a-z]{3,}", s.lower()))
    kept, dropped = [], []
    for c in comments:
        dup = next((k for k in kept
                    if k["path"] == c["path"] and abs(k["line"] - c["line"]) <= 3
                    and len(toks(k["body"]) & toks(c["body"]))
                    / max(1, len(toks(k["body"]) | toks(c["body"]))) >= thr), None)
        (dropped if dup else kept).append(
            {**c, "_dup_of": dup["comment_id"]} if dup else c)
    return kept, dropped


def gate(comments: list) -> dict:
    stages = {"raw": list(comments)}
    x = [c for c in comments if not is_bot(c["author"])]
    stages["去机器人"] = list(x)
    x = [c for c in x if classify(c) == "substantive"]
    stages["去 nit/夸奖/纯提问"] = list(x)
    x, dropped = dedup_comments(x)
    stages["去重复"] = list(x)
    return {"stages": stages, "dropped_dups": dropped, "final": x}


# ─────────────────────────────────────────── 第二步：校准自动信号
def calibrate(comments: list) -> dict:
    """把自动信号（resolved）当成对「有没有用」的预测，量它的 precision / recall。

    这一步需要**一批人工标注**（真实场景里就是 BitsAI-CR 的
    「每天抽样 ≤10%、每周人工标注」）。这里用 `_gt_useful` 当人工标注的替身。
    """
    y = np.array([c["_gt_useful"] for c in comments])
    p = np.array([c["signal"]["resolved"] for c in comments])
    tp = int(((p == 1) & (y == 1)).sum()); fp = int(((p == 1) & (y == 0)).sum())
    fn = int(((p == 0) & (y == 1)).sum()); tn = int(((p == 0) & (y == 0)).sum())
    prec = tp / max(1, tp + fp); rec = tp / max(1, tp + fn)
    return {"tp": tp, "fp": fp, "fn": fn, "tn": tn, "precision": prec,
            "recall": rec, "f1": 2 * prec * rec / max(1e-9, prec + rec),
            "false_positives": [c["comment_id"] for c in comments
                                if c["signal"]["resolved"] and not c["_gt_useful"]],
            "false_negatives": [c["comment_id"] for c in comments
                                if not c["signal"]["resolved"] and c["_gt_useful"]]}


if __name__ == "__main__":
    built = toyreview.build()
    comments = signals.annotate(built["root"], built["comments"])

    print("═══ 第一步：过滤漏斗 ═══\n")
    g = gate(comments)
    prev = None
    for name, xs in g["stages"].items():
        delta = "" if prev is None else f"  (−{prev - len(xs)})"
        print(f"  {name:<22} {len(xs):>3} 条{delta}")
        prev = len(xs)
    print("\n  ⚠️ 语义去重：词袋 Jaccard **抓不到改写**")
    print("  {:<8} {:<6} {}".format("阈值", "命中", "配对"))
    for thr in (0.35, 0.25, 0.15, 0.10):
        _, dd = dedup_comments(g["stages"]["去 nit/夸奖/纯提问"], thr)
        pairs = "、".join(f"{d['comment_id']}≈{d['_dup_of']}" for d in dd) or "—"
        print(f"  {thr:<8.2f} {len(dd):<6} {pairs}")
    print("  真值：cm18 是 cm11 的改写（都在说 MD5），cm19 是 cm01 的改写（都在说 None）。")
    print("  → 阈值 0.35 一条都抓不到；降到 0.10 才抓到，但那时误伤风险已经很高。")
    print("    **原因**：两条评论说的是同一件事，用的却是完全不同的词。")
    print("    词法方法在这里天然失效，**语义去重必须用 embedding**"
          "（真实规模再加 LSH 分桶）。")

    kept_useful = sum(c["_gt_useful"] for c in g["final"])
    print(f"\n  过滤后有价值比例：{kept_useful}/{len(g['final'])} = "
          f"{kept_useful/len(g['final']):.0%}"
          f"（过滤前 {sum(c['_gt_useful'] for c in comments)}/{len(comments)} = "
          f"{sum(c['_gt_useful'] for c in comments)/len(comments):.0%}）")

    print("\n═══ 第二步：校准采纳信号 ⭐ ═══\n")
    cal = calibrate(comments)
    print(f"  把「代码后来变了」当成「这条评论有用」的预测：")
    print(f"    precision {cal['precision']:.0%}   recall {cal['recall']:.0%}   "
          f"F1 {cal['f1']:.2f}")
    print(f"    TP={cal['tp']}  FP={cal['fp']}  FN={cal['fn']}  TN={cal['tn']}")
    print(f"\n  **假阳性**（代码变了但评论没用）：{cal['false_positives']}")
    for cid in cal["false_positives"]:
        c = next(x for x in comments if x["comment_id"] == cid)
        print(f"    {cid} [{c['type']}] 「{c['body'][:56]}…」")
    print("  → 机制：评论恰好落在**因别的原因被改动**的那一行上。")
    print("    最危险的是其中事实错误的那条 —— 它被自动信号盖章成了「有用」，")
    print("    直接进训练集就是在教模型编造听起来专业的错误结论。")

    print(f"\n  **假阴性**（有用但代码没变）：{cal['false_negatives']}")
    for cid in cal["false_negatives"]:
        c = next(x for x in comments if x["comment_id"] == cid)
        print(f"    {cid} [{c['type']}] 「{c['body'][:56]}…」")
    print("  → 这条评论是对的，作者当时没改；三周后它变成了一个真 bug"
          "（见 signals.py 的 SZZ 部分）。")
    print("    **采纳信号会系统性低估「作者当时不认可但其实正确」的评论。**")

    print("\n  ⭐ 结论：采纳信号是**有偏的 proxy**，不能直接当 label 用。")
    print("     正确用法是「大规模弱标签 + 小规模人工校准」——")
    print("     BitsAI-CR 每天抽 ≤10% 人工标注、每周汇总，就是在做这件事。")
