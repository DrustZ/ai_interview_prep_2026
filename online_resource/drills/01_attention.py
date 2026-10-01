"""Drill 01: Attention from scratch.

对应真题
--------
- GDM ML coding 轮: 手写 scaled dot-product attention / Multi-Head Attention
  是标配题, 常要求 numpy 或 torch 两个版本, 并追问 causal mask 与数值稳定性。
- OpenAI transformer 题: 实现 MHA 模块 (显式 reshape/transpose 拆头),
  以及 GQA/MQA 变体 (K/V 头广播), 考察对 KV cache 省显存动机的理解。

冷写清单 (函数签名)
-------------------
1. scaled_dot_product_attention(q, k, v, mask=None) -> (out, attn)   # 纯 numpy
2. build_causal_mask(T) -> torch.Tensor                              # (T, T) bool, True=可见
3. class MultiHeadAttention(nn.Module):
       __init__(self, d_model, n_heads, causal=False)
       forward(self, x) -> torch.Tensor                              # 自注意力
4. grouped_query_attention(q, k, v, n_kv_heads) -> torch.Tensor      # GQA, K/V 头广播

建议 timebox
------------
- numpy SDPA + causal mask:  10 min
- MultiHeadAttention:        15 min
- GQA:                        8 min
- 总计 ~35 min (含自测)
"""

from __future__ import annotations

import math

import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F

# ========================= COLD-WRITE ZONE =========================


def scaled_dot_product_attention(
    q: np.ndarray,
    k: np.ndarray,
    v: np.ndarray,
    mask: np.ndarray | None = None,
) -> tuple[np.ndarray, np.ndarray]:
    """Pure-numpy attention.

    q: (..., T_q, d), k: (..., T_k, d), v: (..., T_k, d_v)
    mask: bool, broadcastable to (..., T_q, T_k), True = 允许注意。
    Returns (out, attn): (..., T_q, d_v) and (..., T_q, T_k).
    """
    d = q.shape[-1]
    scores = q @ np.swapaxes(k, -1, -2) / math.sqrt(d)
    if mask is not None:
        # 用大负数而不是 -inf: 整行被 mask 时退化为均匀分布而不是 NaN
        scores = np.where(mask, scores, -1e9)
    # 数值稳定 softmax: 逐行减最大值, exp 不会上溢
    scores = scores - scores.max(axis=-1, keepdims=True)
    weights = np.exp(scores)
    attn = weights / weights.sum(axis=-1, keepdims=True)
    out = attn @ v
    return out, attn


def build_causal_mask(T: int) -> torch.Tensor:
    """(T, T) bool 下三角: mask[i, j] = True 表示位置 i 可以看到 j (j <= i)."""
    return torch.tril(torch.ones(T, T, dtype=torch.bool))


class MultiHeadAttention(nn.Module):
    """标准 MHA (自注意力), 显式 reshape/transpose 拆头, 不用 F.sdpa."""

    def __init__(self, d_model: int, n_heads: int, causal: bool = False) -> None:
        super().__init__()
        assert d_model % n_heads == 0, "d_model must be divisible by n_heads"
        self.d_model = d_model
        self.n_heads = n_heads
        self.d_head = d_model // n_heads
        self.causal = causal
        self.q_proj = nn.Linear(d_model, d_model)
        self.k_proj = nn.Linear(d_model, d_model)
        self.v_proj = nn.Linear(d_model, d_model)
        self.out_proj = nn.Linear(d_model, d_model)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        B, T, _ = x.shape
        # (B, T, d_model) -> (B, T, h, d_head) -> (B, h, T, d_head)
        q = self.q_proj(x).view(B, T, self.n_heads, self.d_head).transpose(1, 2)
        k = self.k_proj(x).view(B, T, self.n_heads, self.d_head).transpose(1, 2)
        v = self.v_proj(x).view(B, T, self.n_heads, self.d_head).transpose(1, 2)

        scores = q @ k.transpose(-2, -1) / math.sqrt(self.d_head)  # (B, h, T, T)
        if self.causal:
            mask = build_causal_mask(T).to(x.device)  # (T, T), 广播到 (B, h, T, T)
            scores = scores.masked_fill(~mask, float("-inf"))
        attn = torch.softmax(scores, dim=-1)

        out = attn @ v  # (B, h, T, d_head)
        # transpose 后内存不连续, view 前必须 contiguous
        out = out.transpose(1, 2).contiguous().view(B, T, self.d_model)
        return self.out_proj(out)


