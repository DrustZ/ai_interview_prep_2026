"""Drill 08: MiniGPT bug hunt ("变形金刚捉虫").

对应真题
--------
- OpenAI ML coding 轮高频题 (12+ 面经帖): 给你一份 ~400 行的 PyTorch GPT
  训练脚本, 脚本能跑但 loss 不降/降得异常, 要求在 60 分钟内找出并修复
  其中 4 个 bug (通常分布在: embedding、attention mask、训练循环、输出头)。
- 本文件把它压缩成 ~160 行的 char-level MiniGPT, 埋了同族的 4 个 bug。

练法
----
1. 只读 COLD-WRITE ZONE (不要往下翻 TESTS, 有剧透)。
2. 跑 `python 08_bughunt_minigpt.py --buggy` 看 200 步 loss 曲线, 从症状
   反推 bug 位置; 找齐 4 个后对照 08_bughunt_answers.md。
3. 第二遍练: 合上答案, 冷写出下列正确版本 (即 TESTS 区的 Fixed* 参考实现):

冷写清单 (函数签名)
-------------------
1. class CausalSelfAttention(nn.Module):
       __init__(self, n_embd, n_head, block_size)
       forward(self, x) -> torch.Tensor                 # (B, T, C) -> (B, T, C)
2. class MiniGPT(nn.Module):
       forward(self, idx, targets=None) -> tuple[logits, loss | None]
3. get_batch(data, batch_size, block_size, generator) -> (x, y)
4. train(steps, lr, log_every) -> list[float]           # 完整训练循环

运行方式
--------
- python 08_bughunt_minigpt.py            # 跑全部测试 (会各训练 200 步, 剧透)
- python 08_bughunt_minigpt.py --buggy    # 只跑埋 bug 版训练
- python 08_bughunt_minigpt.py --fixed    # 只跑修复版训练

建议 timebox
------------
- 找齐 4 个 bug 并口述修复: 25 min (真题是 60 min / 400 行)
- 冷写修复版 attention + forward + train loop: 20 min
"""

from __future__ import annotations

import argparse
import math

import torch
import torch.nn as nn
import torch.nn.functional as F

# ========================= COLD-WRITE ZONE =========================
# 下面这份脚本能跑通, 但 loss 不降。里面埋了 4 个 bug, 找出它们。

TEXT = (
    "the quick brown fox jumps over the lazy dog. "
    "pack my box with five dozen liquor jugs. "
    "how vexingly quick daft zebras jump! "
    "sphinx of black quartz, judge my vow. "
    "agent 007 beat models 1, 2, 3, 4, 5, 6, 8 and 9 today. "
) * 8

CHARS = sorted(set(TEXT))
VOCAB_SIZE = len(CHARS)
STOI = {ch: i for i, ch in enumerate(CHARS)}
DATA = torch.tensor([STOI[ch] for ch in TEXT], dtype=torch.long)

BLOCK_SIZE = 32
BATCH_SIZE = 16
N_EMBD = 40
N_HEAD = 4
N_LAYER = 2
LR = 3e-3
STEPS = 200


class CausalSelfAttention(nn.Module):
    def __init__(self, n_embd: int, n_head: int, block_size: int) -> None:
        super().__init__()
        assert n_embd % n_head == 0
        self.n_head = n_head
        self.head_dim = n_embd // n_head
        self.qkv = nn.Linear(n_embd, 3 * n_embd)
        self.proj = nn.Linear(n_embd, n_embd)
        self.register_buffer("mask", torch.tril(torch.ones(block_size, block_size)))

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        B, T, C = x.shape
        q, k, v = self.qkv(x).chunk(3, dim=-1)
        q = q.view(B, T, self.n_head, self.head_dim).transpose(1, 2)
        k = k.view(B, T, self.n_head, self.head_dim).transpose(1, 2)
        v = v.view(B, T, self.n_head, self.head_dim).transpose(1, 2)
        att = (q @ k.transpose(-2, -1)) / math.sqrt(self.head_dim)
        att = att * self.mask[:T, :T]
        att = F.softmax(att, dim=-1)
        y = att @ v
        y = y.transpose(1, 2).contiguous().view(B, T, C)
        return self.proj(y)


