"""Drill 07: Decoder-only Transformer + KV cache 单步 decode.

对应真题
--------
- OpenAI MLE tech screen 原题: 给一个 MiniGPT, debug 并补上 KV cache 实现,
  要求 use_cache=True/False 两条路径生成结果完全一致, 并解释为什么 cache
  能把每步 attention 从 O(T^2) 降到 O(T)。
- Anthropic Software Design Q1: 实现层理解 —— cache 里存什么 (每层的 K/V,
  形状 (B, n_heads, T_past, head_dim)), 单步 decode 时 causal mask 怎么处理
  (新 token 是最后一个位置, 可见全部历史, 所以 T_q=1 时根本不需要 mask)。

冷写清单 (函数签名)
-------------------
1. class MultiHeadAttention(nn.Module):
       __init__(self, d_model, n_heads)
       forward(self, x, past_kv=None) -> (out, (K, V))       # K/V 已含历史
2. class Block(nn.Module):                                    # pre-LN
       forward(self, x, past_kv=None) -> (out, (K, V))
3. class TinyDecoder(nn.Module):
       __init__(self, vocab_size, d_model, n_heads, n_layers, max_len)
       forward(self, ids) -> logits                           # 全量 (B,T,V)
       forward_with_cache(self, ids_step, cache) -> (logits, new_cache)
       generate(self, prompt_ids, n, use_cache=True) -> ids   # greedy

关键点 (面试口述用)
-------------------
- cache 是 list, 每层一个 (K, V) tuple; 单步时把新算的 k/v 在时间维 (dim=2)
  cat 到历史后面, attention 用 T_q=1 的 q 对全部 T_k 个 key 打分。
- 位置编码要用 past_len 做 offset, 否则第 t 个 token 会拿到位置 0 的 embedding。
- causal mask 通用写法: query i 的全局位置是 (T_k - T_q + i), 用
  triu(diagonal=T_k - T_q + 1) 屏蔽未来; T_q == T_k 时退化为标准下三角,
  T_q == 1 时全不屏蔽。

建议 timebox
------------
- MHA (带 past_kv) + Block:   15 min
- TinyDecoder + generate:     15 min
- 自测跑通:                   10 min
- 总计 ~40 min
"""
 
from __future__ import annotations

import math

import torch
import torch.nn as nn
import torch.nn.functional as F

# 每层一个 (K, V), 各自形状 (B, n_heads, T_past, head_dim)
KVCache = list[tuple[torch.Tensor, torch.Tensor]]

# ========================= COLD-WRITE ZONE =========================


class MultiHeadAttention(nn.Module):
    def __init__(self, d_model: int, n_heads: int) -> None:
        super().__init__()
        assert d_model % n_heads == 0
        self.n_heads = n_heads
        self.head_dim = d_model // n_heads
        self.qkv = nn.Linear(d_model, 3 * d_model)
        self.out_proj = nn.Linear(d_model, d_model)

    def forward(
        self,
        x: torch.Tensor,
        past_kv: tuple[torch.Tensor, torch.Tensor] | None = None,
    ) -> tuple[torch.Tensor, tuple[torch.Tensor, torch.Tensor]]:
        """x: (B, T_q, d_model); past_kv: 历史 (K, V), 各 (B, n_heads, T_past, head_dim).

        Returns (out, (K, V)) 其中 K/V 已经拼接了历史, 可直接作为下一步的 past_kv.
        """
        B, T, _ = x.shape
        q, k, v = self.qkv(x).split(self.n_heads * self.head_dim, dim=-1)
        # (B, T, D) -> (B, n_heads, T, head_dim)
        q = q.view(B, T, self.n_heads, self.head_dim).transpose(1, 2)
        k = k.view(B, T, self.n_heads, self.head_dim).transpose(1, 2)
        v = v.view(B, T, self.n_heads, self.head_dim).transpose(1, 2)

        if past_kv is not None:
            past_k, past_v = past_kv
            k = torch.cat([past_k, k], dim=2)  # 时间维在 dim=2
            v = torch.cat([past_v, v], dim=2)

        T_q, T_k = q.size(2), k.size(2)
        scores = q @ k.transpose(-1, -2) / math.sqrt(self.head_dim)
        # 通用 causal mask: query i 的全局位置是 T_k - T_q + i, 屏蔽其右侧。
        # T_q == 1 (单步 decode) 时 diagonal = T_k, mask 全 False -> 可见全部历史。
        causal = torch.triu(
            torch.ones(T_q, T_k, dtype=torch.bool, device=x.device),
            diagonal=T_k - T_q + 1,
        )
        # 每个 query 至少能看到自己, 整行不会全被 mask, 用 -inf 不会产生 NaN
        scores = scores.masked_fill(causal, float("-inf"))
        attn = F.softmax(scores, dim=-1)

        out = attn @ v  # (B, n_heads, T_q, head_dim)
        out = out.transpose(1, 2).reshape(B, T, self.n_heads * self.head_dim)
        return self.out_proj(out), (k, v)


