"""
冷写训练 02: 数值稳定 softmax + streaming entropy (online softmax)

对应真题:
    OpenAI Research Scientist / MLE coding 轮真题族 (2025-2026 高频原题):
    - "实现一个数值稳定的 softmax / log-softmax" (热身, 几乎必考)
    - "logits 太大无法一次装入内存, 分块流式计算整个分布的熵"
      —— 即 online softmax, 也是 FlashAttention 的核心原语,
      Anthropic / GDM 的 systems-flavored ML 轮也考过同款 merge 函数。

冷写清单 (建议 timebox: 30 分钟, 其中 streaming 部分 15 分钟):
    1. stable_softmax(x: np.ndarray, axis: int = -1) -> np.ndarray
    2. logsumexp(x: np.ndarray, axis: int = -1, keepdims: bool = False) -> np.ndarray
    3. log_softmax(x: np.ndarray, axis: int = -1) -> np.ndarray
    4. entropy_from_logits(logits: np.ndarray, axis: int = -1) -> np.ndarray
    5. online_softmax_merge(state1: tuple[float, float],
                            state2: tuple[float, float]) -> tuple[float, float]
       # state = (m, s) = (块内 max, sum(exp(x - m))), 满足结合律, 单位元 (-inf, 0)
    6. streaming_entropy(chunks: Iterable[np.ndarray]) -> float
       # 一维 logits 被任意切块, 单遍流式合并 (m, s, t), t = sum(exp(x - m) * x)
       # 最终 H = m + log(s) - t / s, 与整体计算 bit 级一致

核心公式 (面试时先在纸上写出来再动手):
    L = logsumexp(z) = m + log(sum(exp(z_i - m))),  m = max(z)
    log p_i = z_i - L
    H = -sum(p_i * log p_i) = L - E_p[z] = m + log(s) - t/s
"""

from __future__ import annotations

import math
from typing import Iterable

import numpy as np

# ========================= COLD-WRITE ZONE =========================


def stable_softmax(x: np.ndarray, axis: int = -1) -> np.ndarray:
    x = np.asarray(x, dtype=np.float64)
    # max-shift: exp(x - m) <= 1, 杜绝 overflow; 减常数不改变 softmax 结果
    m = np.max(x, axis=axis, keepdims=True)
    e = np.exp(x - m)
    return e / np.sum(e, axis=axis, keepdims=True)


def logsumexp(x: np.ndarray, axis: int = -1, keepdims: bool = False) -> np.ndarray:
    x = np.asarray(x, dtype=np.float64)
    m = np.max(x, axis=axis, keepdims=True)
    out = m + np.log(np.sum(np.exp(x - m), axis=axis, keepdims=True))
    if not keepdims:
        out = np.squeeze(out, axis=axis)
    return out


def log_softmax(x: np.ndarray, axis: int = -1) -> np.ndarray:
    x = np.asarray(x, dtype=np.float64)
    return x - logsumexp(x, axis=axis, keepdims=True)


def entropy_from_logits(logits: np.ndarray, axis: int = -1) -> np.ndarray:
    logp = log_softmax(logits, axis=axis)
    # 用 exp(logp) * logp 而不是 p * log(p): p==0 时 exp(-大数)*(-大数) = 0, 无 log(0)
    return -np.sum(np.exp(logp) * logp, axis=axis)


def online_softmax_merge(
    state1: tuple[float, float], state2: tuple[float, float]
) -> tuple[float, float]:
    """合并两块的 (m, s) 状态; (m, s) 表示 logsumexp = m + log(s)。"""
    m1, s1 = state1
    m2, s2 = state2
    # 单位元 (-inf, 0): 直接返回另一侧, 避免 exp(-inf - (-inf)) = nan
    if s1 == 0.0:
        return state2
    if s2 == 0.0:
        return state1
    m = max(m1, m2)
    # 把两块的 sum(exp) 重新缩放到共同的新 max 下
    s = s1 * math.exp(m1 - m) + s2 * math.exp(m2 - m)
    return (m, s)


