"""Lab 01 · MinHash/LSH 去重 + 质量分类器(参考实现)

对口 07_pretraining_data.md §六(dedup)、§七(filtering)、§十八 Q5。
纯标准库,确定性(用 md5 而不是内置 hash,避免 PYTHONHASHSEED 影响)。

三个可以直接带进面试的结论:
  1. MinHash 估计的是 Jaccard;LSH 的 banding 决定「多相似才会被当候选」,
     阈值 ≈ (1/b)^(1/r) —— 这是一个可以在白板上写出来的数;
  2. 去重不是越狠越好:模板化但内容不同的页面(商品页、API 文档)Jaccard 很高,
     激进阈值会把它们当重复删掉,删的是**信息**不是**冗余**;
  3. quality classifier 学到的是「正样本的文体」,不是「质量」。
     正样本选 Wikipedia 风格,就会系统性地扔掉口语化但高价值的内容。
"""

import hashlib
import math
import re
from typing import Dict, List, Sequence, Set, Tuple

# --------------------------------------------------------------------------
# Part A · Shingling 与 Jaccard
# --------------------------------------------------------------------------

_WORD = re.compile(r"[a-z0-9]+")
MERSENNE_61 = (1 << 61) - 1  # 大素数,做 (a*x+b) mod p 置换


def tokenize(text: str) -> List[str]:
    return _WORD.findall(text.lower())


def shingles(text: str, k: int = 5) -> Set[str]:
    """k-gram(按词)。k 越小越容易撞车,k 越大越严格。"""
    toks = tokenize(text)
    if len(toks) < k:
        return {" ".join(toks)} if toks else set()
    return {" ".join(toks[i:i + k]) for i in range(len(toks) - k + 1)}


def jaccard(a: Set[str], b: Set[str]) -> float:
    if not a and not b:
        return 1.0
    return len(a & b) / len(a | b)


# --------------------------------------------------------------------------
# Part B · MinHash
# --------------------------------------------------------------------------


def _stable_hash(s: str) -> int:
    """确定性 64-bit hash。生产里用 xxhash/murmur,这里用 md5 保证跨进程一致。"""
    return int(hashlib.md5(s.encode("utf-8")).hexdigest()[:16], 16)


def _permutations(num_perm: int, seed: int = 0) -> List[Tuple[int, int]]:
    """生成 num_perm 组 (a, b),用于 h_i(x) = (a*x + b) mod p。"""
    out = []
    for i in range(num_perm):
        a = _stable_hash("a{}:{}".format(seed, i)) % (MERSENNE_61 - 1) + 1
        b = _stable_hash("b{}:{}".format(seed, i)) % MERSENNE_61
        out.append((a, b))
    return out


def minhash_signature(sh: Set[str], perms: Sequence[Tuple[int, int]]) -> List[int]:
    """签名第 i 位 = 所有 shingle 在第 i 个置换下的最小值。"""
    if not sh:
        return [0] * len(perms)
    hashed = [_stable_hash(s) % MERSENNE_61 for s in sh]
    sig = []
    for a, b in perms:
        sig.append(min((a * h + b) % MERSENNE_61 for h in hashed))
    return sig


def estimate_jaccard(sig_a: Sequence[int], sig_b: Sequence[int]) -> float:
    """签名对应位相等的比例,是 Jaccard 的无偏估计。"""
    same = sum(1 for x, y in zip(sig_a, sig_b) if x == y)
    return same / len(sig_a)


# --------------------------------------------------------------------------
# Part C · LSH banding
# --------------------------------------------------------------------------


def lsh_threshold(bands: int, rows: int) -> float:
    """S 曲线拐点。白板上能写出这个式子,面试就赢了一半。

    一对文档在某个 band 上完全相同的概率 = s^r;
    至少一个 band 命中 = 1 - (1 - s^r)^b;拐点约在 (1/b)^(1/r)。
    """
    return (1.0 / bands) ** (1.0 / rows)


def lsh_probability(similarity: float, bands: int, rows: int) -> float:
    return 1.0 - (1.0 - similarity ** rows) ** bands


