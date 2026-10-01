"""Tests for train_bc.py, including the lab's core claim:

    same demos + same MLP trunk, MSE head fails / discretized CE head works.

Run:  <python> test_train_bc.py     (plain asserts, no pytest; ~10 s CPU)
"""

import numpy as np
import torch

from env import EnvConfig
from train_bc import (
    MLPPolicy,
    Normalizer,
    TrainConfig,
    check_experiment_metrics,
    discrete_ce_loss,
    make_action_discretizer,
    mse_loss,
    run_experiment,
    split_train_val,
)


def test_normalizer_basics() -> None:
    rng = np.random.default_rng(0)
    x = rng.normal(3.0, 2.0, size=(500, 4)).astype(np.float32)
    x[:, 2] = 7.0  # constant column must not blow up
    z = Normalizer().fit(x).transform(x)
    assert z.dtype == np.float32 and z.shape == x.shape
    assert np.all(np.abs(z[:, [0, 1, 3]].mean(axis=0)) < 1e-4)
    assert np.all(np.abs(z[:, [0, 1, 3]].std(axis=0) - 1.0) < 1e-3)
    assert np.all(np.isfinite(z))
    try:
        Normalizer().transform(x)
        raise AssertionError("transform before fit must raise RuntimeError")
    except RuntimeError:
        pass


def test_discretizer_round_trip() -> None:
    disc = make_action_discretizer(EnvConfig(), n_bins=8)
    rng = np.random.default_rng(1)
    speed = EnvConfig().max_speed
    actions = np.stack([
        rng.uniform(-speed, speed, size=200),
        rng.uniform(-speed, speed, size=200),
        rng.uniform(0.0, 1.0, size=200),
    ], axis=1).astype(np.float32)
    idx = disc.encode(actions)
    assert idx.shape == actions.shape and idx.dtype == np.int64
    assert idx.min() >= 0 and idx.max() < 8
    recon = disc.decode(idx)
    assert np.all(np.abs(recon - actions) <= disc.bin_width / 2 + 1e-9), (
        "round-trip error must stay within half a bin width")
    # out-of-range actions clip into the boundary bins
    wild = np.array([[10.0, -10.0, 5.0]], dtype=np.float32)
    widx = disc.encode(wild)
    assert widx[0, 0] == 7 and widx[0, 1] == 0 and widx[0, 2] == 7


def test_split_train_val() -> None:
    tr, va = split_train_val(100, 0.1, seed=0)
    assert len(tr) == 90 and len(va) == 10
    assert set(tr.tolist()).isdisjoint(va.tolist())
    assert sorted(tr.tolist() + va.tolist()) == list(range(100))
    tr2, va2 = split_train_val(100, 0.1, seed=0)
    assert np.array_equal(tr, tr2) and np.array_equal(va, va2)


def test_model_output_shapes() -> None:
    torch.manual_seed(0)
    x = torch.randn(5, 4)
    reg = MLPPolicy(hidden_dim=16, n_bins=None)
    assert reg(x).shape == (5, 3)
    cat = MLPPolicy(hidden_dim=16, n_bins=8)
    logits = cat(x)
    assert logits.shape == (5, 3, 8)
    assert float(mse_loss(reg(x), torch.zeros(5, 3)).item()) >= 0.0
    assert float(discrete_ce_loss(logits, torch.zeros(5, 3).long()).item()) > 0.0


def test_core_claim_mse_fails_discrete_wins() -> None:
    """The headline experiment: run once end-to-end and check the gap."""
    results = run_experiment(TrainConfig(), verbose=False)
    check_experiment_metrics(results)  # raises AssertionError on regression
    # spell out the headline numbers for the log
    print("  mse:      success %.2f, collision %.2f"
          % (results["mse"]["success_rate"], results["mse"]["collision_rate"]))
    print("  discrete: success %.2f, collision %.2f"
          % (results["discrete"]["success_rate"],
             results["discrete"]["collision_rate"]))


if __name__ == "__main__":
    test_normalizer_basics()
    test_discretizer_round_trip()
    test_split_train_val()
    test_model_output_shapes()
    test_core_claim_mse_fails_discrete_wins()
    print("test_train_bc.py: ALL PASSED")