class Block(nn.Module):
    def __init__(self, n_embd: int, n_head: int, block_size: int) -> None:
        super().__init__()
        self.ln1 = nn.LayerNorm(n_embd)
        self.attn = CausalSelfAttention(n_embd, n_head, block_size)
        self.ln2 = nn.LayerNorm(n_embd)
        self.mlp = nn.Sequential(
            nn.Linear(n_embd, 4 * n_embd),
            nn.GELU(),
            nn.Linear(4 * n_embd, n_embd),
        )

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        x = x + self.attn(self.ln1(x))
        x = x + self.mlp(self.ln2(x))
        return x


class MiniGPT(nn.Module):
    def __init__(self) -> None:
        super().__init__()
        self.wte = nn.Embedding(VOCAB_SIZE, N_EMBD)
        self.wpe = nn.Embedding(BLOCK_SIZE, N_EMBD)
        self.blocks = nn.ModuleList(
            [Block(N_EMBD, N_HEAD, BLOCK_SIZE) for _ in range(N_LAYER)]
        )
        self.ln_f = nn.LayerNorm(N_EMBD)
        nn.init.normal_(self.wte.weight, std=0.02)
        nn.init.normal_(self.wpe.weight, std=0.02)

    def forward(
        self, idx: torch.Tensor, targets: torch.Tensor | None = None
    ) -> tuple[torch.Tensor, torch.Tensor | None]:
        B, T = idx.shape
        x = self.wte(idx)
        for block in self.blocks:
            x = block(x)
        x = self.ln_f(x)
        logits = x @ self.wte.weight
        loss = None
        if targets is not None:
            loss = F.cross_entropy(logits.view(-1, logits.size(-1)), targets.view(-1))
        return logits, loss


def get_batch(
    data: torch.Tensor, batch_size: int, block_size: int, generator: torch.Generator
) -> tuple[torch.Tensor, torch.Tensor]:
    ix = torch.randint(0, len(data) - block_size - 1, (batch_size,), generator=generator)
    x = torch.stack([data[i : i + block_size] for i in ix])
    y = torch.stack([data[i + 1 : i + 1 + block_size] for i in ix])
    return x, y


def train(steps: int = STEPS, lr: float = LR, log_every: int = 20) -> list[float]:
    torch.manual_seed(0)
    gen = torch.Generator().manual_seed(0)
    model = MiniGPT()
    optimizer = torch.optim.AdamW(model.parameters(), lr=lr)
    losses: list[float] = []
    for step in range(steps):
        xb, yb = get_batch(DATA, BATCH_SIZE, BLOCK_SIZE, gen)
        _, loss = model(xb, yb)
        optimizer.zero_grad()
        optimizer.step()
        losses.append(loss.item())
        if step % log_every == 0 or step == steps - 1:
            print(f"step {step:4d} | loss {loss.item():.4f}")
    return losses


# ========================= TESTS =========================
# !!! 剧透警告: 往下是修复版参考实现 + 测试, 先自己找完 bug 再看 !!!


class FixedCausalSelfAttention(CausalSelfAttention):
    def forward(self, x: torch.Tensor) -> torch.Tensor:
        B, T, C = x.shape
        q, k, v = self.qkv(x).chunk(3, dim=-1)
        q = q.view(B, T, self.n_head, self.head_dim).transpose(1, 2)
        k = k.view(B, T, self.n_head, self.head_dim).transpose(1, 2)
        v = v.view(B, T, self.n_head, self.head_dim).transpose(1, 2)
        att = (q @ k.transpose(-2, -1)) / math.sqrt(self.head_dim)
        # FIX bug 2: 被 mask 的位置要在 softmax 前置为 -inf, 而不是乘 0
        att = att.masked_fill(self.mask[:T, :T] == 0, float("-inf"))
        att = F.softmax(att, dim=-1)
        y = att @ v
        y = y.transpose(1, 2).contiguous().view(B, T, C)
        return self.proj(y)


