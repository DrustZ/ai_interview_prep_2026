"""Behavior cloning on bimodal demonstrations: MSE head vs discretized head.

This file is deliberately written as a *textbook* PyTorch training loop --
the goal is that you can cold-write every function here from memory:

    Normalizer            fit/transform observation statistics (train split only!)
    ActionDiscretizer     continuous action  <->  per-dimension bin index
    MLPPolicy             MLP with either a regression or a logits head
    mse_loss              regression objective (the one that mode-averages)
    discrete_ce_loss      per-dimension cross-entropy (minimal action tokenization)
    train_one_epoch       shuffled minibatch SGD pass
    eval_loss             full-batch validation loss under no_grad
    train_policy          epoch loop + early stopping on val loss
    make_policy_fn        model -> obs->action closure for rollouts
    rollout_policy        closed-loop evaluation: success / collision rates

Experiment (run_experiment): identical data, identical MLP trunk, only the
head + loss differ. The MSE head averages the left/right detour modes and
drives into the obstacle; the discretized cross-entropy head keeps the two
modes as separate probability mass and commits to one. main() asserts the gap.

Run:  python3 train_bc.py       (CPU, < 60 s)
"""

import copy
import time
from dataclasses import dataclass
from typing import Callable, Dict, List, Optional, Tuple

import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F

from env import (
    ACT_DIM,
    OBS_DIM,
    DemoBatch,
    EnvConfig,
    NavGraspEnv,
    collect_demonstrations,
)

PolicyFn = Callable[[np.ndarray], np.ndarray]  # obs (4,) -> action (3,)


# ---------------------------------------------------------------------------
# Data plumbing
# ---------------------------------------------------------------------------

class Normalizer:
    """Standardize inputs with statistics from the *training* split.

    Shapes: fit/transform take (N, D); transform also accepts (D,).
    """

    def __init__(self) -> None:
        self.mean: Optional[np.ndarray] = None
        self.std: Optional[np.ndarray] = None

    def fit(self, x: np.ndarray) -> "Normalizer":
        if x.ndim != 2:
            raise ValueError("fit expects (N, D), got shape %s" % (x.shape,))
        self.mean = x.mean(axis=0)
        # Floor the std so constant features do not divide by zero.
        self.std = np.maximum(x.std(axis=0), 1e-6)
        return self

    def transform(self, x: np.ndarray) -> np.ndarray:
        if self.mean is None or self.std is None:
            raise RuntimeError("Normalizer.transform called before fit()")
        return ((x - self.mean) / self.std).astype(np.float32)


@dataclass(frozen=True)
class ActionDiscretizer:
    """Uniform per-dimension binning: the minimal form of action tokenization.

    low/high: (act_dim,) bounds per dimension; values outside are clipped.
    encode:  (N, act_dim) float  -> (N, act_dim) int64 bin indices
    decode:  (..., act_dim) int  -> (..., act_dim) float32 bin centers
    """

    low: np.ndarray
    high: np.ndarray
    n_bins: int

    @property
    def bin_width(self) -> np.ndarray:
        return (self.high - self.low) / float(self.n_bins)

    def encode(self, actions: np.ndarray) -> np.ndarray:
        a = np.clip(np.asarray(actions, dtype=np.float64), self.low, self.high)
        idx = np.floor((a - self.low) / self.bin_width).astype(np.int64)
        return np.clip(idx, 0, self.n_bins - 1)  # a == high maps to last bin

    def decode(self, indices: np.ndarray) -> np.ndarray:
        idx = np.asarray(indices, dtype=np.float64)
        if np.any(idx < 0) or np.any(idx >= self.n_bins):
            raise ValueError("bin index out of range [0, %d)" % self.n_bins)
        return (self.low + (idx + 0.5) * self.bin_width).astype(np.float32)


def make_action_discretizer(env_cfg: EnvConfig, n_bins: int) -> ActionDiscretizer:
    """Bounds: (dx, dy) in [-max_speed, max_speed]; grasp in [0, 1]."""
    s = env_cfg.max_speed
    return ActionDiscretizer(
        low=np.array([-s, -s, 0.0]),
        high=np.array([s, s, 1.0]),
        n_bins=n_bins,
    )


