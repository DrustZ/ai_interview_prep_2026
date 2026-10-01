"""Drill D · LLM judge 的一致率、位置偏差与系统对比(evals-at-exa 对口)

⏱ timebox 20 分钟  ｜  概率评级:★★★★☆(ML Evals 岗高度对口)

为什么是这道题:Exa 的 evals-at-exa 博客写得很具体 —— 用 GPT-4.1 做 judge、
五个维度打 0–1 分、与人类偏好一致率 easy 97% / hard 83%、pointwise 与
pairwise(ELO)、listwise 都试过而默认 pointwise。这道题就是那套东西的代码版。

冷写协议:
    cp drill_d_judge_agreement.py scratch.py -> 删实现体 -> 计时 20 分钟

四个必须能说的点:
    1. **raw agreement 会骗人**:类别不平衡时瞎猜也能很高 -> 要报 Cohen's kappa
    2. **位置偏差必须测**:同一对结果交换顺序再问一次,统计翻转率
    3. **难易分层报告**:整体 90% 可能是「简单样本 97% + 困难样本 60%」
    4. **系统对比要给置信区间**:按 query bootstrap,不是按 (query,result) 对
"""

from typing import Dict, List, Sequence, Tuple

import numpy as np

# ==========================================================================
# COLD-WRITE ZONE 开始
# ==========================================================================


def raw_agreement(a: Sequence, b: Sequence) -> float:
    """两个标注者逐项完全一致的比例。"""
    assert len(a) == len(b) and len(a) > 0
    return float(np.mean([x == y for x, y in zip(a, b)]))


def cohens_kappa(a: Sequence, b: Sequence) -> float:
    """Cohen's kappa:扣掉「碰巧一致」之后的一致率。

    kappa = (p_o - p_e) / (1 - p_e)
      p_o = 实际一致率
      p_e = 两人各自的边缘分布下随机一致的期望 = Σ_c p_a(c)·p_b(c)

    解读:<0 比瞎猜还差;0.2-0.4 一般;0.4-0.6 中等;0.6-0.8 较好;>0.8 很好。
    p_e == 1(两人都只用同一个标签)时定义为 0.0。
    """
    assert len(a) == len(b) and len(a) > 0
    labels = sorted(set(a) | set(b))
    n = len(a)
    p_o = raw_agreement(a, b)
    p_e = 0.0
    for c in labels:
        p_e += (sum(1 for x in a if x == c) / n) * (sum(1 for y in b if y == c) / n)
    if abs(1.0 - p_e) < 1e-12:
        return 0.0
    return (p_o - p_e) / (1.0 - p_e)


def position_bias_rate(forward: Sequence[str], swapped: Sequence[str]) -> float:
    """同一对候选,交换呈现顺序再判一次,统计**不自洽**的比例。

    约定:两次都用 "A"/"B" 表示「呈现在第一位/第二位的那个」。
    自洽 = 交换后判断也跟着翻转。例如正着判 A 赢,反着就该判 B 赢。
    返回 0 表示无位置偏差,0.5 表示判断与内容无关。
    """
    assert len(forward) == len(swapped) and len(forward) > 0
    flip = {"A": "B", "B": "A"}
    inconsistent = sum(
        1 for f, s in zip(forward, swapped)
        if s != flip.get(f, s)  # 平局等其他标签视为一致,不计入
    )
    return inconsistent / len(forward)


def debias_pairwise(forward: Sequence[str], swapped: Sequence[str]) -> List[str]:
    """双向判定的去偏聚合:两次一致才算数,不一致记 "tie"。

    这是最便宜也最常用的位置去偏做法 —— 代价是 judge 调用翻倍。
    返回每项的胜者,用**内容标识**表示:"first" 指正向呈现时排第一的那个。
    """
    flip = {"A": "B", "B": "A"}
    out = []
    for f, s in zip(forward, swapped):
        if f in flip and s == flip[f]:
            out.append("first" if f == "A" else "second")
        else:
            out.append("tie")
    return out


