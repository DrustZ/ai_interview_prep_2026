"""Statistical toolkit for real-robot policy evaluation.

Real-robot rollouts are expensive (100-200 trials per robot per day), so
every eval must be sized *before* it runs and read with honest uncertainty
*after* it runs. This module packages the five tools that cover that
lifecycle:

  1. ``wilson_ci``            -- how uncertain is a measured success rate?
  2. ``trials_needed``        -- how many trials per arm to detect an
                                 improvement (two-proportion z-test, pooled
                                 normal approximation)?
  3. ``paired_compare``       -- A/B on the *same* task list -> McNemar
                                 exact + approximate test on discordant
                                 pairs (plus ``paired_trials_needed`` to
                                 size a paired design).
  4. ``bootstrap_diff_ci``    -- assumption-light CI on the A/B difference.
  5. ``peeking_inflation_sim``-- what happens to the false-positive rate if
                                 you peek at the z-test every 50 trials.

Dependencies: numpy + standard library only (Python 3.9 compatible).
All randomized routines take an explicit seed and are deterministic.
"""

import math
import statistics
from dataclasses import dataclass
from typing import Sequence, Tuple

import numpy as np

__all__ = [
    "ConfidenceInterval",
    "SampleSize",
    "McNemarResult",
    "PeekingResult",
    "wilson_ci",
    "trials_needed",
    "paired_compare",
    "paired_trials_needed",
    "bootstrap_diff_ci",
    "peeking_inflation_sim",
]

_STD_NORMAL = statistics.NormalDist()


def _z_quantile(q: float) -> float:
    """Standard normal quantile (inverse CDF) via the stdlib, no scipy."""
    return _STD_NORMAL.inv_cdf(q)


def _chi2_sf_1df(x: float) -> float:
    """Survival function of chi-square with 1 df: P(X > x) = 2 * (1 - Phi(sqrt(x)))."""
    if x < 0.0:
        raise ValueError("chi-square statistic must be non-negative, got %r" % x)
    return 2.0 * (1.0 - _STD_NORMAL.cdf(math.sqrt(x)))


def _validate_proportion(name: str, value: float) -> None:
    if not (0.0 < value < 1.0):
        raise ValueError("%s must be strictly inside (0, 1), got %r" % (name, value))


def _as_bool_1d(name: str, values: Sequence) -> np.ndarray:
    arr = np.asarray(values)
    if arr.ndim != 1:
        raise ValueError("%s must be 1-D, got shape %r" % (name, arr.shape))
    if arr.size == 0:
        raise ValueError("%s must be non-empty" % name)
    return arr.astype(bool)


# ---------------------------------------------------------------------------
# 1. Wilson score interval
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class ConfidenceInterval:
    """A two-sided confidence interval around a point estimate."""

    point: float
    lower: float
    upper: float
    confidence: float

    @property
    def half_width(self) -> float:
        return (self.upper - self.lower) / 2.0

    def contains(self, value: float) -> bool:
        return self.lower <= value <= self.upper

    def __str__(self) -> str:
        return "%.3f  [%.3f, %.3f]  (+/-%.1fpp @ %.0f%%)" % (
            self.point, self.lower, self.upper,
            100.0 * self.half_width, 100.0 * self.confidence,
        )


def wilson_ci(k: int, n: int, confidence: float = 0.95) -> ConfidenceInterval:
    """Wilson score interval for a binomial success rate.

    Preferred over the naive Wald interval for robot evals because it stays
    inside [0, 1] and behaves sanely at small n and success rates near 0/1
    (exactly the regime of 20-50 real-robot trials on a 90% policy).

    Args:
        k: number of successes (0 <= k <= n).
        n: number of trials (n >= 1).
        confidence: two-sided coverage, e.g. 0.95.

    Returns:
        ConfidenceInterval with point = k/n.
    """
    if n < 1:
        raise ValueError("n must be >= 1, got %r" % n)
    if not (0 <= k <= n):
        raise ValueError("k must satisfy 0 <= k <= n, got k=%r n=%r" % (k, n))
    _validate_proportion("confidence", confidence)

    z = _z_quantile(0.5 + confidence / 2.0)
    p_hat = k / n
    z2_n = z * z / n
    denom = 1.0 + z2_n
    center = (p_hat + z2_n / 2.0) / denom
    half = (z / denom) * math.sqrt(p_hat * (1.0 - p_hat) / n + z2_n / (4.0 * n))
    return ConfidenceInterval(
        point=p_hat,
        lower=max(0.0, center - half),
        upper=min(1.0, center + half),
        confidence=confidence,
    )


