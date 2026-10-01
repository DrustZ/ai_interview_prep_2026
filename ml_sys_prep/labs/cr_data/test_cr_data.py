"""锁住 code review 数据 pipeline 的关键不变量。`pytest test_cr_data.py -q`"""
from __future__ import annotations

import pytest

import gate
import pairs
import reward
import signals
import toyreview

BUILT = toyreview.build()
ROOT, GT = BUILT["root"], BUILT["gt"]
COMMENTS = signals.annotate(ROOT, BUILT["comments"])
SZZ_POS = signals.szz_positives(ROOT, GT["commits"]["orders_bugfix"])


# ───────────────────────────── 信号
def test_szz_finds_the_right_inducing_commit():
    """SZZ 必须回溯到真正引入 bug 的那个 commit。"""
    res = signals.szz(ROOT, GT["commits"]["orders_bugfix"])
    inducing = {i["commit"] for f in res for i in f["inducing"]}
    assert GT["szz_expected"]["inducing_commit"] in inducing


def test_szz_positives_carry_code_and_evidence():
    assert SZZ_POS
    for p in SZZ_POS:
        assert p["code"] and p["defect_description"] and p["evidence"]


def test_resolution_uses_old_line_numbers():
    """hunk 头左边是旧文件行号。读成右边（新文件）会把采纳信号算歪。"""
    a, b = GT["commits"]["orders_v1"], GT["commits"]["orders_review"]
    touched = signals.changed_old_lines(ROOT, a, b, "shop/orders.py")
    assert 3 in touched          # DISCOUNT 那行确实被改了
    assert 1 not in touched      # import json 没被改


def test_resolution_signal_is_computed_not_hardcoded():
    resolved = [c for c in COMMENTS if c["signal"]["resolved"]]
    assert 0 < len(resolved) < len(COMMENTS)
    for c in resolved:
        assert c["signal"]["by"]


# ───────────────────────────── 质量把关
def test_bot_detection():
    assert gate.is_bot("codecov[bot]") and gate.is_bot("dependabot")
    assert not gate.is_bot("alice")


def test_gate_raises_useful_ratio():
    """过滤的唯一目的：提高有价值评论的占比。不提高就是白做。"""
    before = sum(c["_gt_useful"] for c in COMMENTS) / len(COMMENTS)
    final = gate.gate(COMMENTS)["final"]
    after = sum(c["_gt_useful"] for c in final) / len(final)
    assert after > before + 0.2


def test_lexical_dedup_misses_paraphrases():
    """诚实记录：词袋 Jaccard 在 0.35 阈值下**一条改写都抓不到**。
    cm18 是 cm11 的改写、cm19 是 cm01 的改写 —— 语义去重必须上 embedding。"""
    sub = [c for c in COMMENTS if gate.classify(c) == "substantive"]
    _, at35 = gate.dedup_comments(sub, 0.35)
    _, at10 = gate.dedup_comments(sub, 0.10)
    assert len(at35) == 0
    assert {d["comment_id"] for d in at10} >= {"cm18", "cm19"}


def test_resolution_signal_has_false_positives():
    """**核心主张**：采纳信号是有偏 proxy，不能直接当 label。"""
    cal = gate.calibrate(COMMENTS)
    assert cal["false_positives"], "必须能演示出假阳性"
    assert cal["precision"] < 0.85, "精度不该高到让人误以为它可以直接用"


def test_wrong_comment_gets_credited_by_resolution_signal():
    """最危险的那条：cm17 事实错误，却因为落在被改的行上而被记成采纳。"""
    cm17 = next(c for c in COMMENTS if c["comment_id"] == "cm17")
    assert cm17["_gt_useful"] == 0
    assert cm17["signal"]["resolved"] == 1


def test_correct_but_unaddressed_comment_is_missed():
    """cm03 是对的、当时没被采纳，三周后变成真 bug —— 假阴性。"""
    cm03 = next(c for c in COMMENTS if c["comment_id"] == "cm03")
    assert cm03["_gt_useful"] == 1 and cm03["signal"]["resolved"] == 0
    assert any(p["line"] in (21, 22, 23) for p in SZZ_POS)


