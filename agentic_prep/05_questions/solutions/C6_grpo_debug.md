# [C6] Anthropic RL Fundamentals：debug GRPO training loop · 参考实现

⏱ 读完 12 min ｜ 先做 [../../../online_resource/drills/04_grpo_ppo.py](../../../online_resource/drills/04_grpo_ppo.py) 的盲找 bug 练法（限时 10 分钟不看行尾标注），再看本文

题库原文：[../C_live_ai_coding.md#c6](../C_live_ai_coding.md#c6) ｜ 概念底座：[../../03_gaps/agentic_rl.md](../../03_gaps/agentic_rl.md)

## 题目还原 + 验收标准

Anthropic RE 店面四选一 track（2026 Q2 新增），给一段简化 GRPO training step，埋 3 个 bug。**每个 bug 要求给出检测方法 + 具体修复，不能只点名**。之后必接核心追问：严格 on-policy 下为什么 `exp(logp_new - logp_old) ≠ 1`，要求设计判别实验区分"设计内偏差"与真 bug。

**验收标准**：

1. 开场先澄清（reward 类型、每 rollout batch 几次 optimizer step、rollout 与训练是否同一 forward 路径、精度、KL 实现）——这些直接决定第 4 问答案
2. 每个 bug 三段式：**症状**（loss/梯度/曲线上看到什么）→ **定位**（写出能复现的最小 assert/实验）→ **修法**（具体代码）
3. 能默写正确参考实现：shift 对齐、mask 归一、group advantage 带 eps、`logp_old` detach、k3 KL
4. ratio ≠ 1 追问：先说"设计上首步应该恰等于 1"，再给两类设计内原因 + 判别实验，最后才谈 correction，不张口就说 bug

## 解题主线（假设 45–55 min）

| 时间 | 做什么 | 可以砍什么 |
|---|---|---|
| 0–5 | 澄清 5 问 + 口述 GRPO step 的正确形态（下面代码的结构） | — |
| 5–20 | 系统性扫代码找 bug：按数据流顺序 reward→adv→logp→ratio→loss 逐段对照正确形态 | 不要跳读，按流扫一遍就全出来 |
| 20–35 | 每个 bug 给 检测 assert + 修复代码，边修边说症状 | 检测可以口述断言点，不必真跑 |
| 35–45 | ratio ≠ 1 追问 + 判别实验 | — |
| 45+ | follow-up：clip 防崩、全同 reward、KL 位置 | — |

找 bug 的方法论（开口说出来，占分）：**不逐行猜，按张量流走一遍，每个中间量报 shape 和已知不变式**——`adv` 每组均值 0；`logp` 的位置 t 必须对应 token t+1；masked 位置梯度必须为 0；首步 ratio 必须恰为 1。不变式破在哪，bug 就在哪。

## 参考实现（正确形态，现场可默写，~75 行）

```python
"""GRPO step 正确参考。B 条序列 = 同一 prompt 的一个 group，rewards: [B]。"""
import torch
import torch.nn.functional as F

def token_log_probs(logits, tokens):
    """logits: [B, T, V], tokens: [B, T] -> [B, T]。shift 由调用方负责。"""
    logp = F.log_softmax(logits, dim=-1)          # 内部减 max，大 logits 数值稳定
    return logp.gather(-1, tokens.unsqueeze(-1)).squeeze(-1)

def group_relative_advantage(rewards, eps=1e-8):
    """组内 z-score。全相同 reward -> 全零（零信号，不是 nan）。"""
    std = rewards.std(unbiased=False)             # population std：G=1 时为 0 而非 nan
    if std < eps:
        return torch.zeros_like(rewards)
    return (rewards - rewards.mean()) / std

def kl_k3(logp_policy, logp_ref):
    """Schulman k3 估计 KL(policy||ref)：r - log r - 1，逐点 >=0 且无偏。"""
    delta = logp_ref - logp_policy
    return torch.exp(delta) - delta - 1.0

def grpo_step(logits_new,      # [B, T, V] 当前 policy（带梯度）
              logits_old,      # [B, T, V] rollout 时 policy（生产中直接用 vLLM 记录的 logp）
              logits_ref,      # [B, T, V] 冻结 reference
              tokens,          # [B, T] prompt + response token ids
              response_mask,   # [B, T] 1 = response token, 0 = prompt/padding/tool 输出
              rewards,         # [B]
              clip_eps=0.2, beta=0.04):
    # 1. group-relative advantage：整条序列一个标量，广播到每个 action token
    adv = group_relative_advantage(rewards).unsqueeze(-1)        # [B, 1]

    # 2. shift 对齐：logits[:, t] 预测 tokens[:, t+1]
    targets = tokens[:, 1:]                                      # [B, T-1]
    mask = response_mask[:, 1:].float()                          # target 侧的 mask
    logp_new = token_log_probs(logits_new[:, :-1], targets)
    logp_old = token_log_probs(logits_old[:, :-1], targets).detach()
    logp_ref = token_log_probs(logits_ref[:, :-1], targets).detach()

    # 3. clipped surrogate（token 级）
    ratio = torch.exp(logp_new - logp_old)
    per_token = -torch.min(ratio * adv,
                           ratio.clamp(1 - clip_eps, 1 + clip_eps) * adv)

    # 4. KL 惩罚放 loss（k3），只约束 policy 相对 ref 的漂移
    per_token = per_token + beta * kl_k3(logp_new, logp_ref)

    # 5. mask 归一，绝不 .mean()；clamp(min=1) 防全零 mask 0/0
    return (per_token * mask).sum() / mask.sum().clamp(min=1.0)
```

现场自检 assert（口述或写出，每条对应一个 bug 类）：

```python
# A. 全同 reward -> adv 全零、loss 有限（抓归一化 bug）
assert torch.isfinite(grpo_step(ln, lo, lr, tok, m, torch.ones(B)))
# B. masked 位置梯度必须为 0（抓 shift/mask bug）
g = ln.clone().requires_grad_(True); grpo_step(g, lo, lr, tok, m, r).backward()
assert g.grad[:, :-1][m[:, 1:] == 0].abs().max() < 1e-9
assert g.grad[:, -1].abs().max() < 1e-9   # 最后一个位置不预测任何 target
# C. 首个 inner step（new == old）ratio 恰为 1（抓 old policy 混用）
assert torch.allclose(torch.exp(logp_new - logp_old), torch.ones_like(logp_new))
```

## 三类经典 bug：症状 → 定位 → 修法

### Bug 1：advantage 归一化错（除零 / 维度错）

- **症状**：某些 step loss 突然 nan 且从此不恢复——恰好发生在某组 reward 全相同（全过或全挂）的 batch；或者（维度错变体）loss 有限但训练方向诡异：简单题全对的组被跨组归一化后拿到非零 advantage，policy 在已解决的题上继续推概率。
- **定位**：构造 `rewards = torch.ones(G)` 喂进去，期望 adv 全零、loss 有限——buggy 版返回 nan（`0/0`）。维度错变体：断言**每组内** `adv.mean() ≈ 0`；若只有全 batch 均值为 0、组内不为 0，就是把 `[num_prompts, G]` flatten 后在错误维度上归一了。
- **修法**：`std < eps` 时返回全零（语义：组内无对比信号，这条 batch 对 policy gradient 贡献为 0，只剩 KL 项）；多组时 `rewards.view(num_prompts, G)` 后在 `dim=-1` 归一。工程加分：提 DAPO dynamic sampling（全同组零梯度白烧 rollout，在线丢弃补采）和 Dr. GRPO（干脆不除 std，避免全对/全错附近的 difficulty bias，TRL `scale_rewards=False`）。

### Bug 2：log-prob 对错 token / mask 错（shift + padding）

两个子 bug 常一起埋，症状不同要分开说：

- **shift 缺失**（`token_log_probs(logits, tokens)` 不切片）：**症状**是不炸、loss 有限、曲线还能动，但优化的是"位置 t 的 logits 对 token t 的概率"——一个自回归模型里根本不存在的量，policy 缓慢劣化或不涨。这是三个 bug 里最隐蔽的，**必须用不变式抓**。**定位**：梯度测试——`logits[:, -1]` 不预测任何 target，正确实现下其梯度恒为 0；buggy 版非零（见上面 assert B）。或对拍：`F.cross_entropy(logits[:, :-1].transpose(1,2), tokens[:, 1:])` 应等于 `-logp` 的均值。**修法**：`logp = token_log_probs(logits[:, :-1], tokens[:, 1:])`，mask 同步取 `response_mask[:, 1:]`。
- **padding/prompt 进 loss**（直接 `.mean()`）：**症状**：短 response 的序列被 padding 稀释、每条序列实际权重和长度挂钩（length bias）；prompt token 也吃到 policy gradient，模型学着"预测 prompt"，等于混进一份错位 SFT；multi-turn 下 tool 输出 token 进 loss 更致命——ratio 对环境 token 无定义，policy 给一段 JSON 的概率可以任意低，ratio 爆出极端值，训练直接不稳（[../../03_gaps/agentic_rl.md](../../03_gaps/agentic_rl.md) multi-turn 节的两层论证）。**定位**：给同一 batch 尾部多 pad 几个 token，loss 不应变化；buggy 版变了。**修法**：`(per_token * mask).sum() / mask.sum().clamp(min=1)`，绝不 `.mean()`。

### Bug 3：ratio 用了错误的 old policy

三个高频变体，先看代码里 `logp_old` 是**谁算的、什么时候算的、detach 没有**：

- **变体 a：用训练引擎重算 logp_old 而不是 rollout 时记录的**——若在每次 update 前用当前权重重算，第一 inner step 后 ratio 永远 ≈ 1，clip 永不触发，等价于裸 REINFORCE 在 off-policy 数据上跑，多 inner step 时训练发散。**定位**：打印第二个 inner step 的 `ratio` 分布，恒 1 即中招。**修法**：`logp_old` 在 rollout 时由采样引擎记录并随 trajectory 存储（见 gaps 文件伪码：`logp_old = traj.rollout_logp`），训练时只读不重算。
- **变体 b：没 detach / 直接复用 logp_new 的计算图**——极端情况 `logp_old = logp_new`（同一 tensor），ratio 恒为常数 1，policy gradient 项梯度**恰好为零**，loss 曲线一条直线只剩 KL 在动。**定位**：`loss.backward()` 后看梯度范数是否只来自 KL 项（`beta=0` 时梯度全零即实锤）。**修法**：`.detach()` 或 `torch.no_grad()` 下计算。
- **变体 c：拿 logits_ref 当 old**——ref 是冻结的 KL 锚点，old 是上一次 rollout 的 policy，训练几百步后两者相差很远，ratio 系统性偏离 1，clip 大面积触发，有效梯度被裁掉，loss 看着平稳但 policy 不动。**定位**：监控 clip fraction（被裁 token 占比），正常 <10–20%，buggy 版随训练单调上升到大半。**修法**：ratio 用 old，KL 用 ref，两个变量名义上就不该混。

## 核心追问：on-policy 首步 ratio 为什么应该 = 1，实际为什么 ≠ 1

**先给"应该 = 1"的完整论证**（面试官在验证你懂 ratio 的语义）：ratio = `exp(logp_θ(a|s) - logp_θ_old(a|s))`，是 importance weight，修正"数据从 π_old 采、梯度对 π_θ 求"的分布错位。严格 on-policy 的第一个 optimizer step，θ 和 θ_old 是**同一组参数**，对同一 token 序列、同一 forward 路径，两个 logp 逐位相等，ratio 恒等于 1，clip 不触发。此时 loss 退化为 `-mean(adv · ratio)`，梯度 `∇ratio|ratio=1 = ∇logp`，正是 REINFORCE with baseline——**ratio=1 不代表没梯度**，这是常见误解，要主动说破。

**实际 ≠ 1 的两类设计内原因**（不是 bug）：

1. **推理引擎与训练器 forward 路径不同**：rollout 的 logp 来自 vLLM（paged attention、fused kernel、bf16），训练重算的 logp 来自 FSDP/Megatron 路径——kernel 实现和数值精度不同，逐 token 有 1e-3 量级漂移，exp 之后 ratio 在 1 附近抖动。
2. **每个 rollout batch 走多次 optimizer step**：inner epoch ≥ 2 时，第二步起 θ 已更新，本来就 off-policy——ratio ≠ 1 恰恰是 clip 机制**存在的理由**，此时它在正常工作。

**判别实验**（这是这题的评分重点，"先实验再下结论"）：

1. **同 checkpoint 双路径对拍**：freeze 权重，同一批 token 分别走推理引擎和训练引擎算 logp，画 `|Δlogp|` 分布。均匀的小量级（~1e-3）→ 数值/kernel 差异，设计内；把训练器强制 fp32 + deterministic 后 diff 显著缩小可进一步确认。
2. **看偏差的结构**：diff 集中在 message 边界/特殊 token → retokenization bug（多轮拼 context 重新 tokenize 导致 token 边界漂移，正解 token-in-token-out，永不 re-encode）；diff 整体错位一格 → shift bug；diff 只出现在第二个 inner step 之后且随步数增大 → 多次 optimizer step，设计内。
3. **控制变量排真 bug**：检查训练 forward 是否 `model.eval()`（dropout 开着会造成随机 diff）；检查 `logp_old` 是记录的还是重算的（变体 a）；检查两路径温度/top-p 是否影响了记录的 logp。

**结论口径**：小而均匀的漂移不修，做**监控**（两路 logp diff 作为一级 health metric）；漂移大到影响训练时用 rollout logp 做 truncated importance correction（ratio clamp 上限），或 GSPO 式 sequence-level ratio，而不是硬当 bug 修（gaps 文件失败模式 ④ 的口径）。

## 边界与测试要点（口头必提）

- 全同 reward 组 → adv 全零不炸（test A）；G=1 → std=0 同样走零分支
- 全零 mask（response 被截断光）→ loss 为 0 不是 nan（`clamp(min=1)`）
- masked 位置与最后一个 logits 位置梯度为 0（test B，一条测试同时抓 shift 和 mask 两个 bug）
- policy == ref 且 reward 全同 → loss 恰为 0（k3 逐点为 0 + adv 全零，解析可验证）
- 极大 logits（±1000）→ `log_softmax` 路径仍有限（别手写 `log(softmax(x))`）
- drill 里有完整可跑测试组：[../../../online_resource/drills/04_grpo_ppo.py](../../../online_resource/drills/04_grpo_ppo.py) 的 `test_gradient_masking` / `test_buggy_nan_on_equal_rewards_fixed_is_fine` 就是上面 assert 的成品

## 高频 follow-up 与应对

- **clipped surrogate 怎么防崩？**——ratio 偏离 `1±ε` 且方向是"继续扩大更新"时，`min` 把该 token 的梯度置零：adv>0 时 ratio 涨过 1+ε 不再有推力，adv<0 时 ratio 跌破 1−ε 不再有拉力；反方向（修正回 1）永远保留梯度。它是逐 token 的信任域近似，不是全局约束——所以 off-policy 程度太深时还是会崩，才需要限制 inner step 数。
- **组内奖励全同怎么办？**——数学上零信号，返回全零 advantage；工程上这类 prompt 白烧 rollout 算力，做法是离线按 pass rate 过滤（0 或 1 的剔除）+ 在线 dynamic sampling 补采（DAPO），难度分布随训练滚动更新。
- **process vs outcome supervision？**——agent 任务默认 outcome：终局 reward 广播到全部 action token，credit assignment 交给组内对比 + clip；process reward 步级标注贵且同样可 hack。说完主动补一句 outcome 的代价：长轨迹里"哪一步走对了"完全靠同题多采样的统计对比，G 要够大。
- **KL 放 reward 还是 loss？**——放 reward 里会改变 advantage、污染组内对比（KL 大的轨迹被系统性压 reward，credit assignment 变形）；GRPO 常用做法放 loss 里 per-token 直接约束，配 k3 estimator（无偏 + 逐点非负 → 低方差，`exp(Δ)-Δ-1`，非负性来自 `e^d ≥ d+1`）。TRL 默认 `beta=0` 连 ref model 都不加载，省一份权重——beta 是否为 0 是开场该澄清的问题之一。
- **为什么 GRPO 能砍 value network？**——advantage 从 GAE 换成组内 z-score：同 prompt 采 G 条，组均值就是 baseline。agent 任务 reward 稀疏 + 序列超长，value network 又难训又和 policy 同尺寸，"同题多采样"用 rollout 算力换掉一整个 critic。

## 如果这轮允许 AI

本轮按面经是**可查文档、禁 AI**，别指望现场生成。若例外允许：按 [../../02_playbook.md](../../02_playbook.md) 第八节，第一条任务让 AI 只读复述这段 GRPO step 的张量流（每个中间量 shape + 语义），你对照上面的不变式清单找破绽；修复自己写，让 AI 只生成上面三条 assert 的测试代码来验证。
