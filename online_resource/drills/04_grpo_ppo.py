"""
Drill 04: GRPO / PPO 核心组件 + debug GRPO loop
=================================================

对应真题:
- Anthropic "RL Fundamentals" 轮: 给一段有 bug 的 GRPO training step, 现场找 bug 并修复
  (2026 高频新题; 也可能让你从零写 clipped surrogate + KL 惩罚)
- GDM post-training 深挖轮: 手写 group-relative advantage / k3 KL estimator,
  解释为什么 k3 比 naive (-Δ) 估计好 (无偏 + 恒非负 → 低方差)

冷写清单 (合上文件, 只看签名默写):
    token_log_probs(logits: [B, T, V], tokens: [B, T]) -> [B, T]
    group_relative_advantage(rewards: [G], eps=1e-8) -> [G]
    ppo_clipped_loss(logp_new, logp_old, adv, eps) -> scalar
    kl_k3_estimator(logp_policy, logp_ref) -> same shape
    grpo_token_loss(logp_new, logp_old, adv_per_seq, response_mask, kl, beta, clip_eps) -> scalar
    buggy_grpo_step(...) / fixed_grpo_step(...) -> scalar loss

建议 timebox:
- 函数 (1)-(4): 35 分钟内冷写完并让测试通过
- debug 练法: 先【不看】buggy_grpo_step 行尾的 "# BUG N" 标注, 限时 10 分钟自己找出
  3 个 bug 并口头说明各自的症状 (nan? loss 偏差? 梯度泄漏到 padding?), 再对答案写 fixed 版

三个经典 bug (先自己找, 再看这里):
1. logits -> logp 时没做 shift 对齐: logits[:, t] 预测的是 tokens[:, t+1]
2. loss 对 padding token 也计入 (直接 .mean() 而不是 mask 归一)
3. advantage 除以 std 时没加 eps 保护: 组内奖励全相同 -> 0/0 -> nan
"""

import torch
import torch.nn.functional as F

# ========================= COLD-WRITE ZONE =========================


def token_log_probs(logits: torch.Tensor, tokens: torch.Tensor) -> torch.Tensor:
    """log p(tokens[b, t]) under logits[b, t]. 调用方自己负责 shift 对齐."""
    logp = F.log_softmax(logits, dim=-1)  # log_softmax 内部做了 max 减法, 大 logits 也稳定
    return logp.gather(-1, tokens.unsqueeze(-1)).squeeze(-1)


def group_relative_advantage(rewards: torch.Tensor, eps: float = 1e-8) -> torch.Tensor:
    """GRPO: 组内标准化 (r - mean) / std; 组内全相同时返回全零 (信号为 0, 不该是 nan)."""
    mean = rewards.mean()
    std = rewards.std(unbiased=False)  # population std: G=1 时为 0 而不是 nan
    if std < eps:
        return torch.zeros_like(rewards)
    return (rewards - mean) / std


def ppo_clipped_loss(
    logp_new: torch.Tensor,
    logp_old: torch.Tensor,
    adv: torch.Tensor,
    eps: float,
) -> torch.Tensor:
    """PPO clipped surrogate. 最小化目标, 所以是 -min(...) 的均值."""
    ratio = torch.exp(logp_new - logp_old.detach())
    unclipped = ratio * adv
    clipped = torch.clamp(ratio, 1.0 - eps, 1.0 + eps) * adv
    return -torch.min(unclipped, clipped).mean()


def kl_k3_estimator(logp_policy: torch.Tensor, logp_ref: torch.Tensor) -> torch.Tensor:
    """Schulman k3 估计 KL(policy || ref), 样本 x ~ policy.

    r = p_ref(x)/p_policy(x), k3 = r - log r - 1.
    性质: 逐点 >= 0 (因为 e^d >= d + 1), 且 E_policy[k3] 恰等于 KL (无偏).
    """
    delta = logp_ref - logp_policy
    return torch.exp(delta) - delta - 1.0