# ───────────────────────────── 正负样本
def _neg():
    all_lines = {}
    for path, key in (("shop/orders.py", "orders_v1"), ("shop/auth.py", "auth_v1")):
        all_lines[path] = toyreview.sh(
            f"git show {GT['commits'][key]}:{path}", ROOT).stdout.splitlines()
    return pairs.negatives(COMMENTS, all_lines), all_lines


def test_positives_are_stratified_by_evidence_strength():
    pos = pairs.positives(COMMENTS, SZZ_POS)
    kinds = {p["evidence"] for p in pos}
    assert kinds == {"weak", "strong"}


def test_unreviewed_lines_are_kept_separate():
    """**这个领域最经典的错误**：把「没人评论的行」当负样本。
    没人评论只说明没人看 —— 这是 positive-unlabeled，不是二分类。"""
    neg, _ = _neg()
    assert neg["unreviewed_line"]
    pool = (neg["factually_wrong"] + neg["low_value_nit"]
            + neg["duplicate"] + neg["misplaced"])
    assert not any(n in pool for n in neg["unreviewed_line"])


def test_an_unreviewed_line_actually_contained_a_real_bug():
    """证明上一条不是洁癖：未被评论的行里**确实有**后来被修的真 bug。"""
    neg, _ = _neg()
    unrev = {(n["path"], n["line"]) for n in neg["unreviewed_line"]}
    assert any((p["path"], p["line"]) in unrev for p in SZZ_POS)


def test_pairs_are_matched_within_the_same_file():
    """chosen 和 rejected 跨文件配对 = 模型可以靠文件名走捷径。"""
    neg, _ = _neg()
    ps = pairs.preference_pairs(pairs.positives(COMMENTS, SZZ_POS), neg)
    assert ps and all(p["same_file"] for p in ps)


def test_misplaced_negatives_are_far_from_the_original_line():
    neg, _ = _neg()
    for m in neg["misplaced"]:
        orig = next(c for c in COMMENTS
                    if c["comment_id"] == m["comment_id"].replace("-mis", ""))
        assert abs(m["line"] - orig["line"]) > 4


# ───────────────────────────── reward
def _ctx():
    src = toyreview.sh(f"git show {GT['commits']['auth_v1']}:shop/auth.py",
                       ROOT).stdout
    return {"source": src, "lines": src.splitlines(),
            "n_lines": len(src.splitlines()), "sast_patterns": ["md5(", "SELECT"]}


def test_hard_gate_rejects_out_of_range_line():
    r = reward.total_reward({"line": 999, "body": "x"}, _ctx())
    assert r["gated"] and r["reward"] < 0


def test_hard_gate_rejects_hallucinated_symbol():
    """评论引用了代码里不存在的符号 → 过期引用或幻觉，直接砍。"""
    r = reward.total_reward(
        {"line": 4, "body": "the `read_orders` helper is deprecated"}, _ctx())
    assert r["gated"]


def test_szz_evidence_outranks_resolution_evidence():
    c = {"line": 4, "body": "md5 is broken"}
    strong = reward.total_reward({**c, "szz_confirmed": True}, _ctx())["reward"]
    weak = reward.total_reward({**c, "resolved": True}, _ctx())["reward"]
    none = reward.total_reward(c, _ctx())["reward"]
    assert strong > weak > none


def test_f1_optimum_ignores_false_positive_cost():
    """**核心主张**：F1 最优阈值不随误报代价变化，产品最优会变。"""
    fine = [i / 40 for i in range(40)]
    f1_opts, ad_opts = [], []
    for d in (0.95, 0.75, 0.45):
        rs = reward.two_stage(filter_thresholds=fine, trust_decay=d)
        f1_opts.append(max(rs, key=lambda r: r["f1"])["thr"])
        ad_opts.append(max(rs, key=lambda r: r["adopted_per_pr"])["thr"])
    assert len(set(f1_opts)) == 1, "F1 最优不该随误报代价变"
    assert ad_opts == sorted(ad_opts), "误报越贵，产品最优该越保守"
    assert ad_opts[0] < f1_opts[0] < ad_opts[-1], "两端要跨过 F1 的最优点"


def test_hack_signals_are_all_computed():
    h = reward.hack_signals(COMMENTS)
    assert set(h) and all(isinstance(v, float) for v in h.values())
