"""Drill B · 向量检索:批量 top-k、Matryoshka 截断、两段级联

⏱ timebox 20 分钟  ｜  概率评级:★★★★☆

为什么是这道题:Exa 自己训 embedding、自建 web-scale 向量库,并且明确用了
Matryoshka(2048 维截到 256 维,内存降 20x)。「写一个向量检索」是最直接的
「related to what we do at Exa」。

冷写协议:
    cp drill_b_vector_search.py scratch.py  -> 删实现体 -> 计时 20 分钟

面试时必须能顺口说出来的:
    * 归一化之后,cosine 相似度就是点积 -> 一次矩阵乘搞定全部 query x doc
    * 取 top-k 用 argpartition 是 O(n),argsort 是 O(n log n);
      只在选出的 k 个里再排序
    * Matryoshka: 前 m 维本身就是一个可用 embedding -> 用它做全库粗筛,
      再用全维精排 top-k。省的是**全库**扫描成本
    * 精排只作用于 shortlist,所以「加大 shortlist」是便宜的召回补救
"""

import numpy as np

# ==========================================================================
# COLD-WRITE ZONE 开始
# ==========================================================================


def l2_normalize(x: np.ndarray, axis: int = -1, eps: float = 1e-12) -> np.ndarray:
    """按行归一化。eps 防止零向量除零。"""
    norm = np.linalg.norm(x, axis=axis, keepdims=True)
    return x / np.maximum(norm, eps)


def cosine_scores(queries: np.ndarray, docs: np.ndarray) -> np.ndarray:
    """(Q, D) 相似度矩阵。归一化后 cosine == 点积。

    queries: (Q, dim)   docs: (D, dim)   ->  (Q, D)
    """
    return l2_normalize(queries) @ l2_normalize(docs).T


def top_k(scores: np.ndarray, k: int):
    """按行取 top-k。返回 (indices, values),都按分数降序。

    用 argpartition 先 O(n) 选出 k 个候选,再只对这 k 个排序。
    k >= D 时退化为全排序。
    """
    q, d = scores.shape
    k = min(k, d)
    # argpartition 保证第 -k 位左边都不大于右边;取最后 k 列即 top-k(无序)
    idx = np.argpartition(-scores, kth=k - 1, axis=1)[:, :k]
    vals = np.take_along_axis(scores, idx, axis=1)
    order = np.argsort(-vals, axis=1)          # 只对 k 个排序
    idx = np.take_along_axis(idx, order, axis=1)
    vals = np.take_along_axis(vals, order, axis=1)
    return idx, vals


def search(queries: np.ndarray, docs: np.ndarray, k: int = 10):
    """朴素全量检索:全维打分 + top-k。"""
    return top_k(cosine_scores(queries, docs), k)


def matryoshka_search(queries: np.ndarray, docs: np.ndarray, coarse_dim: int,
                      shortlist_k: int, final_k: int = 10):
    """两段级联:前 coarse_dim 维全库粗筛 -> shortlist 上用全维精排。

    关键实现细节:截断之后**必须重新归一化**,因为前 m 维的范数不是 1。
    返回 (indices, values, cost),cost 按乘加次数计。
    """
    n_docs, dim = docs.shape
    coarse_dim = min(coarse_dim, dim)
    shortlist_k = min(shortlist_k, n_docs)

    # --- 粗筛:只用前 coarse_dim 维 ---
    cand_idx, _ = top_k(
        cosine_scores(queries[:, :coarse_dim], docs[:, :coarse_dim]),
        shortlist_k)

    # --- 精排:每个 query 只在自己的 shortlist 上用全维打分 ---
    qn = l2_normalize(queries)
    dn = l2_normalize(docs)
    final_k = min(final_k, shortlist_k)
    out_idx = np.empty((len(queries), final_k), dtype=np.int64)
    out_val = np.empty((len(queries), final_k), dtype=float)
    for qi in range(len(queries)):
        cands = cand_idx[qi]
        s = dn[cands] @ qn[qi]
        order = np.argsort(-s)[:final_k]
        out_idx[qi] = cands[order]
        out_val[qi] = s[order]

    cost = len(queries) * (n_docs * coarse_dim + shortlist_k * dim)
    return out_idx, out_val, cost


def recall_vs_exact(approx_idx: np.ndarray, exact_idx: np.ndarray) -> float:
    """近似检索相对精确检索的 recall(逐 query 求交集比例再平均)。"""
    per_q = [len(set(a.tolist()) & set(e.tolist())) / len(e)
             for a, e in zip(approx_idx, exact_idx)]
    return float(np.mean(per_q))


def apply_matryoshka_profile(x: np.ndarray, decay: float = 0.035) -> np.ndarray:
    """把「各维等权」的向量改造成「前缀信息量更大」的向量。

    这是在**模拟** Matryoshka 训练的效果:训练时对每个前缀长度都算一次
    损失,模型于是学会把最重要的信息压进前面的维度。
    这里用一条指数衰减的每维权重来近似同样的结构。

    面试要点:前缀可截断**不是向量的天然性质**,是训练目标带来的。
    对一个普通 embedding 直接砍维度,召回会掉得很惨(见 _tests 的对照)。
    """
    dim = x.shape[-1]
    weights = np.exp(-decay * np.arange(dim))
    return x * weights


# ==========================================================================
# COLD-WRITE ZONE 结束
# ==========================================================================