# ---------------------------------------------------------------------------
# 2. Sample size for an independent two-arm eval
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class SampleSize:
    """Required eval size, both the exact formula value and the ceiled int."""

    n_per_arm: int      # ceil(n_exact) -- what you actually schedule
    n_exact: float      # raw formula output -- for cross-checking sources
    p0: float
    p1: float
    power: float
    alpha: float

    def __str__(self) -> str:
        return (
            "%d trials/arm (exact %.1f) to detect %.0f%% -> %.0f%% "
            "@ power=%.2f, alpha=%.2f"
            % (self.n_per_arm, self.n_exact, 100 * self.p0, 100 * self.p1,
               self.power, self.alpha)
        )


def trials_needed(
    p0: float,
    delta: float,
    power: float = 0.80,
    alpha: float = 0.05,
) -> SampleSize:
    """Per-arm sample size for a two-sided two-proportion z-test.

    Uses the pooled-variance normal approximation (the classic textbook
    formula, no continuity correction):

        n = [ z_{1-a/2} * sqrt(2 * pbar * (1-pbar))
              + z_{power} * sqrt(p0*(1-p0) + p1*(1-p1)) ]^2 / delta^2

    with pbar = (p0 + p1) / 2. This is the formula behind the prep-doc
    numbers: 80%->85% gives n_exact ~= 905.3 ("~905 per arm").

    Args:
        p0: baseline success rate, in (0, 1).
        delta: improvement to detect (p1 = p0 + delta); may be negative.
        power: desired power (1 - beta), in (0, 1).
        alpha: two-sided significance level, in (0, 1).

    Returns:
        SampleSize; schedule ``n_per_arm`` trials in EACH arm.
    """
    _validate_proportion("p0", p0)
    _validate_proportion("power", power)
    _validate_proportion("alpha", alpha)
    if delta == 0.0:
        raise ValueError("delta must be non-zero: cannot size a test for no effect")
    p1 = p0 + delta
    _validate_proportion("p1 = p0 + delta", p1)

    z_alpha = _z_quantile(1.0 - alpha / 2.0)
    z_power = _z_quantile(power)
    p_bar = (p0 + p1) / 2.0
    numer = (
        z_alpha * math.sqrt(2.0 * p_bar * (1.0 - p_bar))
        + z_power * math.sqrt(p0 * (1.0 - p0) + p1 * (1.0 - p1))
    ) ** 2
    n_exact = numer / (delta * delta)
    return SampleSize(
        n_per_arm=int(math.ceil(n_exact)),
        n_exact=n_exact,
        p0=p0, p1=p1, power=power, alpha=alpha,
    )


# ---------------------------------------------------------------------------
# 3. Paired A/B comparison (McNemar) + paired design sizing
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class McNemarResult:
    """McNemar test on paired binary outcomes (same tasks, policies A and B)."""

    n_pairs: int
    n_a_only: int          # A succeeded, B failed  (discordant, "b" cell)
    n_b_only: int          # B succeeded, A failed  (discordant, "c" cell)
    diff: float            # success_rate(B) - success_rate(A)
    discordant_rate: float
    p_exact: float         # exact binomial (two-sided) on discordant pairs
    p_approx: float        # continuity-corrected chi-square approximation

    def __str__(self) -> str:
        return (
            "n=%d pairs, diff=%+.1fpp, discordant=%d (A-only %d / B-only %d), "
            "McNemar p_exact=%.4f, p_approx=%.4f"
            % (self.n_pairs, 100 * self.diff, self.n_a_only + self.n_b_only,
               self.n_a_only, self.n_b_only, self.p_exact, self.p_approx)
        )


