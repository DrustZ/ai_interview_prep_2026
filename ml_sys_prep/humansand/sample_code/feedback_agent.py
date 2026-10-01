"""Minimal runnable demo: a personal-assistant agent that learns from human feedback.

Three ideas, one file (mock LLM, numpy only, fully deterministic):
  (a) human corrections -> distilled preference RULES injected into later
      decisions (the in-context learning path)
  (b) the same corrections as preference pairs -> a tiny Bradley-Terry reward
      model (hand-rolled logistic regression) used to RERANK candidate
      responses (the post-training path, in miniature)
  (c) an uncertainty GATE: when the reward margin is low, ASK the human
      instead of acting (mixed-initiative HCI: interruption cost vs error
      cost, quantified)

Run:  python feedback_agent.py
"""
import numpy as np

SEED = 13
FEATURES = ["formality", "brevity", "warmth", "emoji", "structure"]
D = len(FEATURES)

# What THIS user actually wants. Hidden from the agent; only used to simulate
# human feedback (likes formal, brief, structured drafts; dislikes emoji).
HUMAN_W = np.array([2.0, 1.5, 0.5, -2.5, 1.0])

# Generic pretrained-assistant prior: chatty, emoji-happy. Mismatched on
# purpose -- this is the "one model, many users" personalization gap.
BASE_W = np.array([0.0, -1.0, 1.5, 1.5, 0.0])

CATEGORIES = ["email_to_manager", "reschedule_meeting", "status_update", "intro_message"]
N_TRAIN, N_CALIB, N_HELDOUT, N_CANDS = 60, 20, 40, 4
RULE_STRENGTH = 2.0   # how hard an injected rule biases scoring
RM_SCALE = 3.0        # weight of the reward model at rerank time
ASK_COST = 1.0        # cost of interrupting the human with a question
ERROR_COST = 5.0      # cost of confidently acting and being wrong
TAU_GRID = np.arange(0.55, 0.96, 0.05)  # candidate ask thresholds


def sigmoid(z):
    return 1.0 / (1.0 + np.exp(-z))


def make_tasks(n_tasks, n_cands, rng):
    """Mock LLM: for each assistant task, propose n_cands drafts. A draft is
    represented only by its style features in [0,1]^D (text elided)."""
    tasks = []
    for i in range(n_tasks):
        tasks.append({
            "id": i,
            "category": CATEGORIES[i % len(CATEGORIES)],
            "candidates": rng.rand(n_cands, D),
        })
    return tasks


def human_pick(task):
    """Which draft the human actually prefers (simulator ground truth)."""
    return int(np.argmax(task["candidates"] @ HUMAN_W))


class Agent:
    """Mock-LLM assistant. Score = frozen base prior + injected rules
    (in-context path) + reward-model rerank (post-training path)."""

    def __init__(self):
        self.rules = []    # [(feature_idx, direction)] distilled from corrections
        self.rm_w = None   # Bradley-Terry reward model weights

    def scores(self, cands, use_rules=True, use_rm=True):
        s = cands @ BASE_W
        if use_rules:
            for j, direction in self.rules:
                s = s + RULE_STRENGTH * direction * cands[:, j]
        if use_rm and self.rm_w is not None:
            s = s + RM_SCALE * (cands @ self.rm_w)
        return s

    def pick(self, cands, use_rules=True, use_rm=True):
        return int(np.argmax(self.scores(cands, use_rules, use_rm)))

    def distill_rules(self, pairs, threshold=0.12):
        """Compress corrections into human-readable, retrievable rules: any
        feature whose mean (preferred - rejected) gap is consistent enough."""
        diffs = np.array([p - r for p, r in pairs])
        mean_gap = diffs.mean(axis=0)
        self.rules = [(j, 1.0 if mean_gap[j] > 0 else -1.0)
                      for j in range(D) if abs(mean_gap[j]) > threshold]

    def rule_texts(self):
        return [("PREFER more %s" if d > 0 else "AVOID %s") % FEATURES[j]
                for j, d in self.rules]


def collect_corrections(agent, tasks):
    """Human reviews the agent's pick; when it is not what they wanted, they
    point at the draft they DID want. One choose-1-of-k correction yields
    (k-1) preference pairs: (wanted, each other draft)."""
    pairs, n_corrections = [], 0
    for t in tasks:
        a = agent.pick(t["candidates"])
        h = human_pick(t)
        if a != h:
            n_corrections += 1
            for j in range(len(t["candidates"])):
                if j != h:
                    pairs.append((t["candidates"][h], t["candidates"][j]))
    return pairs, n_corrections


def fit_reward_model(pairs, lr=0.5, epochs=2000, l2=1e-4):
    """Bradley-Terry: maximize sum log sigmoid(w . (f_pref - f_rej)).
    Hand-rolled gradient ascent; no sklearn."""
    X = np.array([p - r for p, r in pairs])
    w = np.zeros(D)
    for _ in range(epochs):
        grad = X.T @ (1.0 - sigmoid(X @ w)) / len(X)
        w = w + lr * (grad - l2 * w)
    return w


def match_rate(agent, tasks, use_rules=True, use_rm=True):
    """Fraction of tasks where the agent's pick equals the human's pick."""
    hits = [agent.pick(t["candidates"], use_rules, use_rm) == human_pick(t)
            for t in tasks]
    return float(np.mean(hits))


