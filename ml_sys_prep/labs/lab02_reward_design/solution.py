"""Lab 02 · Code review reward function + reward hacking(参考实现)

对口 04_case_code_review_llm.md §7-§8 与 03_model_training_reward.md §6-§7。

核心论点(面试可以直接讲):
    一个"加权求和"的 reward 会把刷量和通胀的 agent 排在诚实 agent 前面。
    修复不是调权重,而是改变 reward 的**结构**:

      1) hard constraint 用 gate(否决),不能被软分抵消;
      2) **按缺陷去重**:同一个 bug 刷十条评论只算一次 —— 这是最容易漏掉的一条;
      3) precision 用"独立真缺陷数 / 已发布条数",并设地板;
      4) severity 由 ground truth 决定,不采信模型自称;
      5) 成本按每条已发布评论计,让刷量直接变贵。
"""

from dataclasses import dataclass, field
from typing import List, Set, Tuple, Dict, Optional


# --------------------------------------------------------------------------
# 数据模型
# --------------------------------------------------------------------------

SEVERITY_WEIGHT = {"critical": 8.0, "high": 4.0, "medium": 2.0, "nit": 0.25}


@dataclass(frozen=True)
class Defect:
    """ground truth:这个 PR 里真实存在的缺陷。

    来源不是人拍脑袋,而是可验证信号:后续 revert/hotfix 改动的行、
    能复现的失败测试、安全扫描确认项。见 04 §3。
    """

    path: str
    line: int
    severity: str  # critical / high / medium / nit


@dataclass
class Finding:
    """模型产出的一条评论。"""

    path: str
    line: int
    severity: str  # 模型**自称**的严重度 —— 不可信
    claim: str
    has_evidence: bool = False  # 是否引用了具体代码/数据流
    has_repro: bool = False  # 是否给出可复现步骤
    has_fix: bool = False  # 是否给出具体修改建议
    leaks_secret: bool = False  # 评论正文是否泄漏 secret
    reproduced_by_verifier: bool = False  # 确定性 verifier 是否复现


LINE_TOLERANCE = 2  # 定位误差容忍(行)


def match_defect(finding: Finding, defects: Set[Defect]) -> Tuple[bool, Optional[Defect]]:
    """finding 是否命中某个真实缺陷(路径相同且行号在容忍范围内)。"""
    for d in defects:
        if d.path == finding.path and abs(d.line - finding.line) <= LINE_TOLERANCE:
            return True, d
    return False, None


# --------------------------------------------------------------------------
# Reward v1:天真的加权求和 —— 这是会被 hack 的版本
# --------------------------------------------------------------------------


def reward_naive(findings: List[Finding], defects: Set[Defect]) -> float:
    """只奖励"命中了多少条"× 模型自称的严重度。

    三个致命缺陷:
      - 不去重     -> 同一个 bug 刷 N 条拿 N 份分,刷量必胜;
      - 没 precision -> 多说不吃亏;
      - severity 采信自称 -> 通胀必胜。
    """
    score = 0.0
    for f in findings:
        hit, _ = match_defect(f, defects)
        if hit:
            score += SEVERITY_WEIGHT.get(f.severity, 1.0)
    return score


# --------------------------------------------------------------------------
# Reward v2:分层加固
# --------------------------------------------------------------------------


@dataclass
class RewardConfig:
    comment_budget: int = 10  # 每个 PR 允许发布的评论上限(hard gate)
    min_precision: float = 0.5  # 独立真缺陷数/已发布数,低于此值判负
    cost_per_finding: float = 0.5  # 每条已发布评论的 reviewer 注意力成本
    false_positive_penalty: float = 3.0  # 单条误报
    duplicate_penalty: float = 1.0  # 重复评论同一缺陷
    unverified_high_penalty: float = 2.0  # 自称高危却对不上真实缺陷


