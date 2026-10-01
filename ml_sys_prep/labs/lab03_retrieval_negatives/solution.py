"""Lab 03 · InfoNCE、hard negative 的 false-negative 陷阱、Matryoshka 级联成本

对口 06_search_post_training.md §五/§六/§九,以及 13_company_cards.md 的 Exa 卡。
纯标准库、确定性(md5 生成向量,不受 PYTHONHASHSEED 影响)。

四个可以直接带进面试的结论:
  1. easy/random negative 到后期 loss 和梯度都趋近 0,模型学不到东西;
     hard negative 才有信号 —— 这是要换 negative 的真正原因。
  2. 但 top-k 里混着**未标注的相关文档**。把它们当负例训练,会把真正相关的
     文档推走。这正是 Exa 放弃 MS Marco 式封闭评测的第一个理由:
     稀疏标注 -> 假负例。
  3. 去噪规则要**可解释且不偷看答案**:与已知正例过于相似的候选,大概率
     本身就是正例,不当负例。
  4. Matryoshka 截断维度粗筛 + 全维精排,recall 与成本的权衡是可算的;
     shortlist 变大可以买回一部分被截断损失的召回,而且很便宜。
"""

import hashlib
import math
from typing import Dict, List, Sequence, Tuple

DIM = 16  # A/B/C 用的小语料维度
TEMPERATURE = 0.10
DENOISE_TAU = 0.75  # 与正例相似度高于此值的候选不做负例(应在 dev set 上调)


# --------------------------------------------------------------------------
# 确定性向量工具
# --------------------------------------------------------------------------


def _unit(vec: List[float]) -> List[float]:
    n = math.sqrt(sum(v * v for v in vec)) or 1.0
    return [v / n for v in vec]


def _seeded_vec(name: str, dim: int = DIM) -> List[float]:
    out = []
    for i in range(dim):
        h = hashlib.md5("{}::{}".format(name, i).encode()).hexdigest()
        out.append(int(h[:8], 16) / 0xFFFFFFFF - 0.5)
    return _unit(out)


def _blend(a: Sequence[float], b: Sequence[float], w: float) -> List[float]:
    return _unit([(1 - w) * x + w * y for x, y in zip(a, b)])


def dot(a: Sequence[float], b: Sequence[float]) -> float:
    return sum(x * y for x, y in zip(a, b))


def truncated_dot(a: Sequence[float], b: Sequence[float], m: int) -> float:
    """只用前 m 维打分 —— Matryoshka 粗筛就是这么做的。"""
    return sum(a[i] * b[i] for i in range(m))


# --------------------------------------------------------------------------
# InfoNCE
# --------------------------------------------------------------------------


def softmax(scores: Sequence[float]) -> List[float]:
    m = max(scores)
    exps = [math.exp(s - m) for s in scores]
    z = sum(exps)
    return [e / z for e in exps]


def infonce_loss(q, positive, negatives, temperature: float = TEMPERATURE) -> float:
    """L = -log( exp(s+/T) / (exp(s+/T) + Σ exp(s-/T)) )"""
    scores = [dot(q, positive) / temperature]
    scores += [dot(q, n) / temperature for n in negatives]
    return -math.log(softmax(scores)[0])


def infonce_grad(q, positive, negatives, temperature: float = TEMPERATURE):
    """∂L/∂q = ( Σ_i p_i·d_i - d+ ) / T。

    直觉:把 q 拉向正例,推离**当前得分高**的候选。
    负例越 hard,它在 softmax 里的权重越大,梯度越强。
    """
    docs = [positive] + list(negatives)
    probs = softmax([dot(q, d) / temperature for d in docs])
    grad = [0.0] * len(q)
    for p, d in zip(probs, docs):
        for i in range(len(q)):
            grad[i] += p * d[i]
    return [(grad[i] - positive[i]) / temperature for i in range(len(q))]


def train_query(q0, positive, negatives, steps: int = 150, lr: float = 0.05,
                temperature: float = TEMPERATURE) -> List[float]:
    """对 query 向量做梯度下降。真实系统更新的是 encoder 参数,机制相同。"""
    q = list(q0)
    for _ in range(steps):
        g = infonce_grad(q, positive, negatives, temperature)
        q = _unit([qi - lr * gi for qi, gi in zip(q, g)])
    return q