def grpo_token_loss(
    logp_new: torch.Tensor,       # [B, T]
    logp_old: torch.Tensor,       # [B, T]
    adv_per_seq: torch.Tensor,    # [B]  每条序列一个 advantage
    response_mask: torch.Tensor,  # [B, T]  1 = response token, 0 = prompt/padding
    kl: torch.Tensor,             # [B, T]  逐 token KL 估计
    beta: float,
    clip_eps: float = 0.2,
) -> torch.Tensor:
    """token 级 clipped surrogate + beta * KL, 只在 mask 内做均值."""
    adv = adv_per_seq.unsqueeze(-1)  # [B, 1] 广播到每个 token
    ratio = torch.exp(logp_new - logp_old.detach())
    unclipped = ratio * adv
    clipped = torch.clamp(ratio, 1.0 - clip_eps, 1.0 + clip_eps) * adv
    per_token = -torch.min(unclipped, clipped) + beta * kl
    mask = response_mask.to(per_token.dtype)
    # clamp(min=1): 全零 mask 时返回 0 而不是 0/0 = nan
    return (per_token * mask).sum() / mask.sum().clamp(min=1.0)


def buggy_grpo_step(
    logits_new: torch.Tensor,     # [B, T, V] 当前 policy
    logits_old: torch.Tensor,     # [B, T, V] rollout 时的 policy
    logits_ref: torch.Tensor,     # [B, T, V] 冻结的 reference
    tokens: torch.Tensor,         # [B, T] prompt + response token ids
    response_mask: torch.Tensor,  # [B, T] 1 = response token
    rewards: torch.Tensor,        # [B] 每条序列一个标量奖励 (B == group size)
    clip_eps: float = 0.2,
    beta: float = 0.04,
) -> torch.Tensor:
    """一个完整的 GRPO step —— 里面埋了 3 个 bug, 先自己找再看行尾标注."""
    # --- group-relative advantage ---
    mean = rewards.mean()
    std = rewards.std(unbiased=False)
    adv = (rewards - mean) / std                                     # BUG 3
    adv = adv.unsqueeze(-1)  # [B, 1]

    # --- 采样 token 的逐位置 log-prob ---
    logp_new = token_log_probs(logits_new, tokens)                   # BUG 1
    logp_old = token_log_probs(logits_old, tokens).detach()
    logp_ref = token_log_probs(logits_ref, tokens).detach()

    # --- clipped surrogate ---
    ratio = torch.exp(logp_new - logp_old)
    unclipped = ratio * adv
    clipped = torch.clamp(ratio, 1.0 - clip_eps, 1.0 + clip_eps) * adv
    pg_loss = -torch.min(unclipped, clipped)

    # --- KL 惩罚 (k3) ---
    kl = torch.exp(logp_ref - logp_new) - (logp_ref - logp_new) - 1.0

    per_token = pg_loss + beta * kl
    return per_token.mean()                                          # BUG 2


def fixed_grpo_step(
    logits_new: torch.Tensor,
    logits_old: torch.Tensor,
    logits_ref: torch.Tensor,
    tokens: torch.Tensor,
    response_mask: torch.Tensor,
    rewards: torch.Tensor,
    clip_eps: float = 0.2,
    beta: float = 0.04,
) -> torch.Tensor:
    """buggy_grpo_step 的修复版 (复用上面的组件)."""
    adv = group_relative_advantage(rewards)                          # FIX 3: std<eps -> 全零

    targets = tokens[:, 1:]                                          # FIX 1: logits[t] 预测 token[t+1]
    mask = response_mask[:, 1:]
    logp_new = token_log_probs(logits_new[:, :-1], targets)
    logp_old = token_log_probs(logits_old[:, :-1], targets).detach()
    logp_ref = token_log_probs(logits_ref[:, :-1], targets).detach()

    kl = kl_k3_estimator(logp_new, logp_ref)
    return grpo_token_loss(                                          # FIX 2: mask 归一而不是 .mean()
        logp_new, logp_old, adv, mask, kl, beta=beta, clip_eps=clip_eps
    )