class FixedMiniGPT(MiniGPT):
    def __init__(self) -> None:
        super().__init__()
        for block in self.blocks:
            block.attn = FixedCausalSelfAttention(N_EMBD, N_HEAD, BLOCK_SIZE)

    def forward(
        self, idx: torch.Tensor, targets: torch.Tensor | None = None
    ) -> tuple[torch.Tensor, torch.Tensor | None]:
        B, T = idx.shape
        pos = torch.arange(T, device=idx.device)
        # FIX bug 1: token embedding 要加上 positional embedding
        x = self.wte(idx) + self.wpe(pos)
        for block in self.blocks:
            x = block(x)
        x = self.ln_f(x)
        # FIX bug 4: 权重绑定的 lm_head 是 x @ E^T, E:(V,C); 忘 .T 只因 V==C 才没报错
        logits = x @ self.wte.weight.T
        loss = None
        if targets is not None:
            loss = F.cross_entropy(logits.view(-1, logits.size(-1)), targets.view(-1))
        return logits, loss


def train_fixed(steps: int = STEPS, lr: float = LR, log_every: int = 20) -> list[float]:
    torch.manual_seed(0)
    gen = torch.Generator().manual_seed(0)
    model = FixedMiniGPT()
    optimizer = torch.optim.AdamW(model.parameters(), lr=lr)
    losses: list[float] = []
    for step in range(steps):
        xb, yb = get_batch(DATA, BATCH_SIZE, BLOCK_SIZE, gen)
        _, loss = model(xb, yb)
        optimizer.zero_grad()
        # FIX bug 3: step 之前必须 backward, 否则 grad 全为 None, 参数永不更新
        loss.backward()
        optimizer.step()
        losses.append(loss.item())
        if step % log_every == 0 or step == steps - 1:
            print(f"step {step:4d} | loss {loss.item():.4f}")
    return losses


def test_setup_and_shapes() -> None:
    # bug 4 之所以不报 shape 错, 全靠这个巧合
    assert VOCAB_SIZE == N_EMBD == 40
    torch.manual_seed(0)
    gen = torch.Generator().manual_seed(0)
    xb, yb = get_batch(DATA, BATCH_SIZE, BLOCK_SIZE, gen)
    assert xb.shape == yb.shape == (BATCH_SIZE, BLOCK_SIZE)
    assert torch.equal(xb[:, 1:], yb[:, :-1])  # y 是 x 右移一位
    for model in (MiniGPT(), FixedMiniGPT()):
        logits, loss = model(xb, yb)
        assert logits.shape == (BATCH_SIZE, BLOCK_SIZE, VOCAB_SIZE)
        assert loss is not None and torch.isfinite(loss)
        logits, loss = model(xb[:, :1])  # T=1 边界: mask 退化为 1x1
        assert logits.shape == (BATCH_SIZE, 1, VOCAB_SIZE) and loss is None


def test_initial_loss_near_uniform() -> None:
    # 未训练时 logits ~ 0, loss 应约等于 ln(V); 面试时的关键诊断数字
    torch.manual_seed(0)
    gen = torch.Generator().manual_seed(0)
    xb, yb = get_batch(DATA, BATCH_SIZE, BLOCK_SIZE, gen)
    for model in (MiniGPT(), FixedMiniGPT()):
        _, loss = model(xb, yb)
        assert abs(loss.item() - math.log(VOCAB_SIZE)) < 0.2


