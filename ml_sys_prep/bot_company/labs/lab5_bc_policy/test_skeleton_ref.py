"""Grader for the cold-write skeleton.

Default run checks that the REFERENCE implementation (train_bc.py) passes
every assertion -- proving the grader itself is sound:

    <python> test_skeleton_ref.py

After you fill in skeleton.py, point the grader at your version:

    BC_IMPL=skeleton <python> test_skeleton_ref.py

It also verifies that skeleton.py keeps the exact public surface, so the
cold-write target never drifts away from the reference.
"""

import importlib
import os

import numpy as np
import torch

from env import EnvConfig, ExpertConfig, NavGraspEnv, scripted_expert_action

IMPL_NAME = os.environ.get("BC_IMPL", "train_bc")
impl = importlib.import_module(IMPL_NAME)

REQUIRED_NAMES = (
    "Normalizer", "ActionDiscretizer", "make_action_discretizer",
    "split_train_val", "MLPPolicy", "mse_loss", "discrete_ce_loss",
    "train_one_epoch", "eval_loss", "make_policy_fn", "rollout_policy",
)


def test_skeleton_keeps_the_same_public_surface() -> None:
    skeleton = importlib.import_module("skeleton")
    for name in REQUIRED_NAMES:
        assert hasattr(skeleton, name), "skeleton.py lost symbol %r" % name
        assert hasattr(impl, name), "%s lost symbol %r" % (IMPL_NAME, name)


def test_normalizer() -> None:
    rng = np.random.default_rng(0)
    x = rng.normal(-2.0, 5.0, size=(300, 4)).astype(np.float32)
    x[:, 1] = 42.0  # constant column
    norm = impl.Normalizer().fit(x)
    z = norm.transform(x)
    assert z.shape == x.shape and z.dtype == np.float32
    assert np.all(np.isfinite(z)), "constant column must not produce NaN/inf"
    assert np.all(np.abs(z[:, [0, 2, 3]].mean(axis=0)) < 1e-4)
    assert np.all(np.abs(z[:, [0, 2, 3]].std(axis=0) - 1.0) < 1e-3)
    single = norm.transform(x[0])  # (D,) must also work (rollout path)
    assert single.shape == (4,)
    try:
        impl.Normalizer().transform(x)
        raise AssertionError("transform before fit must raise RuntimeError")
    except RuntimeError:
        pass


def test_split_train_val() -> None:
    tr, va = impl.split_train_val(50, 0.2, seed=3)
    assert len(tr) == 40 and len(va) == 10
    assert sorted(list(tr) + list(va)) == list(range(50))
    tr2, va2 = impl.split_train_val(50, 0.2, seed=3)
    assert np.array_equal(tr, tr2) and np.array_equal(va, va2)
    try:
        impl.split_train_val(50, 1.5, seed=0)
        raise AssertionError("bad val_fraction must raise ValueError")
    except ValueError:
        pass


def test_discretizer() -> None:
    disc = impl.make_action_discretizer(EnvConfig(), n_bins=8)
    speed = EnvConfig().max_speed
    a = np.array([[-speed, speed, 0.0], [0.0, 0.0, 1.0]], dtype=np.float32)
    idx = disc.encode(a)
    assert idx.dtype == np.int64 and idx.shape == (2, 3)
    assert idx[0, 0] == 0 and idx[0, 1] == 7, "extremes map to boundary bins"
    assert idx[0, 2] == 0 and idx[1, 2] == 7, "grasp 0/1 map to first/last bin"
    rng = np.random.default_rng(4)
    rand = np.stack([
        rng.uniform(-speed, speed, 100),
        rng.uniform(-speed, speed, 100),
        rng.uniform(0, 1, 100),
    ], axis=1)
    err = np.abs(disc.decode(disc.encode(rand)) - rand)
    assert np.all(err <= np.asarray(disc.bin_width) / 2 + 1e-9)
    try:
        disc.decode(np.array([[0, 3, 8]]))  # 8 is out of range
        raise AssertionError("out-of-range index must raise ValueError")
    except ValueError:
        pass


