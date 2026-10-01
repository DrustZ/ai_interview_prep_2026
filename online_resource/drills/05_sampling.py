"""Drill 05 — LLM sampling: temperature / top-k / top-p / greedy decode.

对应真题:
  - GDM ML coding 轮: top-k / top-p (nucleus) sampling 是点名考点, 常要求现场
    手写 filter + 采样 pipeline, 并解释 top-p 的 off-by-one 边界.
  - deep-ml #419: 组合 sampling pipeline (temperature -> top-k -> top-p -> multinomial).
  - Anthropic/OpenAI coding 轮也常以 "实现一个 decode loop" 作为热身题.

冷写函数签名清单:
  1. apply_temperature(logits: Tensor, T: float) -> Tensor
       T < EPS 时走 argmax one-hot 路径 (argmax 处 0, 其余 -inf).
  2. top_k_filter(logits: Tensor, k: int) -> Tensor
       仅保留每行最大的 k 个 logit, 其余置 -inf; k <= 0 或 k >= vocab 时不过滤.
  3. top_p_filter(logits: Tensor, p: float) -> Tensor
       降序累积概率, 保留累积和达到 p 的最小集合 (含首个越界 token), 其余 -inf.
  4. sample_pipeline(logits: Tensor, T: float, k: int, p: float,
                     generator: torch.Generator | None) -> Tensor
       温度 -> top-k -> top-p -> softmax -> multinomial, 返回 token id.
  5. greedy_decode(model_fn, prompt_ids: Tensor, max_new_tokens: int,
                   stop_id: int | None) -> Tensor
       自回归 argmax 循环, 生成 stop_id 后 (含该 token) 提前终止.

约定: 所有 filter 都作用在最后一维 (vocab 维), 支持 (V,) 和 (B, V).

建议 timebox: 25 分钟 (filter 三件套 12min + pipeline 5min + greedy 8min).
"""

from typing import Callable, Optional

import torch

# ========================= COLD-WRITE ZONE =========================

EPS = 1e-6
NEG_INF = float("-inf")


def apply_temperature(logits: torch.Tensor, T: float) -> torch.Tensor:
    """Scale logits by 1/T; T -> 0 collapses to a deterministic argmax distribution."""
    if T < EPS:
        # one-hot path: softmax of this is exactly one-hot at the argmax
        out = torch.full_like(logits, NEG_INF)
        idx = logits.argmax(dim=-1, keepdim=True)
        return out.scatter(-1, idx, 0.0)
    return logits / T


def top_k_filter(logits: torch.Tensor, k: int) -> torch.Tensor:
    """Keep the k largest logits per row, set the rest to -inf.

    k <= 0 or k >= vocab_size disables filtering. Ties at the k-th value are
    all kept (threshold semantics, same as HuggingFace).
    """
    vocab_size = logits.size(-1)
    if k <= 0 or k >= vocab_size:
        return logits.clone()
    kth_value = torch.topk(logits, k, dim=-1).values[..., -1, None]
    return logits.masked_fill(logits < kth_value, NEG_INF)


def top_p_filter(logits: torch.Tensor, p: float) -> torch.Tensor:
    """Nucleus filtering: keep the smallest prefix (in prob-descending order)
    whose cumulative probability reaches p; set the rest to -inf.

    p >= 1 disables filtering. The top-1 token is always kept.
    """
    if p >= 1.0:
        return logits.clone()
    sorted_logits, sorted_idx = torch.sort(logits, dim=-1, descending=True)
    cumprobs = torch.softmax(sorted_logits, dim=-1).cumsum(dim=-1)
    # remove token i iff the cumulative mass STRICTLY BEFORE i already >= p,
    # i.e. shift the ">= p" mask right by one so the first token that crosses
    # the boundary is still kept (classic off-by-one handling).
    sorted_remove = cumprobs >= p
    sorted_remove[..., 1:] = sorted_remove[..., :-1].clone()
    sorted_remove[..., 0] = False  # always keep the most likely token
    # scatter the mask back from sorted order to original vocab order
    remove = torch.zeros_like(sorted_remove).scatter(-1, sorted_idx, sorted_remove)
    return logits.masked_fill(remove, NEG_INF)


def sample_pipeline(
    logits: torch.Tensor,
    T: float,
    k: int,
    p: float,
    generator: Optional[torch.Generator] = None,
) -> torch.Tensor:
    """temperature -> top-k -> top-p -> softmax -> multinomial.

    Returns sampled token ids with shape logits.shape[:-1]
    (0-dim tensor for (V,) input, (B,) for (B, V) input).
    """
    logits = apply_temperature(logits, T)
    logits = top_k_filter(logits, k)
    logits = top_p_filter(logits, p)
    probs = torch.softmax(logits, dim=-1)
    return torch.multinomial(probs, num_samples=1, generator=generator).squeeze(-1)