class Block(nn.Module):
    """Pre-LN decoder block: x + attn(ln(x)), 再 x + mlp(ln(x))."""

    def __init__(self, d_model: int, n_heads: int) -> None:
        super().__init__()
        self.ln1 = nn.LayerNorm(d_model)
        self.attn = MultiHeadAttention(d_model, n_heads)
        self.ln2 = nn.LayerNorm(d_model)
        self.mlp = nn.Sequential(
            nn.Linear(d_model, 4 * d_model),
            nn.GELU(),
            nn.Linear(4 * d_model, d_model),
        )

    def forward(
        self,
        x: torch.Tensor,
        past_kv: tuple[torch.Tensor, torch.Tensor] | None = None,
    ) -> tuple[torch.Tensor, tuple[torch.Tensor, torch.Tensor]]:
        attn_out, new_kv = self.attn(self.ln1(x), past_kv)
        x = x + attn_out
        x = x + self.mlp(self.ln2(x))
        return x, new_kv


class TinyDecoder(nn.Module):
    def __init__(
        self,
        vocab_size: int,
        d_model: int,
        n_heads: int,
        n_layers: int,
        max_len: int,
    ) -> None:
        super().__init__()
        self.max_len = max_len
        self.tok_emb = nn.Embedding(vocab_size, d_model)
        self.pos_emb = nn.Embedding(max_len, d_model)
        self.blocks = nn.ModuleList(Block(d_model, n_heads) for _ in range(n_layers))
        self.ln_f = nn.LayerNorm(d_model)
        self.lm_head = nn.Linear(d_model, vocab_size, bias=False)

    def forward(self, ids: torch.Tensor) -> torch.Tensor:
        """全量 forward. ids: (B, T) -> logits: (B, T, vocab_size)."""
        logits, _ = self.forward_with_cache(ids, cache=None)
        return logits

    def forward_with_cache(
        self,
        ids_step: torch.Tensor,
        cache: KVCache | None,
    ) -> tuple[torch.Tensor, KVCache]:
        """ids_step: (B, T_step); cache: 每层的 (K, V) 或 None (等价于空历史).

        Returns (logits, new_cache), logits: (B, T_step, vocab_size).
        """
        B, T = ids_step.shape
        past_len = 0 if cache is None else cache[0][0].size(2)
        assert past_len + T <= self.max_len, "sequence exceeds max_len"

        # 位置编码必须从 past_len 开始 offset
        pos = torch.arange(past_len, past_len + T, device=ids_step.device)
        x = self.tok_emb(ids_step) + self.pos_emb(pos)

        new_cache: KVCache = []
        for i, block in enumerate(self.blocks):
            past_kv = None if cache is None else cache[i]
            x, kv = block(x, past_kv)
            new_cache.append(kv)

        logits = self.lm_head(self.ln_f(x))
        return logits, new_cache

    @torch.no_grad()
    def generate(
        self,
        prompt_ids: torch.Tensor,
        n: int,
        use_cache: bool = True,
    ) -> torch.Tensor:
        """Greedy decoding. prompt_ids: (B, T0) -> (B, T0 + n)."""
        ids = prompt_ids
        if use_cache:
            # prefill: 一次算完 prompt, 之后每步只喂 1 个新 token
            logits, cache = self.forward_with_cache(prompt_ids, cache=None)
            for _ in range(n):
                next_id = logits[:, -1, :].argmax(dim=-1, keepdim=True)  # (B, 1)
                ids = torch.cat([ids, next_id], dim=1)
                logits, cache = self.forward_with_cache(next_id, cache)
        else:
            for _ in range(n):
                logits = self.forward(ids)
                next_id = logits[:, -1, :].argmax(dim=-1, keepdim=True)
                ids = torch.cat([ids, next_id], dim=1)
        return ids


