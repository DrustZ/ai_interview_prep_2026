"""Drill A · 检索评测指标(recall@k / precision@k / MRR / nDCG / MAP)

⏱ timebox 20 分钟  ｜  概率评级:★★★★★(ML Evals 岗第一顺位)

为什么是这道题:Exa 的 evals-at-exa 讲的就是「怎么给搜索结果打分」。
他们用 LLM 对 (query, result) 打 0–1 的**分级**相关性,分级相关性最自然的
指标就是 nDCG。这题几乎是他们日常工作的最小复现。

冷写协议:
    cp drill_a_retrieval_metrics.py scratch.py
    删掉 COLD-WRITE ZONE 里的实现体(保留签名和 docstring)
    计时 20 分钟从记忆写 -> python3 scratch.py -> 红了就修,不看参考

面试时必须能顺口说出来的:
    * nDCG 的折扣是 log2(i+1),i 从 1 开始 -> 第 1 位折扣为 1
    * IDCG 是「把相关性降序排好」的 DCG;IDCG=0 时 nDCG 定义为 0
    * MRR 只看第一个相关结果 -> 适合「有唯一正确答案」的场景
    * recall@k 的分母是**全部**相关文档数,不是 k
    * 二值相关性用 MAP/MRR,分级相关性用 nDCG
"""

import math
from typing import Dict, List, Sequence

# ==========================================================================
# COLD-WRITE ZONE 开始
# ==========================================================================


def recall_at_k(ranked: Sequence[str], relevant: Sequence[str], k: int) -> float:
    """top-k 里命中了多少比例的**全部**相关文档。

    分母是 len(relevant),不是 k —— 这是最常见的口误。
    relevant 为空时返回 0.0(而不是崩掉)。
    """
    rel = set(relevant)
    if not rel:
        return 0.0
    hit = sum(1 for d in ranked[:k] if d in rel)
    return hit / len(rel)


def precision_at_k(ranked: Sequence[str], relevant: Sequence[str], k: int) -> float:
    """top-k 里有多少比例是相关的。分母是 k(不足 k 时按实际长度)。"""
    if k <= 0:
        return 0.0
    window = ranked[:k]
    if not window:
        return 0.0
    rel = set(relevant)
    return sum(1 for d in window if d in rel) / len(window)


def reciprocal_rank(ranked: Sequence[str], relevant: Sequence[str],
                    k: int = None) -> float:
    """第一个相关结果排名的倒数;top-k 内没有相关结果则 0。"""
    rel = set(relevant)
    window = ranked if k is None else ranked[:k]
    for i, d in enumerate(window, start=1):
        if d in rel:
            return 1.0 / i
    return 0.0


def dcg_at_k(gains: Sequence[float], k: int) -> float:
    """DCG = Σ_{i=1..k} gain_i / log2(i + 1)。

    注意 i 从 1 开始,所以第 1 位的折扣是 log2(2)=1(不打折)。
    """
    return sum(g / math.log2(i + 1) for i, g in enumerate(gains[:k], start=1))


def ndcg_at_k(ranked: Sequence[str], gain_by_doc: Dict[str, float], k: int) -> float:
    """分级相关性下的归一化 DCG。

    IDCG = 把所有已知的相关性分数降序排列后取前 k 的 DCG。
    IDCG == 0(没有任何相关文档)时返回 0.0。
    """
    gains = [gain_by_doc.get(d, 0.0) for d in ranked[:k]]
    ideal = sorted(gain_by_doc.values(), reverse=True)
    idcg = dcg_at_k(ideal, k)
    if idcg == 0.0:
        return 0.0
    return dcg_at_k(gains, k) / idcg


def average_precision_at_k(ranked: Sequence[str], relevant: Sequence[str],
                           k: int) -> float:
    """AP@k:每命中一个相关文档就记一次 precision@该位置,再对相关文档总数取平均。

    分母用 min(len(relevant), k) —— 否则 k 小于相关文档数时 AP 永远拿不到 1。
    """
    rel = set(relevant)
    if not rel:
        return 0.0
    hits = 0
    acc = 0.0
    for i, d in enumerate(ranked[:k], start=1):
        if d in rel:
            hits += 1
            acc += hits / i
    denom = min(len(rel), k)
    return acc / denom if denom else 0.0