# ========================= TESTS =========================


def _make_batch(seed: int = 0):
    """B=4 条序列 (一个 group), T=6, V=7; 前 2 个位置是 prompt, 各行 response 长度不同."""
    torch.manual_seed(seed)
    B, T, V = 4, 6, 7
    tokens = torch.randint(0, V, (B, T))
    response_mask = torch.tensor(
        [
            [0, 0, 1, 1, 1, 1],  # response 长度 4
            [0, 0, 1, 1, 1, 0],  # 长度 3, 末尾 1 个 padding
            [0, 0, 1, 1, 0, 0],  # 长度 2, 末尾 2 个 padding
            [0, 0, 1, 1, 1, 1],
        ],
        dtype=torch.float32,
    )
    logits_old = 0.5 * torch.randn(B, T, V)
    logits_new = logits_old + 0.3 * torch.randn(B, T, V)
    logits_ref = logits_old.clone()
    rewards = torch.tensor([1.0, 0.0, 0.5, -0.5])
    return logits_new, logits_old, logits_ref, tokens, response_mask, rewards


def test_group_relative_advantage():
    # 全相同奖励 -> 全零, 绝不能是 nan
    adv = group_relative_advantage(torch.tensor([2.0, 2.0, 2.0, 2.0]))
    assert torch.equal(adv, torch.zeros(4))
    # G=1 也返回 0
    assert torch.equal(group_relative_advantage(torch.tensor([3.14])), torch.zeros(1))
    # 正常情况: 均值 0, 方差 1, 与手写公式一致
    r = torch.tensor([1.0, 2.0, 3.0, 4.0])
    adv = group_relative_advantage(r)
    expected = (r - r.mean()) / r.std(unbiased=False)
    assert torch.allclose(adv, expected, rtol=1e-6, atol=1e-6)
    assert torch.allclose(adv.mean(), torch.tensor(0.0), atol=1e-6)
    assert torch.allclose(adv.pow(2).mean(), torch.tensor(1.0), rtol=1e-5)


def test_ppo_clipped_loss_analytic():
    # eps=0.2, 手算 4 种 ratio/adv 组合:
    #   ratio=1.5, adv=+1: min(1.5, 1.2)   = 1.2  -> -1.2
    #   ratio=0.5, adv=+1: min(0.5, 0.8)   = 0.5  -> -0.5
    #   ratio=1.5, adv=-1: min(-1.5, -1.2) = -1.5 -> +1.5
    #   ratio=0.5, adv=-1: min(-0.5, -0.8) = -0.8 -> +0.8
    # loss = mean([-1.2, -0.5, 1.5, 0.8]) = 0.15
    ratio = torch.tensor([1.5, 0.5, 1.5, 0.5])
    adv = torch.tensor([1.0, 1.0, -1.0, -1.0])
    logp_old = torch.zeros(4)
    logp_new = torch.log(ratio)
    loss = ppo_clipped_loss(logp_new, logp_old, adv, eps=0.2)
    assert torch.allclose(loss, torch.tensor(0.15), rtol=1e-5, atol=1e-6)

    # ratio == 1 (on-policy 第一步): loss = -mean(adv)
    torch.manual_seed(0)
    logp = torch.randn(8)
    adv = torch.randn(8)
    loss = ppo_clipped_loss(logp, logp.clone(), adv, eps=0.2)
    assert torch.allclose(loss, -adv.mean(), rtol=1e-5, atol=1e-6)

    # advantage 全零 -> loss 为 0
    loss = ppo_clipped_loss(torch.randn(8), torch.randn(8), torch.zeros(8), eps=0.2)
    assert torch.allclose(loss, torch.tensor(0.0), atol=1e-7)