def lsh_candidate_pairs(
    signatures: Dict[str, List[int]], bands: int, rows: int
) -> Set[Tuple[str, str]]:
    """把签名切成 bands 个 band,同 band 同桶即候选对。"""
    assert bands * rows <= len(next(iter(signatures.values())))
    buckets: Dict[Tuple[int, str], List[str]] = {}
    for doc_id, sig in signatures.items():
        for band in range(bands):
            chunk = tuple(sig[band * rows:(band + 1) * rows])
            key = (band, hashlib.md5(str(chunk).encode()).hexdigest())
            buckets.setdefault(key, []).append(doc_id)
    pairs = set()
    for members in buckets.values():
        if len(members) < 2:
            continue
        for i in range(len(members)):
            for j in range(i + 1, len(members)):
                pairs.add(tuple(sorted((members[i], members[j]))))
    return pairs


def dedup(
    docs: Dict[str, str],
    threshold: float,
    num_perm: int = 128,
    bands: int = 32,
    rows: int = 4,
    k: int = 5,
) -> Tuple[List[str], List[Tuple[str, str, float]]]:
    """LSH 找候选 -> 精确 Jaccard 复核 -> 保留每个重复簇的一份。

    返回 (保留的 doc_id, 被判为重复的 (dropped, kept, jaccard) 列表)。
    """
    perms = _permutations(num_perm)
    sh = {d: shingles(t, k) for d, t in docs.items()}
    sigs = {d: minhash_signature(s, perms) for d, s in sh.items()}

    dropped = []
    kept: List[str] = []
    removed: Set[str] = set()
    cands = lsh_candidate_pairs(sigs, bands, rows)

    # 精确复核:LSH 只负责生成候选,判定必须用真 Jaccard(这一步不能省)
    dup_of: Dict[str, Tuple[str, float]] = {}
    for a, b in sorted(cands):
        j = jaccard(sh[a], sh[b])
        if j >= threshold:
            loser, winner = (b, a) if a < b else (a, b)
            if loser not in dup_of:
                dup_of[loser] = (winner, j)

    for doc_id in sorted(docs):
        if doc_id in dup_of:
            removed.add(doc_id)
            dropped.append((doc_id, dup_of[doc_id][0], dup_of[doc_id][1]))
        else:
            kept.append(doc_id)
    return kept, dropped


# --------------------------------------------------------------------------
# Part D · 质量分类器:正样本决定了过滤器的偏见
# --------------------------------------------------------------------------

STOPWORDS = {"the", "a", "an", "of", "and", "to", "in", "is", "it", "for",
             "that", "this", "with", "as", "on", "was", "by", "are", "be"}
BOILERPLATE = ("click here", "sign up", "cookie", "subscribe", "advertisement",
               "all rights reserved", "buy now")


def features(text: str) -> List[float]:
    toks = tokenize(text)
    n = max(1, len(toks))
    avg_len = sum(len(t) for t in toks) / n
    stop_frac = sum(1 for t in toks if t in STOPWORDS) / n
    digit_frac = sum(1 for t in toks if t.isdigit()) / n
    lower = text.lower()
    boiler = sum(1 for b in BOILERPLATE if b in lower)
    sent = max(1, text.count(".") + text.count("!") + text.count("?"))
    words_per_sent = n / sent
    return [avg_len / 10.0, stop_frac, digit_frac, boiler / 3.0,
            min(words_per_sent, 40) / 40.0, min(n, 200) / 200.0]


def train_logistic(X: List[List[float]], y: List[int],
                   epochs: int = 4000, lr: float = 0.5) -> List[float]:
    """极简 logistic regression(纯 Python),含偏置项。"""
    dim = len(X[0]) + 1
    w = [0.0] * dim
    for _ in range(epochs):
        grad = [0.0] * dim
        for xi, yi in zip(X, y):
            feats = [1.0] + xi
            z = sum(wj * fj for wj, fj in zip(w, feats))
            p = 1.0 / (1.0 + math.exp(-max(-30.0, min(30.0, z))))
            err = p - yi
            for j in range(dim):
                grad[j] += err * feats[j]
        for j in range(dim):
            w[j] -= lr * grad[j] / len(X)
    return w


def quality_score(text: str, w: List[float]) -> float:
    feats = [1.0] + features(text)
    z = sum(wj * fj for wj, fj in zip(w, feats))
    return 1.0 / (1.0 + math.exp(-max(-30.0, min(30.0, z))))