def paired_compare(a_success: Sequence, b_success: Sequence) -> McNemarResult:
    """Compare policies A and B run on the SAME list of tasks.

    Only discordant pairs (exactly one policy succeeded) carry information
    about which policy is better; concordant pairs cancel out. That is why a
    paired eval on a fixed task list needs far fewer robot runs than two
    independent arms -- see ``paired_trials_needed``.

    Args:
        a_success: 1-D boolean-like outcomes of policy A, one per task.
        b_success: 1-D boolean-like outcomes of policy B, same tasks/order.

    Returns:
        McNemarResult with exact and approximate two-sided p-values.
    """
    a = _as_bool_1d("a_success", a_success)
    b = _as_bool_1d("b_success", b_success)
    if a.shape != b.shape:
        raise ValueError(
            "paired outcomes must have equal length, got %d vs %d"
            % (a.size, b.size)
        )

    n_a_only = int(np.sum(a & ~b))
    n_b_only = int(np.sum(~a & b))
    m = n_a_only + n_b_only

    # Exact two-sided binomial test: under H0 each discordant pair is a fair
    # coin flip between "A-only" and "B-only".
    if m == 0:
        p_exact = 1.0
        p_approx = 1.0
    else:
        tail = min(n_a_only, n_b_only)
        cdf = sum(math.comb(m, i) for i in range(tail + 1)) * (0.5 ** m)
        p_exact = min(1.0, 2.0 * cdf)
        # Edwards continuity-corrected McNemar chi-square (1 df).
        chi2 = (abs(n_a_only - n_b_only) - 1.0) ** 2 / m
        p_approx = min(1.0, _chi2_sf_1df(chi2))

    return McNemarResult(
        n_pairs=int(a.size),
        n_a_only=n_a_only,
        n_b_only=n_b_only,
        diff=float(b.mean() - a.mean()),
        discordant_rate=m / a.size,
        p_exact=p_exact,
        p_approx=p_approx,
    )


def paired_trials_needed(
    p0: float,
    delta: float,
    rho: float,
    power: float = 0.80,
    alpha: float = 0.05,
) -> SampleSize:
    """Number of task PAIRS for a paired (McNemar) design, Connor (1987).

    ``rho`` is the correlation between A's and B's outcome on the same task
    (driven by shared task difficulty: a task that is hard for A tends to be
    hard for B). Higher rho -> fewer discordant pairs -> the paired design
    needs fewer tasks than the independent design needs per arm.

        psi = P(discordant) = p0 + p1 - 2*p11
        n_pairs = [ z_{1-a/2}*sqrt(psi) + z_{power}*sqrt(psi - delta^2) ]^2
                  / delta^2

    Args:
        p0: success rate of policy A, in (0, 1).
        delta: improvement of B over A (p1 = p0 + delta).
        rho: within-task outcome correlation in [0, 1); 0 recovers roughly
            the independent-arm answer.
        power, alpha: as in ``trials_needed``.

    Returns:
        SampleSize where ``n_per_arm`` means number of task pairs (each pair
        = 1 run of A + 1 run of B).
    """
    _validate_proportion("p0", p0)
    _validate_proportion("power", power)
    _validate_proportion("alpha", alpha)
    if delta == 0.0:
        raise ValueError("delta must be non-zero: cannot size a test for no effect")
    p1 = p0 + delta
    _validate_proportion("p1 = p0 + delta", p1)
    if not (0.0 <= rho < 1.0):
        raise ValueError("rho must be in [0, 1), got %r" % rho)

    # Joint cell probabilities implied by (p0, p1, rho).
    cov = rho * math.sqrt(p0 * (1.0 - p0) * p1 * (1.0 - p1))
    p11 = p0 * p1 + cov
    p10 = p0 - p11            # A-only success
    p01 = p1 - p11            # B-only success
    p00 = 1.0 - p11 - p10 - p01
    for name, cell in (("p11", p11), ("p10", p10), ("p01", p01), ("p00", p00)):
        if cell < 0.0:
            raise ValueError(
                "rho=%r is infeasible for marginals p0=%r p1=%r (cell %s < 0)"
                % (rho, p0, p1, name)
            )
    psi = p10 + p01
    if psi <= delta * delta:
        raise ValueError(
            "discordant probability psi=%.4f too small relative to delta; "
            "the normal approximation breaks down" % psi
        )

    z_alpha = _z_quantile(1.0 - alpha / 2.0)
    z_power = _z_quantile(power)
    n_exact = (
        z_alpha * math.sqrt(psi) + z_power * math.sqrt(psi - delta * delta)
    ) ** 2 / (delta * delta)
    return SampleSize(
        n_per_arm=int(math.ceil(n_exact)),
        n_exact=n_exact,
        p0=p0, p1=p1, power=power, alpha=alpha,
    )


