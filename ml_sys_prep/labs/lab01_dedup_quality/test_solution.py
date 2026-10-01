"""Lab 01 测试。跑法: python3 test_solution.py  (也兼容 pytest)"""

import sys

from solution import (
    _permutations,
    build_corpus,
    build_quality_training,
    dedup,
    estimate_jaccard,
    jaccard,
    lsh_candidate_pairs,
    lsh_probability,
    lsh_threshold,
    minhash_signature,
    quality_score,
    shingles,
)


def test_minhash_approximates_jaccard():
    """128 个置换下,估计值与真值的绝对误差应当很小。"""
    corpus = build_corpus()
    perms = _permutations(128)
    sh = {k: shingles(v) for k, v in corpus.items()}
    sigs = {k: minhash_signature(v, perms) for k, v in sh.items()}
    ids = sorted(corpus)
    for i in range(len(ids)):
        for j in range(i + 1, len(ids)):
            a, b = ids[i], ids[j]
            true_j = jaccard(sh[a], sh[b])
            est = estimate_jaccard(sigs[a], sigs[b])
            assert abs(est - true_j) < 0.12, \
                "{} vs {}: true={:.3f} est={:.3f}".format(a, b, true_j, est)


def test_more_permutations_reduce_error():
    """签名越长,估计越准 —— 这是 MinHash 的核心权衡(精度 vs 内存)。"""
    corpus = build_corpus()
    a, b = shingles(corpus["art_original"]), shingles(corpus["art_extended"])
    true_j = jaccard(a, b)
    errs = []
    for n in (16, 256):
        perms = _permutations(n)
        est = estimate_jaccard(minhash_signature(a, perms),
                               minhash_signature(b, perms))
        errs.append(abs(est - true_j))
    assert errs[1] <= errs[0], "256 个置换的误差不应大于 16 个"


def test_lsh_threshold_formula():
    """阈值 ≈ (1/b)^(1/r),且应落在命中概率 0.5 附近。"""
    for bands, rows in [(32, 4), (16, 8), (8, 16)]:
        thr = lsh_threshold(bands, rows)
        assert abs(thr - (1.0 / bands) ** (1.0 / rows)) < 1e-9
        p = lsh_probability(thr, bands, rows)
        assert 0.4 < p < 0.8, "在阈值处命中概率应当在拐点附近,实际 {:.3f}".format(p)


def test_lsh_is_monotonic_in_similarity():
    """相似度越高,被选为候选的概率必须单调不降。"""
    prev = -1.0
    for s in (0.1, 0.3, 0.5, 0.7, 0.9, 1.0):
        p = lsh_probability(s, 32, 4)
        assert p >= prev
        prev = p


def test_lsh_recalls_the_near_duplicate_pair():
    """真正的近重复必须出现在候选集里,否则 LSH 参数选错了。"""
    corpus = build_corpus()
    perms = _permutations(128)
    sigs = {k: minhash_signature(shingles(v), perms) for k, v in corpus.items()}
    pairs = lsh_candidate_pairs(sigs, bands=32, rows=4)
    assert ("art_original", "art_reposted") in pairs


def test_over_dedup_destroys_distinct_content():
    """本 lab 的题眼:阈值压太低会把模板化但内容不同的页面删掉。"""
    corpus = build_corpus()
    _, dropped_safe = dedup(corpus, threshold=0.70)
    _, dropped_aggressive = dedup(corpus, threshold=0.50)

    safe_ids = {d for d, _, _ in dropped_safe}
    aggro_ids = {d for d, _, _ in dropped_aggressive}

    # 0.70 只去掉转载,不碰商品页
    assert "art_reposted" in safe_ids
    assert not any(i.startswith("prod") for i in safe_ids)
    # 0.50 开始误删商品页 —— 删的是产品规格这类长尾事实
    assert any(i.startswith("prod") for i in aggro_ids)
    assert len(aggro_ids) > len(safe_ids)


def test_unrelated_documents_are_never_merged():
    """完全无关的文档在任何合理阈值下都不能被判为重复。"""
    corpus = build_corpus()
    for thr in (0.85, 0.70, 0.50):
        _, dropped = dedup(corpus, threshold=thr)
        for d, w, _ in dropped:
            assert not (d == "unique_law" or w == "unique_law")


def test_quality_classifier_learns_style_not_value():
    """题眼:正样本决定偏见 —— 空洞但正式的文本排在有实质但口语的前面。"""
    w = build_quality_training()
    corpus = build_corpus()
    informal = ("ok so the bug is that malloc returns null and you never check "
                "it. i hit this on arm64 only. fix: check the return, then retry "
                "once with a smaller block. took me two days lol.")
    vacuous = ("Our comprehensive enterprise solution leverages synergistic "
               "paradigms to deliver transformative outcomes across the "
               "organizational value chain in a scalable and robust manner.")
    terse = "HTTP 429 means too many requests. Back off exponentially."

    # 它做对的部分:垃圾页确实被打了低分
    assert quality_score(corpus["spam_nav"], w) < 0.1
    # 它做错的部分:文体压过了信息价值
    assert quality_score(vacuous, w) >= quality_score(informal, w)
    # 长度偏见:极短但正确的事实被压低
    assert quality_score(terse, w) < quality_score(vacuous, w)


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