@dataclass
class RewardBreakdown:
    """把 reward 拆开报告,而不是只给一个标量。见 03 §7 第 6 条。"""

    total: float = 0.0
    gate_failed: str = ""
    outcome: float = 0.0
    quality: float = 0.0
    precision: float = 0.0
    cost: float = 0.0
    n_published: int = 0
    n_unique_true: int = 0
    n_duplicate: int = 0
    n_false: int = 0
    detail: Dict[str, float] = field(default_factory=dict)


def check_hard_constraints(findings: List[Finding], cfg: RewardConfig) -> str:
    """Hard constraint 是**否决项**,不是加权项。返回失败原因,空串表示通过。"""
    for f in findings:
        if f.leaks_secret:
            return "leaked_secret"
    if len(findings) > cfg.comment_budget:
        return "exceeded_comment_budget"
    return ""


def reward_hardened(
    findings: List[Finding],
    defects: Set[Defect],
    cfg: Optional[RewardConfig] = None,
) -> RewardBreakdown:
    cfg = cfg or RewardConfig()
    br = RewardBreakdown()
    br.n_published = len(findings)

    # ---- 第 1 层:hard constraints(否决,不能被软分抵消) ----
    gate = check_hard_constraints(findings, cfg)
    if gate:
        br.gate_failed = gate
        br.total = -10.0
        return br

    if not findings:
        br.total = 0.0
        return br

    # ---- 第 2 层:task outcome,**按缺陷去重** ----
    credited: Set[Defect] = set()
    for f in findings:
        hit, d = match_defect(f, defects)
        if hit and d not in credited:
            credited.add(d)
            br.n_unique_true += 1
            # severity 以 ground truth 为准 —— 这一行就是"先 gate truth,再优化表达"
            br.outcome += SEVERITY_WEIGHT[d.severity]
        elif hit:
            # 同一个缺陷的第 2..N 条评论:不加分,而且消耗 reviewer 注意力
            br.n_duplicate += 1
            br.outcome -= cfg.duplicate_penalty
        else:
            br.n_false += 1
            br.outcome -= cfg.false_positive_penalty
            if f.severity in ("critical", "high"):
                br.outcome -= cfg.unverified_high_penalty  # 专治 severity 通胀

    # ---- 第 3 层:quality(只对命中的评论计,错的写得再漂亮也不加分) ----
    for f in findings:
        hit, _ = match_defect(f, defects)
        if not hit:
            continue
        if f.has_evidence:
            br.quality += 0.5
        if f.has_repro:
            br.quality += 0.5
        if f.has_fix:
            br.quality += 0.5
        if f.reproduced_by_verifier:
            br.quality += 1.0

    # ---- precision 地板:分子是**独立**真缺陷数,不是命中条数 ----
    br.precision = br.n_unique_true / len(findings)
    if br.precision < cfg.min_precision:
        br.gate_failed = "precision_below_floor"
        br.total = -5.0
        br.detail["precision"] = br.precision
        return br

    # ---- 第 4 层:成本 ----
    br.cost = cfg.cost_per_finding * len(findings)

    br.total = br.outcome + br.quality - br.cost
    br.detail = {
        "outcome": br.outcome,
        "quality": br.quality,
        "cost": br.cost,
        "precision": br.precision,
        "defect_recall": len(credited) / max(1, len(defects)),
    }
    return br


# --------------------------------------------------------------------------
# 场景:一个 PR 的 ground truth + 五个 agent
# --------------------------------------------------------------------------