# --------------------------------------------------------------------------
# 小语料:一个 query、一个已标注正例、一个未标注但相关的文档、一批负例
# --------------------------------------------------------------------------


def build_corpus() -> Tuple[List[float], Dict[str, List[float]]]:
    topic = _seeded_vec("topic:transformer-attention")
    other = _seeded_vec("topic:database-indexing")

    query = _blend(topic, _seeded_vec("q-noise"), 0.15)
    positive = _blend(topic, _seeded_vec("d-pos"), 0.40)

    docs: Dict[str, List[float]] = {"labeled_positive": positive}
    # 与正例讲同一件事、同样相关,但标注集里没有它 —— 假负例的真实来源
    docs["unlabeled_relevant"] = _blend(positive, _seeded_vec("d-unlab"), 0.30)
    # 主题相邻但确实不相关
    for i in range(8):
        docs["hard_neg_{}".format(i)] = _blend(
            topic, _seeded_vec("hn{}".format(i)), 0.52 + 0.01 * i)
    # 完全无关
    for i in range(6):
        docs["easy_neg_{}".format(i)] = _blend(
            other, _seeded_vec("d-easy-{}".format(i)), 0.5)
    return query, docs


def rank_of(query, docs: Dict[str, List[float]], doc_id: str) -> int:
    """1 = 最相关。"""
    return sorted(docs, key=lambda d: -dot(query, docs[d])).index(doc_id) + 1


def mine_hard_negatives(query, docs, positive_id: str, top_k: int = 6,
                        denoise_tau: float = None) -> List[str]:
    """用当前模型取 top-k 非正例作为 hard negatives(ANCE 式迭代挖掘)。

    denoise_tau: 丢弃与正例相似度 > tau 的候选。
        依据:「与已知正例极其相似的文档,大概率本身就是正例,只是没被标注」。
        注意这条规则只看 (候选, 正例) 的相似度,**不需要知道谁是假负例**。
    """
    pos_vec = docs[positive_id]
    ranked = sorted((d for d in docs if d != positive_id),
                    key=lambda d: -dot(query, docs[d]))
    picked = []
    for d in ranked:
        if denoise_tau is not None and dot(docs[d], pos_vec) > denoise_tau:
            continue
        picked.append(d)
        if len(picked) == top_k:
            break
    return picked


# --------------------------------------------------------------------------
# Matryoshka 级联(独立的大语料)
# --------------------------------------------------------------------------

LARGE_DIM = 64
LARGE_N = 2000
N_GOLD = 12


def build_large_corpus():
    topic = _seeded_vec("topic:gold", LARGE_DIM)
    query = _blend(topic, _seeded_vec("qn", LARGE_DIM), 0.10)
    docs = {}
    for i in range(N_GOLD):
        docs["gold_{}".format(i)] = _blend(
            topic, _seeded_vec("g{}".format(i), LARGE_DIM), 0.30 + 0.02 * i)
    for i in range(LARGE_N):
        docs["d{}".format(i)] = _blend(
            _seeded_vec("t{}".format(i % 40), LARGE_DIM),
            _seeded_vec("n{}".format(i), LARGE_DIM), 0.5)
    gold = [k for k in docs if k.startswith("gold_")]
    return query, docs, gold


def cascade(query, docs, gold, coarse_dim: int, shortlist_k: int,
            final_k: int = 10) -> Tuple[float, int]:
    """前 coarse_dim 维全库粗筛 -> top-k 用全维精排 -> 取 final_k。

    成本按乘加次数计: N*coarse_dim + shortlist_k*LARGE_DIM。
    """
    coarse = sorted(docs, key=lambda d: -truncated_dot(query, docs[d], coarse_dim))
    shortlist = coarse[:shortlist_k]
    final = sorted(shortlist, key=lambda d: -dot(query, docs[d]))[:final_k]
    gold_set = set(gold)
    recall = len([d for d in final if d in gold_set]) / float(final_k)
    cost = len(docs) * coarse_dim + shortlist_k * LARGE_DIM
    return recall, cost