# --------------------------------------------------------------------------
# 语料
# --------------------------------------------------------------------------

ARTICLE = ("Photosynthesis converts light energy into chemical energy stored in "
           "glucose molecules. Chloroplasts in plant cells absorb photons through "
           "chlorophyll pigments. The light dependent reactions split water and "
           "release oxygen as a byproduct of the process.")


_PRODUCT_BOILERPLATE = (
    "Product overview and technical specification sheet for the industrial "
    "sensor series. This document describes installation requirements, "
    "operating conditions, calibration intervals and the recommended "
    "maintenance schedule for facilities operating under continuous load. "
    "Please read the safety notice before installation and ensure that "
    "the mounting surface is clean, dry and free of vibration. "
)

_PRODUCT_FOOTER = (
    " Shipping worldwide from regional distribution centres. Returns accepted "
    "within thirty days of delivery in original packaging. All rights reserved."
)


def _product_page(model, voltage, weight, housing, warranty_months) -> str:
    """样板一字不差,只有中间一句规格不同 —— 真实的商品页/API 文档就长这样。"""
    spec = ("Model {} delivers {} and weighs {} with a {} housing, "
            "carrying a warranty of {} months.").format(
        model, voltage, weight, housing, warranty_months)
    return _PRODUCT_BOILERPLATE + spec + _PRODUCT_FOOTER


def build_corpus() -> Dict[str, str]:
    return {
        # 近重复族:同一篇文章的三个版本
        "art_original": ARTICLE,
        "art_reposted": ARTICLE.replace("glucose", "sugar"),  # 转载改一个词
        "art_extended": ARTICLE + (" The Calvin cycle then fixes carbon dioxide "
                                   "into organic compounds using ATP and NADPH."),
        # 模板化但内容不同:大段样板一字不差,只有规格不同。
        # 这类页面(商品页、API 文档、财报模板)是过度去重的最大受害者。
        "prod_a": _product_page("X100", "12 volts", "340 grams", "aluminium", "24"),
        "prod_b": _product_page("X200", "24 volts", "620 grams", "steel", "36"),
        # 真正独立的文档
        "unique_law": ("The doctrine of promissory estoppel prevents a party from "
                       "withdrawing a promise when the other party has reasonably "
                       "relied on it to their detriment."),
        # 垃圾页
        "spam_nav": ("Click here to sign up. Buy now. Advertisement. Cookie policy. "
                     "Subscribe. All rights reserved. Click here."),
    }


def build_quality_training():
    """正样本 = 百科式正式文本;负样本 = 导航/垃圾页。

    注意这个选择本身就是一个**设计决策**,它决定了过滤器会扔掉什么。
    """
    positives = [
        ARTICLE,
        ("The mitochondrion is an organelle that generates most of the chemical "
         "energy needed to power the biochemical reactions of the cell."),
        ("Promissory estoppel prevents a party from withdrawing a promise when "
         "another party has reasonably relied upon it."),
        ("Tectonic plates move over the asthenosphere, and their interactions "
         "produce earthquakes, volcanoes and mountain ranges over geological time."),
    ]
    negatives = [
        "Click here to sign up. Buy now. Advertisement. Subscribe. Cookie policy.",
        "Home About Contact Login Register Cart Checkout All rights reserved.",
        "BUY NOW BUY NOW limited offer click here click here 50 50 50 discount.",
        "Next page previous page page 1 2 3 4 5 6 7 8 9 10 click here.",
    ]
    X = [features(t) for t in positives + negatives]
    y = [1] * len(positives) + [0] * len(negatives)
    return train_logistic(X, y)