def build_scenario():
    """两个真实缺陷:一个 critical,一个 medium。"""
    defects = {
        Defect("src/auth/session.py", 86, "critical"),
        Defect("src/api/handler.py", 42, "medium"),
    }

    honest = [
        Finding(
            "src/auth/session.py", 86, "critical",
            "Negative clock_skew lets expired sessions validate.",
            has_evidence=True, has_repro=True, has_fix=True,
            reproduced_by_verifier=True,
        ),
        Finding(
            "src/api/handler.py", 43, "medium",
            "Unbounded retry loop on 5xx.",
            has_evidence=True, has_fix=True,
        ),
        Finding("src/util/fmt.py", 12, "nit", "Prefer f-string here."),  # 无害误报
    ]

    # 刷量:围着两个可疑区域各刷一圈,外加几条凑数。
    # 天真 reward 下每条命中都单独计分 -> 分数爆炸。
    spam = (
        [Finding("src/auth/session.py", ln, "high", "Possible issue here.")
         for ln in (84, 85, 86, 87, 88)]
        + [Finding("src/api/handler.py", ln, "high", "Possible issue here.")
           for ln in (41, 42, 43)]
        + [Finding("src/util/fmt.py", ln, "high", "Possible issue here.")
           for ln in (3, 7)]
    )

    # 严重度通胀:全部自称 critical,内容空洞
    inflator = [
        Finding("src/auth/session.py", 86, "critical", "Critical bug."),
        Finding("src/api/handler.py", 42, "critical", "Critical bug."),
        Finding("src/util/fmt.py", 3, "critical", "Critical bug."),
    ]

    # 只挑容易被采纳的琐事:采纳率高,真实价值为零
    nitpicker = [
        Finding("src/util/fmt.py", 3, "nit", "Add trailing comma.", has_fix=True),
        Finding("src/util/fmt.py", 7, "nit", "Rename variable.", has_fix=True),
        Finding("src/util/fmt.py", 9, "nit", "Sort imports.", has_fix=True),
    ]

    # 找到了真 bug,但把 secret 抄进了评论正文
    leaker = [
        Finding(
            "src/auth/session.py", 86, "critical",
            "Token signing key AKIA... is hardcoded; expired sessions validate.",
            has_evidence=True, leaks_secret=True,
        ),
    ]

    return defects, {
        "honest": honest,
        "spam": spam,
        "inflator": inflator,
        "nitpicker": nitpicker,
        "leaker": leaker,
    }


def main():
    defects, agents = build_scenario()

    print("=" * 72)
    print("Reward v1(天真加权求和:不去重 / 无 precision / 采信自称 severity)")
    print("=" * 72)
    naive = {name: reward_naive(f, defects) for name, f in agents.items()}
    for name, s in sorted(naive.items(), key=lambda kv: -kv[1]):
        print("  {:<10} {:>7.2f}".format(name, s))
    print("\n  -> spam 靠围着同一个 bug 刷 8 条命中拿到最高分,inflator 靠自称")
    print("     critical 把一个 medium 缺陷算成 8 分。honest 只排第三。\n")

    print("=" * 72)
    print("Reward v2(hard gate + 按缺陷去重 + precision 地板 + 真实 severity + 成本)")
    print("=" * 72)
    hard = {name: reward_hardened(f, defects) for name, f in agents.items()}
    for name, br in sorted(hard.items(), key=lambda kv: -kv[1].total):
        if br.gate_failed:
            note = "GATE: " + br.gate_failed
            if br.gate_failed == "precision_below_floor":
                note += " ({}/{}={:.2f})".format(
                    br.n_unique_true, br.n_published, br.precision)
        else:
            note = ("unique_true={} dup={} fp={} outcome={:.1f} "
                    "quality={:.1f} cost={:.1f}").format(
                br.n_unique_true, br.n_duplicate, br.n_false,
                br.outcome, br.quality, br.cost)
        print("  {:<10} {:>7.2f}   {}".format(name, br.total, note))

    print("\n  -> honest 第一。四个 hacker 分别被:")
    print("       spam      -> 去重后 precision=2/10 击穿地板")
    print("       inflator  -> severity 用 ground truth,medium 就是 2 分不是 8 分")
    print("       nitpicker -> 一个真缺陷都没碰到,precision=0")
    print("       leaker    -> hard gate 否决,找到真 bug 也不能抵消泄密")
    print("     修的是结构,不是权重。")


if __name__ == "__main__":
    main()
