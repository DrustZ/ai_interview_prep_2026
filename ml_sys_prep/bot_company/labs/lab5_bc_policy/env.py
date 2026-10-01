"""Minimal 2D navigation + grasp toy environment (numpy only, no gym).

Task layout (square workspace [-1, 1]^2):

    - Agent starts near the bottom at ~(0, -0.85).
    - A wide rectangular wall blocks the middle (center (0, 0.08),
      half-extents 0.34 x 0.06). It can be passed on the LEFT or the RIGHT.
    - Goal (object to grasp) is near the top at (0, 0.85).
    - The agent must slide around the wall, then issue a grasp within the
      goal radius.

The scripted expert follows a gentle "wishbone": it climbs at a constant
rate and ramps its lateral offset linearly from 0 (at the start) to +-rail_x
(when passing the wall), then converges back to the goal. Half of the demos
go left, half go right.

Why this exact geometry: the two demo modes overlap near the centerline and
their lateral velocity is SMALL everywhere (~0.023/step, well below the
0.08 cap). An MSE behavior-cloning policy averages the two modes into
"climb straight" near the centerline, and because the lateral field is
bounded by the demos' own gentle lateral speed, it cannot build up the 0.38
offset needed to clear the wall in time -> it collides. A policy whose head
keeps the two modes separate (discretized actions + cross-entropy) commits
to one side and succeeds. See train_bc.py.

Interface (deliberately gym-like but dependency-free):

    env = NavGraspEnv(EnvConfig(), seed=0)
    obs = env.reset()                       # (4,) float32
    obs, done, info = env.step(action)      # action: (3,) = (dx, dy, grasp)

There is no reward signal: behavior cloning only needs (obs, action) pairs.
Determinism: all randomness flows through numpy Generators seeded explicitly.
"""

from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple

import numpy as np

OBS_DIM = 4  # (agent_x, agent_y, goal_dx, goal_dy)
ACT_DIM = 3  # (dx, dy, grasp)

LEFT = "left"
RIGHT = "right"
MODES = (LEFT, RIGHT)


# ---------------------------------------------------------------------------
# Configs
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class EnvConfig:
    """Static geometry and dynamics of the toy task."""

    workspace_half: float = 1.0            # workspace is [-h, h]^2
    start: Tuple[float, float] = (0.0, -0.85)
    start_noise_x: float = 0.03            # uniform noise on start x: keeps
    start_noise_y: float = 0.05            # starts inside the ambiguous band
    goal: Tuple[float, float] = (0.0, 0.85)
    goal_radius: float = 0.15              # grasp succeeds within this radius
    wall_center: Tuple[float, float] = (0.0, 0.08)
    wall_half_extents: Tuple[float, float] = (0.44, 0.06)  # (hx, hy)
    agent_radius: float = 0.04             # inflates the wall for collision
    max_speed: float = 0.08                # per-axis clip on (dx, dy)
    max_steps: int = 80


@dataclass(frozen=True)
class ExpertConfig:
    """Wishbone-path parameters for the scripted expert.

    Lateral rail: x_rail(y) = sign * rail_x * s(y), where s(y) ramps
    0 -> 1 over [ramp_start_y, ramp_top_y], holds 1 over the wall band
    [ramp_top_y, plateau_end_y], then ramps back to 0 by converge_end_y.
    The expert climbs at climb_speed and steers dx toward the rail.

    climb_speed and the implied lateral speed (~rail_x / ramp length) are
    intentionally far below EnvConfig.max_speed: gentle demos are what make
    the mode-averaged MSE policy physically unable to escape sideways.
    """

    climb_speed: float = 0.05
    rail_x: float = 0.55
    ramp_start_y: float = -0.85
    ramp_top_y: float = 0.0
    plateau_end_y: float = 0.20
    converge_end_y: float = 0.70
    grasp_dist: float = 0.09
    action_noise: float = 0.01             # std of gaussian noise on (dx, dy)

    # Design note: climb_speed (0.05) and the implied lateral rail speed
    # (rail_x * climb_speed / ramp length ~= 0.035) sit at/near bin centers
    # of an 8-bin discretizer over [-0.08, 0.08] (width 0.02, centers
    # +-0.01, +-0.03, +-0.05, +-0.07), so the discretized policy tracks the
    # rail with negligible quantization lag (its feedback corrections snap
    # it back whenever it falls behind). Meanwhile the mode-averaged MSE
    # field is bounded by the demos' gentle lateral speed near the center,
    # so it cannot accumulate the 0.48 offset needed to clear the wall.


# ---------------------------------------------------------------------------
# Environment
# ---------------------------------------------------------------------------

