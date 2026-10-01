#!/usr/bin/env python3
"""Tests for lab6: the fixed BC trainer must converge, evaluate
deterministically, and beat the buggy trainer by a wide margin.

Run:
    python3 test_fixed.py

Plain asserts only -- no pytest dependency. Everything is seeded, so all
comparisons (including exact float equality for determinism checks) are
stable on this pinned environment (CPU, torch 2.8, numpy 2.0.2).
"""

import contextlib
import io
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import torch

import buggy_train
import fixed_train


def run_silently(module) -> dict:
    """Run a module's experiment while swallowing its per-epoch prints."""
    sink = io.StringIO()
    with contextlib.redirect_stdout(sink):
        metrics = module.run_experiment(module.TrainConfig())
    return metrics


def main() -> None:
    start = time.time()

    print("[1/4] training buggy_train ...")
    buggy = run_silently(buggy_train)
    print("[2/4] training fixed_train ...")
    fixed = run_silently(fixed_train)
    print("[3/4] re-training fixed_train (determinism check) ...")
    fixed_again = run_silently(fixed_train)
    print("[4/4] asserting ...")

    # --- 1. fixed trainer converges -------------------------------------
    assert fixed["final_epoch_train_loss"] < 0.5 * fixed["first_epoch_train_loss"], (
        "fixed loss did not drop: first=%.4f final=%.4f"
        % (fixed["first_epoch_train_loss"], fixed["final_epoch_train_loss"])
    )
    assert fixed["final_epoch_train_loss"] < 0.15, (
        "fixed final loss too high: %.4f" % fixed["final_epoch_train_loss"]
    )

    # --- 2. fixed policy actually reaches goals -------------------------
    assert fixed["success_rate_first"] >= 0.90, (
        "fixed success rate too low: %.3f" % fixed["success_rate_first"]
    )

    # --- 3. fixed evaluation is repeatable (model.eval + no_grad) -------
    assert fixed["success_rate_first"] == fixed["success_rate_second"], (
        "fixed rollout eval not repeatable: %.3f vs %.3f"
        % (fixed["success_rate_first"], fixed["success_rate_second"])
    )
    assert fixed["final_val_mse"] == fixed["final_val_mse_recheck"], (
        "fixed val MSE not repeatable: %.6f vs %.6f"
        % (fixed["final_val_mse"], fixed["final_val_mse_recheck"])
    )

    # --- 4. buggy policy is far worse in closed loop --------------------
    buggy_best = max(buggy["success_rate_first"], buggy["success_rate_second"])
    assert buggy_best <= 0.5, "buggy success unexpectedly high: %.3f" % buggy_best
    gap = fixed["success_rate_first"] - buggy_best
    assert gap >= 0.4, (
        "success gap too small: fixed=%.3f buggy=%.3f gap=%.3f"
        % (fixed["success_rate_first"], buggy_best, gap)
    )

    # --- 5. buggy evaluation is NOT repeatable (dropout left on) --------
    assert buggy["final_val_mse"] != buggy["final_val_mse_recheck"], (
        "buggy val MSE should jitter (dropout active during eval)"
    )
    assert buggy["success_rate_first"] != buggy["success_rate_second"], (
        "buggy rollout success should jitter (dropout active during eval)"
    )

    # --- 6. direct probe: train-mode forward pass is stochastic ---------
    torch.manual_seed(123)
    net = buggy_train.PolicyNet(obs_dim=4, action_dim=2, hidden_dim=32, dropout=0.15)
    net.train()
    x = torch.randn(16, 4)
    out_a = net(x).detach()
    out_b = net(x).detach()
    assert not torch.equal(out_a, out_b), (
        "two train-mode forward passes matched; dropout probe is broken"
    )

    # --- 7. masked_mse ignores padded timesteps -------------------------
    pred = torch.zeros(2, 3, 2)
    target = torch.zeros(2, 3, 2)
    lengths = torch.tensor([1, 3])
    pred[0, 1:] = 5.0  # garbage on sample 0's PADDED steps only
    masked = fixed_train.masked_mse(pred, target, lengths).item()
    unmasked = torch.nn.functional.mse_loss(pred, target).item()
    assert masked == 0.0, "masked_mse leaked padding: %.4f" % masked
    assert unmasked > 0.0, "unmasked control should be nonzero"

    # --- 8. fixed pipeline is fully deterministic across runs -----------
    for key in fixed:
        assert fixed[key] == fixed_again[key], (
            "fixed run not reproducible for %s: %r vs %r"
            % (key, fixed[key], fixed_again[key])
        )

    elapsed = time.time() - start
    assert elapsed < 60.0, "test suite too slow: %.1fs" % elapsed

    print("-" * 64)
    print("buggy : success #1=%.3f #2=%.3f | val MSE #1=%.4f #2=%.4f"
          % (buggy["success_rate_first"], buggy["success_rate_second"],
             buggy["final_val_mse"], buggy["final_val_mse_recheck"]))
    print("fixed : success #1=%.3f #2=%.3f | val MSE #1=%.4f #2=%.4f"
          % (fixed["success_rate_first"], fixed["success_rate_second"],
             fixed["final_val_mse"], fixed["final_val_mse_recheck"]))
    print("gap   : %.3f (assert >= 0.4)" % gap)
    print("ALL TESTS PASSED in %.1fs" % elapsed)


if __name__ == "__main__":
    main()