def test_fixed_attention_matches_torch_sdpa() -> None:
    torch.manual_seed(0)
    attn = FixedCausalSelfAttention(N_EMBD, N_HEAD, BLOCK_SIZE)
    x = torch.randn(2, 16, N_EMBD)
    B, T, C = x.shape
    q, k, v = attn.qkv(x).chunk(3, dim=-1)
    q = q.view(B, T, N_HEAD, C // N_HEAD).transpose(1, 2)
    k = k.view(B, T, N_HEAD, C // N_HEAD).transpose(1, 2)
    v = v.view(B, T, N_HEAD, C // N_HEAD).transpose(1, 2)
    y = F.scaled_dot_product_attention(q, k, v, is_causal=True)
    expected = attn.proj(y.transpose(1, 2).contiguous().view(B, T, C))
    torch.testing.assert_close(attn(x), expected, rtol=1e-4, atol=1e-5)


def test_fixed_model_is_causal() -> None:
    torch.manual_seed(0)
    model = FixedMiniGPT().eval()
    idx = torch.randint(0, VOCAB_SIZE, (1, 16))
    idx2 = idx.clone()
    idx2[0, -1] = (idx2[0, -1] + 1) % VOCAB_SIZE
    with torch.no_grad():
        logits1, _ = model(idx)
        logits2, _ = model(idx2)
    # 改最后一个 token 不能影响之前任何位置的预测
    torch.testing.assert_close(logits1[:, :-1], logits2[:, :-1], rtol=1e-4, atol=1e-5)
    assert not torch.allclose(logits1[:, -1], logits2[:, -1], atol=1e-5)
    # 全相同 token 输入也应有限且因果
    same = torch.zeros(1, 8, dtype=torch.long)
    with torch.no_grad():
        logits, _ = model(same)
    assert torch.isfinite(logits).all()


def test_buggy_model_leaks_future() -> None:
    # 反向验证 bug 2: 乘 0/1 的 mask 挡不住未来信息
    torch.manual_seed(0)
    model = MiniGPT().eval()
    idx = torch.randint(0, VOCAB_SIZE, (1, 16))
    idx2 = idx.clone()
    idx2[0, -1] = (idx2[0, -1] + 1) % VOCAB_SIZE
    with torch.no_grad():
        logits1, _ = model(idx)
        logits2, _ = model(idx2)
    assert not torch.allclose(logits1[:, 0], logits2[:, 0], atol=1e-6)


def test_buggy_wpe_unused() -> None:
    # 反向验证 bug 1: wpe 没进计算图, backward 后 grad 是 None
    torch.manual_seed(0)
    gen = torch.Generator().manual_seed(0)
    xb, yb = get_batch(DATA, BATCH_SIZE, BLOCK_SIZE, gen)
    buggy = MiniGPT()
    _, loss = buggy(xb, yb)
    loss.backward()
    assert buggy.wpe.weight.grad is None
    fixed = FixedMiniGPT()
    _, loss = fixed(xb, yb)
    loss.backward()
    assert fixed.wpe.weight.grad is not None
    assert fixed.wpe.weight.grad.abs().sum() > 0


def test_buggy_params_never_update() -> None:
    # 反向验证 bug 3: 没有 backward, optimizer.step() 是空操作
    torch.manual_seed(0)
    gen = torch.Generator().manual_seed(0)
    model = MiniGPT()
    optimizer = torch.optim.AdamW(model.parameters(), lr=LR)
    before = [p.detach().clone() for p in model.parameters()]
    for _ in range(3):
        xb, yb = get_batch(DATA, BATCH_SIZE, BLOCK_SIZE, gen)
        _, loss = model(xb, yb)
        optimizer.zero_grad()
        optimizer.step()
    for p, b in zip(model.parameters(), before):
        assert torch.equal(p, b)


def test_loss_trajectories() -> None:
    print("  [buggy] 200 steps:")
    buggy = train(steps=STEPS, log_every=40)
    print("  [fixed] 200 steps:")
    fixed = train_fixed(steps=STEPS, log_every=40)
    buggy_final = sum(buggy[-10:]) / 10
    fixed_final = sum(fixed[-10:]) / 10
    print(f"  buggy: init {buggy[0]:.4f} -> final(avg last 10) {buggy_final:.4f}")
    print(f"  fixed: init {fixed[0]:.4f} -> final(avg last 10) {fixed_final:.4f}")
    assert buggy_final > 0.8 * buggy[0], "buggy 版 loss 不应明显下降"
    assert fixed_final < 0.6 * fixed[0], "fixed 版 loss 应显著下降"


def run_all_tests() -> None:
    tests = [
        test_setup_and_shapes,
        test_initial_loss_near_uniform,
        test_fixed_attention_matches_torch_sdpa,
        test_fixed_model_is_causal,
        test_buggy_model_leaks_future,
        test_buggy_wpe_unused,
        test_buggy_params_never_update,
        test_loss_trajectories,
    ]
    for t in tests:
        print(t.__name__)
        t()
    print("ALL TESTS PASSED")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--buggy", action="store_true", help="只跑埋 bug 版训练")
    parser.add_argument("--fixed", action="store_true", help="只跑修复版训练")
    args = parser.parse_args()
    if args.buggy:
        train()
    elif args.fixed:
        train_fixed()
    else:
        run_all_tests()