# ---------------------------------------------------------------------------
# 4. Bootstrap CI on the A/B difference
# ---------------------------------------------------------------------------

def bootstrap_diff_ci(
    a_success: Sequence,
    b_success: Sequence,
    paired: bool = True,
    n_boot: int = 5000,
    confidence: float = 0.95,
    seed: int = 0,
) -> ConfidenceInterval:
    """Percentile-bootstrap CI for mean(B) - mean(A).

    Paired mode resamples task indices (keeping the A/B outcomes of a task
    together), so shared task-difficulty variance cancels and the CI is
    tighter than in independent mode -- the same effect that makes the
    paired design cheaper.

    Args:
        a_success, b_success: 1-D boolean-like outcome arrays. In paired
            mode they must be equal length and task-aligned.
        paired: resample tasks jointly (True) or each arm separately (False).
        n_boot: number of bootstrap resamples.
        confidence: two-sided coverage.
        seed: RNG seed; results are deterministic for a fixed seed.

    Returns:
        ConfidenceInterval on the success-rate difference (B minus A).
    """
    if n_boot < 100:
        raise ValueError("n_boot must be >= 100 for a meaningful CI, got %r" % n_boot)
    _validate_proportion("confidence", confidence)
    a = _as_bool_1d("a_success", a_success).astype(np.float64)
    b = _as_bool_1d("b_success", b_success).astype(np.float64)
    if paired and a.size != b.size:
        raise ValueError(
            "paired=True requires equal lengths, got %d vs %d" % (a.size, b.size)
        )

    rng = np.random.default_rng(seed)
    if paired:
        idx = rng.integers(0, a.size, size=(n_boot, a.size))
        diffs = (b[idx] - a[idx]).mean(axis=1)
    else:
        idx_a = rng.integers(0, a.size, size=(n_boot, a.size))
        idx_b = rng.integers(0, b.size, size=(n_boot, b.size))
        diffs = b[idx_b].mean(axis=1) - a[idx_a].mean(axis=1)

    tail = (1.0 - confidence) / 2.0
    lower, upper = np.quantile(diffs, [tail, 1.0 - tail])
    return ConfidenceInterval(
        point=float(b.mean() - a.mean()),
        lower=float(lower),
        upper=float(upper),
        confidence=confidence,
    )


# ---------------------------------------------------------------------------
# 5. Peeking / sequential-testing alpha inflation
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class PeekingResult:
    """Monte-Carlo estimate of type-I error under repeated peeking."""

    alpha_nominal: float
    n_peeks: int
    peek_every: int
    n_sims: int
    fpr_final_only: float   # reject rate testing ONCE at the final n (sanity)
    fpr_any_peek: float     # reject rate if you stop at the FIRST significant peek

    @property
    def inflation_factor(self) -> float:
        return self.fpr_any_peek / self.alpha_nominal

    def __str__(self) -> str:
        return (
            "nominal alpha=%.0f%%: test once at the end -> %.1f%% false "
            "positives; peek every %d trials (%d looks) -> %.1f%% "
            "(x%.1f inflation)"
            % (100 * self.alpha_nominal, 100 * self.fpr_final_only,
               self.peek_every, self.n_peeks, 100 * self.fpr_any_peek,
               self.inflation_factor)
        )