# ========================= TESTS =========================

VOCAB, D_MODEL, N_HEADS, N_LAYERS, MAX_LEN = 53, 32, 4, 2, 64


def make_model(seed: int = 0) -> TinyDecoder:
    torch.manual_seed(seed)
    return TinyDecoder(VOCAB, D_MODEL, N_HEADS, N_LAYERS, MAX_LEN)


def attach_attn_counter(model: TinyDecoder):
    """用 forward hook 统计 attention score 矩阵的总元素数 (~计算量), 不侵入实现."""
    counts = {"score_numel": 0}
    handles = []

    def hook(module, args, output):
        t_q = args[0].size(1)          # 本次 query 长度
        t_k = output[1][0].size(2)     # 拼接历史后的 key 长度
        counts["score_numel"] += module.n_heads * t_q * t_k

    for block in model.blocks:
        handles.append(block.attn.register_forward_hook(hook))
    return counts, handles


def test_attention_matches_sdpa() -> None:
    """无 cache 的 MHA 与 torch 官方 F.scaled_dot_product_attention(is_causal=True) 对拍."""
    torch.manual_seed(1)
    attn = MultiHeadAttention(D_MODEL, N_HEADS)
    x = torch.randn(2, 9, D_MODEL)
    with torch.no_grad():
        out, (k_cat, v_cat) = attn(x, past_kv=None)
        # 参考实现: 用同一套投影权重 + 官方 SDPA
        q, k, v = attn.qkv(x).split(D_MODEL, dim=-1)
        q = q.view(2, 9, N_HEADS, -1).transpose(1, 2)
        k = k.view(2, 9, N_HEADS, -1).transpose(1, 2)
        v = v.view(2, 9, N_HEADS, -1).transpose(1, 2)
        ref = F.scaled_dot_product_attention(q, k, v, is_causal=True)
        ref = attn.out_proj(ref.transpose(1, 2).reshape(2, 9, D_MODEL))
    assert torch.allclose(out, ref, rtol=1e-5, atol=1e-6), (out - ref).abs().max()
    assert torch.equal(k_cat, k) and torch.equal(v_cat, v)


def test_step_logits_match_full_forward() -> None:
    """逐 token 增量 decode 的每一步 logits == 全量 forward 对应位置的 logits."""
    model = make_model()
    torch.manual_seed(2)
    B, T = 2, 7
    ids = torch.randint(0, VOCAB, (B, T))
    with torch.no_grad():
        full_logits = model(ids)  # (B, T, V)
        cache: KVCache | None = None
        for t in range(T):
            step_logits, cache = model.forward_with_cache(ids[:, t : t + 1], cache)
            assert step_logits.shape == (B, 1, VOCAB)
            assert torch.allclose(
                step_logits[:, 0], full_logits[:, t], rtol=1e-4, atol=1e-5
            ), f"step {t}: max diff {(step_logits[:, 0] - full_logits[:, t]).abs().max()}"


def test_prefill_last_logits_match_full_forward() -> None:
    """prefill(prompt) + 单步的 logits 与全量 forward 最后一位 allclose."""
    model = make_model()
    torch.manual_seed(3)
    B, T = 3, 10
    ids = torch.randint(0, VOCAB, (B, T))
    with torch.no_grad():
        full_last = model(ids)[:, -1]
        # prefill 前 T-1 个, 再单步喂最后 1 个
        _, cache = model.forward_with_cache(ids[:, :-1], cache=None)
        step_logits, _ = model.forward_with_cache(ids[:, -1:], cache)
    assert torch.allclose(step_logits[:, 0], full_last, rtol=1e-4, atol=1e-5)