def test_kl_k3_estimator():
    # policy == ref -> 逐点恰为 0
    torch.manual_seed(0)
    logp = torch.randn(4, 6)
    assert torch.allclose(kl_k3_estimator(logp, logp.clone()), torch.zeros(4, 6), atol=1e-7)

    # 恒非负 (e^d >= d + 1), 随机输入下逐点成立
    lp, lq = torch.randn(1000), torch.randn(1000)
    k3 = kl_k3_estimator(lp, lq)
    assert (k3 >= -1e-7).all()

    # 无偏性: 离散分布上 E_p[k3] == KL(p||q), 与 torch.F.kl_div 对拍
    p = torch.tensor([0.7, 0.2, 0.1])
    q = torch.tensor([0.5, 0.25, 0.25])
    k3_per_point = kl_k3_estimator(p.log(), q.log())
    expectation = (p * k3_per_point).sum()
    true_kl = F.kl_div(q.log(), p, reduction="sum")  # = sum p * (log p - log q)
    assert torch.allclose(expectation, true_kl, rtol=1e-5, atol=1e-7)

    # 极大 logits: log_softmax 路径依然有限, policy==ref 时 KL 为 0
    big = torch.tensor([[[1000.0, -1000.0, 500.0]]])  # [B=1, T=1, V=3]
    tok = torch.tensor([[0]])                          # [B=1, T=1]
    lp_big = token_log_probs(big, tok)
    assert torch.isfinite(lp_big).all()
    assert torch.allclose(kl_k3_estimator(lp_big, lp_big.clone()), torch.zeros_like(lp_big))


def test_grpo_token_loss():
    torch.manual_seed(1)
    B, T = 3, 5
    logp_new = torch.randn(B, T)
    logp_old = torch.randn(B, T)
    adv = torch.tensor([1.0, -0.5, 0.2])
    kl = kl_k3_estimator(logp_new, logp_old)

    # 空 mask -> 0, 不是 nan
    empty = torch.zeros(B, T)
    loss = grpo_token_loss(logp_new, logp_old, adv, empty, kl, beta=0.1)
    assert torch.equal(loss, torch.tensor(0.0))

    # 全 1 mask + beta=0 时应等于 ppo_clipped_loss (adv 广播成逐 token)
    ones = torch.ones(B, T)
    loss = grpo_token_loss(logp_new, logp_old, adv, ones, kl, beta=0.0, clip_eps=0.2)
    ref = ppo_clipped_loss(logp_new, logp_old, adv.unsqueeze(-1).expand(B, T), eps=0.2)
    assert torch.allclose(loss, ref, rtol=1e-6, atol=1e-7)

    # KL 项线性: loss(beta) - loss(0) == beta * masked_mean(kl)
    mask = (torch.rand(B, T) > 0.4).float()
    beta = 0.5
    l_beta = grpo_token_loss(logp_new, logp_old, adv, mask, kl, beta=beta)
    l_zero = grpo_token_loss(logp_new, logp_old, adv, mask, kl, beta=0.0)
    kl_mean = (kl * mask).sum() / mask.sum()
    assert torch.allclose(l_beta - l_zero, beta * kl_mean, rtol=1e-5, atol=1e-6)

    # ratio==1, kl==0: loss = -masked_mean(adv 广播)
    zeros_kl = torch.zeros(B, T)
    l = grpo_token_loss(logp_new, logp_new.clone(), adv, mask, zeros_kl, beta=1.0)
    expected = -(adv.unsqueeze(-1) * mask).sum() / mask.sum()
    assert torch.allclose(l, expected, rtol=1e-5, atol=1e-6)


def test_buggy_vs_fixed_distinguishable():
    logits_new, logits_old, logits_ref, tokens, mask, rewards = _make_batch(seed=42)
    buggy = buggy_grpo_step(logits_new, logits_old, logits_ref, tokens, mask, rewards)
    fixed = fixed_grpo_step(logits_new, logits_old, logits_ref, tokens, mask, rewards)
    assert torch.isfinite(buggy) and torch.isfinite(fixed)
    # shift + padding 两个 bug 让两者在同一批数据上给出不同的 loss
    assert not torch.allclose(buggy, fixed, rtol=1e-3, atol=1e-4)