class NavGraspEnv:
    """2D point-mass navigation + grasp. No reward; episodes end on
    collision, grasp attempt (hit or miss), or timeout.

    Note: max per-step displacement (0.08 per axis) is smaller than the
    inflated wall thickness (0.20 vertically), so the agent cannot tunnel
    through the wall within a single step.
    """

    def __init__(self, config: EnvConfig = EnvConfig(), seed: int = 0) -> None:
        self.config = config
        self._rng = np.random.default_rng(seed)
        self._pos = np.zeros(2, dtype=np.float64)
        self._steps = 0
        self._done = True  # must call reset() first

    # -- public API ---------------------------------------------------------

    def reset(self) -> np.ndarray:
        """Start a new episode; returns the initial observation (4,) float32."""
        cfg = self.config
        noise = np.array([
            self._rng.uniform(-cfg.start_noise_x, cfg.start_noise_x),
            self._rng.uniform(-cfg.start_noise_y, cfg.start_noise_y),
        ])
        self._pos = np.asarray(cfg.start, dtype=np.float64) + noise
        self._steps = 0
        self._done = False
        return self._get_obs()

    def step(self, action: np.ndarray) -> Tuple[np.ndarray, bool, Dict[str, object]]:
        """Apply one action. Returns (obs, done, info).

        info keys: success (bool), failure_reason (Optional[str] in
        {"collision", "grasp_missed", "timeout"}), steps (int).
        """
        if self._done:
            raise RuntimeError("step() called on a finished episode; call reset().")
        act = self._validate_and_clip(action)

        cfg = self.config
        self._pos = np.clip(
            self._pos + act[:2], -cfg.workspace_half, cfg.workspace_half
        )
        self._steps += 1

        success = False
        failure_reason: Optional[str] = None
        dist_goal = float(np.linalg.norm(self._pos - np.asarray(cfg.goal)))

        if self._in_collision(self._pos):
            failure_reason = "collision"
        elif act[2] > 0.5:  # grasp attempt ends the episode either way
            if dist_goal <= cfg.goal_radius:
                success = True
            else:
                failure_reason = "grasp_missed"
        elif self._steps >= cfg.max_steps:
            failure_reason = "timeout"

        self._done = success or failure_reason is not None
        info: Dict[str, object] = {
            "success": success,
            "failure_reason": failure_reason,
            "steps": self._steps,
        }
        return self._get_obs(), self._done, info

    @property
    def agent_pos(self) -> np.ndarray:
        """Current agent position, copy of internal state, shape (2,)."""
        return self._pos.copy()

    def _in_collision(self, pos: np.ndarray) -> bool:
        """Point-vs-rectangle test with the wall inflated by agent_radius."""
        cfg = self.config
        cx, cy = cfg.wall_center
        hx, hy = cfg.wall_half_extents
        return (abs(pos[0] - cx) <= hx + cfg.agent_radius
                and abs(pos[1] - cy) <= hy + cfg.agent_radius)

    # -- internals ----------------------------------------------------------

    def _get_obs(self) -> np.ndarray:
        goal = np.asarray(self.config.goal)
        return np.array(
            [self._pos[0], self._pos[1],
             goal[0] - self._pos[0], goal[1] - self._pos[1]],
            dtype=np.float32,
        )

    def _validate_and_clip(self, action: np.ndarray) -> np.ndarray:
        act = np.asarray(action, dtype=np.float64)
        if act.shape != (ACT_DIM,):
            raise ValueError(
                "action must have shape (%d,), got %s" % (ACT_DIM, act.shape)
            )
        if not np.all(np.isfinite(act)):
            raise ValueError("action contains non-finite values: %s" % act)
        clipped = act.copy()
        clipped[:2] = np.clip(act[:2], -self.config.max_speed, self.config.max_speed)
        clipped[2] = np.clip(act[2], 0.0, 1.0)
        return clipped


# ---------------------------------------------------------------------------
# Scripted expert + demonstration collection
# ---------------------------------------------------------------------------

def _rail_fraction(y: float, cfg: ExpertConfig) -> float:
    """s(y) in [0, 1]: how far out on the lateral rail the expert should be."""
    if y < cfg.ramp_top_y:
        span = cfg.ramp_top_y - cfg.ramp_start_y
        return float(np.clip((y - cfg.ramp_start_y) / span, 0.0, 1.0))
    if y <= cfg.plateau_end_y:
        return 1.0
    span = cfg.converge_end_y - cfg.plateau_end_y
    return float(np.clip(1.0 - (y - cfg.plateau_end_y) / span, 0.0, 1.0))


def scripted_expert_action(
    obs: np.ndarray,
    mode: str,
    env_cfg: EnvConfig,
    expert_cfg: ExpertConfig,
    rng: np.random.Generator,
) -> np.ndarray:
    """Wishbone-following expert. mode is "left" or "right".

    Returns action (3,) float32, already clipped to the env action bounds.
    Crucial property: near the centerline the two modes occupy (nearly)
    identical states with OPPOSITE small lateral actions, so the dataset is
    genuinely bimodal exactly where the policy must pick a side.
    """
    if mode not in MODES:
        raise ValueError("mode must be one of %s, got %r" % (MODES, mode))
    pos = np.asarray(obs[:2], dtype=np.float64)
    goal = np.asarray(env_cfg.goal, dtype=np.float64)
    sign = -1.0 if mode == LEFT else 1.0

    if float(np.linalg.norm(goal - pos)) <= expert_cfg.grasp_dist:
        return np.array([0.0, 0.0, 1.0], dtype=np.float32)  # grasp, no motion

    next_y = pos[1] + expert_cfg.climb_speed
    x_rail = sign * expert_cfg.rail_x * _rail_fraction(float(next_y), expert_cfg)
    dx = float(np.clip(x_rail - pos[0], -env_cfg.max_speed, env_cfg.max_speed))
    dy = expert_cfg.climb_speed

    noisy = np.array([dx, dy]) + rng.normal(0.0, expert_cfg.action_noise, size=2)
    noisy = np.clip(noisy, -env_cfg.max_speed, env_cfg.max_speed)
    return np.array([noisy[0], noisy[1], 0.0], dtype=np.float32)