def main():
    query, docs = build_corpus()
    pos_id, unlab_id = "labeled_positive", "unlabeled_relevant"

    print("=" * 76)
    print("A · hard negative vs random negative:梯度信号强度")
    print("=" * 76)
    easy = [docs[d] for d in sorted(docs) if d.startswith("easy_neg")][:6]
    hard = [docs[d] for d in sorted(docs) if d.startswith("hard_neg")][:6]
    for name, negs in (("easy/random", easy), ("hard", hard)):
        loss = infonce_loss(query, docs[pos_id], negs)
        g = infonce_grad(query, docs[pos_id], negs)
        gnorm = math.sqrt(sum(x * x for x in g))
        print("  {:<12} loss={:.4f}   |grad|={:.4f}".format(name, loss, gnorm))
    print("\n  -> easy negative 的 loss 和梯度都趋近 0:模型已经能轻松区分,再练无益。")
    print("     这才是「in-batch random negatives 到后期必须换 hard negatives」的原因。")

    print("\n" + "=" * 76)
    print("B · false negative 陷阱:把未标注的相关文档当负例")
    print("=" * 76)
    print("  相似度事实:")
    print("     dot(positive, unlabeled_relevant) = {:.3f}".format(
        dot(docs[pos_id], docs[unlab_id])))
    print("     max dot(positive, hard_neg_*)     = {:.3f}".format(
        max(dot(docs[pos_id], docs[d]) for d in docs if d.startswith("hard_neg"))))
    print("\n  训练前:  positive 排名={}   unlabeled_relevant 排名={}".format(
        rank_of(query, docs, pos_id), rank_of(query, docs, unlab_id)))

    dirty = mine_hard_negatives(query, docs, pos_id, top_k=6)
    print("\n  朴素挖掘 top-6: {}".format(dirty))
    print("  未标注的相关文档被当成负例了吗? {}".format(
        "是 <-- 污染" if unlab_id in dirty else "否"))
    q_dirty = train_query(query, docs[pos_id], [docs[d] for d in dirty])
    r_dirty = rank_of(q_dirty, docs, unlab_id)
    print("  训练后:  positive 排名={}   unlabeled_relevant 排名={}  <-- 被推走".format(
        rank_of(q_dirty, docs, pos_id), r_dirty))

    print("\n" + "=" * 76)
    print("C · 去噪:与已知正例过于相似的候选,不当负例")
    print("=" * 76)
    print("  规则:dot(candidate, positive) > tau={} 就跳过。".format(DENOISE_TAU))
    print("  注意这条规则不需要知道谁是假负例,只看候选与正例的相似度。")
    clean = mine_hard_negatives(query, docs, pos_id, top_k=6, denoise_tau=DENOISE_TAU)
    print("\n  去噪后 top-6: {}".format(clean))
    q_clean = train_query(query, docs[pos_id], [docs[d] for d in clean])
    r_clean = rank_of(q_clean, docs, unlab_id)
    print("  训练后:  positive 排名={}   unlabeled_relevant 排名={}  <-- 保住了".format(
        rank_of(q_clean, docs, pos_id), r_clean))
    print("\n  对照:未标注相关文档的排名  污染={}  去噪={}".format(r_dirty, r_clean))
    print("  -> 同样叫 hard negative mining,一个 tau 的差别决定了你是在提升召回,")
    print("     还是在系统性地把自己的正例训练成负例。")

    print("\n" + "=" * 76)
    print("D · Matryoshka 级联:截断维度粗筛 + 全维精排({} 文档, {} 维)".format(
        LARGE_N + N_GOLD, LARGE_DIM))
    print("=" * 76)
    lq, ldocs, lgold = build_large_corpus()
    full_cost = len(ldocs) * LARGE_DIM
    print("  {:<12}{:<12}{:<14}{}".format("coarse_dim", "shortlist", "recall@10", "成本"))
    for m, k in [(64, 10), (32, 50), (16, 50), (8, 50), (8, 200), (4, 50), (4, 200)]:
        rec, cost = cascade(lq, ldocs, lgold, m, k)
        print("  {:<12}{:<12}{:<14.2f}{:>8}  ({:>3.0f}% of full)".format(
            m, k, rec, cost, 100.0 * cost / full_cost))
    print("\n  -> 截到 1/4 维(16/64)召回不掉而成本只剩 27%;截到 1/8 开始掉;")
    print("     但把 shortlist 从 50 加到 200 能买回一部分 —— 因为精排只作用于 k 条,")
    print("     很便宜。这就是 Exa 把 2048 维截到 256 维省 20x 内存的同一个权衡。")
    print("     面试要点:降维省的是**全库扫描**成本,精排贵但只碰 top-k。")


if __name__ == "__main__":
    main()