def split_train_val(
    n: int, val_fraction: float, seed: int
) -> Tuple[np.ndarray, np.ndarray]:
    """Shuffled index split. Returns (train_idx, val_idx)."""
    if not 0.0 < val_fraction < 1.0:
        raise ValueError("val_fraction must be in (0, 1), got %s" % val_fraction)
    rng = np.random.default_rng(seed)
    perm = rng.permutation(n)
    n_val = max(1, int(round(n * val_fraction)))
    return perm[n_val:], perm[:n_val]


# ---------------------------------------------------------------------------
# Model + losses
# ---------------------------------------------------------------------------

class MLPPolicy(nn.Module):
    """Two-hidden-layer MLP.

    n_bins=None -> regression head:  forward (B, obs_dim) -> (B, act_dim)
    n_bins=K    -> logits head:      forward (B, obs_dim) -> (B, act_dim, K)
    """

    def __init__(
        self,
        obs_dim: int = OBS_DIM,
        act_dim: int = ACT_DIM,
        hidden_dim: int = 128,
        n_bins: Optional[int] = None,
    ) -> None:
        super().__init__()
        self.act_dim = act_dim
        self.n_bins = n_bins
        out_dim = act_dim if n_bins is None else act_dim * n_bins
        self.net = nn.Sequential(
            nn.Linear(obs_dim, hidden_dim),
            nn.ReLU(),
            nn.Linear(hidden_dim, hidden_dim),
            nn.ReLU(),
            nn.Linear(hidden_dim, out_dim),
        )

    def forward(self, obs: torch.Tensor) -> torch.Tensor:
        out = self.net(obs)
        if self.n_bins is not None:
            out = out.view(-1, self.act_dim, self.n_bins)
        return out


def mse_loss(pred: torch.Tensor, target: torch.Tensor) -> torch.Tensor:
    """pred (B, act_dim) float, target (B, act_dim) float -> scalar."""
    return F.mse_loss(pred, target)


def discrete_ce_loss(logits: torch.Tensor, target_idx: torch.Tensor) -> torch.Tensor:
    """logits (B, act_dim, n_bins), target_idx (B, act_dim) int64 -> scalar.

    Cross-entropy per action dimension, averaged. Unlike MSE this represents
    a full distribution over bins, so two demonstration modes stay two peaks.
    """
    n_bins = logits.shape[-1]
    return F.cross_entropy(logits.reshape(-1, n_bins), target_idx.reshape(-1))


# ---------------------------------------------------------------------------
# Training loop
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class TrainConfig:
    seed: int = 0
    n_demos: int = 100                # alternating left/right => exact 50/50
    hidden_dim: int = 128
    n_bins: int = 8
    batch_size: int = 256
    lr: float = 1e-3
    weight_decay: float = 1e-4
    max_epochs: int = 50
    patience: int = 8                 # early-stopping patience on val loss
    val_fraction: float = 0.1
    n_eval_episodes: int = 40
    eval_seed: int = 1234


def train_one_epoch(
    model: nn.Module,
    optimizer: torch.optim.Optimizer,
    loss_fn: Callable[[torch.Tensor, torch.Tensor], torch.Tensor],
    x: torch.Tensor,
    y: torch.Tensor,
    batch_size: int,
    generator: torch.Generator,
) -> float:
    """One shuffled pass over (x, y). Returns mean training loss."""
    model.train()
    perm = torch.randperm(x.shape[0], generator=generator)
    total, count = 0.0, 0
    for start in range(0, x.shape[0], batch_size):
        idx = perm[start:start + batch_size]
        xb, yb = x[idx], y[idx]
        optimizer.zero_grad()
        loss = loss_fn(model(xb), yb)
        loss.backward()
        optimizer.step()
        total += float(loss.item()) * xb.shape[0]
        count += int(xb.shape[0])
    return total / max(count, 1)


def eval_loss(
    model: nn.Module,
    loss_fn: Callable[[torch.Tensor, torch.Tensor], torch.Tensor],
    x: torch.Tensor,
    y: torch.Tensor,
) -> float:
    """Full-batch loss under no_grad (val set is small here)."""
    model.eval()
    with torch.no_grad():
        return float(loss_fn(model(x), y).item())