def streaming_entropy(chunks: Iterable[np.ndarray]) -> float:
    """对被任意切块的一维 logits 单遍计算熵, 每块内存 O(chunk)。"""
    m, s, t = -math.inf, 0.0, 0.0  # 单位元
    for chunk in chunks:
        c = np.asarray(chunk, dtype=np.float64).ravel()
        if c.size == 0:
            continue
        cm = float(np.max(c))
        e = np.exp(c - cm)
        cs = float(np.sum(e))
        ct = float(np.sum(e * c))
        # 与 online_softmax_merge 相同的合并规则, 多带一个一阶矩 t
        new_m = max(m, cm)
        scale_old = math.exp(m - new_m) if s > 0.0 else 0.0
        scale_new = math.exp(cm - new_m)
        s = s * scale_old + cs * scale_new
        t = t * scale_old + ct * scale_new
        m = new_m
    if s == 0.0:
        raise ValueError("streaming_entropy: no logits seen (all chunks empty)")
    # H = logsumexp(z) - E_p[z] = (m + log s) - t/s
    return m + math.log(s) - t / s


# ========================= TESTS =========================

import torch


def test_stable_softmax_matches_torch() -> None:
    rng = np.random.default_rng(0)
    for shape, axis in [((7,), -1), ((3, 5), -1), ((3, 5), 0), ((2, 3, 4), 1)]:
        x = rng.normal(size=shape) * 5.0
        ours = stable_softmax(x, axis=axis)
        ref = torch.softmax(torch.from_numpy(x), dim=axis).numpy()
        assert np.allclose(ours, ref, rtol=1e-12, atol=1e-14)
        assert np.allclose(ours.sum(axis=axis), 1.0, rtol=1e-12, atol=1e-14)


def test_log_softmax_matches_torch() -> None:
    rng = np.random.default_rng(1)
    for shape, axis in [((11,), -1), ((4, 6), -1), ((4, 6), 0)]:
        x = rng.normal(size=shape) * 8.0
        ours = log_softmax(x, axis=axis)
        ref = torch.log_softmax(torch.from_numpy(x), dim=axis).numpy()
        assert np.allclose(ours, ref, rtol=1e-12, atol=1e-14)
    lse_ref = torch.logsumexp(torch.from_numpy(x), dim=-1).numpy()
    assert np.allclose(logsumexp(x, axis=-1), lse_ref, rtol=1e-12, atol=1e-14)


def test_extreme_logits_no_overflow() -> None:
    # naive exp(1e4) 会 overflow 成 inf; max-shift 后必须全 finite
    x = np.array([1e4, 0.0, -1e4, 1e4 - 1.0])
    p = stable_softmax(x)
    assert np.all(np.isfinite(p))
    assert abs(p.sum() - 1.0) < 1e-12
    # 解析解: 只有 1e4 和 1e4-1 存活, 比例 1 : e^{-1}
    z = 1.0 + math.exp(-1.0)
    assert np.allclose(p, [1.0 / z, 0.0, 0.0, math.exp(-1.0) / z], rtol=1e-12, atol=1e-300)
    assert np.all(np.isfinite(log_softmax(x)))
    assert np.isfinite(entropy_from_logits(x))
    # 二点分布解析熵
    p0, p1 = 1.0 / z, math.exp(-1.0) / z
    h_expected = -(p0 * math.log(p0) + p1 * math.log(p1))
    assert abs(float(entropy_from_logits(x)) - h_expected) < 1e-12


def test_all_equal_logits_uniform() -> None:
    # 全相同 logits (包括极大/极小常数) -> 均匀分布, H = log(n)
    for c in [0.0, 1e4, -1e4]:
        x = np.full(10, c)
        assert np.allclose(stable_softmax(x), 0.1, rtol=1e-12, atol=1e-14)
        assert abs(float(entropy_from_logits(x)) - math.log(10)) < 1e-12
        assert abs(streaming_entropy(np.split(x, [3, 7])) - math.log(10)) < 1e-12


def test_entropy_matches_torch_categorical() -> None:
    rng = np.random.default_rng(2)
    logits = rng.normal(size=(5, 9)) * 3.0
    logits[0] = np.array([50.0, 0.0, -50.0, 1.0, 2.0, -3.0, 0.5, 49.0, -49.0])
    ours = entropy_from_logits(logits, axis=-1)
    ref = torch.distributions.Categorical(logits=torch.from_numpy(logits)).entropy().numpy()
    assert ours.shape == (5,)
    assert np.allclose(ours, ref, rtol=1e-10, atol=1e-12)
    # axis=0 与转置后 axis=-1 一致
    assert np.allclose(entropy_from_logits(logits, axis=0), entropy_from_logits(logits.T), rtol=1e-12, atol=1e-14)