def greedy_decode(
    model_fn: Callable[[torch.Tensor], torch.Tensor],
    prompt_ids: torch.Tensor,
    max_new_tokens: int,
    stop_id: Optional[int] = None,
) -> torch.Tensor:
    """Autoregressive argmax decoding.

    model_fn: takes the full 1-D id sequence so far, returns next-token logits (V,).
    Returns prompt + generated ids; if stop_id is generated it is included and
    decoding stops early.
    """
    ids = prompt_ids.clone()
    for _ in range(max_new_tokens):
        logits = model_fn(ids)
        next_id = logits.argmax(dim=-1, keepdim=True)
        ids = torch.cat([ids, next_id], dim=-1)
        if stop_id is not None and next_id.item() == stop_id:
            break
    return ids


# ========================= TESTS =========================


def _finite_mask(t: torch.Tensor) -> torch.Tensor:
    return t > NEG_INF


def test_apply_temperature() -> None:
    logits = torch.tensor([1.0, 2.0, 3.0, -1.0])
    # T=1 is identity
    assert torch.allclose(apply_temperature(logits, 1.0), logits)
    # matches torch reference: softmax(logits / T)
    for T in (0.5, 2.0, 10.0):
        ours = torch.softmax(apply_temperature(logits, T), dim=-1)
        ref = torch.softmax(logits / T, dim=-1)
        assert torch.allclose(ours, ref, rtol=1e-5, atol=1e-7)
    # T -> 0: one-hot at argmax
    out = apply_temperature(logits, 0.0)
    assert out[2].item() == 0.0
    assert torch.isinf(out[[0, 1, 3]]).all()
    assert torch.allclose(
        torch.softmax(out, dim=-1), torch.tensor([0.0, 0.0, 1.0, 0.0])
    )
    # batch input + all-equal logits (argmax picks index 0)
    batch = torch.zeros(2, 4)
    out_b = apply_temperature(batch, 1e-9)
    assert torch.allclose(
        torch.softmax(out_b, dim=-1),
        torch.tensor([[1.0, 0.0, 0.0, 0.0]] * 2),
    )


def test_top_k_filter() -> None:
    logits = torch.tensor([1.0, 5.0, 3.0, 2.0])
    out = top_k_filter(logits, 2)
    assert torch.equal(out, torch.tensor([NEG_INF, 5.0, 3.0, NEG_INF]))
    # kept entries renormalize to the same relative probs as torch's topk
    probs = torch.softmax(out, dim=-1)
    ref = torch.softmax(torch.tensor([5.0, 3.0]), dim=-1)
    assert torch.allclose(probs[[1, 2]], ref, rtol=1e-5, atol=1e-7)
    assert probs[[0, 3]].sum().item() == 0.0
    # k >= vocab and k <= 0 are no-ops
    assert torch.equal(top_k_filter(logits, 4), logits)
    assert torch.equal(top_k_filter(logits, 100), logits)
    assert torch.equal(top_k_filter(logits, 0), logits)
    # all-equal values: threshold semantics keeps everything (ties at k-th value)
    flat = torch.ones(5)
    assert _finite_mask(top_k_filter(flat, 2)).all()
    # batch: each row filtered independently
    b = torch.tensor([[1.0, 5.0, 3.0, 2.0], [9.0, 0.0, 8.0, 7.0]])
    out_b = top_k_filter(b, 2)
    assert torch.equal(_finite_mask(out_b), torch.tensor(
        [[False, True, True, False], [True, False, True, False]]
    ))
    # huge logits: no NaN/overflow because we only threshold, never exponentiate
    big = torch.tensor([1e10, 1e10 - 1, 0.0])
    assert torch.equal(_finite_mask(top_k_filter(big, 2)),
                       torch.tensor([True, True, False]))


def test_top_p_filter() -> None:
    # hand-computed case from the drill spec:
    # probs = [0.5, 0.3, 0.15, 0.05], cum = [0.5, 0.8, 0.95, 1.0]
    # p = 0.8 -> smallest prefix reaching 0.8 is the first TWO tokens
    probs = torch.tensor([0.5, 0.3, 0.15, 0.05])
    logits = probs.log()
    out = top_p_filter(logits, 0.8)
    assert torch.equal(_finite_mask(out), torch.tensor([True, True, False, False]))
    # off-by-one: p=0.6 -> {0.5} alone is NOT enough (0.5 < 0.6), so the token
    # that first crosses the boundary (0.3) must be INCLUDED -> keep 2 tokens
    out = top_p_filter(logits, 0.6)
    assert torch.equal(_finite_mask(out), torch.tensor([True, True, False, False]))
    # kept tokens renormalize correctly
    renorm = torch.softmax(out, dim=-1)
    assert torch.allclose(renorm[:2], torch.tensor([0.5 / 0.8, 0.3 / 0.8]),
                          rtol=1e-5, atol=1e-6)
    # p=0.9 -> need three tokens (0.5+0.3=0.8 < 0.9)
    out = top_p_filter(logits, 0.9)
    assert torch.equal(_finite_mask(out), torch.tensor([True, True, True, False]))
    # tiny p -> always keep at least the top-1 token
    out = top_p_filter(logits, 1e-9)
    assert torch.equal(_finite_mask(out), torch.tensor([True, False, False, False]))
    # p >= 1 is a no-op
    assert torch.equal(top_p_filter(logits, 1.0), logits)
    # unsorted input: mask must be scattered back to original positions
    perm = torch.tensor([2, 0, 3, 1])
    out = top_p_filter(logits[perm], 0.8)
    assert torch.equal(_finite_mask(out), torch.tensor([False, True, False, True]))
    # all-equal logits: uniform probs, p=0.5 over 4 tokens keeps ceil-crossing set
    # cum = [0.25, 0.5, 0.75, 1.0] -> smallest prefix reaching 0.5 is 2 tokens
    out = top_p_filter(torch.zeros(4), 0.5)
    assert int(_finite_mask(out).sum()) == 2
    # batch input
    b = torch.stack([logits, logits[perm]])
    out_b = top_p_filter(b, 0.8)
    assert torch.equal(_finite_mask(out_b), torch.tensor(
        [[True, True, False, False], [False, True, False, True]]
    ))
    # extreme logits: softmax inside must not produce NaN
    big = torch.tensor([1000.0, 999.0, 0.0])
    out = top_p_filter(big, 0.5)
    assert not torch.isnan(out[_finite_mask(out)]).any()
    assert _finite_mask(out)[0].item()  # dominant token kept


