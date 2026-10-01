"""Statistical release gate for canary rollouts.

Given per-cohort success counts for a canary arm and a control arm, decide
one of three actions:

- ``ROLLBACK``: canary is *significantly worse* than control
  (one-sided two-proportion z-test, z <= -z_alpha).
- ``PROMOTE``: canary is *demonstrably non-inferior*: the Wilson lower bound
  of the canary success rate is at or above the control point estimate minus
  a non-inferiority margin (or canary is significantly better, z >= z_alpha).
- ``HOLD``: everything else -- including, crucially, **insufficient sample
  size**. A gate that answers before it has data is worse than no gate:
  underpowered "wins" promote bad models and underpowered "losses" roll back
  good ones. Below ``min_trials_per_arm`` we always HOLD and say why.

Cohorts
-------
The fleet-level decision is the *worst* decision across cohorts
(ROLLBACK > HOLD > PROMOTE). This is the whole point: an aggregate metric can
be flat while one cohort (e.g. carpet floors) regresses badly and another
improves -- Simpson's-paradox-style masking. ``rollout.py`` demonstrates this
failure mode end to end.

Pure stdlib (``math`` only), fully deterministic.
"""

import enum
import math
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple


class Decision(enum.Enum):
    """Gate decision, ordered by severity (see ``_SEVERITY``)."""

    PROMOTE = "promote"
    HOLD = "hold"
    ROLLBACK = "rollback"


_SEVERITY = {Decision.PROMOTE: 0, Decision.HOLD: 1, Decision.ROLLBACK: 2}


@dataclass(frozen=True)
class ArmCounts:
    """Success counts for one arm (canary or control) of one cohort."""

    successes: int
    trials: int

    def __post_init__(self) -> None:
        if self.trials < 0 or self.successes < 0:
            raise ValueError("counts must be non-negative")
        if self.successes > self.trials:
            raise ValueError(
                "successes (%d) cannot exceed trials (%d)"
                % (self.successes, self.trials)
            )

    @property
    def rate(self) -> float:
        """Point estimate of the success rate (0.0 when there are no trials)."""
        return self.successes / self.trials if self.trials > 0 else 0.0


@dataclass(frozen=True)
class GateConfig:
    """Tunable knobs of the gate.

    Attributes:
        min_trials_per_arm: below this, the cohort verdict is always HOLD.
        z_alpha: critical z value (1.96 ~= one-sided alpha 0.025).
        non_inferiority_margin: how much worse than control (in absolute
            success-rate points) the *pessimistic* canary estimate may be and
            still promote. Robots: a small regression on one floor type is an
            acceptable price for a fleet-wide win -- but it must be bounded.
    """

    min_trials_per_arm: int = 200
    z_alpha: float = 1.96
    non_inferiority_margin: float = 0.03

    def __post_init__(self) -> None:
        if self.min_trials_per_arm < 1:
            raise ValueError("min_trials_per_arm must be >= 1")
        if self.z_alpha <= 0:
            raise ValueError("z_alpha must be positive")
        if self.non_inferiority_margin < 0:
            raise ValueError("non_inferiority_margin must be >= 0")


@dataclass(frozen=True)
class CohortVerdict:
    """Per-cohort gate output, with enough detail to be auditable."""

    cohort: str
    decision: Decision
    reason: str
    z_score: Optional[float]
    canary_ci: Optional[Tuple[float, float]]
    control_ci: Optional[Tuple[float, float]]


@dataclass(frozen=True)
class GateReport:
    """Fleet-level decision plus the per-cohort verdicts behind it."""

    decision: Decision
    verdicts: List[CohortVerdict]

    def verdict_for(self, cohort: str) -> CohortVerdict:
        for verdict in self.verdicts:
            if verdict.cohort == cohort:
                return verdict
        raise KeyError("no verdict for cohort: %s" % cohort)


def wilson_interval(
    successes: int, trials: int, z: float = 1.96
) -> Tuple[float, float]:
    """Wilson score interval for a binomial proportion.

    Preferred over the normal ("Wald") interval because it behaves sanely at
    small n and rates near 0/1 -- exactly the regime a young canary lives in.

    Raises:
        ValueError: invalid counts or ``trials == 0`` (no data, no interval).
    """
    if trials <= 0:
        raise ValueError("wilson_interval requires trials > 0")
    if successes < 0 or successes > trials:
        raise ValueError("successes must be within [0, trials]")
    p_hat = successes / trials
    z2 = z * z
    denom = 1.0 + z2 / trials
    center = (p_hat + z2 / (2.0 * trials)) / denom
    half = (
        z
        * math.sqrt(p_hat * (1.0 - p_hat) / trials + z2 / (4.0 * trials * trials))
        / denom
    )
    return (max(0.0, center - half), min(1.0, center + half))