def bradley_terry(pairs: Sequence[Tuple[str, str]], iters: int = 500
                  ) -> Dict[str, float]:
    """从成对胜负拟合 Bradley-Terry 强度(MM 迭代)。

    pairs: [(winner, loser), ...]
    模型: P(i 胜 j) = p_i / (p_i + p_j)
    迭代: p_i <- W_i / Σ_{j≠i} n_ij / (p_i + p_j)
    返回归一化后的强度(和为 1),越大越强。
    """
    items = sorted({x for pair in pairs for x in pair})
    idx = {name: i for i, name in enumerate(items)}
    n = len(items)
    wins = np.zeros(n)
    counts = np.zeros((n, n))
    for w, l in pairs:
        wins[idx[w]] += 1
        counts[idx[w], idx[l]] += 1
        counts[idx[l], idx[w]] += 1

    p = np.ones(n)
    for _ in range(iters):
        new = np.empty(n)
        for i in range(n):
            denom = sum(counts[i, j] / (p[i] + p[j])
                        for j in range(n) if j != i and counts[i, j] > 0)
            new[i] = wins[i] / denom if denom > 0 else p[i]
        new = np.maximum(new, 1e-12)
        new /= new.sum()
        if np.allclose(new, p, atol=1e-12):
            p = new
            break
        p = new
    return {name: float(p[idx[name]]) for name in items}


def bootstrap_ci(per_query_scores: Sequence[float], n_boot: int = 2000,
                 alpha: float = 0.05, seed: int = 0) -> Tuple[float, float, float]:
    """按 **query** 重采样求均值的置信区间。

    重点:重采样单位必须是 query,不是 (query, result) 对 —— 同一 query 下的
    多个结果高度相关,按对重采样会把置信区间算得过窄。
    返回 (mean, lo, hi)。
    """
    x = np.asarray(per_query_scores, dtype=float)
    rng = np.random.default_rng(seed)
    means = np.array([rng.choice(x, size=len(x), replace=True).mean()
                      for _ in range(n_boot)])
    return float(x.mean()), float(np.quantile(means, alpha / 2)), \
        float(np.quantile(means, 1 - alpha / 2))


def stratified_agreement(judge: Sequence, human: Sequence,
                         difficulty: Sequence[str]) -> Dict[str, dict]:
    """按难度分层报告一致率 —— 整体数字会掩盖困难样本上的崩塌。"""
    out = {}
    for level in sorted(set(difficulty)):
        j = [x for x, d in zip(judge, difficulty) if d == level]
        h = [x for x, d in zip(human, difficulty) if d == level]
        out[level] = {"n": len(j), "agreement": raw_agreement(j, h),
                      "kappa": cohens_kappa(j, h)}
    out["overall"] = {"n": len(judge), "agreement": raw_agreement(judge, human),
                      "kappa": cohens_kappa(judge, human)}
    return out


# ==========================================================================
# COLD-WRITE ZONE 结束
# ==========================================================================


