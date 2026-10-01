"""Drill 03: 常考 Loss 手写（全部从 logits 出发）。

对应真题：
  - GDM ML coding 轮：手写 cross-entropy（不许调 F.cross_entropy），追问数值稳定性
  - OpenAI ML coding：BCE-with-logits 稳定式推导 + 实现
  - Anthropic RL 轮 / agentic 后训练（2026 中文大厂同款）：多轮对话 loss masking——
    只对 assistant token 计损失，除以有效 token 数，追问全 0 mask 会不会 NaN、
    masked 位置的 label 是 -100 时 gather 会不会炸
  - RLHF 三件套追问：reward model pairwise loss、DPO loss（policy==ref 时 loss 是多少？）

冷写清单（建议 timebox：全部 5 个函数 25 分钟，测试不用背）：
  1. cross_entropy_from_logits(logits: (N, C), targets: (N,)) -> scalar
       log_softmax + gather，mean reduction
  2. masked_cross_entropy(logits: (B, T, V), targets: (B, T), loss_mask: (B, T)) -> scalar
       只对 mask=1 的 token 计损失，sum(loss*mask) / max(sum(mask), 1)；
       masked 位置 label 可能是 -100，gather 前要替换掉
  3. bce_with_logits(logits, targets) -> scalar
       稳定式：max(x, 0) - x*z + log(1 + exp(-|x|))，mean reduction
  4. reward_model_pairwise_loss(chosen_scores, rejected_scores) -> scalar
       -logsigmoid(chosen - rejected)，mean
  5. dpo_loss(policy_chosen_logps, policy_rejected_logps,
              ref_chosen_logps, ref_rejected_logps, beta) -> scalar
       -logsigmoid(beta * ((pi_c - pi_r) - (ref_c - ref_r)))，mean

面试口头要点（写代码时顺嘴说出来加分）：
  - log_softmax 内部就是 x - logsumexp(x)，比先 softmax 再 log 稳定
  - masked CE 的分母 clamp(min=1) 是为了全 0 mask 时返回 0 而不是 0/0=NaN
  - BCE 稳定式来自 softplus(x) - x*z 的分段改写，|x| 很大时 exp(-|x|) -> 0 不会溢出
  - DPO 在 policy==ref 时内部 logit 为 0，loss = -log(1/2) = log 2 ≈ 0.693
"""

from __future__ import annotations

import torch
import torch.nn.functional as F

# ========================= COLD-WRITE ZONE =========================


def cross_entropy_from_logits(logits: torch.Tensor, targets: torch.Tensor) -> torch.Tensor:
    """Cross-entropy from raw logits.

    logits: (N, C) float, targets: (N,) int64 class indices. Mean over N.
    """
    log_probs = F.log_softmax(logits, dim=-1)  # = x - logsumexp(x), stable for huge logits
    nll = -log_probs.gather(dim=-1, index=targets.unsqueeze(-1)).squeeze(-1)  # (N,)
    return nll.mean()


def masked_cross_entropy(
    logits: torch.Tensor, targets: torch.Tensor, loss_mask: torch.Tensor
) -> torch.Tensor:
    """Token-level CE for multi-turn agent training: only mask==1 tokens count.

    logits: (B, T, V), targets: (B, T) int64, loss_mask: (B, T) bool/0-1.
    Returns sum(per_token_loss * mask) / max(sum(mask), 1).
    """
    mask = loss_mask.to(logits.dtype)
    # Masked positions often carry ignore labels like -100; gather would crash on
    # out-of-range indices, so replace them with a valid dummy class first.
    safe_targets = torch.where(loss_mask.bool(), targets, torch.zeros_like(targets))
    log_probs = F.log_softmax(logits, dim=-1)  # (B, T, V)
    nll = -log_probs.gather(dim=-1, index=safe_targets.unsqueeze(-1)).squeeze(-1)  # (B, T)
    # clamp denominator so an all-zero mask gives 0 loss instead of 0/0 = NaN
    return (nll * mask).sum() / mask.sum().clamp(min=1.0)


