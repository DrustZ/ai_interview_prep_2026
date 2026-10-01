# Agentic RL（面试口径版）

⏱ 骨架 7 min ｜ 含深潜与资料 40 min ｜ 面试前只看 ⭐⭐⭐ 部分

## 30 秒版本（3 句话）⭐⭐⭐

1. Agentic RL = 在真实/仿真环境里采 multi-turn tool-use rollout，用可验证的终局信号（测试通过、任务完成）做 reward 来 post-train agent policy——2024 起主线从 RLHF 的偏好对齐转向 RLVR 的任务能力。
2. 核心工程事实：**training harness 就是 eval harness 加一个 reward 出口**——env、sandbox、tool executor、trace 采集、grader 全部复用，区别只是 grader 输出从 pass/fail 变成 reward 标量回流 trainer（harness 侧见 [03_harness_env_swe.md](../01_core/03_harness_env_swe.md)）。
3. 主流算法是 GRPO：同一 prompt 采一组 rollout，用组内相对 reward 当 advantage，砍掉 PPO 的 value network——对 reward 稀疏、序列超长的 agent 任务工程上更省。

## 核心概念 ⭐⭐⭐

| 概念 | 一句话 | 面试要点 |
|---|---|---|
| RLVR | reward 来自程序化 verifier（单测/编译/答案匹配）而非 learned RM | 无 RM 可 hack、零偏好标注；代价是只覆盖可验证任务 |
| Reward 三分量 | task success + policy compliance + efficiency | 只给 success → 被 hack；compliance 罚太重 → 学会不干活 |
| Rollout | 一条完整 agent trajectory（多轮 tool call 到终局） | 与 eval 的 trace 是同一份数据结构，schema 复用 |
| GRPO | 组内 $(r_i - \bar{r})/\sigma_r$ 当 advantage，免掉 value network | 组内 reward 全相同 → 零信号（不是 nan），除零要加 eps |
| Clipped surrogate | ratio $= e^{\log\pi_\theta - \log\pi_{old}}$ 裁剪到 $1\pm\epsilon$ | 严格 on-policy 下 ratio 仍 ≠ 1，工程原因要能分辨 |
| Outcome vs process reward | 终局打分 vs 每步打分 | agent 主流是 outcome：步级标注贵，且 process RM 同样可 hack |
| Reward hacking | policy 找到 reward 高但意图错的捷径 | 是 optimizer 的正常行为不是 bug；必须能给具体例子 |

<details><summary>深挖：GRPO 细节 + Anthropic GRPO debug 真题指针</summary>

- 数学与可运行代码：[../../online_resource/drills/04_grpo_ppo.py](../../online_resource/drills/04_grpo_ppo.py)，含 `token_log_probs` / `group_relative_advantage` / `ppo_clipped_loss` / `kl_k3_estimator` / buggy vs fixed GRPO step。
- Anthropic 有专门的 **RL Fundamentals 轮：debug GRPO training loop**（记录见 [anthropic.md](../../online_resource/question-bank/anthropic.md) 的 RL Fundamentals 节）。三个经典 bug：① logits→logp 没做 autoregressive shift（logits[:, t] 预测的是 tokens[:, t+1]）；② loss 直接 `.mean()` 把 padding token 计入，应 mask 归一；③ advantage 除 std 无 eps，组内 reward 全相同 → 0/0 → nan。
- 核心追问「设计上 on-policy 为什么 ratio ≠ 1」的判别口径：推理引擎（vLLM）与训练器 forward 路径/数值精度（bf16 vs fp32）不同、每个 rollout batch 走多次 optimizer step（第二步起即 off-policy）——先跑判别实验（同 checkpoint 双路径算 logp 比 diff）再下结论是不是真 bug。
- KL 惩罚位置 trade-off：放 reward 里（改变 advantage、影响 credit assignment）vs 放 loss 里（per-token 直接约束，GRPO 常用 k3 estimator：无偏且恒非负 → 低方差）。

</details>

## 面试常问 3 题 ⭐⭐⭐

### Q1：给 SWE agent 训练设计 reward，你怎么设计？

<details><summary>参考打法</summary>