def test_sample_pipeline() -> None:
    logits = torch.tensor([1.0, 3.0, 2.0, 0.5])
    # tiny T -> deterministic argmax, regardless of generator
    for _ in range(5):
        tok = sample_pipeline(logits, T=1e-9, k=0, p=1.0)
        assert tok.item() == 1
    # seeded generator -> reproducible
    g1 = torch.Generator().manual_seed(42)
    g2 = torch.Generator().manual_seed(42)
    seq1 = [sample_pipeline(logits, 1.0, 0, 1.0, g1).item() for _ in range(20)]
    seq2 = [sample_pipeline(logits, 1.0, 0, 1.0, g2).item() for _ in range(20)]
    assert seq1 == seq2
    # k=1 -> always the argmax even at high temperature
    g = torch.Generator().manual_seed(0)
    for _ in range(10):
        assert sample_pipeline(logits, T=5.0, k=1, p=1.0, generator=g).item() == 1
    # top-p restricts support: with p=0.8 only tokens {0, 1} can ever appear
    probs = torch.tensor([0.5, 0.3, 0.15, 0.05])
    g = torch.Generator().manual_seed(0)
    samples = [sample_pipeline(probs.log(), 1.0, 0, 0.8, g).item() for _ in range(200)]
    assert set(samples) <= {0, 1}
    # statistical check vs analytic distribution: p(0)=0.7, p(1)=0.3
    g = torch.Generator().manual_seed(123)
    two = torch.tensor([0.7, 0.3]).log()
    n = 5000
    hits = sum(sample_pipeline(two, 1.0, 0, 1.0, g).item() == 0 for _ in range(n))
    assert abs(hits / n - 0.7) < 0.03  # ~4.6 sigma of binomial std 0.0065
    # batch input returns one token per row
    b = torch.tensor([[100.0, 0.0], [0.0, 100.0]])
    toks = sample_pipeline(b, 1.0, 0, 1.0, torch.Generator().manual_seed(0))
    assert toks.tolist() == [0, 1]


def test_greedy_decode() -> None:
    vocab_size = 5

    def toy_model(ids: torch.Tensor) -> torch.Tensor:
        # deterministic: next token = (last token + 1) % vocab_size
        logits = torch.zeros(vocab_size)
        logits[(ids[-1].item() + 1) % vocab_size] = 10.0
        return logits

    out = greedy_decode(toy_model, torch.tensor([0]), max_new_tokens=4, stop_id=None)
    assert out.tolist() == [0, 1, 2, 3, 4]
    # stop_id triggers early termination (stop token included)
    out = greedy_decode(toy_model, torch.tensor([0]), max_new_tokens=10, stop_id=3)
    assert out.tolist() == [0, 1, 2, 3]
    # stop_id never generated -> full length
    out = greedy_decode(toy_model, torch.tensor([2]), max_new_tokens=3, stop_id=99)
    assert out.tolist() == [2, 3, 4, 0]
    # max_new_tokens=0 -> prompt unchanged
    out = greedy_decode(toy_model, torch.tensor([1, 2]), max_new_tokens=0, stop_id=None)
    assert out.tolist() == [1, 2]
    # prompt must not be mutated
    prompt = torch.tensor([0])
    greedy_decode(toy_model, prompt, max_new_tokens=2, stop_id=None)
    assert prompt.tolist() == [0]


if __name__ == "__main__":
    for test in (
        test_apply_temperature,
        test_top_k_filter,
        test_top_p_filter,
        test_sample_pipeline,
        test_greedy_decode,
    ):
        test()
        print(f"{test.__name__} passed")
    print("ALL TESTS PASSED")