def rm_heldout_accuracy(rm_w, tasks):
    """Pairwise accuracy of the reward model on unseen tasks."""
    correct, total = 0, 0
    for t in tasks:
        h = human_pick(t)
        for j in range(len(t["candidates"])):
            if j != h:
                total += 1
                correct += int((t["candidates"][h] - t["candidates"][j]) @ rm_w > 0)
    return correct / total


def gate_policy_costs(agent, tasks, tau):
    """Ask-vs-act. Confidence = RM's P(top beats runner-up). Compare the gate
    against the two degenerate policies: always-ask and never-ask."""
    gate = always = never = 0.0
    n_ask = n_act_errors = 0
    for t in tasks:
        s = agent.scores(t["candidates"])
        order = np.argsort(-s)
        top, second = int(order[0]), int(order[1])
        conf = sigmoid((t["candidates"][top] - t["candidates"][second]) @ agent.rm_w)
        wrong = top != human_pick(t)
        always += ASK_COST
        never += ERROR_COST if wrong else 0.0
        if conf < tau:                      # low margin: interrupt the human
            gate += ASK_COST
            n_ask += 1
        else:                               # confident: act autonomously
            gate += ERROR_COST if wrong else 0.0
            n_act_errors += int(wrong)
    return {"gate": gate, "always_ask": always, "never_ask": never,
            "n_ask": n_ask, "n_act_errors": n_act_errors, "n_tasks": len(tasks)}


def calibrate_gate_tau(agent, calib_tasks):
    """Pick the ask threshold that minimizes total cost on a calibration split
    (not hand-set, and never tuned on the held-out set)."""
    best_tau, best_cost = None, None
    for tau in TAU_GRID:
        cost = gate_policy_costs(agent, calib_tasks, tau)["gate"]
        if best_cost is None or cost < best_cost:
            best_tau, best_cost = float(tau), cost
    return best_tau


def run_demo(seed=SEED):
    rng = np.random.RandomState(seed)
    train = make_tasks(N_TRAIN, N_CANDS, rng)
    calib = make_tasks(N_CALIB, N_CANDS, rng)
    heldout = make_tasks(N_HELDOUT, N_CANDS, rng)
    agent = Agent()

    before = match_rate(agent, heldout)             # generic prior, no feedback
    pairs, n_corr = collect_corrections(agent, train)   # human corrects the agent
    agent.distill_rules(pairs)                      # path (a): rules
    rules_only = match_rate(agent, heldout, use_rm=False)
    agent.rm_w = fit_reward_model(pairs)            # path (b): reward model
    rm_acc = rm_heldout_accuracy(agent.rm_w, heldout)
    after = match_rate(agent, heldout)              # rules + RM rerank
    tau = calibrate_gate_tau(agent, calib)          # path (c): ask-vs-act gate
    costs = gate_policy_costs(agent, heldout, tau)

    return {"before": before, "rules_only": rules_only, "after": after,
            "rm_acc": rm_acc, "n_pairs": len(pairs), "n_corrections": n_corr,
            "rules": agent.rule_texts(), "rm_w": agent.rm_w, "tau": tau,
            "costs": costs, "agent": agent, "heldout": heldout}


def main():
    m = run_demo()
    c = m["costs"]
    print("== Personal assistant that learns from human feedback (mock LLM, numpy) ==")
    print("train tasks: %d | calibration tasks: %d | held-out tasks: %d | drafts per task: %d"
          % (N_TRAIN, N_CALIB, N_HELDOUT, N_CANDS))
    print()
    print("[1] BEFORE feedback  held-out preference match: %5.1f%%" % (100 * m["before"]))
    print("[2] %d corrections -> %d preference pairs"
          % (m["n_corrections"], m["n_pairs"]))
    print("[3a] distilled rules (injected in-context):")
    for r in m["rules"]:
        print("      - " + r)
    print("     rules only          held-out preference match: %5.1f%%"
          % (100 * m["rules_only"]))
    print("[3b] reward model (Bradley-Terry LR)  held-out pairwise acc: %5.1f%%"
          % (100 * m["rm_acc"]))
    print("     rules + RM rerank   held-out preference match: %5.1f%%"
          % (100 * m["after"]))
    print("[4] ask-vs-act gate: ask iff P(top beats runner-up) < %.2f"
          " (calibrated; ask=%.0f, error=%.0f)" % (m["tau"], ASK_COST, ERROR_COST))
    print("     always-ask cost: %5.1f | never-ask cost: %5.1f | gate cost: %5.1f"
          % (c["always_ask"], c["never_ask"], c["gate"]))
    print("     asked %d/%d tasks; errors while acting: %d"
          % (c["n_ask"], c["n_tasks"], c["n_act_errors"]))

    # Pin the headline claims.
    assert m["after"] >= m["before"] + 0.30, "feedback must lift match rate by >=30pts"
    assert m["rules_only"] > m["before"], "rules alone must already help"
    assert m["rm_acc"] >= 0.90, "reward model must generalize to held-out pairs"
    assert c["gate"] < c["always_ask"], "gate must beat always-ask"
    assert c["gate"] < c["never_ask"], "gate must beat never-ask"
    assert 0 < c["n_ask"] < c["n_tasks"], "gate must be selective, not degenerate"
    print()
    print("all main-script assertions passed")


if __name__ == "__main__":
    main()