def grouped_query_attention(
    q: torch.Tensor,
    k: torch.Tensor,
    v: torch.Tensor,
    n_kv_heads: int,
) -> torch.Tensor:
    """GQA: q (B, n_heads, T, d), k/v (B, n_kv_heads, T, d)。

    每 group_size = n_heads // n_kv_heads 个 query 头共享一个 K/V 头。
    """
    B, n_heads, T, d = q.shape
    assert n_heads % n_kv_heads == 0, "n_heads must be divisible by n_kv_heads"
    assert k.shape[1] == n_kv_heads and v.shape[1] == n_kv_heads
    group_size = n_heads // n_kv_heads
    # 把每个 K/V 头复制 group_size 次, 对齐到 n_heads
    k = k.repeat_interleave(group_size, dim=1)  # (B, n_heads, T, d)
    v = v.repeat_interleave(group_size, dim=1)

    scores = q @ k.transpose(-2, -1) / math.sqrt(d)
    attn = torch.softmax(scores, dim=-1)
    return attn @ v


# ========================= TESTS =========================


def _torch_einsum_reference(
    q: torch.Tensor,
    k: torch.Tensor,
    v: torch.Tensor,
    mask: torch.Tensor | None = None,
) -> torch.Tensor:
    """独立的 torch 参考实现 (einsum), 用于对拍 numpy 版本。"""
    d = q.shape[-1]
    scores = torch.einsum("...qd,...kd->...qk", q, k) / math.sqrt(d)
    if mask is not None:
        scores = scores.masked_fill(~mask, float("-inf"))
    attn = torch.softmax(scores, dim=-1)
    return torch.einsum("...qk,...kd->...qd", attn, v)


def test_numpy_sdpa_matches_torch_einsum() -> None:
    rng = np.random.default_rng(0)
    B, T, d = 2, 5, 8
    q = rng.standard_normal((B, T, d))
    k = rng.standard_normal((B, T, d))
    v = rng.standard_normal((B, T, d))

    # 无 mask
    out_np, attn = scaled_dot_product_attention(q, k, v)
    ref = _torch_einsum_reference(
        torch.from_numpy(q), torch.from_numpy(k), torch.from_numpy(v)
    ).numpy()
    assert out_np.shape == (B, T, d)
    assert np.allclose(out_np, ref, rtol=1e-6, atol=1e-8)
    assert np.allclose(attn.sum(axis=-1), 1.0, atol=1e-10)

    # causal mask
    mask_t = build_causal_mask(T)
    out_np_c, attn_c = scaled_dot_product_attention(q, k, v, mask=mask_t.numpy())
    ref_c = _torch_einsum_reference(
        torch.from_numpy(q), torch.from_numpy(k), torch.from_numpy(v), mask=mask_t
    ).numpy()
    assert np.allclose(out_np_c, ref_c, rtol=1e-6, atol=1e-8)
    # 被 mask 的位置权重应为 0
    assert np.all(attn_c[:, ~mask_t.numpy()] == 0.0)


def test_numpy_sdpa_edge_cases() -> None:
    rng = np.random.default_rng(1)
    T, d = 4, 8

    # 极大 logits: 不减最大值的 naive softmax 会 exp 上溢出 NaN
    q = 1e4 * np.ones((T, d))
    k = 1e4 * np.ones((T, d))
    v = rng.standard_normal((T, d))
    out, attn = scaled_dot_product_attention(q, k, v)
    assert np.all(np.isfinite(out))
    assert np.allclose(attn, 1.0 / T, atol=1e-12)  # 分数全相同 -> 均匀权重

    # 全相同 value: 输出应恰为该 value
    v_const = np.ones((T, d)) * 3.7
    q2 = rng.standard_normal((T, d))
    k2 = rng.standard_normal((T, d))
    out2, _ = scaled_dot_product_attention(q2, k2, v_const)
    assert np.allclose(out2, 3.7, atol=1e-12)

    # 整行全 False 的 mask: 不应出 NaN (退化为均匀注意)
    mask = np.zeros((T, T), dtype=bool)
    mask[1:, :] = True
    out3, attn3 = scaled_dot_product_attention(q2, k2, v, mask=mask)
    assert np.all(np.isfinite(out3))
    assert np.allclose(attn3[0], 1.0 / T, atol=1e-12)

    # T_q != T_k (cross-attention 形状)
    q4 = rng.standard_normal((3, d))
    out4, attn4 = scaled_dot_product_attention(q4, k2, v)
    assert out4.shape == (3, d) and attn4.shape == (3, T)


