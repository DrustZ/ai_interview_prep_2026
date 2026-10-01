# ML 理论 + 手写题弹药库（三家通用）

> 一份材料覆盖三家的 ML 轮：GDM fundamentals quiz、OpenAI AI coding、Anthropic RL/ML track。
> 按（定义 → 公式 → trade-off → failure mode → 实战经验）五层准备；RS 面试重点考后三层。

## 1. 二十道跨源必背理论题（≥3 个独立来源出现）

| # | 题 | 一句话答案要点 |
|---|---|---------------|
| 1 | RLHF 三阶段 | SFT → BT loss 训 RM → PPO + KL 约束优化 |
| 2 | PPO vs DPO | DPO 离线免 RM、简单稳定；PPO 在线探索、上限更高、可用 RM 泛化到新 prompt |
| 3 | PPO 四个模型 | actor / critic / RM / reference，各自作用与显存开销 |
| 4 | KL penalty / reference model 为什么必要 | 防 reward hacking + 防遗忘；两个方向的 KL 行为不同（mode-seeking vs covering） |
| 5 | GRPO 原理、与 PPO 区别 | 组内 (r−mean)/std 相对优势替代 critic；假设：同 prompt rollouts 可比、非退化；std 归一化有偏差 |
| 6 | Reward hacking 定义/实例/缓解 | Goodhart；改测试用例/迎合 RM；KL + RM 迭代 + ensemble + 过程监督。参考 [Lilian Weng](https://lilianweng.github.io/posts/2024-11-28-reward-hacking/) |
| 7 | DPO loss 手写 + β 含义 | −log σ(β·[logπ/π_ref(y_w) − logπ/π_ref(y_l)])；β = 隐式 KL 强度 |
| 8 | 拒绝采样 / RLAIF / RLVR | best-of-K 蒸馏；AI 反馈替代人类；可验证奖励（math/code） |
| 9 | o1/R1 怎么训的、R1-Zero vs R1 | 大规模 RL on 可验证任务 + 长 CoT 涌现；Zero 纯 RL 冷启动 vs R1 加 SFT 种子 |
| 10 | Attention 为何除 √d_k | q·k 方差 ≈ d_k → softmax 饱和 → 梯度消失；会推方差 |
| 11 | MHA/MQA/GQA + KV cache 计算 | KV = 2·layers·kv_heads·head_dim·bytes·seq·batch；GQA 砍 kv_heads 省显存 |
| 12 | FlashAttention 为什么快 | IO-aware：tiling + online softmax（running max/normalizer）+ backward 重计算，省 HBM 读写非省 FLOPs |
| 13 | RoPE 原理与长度外推 | 旋转使 score 只依赖相对位置；外推失败因高频带没见过全部角度 → PI/YaRN/继续训练 |
| 14 | MoE 路由/负载均衡/routing collapse | top-k gating + aux loss；容量因子；collapse 成因与解法 |
| 15 | PTQ vs QAT、AWQ/GPTQ/NF4 | 训后 vs 训中；权重量化选型、激活离群值问题 |
| 16 | LoRA/QLoRA | 低秩增量 ΔW=BA；QLoRA=NF4 底座+bf16 适配器 |
| 17 | 灾难性遗忘与缓解 | 重放/正则（KL to ref）/低 lr/数据配比 |
| 18 | SFT 后为什么还要对齐、数据配比 | SFT 学格式≠学偏好；质量>数量；你有一手经验，讲实战 |
| 19 | 显存估算 | 训练 Adam 混合精度 ≈16 bytes/param（4w+4g+8opt）；激活项与 seq 平方项何时主导 |
| 20 | 解码策略 | temperature/top-k/top-p/beam/speculative 各自机制与失败模式 |

深挖答案源：[Bojie Li 200 题](https://01.me/en/2025/04/llm-interview-questions/) · [wdndev/llm_interview_note（11.5k★，RLHF 14 问中文答案）](https://github.com/wdndev/llm_interview_note) · [aman.ai Policy/Preference Optimization](https://aman.ai/primers/ai/llm-alignment/) · [HF: PPO/DPO/GRPO guide](https://huggingface.co/blog/NormalUhr/rlhf-pipeline) · [Lilian Weng Policy Gradient](https://lilianweng.github.io/posts/2018-04-08-policy-gradient/) · [小林 74 题八股](https://xiaolincoding.com/interview/llm.html)

## 2. 手写题清单（deep-ml.com，按优先级）

公司专属合集（登录可见成员题）：[OpenAI RS](https://www.deep-ml.com/collections/OpenAI%20Research%20Scientist%20Interview%20Prep) · [Anthropic](https://www.deep-ml.com/collections/Anthropic%20Interview%20Prep) · [DeepMind](https://www.deep-ml.com/collections/DeepMind%20Interview%20Prep)；离线全题库：[开源 repo（164 题带解）](https://github.com/moe18/DML-OpenProblem)

**⭐ P0（你的方向必会，一次写对）**
- RLHF/策略优化：[#122 REINFORCE](https://www.deep-ml.com/problems/122) → [#487 GAE](https://www.deep-ml.com/problems/487) → [#485 PPO clipped loss](https://www.deep-ml.com/problems/485) → [#101 GRPO objective](https://www.deep-ml.com/problems/101) → [#224 组相对优势](https://www.deep-ml.com/problems/224) → [#225 KL 估计器](https://www.deep-ml.com/problems/225) → [#382 DPO loss](https://www.deep-ml.com/problems/382) → [#484 RM pairwise loss](https://www.deep-ml.com/problems/484)
- Attention：[#53 self-attention](https://www.deep-ml.com/problems/53) → [#107 masked](https://www.deep-ml.com/problems/107) → [#94 MHA](https://www.deep-ml.com/problems/94) → [#391 GQA]/[#390 MQA] → [#960 einsum 版](https://www.deep-ml.com/problems/960)（GDM 考 einsum）
- 采样：[#378 temperature](https://www.deep-ml.com/problems/378) → [#383 top-p](https://www.deep-ml.com/problems/383) → [#419 组合 pipeline](https://www.deep-ml.com/problems/419) → [#385 beam](https://www.deep-ml.com/problems/385)
- 数值稳定：stable softmax（[#962](https://www.deep-ml.com/problems/962)）、log-sum-exp、streaming entropy（OpenAI 原题族）

**P1（推理系统 + 训练机制）**
- KV cache：[#376 实现](https://www.deep-ml.com/problems/376) → [#418 大小估算](https://www.deep-ml.com/problems/418) → [#417 prefill/decode compute vs memory bound](https://www.deep-ml.com/problems/417) → [#492 PagedAttention](https://www.deep-ml.com/problems/492)
- 优化器：[#49 Adam](https://www.deep-ml.com/problems/49)、AdamW；损失：CE 系（含 masked CE）、[#769 DPO+NLL](https://www.deep-ml.com/problems/769)
- 归一化：LayerNorm/RMSNorm 手写（[17 题清单](https://www.deep-ml.com/problems)）；RoPE（[13 题](https://www.deep-ml.com/problems)）
- 从零搭 GPT：makemore/micrograd 系列 12 题（Karpathy 路线，OpenAI autograd 题的练兵场）

**P2（广度）**：BPE/tokenization 17 题、MoE 12 题、RL 基础（Bellman/Q-learning）19 题

## 3. 你已有的王牌材料 → 轮次映射（reflection 目录，Reflection 面试原题风格改写版）

| 文件 | 对应轮次 |
|------|---------|
| `reflection/theory-mte-quiz-and-stories.md` | **GDM quiz** 完美模拟（快问快答+深挖：硬件数量级、einsum、FSDP、显存预算） |
| `reflection/theory-ml-question-bank.md` | GDM/OAI ML 理论（pre/post-norm 梯度、attention 方差推导、RL for LM、多轮 agent 的 loss masking——快手 2026 也考这个） |
| `reflection/coding-distributed-softmax-loss.md` | OpenAI 分布式 all_gather 题 / xAI 分布式矩阵乘同族 |
| `reflection/coding-tensor-golf.md` | OpenAI 1-NN/向量化 numpy 题同族 |
| `reflection/coding-agentic-bootstrap.md` | Anthropic agent 轮 + batch inference pipeline |
| `reflection/coding-pretraining-performance-optimization.md` | 训练性能 review（各家 perf 向轮次） |
| `reflection/design-rl-on-video-game.md` | GDM ML design / RL 系统设计 |
| `reflection/case-study-rl-bottleneck.md` | 分布式 RL debug（Anthropic RL 轮的系统版） |

## 4. ML System Design 框架 + 题源

- 万能骨架：问题定义 → 数据 → 模型选型（API/finetune/distill）→ 训练 → **评估（第一等公民，你的强项）** → 部署/监控 → 迭代。约束升级练法见 gdm.md。
- LLM serving 物理学：prefill compute-bound / decode memory-bound；KV cache 数学；continuous batching；speculative decoding。
- 题源：[alirezadir ML-Interviews（23k★，9-step MLSD + 2026 GenAI 章）](https://github.com/alirezadir/Machine-Learning-Interviews) · [Chip Huyen 27 道开放题](https://huyenchip.com/machine-learning-systems-design/toc.html) · [Chip Huyen 200+ 知识题](https://huyenchip.com/ml-interviews-book/) · [Hello Interview: Design ChatGPT](https://www.hellointerview.com/learn/system-design/problem-breakdowns/chatgpt) · 书：《Generative AI System Design Interview》(ByteByteGo, 2024)
