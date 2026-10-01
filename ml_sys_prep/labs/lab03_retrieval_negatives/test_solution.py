"""Lab 03 测试。跑法: python3 test_solution.py  (也兼容 pytest)"""

import math
import sys

from solution import (
    DENOISE_TAU,
    build_corpus,
    build_large_corpus,
    cascade,
    dot,
    infonce_grad,
    infonce_loss,
    mine_hard_negatives,
    rank_of,
    softmax,
    train_query,
    truncated_dot,
)

POS, UNLAB = "labeled_positive", "unlabeled_relevant"


def _negs(docs, prefix, n):
    return [docs[d] for d in sorted(docs) if d.startswith(prefix)][:n]


def test_softmax_is_a_distribution():
    p = softmax([3.0, 1.0, -2.0, 10.0])
    assert abs(sum(p) - 1.0) < 1e-12
    assert all(x >= 0 for x in p)
    assert p[3] == max(p)


def test_infonce_decreases_when_positive_scores_higher():
    q, docs = build_corpus()
    negs = _negs(docs, "hard_neg", 6)
    loss_before = infonce_loss(q, docs[POS], negs)
    q_after = train_query(q, docs[POS], negs)
    assert infonce_loss(q_after, docs[POS], negs) < loss_before


def test_hard_negatives_carry_more_gradient_than_random():
    """本 lab 的第一个题眼:easy negative 的梯度趋近 0。"""
    q, docs = build_corpus()
    easy, hard = _negs(docs, "easy_neg", 6), _negs(docs, "hard_neg", 6)
    g_easy = infonce_grad(q, docs[POS], easy)
    g_hard = infonce_grad(q, docs[POS], hard)
    n_easy = math.sqrt(sum(x * x for x in g_easy))
    n_hard = math.sqrt(sum(x * x for x in g_hard))
    assert n_hard > 10 * n_easy, "hard 的梯度范数应远大于 easy: {:.4f} vs {:.4f}".format(
        n_hard, n_easy)
    assert infonce_loss(q, docs[POS], easy) < infonce_loss(q, docs[POS], hard)


def test_naive_mining_picks_up_the_false_negative():
    """未标注但相关的文档会排进 top-k,被当作负例。"""
    q, docs = build_corpus()
    assert UNLAB in mine_hard_negatives(q, docs, POS, top_k=6)


def test_false_negative_contamination_hurts_the_relevant_doc():
    """第二个题眼:污染训练把真正相关的文档推走。"""
    q, docs = build_corpus()
    before = rank_of(q, docs, UNLAB)
    dirty = mine_hard_negatives(q, docs, POS, top_k=6)
    q_dirty = train_query(q, docs[POS], [docs[d] for d in dirty])
    after = rank_of(q_dirty, docs, UNLAB)
    assert after > before, "污染后排名应当变差: {} -> {}".format(before, after)


def test_denoising_protects_the_false_negative():
    """第三个题眼:一个 tau 就能挡住,而且规则不依赖「知道谁是假负例」。"""
    q, docs = build_corpus()
    clean = mine_hard_negatives(q, docs, POS, top_k=6, denoise_tau=DENOISE_TAU)
    assert UNLAB not in clean

    dirty = mine_hard_negatives(q, docs, POS, top_k=6)
    q_dirty = train_query(q, docs[POS], [docs[d] for d in dirty])
    q_clean = train_query(q, docs[POS], [docs[d] for d in clean])
    assert rank_of(q_clean, docs, UNLAB) < rank_of(q_dirty, docs, UNLAB)
    # 去噪不能以牺牲正例为代价
    assert rank_of(q_clean, docs, POS) == 1


def test_denoise_tau_separates_false_negative_from_true_hard_negatives():
    """tau 之所以可用,是因为假负例与正例的相似度显著高于真负例。"""
    _, docs = build_corpus()
    sim_unlab = dot(docs[POS], docs[UNLAB])
    sim_hard_max = max(dot(docs[POS], docs[d])
                       for d in docs if d.startswith("hard_neg"))
    assert sim_hard_max < DENOISE_TAU < sim_unlab


def test_truncated_dot_matches_full_dot_at_full_dim():
    _, docs = build_corpus()
    a, b = docs[POS], docs[UNLAB]
    assert abs(truncated_dot(a, b, len(a)) - dot(a, b)) < 1e-12


def test_cascade_trades_recall_for_cost():
    """第四个题眼:截断维度省的是全库成本,但截过头会掉召回。"""
    q, docs, gold = build_large_corpus()
    r_full, c_full = cascade(q, docs, gold, 64, 10)
    r_16, c_16 = cascade(q, docs, gold, 16, 50)
    r_4, c_4 = cascade(q, docs, gold, 4, 50)

    assert r_full == 1.0
    assert r_16 == 1.0 and c_16 < 0.4 * c_full, "1/4 维应当近乎免费"
    assert r_4 < r_16, "截到 1/16 维必须看到召回下降"


def test_bigger_shortlist_buys_back_recall():
    """精排只作用于 k 条,所以加大 shortlist 是便宜的补救。"""
    q, docs, gold = build_large_corpus()
    r_small, c_small = cascade(q, docs, gold, 8, 50)
    r_big, c_big = cascade(q, docs, gold, 8, 200)
    assert r_big > r_small
    assert c_big < 2 * c_small, "加大 shortlist 的成本增幅应当有限"


def _run():
    tests = [v for k, v in sorted(globals().items()) if k.startswith("test_")]
    failed = 0
    for t in tests:
        try:
            t()
            print("  PASS  " + t.__name__)
        except AssertionError as e:
            failed += 1
            print("  FAIL  " + t.__name__ + " :: " + str(e))
    print("\n{}/{} passed".format(len(tests) - failed, len(tests)))
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(_run())