def main():
    corpus = build_corpus()
    perms = _permutations(128)
    sh = {d: shingles(t) for d, t in corpus.items()}
    sigs = {d: minhash_signature(s, perms) for d, s in sh.items()}

    print("=" * 74)
    print("A · MinHash 估计 vs 真实 Jaccard(128 个置换)")
    print("=" * 74)
    checks = [("art_original", "art_reposted"), ("art_original", "art_extended"),
              ("prod_a", "prod_b"), ("art_original", "unique_law")]
    for a, b in checks:
        true_j = jaccard(sh[a], sh[b])
        est = estimate_jaccard(sigs[a], sigs[b])
        print("  {:<14} vs {:<14} true={:.3f}  minhash={:.3f}  err={:+.3f}".format(
            a, b, true_j, est, est - true_j))

    print("\n" + "=" * 74)
    print("B · LSH banding:阈值由 (b, r) 决定")
    print("=" * 74)
    print("  {:<12} {:<10} {}".format("(bands,rows)", "阈值", "命中概率 @ s=0.4/0.6/0.8"))
    for bands, rows in [(32, 4), (16, 8), (8, 16)]:
        probs = "  ".join("{:.2f}".format(lsh_probability(s, bands, rows))
                          for s in (0.4, 0.6, 0.8))
        print("  {:<12} {:<10.3f} {}".format(
            "({},{})".format(bands, rows), lsh_threshold(bands, rows), probs))
    print("\n  -> b 大 r 小 = 松(召回多、候选多、算得慢);b 小 r 大 = 紧。")

    print("\n" + "=" * 74)
    print("C · 阈值选错的代价:过度去重会删掉信息,不只是冗余")
    print("=" * 74)
    for thr in (0.85, 0.70, 0.50):
        kept, dropped = dedup(corpus, threshold=thr)
        print("\n  threshold={:.2f}  保留 {}/{}".format(thr, len(kept), len(corpus)))
        if not dropped:
            print("      (无删除)")
        for d, w, j in dropped:
            flag = "   <-- 删错了:规格完全不同,删的是事实不是冗余" \
                if d.startswith("prod") or w.startswith("prod") else ""
            print("      drop {:<14} (~= {:<14} J={:.3f}){}".format(d, w, j, flag))

    print("\n  -> 0.85 太松,转载没去掉;0.70 刚好去掉转载;0.50 开始误伤。")
    print("     prod_a/prod_b 样板一字不差、规格完全不同,J=0.62 —— 阈值压到 0.5")
    print("     就把产品规格这类**长尾事实**当重复删了。商品页、API 文档、")
    print("     财报模板都是这个形态,而它们恰恰是稀缺的结构化事实来源。")
    print("     这就是 07 §六:dedup 提高信息密度,过度 dedup 伤害长尾。")

    print("\n" + "=" * 74)
    print("D · 质量分类器:正样本定义了偏见")
    print("=" * 74)
    w = build_quality_training()
    informal = ("ok so the bug is that malloc returns null and you never check it. "
                "i hit this on arm64 only. fix: check the return, then retry once "
                "with a smaller block. took me two days lol.")
    vacuous = ("Our comprehensive enterprise solution leverages synergistic "
               "paradigms to deliver transformative outcomes across the "
               "organizational value chain in a scalable and robust manner.")
    terse_fact = "HTTP 429 means too many requests. Back off exponentially."

    probes = [
        ("百科式(与训练正样本同分布)", ARTICLE),
        ("导航垃圾页(与训练负样本同分布)", corpus["spam_nav"]),
        ("口语但有实质内容的技术问答", informal),
        ("正式但空洞的营销稿", vacuous),
        ("极短但完全正确的事实", terse_fact),
    ]
    scores = {}
    for name, text in probes:
        s = quality_score(text, w)
        scores[name] = s
        print("  {:<32} score={:.3f}".format(name, s))

    print("\n  -> 分类器确实认出了垃圾页(0.00),这部分它做对了。问题在排序:")
    print("     * 「正式但空洞的营销稿」得分 >= 「口语但有实质内容的技术问答」;")
    print("     * 「极短但完全正确的事实」被长度特征压到很低。")
    print("     它学到的是**文体和长度**,不是**信息价值** —— 因为正样本全是")
    print("     百科式长文本。换一批正样本,过滤器的偏好就完全变了。")
    print("\n     面试必答两句:① quality classifier 的正样本选择本身就是数据")
    print("     决策,要说清正样本从哪来(FineWeb-Edu 用 LLM 打教育性分数、")
    print("     DCLM 用 OH-2.5+ELI5 当正例);② 过滤器好不好,只能用固定算力的")
    print("     下游训练 ablation 判定,不能看分数分布好不好看。见 07 §七/§十三。")


if __name__ == "__main__":
    main()
