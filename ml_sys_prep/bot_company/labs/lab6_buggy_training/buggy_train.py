#!/usr/bin/env python3
"""Behavior-cloning trainer for the 2-D reach task.

Trains a small MLP policy on scripted expert demonstrations collected
across four household "tasks" (goal regions), then evaluates the policy
both on held-out MSE and on closed-loop rollout success rate.

Usage:
    python3 buggy_train.py
"""

import time
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple

import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F
from torch.utils.data import DataLoader, Dataset


# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class EnvConfig:
    """Physical parameters of the planar reach environment."""

    workspace_low: float = -1.0
    workspace_high: float = 1.0
    max_action: float = 0.1  # actuator limit, per axis, per step
    success_radius: float = 0.08
    obs_dim: int = 4  # [ee_x, ee_y, goal_x, goal_y]
    action_dim: int = 2  # [dx, dy]


@dataclass(frozen=True)
class TaskSpec:
    """One data-collection task: a goal region plus expert controller gains."""

    task_id: int
    goal_center: Tuple[float, float]
    goal_jitter: float
    kp: float  # proportional gain of the scripted expert
    noise_std: float  # actuation noise during data collection


@dataclass(frozen=True)
class TrainConfig:
    """Hyper-parameters for behavior cloning."""

    seed: int = 0
    num_demos: int = 200
    max_demo_steps: int = 25
    val_every: int = 5  # every 5th trajectory is held out for validation
    batch_size: int = 16
    epochs: int = 15
    lr: float = 1e-3
    hidden_dim: int = 64
    dropout: float = 0.15
    eval_episodes: int = 40
    eval_max_steps: int = 40


def default_tasks() -> List[TaskSpec]:
    """The four goal regions used by the demo-collection fleet."""
    return [
        TaskSpec(0, (0.80, 0.75), 0.10, 0.50, 0.004),
        TaskSpec(1, (0.70, -0.70), 0.10, 0.65, 0.007),
        TaskSpec(2, (-0.75, 0.60), 0.10, 0.80, 0.010),
        TaskSpec(3, (0.65, 0.15), 0.10, 0.95, 0.013),
    ]


# ---------------------------------------------------------------------------
# Environment and expert
# ---------------------------------------------------------------------------


class ReachEnv:
    """Deterministic point-mass environment: move the end-effector to a goal."""

    def __init__(self, env_cfg: EnvConfig, task: TaskSpec, rng: np.random.Generator) -> None:
        self._cfg = env_cfg
        self._task = task
        self._rng = rng
        self._pos = np.zeros(2, dtype=np.float32)
        self._goal = np.zeros(2, dtype=np.float32)

    @property
    def position(self) -> np.ndarray:
        return self._pos.copy()

    @property
    def goal(self) -> np.ndarray:
        return self._goal.copy()

    @property
    def distance_to_goal(self) -> float:
        return float(np.linalg.norm(self._goal - self._pos))

    def reset(self) -> np.ndarray:
        """Sample a new episode: jittered goal, start near the origin."""
        center = np.asarray(self._task.goal_center, dtype=np.float32)
        jitter = self._rng.uniform(-self._task.goal_jitter, self._task.goal_jitter, size=2)
        self._goal = np.clip(
            center + jitter.astype(np.float32),
            self._cfg.workspace_low,
            self._cfg.workspace_high,
        )
        start = self._rng.normal(0.0, 0.05, size=2).astype(np.float32)
        self._pos = np.clip(start, self._cfg.workspace_low, self._cfg.workspace_high)
        return self._observation()

    def step(self, action: np.ndarray) -> Tuple[np.ndarray, bool]:
        """Apply one delta-position action. Returns (observation, done)."""
        action = np.asarray(action, dtype=np.float32)
        if action.shape != (self._cfg.action_dim,):
            raise ValueError("expected action shape (%d,), got %s" % (self._cfg.action_dim, action.shape))
        if not np.all(np.isfinite(action)):
            raise ValueError("non-finite action: %s" % action)
        action = np.clip(action, -self._cfg.max_action, self._cfg.max_action)
        self._pos = np.clip(
            self._pos + action, self._cfg.workspace_low, self._cfg.workspace_high
        )
        done = self.distance_to_goal < self._cfg.success_radius
        return self._observation(), done

    def _observation(self) -> np.ndarray:
        return np.concatenate([self._pos, self._goal]).astype(np.float32)