def _tests():
    # --- kappa 基本性质 ---
    a = ["rel", "rel", "irr", "irr"]
    assert raw_agreement(a, a) == 1.0 and abs(cohens_kappa(a, a) - 1.0) < 1e-12
    # 完全相反 -> kappa 为 -1
    opp = ["irr", "irr", "rel", "rel"]
    assert abs(cohens_kappa(a, opp) + 1.0) < 1e-12
    # 常数标注者 -> p_e = 1 -> 定义为 0
    assert cohens_kappa(["rel"] * 4, ["rel"] * 4) == 0.0

    # --- kappa 揭穿「高 raw agreement」的假象 ---
    # 95% 的样本是 irrelevant;judge 全判 irrelevant
    human = ["irr"] * 95 + ["rel"] * 5
    lazy = ["irr"] * 100
    assert abs(raw_agreement(lazy, human) - 0.95) < 1e-12
    assert cohens_kappa(lazy, human) == 0.0, "全判一个类别的 judge kappa 必须为 0"

    # --- 位置偏差 ---
    fwd = ["A", "A", "B", "A", "B"]
    perfect = ["B", "B", "A", "B", "A"]        # 完全自洽
    assert position_bias_rate(fwd, perfect) == 0.0
    always_first = ["A", "A", "A", "A", "A"]   # 永远选第一个 -> 严重偏差
    rate = position_bias_rate(fwd, always_first)
    assert rate > 0.5, rate
    agg = debias_pairwise(fwd, perfect)
    assert agg == ["first", "first", "second", "first", "second"]
    assert debias_pairwise(["A"], ["A"]) == ["tie"]   # 不自洽记平局

    # --- Bradley-Terry 能恢复真实排序 ---
    rng = np.random.default_rng(0)
    truth = {"sys_a": 0.6, "sys_b": 0.3, "sys_c": 0.1}
    names = list(truth)
    pairs = []
    for _ in range(3000):
        i, j = rng.choice(len(names), size=2, replace=False)
        ni, nj = names[i], names[j]
        p = truth[ni] / (truth[ni] + truth[nj])
        pairs.append((ni, nj) if rng.random() < p else (nj, ni))
    fit = bradley_terry(pairs)
    order = sorted(fit, key=lambda k: -fit[k])
    assert order == ["sys_a", "sys_b", "sys_c"], (order, fit)
    for n in names:
        assert abs(fit[n] - truth[n]) < 0.08, (n, fit[n], truth[n])

    # --- bootstrap CI ---
    scores = list(rng.normal(0.72, 0.15, size=200))
    mean, lo, hi = bootstrap_ci(scores)
    assert lo < mean < hi and (hi - lo) < 0.12
    # 样本越少区间越宽
    _, lo2, hi2 = bootstrap_ci(scores[:20])
    assert (hi2 - lo2) > (hi - lo)

    # --- 分层报告 ---
    # 模仿 Exa 报的 easy 97% / hard 83%
    j = ["rel"] * 97 + ["irr"] * 3 + ["rel"] * 83 + ["irr"] * 17
    h = ["rel"] * 100 + ["rel"] * 100
    diff = ["easy"] * 100 + ["hard"] * 100
    rep = stratified_agreement(j, h, diff)
    assert abs(rep["easy"]["agreement"] - 0.97) < 1e-9
    assert abs(rep["hard"]["agreement"] - 0.83) < 1e-9
    assert abs(rep["overall"]["agreement"] - 0.90) < 1e-9

    print("  全部断言通过\n")
    print("  懒惰 judge(全判 irrelevant,类别 95/5 不平衡):")
    print("    raw agreement = {:.2f}   kappa = {:.2f}   <- kappa 揭穿了它".format(
        raw_agreement(lazy, human), cohens_kappa(lazy, human)))
    print("\n  分层一致率(模仿 evals-at-exa 报的 easy/hard):")
    for lvl in ("easy", "hard", "overall"):
        r = rep[lvl]
        print("    {:<8} n={:<5} agreement={:.2f}".format(lvl, r["n"], r["agreement"]))
    print("    -> 整体 0.90 完全掩盖了困难样本上的 0.83")
    print("\n  Bradley-Terry 拟合: " + ", ".join(
        "{}={:.3f}(真值 {:.2f})".format(k, fit[k], truth[k]) for k in names))
    m, lo_, hi_ = bootstrap_ci(scores)
    print("  Bootstrap: mean={:.3f}  95% CI=[{:.3f}, {:.3f}]".format(m, lo_, hi_))


if __name__ == "__main__":
    print("Drill D · LLM judge 一致率与系统对比")
    _tests()
    print("""
面试追问预演:
  Q 为什么不能只报 agreement?
  A 类别不平衡时它会骗人。一个「全判不相关」的 judge 在 95/5 的数据上
    agreement 有 0.95,但 kappa 是 0 —— 它没有任何判别力。

  Q pointwise 还是 pairwise?
  A pairwise 理论上更可靠(人更擅长比较而非打绝对分),但成本是 O(n²) 且
    只给相对序、拿不到绝对分,难以跨时间追踪。pointwise 是 O(n)、可缓存、
    可以直接喂给 nDCG。Exa 就是知道 pairwise 更优仍默认 pointwise,
    这是个明确的工程取舍 —— 面试里能说出「他们知道但仍这么选」很加分。

  Q 位置偏差怎么处理?
  A 双向判定:交换顺序再问一次,只有两次自洽才采信,不一致记平局。
    代价是 judge 调用翻倍。也可以在 prompt 里要求先给理由再给结论,
    以及随机化呈现顺序后统计整体胜率。

  Q judge 本身怎么验证?
  A 用人类标注的校准集,分层报 agreement 和 kappa;定期重跑防止模型
    版本漂移。judge 换版本要当作一次「实验变量变更」,不能悄悄升级 ——
    否则历史指标不可比。

  Q 系统 A 比 B 高 2 个点,能上线吗?
  A 先看置信区间,而且 bootstrap 的重采样单位必须是 query 而不是
    (query,result) 对 —— 同 query 内的结果高度相关,按对采样会让区间
    虚假地变窄。再看分层:是全面提升还是只在简单 query 上提升。
""")