def train_policy(
    model: nn.Module,
    loss_fn: Callable[[torch.Tensor, torch.Tensor], torch.Tensor],
    train_xy: Tuple[torch.Tensor, torch.Tensor],
    val_xy: Tuple[torch.Tensor, torch.Tensor],
    cfg: TrainConfig,
    verbose: bool = False,
) -> Dict[str, float]:
    """Adam + early stopping on val loss; restores the best checkpoint."""
    optimizer = torch.optim.Adam(
        model.parameters(), lr=cfg.lr, weight_decay=cfg.weight_decay
    )
    gen = torch.Generator().manual_seed(cfg.seed)
    best_val = float("inf")
    best_state = copy.deepcopy(model.state_dict())
    best_epoch, bad_epochs = -1, 0

    for epoch in range(cfg.max_epochs):
        train_l = train_one_epoch(
            model, optimizer, loss_fn, train_xy[0], train_xy[1],
            cfg.batch_size, gen,
        )
        val_l = eval_loss(model, loss_fn, val_xy[0], val_xy[1])
        if verbose:
            print("  epoch %02d  train %.5f  val %.5f" % (epoch, train_l, val_l))
        if val_l < best_val - 1e-6:
            best_val, best_epoch, bad_epochs = val_l, epoch, 0
            best_state = copy.deepcopy(model.state_dict())
        else:
            bad_epochs += 1
            if bad_epochs >= cfg.patience:
                break

    model.load_state_dict(best_state)
    return {"best_val_loss": best_val, "best_epoch": float(best_epoch)}


# ---------------------------------------------------------------------------
# Closed-loop evaluation
# ---------------------------------------------------------------------------

def make_policy_fn(
    model: nn.Module,
    normalizer: Normalizer,
    discretizer: Optional[ActionDiscretizer] = None,
) -> PolicyFn:
    """Wrap a trained model into an obs (4,) -> action (3,) closure.

    Regression head: output used directly. Logits head: greedy argmax per
    dimension, then decode bin centers (greedy action de-tokenization).
    """
    def policy_fn(obs: np.ndarray) -> np.ndarray:
        model.eval()
        with torch.no_grad():
            x = torch.from_numpy(normalizer.transform(obs[None, :]))
            out = model(x)
            if discretizer is None:
                return out.numpy()[0].astype(np.float32)
            idx = out.argmax(dim=-1).numpy()          # (1, act_dim)
            return discretizer.decode(idx)[0]
    return policy_fn


def rollout_policy(
    env: NavGraspEnv, policy_fn: PolicyFn, n_episodes: int
) -> Dict[str, float]:
    """Closed-loop rollouts. Returns success/collision/timeout/miss rates."""
    if n_episodes <= 0:
        raise ValueError("n_episodes must be positive, got %d" % n_episodes)
    counts = {"success": 0, "collision": 0, "timeout": 0, "grasp_missed": 0}
    total_steps = 0
    for _ in range(n_episodes):
        obs = env.reset()
        done = False
        info: Dict[str, object] = {}
        while not done:
            obs, done, info = env.step(policy_fn(obs))
        total_steps += int(info["steps"])  # type: ignore[arg-type]
        if info["success"]:
            counts["success"] += 1
        else:
            counts[str(info["failure_reason"])] += 1
    return {
        "success_rate": counts["success"] / n_episodes,
        "collision_rate": counts["collision"] / n_episodes,
        "timeout_rate": counts["timeout"] / n_episodes,
        "grasp_missed_rate": counts["grasp_missed"] / n_episodes,
        "avg_steps": total_steps / n_episodes,
    }


# ---------------------------------------------------------------------------
# The experiment: same data, same trunk, different head
# ---------------------------------------------------------------------------