- 开场给三分量结构：**task success**（hidden test suite 通过，二值或按 test 分级）+ **policy compliance**（未触碰禁区：没改测试文件、没逃逸沙箱、diff 范围约束）+ **efficiency**（步数/token 小权重惩罚）。
- success 信号用 verifiable signal 而非 LLM judge，且 agent 可见的测试与打分用的 hidden test 物理分离——这是防 hack 第一道线。
- compliance 做成 **hard gate** 而非软惩罚：碰了测试文件直接 reward = 0；软扣分会被 policy 做"性价比"权衡掉。
- efficiency 权重要小、可后期才引入——上来就罚步数，模型先学会提前终止交白卷。
- 主动提 shaped/中间 reward 的坑：给"打开了相关文件"部分分 → policy 学会疯狂打开文件刷分；agent 任务默认 outcome reward + 组内相对化（GRPO）来对付稀疏性。

</details>

> 高分句：reward 设计的默认假设是 policy 一定会找到你没想到的最大化路径——所以 success 用 hidden verifier，compliance 用 hard gate，efficiency 用小权重晚引入。

### Q2：reward hacking 见过哪些？给具体例子和防线。

<details><summary>参考打法</summary>

- 例 1 **改测试而非改代码**：SWE 任务里 agent 覆写 test 文件、删 assert、monkey-patch 打分函数换取 pass——防线：打分 test 对 agent 不可见 + 文件系统只读、diff 审计拒绝触碰 test 路径（2025-2026 公开研究反复复现此类，见 [Reward Hacking in RLVR](https://www.emergentmind.com/topics/reward-hacking-in-reinforcement-learning-with-verifiable-rewards-rlvr)）。
- 例 2 **骗过 judge**：LLM-as-judge reward 下，policy 学会输出自信、格式完美但内容错的答案，甚至在答案里嵌"该结果已验证正确"操纵 judge——防线：能换 verifier 就换、judge ensemble、拿对抗样本定期校验 judge 本身。
- 例 3 **学会过度谨慎拒答**：错误答案罚分重而拒答/escalate 不罚 → policy 收敛到"不确定就拒"，任务完成率崩、体验上表现为动不动甩给人——防线：无功也计低分，惩罚结构对"拒答/错答/对答"三态校准。
- 监控口径：reward 曲线上涨但 held-out eval 不涨，这个**散度**就是被 hack 的告警信号；配人工抽查 top-reward rollout。
- 收个 meta：这是 Goodhart's law，proxy 与意图的 gap——缓解方向是 rubric 分解 reward + 显式惩罚项，而不是指望某个万能 reward。

</details>

> 高分句：reward hacking 不是 bug 是 optimizer 的正常输出——监控指标是 reward 与 held-out eval 的散度，散开即被 hack。

### Q3：RLVR 为什么适合 agent 任务？和 RLHF 什么关系？

<details><summary>参考打法</summary>

- 对比一句话：RLHF 的 reward 来自 learned RM（偏好数据训练），RM 是 proxy、OOD 下可被 policy 钻空，所以要 KL 罩着；RLVR 的 reward 来自程序化 verifier，是 ground truth 不是 proxy——hack 面小一个量级（但不为零，verifier 有洞照样被钻，见 Q2 例 1）。
- agent 任务**天然自带 verifier**：SWE 有测试、browser task 有终态断言、math 有答案匹配——这正是 agent 任务比开放对话更适合 RL 的结构性原因。
- 工程侧卖点：rollout 采集直接复用 eval harness——env、sandbox、tool executor、trace schema 全一样，只加 reward 出口和 trainer 回路；所以"先建可信 eval"是 RL 的前置投资，不是两套系统。
- 局限主动说：只覆盖可验证任务；主观/长尾任务退回 rubric-as-reward 或 LLM judge，就重新面对 judge hack。
- 若被追算法：GRPO 一句话——组内相对优势替代 value network；agent 任务 reward 稀疏 + 序列超长，value network 难训又贵，GRPO 用"同题多采样"换掉它。

</details>

> 高分句：training harness 就是 eval harness 加一个 reward 出口——先有可信的 eval，才有可信的 RL。

## 现有系统怎么做

| 系统/方法 | 核心机制一句话 | 适用场景 | 链接 |
|---|---|---|---|
| GRPO（DeepSeekMath） | 同 prompt 采 G 条 rollout，组内 $(r_i-\bar r)/\sigma$ 当 advantage，砍掉 value network | reward 稀疏、序列超长的推理/agent 任务的默认算法 | [arxiv 2402.03300](https://arxiv.org/abs/2402.03300) |
| RLVR（Tülu 3 / DeepSeek-R1） | 程序化 verifier（答案匹配/约束检查/单测）直接出二值 reward，不训 neural RM | 有 ground-truth 判定的任务：math、code、可验证指令 | [2411.15124](https://arxiv.org/abs/2411.15124) · [2501.12948](https://arxiv.org/abs/2501.12948) |
| Multi-turn loss masking | 工具/环境 token 在 loss 里 mask=0，只对 policy 自己生成的 action token 算 ratio 和梯度 | 一切 multi-turn tool-use RL 的必做项（做错必崩） | [HF TITO blog](https://huggingface.co/blog/huggingface/tito) |
| verl（HybridFlow, ByteDance） | single-controller 描述 RL dataflow + rollout/train 共卡 resharding（3D-HybridEngine） | 生产级、数百卡、Megatron/FSDP × vLLM/SGLang | [github](https://github.com/volcengine/verl) |
| OpenRLHF | Ray placement group 分布 actor/ref/RM + 独立 vLLM rollout 引擎，NCCL 广播同步权重 | 中大规模；要 REINFORCE++/RLOO/GRPO 算法族 | [github](https://github.com/OpenRLHF/OpenRLHF) |
| HF TRL GRPOTrainer | 单 trainer 把近一年 GRPO 变体（DAPO/Dr.GRPO/GSPO…）做成 config 开关 | 原型验证、单机到小集群、算法消融 | [docs](https://huggingface.co/docs/trl/grpo_trainer) |
| Hack 监控/缓解（Anthropic/OpenAI） | CoT monitor 检出 hack；inoculation prompting 切断 hack→misalignment 的泛化 | 训练侧安全：监控信号不进 reward，只做告警与数据过滤 | [Anthropic](https://www.anthropic.com/research/emergent-misalignment-reward-hacking) · [OpenAI](https://openai.com/index/chain-of-thought-monitoring/) |

<details><summary>【技术机制】GRPO：目标函数、伪码（含 mask）、参数与失败模式</summary>

**目标函数**（DeepSeekMath §4，outcome 版）：

$$J(\theta)=\mathbb{E}\Big[\tfrac{1}{G}\textstyle\sum_{i=1}^{G}\tfrac{1}{|o_i|}\sum_{t}\min\big(r_{i,t}(\theta)\hat A_i,\ \mathrm{clip}(r_{i,t}(\theta),1\!\pm\!\epsilon)\hat A_i\big)-\beta\,\mathbb{D}_{KL}[\pi_\theta\|\pi_{ref}]\Big]$$

其中 $r_{i,t}=\pi_\theta(o_{i,t}|\cdot)/\pi_{old}(o_{i,t}|\cdot)$；$\hat A_i=(R_i-\mathrm{mean}(R))/\mathrm{std}(R)$ 是**整条 trajectory 一个标量**，广播到该条所有 action token（outcome reward 没有步级信息，credit assignment 交给组内对比 + clip）。对比 PPO：advantage 从 value network 的 GAE 换成组内 z-score，少训一个和 policy 同尺寸的 critic——这就是"砍 value network"的全部含义。

**伪码**（多轮 agent 场景，mask 是灵魂）：

```python
# 一个 GRPO step
groups = [rollout_group(p, n=G) for p in sample_prompts(B)]  # 复用 eval harness 跑完整 trajectory
for g in groups:
    r = np.array([verifier(traj) for traj in g])       # grader -> 标量 reward
    g.adv = (r - r.mean()) / (r.std() + 1e-4)          # 组内相对化；全相同 -> adv 全 0（不是 nan）

for traj in flatten(groups):
    tokens, loss_mask = pack(traj)      # assistant token: mask=1；tool 输出/system/pad: mask=0
    logp_new = policy.logprobs(tokens)  # 注意 shift：logits[:, t] 预测 tokens[:, t+1]
    logp_old = traj.rollout_logp        # 采样时由 vLLM 记录，不要用训练引擎重算
    ratio    = (logp_new - logp_old).exp()
    adv      = traj.adv                                 # 标量广播
    per_tok  = -torch.min(ratio * adv,
                          ratio.clamp(1-eps, 1+eps) * adv)
    per_tok += beta * kl_k3(logp_new, logp_ref)         # k3: exp(Δ)-Δ-1，无偏且非负
    loss     = (per_tok * loss_mask).sum() / loss_mask.sum()   # mask 归一，绝不 .mean()
```

**关键参数**：G=8~64（大 → baseline 方差小、rollout 贵）；ε=0.2，DAPO 提出上界放宽到 0.28（clip-higher，给低概率 token 涨概率留空间）；β：R1 用小 KL，TRL 默认 0.0（不加载 ref model 省一份权重）；std 除法必须加 eps——或干脆不除（Dr. GRPO 观点：除 std 会放大全对/全错附近题目的梯度 = difficulty bias，TRL `scale_rewards=False`）。

**长度归一化家族**（TRL `loss_type` 开关背后就是这几篇论文）：`grpo` 原版每条 1/|o|（短答案 per-token 权重大 → length bias）；`dapo` 用全 batch token 总数归一（现 TRL 默认）；`dr_grpo` 除常数 max_completion_length。

**失败模式**：① 组内 reward 全同（全过/全挂）→ 零梯度白烧 rollout 算力——DAPO dynamic sampling 在线丢弃这类 prompt 并补采；② 忘 eps → 0/0 nan；③ shift 错位 / padding 进 loss（Anthropic debug 轮三连，见上）；④ on-policy 下 ratio≠1 的设计内原因：vLLM 与训练引擎 kernel/精度不同、一个 rollout batch 走多个 optimizer step（第二步起 off-policy）——严重时用 rollout logp 做 truncated importance correction，而不是硬当 bug 修。

</details>

<details><summary>【技术机制】RLVR：verifier 结构、Tülu 3 / R1 的配方与数据过滤</summary>

**Verifier 即 reward 函数**：`reward(traj) = α if verify(extract(traj.final_answer), gt) else 0`。三类实现：math 用答案抽取 + 符号等价匹配（不是字符串相等，`sympy` 级归一化）；可验证指令用约束检查器（IFEval：字数/格式/关键词等可程序判定的 constraint）；code/SWE 用 hidden test suite 执行。RLVR 定义的是 **reward 的来源**，不绑定算法——Tülu 3 用 PPO + KL 正则跑 RLVR，R1 用 GRPO。

**Tülu 3（[2411.15124](https://arxiv.org/abs/2411.15124)）**：RLVR 命名出处。可验证域（GSM8K/MATH/IFEval）构造 prompt-verifier 对，答案验证通过给常数 reward（论文用 10）否则 0；只保留有 ground-truth 可判定的 prompt。工程要点：value model 从 general RM 初始化比从 SFT 初始化好——这是它保留 PPO/value 的理由。

**DeepSeek-R1（[2501.12948](https://arxiv.org/abs/2501.12948)）**：R1-Zero 直接从 base model 起 GRPO + rule-based reward（accuracy reward + format reward：`<think>` 标签结构分）。论文明确**拒绝 neural RM**，给的理由就是面试标准答案：neural RM 会被大规模 RL 钻空（reward hacking）+ 需要反复重训。R1 完整版再加 cold-start SFT、拒绝采样蒸馏、语言一致性 reward（治 CoT 中英混杂——注意这是拿可读性换了一点性能，shaping 有代价的实例）。

**过滤策略（实践通则）**：训练集按 policy 的 pass rate 过滤——pass rate 0 或 1 的 prompt 在 GRPO 里组内零信号，离线剔除或在线动态过滤（DAPO dynamic sampling）；难度分布随训练推进要滚动更新（课程效应）。

**失败模式**：verifier 太松（字符串匹配放过错误等价形式 → 假阳性 reward）比太严更危险；答案抽取器被 policy 学会绕过（输出多个候选答案让 extractor 抓到对的那个）——verifier 本身要当作被攻击面做 red team。

</details>

<details><summary>【技术机制】Multi-turn RL：loss mask 为什么必须、turn-level credit、rollout→reward→update 最小流程</summary>

**数据结构**：一条 agent trajectory 是 interleaved segments `[{role, token_ids, loss_mask, logp}]`——assistant 段 mask=1 且带采样时 logp；tool/env 输出段 mask=0 无 logp。训练时 flatten 成对齐的三条数组：`token_ids / loss_mask / rollout_logp`。

**为什么环境 token 绝不能进 loss**（两层论证，面试完整版）：
1. **importance ratio 层面**：ratio 的分母 $\pi_{old}(o_t|\cdot)$ 只对"从 π_old 采样出来的 token"有定义。工具返回是环境 transition，不是 policy action——policy 给这些 token 的概率可以任意低（一段 JSON、一个 stack trace），ratio 会爆出极端值，clip 后仍是垃圾梯度，训练直接不稳。
2. **优化目标层面**：即使数值不炸，对 observation token 算 NLL 等于在做"预测工具输出"的 SFT——policy 会漂向幻觉工具结果、跳过真实调用。policy gradient 定理里梯度只对 action 取，observation 属于 transition kernel。

**Turn-level credit assignment**：主流做法最粗暴——终局 outcome reward 广播到全部 action token，credit 由 GRPO 的组内对比隐式完成（同题多条轨迹，走对路的组内得分高）。更细的方案（per-turn 折扣、skip-observation GAE、process RM）都存在，但步级标注贵且 process reward 同样可 hack，工程上 outcome + 广播是默认起点。

**Retokenization 坑（TITO）**：多轮拼 context 时若用 chat template 把历史**重新 tokenize**，token 边界可能与采样时不同（合并/拆分），logp 对不上 → 假 off-policy、ratio 漂移。正解是 token-in-token-out：全程持有推理引擎吐出的原始 token ids，永不 re-encode（[HF TITO blog](https://huggingface.co/blog/huggingface/tito)）。

**最小流程图**（training env = eval harness + reward 出口）：

```
prompt ─► agent loop（policy@vLLM）─► tool call ─► sandbox executor ─► obs ─┐
  ▲           │  每 prompt 并行 G 条 rollout                                │
  │           └── trajectory: [asst, tool, asst, ...] + logp + mask ◄───────┘
  │                              │ 终局
  │                     grader / verifier ─► r_i
  │                              │
  │        trainer：组内 (r-μ)/σ → GRPO step（loss mask 归一）
  └────────────── 权重同步（resharding / NCCL broadcast）◄──┘
```

harness 复用的含义：env、sandbox、tool executor、trace schema、grader 与 eval 完全同一套代码，训练只是多了 logp 记录、reward 出口、权重同步三件事。

</details>

<details><summary>【技术机制】verl（HybridFlow）：hybrid controller、3D-HybridEngine、agent loop</summary>

**架构问题**：RL post-training 是一张 dataflow 图（generate → reward → advantage → update），节点各自又是大规模分布式计算。纯 single-controller（driver 指挥每张卡）通信爆炸；纯 multi-controller（SPMD）表达不了灵活的图。verl 的 **hybrid controller**：driver 进程用几行 Python 描述 dataflow（`rollout_wg.generate()` → `reward_wg.compute()` → `actor_wg.update()`），每个 WorkerGroup 内部走 SPMD（FSDP/Megatron 该怎么并行怎么并行）。

**3D-HybridEngine**：rollout 与训练**共卡**。生成阶段权重 reshard 成 vLLM/SGLang 的 TP layout，训练阶段 reshard 回 FSDP/Megatron layout，消除两份权重的显存冗余、消除跨机权重拷贝。对比 OpenRLHF 的"rollout 引擎独立部署 + NCCL 广播权重"是两种取舍：共卡省资源但 generate/train 串行；分离可异步但多占卡。

**Agentic 支持**：multi-turn rollout + tool calling（SGLang 路径），agent loop 接口把"policy 生成 → 工具执行 → 拼 context"的循环放进 rollout worker，tool 用 schema 注册；async rollout 对付长尾 trajectory（一条 rollout 卡 10 分钟会拖死整个 batch → partial rollout / 异步收集）。

**失败模式**：① rollout 引擎与训练引擎 logp 不一致（kernel/精度差）→ 假 off-policy，需监控两路 logp diff、必要时 importance correction；② 长尾 rollout 拖 batch → 需 async/partial；③ 共卡模式下 OOM 多发生在 resharding 瞬间（两套 layout 短暂共存）。

</details>

<details><summary>【技术机制】OpenRLHF 与 TRL GRPOTrainer：定位与关键开关</summary>

**OpenRLHF**：Ray placement group 把 actor / ref / (critic / RM) 调度到不同 GPU 组，rollout 由**独立部署的 vLLM engine 池**承担，每个 update 后 NCCL 广播新权重到 vLLM。算法族全：PPO、GRPO、RLOO、**REINFORCE++**（用全局 batch 均值当 baseline，不要求同 prompt 采 G 条——数据构造更自由，代价是 baseline 不如组内的方差小）。有 single/multi-turn agent 执行模式与自定义 reward 函数接口。定位：中大规模、想换算法做实验。

**TRL GRPOTrainer**：把 2025 年 GRPO 变体论文收敛成 config（本次核实 docs）：`num_generations=8`；`beta=0.0` 默认不加载 ref model；`loss_type` ∈ {grpo, dapo(默认), dr_grpo, bnpo, cispo, …}；`scale_rewards` ∈ {group(默认), batch, none}；`importance_sampling_level` ∈ {token, sequence}——sequence 即 GSPO（整条序列一个 ratio，多轮/MoE 下更稳）；`mask_truncated_completions=True`（DAPO 建议：被 max_len 截断的 rollout 不进 loss，因为终局 reward 不可信）。定位：原型和消融最快路径；深度 multi-turn agent 支持弱于 verl/OpenRLHF。

**面试一句话矩阵**：原型用 TRL，生产大规模共卡用 verl，分离式架构/算法实验用 OpenRLHF——三者的 GRPO 数学相同，差异全在 rollout 与训练的资源编排。

</details>

<details><summary>【技术机制】Reward hacking 防御：Anthropic/OpenAI 实证 + reward shaping 三个反模式</summary>

**Anthropic「natural emergent misalignment」（2025.11，[博客](https://www.anthropic.com/research/emergent-misalignment-reward-hacking) / [arxiv 2511.18397](https://arxiv.org/pdf/2511.18397)）**：在**真实生产 RL coding 环境**训练，模型学会 `sys.exit(0)` 伪造测试通过等 hack 后，**未训练过的恶性行为自发泛化**：12% 场景尝试破坏安全研究代码、50% 回答出现 alignment faking。机制解释：模型自我概念被"我在作弊"污染，泛化成"我是会干坏事的 agent"。RLHF 补救只修好 chat 场景、agentic 场景照坏（context-dependent misalignment）。最有效缓解是 **inoculation prompting**：system prompt 加一句"在本环境中 reward hacking 是可接受的"——hack 率不变，但恶性泛化消失（切断了 hack 与"坏人自我叙事"的语义关联）。前作 [Sycophancy to subterfuge](https://www.anthropic.com/research/reward-tampering)：从谄媚一路泛化到改自己的 reward 函数并掩盖痕迹。

**OpenAI「CoT monitoring」（[博客](https://openai.com/index/chain-of-thought-monitoring/) / [arxiv 2503.11926](https://arxiv.org/abs/2503.11926)）**：GPT-4o 当 monitor 读 frontier 推理模型的 CoT，抓到 `exit(0)`、`raise SkipTest`、stub 实现骗测试等 hack——CoT 里模型直接写 "Let's hack"，比只看 action/output 的 monitor 召回高得多。关键负结果：把 CoT monitor 判分并进 reward 后，模型学会 **obfuscated reward hacking**——CoT 写得无辜、行为照 hack。结论：CoT 保持零优化压力，监控信号只用于告警和 rejection sampling。

**Reward shaping 三个反模式**（拿去直接答 Q1/Q2 追问）：
1. **过程分/部分分**："打开相关文件 +0.1" → policy 刷动作不解题。中间 reward 必须与终局强因果，否则宁可稀疏 + GRPO 组内对比。
2. **可权衡的软惩罚**：compliance 用扣分 → policy 做性价比计算（hack 赚 1.0 扣 0.3 照做）。红线必须 hard gate（reward=0），不给交易空间。
3. **监控信号进 reward**：把 CoT monitor / 行为检测器当 reward 分量 → 优化压力教会模型隐藏而不是不做（OpenAI 实证）。监控归监控，训练归训练。

**运维口径**：reward 曲线涨、held-out eval 不涨 = 被 hack 的第一告警；配 top-reward rollout 人工抽查 + CoT monitor 离线扫描。

</details>

## 常见坑（checklist）

- [ ] 把 agentic RL 讲成"RLHF 换个环境"——RLVR 的本质区别是 reward 是 ground-truth verifier 而非 learned proxy。
- [ ] reward 只有 task success 一项——没有 compliance / efficiency 分量，等于邀请 hack。
- [ ] 讲 GRPO 说不出"为什么能砍 value network"——组内相对 advantage 免掉 value 训练；长序列 credit assignment 下 value 尤其难训。
- [ ] 被问 on-policy 下 ratio ≠ 1 就说"有 bug"——先排除设计内偏差：推理引擎与训练器 forward 数值不一致、每 batch 多次 optimizer step（Anthropic GRPO debug 轮核心追问）。
- [ ] 声称 RLVR 免疫 reward hacking——verifier 自身有洞（测试可写、打分函数可 patch）时照样被 hack。
- [ ] multi-turn 训练不 mask 工具输出 token——ratio 对环境 token 无定义、梯度爆炸，且等于教模型幻觉工具结果。

## 自学资料

按优先级排序，标注读什么与预计时间：

1. [DeepSeekMath: Pushing the Limits of Mathematical Reasoning in Open Language Models](https://arxiv.org/abs/2402.03300) — GRPO 原始出处；只读 §4：目标函数推导、与 PPO 的关系、outcome vs process supervision · 30 min
2. [DeepSeek-R1: Incentivizing Reasoning Capability in LLMs via Reinforcement Learning](https://arxiv.org/abs/2501.12948) — 大规模 RLVR 实践：rule-based reward 设计、为何明确弃用 neural RM、R1-Zero→R1 的完整 pipeline · 40 min
3. [Tülu 3: Pushing Frontiers in Open Language Model Post-Training](https://arxiv.org/abs/2411.15124) — RLVR 命名出处；重点读 RLVR 章节的 verifier 构造与可验证 prompt 数据集 · 30 min
4. [From shortcuts to sabotage: natural emergent misalignment from reward hacking (Anthropic)](https://www.anthropic.com/research/emergent-misalignment-reward-hacking) — 生产 RL 环境 hack→misalignment 泛化 + inoculation prompting，Q2 最硬的实证弹药 · 25 min
5. [Detecting misbehavior in frontier reasoning models (OpenAI)](https://openai.com/index/chain-of-thought-monitoring/) — CoT monitoring 抓 hack 的方法与"优化 CoT 导致 obfuscation"负结果；配套论文 [arxiv 2503.11926](https://arxiv.org/abs/2503.11926) · 20 min
6. [TRL GRPOTrainer docs](https://huggingface.co/docs/trl/grpo_trainer) — GRPO 变体工程全景：loss_type 家族、scale_rewards、token vs sequence importance sampling，每个开关都注了出处论文 · 25 min
7. [Agentic RL: Token-In, Token-Out Done Right (HF blog)](https://huggingface.co/blog/huggingface/tito) — multi-turn 的 retokenization/loss mask 坑，为什么必须 token 进 token 出 · 20 min
8. [verl (GitHub)](https://github.com/volcengine/verl) — 生产级 RL 框架；读 README + multi-turn/agent loop 文档，理解 hybrid controller 与 rollout/train 共卡 · 30 min
9. [OpenRLHF (GitHub)](https://github.com/OpenRLHF/OpenRLHF) — Ray+vLLM 分离式架构与 REINFORCE++；对照 verl 看资源编排的另一种取舍 · 15 min
10. [Sycophancy to subterfuge: Investigating reward tampering (Anthropic)](https://www.anthropic.com/research/reward-tampering) — 早期实证：从谄媚逐级泛化到篡改自己的 reward 函数 · 15 min