def two_proportion_z(canary: ArmCounts, control: ArmCounts) -> float:
    """Pooled two-proportion z statistic for (canary rate - control rate).

    Positive z: canary better. Returns 0.0 when the pooled standard error is
    zero (both arms all-success or all-failure), i.e. "no evidence of a
    difference", which downstream logic treats as not-significant.

    Raises:
        ValueError: either arm has zero trials.
    """
    if canary.trials == 0 or control.trials == 0:
        raise ValueError("two_proportion_z requires trials > 0 in both arms")
    pooled = (canary.successes + control.successes) / (
        canary.trials + control.trials
    )
    se = math.sqrt(
        pooled * (1.0 - pooled) * (1.0 / canary.trials + 1.0 / control.trials)
    )
    if se == 0.0:
        return 0.0
    return (canary.rate - control.rate) / se


def evaluate_cohort(
    cohort: str,
    canary: ArmCounts,
    control: ArmCounts,
    config: GateConfig,
) -> CohortVerdict:
    """Gate one cohort. Decision order (first match wins):

    1. Either arm below ``min_trials_per_arm``  -> HOLD ("insufficient samples").
    2. z <= -z_alpha (significantly worse)      -> ROLLBACK.
    3. z >= +z_alpha (significantly better), or Wilson lower bound of canary
       >= control point estimate - margin       -> PROMOTE.
    4. Otherwise                                -> HOLD ("keep observing").
    """
    if canary.trials < config.min_trials_per_arm or (
        control.trials < config.min_trials_per_arm
    ):
        return CohortVerdict(
            cohort=cohort,
            decision=Decision.HOLD,
            reason=(
                "insufficient samples (canary=%d, control=%d, need %d/arm)"
                % (canary.trials, control.trials, config.min_trials_per_arm)
            ),
            z_score=None,
            canary_ci=None,
            control_ci=None,
        )

    z = two_proportion_z(canary, control)
    canary_ci = wilson_interval(canary.successes, canary.trials, config.z_alpha)
    control_ci = wilson_interval(control.successes, control.trials, config.z_alpha)

    if z <= -config.z_alpha:
        return CohortVerdict(
            cohort=cohort,
            decision=Decision.ROLLBACK,
            reason=(
                "canary significantly worse: rate %.3f vs %.3f (z=%.2f <= -%.2f)"
                % (canary.rate, control.rate, z, config.z_alpha)
            ),
            z_score=z,
            canary_ci=canary_ci,
            control_ci=control_ci,
        )

    non_inferior = canary_ci[0] >= control.rate - config.non_inferiority_margin
    if z >= config.z_alpha or non_inferior:
        return CohortVerdict(
            cohort=cohort,
            decision=Decision.PROMOTE,
            reason=(
                "non-inferior: canary Wilson lower %.3f >= control %.3f - %.3f"
                " (z=%.2f)"
                % (
                    canary_ci[0],
                    control.rate,
                    config.non_inferiority_margin,
                    z,
                )
            ),
            z_score=z,
            canary_ci=canary_ci,
            control_ci=control_ci,
        )

    return CohortVerdict(
        cohort=cohort,
        decision=Decision.HOLD,
        reason=(
            "inconclusive, keep observing: rate %.3f vs %.3f (z=%.2f)"
            % (canary.rate, control.rate, z)
        ),
        z_score=z,
        canary_ci=canary_ci,
        control_ci=control_ci,
    )


def evaluate(
    cohorts: Dict[str, Tuple[ArmCounts, ArmCounts]],
    config: GateConfig,
) -> GateReport:
    """Gate all cohorts; fleet decision = worst per-cohort decision.

    Args:
        cohorts: cohort name -> (canary counts, control counts).
        config: gate configuration.

    Raises:
        ValueError: ``cohorts`` is empty (a gate with no inputs must not
            silently promote).
    """
    if not cohorts:
        raise ValueError("evaluate requires at least one cohort")
    verdicts = [
        evaluate_cohort(name, canary, control, config)
        for name, (canary, control) in sorted(cohorts.items())
    ]
    worst = max(verdicts, key=lambda v: _SEVERITY[v.decision]).decision
    return GateReport(decision=worst, verdicts=verdicts)


def merge_cohorts(
    cohorts: Dict[str, Tuple[ArmCounts, ArmCounts]]
) -> Tuple[ArmCounts, ArmCounts]:
    """Collapse per-cohort counts into one aggregate (canary, control) pair.

    Exists so the demo can show what an aggregate-only gate *would* have
    decided -- i.e. the anti-pattern this module is designed to avoid.
    """
    canary_s = sum(c.successes for c, _ in cohorts.values())
    canary_t = sum(c.trials for c, _ in cohorts.values())
    control_s = sum(k.successes for _, k in cohorts.values())
    control_t = sum(k.trials for _, k in cohorts.values())
    return (
        ArmCounts(successes=canary_s, trials=canary_t),
        ArmCounts(successes=control_s, trials=control_t),
    )