def _tests():
    rng = np.random.default_rng(0)
    D, DIM, Q = 4000, 128, 16
    docs = rng.normal(size=(D, DIM))
    # 让 query 有真实近邻:从若干文档加噪声派生
    anchors = rng.choice(D, size=Q, replace=False)
    queries = docs[anchors] + 0.35 * rng.normal(size=(Q, DIM))

    # --- 归一化 ---
    n = l2_normalize(docs)
    assert np.allclose(np.linalg.norm(n, axis=1), 1.0)
    assert np.allclose(l2_normalize(np.zeros((2, 4))), 0.0)  # 零向量不炸

    # --- cosine 与手算一致 ---
    s = cosine_scores(queries[:3], docs[:5])
    for i in range(3):
        for j in range(5):
            man = (queries[i] @ docs[j] /
                   (np.linalg.norm(queries[i]) * np.linalg.norm(docs[j])))
            assert abs(s[i, j] - man) < 1e-10
    assert (s <= 1.0 + 1e-9).all() and (s >= -1.0 - 1e-9).all()

    # --- top_k 与全排序一致 ---
    full = cosine_scores(queries, docs)
    idx, vals = top_k(full, 10)
    ref = np.argsort(-full, axis=1)[:, :10]
    assert (idx == ref).all(), "top_k 应与 argsort 结果一致"
    assert (np.diff(vals, axis=1) <= 1e-12).all(), "必须降序"
    # 每个 query 命中自己的 anchor
    assert all(anchors[i] in idx[i] for i in range(Q))

    # k 超过文档数不应崩
    small_idx, _ = top_k(full[:, :5], 50)
    assert small_idx.shape == (Q, 5)

    # --- 级联:普通 embedding vs Matryoshka 式 embedding 对照 ---
    m_docs = apply_matryoshka_profile(docs)
    m_queries = apply_matryoshka_profile(queries)

    exact_idx, _ = search(queries, docs, k=10)
    m_exact_idx, _ = search(m_queries, m_docs, k=10)
    full_cost = Q * D * DIM

    print("  截断粗筛的召回:普通 embedding vs Matryoshka 式(shortlist=100)")
    print("  {:<12}{:<16}{:<18}{}".format(
        "coarse_dim", "普通 recall", "Matryoshka recall", "成本"))
    for cdim in (128, 64, 32, 16, 8):
        sk = 10 if cdim == DIM else 100
        a_idx, _, cost = matryoshka_search(queries, docs, cdim, sk, final_k=10)
        rec = recall_vs_exact(a_idx, exact_idx)
        m_idx, _, _ = matryoshka_search(m_queries, m_docs, cdim, sk, final_k=10)
        m_rec = recall_vs_exact(m_idx, m_exact_idx)
        print("  {:<12}{:<16.3f}{:<18.3f}{:>9}  ({:>3.0f}% of full)".format(
            cdim, rec, m_rec, cost, 100 * cost / full_cost))
        if cdim == DIM:
            assert rec == 1.0 and m_rec == 1.0, "全维粗筛必须无损"

    # 同样截到 1/4 维,Matryoshka 式明显更抗截断
    r32 = recall_vs_exact(matryoshka_search(queries, docs, 32, 100)[0], exact_idx)
    m32 = recall_vs_exact(
        matryoshka_search(m_queries, m_docs, 32, 100)[0], m_exact_idx)
    assert m32 > r32, "Matryoshka 式应当更抗截断: {:.3f} vs {:.3f}".format(m32, r32)

    # 截断越狠召回越差(单调性,允许同分)
    r64 = recall_vs_exact(matryoshka_search(queries, docs, 64, 100)[0], exact_idx)
    r8 = recall_vs_exact(matryoshka_search(queries, docs, 8, 100)[0], exact_idx)
    assert r64 >= r8, "更多维度不应更差"

    # 加大 shortlist 能买回召回
    r_small = recall_vs_exact(matryoshka_search(queries, docs, 16, 30)[0], exact_idx)
    r_big = recall_vs_exact(matryoshka_search(queries, docs, 16, 400)[0], exact_idx)
    assert r_big >= r_small
    print("\n  普通 embedding, coarse_dim=16: shortlist 30 -> 400 召回 {:.3f} -> {:.3f}"
          .format(r_small, r_big))
    print("  -> 两条补救路径:把 embedding 训成可截断的(Matryoshka),")
    print("     或者留着普通 embedding 但加大 shortlist。前者省内存,后者省训练。")
    print("  全部断言通过")


if __name__ == "__main__":
    print("Drill B · 向量检索与 Matryoshka 级联")
    _tests()
    print("""
面试追问预演:
  Q 为什么不用 argsort?
  A argpartition 是 O(n) 选出 top-k,argsort 是 O(n log n) 排全部。
    D 上百万时差距很大,而我们只关心前 k 个的顺序。

  Q 这个还不是 ANN,真实系统怎么做?
  A 这里是精确暴力检索,复杂度 O(N·dim)。web 规模要上 ANN:
    HNSW(图索引,高召回低延迟,内存大)或 IVF-PQ(倒排+量化,十亿级、
    内存受限时用)。Matryoshka 截断可以和两者叠加 —— 它降的是每次
    距离计算的维度,ANN 降的是要算多少次。

  Q 截断为什么要重新归一化?
  A 前 m 维的子向量范数不是 1,不重新归一化就不是 cosine 了,
    会偏向那些「能量集中在前 m 维」的文档。

  Q 怎么选 coarse_dim?
  A 不是猜,是画 recall-成本曲线:固定 shortlist 扫 coarse_dim,
    找召回开始掉的拐点。掉了还可以用更大的 shortlist 买回来,
    因为精排只作用于 k 条。
""")
