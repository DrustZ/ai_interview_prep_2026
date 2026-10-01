"""Plain-assert tests for evalstats.py (no pytest).

Run:  /Users/mingrui/Documents/codes/interview/.venv/bin/python test_evalstats.py

Pins the interview-critical numbers:
  * 80%->85% @ power 0.8, alpha 0.05  ->  ~905 exact, 906 scheduled per arm
  * 50%->55%                          ->  1565 per arm (harder near 50%)
  * paired design at rho=0.6          ->  >2x fewer robot runs
  * peeking every 50 trials           ->  alpha inflates 5% -> ~20-30%
"""

import math

import numpy as np

from evalstats import (
    bootstrap_diff_ci,
    paired_compare,
    paired_trials_needed,
    peeking_inflation_sim,
    simulate_paired_outcomes,
    trials_needed,
    wilson_ci,
)


def expect_value_error(fn, *args, **kwargs):
    try:
        fn(*args, **kwargs)
    except ValueError:
        return
    raise AssertionError(
        "%s(%r, %r) should have raised ValueError" % (fn.__name__, args, kwargs)
    )


def test_wilson_ci():
    # The prep-doc talking point: ~50 trials at 90% success -> roughly +/-8pp.
    ci = wilson_ci(45, 50)
    assert ci.point == 0.9
    assert 0.78 < ci.lower < 0.80, ci
    assert 0.95 < ci.upper < 0.96, ci
    assert 0.07 < ci.half_width < 0.09, ci

    # More trials -> tighter interval, same point.
    ci_big = wilson_ci(900, 1000)
    assert ci_big.half_width < 0.025, ci_big
    assert ci_big.half_width < ci.half_width

    # Stays inside [0, 1] at the edges (where Wald breaks).
    ci0 = wilson_ci(0, 20)
    ciN = wilson_ci(20, 20)
    assert ci0.lower == 0.0 and ci0.upper > 0.0, ci0
    assert ciN.upper == 1.0 and ciN.lower < 1.0, ciN
    assert ciN.lower < 0.9  # 20/20 does NOT prove a 90% policy

    # Higher confidence -> wider interval.
    assert wilson_ci(45, 50, confidence=0.99).half_width > ci.half_width

    # Input validation.
    expect_value_error(wilson_ci, 5, 0)
    expect_value_error(wilson_ci, 11, 10)
    expect_value_error(wilson_ci, -1, 10)
    expect_value_error(wilson_ci, 5, 10, confidence=1.0)
    print("PASS test_wilson_ci")


def test_trials_needed_headline_numbers():
    # 80% -> 85%: prep docs quote ~905/arm; that is the un-ceiled formula
    # value (905.4). We schedule ceil() = 906.
    ss = trials_needed(0.80, 0.05, power=0.80, alpha=0.05)
    assert round(ss.n_exact) == 905, ss.n_exact       # doc figure
    assert ss.n_per_arm == 906, ss.n_per_arm          # what we schedule
    assert 900 < ss.n_exact < 910
    assert math.isclose(ss.p1, 0.85)

    # 50% -> 55% needs MORE (variance p(1-p) peaks at 0.5): doc says ~1,565.
    ss50 = trials_needed(0.50, 0.05)
    assert ss50.n_per_arm == 1565, ss50.n_per_arm
    assert ss50.n_per_arm > 1500
    assert ss50.n_per_arm > ss.n_per_arm

    # 90% -> 95%: doc says ~434 (rounded); exact 434.4, scheduled 435.
    ss90 = trials_needed(0.90, 0.05)
    assert round(ss90.n_exact) == 434, ss90.n_exact
    assert ss90.n_per_arm == 435, ss90.n_per_arm

    # Bigger effect -> far fewer trials (10pp from 80%: ~199).
    ss10 = trials_needed(0.80, 0.10)
    assert ss10.n_per_arm == 199, ss10.n_per_arm

    # Symmetric in direction: detecting 85% -> 80% costs the same.
    assert trials_needed(0.85, -0.05).n_per_arm == ss.n_per_arm

    # Higher power / stricter alpha -> more trials.
    assert trials_needed(0.80, 0.05, power=0.90).n_per_arm > ss.n_per_arm
    assert trials_needed(0.80, 0.05, alpha=0.01).n_per_arm > ss.n_per_arm

    # Input validation.
    expect_value_error(trials_needed, 0.80, 0.0)
    expect_value_error(trials_needed, 0.80, 0.25)     # p1 = 1.05
    expect_value_error(trials_needed, 0.0, 0.05)
    expect_value_error(trials_needed, 0.80, 0.05, power=1.0)
    print("PASS test_trials_needed_headline_numbers")


def test_paired_compare_mcnemar():
    # Known exact value: b=5 A-only, c=15 B-only, 20 discordant of 100 tasks.
    # Two-sided exact p = 2 * P(Binom(20, 0.5) <= 5) = 43400/2^20 ~= 0.041390.
    a = np.zeros(100, dtype=bool)
    b = np.zeros(100, dtype=bool)
    a[:60] = True; b[:60] = True          # 60 both succeed
    a[60:65] = True                        # 5 A-only
    b[65:80] = True                        # 15 B-only
    res = paired_compare(a, b)
    assert res.n_pairs == 100
    assert res.n_a_only == 5 and res.n_b_only == 15
    assert abs(res.p_exact - 0.041389465) < 1e-6, res.p_exact
    assert res.p_exact < 0.05              # significant at 5%
    assert abs(res.diff - 0.10) < 1e-12
    assert abs(res.discordant_rate - 0.20) < 1e-12
    # Continuity-corrected approximation is in the same ballpark.
    assert abs(res.p_approx - res.p_exact) < 0.02, res

    # Symmetric discordance -> no evidence either way.
    a2 = np.array([True, False, True, False])
    b2 = np.array([False, True, False, True])
    res2 = paired_compare(a2, b2)
    assert res2.p_exact == 1.0

    # Identical outcomes -> zero discordant pairs, p = 1.
    same = np.array([True, True, False])
    res3 = paired_compare(same, same)
    assert res3.p_exact == 1.0 and res3.p_approx == 1.0

    # Input validation.
    expect_value_error(paired_compare, [True, False], [True])
    expect_value_error(paired_compare, [], [])
    print("PASS test_paired_compare_mcnemar")


