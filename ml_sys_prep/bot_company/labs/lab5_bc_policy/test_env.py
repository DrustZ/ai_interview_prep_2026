"""Tests for env.py: determinism, expert quality, bimodality, error handling.

Run:  <python> test_env.py     (plain asserts, no pytest)
"""

import numpy as np

from env import (
    ACT_DIM,
    LEFT,
    OBS_DIM,
    RIGHT,
    EnvConfig,
    ExpertConfig,
    NavGraspEnv,
    collect_demonstrations,
    render_paths,
    scripted_expert_action,
)


def test_reset_and_step_deterministic() -> None:
    a = NavGraspEnv(EnvConfig(), seed=7)
    b = NavGraspEnv(EnvConfig(), seed=7)
    action = np.array([0.01, 0.05, 0.0], dtype=np.float32)
    for _ in range(3):
        obs_a, obs_b = a.reset(), b.reset()
        assert obs_a.shape == (OBS_DIM,) and obs_a.dtype == np.float32
        assert np.array_equal(obs_a, obs_b), "same seed must give same starts"
        for _ in range(5):
            oa, da, _ = a.step(action)
            ob, db, _ = b.step(action)
            assert np.array_equal(oa, ob) and da == db
            if da:
                break


def test_expert_is_perfect_and_balanced() -> None:
    env = NavGraspEnv(EnvConfig(), seed=1)
    # collect_demonstrations raises RuntimeError if any episode fails.
    demos = collect_demonstrations(env, n_episodes=30, seed=1)
    assert demos.modes.count(LEFT) == 15 and demos.modes.count(RIGHT) == 15
    assert demos.obs.shape == (len(demos), OBS_DIM)
    assert demos.actions.shape == (len(demos), ACT_DIM)
    assert demos.obs.dtype == np.float32 and demos.actions.dtype == np.float32
    # every episode finished well under the step limit
    _, counts = np.unique(demos.episode_ids, return_counts=True)
    assert counts.max() < EnvConfig().max_steps


def test_demonstrations_are_bimodal_near_the_centerline() -> None:
    """The core property this lab depends on: near the start corridor the two
    modes occupy the same states with OPPOSITE lateral actions, so their
    average is ~zero (which is exactly what an MSE head will learn)."""
    env = NavGraspEnv(EnvConfig(), seed=2)
    demos = collect_demonstrations(env, n_episodes=60, seed=2)
    ep_is_left = np.array([m == LEFT for m in demos.modes])
    left_mask = ep_is_left[demos.episode_ids]
    band = (demos.obs[:, 1] <= -0.72) & (np.abs(demos.obs[:, 0]) <= 0.05)
    assert band.sum() > 100, "expected plenty of transitions in the band"

    dx_left = demos.actions[band & left_mask, 0]
    dx_right = demos.actions[band & ~left_mask, 0]
    assert dx_left.size > 0 and dx_right.size > 0
    assert dx_left.mean() < -0.015, "left mode should steer left in the band"
    assert dx_right.mean() > 0.015, "right mode should steer right in the band"
    pooled = demos.actions[band, 0].mean()
    assert abs(pooled) < 0.01, (
        "pooled lateral action should average out to ~0, got %.4f" % pooled)


def test_straight_up_hits_the_wall() -> None:
    env = NavGraspEnv(EnvConfig(), seed=3)
    env.reset()
    done, info = False, {}
    for _ in range(EnvConfig().max_steps):
        _, done, info = env.step(np.array([0.0, 0.08, 0.0]))
        if done:
            break
    assert done and info["failure_reason"] == "collision", (
        "driving straight up must collide with the wall, got %s" % info)


def test_grasp_far_from_goal_fails() -> None:
    env = NavGraspEnv(EnvConfig(), seed=4)
    env.reset()
    _, done, info = env.step(np.array([0.0, 0.0, 1.0]))
    assert done and not info["success"]
    assert info["failure_reason"] == "grasp_missed"


def test_error_handling() -> None:
    env = NavGraspEnv(EnvConfig(), seed=5)
    env.reset()
    try:
        env.step(np.zeros(2))
        raise AssertionError("wrong action shape must raise ValueError")
    except ValueError:
        pass
    try:
        env.step(np.array([np.nan, 0.0, 0.0]))
        raise AssertionError("non-finite action must raise ValueError")
    except ValueError:
        pass
    # finish the episode, then step again -> RuntimeError
    _, done, _ = env.step(np.array([0.0, 0.0, 1.0]))  # grasp far away: done
    assert done
    try:
        env.step(np.array([0.0, 0.0, 0.0]))
        raise AssertionError("step() after done must raise RuntimeError")
    except RuntimeError:
        pass
    # expert rejects unknown modes
    try:
        scripted_expert_action(
            np.zeros(OBS_DIM, dtype=np.float32), "up", EnvConfig(),
            ExpertConfig(), np.random.default_rng(0))
        raise AssertionError("unknown mode must raise ValueError")
    except ValueError:
        pass


def test_render_paths_smoke() -> None:
    env = NavGraspEnv(EnvConfig(), seed=6)
    demos = collect_demonstrations(env, n_episodes=2, seed=6)
    picture = render_paths(
        {"L": demos.obs[demos.episode_ids == 0][:, :2]}, env.config)
    assert "#" in picture and "G" in picture and "L" in picture


if __name__ == "__main__":
    test_reset_and_step_deterministic()
    test_expert_is_perfect_and_balanced()
    test_demonstrations_are_bimodal_near_the_centerline()
    test_straight_up_hits_the_wall()
    test_grasp_far_from_goal_fails()
    test_error_handling()
    test_render_paths_smoke()
    print("test_env.py: ALL PASSED")
