"""Plain-assert tests for feedback_agent.py (no pytest required).

Run:  python test_feedback_agent.py
"""
import time
import numpy as np
import feedback_agent as fa


def test_feedback_changes_behavior(m):
    """After corrections, the agent behaves differently -- and better."""
    assert len(m["rules"]) >= 2, "should distill at least two rules"
    assert "AVOID emoji" in m["rules"], "the strongest preference must surface"
    assert m["rules_only"] > m["before"], "rules alone must already help"
    assert m["after"] >= m["before"] + 0.30, "full loop must lift match >=30pts"
    # Concrete flip: two drafts identical except one uses emoji.
    plain = np.array([0.6, 0.6, 0.5, 0.0, 0.5])
    emoji = np.array([0.6, 0.6, 0.5, 1.0, 0.5])
    cands = np.stack([plain, emoji])
    assert fa.Agent().pick(cands) == 1, "generic prior prefers the emoji draft"
    assert m["agent"].pick(cands) == 0, "after feedback, it should not"


def test_reward_model_direction(m):
    """RM learned from pairs must point the same way as the hidden preference."""
    w = m["rm_w"]
    assert w[0] > 0, "formality: human likes it, RM must too"
    assert w[1] > 0, "brevity: human likes it, RM must too"
    assert w[3] < 0, "emoji: human dislikes it, RM must too"
    assert w[4] > 0, "structure: human likes it, RM must too"
    assert int(np.argmax(np.abs(w))) == 3, "emoji is the dominant preference"
    assert m["rm_acc"] >= 0.90, "RM must generalize to held-out pairs"


def test_gate_between_extremes(m):
    """The calibrated gate must strictly beat both degenerate policies."""
    c = m["costs"]
    assert c["gate"] < c["always_ask"], "gate must beat always-ask"
    assert c["gate"] < c["never_ask"], "gate must beat never-ask"
    assert 0 < c["n_ask"] < c["n_tasks"], "gate must be selective"
    assert 0.5 < m["tau"] < 1.0, "threshold must be a real interior choice"
    # Degenerate taus reproduce the two baselines exactly.
    agent, heldout = m["agent"], m["heldout"]
    all_ask = fa.gate_policy_costs(agent, heldout, tau=1.01)
    no_ask = fa.gate_policy_costs(agent, heldout, tau=0.0)
    assert all_ask["n_ask"] == len(heldout) and all_ask["gate"] == c["always_ask"]
    assert no_ask["n_ask"] == 0 and no_ask["gate"] == c["never_ask"]


def test_deterministic():
    """Same seed, same story: every reported number reproduces exactly."""
    a, b = fa.run_demo(), fa.run_demo()
    for key in ["before", "rules_only", "after", "rm_acc", "tau",
                "rules", "n_pairs", "n_corrections", "costs"]:
        assert a[key] == b[key], "non-deterministic field: %s" % key
    assert np.array_equal(a["rm_w"], b["rm_w"])


if __name__ == "__main__":
    t0 = time.time()
    m = fa.run_demo()
    test_feedback_changes_behavior(m)
    test_reward_model_direction(m)
    test_gate_between_extremes(m)
    test_deterministic()
    elapsed = time.time() - t0
    assert elapsed < 30.0, "tests must finish in under 30s"
    print("4/4 test groups passed in %.2fs" % elapsed)
