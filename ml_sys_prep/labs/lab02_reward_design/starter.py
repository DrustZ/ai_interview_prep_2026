"""Lab 02 starter · 自己写一遍 reward,再看 solution.py

用法:
    1. 只看下面的 TODO,不要打开 solution.py;
    2. 填完后把 test_solution.py 里的 `from solution import` 改成 `from starter import`,
       跑 `python3 test_solution.py`;
    3. 全绿之后再对照 solution.py 看差异。

限时 30 分钟。写不出来先跳到 04_case_code_review_llm.md §7 读 10 分钟再回来。
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Set, Tuple

SEVERITY_WEIGHT = {"critical": 8.0, "high": 4.0, "medium": 2.0, "nit": 0.25}
LINE_TOLERANCE = 2


@dataclass(frozen=True)
class Defect:
    path: str
    line: int
    severity: str


@dataclass
class Finding:
    path: str
    line: int
    severity: str
    claim: str
    has_evidence: bool = False
    has_repro: bool = False
    has_fix: bool = False
    leaks_secret: bool = False
    reproduced_by_verifier: bool = False


@dataclass
class RewardConfig:
    comment_budget: int = 10
    min_precision: float = 0.5
    cost_per_finding: float = 0.5
    false_positive_penalty: float = 3.0
    duplicate_penalty: float = 1.0
    unverified_high_penalty: float = 2.0


@dataclass
class RewardBreakdown:
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


def match_defect(finding, defects) -> Tuple[bool, Optional[Defect]]:
    # TODO: 路径相同且 |line 差| <= LINE_TOLERANCE 即算命中
    raise NotImplementedError


def reward_naive(findings: List[Finding], defects: Set[Defect]) -> float:
    """TODO: 故意写一个会被 hack 的版本。

    要求:命中就加分,分值用 **模型自称的** severity,不去重、不算 precision。
    写完先想清楚:一个刷量的 agent 会怎么利用它?
    """
    raise NotImplementedError


def check_hard_constraints(findings: List[Finding], cfg: RewardConfig) -> str:
    """TODO: 返回失败原因字符串,通过则返回 ""。

    至少两条:① 任一 finding 泄漏 secret;② 条数超过 comment_budget。
    想清楚为什么这必须是**否决**而不是一个大的负权重项。
    """
    raise NotImplementedError


def reward_hardened(findings, defects, cfg: Optional[RewardConfig] = None) -> RewardBreakdown:
    """TODO: 四层结构。逐层实现,每层写完跑一次测试。

    第 1 层 hard gate      : check_hard_constraints,失败直接 total=-10 返回。
    第 2 层 task outcome   : 遍历 findings ——
                              * 命中且该 defect 还没被计过 -> 用 **ground truth 的**
                                severity 加分,记入 credited 集合;
                              * 命中但 defect 已计过       -> n_duplicate += 1,扣
                                duplicate_penalty(同一 bug 刷 N 条不能拿 N 份分);
                              * 未命中                     -> 扣 false_positive_penalty;
                                若自称 critical/high 再多扣 unverified_high_penalty。
    第 3 层 quality        : 只对**命中**的 finding 计 evidence/repro/fix/verifier 加分。
    precision 地板         : n_unique_true / n_published < min_precision -> total=-5 返回。
                             注意分子是**独立缺陷数**,不是命中条数。
    第 4 层 cost           : cost_per_finding * n_published。
    total = outcome + quality - cost
    """
    raise NotImplementedError


# 场景直接复用 solution 里的,专注写 reward 本身
try:
    from solution import build_scenario  # noqa: F401
except ImportError:  # pragma: no cover
    build_scenario = None