def test_buggy_nan_on_equal_rewards_fixed_is_fine():
    logits_new, logits_old, logits_ref, tokens, mask, _ = _make_batch(seed=7)
    equal_rewards = torch.ones(4)
    buggy = buggy_grpo_step(logits_new, logits_old, logits_ref, tokens, mask, equal_rewards)
    fixed = fixed_grpo_step(logits_new, logits_old, logits_ref, tokens, mask, equal_rewards)
    assert torch.isnan(buggy)  # BUG 3: 0/0
    assert torch.isfinite(fixed)
    assert fixed >= 0.0  # adv 全零, 只剩 beta * masked_mean(k3), k3 恒非负

    # 再加一条解析性质: policy == ref 且奖励全相同 -> fixed loss 恰为 0
    fixed0 = fixed_grpo_step(logits_new, logits_old, logits_new.clone(), tokens, mask, equal_rewards)
    assert torch.allclose(fixed0, torch.tensor(0.0), atol=1e-6)


def test_fixed_matches_primitive_composition():
    # fixed_grpo_step 必须和 "手动 shift + 组件组合" 逐位一致
    logits_new, logits_old, logits_ref, tokens, mask, rewards = _make_batch(seed=3)
    fixed = fixed_grpo_step(logits_new, logits_old, logits_ref, tokens, mask, rewards,
                            clip_eps=0.2, beta=0.04)
    adv = group_relative_advantage(rewards)
    lp_new = token_log_probs(logits_new[:, :-1], tokens[:, 1:])
    lp_old = token_log_probs(logits_old[:, :-1], tokens[:, 1:])
    lp_ref = token_log_probs(logits_ref[:, :-1], tokens[:, 1:])
    kl = kl_k3_estimator(lp_new, lp_ref)
    ref = grpo_token_loss(lp_new, lp_old, adv, mask[:, 1:], kl, beta=0.04, clip_eps=0.2)
    assert torch.allclose(fixed, ref, rtol=1e-6, atol=1e-7)


def test_gradient_masking():
    # fixed: padding / prompt 尾部对应的 logits 位置梯度应为 0; buggy 会泄漏梯度
    logits_new, logits_old, logits_ref, tokens, mask, rewards = _make_batch(seed=11)

    g_new = logits_new.clone().requires_grad_(True)
    fixed_grpo_step(g_new, logits_old, logits_ref, tokens, mask, rewards).backward()
    grad = g_new.grad
    assert torch.isfinite(grad).all()
    # logits 位置 t 只通过预测 token t+1 参与 loss, 所以 mask[:, 1:][:, t]==0 处梯度为 0
    target_mask = mask[:, 1:]  # [B, T-1]
    masked_out = grad[:, :-1][target_mask == 0]
    assert torch.allclose(masked_out, torch.zeros_like(masked_out), atol=1e-9)
    # 最后一个位置的 logits 不预测任何 target, 梯度恒为 0
    assert torch.allclose(grad[:, -1], torch.zeros_like(grad[:, -1]), atol=1e-9)

    b_new = logits_new.clone().requires_grad_(True)
    buggy_grpo_step(b_new, logits_old, logits_ref, tokens, mask, rewards).backward()
    # BUG 1 + BUG 2: buggy 版在最后一个位置也有非零梯度 (根本不该被训练到)
    assert b_new.grad[:, -1].abs().max() > 1e-6


if __name__ == "__main__":
    tests = [
        test_group_relative_advantage,
        test_ppo_clipped_loss_analytic,
        test_kl_k3_estimator,
        test_grpo_token_loss,
        test_buggy_vs_fixed_distinguishable,
        test_buggy_nan_on_equal_rewards_fixed_is_fine,
        test_fixed_matches_primitive_composition,
        test_gradient_masking,
    ]
    for t in tests:
        t()
        print(f"[PASS] {t.__name__}")
    print("ALL TESTS PASSED")