def peeking_inflation_sim(
    p: float = 0.80,
    n_max: int = 1000,
    peek_every: int = 50,
    alpha: float = 0.05,
    n_sims: int = 2000,
    seed: int = 0,
) -> PeekingResult:
    """Simulate the alpha inflation caused by peeking at a running A/B eval.

    Both arms have the SAME true success rate ``p`` (H0 is true). We run the
    two-proportion z-test every ``peek_every`` trials per arm and 'ship' at
    the first significant look. The fraction of simulations that ever reject
    is the real false-positive rate -- far above the nominal alpha.

    This is why "keep evaluating until the improvement is significant" is a
    bug, and why sequential designs need alpha-spending corrections
    (Pocock / O'Brien-Fleming) or a fixed pre-registered n.

    Args:
        p: common true success rate under H0.
        n_max: total trials per arm.
        peek_every: interval (in trials per arm) between looks.
        alpha: nominal two-sided significance level per look.
        n_sims: number of Monte-Carlo replications.
        seed: RNG seed; deterministic for a fixed seed.

    Returns:
        PeekingResult with final-look-only and any-peek rejection rates.
    """
    _validate_proportion("p", p)
    _validate_proportion("alpha", alpha)
    if peek_every < 1 or n_max < peek_every:
        raise ValueError(
            "need 1 <= peek_every <= n_max, got peek_every=%r n_max=%r"
            % (peek_every, n_max)
        )
    if n_sims < 100:
        raise ValueError("n_sims must be >= 100, got %r" % n_sims)

    rng = np.random.default_rng(seed)
    cum_a = np.cumsum(rng.random((n_sims, n_max)) < p, axis=1)
    cum_b = np.cumsum(rng.random((n_sims, n_max)) < p, axis=1)

    peek_ns = np.arange(peek_every, n_max + 1, peek_every)
    k_a = cum_a[:, peek_ns - 1].astype(np.float64)
    k_b = cum_b[:, peek_ns - 1].astype(np.float64)
    n = peek_ns.astype(np.float64)                       # broadcasts over sims

    p_pool = (k_a + k_b) / (2.0 * n)
    se = np.sqrt(p_pool * (1.0 - p_pool) * (2.0 / n))
    with np.errstate(divide="ignore", invalid="ignore"):
        z = np.where(se > 0.0, (k_b / n - k_a / n) / se, 0.0)

    z_crit = _z_quantile(1.0 - alpha / 2.0)
    significant = np.abs(z) > z_crit
    return PeekingResult(
        alpha_nominal=alpha,
        n_peeks=int(peek_ns.size),
        peek_every=peek_every,
        n_sims=n_sims,
        fpr_final_only=float(significant[:, -1].mean()),
        fpr_any_peek=float(significant.any(axis=1).mean()),
    )


# ---------------------------------------------------------------------------
# Demo helpers + main
# ---------------------------------------------------------------------------

def simulate_paired_outcomes(
    p0: float,
    p1: float,
    rho: float,
    n_tasks: int,
    seed: int = 0,
) -> Tuple[np.ndarray, np.ndarray]:
    """Sample correlated paired Bernoulli outcomes for n_tasks tasks.

    Draws each task from the exact 2x2 joint distribution implied by the
    marginals (p0, p1) and within-task correlation rho -- the generative
    model behind ``paired_trials_needed``.
    """
    _validate_proportion("p0", p0)
    _validate_proportion("p1", p1)
    if not (0.0 <= rho < 1.0):
        raise ValueError("rho must be in [0, 1), got %r" % rho)
    if n_tasks < 1:
        raise ValueError("n_tasks must be >= 1, got %r" % n_tasks)

    cov = rho * math.sqrt(p0 * (1.0 - p0) * p1 * (1.0 - p1))
    p11 = p0 * p1 + cov
    cells = np.array([p11, p0 - p11, p1 - p11, 1.0 - p0 - p1 + p11])
    if np.any(cells < 0.0):
        raise ValueError("rho=%r infeasible for marginals p0=%r p1=%r" % (rho, p0, p1))

    rng = np.random.default_rng(seed)
    draw = rng.choice(4, size=n_tasks, p=cells)   # 0:both, 1:A-only, 2:B-only, 3:neither
    a = (draw == 0) | (draw == 1)
    b = (draw == 0) | (draw == 2)
    return a, b