def test_build_causal_mask() -> None:
    m = build_causal_mask(4)
    assert m.shape == (4, 4) and m.dtype == torch.bool
    expected = torch.tensor(
        [
            [True, False, False, False],
            [True, True, False, False],
            [True, True, True, False],
            [True, True, True, True],
        ]
    )
    assert torch.equal(m, expected)
    # T=1 边界: 单 token 只能看自己
    assert torch.equal(build_causal_mask(1), torch.ones(1, 1, dtype=torch.bool))


def test_mha_shapes_and_causality() -> None:
    torch.manual_seed(0)
    B, T, d_model, n_heads = 2, 6, 32, 4
    mha = MultiHeadAttention(d_model, n_heads, causal=True).eval()
    x = torch.randn(B, T, d_model)

    with torch.no_grad():
        y1 = mha(x)
        assert y1.shape == (B, T, d_model)

        # causal 性质: 扰动最后一个 token, 前面所有位置的输出不变
        x2 = x.clone()
        x2[:, -1, :] += 10.0
        y2 = mha(x2)
    assert torch.allclose(y1[:, :-1], y2[:, :-1], rtol=1e-5, atol=1e-6)
    assert not torch.allclose(y1[:, -1], y2[:, -1], atol=1e-3)


def _make_identity_mha(d_model: int, n_heads: int, causal: bool) -> MultiHeadAttention:
    """把四个投影都设成恒等, 使 MHA 退化为裸 attention, 便于和 F.sdpa 对拍。"""
    mha = MultiHeadAttention(d_model, n_heads, causal=causal)
    with torch.no_grad():
        for proj in (mha.q_proj, mha.k_proj, mha.v_proj, mha.out_proj):
            proj.weight.copy_(torch.eye(d_model))
            proj.bias.zero_()
    return mha.eval()


def test_mha_matches_torch_sdpa() -> None:
    torch.manual_seed(1)
    B, T, d_model = 2, 5, 16
    x = torch.randn(B, T, d_model)

    for n_heads in (1, 4):
        for causal in (False, True):
            mha = _make_identity_mha(d_model, n_heads, causal)
            with torch.no_grad():
                y = mha(x)
            d_head = d_model // n_heads
            xh = x.view(B, T, n_heads, d_head).transpose(1, 2)  # (B, h, T, d_head)
            ref = F.scaled_dot_product_attention(xh, xh, xh, is_causal=causal)
            ref = ref.transpose(1, 2).contiguous().view(B, T, d_model)
            assert torch.allclose(y, ref, rtol=1e-5, atol=1e-6), (n_heads, causal)


def test_gqa_reduces_to_mha_and_broadcasts() -> None:
    torch.manual_seed(2)
    B, n_heads, T, d = 2, 8, 5, 16

    # n_kv_heads == n_heads: 退化为标准 MHA
    q = torch.randn(B, n_heads, T, d)
    k = torch.randn(B, n_heads, T, d)
    v = torch.randn(B, n_heads, T, d)
    out = grouped_query_attention(q, k, v, n_kv_heads=n_heads)
    ref = F.scaled_dot_product_attention(q, k, v)
    assert torch.allclose(out, ref, rtol=1e-5, atol=1e-6)

    # n_kv_heads < n_heads: 与手工把 K/V 头 repeat 后的全头 attention 一致
    n_kv = 2
    k_small = torch.randn(B, n_kv, T, d)
    v_small = torch.randn(B, n_kv, T, d)
    out_gqa = grouped_query_attention(q, k_small, v_small, n_kv_heads=n_kv)
    assert out_gqa.shape == (B, n_heads, T, d)
    k_rep = k_small.repeat_interleave(n_heads // n_kv, dim=1)
    v_rep = v_small.repeat_interleave(n_heads // n_kv, dim=1)
    ref_gqa = F.scaled_dot_product_attention(q, k_rep, v_rep)
    assert torch.allclose(out_gqa, ref_gqa, rtol=1e-5, atol=1e-6)

    # n_kv_heads == 1 即 MQA
    k1 = torch.randn(B, 1, T, d)
    v1 = torch.randn(B, 1, T, d)
    out_mqa = grouped_query_attention(q, k1, v1, n_kv_heads=1)
    ref_mqa = F.scaled_dot_product_attention(q, k1.expand_as(q), v1.expand_as(q))
    assert torch.allclose(out_mqa, ref_mqa, rtol=1e-5, atol=1e-6)


if __name__ == "__main__":
    tests = [
        test_numpy_sdpa_matches_torch_einsum,
        test_numpy_sdpa_edge_cases,
        test_build_causal_mask,
        test_mha_shapes_and_causality,
        test_mha_matches_torch_sdpa,
        test_gqa_reduces_to_mha_and_broadcasts,
    ]
    for t in tests:
        t()
        print(f"{t.__name__} OK")
    print("ALL TESTS PASSED")