def test_paired_design_savings():
    indep = trials_needed(0.80, 0.05)
    paired = paired_trials_needed(0.80, 0.05, rho=0.6)
    # At rho=0.6 the paired design needs ~371 task pairs vs 906 per arm.
    assert paired.n_per_arm == 371, paired.n_per_arm
    savings = indep.n_exact / paired.n_exact
    assert savings > 2.0, savings                     # headline: >2x fewer runs
    assert 2.3 < savings < 2.6, savings               # ~2.4x at rho=0.6

    # rho=0 (no shared task difficulty) ~ recovers the independent answer.
    paired0 = paired_trials_needed(0.80, 0.05, rho=0.0)
    assert abs(paired0.n_exact - indep.n_exact) / indep.n_exact < 0.01

    # More correlation -> fewer pairs needed (monotone).
    n_by_rho = [paired_trials_needed(0.80, 0.05, rho=r).n_per_arm
                for r in (0.0, 0.3, 0.6)]
    assert n_by_rho[0] > n_by_rho[1] > n_by_rho[2], n_by_rho

    # Infeasible correlation for these marginals must be rejected.
    expect_value_error(paired_trials_needed, 0.80, 0.05, rho=0.99)
    expect_value_error(paired_trials_needed, 0.80, 0.05, rho=-0.1)
    print("PASS test_paired_design_savings")


def test_simulated_paired_eval_end_to_end():
    # Generative model matches the sizing model: at the recommended n_pairs,
    # a true 5pp improvement should usually be detected (power ~ 0.8).
    n_pairs = paired_trials_needed(0.80, 0.05, rho=0.6).n_per_arm
    detected = 0
    n_reps = 200
    for rep in range(n_reps):
        a, b = simulate_paired_outcomes(0.80, 0.85, rho=0.6,
                                        n_tasks=n_pairs, seed=1000 + rep)
        if paired_compare(a, b).p_exact < 0.05:
            detected += 1
    power_hat = detected / n_reps
    assert 0.68 < power_hat < 0.92, power_hat         # ~0.8 +/- MC noise
    print("PASS test_simulated_paired_eval_end_to_end (power_hat=%.2f)" % power_hat)


def test_bootstrap_diff_ci():
    a, b = simulate_paired_outcomes(0.80, 0.85, rho=0.6, n_tasks=600, seed=42)
    true_diff = float(b.mean() - a.mean())

    ci = bootstrap_diff_ci(a, b, paired=True, n_boot=2000, seed=0)
    assert abs(ci.point - true_diff) < 1e-12
    assert ci.lower < true_diff < ci.upper
    assert ci.upper - ci.lower < 0.12                 # sane width at n=600

    # Deterministic for a fixed seed.
    ci_again = bootstrap_diff_ci(a, b, paired=True, n_boot=2000, seed=0)
    assert (ci.lower, ci.upper) == (ci_again.lower, ci_again.upper)

    # Pairing exploits shared task difficulty -> tighter CI than treating
    # the two arms as independent samples of the same data.
    ci_indep = bootstrap_diff_ci(a, b, paired=False, n_boot=2000, seed=0)
    assert (ci.upper - ci.lower) < (ci_indep.upper - ci_indep.lower), \
        (ci, ci_indep)

    # Input validation.
    expect_value_error(bootstrap_diff_ci, a, b[:-1], paired=True)
    expect_value_error(bootstrap_diff_ci, a, b, n_boot=10)
    print("PASS test_bootstrap_diff_ci")


def test_peeking_inflation():
    res = peeking_inflation_sim(p=0.80, n_max=1000, peek_every=50,
                                alpha=0.05, n_sims=2000, seed=3)
    assert res.n_peeks == 20
    # Single pre-registered look is calibrated near the nominal 5%.
    assert 0.03 < res.fpr_final_only < 0.075, res.fpr_final_only
    # Peeking every 50 trials inflates alpha to roughly 20-30%.
    assert 0.15 < res.fpr_any_peek < 0.35, res.fpr_any_peek
    assert res.fpr_any_peek > 3.0 * res.fpr_final_only
    assert res.inflation_factor > 3.0

    # More looks -> more inflation (5 looks vs 20 looks).
    res_few = peeking_inflation_sim(p=0.80, n_max=1000, peek_every=200,
                                    alpha=0.05, n_sims=2000, seed=3)
    assert res_few.fpr_any_peek < res.fpr_any_peek

    # Input validation.
    expect_value_error(peeking_inflation_sim, p=1.5)
    expect_value_error(peeking_inflation_sim, n_max=10, peek_every=50)
    expect_value_error(peeking_inflation_sim, n_sims=5)
    print("PASS test_peeking_inflation (fpr_any_peek=%.3f)" % res.fpr_any_peek)


def main():
    test_wilson_ci()
    test_trials_needed_headline_numbers()
    test_paired_compare_mcnemar()
    test_paired_design_savings()
    test_simulated_paired_eval_end_to_end()
    test_bootstrap_diff_ci()
    test_peeking_inflation()
    print("ALL TESTS PASSED")


if __name__ == "__main__":
    main()