def bce_with_logits(logits: torch.Tensor, targets: torch.Tensor) -> torch.Tensor:
    """Binary cross-entropy from logits, numerically stable form.

    Derivation: loss = softplus(x) - x*z, rewritten piecewise as
    max(x, 0) - x*z + log(1 + exp(-|x|)) so exp never overflows.
    """
    loss = logits.clamp(min=0) - logits * targets + torch.log1p(torch.exp(-logits.abs()))
    return loss.mean()


def reward_model_pairwise_loss(
    chosen_scores: torch.Tensor, rejected_scores: torch.Tensor
) -> torch.Tensor:
    """Bradley-Terry pairwise loss: -log sigmoid(chosen - rejected), mean."""
    return -F.logsigmoid(chosen_scores - rejected_scores).mean()


def dpo_loss(
    policy_chosen_logps: torch.Tensor,
    policy_rejected_logps: torch.Tensor,
    ref_chosen_logps: torch.Tensor,
    ref_rejected_logps: torch.Tensor,
    beta: float = 0.1,
) -> torch.Tensor:
    """DPO loss: -log sigmoid(beta * (policy_logratio - ref_logratio)), mean.

    Inputs are per-sequence summed log-probs, shape (B,).
    """
    pi_logratios = policy_chosen_logps - policy_rejected_logps
    ref_logratios = ref_chosen_logps - ref_rejected_logps
    return -F.logsigmoid(beta * (pi_logratios - ref_logratios)).mean()


# ========================= TESTS =========================


def test_cross_entropy_matches_torch() -> None:
    torch.manual_seed(0)
    logits = torch.randn(64, 10)
    targets = torch.randint(0, 10, (64,))
    ours = cross_entropy_from_logits(logits, targets)
    ref = F.cross_entropy(logits, targets)
    assert torch.allclose(ours, ref, rtol=1e-5, atol=1e-7), (ours, ref)


def test_cross_entropy_uniform_logits_analytic() -> None:
    # all-identical logits -> uniform distribution -> CE = log(C)
    logits = torch.full((5, 7), 3.14)
    targets = torch.randint(0, 7, (5,))
    ours = cross_entropy_from_logits(logits, targets)
    assert torch.allclose(ours, torch.log(torch.tensor(7.0)), rtol=1e-6, atol=1e-7), ours


def test_cross_entropy_extreme_logits_stable() -> None:
    # huge logits must not overflow to inf/nan; still match torch
    torch.manual_seed(1)
    logits = torch.randn(32, 5) * 1e4
    targets = torch.randint(0, 5, (32,))
    ours = cross_entropy_from_logits(logits, targets)
    ref = F.cross_entropy(logits, targets)
    assert torch.isfinite(ours), ours
    assert torch.allclose(ours, ref, rtol=1e-5, atol=1e-6), (ours, ref)


def test_masked_ce_matches_ignore_index() -> None:
    torch.manual_seed(2)
    B, T, V = 4, 9, 11
    logits = torch.randn(B, T, V)
    targets = torch.randint(0, V, (B, T))
    loss_mask = (torch.rand(B, T) > 0.4).long()
    assert loss_mask.sum() > 0  # make sure this case isn't degenerate
    # masked positions carry -100 exactly like HF-style labels
    labels = torch.where(loss_mask.bool(), targets, torch.full_like(targets, -100))
    ours = masked_cross_entropy(logits, labels, loss_mask)
    ref = F.cross_entropy(logits.reshape(-1, V), labels.reshape(-1), ignore_index=-100)
    assert torch.allclose(ours, ref, rtol=1e-5, atol=1e-7), (ours, ref)


def test_masked_ce_full_mask_equals_plain_ce() -> None:
    torch.manual_seed(3)
    B, T, V = 2, 5, 6
    logits = torch.randn(B, T, V)
    targets = torch.randint(0, V, (B, T))
    ours = masked_cross_entropy(logits, targets, torch.ones(B, T))
    ref = F.cross_entropy(logits.reshape(-1, V), targets.reshape(-1))
    assert torch.allclose(ours, ref, rtol=1e-5, atol=1e-7), (ours, ref)


