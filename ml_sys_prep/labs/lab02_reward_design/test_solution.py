"""Lab 02 测试:把"reward 被 hack / 被修好"变成可执行断言。

跑法:  python3 test_solution.py     (也兼容 pytest)
"""

import sys

from solution import (
    Defect,
    Finding,
    RewardConfig,
    build_scenario,
    reward_hardened,
    reward_naive,
)


def test_naive_reward_is_hackable():
    """天真 reward 下,刷量和通胀都打败诚实 agent —— 这就是被 hack 的定义。"""
    defects, agents = build_scenario()
    s = {k: reward_naive(v, defects) for k, v in agents.items()}
    assert s["spam"] > s["honest"], "刷量应当在天真 reward 下胜出"
    assert s["inflator"] > s["honest"], "severity 通胀应当在天真 reward 下胜出"


def test_hardened_reward_ranks_honest_first():
    """加固后诚实 agent 必须排第一。"""
    defects, agents = build_scenario()
    s = {k: reward_hardened(v, defects).total for k, v in agents.items()}
    best = max(s, key=lambda k: s[k])
    assert best == "honest", "加固后应当是 honest 第一,实际是 " + best
    for hacker in ("spam", "inflator", "nitpicker", "leaker"):
        assert s["honest"] > s[hacker], hacker + " 不应超过 honest"


def test_hard_constraint_cannot_be_offset():
    """泄密是否决项:即使找到了真 critical bug 也不能抵消。"""
    defects, agents = build_scenario()
    br = reward_hardened(agents["leaker"], defects)
    assert br.gate_failed == "leaked_secret"
    assert br.total < 0
    # 对照:同一条 finding 去掉泄密标记就应该是正分
    clean = [Finding(f.path, f.line, f.severity, f.claim,
                     has_evidence=f.has_evidence, leaks_secret=False)
             for f in agents["leaker"]]
    assert reward_hardened(clean, defects).total > 0


def test_duplicate_findings_get_no_extra_credit():
    """同一个缺陷刷 N 条评论,outcome 不随 N 增长。"""
    defects = {Defect("a.py", 10, "critical")}
    one = [Finding("a.py", 10, "critical", "bug")]
    five = [Finding("a.py", 10 + i, "critical", "bug") for i in (-2, -1, 0, 1, 2)]
    cfg = RewardConfig(min_precision=0.0)  # 关掉地板,单独观察去重效果
    r1 = reward_hardened(one, defects, cfg)
    r5 = reward_hardened(five, defects, cfg)
    assert r1.n_unique_true == r5.n_unique_true == 1
    assert r5.n_duplicate == 4
    assert r5.total < r1.total, "重复评论应当降低总分(消耗注意力)"


def test_severity_comes_from_ground_truth_not_self_report():
    """模型自称 critical 不能把一个 medium 缺陷变成 8 分。"""
    defects = {Defect("a.py", 10, "medium")}
    honest = [Finding("a.py", 10, "medium", "bug")]
    inflated = [Finding("a.py", 10, "critical", "bug")]
    cfg = RewardConfig(min_precision=0.0)
    assert (reward_hardened(honest, defects, cfg).outcome
            == reward_hardened(inflated, defects, cfg).outcome)


def test_precision_floor_kills_spam():
    """precision 分子必须是独立缺陷数,否则刷量能靠重复命中蒙混过关。"""
    defects, agents = build_scenario()
    br = reward_hardened(agents["spam"], defects)
    assert br.gate_failed == "precision_below_floor"
    assert br.n_unique_true == 2 and br.n_published == 10


def test_empty_output_is_zero_not_negative():
    """什么都不说应当是 0 分:既不奖励也不惩罚,避免逼模型硬凑评论。"""
    defects, _ = build_scenario()
    assert reward_hardened([], defects).total == 0.0


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