def test_streaming_entropy_any_chunking() -> None:
    rng = np.random.default_rng(3)
    x = rng.normal(size=257) * 10.0
    full = float(entropy_from_logits(x))
    # 若干随机切法
    for seed in range(6):
        r = np.random.default_rng(seed)
        n_cuts = int(r.integers(1, 9))
        cuts = np.sort(r.choice(np.arange(1, x.size), size=n_cuts, replace=False))
        assert abs(streaming_entropy(np.split(x, cuts)) - full) < 1e-12
    # 极端切法: 整块 / 逐元素 / 夹带空块
    assert abs(streaming_entropy([x]) - full) < 1e-12
    assert abs(streaming_entropy([x[i : i + 1] for i in range(x.size)]) - full) < 1e-11
    assert abs(streaming_entropy([x[:100], np.array([]), x[100:]]) - full) < 1e-12


def test_streaming_entropy_extreme_logits_across_chunks() -> None:
    rng = np.random.default_rng(4)
    x = rng.normal(size=64)
    x[3], x[40], x[41], x[60] = 1e4, -1e4, 1e4 - 0.5, 1e4 - 2.0  # 极值分散在不同块
    full = float(entropy_from_logits(x))
    assert math.isfinite(full)
    for cuts in [[10, 32, 50], [4, 39, 42, 61], [1]]:
        h = streaming_entropy(np.split(x, cuts))
        assert math.isfinite(h)
        assert abs(h - full) < 1e-12


def test_streaming_entropy_empty_input_raises() -> None:
    try:
        streaming_entropy([np.array([]), np.array([])])
    except ValueError:
        pass
    else:
        raise AssertionError("expected ValueError on all-empty chunks")


def test_online_softmax_merge() -> None:
    rng = np.random.default_rng(5)
    x = rng.normal(size=64) * 100.0  # 大尺度, naive 合并会 overflow

    def state(v: np.ndarray) -> tuple[float, float]:
        m = float(np.max(v))
        return (m, float(np.sum(np.exp(v - m))))

    def lse(st: tuple[float, float]) -> float:
        return st[0] + math.log(st[1])

    # 两块合并 == 整体
    merged = online_softmax_merge(state(x[:20]), state(x[20:]))
    assert abs(lse(merged) - lse(state(x))) < 1e-12
    # 与 torch.logsumexp 对拍
    assert abs(lse(merged) - float(torch.logsumexp(torch.from_numpy(x), dim=0))) < 1e-12
    # 结合律 (顺序无关)
    a, b, c = state(x[:10]), state(x[10:40]), state(x[40:])
    l1 = lse(online_softmax_merge(online_softmax_merge(a, b), c))
    l2 = lse(online_softmax_merge(a, online_softmax_merge(b, c)))
    l3 = lse(online_softmax_merge(online_softmax_merge(c, a), b))
    assert abs(l1 - l2) < 1e-12 and abs(l1 - l3) < 1e-12
    # 单位元 (-inf, 0)
    ident = (-math.inf, 0.0)
    assert online_softmax_merge(ident, a) == a
    assert online_softmax_merge(a, ident) == a
    # 极值状态合并不产生 nan/inf
    m_big = online_softmax_merge((1e4, 2.0), (-1e4, 3.0))
    assert m_big[0] == 1e4 and math.isfinite(m_big[1]) and abs(m_big[1] - 2.0) < 1e-12


if __name__ == "__main__":
    tests = [
        test_stable_softmax_matches_torch,
        test_log_softmax_matches_torch,
        test_extreme_logits_no_overflow,
        test_all_equal_logits_uniform,
        test_entropy_matches_torch_categorical,
        test_streaming_entropy_any_chunking,
        test_streaming_entropy_extreme_logits_across_chunks,
        test_streaming_entropy_empty_input_raises,
        test_online_softmax_merge,
    ]
    for t in tests:
        t()
        print(f"[PASS] {t.__name__}")
    print("ALL TESTS PASSED")