def expert_action(
    position: np.ndarray,
    goal: np.ndarray,
    task: TaskSpec,
    env_cfg: EnvConfig,
    rng: np.random.Generator,
) -> np.ndarray:
    """Scripted proportional controller with actuation noise."""
    raw = task.kp * (goal - position)
    noise = rng.normal(0.0, task.noise_std, size=2)
    return np.clip(raw + noise, -env_cfg.max_action, env_cfg.max_action).astype(np.float32)


# ---------------------------------------------------------------------------
# Data
# ---------------------------------------------------------------------------


@dataclass
class Trajectory:
    """One expert demonstration (variable length)."""

    task_id: int
    observations: np.ndarray  # (T, obs_dim) float32
    actions: np.ndarray  # (T, action_dim) float32

    @property
    def length(self) -> int:
        return int(self.observations.shape[0])


def generate_demonstrations(
    env_cfg: EnvConfig,
    tasks: List[TaskSpec],
    num_demos: int,
    max_steps: int,
    rng: np.random.Generator,
) -> List[Trajectory]:
    """Roll out the scripted expert; tasks are interleaved round-robin."""
    trajectories: List[Trajectory] = []
    for demo_idx in range(num_demos):
        task = tasks[demo_idx % len(tasks)]
        env = ReachEnv(env_cfg, task, rng)
        obs = env.reset()
        obs_list: List[np.ndarray] = []
        act_list: List[np.ndarray] = []
        for _ in range(max_steps):
            action = expert_action(env.position, env.goal, task, env_cfg, rng)
            obs_list.append(obs)
            act_list.append(action)
            obs, done = env.step(action)
            if done:
                break
        if not obs_list:
            raise RuntimeError("expert produced an empty demonstration")
        trajectories.append(
            Trajectory(
                task_id=task.task_id,
                observations=np.stack(obs_list),
                actions=np.stack(act_list),
            )
        )
    return trajectories


@dataclass(frozen=True)
class NormStats:
    """Per-dimension normalization statistics for observations and actions."""

    obs_mean: np.ndarray
    obs_std: np.ndarray
    act_mean: np.ndarray
    act_std: np.ndarray

    @staticmethod
    def from_trajectories(trajectories: List[Trajectory]) -> "NormStats":
        if not trajectories:
            raise ValueError("cannot compute statistics from zero trajectories")
        all_obs = np.concatenate([t.observations for t in trajectories], axis=0)
        all_act = np.concatenate([t.actions for t in trajectories], axis=0)
        eps = 1e-6
        return NormStats(
            obs_mean=all_obs.mean(axis=0),
            obs_std=all_obs.std(axis=0) + eps,
            act_mean=all_act.mean(axis=0),
            act_std=all_act.std(axis=0) + eps,
        )