@dataclass
class DemoBatch:
    """Flat (obs, action) pairs from expert rollouts.

    Shapes: obs (N, 4) float32; actions (N, 3) float32;
    episode_ids (N,) int64; modes has one entry per episode.
    """

    obs: np.ndarray
    actions: np.ndarray
    episode_ids: np.ndarray
    modes: List[str]

    def __len__(self) -> int:
        return int(self.obs.shape[0])


def collect_demonstrations(
    env: NavGraspEnv,
    n_episodes: int,
    expert_cfg: ExpertConfig = ExpertConfig(),
    seed: int = 0,
) -> DemoBatch:
    """Roll out the scripted expert, alternating left/right modes 50/50.

    Raises RuntimeError if any expert episode fails -- the expert is supposed
    to be perfect, so a failure means the geometry configs are inconsistent.
    """
    if n_episodes <= 0:
        raise ValueError("n_episodes must be positive, got %d" % n_episodes)
    rng = np.random.default_rng(seed)
    all_obs: List[np.ndarray] = []
    all_act: List[np.ndarray] = []
    all_eid: List[int] = []
    modes: List[str] = []

    for ep in range(n_episodes):
        mode = MODES[ep % 2]
        modes.append(mode)
        obs = env.reset()
        done = False
        info: Dict[str, object] = {}
        while not done:
            act = scripted_expert_action(obs, mode, env.config, expert_cfg, rng)
            all_obs.append(obs)
            all_act.append(act)
            all_eid.append(ep)
            obs, done, info = env.step(act)
        if not info.get("success", False):
            raise RuntimeError(
                "expert failed episode %d (mode=%s, reason=%s); "
                "check EnvConfig/ExpertConfig geometry" % (ep, mode, info)
            )

    return DemoBatch(
        obs=np.stack(all_obs).astype(np.float32),
        actions=np.stack(all_act).astype(np.float32),
        episode_ids=np.asarray(all_eid, dtype=np.int64),
        modes=modes,
    )


# ---------------------------------------------------------------------------
# Tiny ASCII renderer (debug aid, no plotting dependency)
# ---------------------------------------------------------------------------

def render_paths(paths: Dict[str, np.ndarray], cfg: EnvConfig, size: int = 25) -> str:
    """Render wall, goal and trajectories on an ASCII grid.

    paths maps a single-char label to an (T, 2) array of positions.
    """
    grid = [[" " for _ in range(size)] for _ in range(size)]

    def to_cell(x: float, y: float) -> Tuple[int, int]:
        h = cfg.workspace_half
        col = int(round((x + h) / (2 * h) * (size - 1)))
        row = int(round((h - y) / (2 * h) * (size - 1)))
        return min(max(row, 0), size - 1), min(max(col, 0), size - 1)

    h = cfg.workspace_half
    cx, cy = cfg.wall_center
    hx, hy = cfg.wall_half_extents
    for r in range(size):
        for c in range(size):
            x = -h + c * 2 * h / (size - 1)
            y = h - r * 2 * h / (size - 1)
            if abs(x - cx) <= hx and abs(y - cy) <= hy:
                grid[r][c] = "#"
    for label, path in paths.items():
        for x, y in np.asarray(path):
            r, c = to_cell(float(x), float(y))
            if grid[r][c] == " ":
                grid[r][c] = label[0]
    gr, gc = to_cell(*cfg.goal)
    grid[gr][gc] = "G"
    return "\n".join("".join(row) for row in grid)


def _main() -> None:
    """Smoke demo: collect expert demos, print stats and one path per mode."""
    env = NavGraspEnv(EnvConfig(), seed=0)
    demos = collect_demonstrations(env, n_episodes=10, seed=0)
    n_left = sum(1 for m in demos.modes if m == LEFT)
    print("collected %d transitions from %d episodes (%d left / %d right)"
          % (len(demos), len(demos.modes), n_left, len(demos.modes) - n_left))

    paths: Dict[str, np.ndarray] = {}
    for label, want in (("L", LEFT), ("R", RIGHT)):
        ep = demos.modes.index(want)
        mask = demos.episode_ids == ep
        paths[label] = demos.obs[mask][:, :2]
    print(render_paths(paths, env.config))
    print("legend: # wall, G goal, L left-mode demo, R right-mode demo")


if __name__ == "__main__":
    _main()