def test_masked_ce_all_zero_mask_no_nan() -> None:
    torch.manual_seed(4)
    B, T, V = 2, 4, 5
    logits = torch.randn(B, T, V, requires_grad=True)
    # all labels are -100: would crash gather if not sanitized
    labels = torch.full((B, T), -100, dtype=torch.long)
    loss = masked_cross_entropy(logits, labels, torch.zeros(B, T))
    assert torch.allclose(loss, torch.tensor(0.0)), loss
    loss.backward()
    assert logits.grad is not None
    assert torch.isfinite(logits.grad).all(), "grad has NaN/Inf on empty mask"
    assert torch.allclose(logits.grad, torch.zeros_like(logits.grad)), "empty mask should give zero grad"


def test_bce_matches_torch() -> None:
    torch.manual_seed(5)
    logits = torch.randn(50)
    targets = torch.rand(50)  # soft targets allowed too
    ours = bce_with_logits(logits, targets)
    ref = F.binary_cross_entropy_with_logits(logits, targets)
    assert torch.allclose(ours, ref, rtol=1e-5, atol=1e-7), (ours, ref)
    # hard 0/1 labels
    hard = torch.randint(0, 2, (50,)).float()
    ours = bce_with_logits(logits, hard)
    ref = F.binary_cross_entropy_with_logits(logits, hard)
    assert torch.allclose(ours, ref, rtol=1e-5, atol=1e-7), (ours, ref)


def test_bce_extreme_logits_stable() -> None:
    logits = torch.tensor([-200.0, -50.0, 0.0, 50.0, 200.0])
    targets = torch.tensor([0.0, 1.0, 0.5, 0.0, 1.0])
    ours = bce_with_logits(logits, targets)
    ref = F.binary_cross_entropy_with_logits(logits, targets)
    assert torch.isfinite(ours), ours
    assert torch.allclose(ours, ref, rtol=1e-5, atol=1e-7), (ours, ref)


def test_rm_pairwise_analytic_and_grad() -> None:
    # equal scores -> loss = -log(1/2) = log 2
    chosen = torch.tensor([1.0, -2.0, 0.5], requires_grad=True)
    rejected = chosen.detach().clone()
    loss = reward_model_pairwise_loss(chosen, rejected)
    assert torch.allclose(loss, torch.log(torch.tensor(2.0)), rtol=1e-6, atol=1e-7), loss
    loss.backward()
    # pushing chosen scores up decreases the loss -> gradient must be negative
    assert (chosen.grad < 0).all(), chosen.grad
    # match torch's logsigmoid on random inputs
    torch.manual_seed(6)
    c, r = torch.randn(40), torch.randn(40)
    ref = -F.logsigmoid(c - r).mean()
    assert torch.allclose(reward_model_pairwise_loss(c, r), ref, rtol=1e-5, atol=1e-7)


def test_dpo_policy_equals_ref() -> None:
    torch.manual_seed(7)
    pc = torch.randn(8, requires_grad=True)
    pr = torch.randn(8, requires_grad=True)
    for beta in (0.05, 0.1, 0.5):
        loss = dpo_loss(pc, pr, pc.detach().clone(), pr.detach().clone(), beta=beta)
        # policy == ref -> inner logit is 0 -> loss = log 2, independent of beta
        assert torch.allclose(loss, torch.log(torch.tensor(2.0)), rtol=1e-6, atol=1e-7), loss


def test_dpo_gradient_direction() -> None:
    torch.manual_seed(8)
    pc = torch.randn(8, requires_grad=True)
    pr = torch.randn(8, requires_grad=True)
    loss = dpo_loss(pc, pr, torch.randn(8), torch.randn(8), beta=0.1)
    loss.backward()
    # raising chosen logp lowers loss; raising rejected logp raises loss
    assert (pc.grad < 0).all(), pc.grad
    assert (pr.grad > 0).all(), pr.grad


if __name__ == "__main__":
    tests = [
        test_cross_entropy_matches_torch,
        test_cross_entropy_uniform_logits_analytic,
        test_cross_entropy_extreme_logits_stable,
        test_masked_ce_matches_ignore_index,
        test_masked_ce_full_mask_equals_plain_ce,
        test_masked_ce_all_zero_mask_no_nan,
        test_bce_matches_torch,
        test_bce_extreme_logits_stable,
        test_rm_pairwise_analytic_and_grad,
        test_dpo_policy_equals_ref,
        test_dpo_gradient_direction,
    ]
    for t in tests:
        t()
        print(f"PASS {t.__name__}")
    print("ALL TESTS PASSED")