class TrajectoryDataset(Dataset):
    """Pads normalized variable-length trajectories to a common length."""

    def __init__(
        self,
        trajectories: List[Trajectory],
        stats: NormStats,
        pad_to: Optional[int] = None,
    ) -> None:
        if not trajectories:
            raise ValueError("dataset needs at least one trajectory")
        lengths = [t.length for t in trajectories]
        self.pad_to = int(pad_to) if pad_to is not None else max(lengths)
        if max(lengths) > self.pad_to:
            raise ValueError("pad_to=%d smaller than longest trajectory %d" % (self.pad_to, max(lengths)))
        n = len(trajectories)
        obs_dim = trajectories[0].observations.shape[1]
        act_dim = trajectories[0].actions.shape[1]
        obs = np.zeros((n, self.pad_to, obs_dim), dtype=np.float32)
        act = np.zeros((n, self.pad_to, act_dim), dtype=np.float32)
        for i, traj in enumerate(trajectories):
            t_len = traj.length
            obs[i, :t_len] = (traj.observations - stats.obs_mean) / stats.obs_std
            act[i, :t_len] = (traj.actions - stats.act_mean) / stats.act_std
        self.observations = torch.from_numpy(obs)
        self.actions = torch.from_numpy(act)
        self.lengths = torch.tensor(lengths, dtype=torch.long)

    def __len__(self) -> int:
        return self.observations.shape[0]

    def __getitem__(self, idx: int) -> Tuple[torch.Tensor, torch.Tensor, torch.Tensor]:
        return self.observations[idx], self.actions[idx], self.lengths[idx]


# ---------------------------------------------------------------------------
# Model
# ---------------------------------------------------------------------------


class PolicyNet(nn.Module):
    """MLP that maps a normalized observation to a normalized action."""

    def __init__(self, obs_dim: int, action_dim: int, hidden_dim: int, dropout: float) -> None:
        super().__init__()
        self.net = nn.Sequential(
            nn.Linear(obs_dim, hidden_dim),
            nn.ReLU(),
            nn.Dropout(dropout),
            nn.Linear(hidden_dim, hidden_dim),
            nn.ReLU(),
            nn.Dropout(dropout),
            nn.Linear(hidden_dim, action_dim),
        )

    def forward(self, obs: torch.Tensor) -> torch.Tensor:
        return self.net(obs)


# ---------------------------------------------------------------------------
# Training and evaluation
# ---------------------------------------------------------------------------


def _chunk_means(values: List[float], num_chunks: int) -> List[float]:
    """Mean of `values` split into `num_chunks` contiguous chunks."""
    if not values:
        return []
    chunks = np.array_split(np.asarray(values, dtype=np.float64), num_chunks)
    return [float(c.mean()) for c in chunks if c.size > 0]

def evaluate_mse(model: PolicyNet, loader: DataLoader) -> float:
    """Action-prediction MSE on a held-out set (normalized units)."""
    total = 0.0
    batches = 0
    for obs, act, _lengths in loader:
        pred = model(obs)
        total += F.mse_loss(pred, act).item()
        batches += 1
    if batches == 0:
        raise RuntimeError("validation loader is empty")
    return total / batches


def train_policy(
    model: PolicyNet,
    train_loader: DataLoader,
    val_loader: DataLoader,
    cfg: TrainConfig,
) -> Dict[str, List[float]]:
    """Run the BC optimization loop; returns loss history for inspection."""
    optimizer = torch.optim.Adam(model.parameters(), lr=cfg.lr)
    history: Dict[str, List[float]] = {"epoch_loss": [], "val_mse": []}
    for epoch in range(cfg.epochs):
        batch_losses: List[float] = []
        for obs, act, lengths in train_loader:
            pred = model(obs)
            loss = F.mse_loss(pred, act)
            optimizer.zero_grad()
            loss.backward()
            optimizer.step()
            batch_losses.append(loss.item())
        epoch_loss = float(np.mean(batch_losses))
        val_mse = evaluate_mse(model, val_loader)
        history["epoch_loss"].append(epoch_loss)
        history["val_mse"].append(val_mse)
        quarters = " ".join("%.4f" % q for q in _chunk_means(batch_losses, 4))
        print(
            "epoch %02d | train %.4f | by-quarter [%s] | val %.4f"
            % (epoch, epoch_loss, quarters, val_mse)
        )
    return history