def evaluate(runs: List[dict], k: int = 10) -> Dict[str, float]:
    """对一批 query 求各指标均值。

    runs 里每项: {"ranked": [doc_id...], "gains": {doc_id: 相关性分数}}
    二值场景把 gains 的值设成 0/1 即可。
    """
    if not runs:
        return {}
    out = {"recall@k": 0.0, "precision@k": 0.0, "mrr@k": 0.0,
           "ndcg@k": 0.0, "map@k": 0.0}
    for r in runs:
        ranked, gains = r["ranked"], r["gains"]
        relevant = [d for d, g in gains.items() if g > 0]
        out["recall@k"] += recall_at_k(ranked, relevant, k)
        out["precision@k"] += precision_at_k(ranked, relevant, k)
        out["mrr@k"] += reciprocal_rank(ranked, relevant, k)
        out["ndcg@k"] += ndcg_at_k(ranked, gains, k)
        out["map@k"] += average_precision_at_k(ranked, relevant, k)
    return {m: v / len(runs) for m, v in out.items()}


# ==========================================================================
# COLD-WRITE ZONE 结束
# ==========================================================================


def _tests():
    # --- nDCG 手算校验 ---
    gains = {"a": 3.0, "b": 2.0, "c": 3.0, "d": 0.0, "e": 1.0, "f": 2.0}
    ranked = ["a", "b", "c", "d", "e", "f"]
    # DCG@6 = 3/1 + 2/log2(3) + 3/2 + 0/log2(5) + 1/log2(6) + 2/log2(7)
    expect_dcg = (3 / 1 + 2 / math.log2(3) + 3 / math.log2(4)
                  + 0 / math.log2(5) + 1 / math.log2(6) + 2 / math.log2(7))
    got = dcg_at_k([gains[d] for d in ranked], 6)
    assert abs(got - expect_dcg) < 1e-9, (got, expect_dcg)

    # 完美排序的 nDCG 必须是 1
    perfect = sorted(gains, key=lambda d: -gains[d])
    assert abs(ndcg_at_k(perfect, gains, 6) - 1.0) < 1e-12
    # 打乱后必须 <= 1
    assert ndcg_at_k(["d", "e", "f", "a", "b", "c"], gains, 6) < 1.0
    # 全不相关 -> 0
    assert ndcg_at_k(["x", "y"], {"x": 0.0, "y": 0.0}, 2) == 0.0

    # --- recall/precision ---
    r = ["d1", "d2", "d3", "d4"]
    rel = ["d2", "d4", "d9"]  # d9 不在结果里
    assert abs(recall_at_k(r, rel, 4) - 2 / 3) < 1e-12    # 分母是 3 不是 4
    assert abs(precision_at_k(r, rel, 4) - 2 / 4) < 1e-12
    assert abs(precision_at_k(r, rel, 2) - 1 / 2) < 1e-12
    assert recall_at_k(r, [], 4) == 0.0

    # --- MRR ---
    assert reciprocal_rank(["a", "b", "c"], ["b"]) == 0.5
    assert reciprocal_rank(["a", "b", "c"], ["c"], k=2) == 0.0  # 截断后没命中
    assert reciprocal_rank(["a"], ["z"]) == 0.0

    # --- AP ---
    # 命中在第 1、3 位: (1/1 + 2/3)/2
    ap = average_precision_at_k(["a", "x", "b", "y"], ["a", "b"], 4)
    assert abs(ap - (1.0 + 2 / 3) / 2) < 1e-12
    # 相关文档数 > k 时分母用 k
    ap2 = average_precision_at_k(["a", "b"], ["a", "b", "c", "d"], 2)
    assert abs(ap2 - 1.0) < 1e-12

    # --- 汇总 ---
    runs = [{"ranked": ranked, "gains": gains},
            {"ranked": perfect, "gains": gains}]
    agg = evaluate(runs, k=6)
    assert 0.0 < agg["ndcg@k"] <= 1.0
    assert abs(agg["recall@k"] - 1.0) < 1e-12  # 两次都召回了全部相关文档

    print("  全部断言通过")
    print("  示例汇总(k=6):")
    for m, v in agg.items():
        print("    {:<14}{:.4f}".format(m, v))


if __name__ == "__main__":
    print("Drill A · 检索评测指标")
    _tests()
    print("""
面试追问预演:
  Q 为什么用 nDCG 不用 precision?
  A 搜索结果的相关性是**分级**的而不是二值的,而且位置很重要 ——
    nDCG 同时处理了这两点。Exa 用 LLM 给 (query,result) 打 0–1 分,
    正好是分级相关性。

  Q nDCG 的局限?
  A ① IDCG 依赖「已知的相关文档集合」,而 web 规模下这个集合永远不完整
       -> 未标注的相关文档被当成 gain=0,系统性低估好系统(这正是 Exa
       放弃 MS Marco 式封闭评测的理由之一);
     ② 跨 query 平均会被「容易的 query」主导,要分层报告;
     ③ 折扣函数是约定俗成的,不等于真实用户的注意力衰减。

  Q recall@k 在 web 搜索里怎么算?
  A 严格意义算不了 —— 分母(全部相关文档)未知。实践中用 pooling:
    把多个系统的 top-k 并起来人工/LLM 判定,当作近似的相关集合。
""")