def test_cache_shapes_grow() -> None:
    """cache 形状: 每层 (K, V) 都是 (B, n_heads, past_len, head_dim), 随步数 +1."""
    model = make_model()
    torch.manual_seed(4)
    B, T0, n_steps = 2, 5, 6
    ids = torch.randint(0, VOCAB, (B, T0))
    head_dim = D_MODEL // N_HEADS
    with torch.no_grad():
        _, cache = model.forward_with_cache(ids, cache=None)
        assert len(cache) == N_LAYERS
        for step in range(n_steps):
            expected_len = T0 + step
            for k, v in cache:
                assert k.shape == (B, N_HEADS, expected_len, head_dim), k.shape
                assert v.shape == (B, N_HEADS, expected_len, head_dim), v.shape
            nxt = torch.randint(0, VOCAB, (B, 1))
            _, cache = model.forward_with_cache(nxt, cache)


def test_generate_cache_vs_no_cache() -> None:
    """固定权重下 greedy 生成: use_cache=True/False 序列完全一致."""
    model = make_model()
    torch.manual_seed(5)
    prompt = torch.randint(0, VOCAB, (2, 6))
    out_cache = model.generate(prompt, n=20, use_cache=True)
    out_full = model.generate(prompt, n=20, use_cache=False)
    assert out_cache.shape == (2, 6 + 20)
    assert torch.equal(out_cache, out_full), (out_cache, out_full)
    assert torch.equal(out_cache[:, :6], prompt)  # prompt 不被改写
    # 换一个 seed 的权重再来一遍, 排除偶然
    model2 = make_model(seed=42)
    assert torch.equal(
        model2.generate(prompt, n=15, use_cache=True),
        model2.generate(prompt, n=15, use_cache=False),
    )


def test_cache_reduces_attention_compute() -> None:
    """计数器 hook: cache 路径的 attention score 总元素数显著更小."""
    model = make_model()
    torch.manual_seed(6)
    prompt = torch.randint(0, VOCAB, (1, 8))
    n = 16

    counts, handles = attach_attn_counter(model)
    model.generate(prompt, n=n, use_cache=True)
    cached = counts["score_numel"]
    counts["score_numel"] = 0
    model.generate(prompt, n=n, use_cache=False)
    full = counts["score_numel"]
    for h in handles:
        h.remove()

    # 理论值 (每层每头): cache = prefill 8^2 + 16 次单步 sum_{T_k=9..24} T_k = 328
    #   (生成第 n 个 token 后还会多算一次下一步 logits, 所以 T_k 到 24)
    #                     full  = sum_{L=8..23} L^2 = 4184
    assert cached == N_LAYERS * N_HEADS * (8 * 8 + sum(range(9, 25))), cached
    assert full == N_LAYERS * N_HEADS * sum(L * L for L in range(8, 24)), full
    assert cached * 5 < full, (cached, full)


def test_edge_cases() -> None:
    model = make_model()
    # 单 token 全量 forward: T=1 时 mask 只留自己, 不应出 NaN/Inf
    one = torch.tensor([[3]])
    with torch.no_grad():
        logits = model(one)
    assert logits.shape == (1, 1, VOCAB)
    assert torch.isfinite(logits).all()

    # n=0: 两条路径都原样返回 prompt
    torch.manual_seed(7)
    prompt = torch.randint(0, VOCAB, (2, 4))
    assert torch.equal(model.generate(prompt, n=0, use_cache=True), prompt)
    assert torch.equal(model.generate(prompt, n=0, use_cache=False), prompt)

    # 长度为 1 的 prompt 也能双路径一致生成
    p1 = torch.tensor([[7], [11]])
    assert torch.equal(
        model.generate(p1, n=10, use_cache=True),
        model.generate(p1, n=10, use_cache=False),
    )

    # 超过 max_len 必须报错而不是静默出错 (pos_emb 会越界)
    try:
        model.generate(torch.randint(0, VOCAB, (1, MAX_LEN)), n=1, use_cache=True)
        raise RuntimeError("should have raised")
    except AssertionError:
        pass


if __name__ == "__main__":
    tests = [
        test_attention_matches_sdpa,
        test_step_logits_match_full_forward,
        test_prefill_last_logits_match_full_forward,
        test_cache_shapes_grow,
        test_generate_cache_vs_no_cache,
        test_cache_reduces_attention_compute,
        test_edge_cases,
    ]
    for t in tests:
        t()
        print(f"[ok] {t.__name__}")
    print("ALL TESTS PASSED")