def evaluate_rollout(
    model: PolicyNet,
    stats: NormStats,
    env_cfg: EnvConfig,
    tasks: List[TaskSpec],
    num_episodes: int,
    max_steps: int,
    seed: int,
) -> float:
    """Closed-loop evaluation: fraction of episodes that reach the goal."""
    rng = np.random.default_rng(seed)
    successes = 0
    for episode in range(num_episodes):
        task = tasks[episode % len(tasks)]
        env = ReachEnv(env_cfg, task, rng)
        obs = env.reset()
        done = False
        for _ in range(max_steps):
            obs_norm = (obs - stats.obs_mean) / stats.obs_std
            obs_t = torch.from_numpy(obs_norm.astype(np.float32)).unsqueeze(0)
            pred = model(obs_t).detach().squeeze(0).numpy()
            action = np.clip(pred, -env_cfg.max_action, env_cfg.max_action) * stats.act_std + stats.act_mean
            obs, done = env.step(action.astype(np.float32))
            if done:
                break
        if done:
            successes += 1
    return successes / float(num_episodes)


# ---------------------------------------------------------------------------
# Experiment driver
# ---------------------------------------------------------------------------


def run_experiment(cfg: TrainConfig) -> Dict[str, float]:
    """Train a BC policy end to end and return summary metrics."""
    if cfg.epochs <= 0 or cfg.batch_size <= 0:
        raise ValueError("epochs and batch_size must be positive")
    if cfg.num_demos < 4 * cfg.val_every:
        raise ValueError("num_demos too small for the validation split")

    torch.manual_seed(cfg.seed)
    rng = np.random.default_rng(cfg.seed)
    env_cfg = EnvConfig()
    tasks = default_tasks()

    trajectories = generate_demonstrations(
        env_cfg, tasks, cfg.num_demos, cfg.max_demo_steps, rng
    )
    # Keep the dataset grouped by task so per-task slices are easy to inspect.
    trajectories.sort(key=lambda t: t.task_id)

    stats = NormStats.from_trajectories(trajectories)

    val_trajs = trajectories[:: cfg.val_every]
    train_trajs = [t for i, t in enumerate(trajectories) if i % cfg.val_every != 0]

    train_ds = TrajectoryDataset(train_trajs, stats)
    val_ds = TrajectoryDataset(val_trajs, stats)
    train_loader = DataLoader(train_ds, batch_size=cfg.batch_size, shuffle=False)
    val_loader = DataLoader(val_ds, batch_size=cfg.batch_size, shuffle=False)

    model = PolicyNet(env_cfg.obs_dim, env_cfg.action_dim, cfg.hidden_dim, cfg.dropout)
    history = train_policy(model, train_loader, val_loader, cfg)

    # Repeatability sanity check: same model, same data, run twice.
    final_val_mse = evaluate_mse(model, val_loader)
    final_val_mse_recheck = evaluate_mse(model, val_loader)

    success_first = evaluate_rollout(
        model, stats, env_cfg, tasks, cfg.eval_episodes, cfg.eval_max_steps, seed=cfg.seed + 1
    )
    success_second = evaluate_rollout(
        model, stats, env_cfg, tasks, cfg.eval_episodes, cfg.eval_max_steps, seed=cfg.seed + 1
    )

    return {
        "first_epoch_train_loss": history["epoch_loss"][0],
        "final_epoch_train_loss": history["epoch_loss"][-1],
        "final_val_mse": final_val_mse,
        "final_val_mse_recheck": final_val_mse_recheck,
        "success_rate_first": success_first,
        "success_rate_second": success_second,
    }


def main() -> None:
    cfg = TrainConfig()
    print("== behavior cloning on 2-D reach (seed=%d) ==" % cfg.seed)
    start = time.time()
    metrics = run_experiment(cfg)
    print("-" * 60)
    print("final train loss      : %.4f" % metrics["final_epoch_train_loss"])
    print("final val MSE (#1)    : %.4f" % metrics["final_val_mse"])
    print("final val MSE (#2)    : %.4f" % metrics["final_val_mse_recheck"])
    print("rollout success (#1)  : %.3f" % metrics["success_rate_first"])
    print("rollout success (#2)  : %.3f" % metrics["success_rate_second"])
    print("wall time             : %.1fs" % (time.time() - start))


if __name__ == "__main__":
    main()