def test_model_and_losses() -> None:
    torch.manual_seed(0)
    x = torch.randn(6, 4)
    reg = impl.MLPPolicy(hidden_dim=16, n_bins=None)
    out = reg(x)
    assert out.shape == (6, 3)
    cat = impl.MLPPolicy(hidden_dim=16, n_bins=5)
    logits = cat(x)
    assert logits.shape == (6, 3, 5)

    pred = torch.tensor([[1.0, 0.0, 0.0]])
    target = torch.tensor([[0.0, 0.0, 0.0]])
    got = float(impl.mse_loss(pred, target).item())
    assert abs(got - 1.0 / 3.0) < 1e-6, "mse_loss must mean over all elements"

    # hand-checkable CE: uniform logits over 5 bins -> loss = log(5)
    logits = torch.zeros(2, 3, 5)
    tgt = torch.zeros(2, 3, dtype=torch.long)
    got = float(impl.discrete_ce_loss(logits, tgt).item())
    assert abs(got - float(np.log(5.0))) < 1e-5


def test_training_reduces_loss() -> None:
    """train_one_epoch + eval_loss must actually optimize a simple problem."""
    torch.manual_seed(1)
    x = torch.randn(512, 4)
    true_w = torch.randn(4, 3)
    y = x @ true_w
    model = impl.MLPPolicy(hidden_dim=32, n_bins=None)
    opt = torch.optim.Adam(model.parameters(), lr=1e-2)
    gen = torch.Generator().manual_seed(0)
    before = impl.eval_loss(model, impl.mse_loss, x, y)
    for _ in range(10):
        impl.train_one_epoch(model, opt, impl.mse_loss, x, y, 64, gen)
    after = impl.eval_loss(model, impl.mse_loss, x, y)
    assert after < before * 0.2, (
        "10 epochs on a linear task should cut MSE by >5x: %.4f -> %.4f"
        % (before, after))


def test_policy_fn_and_rollout() -> None:
    # make_policy_fn output contract (untrained model is fine for shapes)
    torch.manual_seed(2)
    obs_stats = np.random.default_rng(5).normal(size=(100, 4)).astype(np.float32)
    norm = impl.Normalizer().fit(obs_stats)
    disc = impl.make_action_discretizer(EnvConfig(), n_bins=8)

    reg_fn = impl.make_policy_fn(impl.MLPPolicy(hidden_dim=16), norm, None)
    a = reg_fn(obs_stats[0])
    assert a.shape == (3,) and a.dtype == np.float32

    cat_fn = impl.make_policy_fn(
        impl.MLPPolicy(hidden_dim=16, n_bins=8), norm, disc)
    a = cat_fn(obs_stats[0])
    assert a.shape == (3,) and a.dtype == np.float32
    # each decoded dim must be one of that dim's 8 bin centers
    all_centers = disc.decode(np.stack([np.arange(8)] * 3, axis=1))  # (8, 3)
    for d in range(3):
        assert np.any(np.abs(all_centers[:, d] - a[d]) < 1e-6), (
            "discrete policy output must be a bin center, got %r" % a)

    # rollout_policy with the scripted expert must be perfect
    env = NavGraspEnv(EnvConfig(), seed=9)
    rng = np.random.default_rng(9)

    def expert_fn(obs: np.ndarray) -> np.ndarray:
        return scripted_expert_action(
            obs, "right", EnvConfig(), ExpertConfig(), rng)

    stats = impl.rollout_policy(env, expert_fn, n_episodes=10)
    assert stats["success_rate"] == 1.0, (
        "expert rollout must always succeed, got %s" % stats)
    assert stats["collision_rate"] == 0.0
    assert 0 < stats["avg_steps"] < EnvConfig().max_steps
    try:
        impl.rollout_policy(env, expert_fn, n_episodes=0)
        raise AssertionError("n_episodes=0 must raise ValueError")
    except ValueError:
        pass


if __name__ == "__main__":
    test_skeleton_keeps_the_same_public_surface()
    test_normalizer()
    test_split_train_val()
    test_discretizer()
    test_model_and_losses()
    test_training_reduces_loss()
    test_policy_fn_and_rollout()
    print("test_skeleton_ref.py [%s]: ALL PASSED" % IMPL_NAME)