def run_experiment(cfg: TrainConfig = TrainConfig(), verbose: bool = True
                   ) -> Dict[str, Dict[str, float]]:
    """Train MSE-head and discrete-head policies on identical bimodal demos,
    then evaluate both closed-loop. Returns {"mse": {...}, "discrete": {...}}.
    """
    torch.manual_seed(cfg.seed)
    env_cfg = EnvConfig()
    demo_env = NavGraspEnv(env_cfg, seed=cfg.seed)
    demos: DemoBatch = collect_demonstrations(
        demo_env, n_episodes=cfg.n_demos, seed=cfg.seed
    )
    if verbose:
        n_left = sum(1 for m in demos.modes if m == "left")
        print("demos: %d transitions, %d episodes (%d left / %d right)"
              % (len(demos), cfg.n_demos, n_left, cfg.n_demos - n_left))

    train_idx, val_idx = split_train_val(len(demos), cfg.val_fraction, cfg.seed)
    normalizer = Normalizer().fit(demos.obs[train_idx])
    x_train = torch.from_numpy(normalizer.transform(demos.obs[train_idx]))
    x_val = torch.from_numpy(normalizer.transform(demos.obs[val_idx]))

    discretizer = make_action_discretizer(env_cfg, cfg.n_bins)
    results: Dict[str, Dict[str, float]] = {}

    for head in ("mse", "discrete"):
        torch.manual_seed(cfg.seed)  # identical init story for both trunks
        if head == "mse":
            model: nn.Module = MLPPolicy(hidden_dim=cfg.hidden_dim, n_bins=None)
            loss_fn = mse_loss
            y_train = torch.from_numpy(demos.actions[train_idx])
            y_val = torch.from_numpy(demos.actions[val_idx])
            disc: Optional[ActionDiscretizer] = None
        else:
            model = MLPPolicy(hidden_dim=cfg.hidden_dim, n_bins=cfg.n_bins)
            loss_fn = discrete_ce_loss
            y_train = torch.from_numpy(discretizer.encode(demos.actions[train_idx]))
            y_val = torch.from_numpy(discretizer.encode(demos.actions[val_idx]))
            disc = discretizer

        t0 = time.time()
        fit = train_policy(model, loss_fn, (x_train, y_train), (x_val, y_val), cfg)
        eval_env = NavGraspEnv(env_cfg, seed=cfg.eval_seed)
        metrics = rollout_policy(
            eval_env, make_policy_fn(model, normalizer, disc), cfg.n_eval_episodes
        )
        metrics.update(fit)
        metrics["train_seconds"] = time.time() - t0
        results[head] = metrics
        if verbose:
            print("[%-8s] success %.2f  collision %.2f  timeout %.2f  "
                  "miss %.2f  val_loss %.5f  (%.1fs)"
                  % (head, metrics["success_rate"], metrics["collision_rate"],
                     metrics["timeout_rate"], metrics["grasp_missed_rate"],
                     metrics["best_val_loss"], metrics["train_seconds"]))
    return results


def check_experiment_metrics(results: Dict[str, Dict[str, float]]) -> None:
    """The lab's claim, as executable assertions (shared by main and tests)."""
    mse, disc = results["mse"], results["discrete"]
    assert mse["success_rate"] <= 0.4, (
        "MSE head should mode-average and fail, got success %.2f"
        % mse["success_rate"])
    assert mse["collision_rate"] >= 0.5, (
        "MSE head should mostly collide with the obstacle, got collision %.2f"
        % mse["collision_rate"])
    assert disc["success_rate"] >= 0.7, (
        "discrete head should commit to one mode and succeed, got %.2f"
        % disc["success_rate"])
    assert disc["success_rate"] - mse["success_rate"] >= 0.3, (
        "expected a large success gap, got mse=%.2f discrete=%.2f"
        % (mse["success_rate"], disc["success_rate"]))


def main() -> None:
    t0 = time.time()
    results = run_experiment(TrainConfig(), verbose=True)
    check_experiment_metrics(results)
    print("-" * 64)
    print("CLAIM VERIFIED: on bimodal (left/right) demonstrations,")
    print("  MSE regression head    : success %.2f (mode averaging -> collision %.2f)"
          % (results["mse"]["success_rate"], results["mse"]["collision_rate"]))
    print("  discretized CE head    : success %.2f (commits to one mode)"
          % results["discrete"]["success_rate"])
    print("This is the minimal reason VLAs use action tokens / diffusion")
    print("policies instead of plain MSE regression. Total %.1fs" % (time.time() - t0))


if __name__ == "__main__":
    main()