def main() -> None:
    """End-to-end demo: sizing, running, and reading a robot policy eval."""
    sep = "-" * 72

    print(sep)
    print("[1] Wilson CI -- what does a small real-robot eval actually tell you?")
    print(sep)
    for k, n in ((45, 50), (63, 70), (180, 200), (900, 1000)):
        ci = wilson_ci(k, n)
        print("  %4d/%4d trials  ->  %s" % (k, n, ci))
    print("  => 50 trials around 90% success is roughly a +/-8pp interval;")
    print("     you cannot see a 5pp policy improvement in that noise.")

    print()
    print(sep)
    print("[2] trials_needed -- size the eval BEFORE running it")
    print(sep)
    for p0, d in ((0.50, 0.05), (0.80, 0.05), (0.90, 0.05), (0.50, 0.10), (0.80, 0.10)):
        ss = trials_needed(p0, d)
        print("  %s" % ss)
    ref = trials_needed(0.80, 0.05)
    print(
        "  => 80%%->85%% detection: exact %.1f, schedule %d/arm "
        "(prep docs quote '~905', the un-ceiled value rounded)."
        % (ref.n_exact, ref.n_per_arm)
    )
    print("  => at 100-200 real trials/robot/day, ~900/arm is a week of robot")
    print("     time -- so sim carries statistical power, real robots gate.")

    print()
    print(sep)
    print("[3] paired_compare -- A/B on the SAME tasks (McNemar)")
    print(sep)
    rho = 0.6
    a, b = simulate_paired_outcomes(p0=0.80, p1=0.85, rho=rho, n_tasks=400, seed=7)
    res = paired_compare(a, b)
    print("  simulated 400 shared tasks (true 80%% vs 85%%, rho=%.1f):" % rho)
    print("  %s" % res)
    indep = trials_needed(0.80, 0.05)
    paired = paired_trials_needed(0.80, 0.05, rho=rho)
    savings = indep.n_exact / paired.n_exact
    print(
        "  design cost: independent %d/arm = %d robot runs total, vs paired "
        "%d task pairs = %d runs total  ->  %.1fx fewer robot runs"
        % (indep.n_per_arm, 2 * indep.n_per_arm,
           paired.n_per_arm, 2 * paired.n_per_arm, savings)
    )

    print()
    print(sep)
    print("[4] bootstrap_diff_ci -- assumption-light CI on the same data")
    print(sep)
    ci_paired = bootstrap_diff_ci(a, b, paired=True, seed=11)
    ci_indep = bootstrap_diff_ci(a, b, paired=False, seed=11)
    print("  paired bootstrap:      %s" % ci_paired)
    print("  independent bootstrap: %s" % ci_indep)
    print("  => same data, but respecting the pairing gives a tighter CI.")

    print()
    print(sep)
    print("[5] peeking_inflation_sim -- the sequential-testing trap")
    print(sep)
    peek = peeking_inflation_sim(p=0.80, n_max=1000, peek_every=50,
                                 alpha=0.05, n_sims=2000, seed=3)
    print("  %s" % peek)
    print("  => 'run until significant' turns a 5%% test into a ~%.0f%% test;"
          % (100 * peek.fpr_any_peek))
    print("     pre-register n (from [2]) or use alpha-spending corrections.")


if __name__ == "__main__":
    main()
