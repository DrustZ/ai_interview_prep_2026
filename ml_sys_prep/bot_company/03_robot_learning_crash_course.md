# 03 · Robot Learning 一天速成（写给 LLM post-training 背景的你）

> 用法：先读 TL;DR 和 §0 映射表（20 分钟），再按 §2 post-training → §5 evaluation → §3 动作表示 → §1 谱系 → §4 数据 的顺序读（这是按「面试被问概率」排的）。每个概念都配了一句能直接说出口的英文。最后用 §6 的 15 道 quiz 自测。

---

## TL;DR — 只有 20 分钟就看这段

1. **一句话总纲**：过去三年 robot learning 完成了「LLM 化」——VLA (vision-language-action) 模型 = 拿 VLM 当 base model，把机器人动作当一种新输出模态，走 pretrain → SFT → RL 的 post-training 流水线。你的技能栈迁移度极高。
2. **三个关键差异**：(a) 没有「机器人的互联网」，数据要自己采，数据工程 > 算法；(b) 动作是连续、高频（20–50Hz+）、有物理后果的，延迟和安全是一等公民；(c) 评估没有 ground truth 文件，每次 eval 都是一次物理实验。
3. **术语翻译**：机器人圈说的 "post-training / fine-tuning" ≈ 你的 SFT；behavior cloning (BC) = 在遥操作演示上做 supervised fine-tuning；compounding error = exposure bias 的物理放大版。
4. **动作表示三条路**：离散 token（RT-2/OpenVLA，慢且量化伤精度）→ diffusion policy（表达多模态动作分布）→ **flow matching**（π0 路线，当前一线主流）。Action chunking = 一次预测未来 50–100 步，类比多 token 预测。
5. **延迟矛盾的标准解**：双系统/分层架构——大 VLM 低频出语义（7–9Hz），小策略高频出动作（200Hz+），Figure Helix 02 甚至有 1000Hz 的 System 0。
6. **RL fine-tuning 是 2026 最热战场**：真机 RL 的里程碑是 π*0.6/RECAP（advantage-conditioned offline RL，吞吐翻倍）；机器人版 RLHF 不是 pairwise preference，而是**人类接管纠正 (intervention/correction)**。
7. **Evaluation 是全行业公认未解难题**：一次 rollout 数分钟 + 人工 reset，方差大、不可复现，且 **validation action MSE 与真机成功率脱钩**（没有 validation loss 可看）——这是 LLM 人最不适应的一点，也是你最能建立话语权的地方。
8. **当前第一梯队**：Physical Intelligence（π0→π0.7，领域的 OpenAI）、Figure Helix、NVIDIA GR00T、Google DeepMind Gemini Robotics。格局分「robot brain 实验室」vs「机器人 OEM」两条线。
9. **面试定位**：把自己卖成「post-training + evaluation 的人」，这两块 2026 年刚起爆、方法论未收敛、恰好是你的主场。
10. **一句英文总纲（开场可用）**："Robot learning has converged on the LLM recipe—a VLM backbone, behavior cloning as SFT, and RL fine-tuning on top—but the bottlenecks are different: data has to be collected physically, inference runs under hard real-time constraints, and every evaluation is a physical experiment."

---

## §0. LLM → Robotics 概念映射表（先看这个，这是你最快的学习路径）

读法：左列是你已经会的，右列是它在机器人世界的名字。面试时主动做这种映射会非常加分——它证明你能快速迁移。

| LLM 概念 | Robotics 对应物 | 备注 |
|---|---|---|
| Base model | VLM backbone（PaliGemma / Qwen-VL / Cosmos-Reason） | web 知识免费继承 |
| Pretraining corpus | 数据金字塔：OXE 跨本体数据 + 人类视频 + 仿真 | 总量比文本少 **5–6 个数量级** |
| Continued pretraining | 跨本体 robot pre-training | 本体 ≈ 语言，跨本体迁移 ≈ 跨语言迁移 |
| Tokenizer | action tokenizer（256-bin 离散化 / FAST 的 DCT+BPE），或干脆换连续 head | diffusion/flow head = 放弃离散化 |
| Next-token prediction | next-action-chunk prediction（BC 的训练目标） | |
| **SFT** | **Behavior cloning on teleop demos** | 机器人圈把这步叫 "post-training/fine-tuning" |
| Instruction tuning | 语言条件化的多任务 BC | |
| SFT 数据质量筛选 | 演示筛选 / operator 一致性管理 | 同样 quality >> quantity |
| Catastrophic forgetting → replay | 与 web VQA 数据 co-training（π0.5 明确这么做） | |
| **RLHF** | **RL from human interventions/corrections**（HIL-SERL、RECAP、RLIF） | pairwise preference 被「接管纠正」取代 |
| Reward model | 学到的 value function / success detector / VLM-as-judge | |
| DPO | GRAPE 等 trajectory preference optimization | 存在但小众 |
| RLAIF | VLM 给 rollout 打分当奖励 | 兴起中 |
| RLVR（可验证奖励） | sim RL 的 task success reward；真机自动成功检测 | 「verifiable」在物理世界反而稀缺 |
| Online RL from production traffic | fleet-scale offline-to-online（LWD）；部署即采数的数据飞轮 | |
| **Exposure bias / OOD** | **Compounding error / distribution shift**（BC 的头号病） | DAgger ≈ 迭代式 SFT-on-failures |
| Hallucination | OOD 状态下自信执行错误动作（幻觉出不存在的抓取点） | 后果是物理的、不可撤销 |
| Long context | Observation history——反直觉：主流 VLA 只看 1–2 帧，近似马尔可夫 | 长记忆是开放问题 |
| Prompt engineering | 任务指令 + 执行 metadata + 视觉子目标条件化（π0.7 的 steering） | |
| Chain-of-thought | Embodied CoT、Gemini-ER 的 think-before-act、π0.5 的语义子任务预测 | |
| 多 token 预测 / speculative decoding | **Action chunking (ACT)** + real-time chunking | 摊薄推理延迟 |
| 推理延迟优化 | 分层双系统（System 2/1/0）、端侧蒸馏 | 延迟约束硬得多：50–1000Hz |
| 大小模型蒸馏 | System 2 → System 1 蒸馏；sim 特权 teacher → 视觉 student | |
| LoRA / 少样本适配 | 50–100 条演示适配新任务/新本体（Gemini On-Device 卖点） | |
| Temperature / 采样 | diffusion/flow 的噪声注入与随机策略 | 多模态动作分布是刚需 |
| Eval benchmark | sim：LIBERO / SimplerEnv；真机：RoboArena (Elo)、RoboChallenge | 没有 HELM 级统一标准 |
| Chatbot Arena | RoboArena（多实验室分布式双盲真机 A/B） | |
| **Validation loss 选 checkpoint** | **不存在可靠对应物**——action MSE 与成功率脱钩 | LLM 人最大的不适应点 |
| Benchmark 过拟合 | LIBERO 刷分已饱和、sim-benchmark hacking | 同样的病 |
| Reward hacking | offline RL 的 OOD 价值高估；真机「假成功」骗过 success detector | |
| Guardrails | 力/扭矩限幅、protective stop、运行时监控层 | 硬件级兜底，不靠模型 |
| Agent 多轮 RL / long-horizon | 移动操作长横任务；高层规划器编排低层技能 | 你的 agent RL 经验最直接可用处 |
| Scaling laws | 操作数据 scaling laws（Generalist GEN-0 的主打叙事） | 尚无 Chinchilla 级共识 |
| World model / LLM-as-simulator | DreamZero / GR00T N2、Genie 系 latent action | 2026 年最热的架构叙事 |

**面试怎么说（映射能力展示）**：
> "Coming from LLM post-training, I found the mapping surprisingly clean: behavior cloning is SFT on teleoperated demos, compounding error is exposure bias with physical consequences, and the robotics version of RLHF is learning from human interventions rather than pairwise preferences—because when a policy is about to fail, an operator just takes over, and that takeover is simultaneously a negative label and a corrective demonstration."

---

## §1. VLA 谱系一页纸

### 奠基线（2022–2024）

| 模型 | 机构/年份 | 动作表示 | 一句话亮点 |
|---|---|---|---|
| **RT-1** | Google, 2022 | 离散 token | 第一个证明「大 transformer + 13 万条真机演示」可行；35M 参数，谈不上语言理解 |
| **RT-2** | Google DeepMind, 2023 | 动作当文本 token | 「VLA」一词来源；直接 co-fine-tune VLM，首次展示 web 知识迁移到操作任务 |
| **Octo** | Berkeley, 2024 | diffusion action head | 第一个开源通才策略（27M/93M），训练在 Open X-Embodiment 上，证明跨本体正迁移 |
| **OpenVLA** | Stanford/Berkeley, 2024 | 每维 256-bin 离散 | 第一个完全开源 7B VLA（Llama-2 底座，970k OXE episodes），至今学术默认 baseline；后续 OpenVLA-OFT 改成并行解码 + chunking + 连续 L1 回归，速度成功率双升——这次改动本身就说明了离散 token 化的局限 |

### 当前第一梯队（截至 2026-08）

| 模型 | 机构/时间 | 动作表示 | 一句话亮点 |
|---|---|---|---|
| **π0** | Physical Intelligence, 2024-10 | **flow matching**，50Hz 动作块 | 范式定义者：PaliGemma 3B + 300M action expert；叠衣服 demo 出圈；已开源 (openpi) |
| **π0.5** | PI, 2025-04 | 同上 + 分层推理 | 开放世界泛化：进从未见过的厨房/卧室做清洁；先输出语义子任务再执行；与 web 数据 co-training 防遗忘 |
| **π\*0.6 / RECAP** | PI, 2025 末 | flow matching + advantage-conditioned offline RL | **真机 RL post-training 里程碑**：demos → 人类纠正 → 自主经验，咖啡机/叠衣/纸箱任务吞吐量翻倍；同期融资 $600M |
| **π0.7** | PI, 2026-04 | 同上 + 多样化上下文条件化 | **当前最新**：单一通才追平 RL 特调专家（π\*0.6），组合泛化 + 跨本体迁移——「通才吃掉专家」叙事 |
| **Helix / Helix 02** | Figure, 2025-02 / 2026-01 | S2 (7B VLM, 7–9Hz) → S1 (80M, 200Hz)；02 加 **S0 (10M, 1000Hz 全身力控)** | 双系统代表 + 垂直整合；S0 替换大量手写 C++ 控制代码（"10.9 万行"口径未证实）；演示 8 小时自主分拣班次 |
| **GR00T N1.7** | NVIDIA, 2026-04 GA | flow matching / diffusion transformer 头 | 开源人形基础模型 + 全套 sim/数据工具链（Isaac Lab, Cosmos）；预训练含 2 万小时 EgoScale 人类第一视角视频；**N2**（2026 底）将是 world-action model（DreamZero） |
| **Gemini Robotics 2** | Google DeepMind, 2026-07 | 大脑 (ER 云端推理) + 小脑 (VLA/On-Device 本地执行) | 三件套；whole-body intelligence（Apollo 2 从脚到指尖）；数小时适配全新本体；可全设备端运行 |

### 2026 新玩家速记（一句话即可）

- **Skild AI**：omni-bodied 一脑控多机；后期大额融资、估值数十亿美元级（具体轮次金额未证实，面试别报具体数）。
- **Generalist AI**（ex-DeepMind）：GEN-0，主打操作数据 scaling laws，数十万小时自采数据。
- **Sunday Robotics**：不用 teleop，用「skill capture 手套」采人类数据（创始人是 ACT/Diffusion Policy 一作）。
- **1X NEO**：$20k（或 $499/月）家用人形，2025-10 开启预订、2026 年交付（具体量产节奏口径不一，未证实；01 记作 "2026 底交付"）——消费级真机数据飞轮开始转。
- **格局判断**：「机器人 OEM（Figure/1X/Unitree）」vs「robot brain 实验室（PI/Skild/DeepMind/NVIDIA）」，类似手机 OEM vs OS。

**面试怎么说（谱系一句话）**：
> "The field's trajectory is basically RT-2 proving that VLMs can output actions as tokens, pi-0 replacing tokens with flow matching for smooth high-frequency control, and then 2025–26 being about RL post-training on real robots—RECAP doubled throughput on real tasks, and pi-0.7 showed a single generalist matching RL-specialized experts, which is the same generalist-eats-specialist story we saw in LLMs."

---

## §2. Robot Post-Training 全流程（逐段对照你的技能栈）

这是你面试的主战场。每个 stage 都按「LLM 里你怎么做 → 机器人里怎么做 → 差异在哪」展开。

### Stage 0 — Base model：拿 VLM 白嫖 web 知识

拿现成 VLM（PaliGemma、Qwen-VL、Cosmos-Reason）当起点。语义理解、OCR、常识空间关系全部免费继承——这就是为什么 VLA 能听懂 "put the coke can next to the apple" 而不需要机器人数据里出现过可乐罐。

> "The VLM backbone gives you web-scale semantics for free—the robot data only needs to teach the model how to move, not what things are."

### Stage 1 — Robot pre-training ≈ continued pretraining / mid-training

在跨本体大杂烩（OXE + 自采 + 人类视频 + 仿真）上训练动作预测。π0 配方约 1 万小时多样数据。**关键工程点：与 web VQA 数据 co-training 防止 VLM 能力灾难性遗忘**（π0.5 明确这么做）——就是你熟悉的 replay/data mixing，配方思路完全同构。

> "Cross-embodiment pre-training is like multilingual pretraining—each robot body is a 'language,' and you co-train with web VQA data to prevent catastrophic forgetting of the VLM's semantic abilities."

### Stage 2 — SFT = Behavior Cloning on demonstrations

**术语排雷**：机器人圈把这一步叫 "post-training" 或 "fine-tuning"，本质就是 SFT——在目标任务的高质量遥操作演示上做监督学习，目标是 next-action-chunk prediction。

和 LLM 相同的规律：**数据质量 >> 数量**。演示的一致性、operator 的操作水平直接决定策略上限；50–100 条演示即可完成任务适配（Gemini On-Device 的卖点，对应你熟悉的少样本 LoRA 适配）。

**BC 特有的病：compounding error / distribution shift**。策略执行时一旦有小偏差，就进入演示里没见过的状态，在 OOD 状态下犯更大的错，错误滚雪球。这是 exposure bias 的物理放大版——LLM 里跑偏了大不了生成一段烂文本，机器人跑偏了会把杯子扫到地上，而且回不去了。

缓解手段（按面试出现频率）：
1. **DAgger**：策略上线跑，专家对它到达的（偏离）状态标注正确动作，加回训练集迭代——本质是 iterated SFT on the policy's own failure states。
2. **Action chunking**：减少决策次数，误差累积更慢（见 §3）。
3. **根治方案：RL**（见 Stage 3）。

> "Behavior cloning's fundamental failure mode is compounding error: one small deviation puts the policy in a state the demos never covered, and errors snowball—it's exposure bias, except the consequences are physical and irreversible. DAgger mitigates it by iteratively collecting expert labels on the states the policy actually visits."

### Stage 3 — RL fine-tuning：2026 年的最热战场

**Sim RL**：locomotion 的标准答案。Isaac Gym 万级并行环境 + PPO，几小时训出四足/人形行走；用「特权信息 teacher → 视觉 student」蒸馏后 sim2real 直接部署。**但 manipulation 在仿真里做 RL 再迁移仍不可靠**（原因见 §4）。

**Offline RL**：CQL/IQL/AWAC 一脉，在固定数据集上学超越演示者的策略；痛点是分布外动作的价值高估——**reward hacking 的离线版**。

**RLPD**（RL with Prior Data）：真机 RL 的实用配方——SAC + 每个 batch 一半采 offline demos、一半采 online 经验，样本效率高到真机上一两小时学会插接件。衍生的 **HIL-SERL** 加人类实时接管纠正，真机成功率能推到 ~100%。

**Residual RL**：冻结 BC 基座，RL 只学修正量 delta——安全稳定，2026 年还被用来给 VLA 自产训练数据。

**真机 RL 四大难（必背，面试大概率追问）**：
1. **Reset**：谁把杯子放回去？需要人力或 reset-free RL。
2. **Reward**：没有 verifiable reward；VLM-as-judge 判成功正在兴起（≈ RLAIF）。
3. **安全探索**：随机动作会砸东西，探索必须受限。
4. **样本贵 + 环境非平稳**：物体磨损、光照变化，环境自己在漂移。

> "Real-robot RL has four hard problems that don't exist in LLM RL: resets require physical labor, rewards aren't verifiable so people are turning to VLM-as-judge, exploration has to be safe because random actions break things, and samples are expensive in a non-stationary environment."

**2026 前沿（点名即可加分）**：
- **RECAP / π\*0.6**：advantage-conditioned offline RL，统一吸收演示、人类纠正、自主经验三种数据，真机吞吐翻倍。方法论上 ≈ conditional SFT / RCSL（advantage conditioning），你可以直接对上。
- **π0.7**：把 RL 特调专家的经验数据回灌通才模型——RL 产出的数据成为下一代通才的语料。
- **SimpleVLA-RL**（ICLR 2026）：GRPO 式 online RL 直接调 VLA。
- **ReinFlow / πRL**：穿透 flow matching 策略做 RL 的技术路线（flow 策略的 log-prob 不好算，是技术难点）。
- **LWD**：fleet-scale offline-to-online——整个机器人车队的 rollout + 人类干预进共享 replay buffer，训完重新下发。机器人版「从生产流量持续学习」。

### Stage 4 — RLHF 的类比：Intervention 取代 Preference

机器人领域**最主流的人类反馈不是 pairwise preference，而是「接管纠正」(intervention/correction)**：操作员看策略跑偏就抢过手柄。接管这个动作本身 = 天然负信号 + 正确示范，一石二鸟（HG-DAgger、RLIF、HIL-SERL、RECAP 全走这条路）。

为什么？机器人失败肉眼可见、纠正即演示，比让人对比两段视频高效得多。纯 preference 路线存在但小众：老一代 PEBBLE/T-REX，新一代 **GRAPE**（对 VLA 轨迹做 DPO 式 trajectory preference optimization）。

**RM 的对应物**：学到的 value function / success classifier + 新兴的 VLM-as-reward-judge。

> "In robotics, RLHF becomes 'RL from human takeover': instead of ranking two trajectories, an operator intervenes when the policy drifts, and that intervention gives you both a failure label and a corrective demonstration in one shot—strictly more information per unit of human time."

---

## §3. 动作表示与双系统架构（这个领域的「tokenizer 之争」）

**问题设定**：动作 = 连续向量（7-DoF 臂：6 维末端位姿增量 + 1 维夹爪），要以 20–50Hz 输出。怎么让一个 transformer 输出它？三条路线：

### 路线一：离散 action tokenization（RT-2 / OpenVLA）

每个动作维度离散成 256 个 bin，动作变成「词」，完全复用 LLM 的自回归 + cross-entropy。
- 优点：无缝接入 VLM。
- 三宗罪：(a) 自回归逐 token 太慢；(b) 高频连续信号离散化后相邻 token 高度相关、学习效率低；(c) 量化误差伤精细操作。
- 改进版 **FAST**（π0-FAST）：动作序列先 DCT 变换到频域再压缩编码（类比 BPE 之于字符），token 数降一个量级——「为连续信号设计更好 tokenizer」的代表作。

### 路线二：Diffusion Policy（Chi et al. 2023）

用去噪扩散生成动作块。**核心直觉（必须讲得出）**：同一个状态下「从左绕开障碍」和「从右绕开」都是对的——演示数据里两种都有。如果用回归 loss（MSE/L1），模型会学出两者的平均：**径直撞上去**。扩散模型学的是完整的多模态分布，采样时会 commit 到其中一个 mode，不会平均。

这对应 LLM 里「为什么用采样而不是逐位平均」的直觉，但在连续动作空间这个问题是致命的而非风格性的。缺点：多步去噪推理慢。

> "Diffusion policies exist because demonstrations are multimodal—going left and going right around an obstacle are both valid, and a regression loss would average them into driving straight into it. Diffusion learns the full distribution and commits to one mode at sampling time."

### 路线三：Flow Matching（π0 路线，当前一线主流）

直觉版：diffusion 的连续正规化流亲戚——学一个从噪声到目标动作的「直线化」速度场，训练更简单，积分步数更少（推理更快），天然输出连续值。π0 架构 = 「VLM backbone + 小 action expert（类 MoE 的注意力路由接入）」——**可以理解为：语义住在离散 token 空间，动作住在连续空间，各用各的头**。GR00T 亦用 flow matching / diffusion transformer 头。

> "Flow matching is diffusion's faster cousin: instead of many denoising steps, you learn a velocity field that transports noise to the action in a few integration steps—which matters when you need 50Hz control."

### Action Chunking（ACT, Zhao et al. 2023）

一次预测未来 k 步（50–100 步）动作块而非单步。三个动机：
1. Teleop 演示是非马尔可夫的（人有意图延续性），单步 BC 学不好；
2. 减少决策次数 → 缓解 compounding error；
3. **摊薄推理延迟**——一次前向产出一段，边执行边算下一段。

ACT 还加 temporal ensembling（重叠块加权平均）平滑动作。LLM 类比：多 token 预测 / speculative decoding。

> "Action chunking predicts the next 50 to 100 actions in one forward pass—it amortizes inference latency, reduces the number of decision points where errors can compound, and matches the non-Markovian structure of human demonstrations."

### 双系统架构：50Hz vs LLM 延迟的标准解

矛盾：3B+ VLM 一次前向 100ms–1s，但控制回路要 20–50Hz，人形全身要 200–1000Hz。所有一线玩家殊途同归到**分层/双系统**：

| 玩家 | 架构 |
|---|---|
| Figure Helix 02 | S2（VLM，7–9Hz，语义 latent）→ S1（80M，200Hz，动作）→ S0（10M，1000Hz，全身力控） |
| π0.5 | 同一模型两种推理模式：低频输出语义子任务（离散 token）→ 高频 flow matching 出动作块 |
| Gemini Robotics | ER（云端大模型规划/编排）+ VLA / On-Device（本地执行） |

补充技巧：action chunk 在两次重规划之间开环执行；**real-time chunking**（异步推理，新块与旧块执行重叠拼接）；蒸馏到端侧小模型。

类比：System 2/1 ≈ 深思模型 + 快速草稿模型；chunk 开环执行 ≈ 一次生成一段再重新进 context。

> "Everyone converged on the same answer to the latency problem: a slow VLM thinks at a few hertz and emits semantic intent, a small policy runs at hundreds of hertz to execute it, and action chunks bridge the gap by executing open-loop between replans."

---

## §4. 数据来源与 Sim2Real

### 数据金字塔（越往上越贵越对口）

**1. 真机遥操作（塔尖，最贵最有效）**
- **ALOHA / ALOHA 2**：~$30k 内的双臂 leader-follower 套件，人拉「主臂」示范、「从臂」复现；ACT 是配套算法；Mobile ALOHA 扩展到移动操作。
- **DROID**：13 个机构、564 个场景、76k episodes——重点是**场景多样性**而非单场景量。
- 降本新方式：UMI 手持夹爪（不需要机器人在场）、外骨骼、Sunday 的数据手套。
- **成本直觉（面试可引用）**：一小时高质量 teleop ≈ 数十美元人力；全行业真机数据总量 ≈ 万–十万小时量级，对比文本万亿 token，**差 5–6 个数量级**。

**2. 人类第一视角视频**（量大但有 embodiment gap）：Ego4D、NVIDIA EgoScale（N1.7 用了 2 万小时）。用法：学 affordance/视觉表征、latent action models（从视频无监督推断「伪动作」当预训练目标，Genie/LAPA/DreamZero 一脉）、动作重定向。

**3. 仿真 + 合成数据**：Isaac Lab、MuJoCo/MJX、ManiSkill、RoboCasa、Genesis；MimicGen 从少量真实演示程序化增殖千倍仿真演示；NVIDIA 用 Cosmos world model 生成视频级合成数据。

**4. Cross-embodiment 聚合**：**Open X-Embodiment (OXE)**——22 种机器人、100 万+ 轨迹；RT-X 证明跨本体训练比单本体正迁移。难点是动作空间/相机视角/控制频率异构，处理方式从「各配一个 head」到「统一末端位姿空间」到 π0.7 式「metadata 条件化」。

> "There is no internet of robot actions—the entire industry's teleop data is on the order of tens of thousands of hours, five to six orders of magnitude less than text. That's why data engineering beats algorithms here, and why everyone builds a data pyramid: expensive teleop at the top, human video and simulation filling the bulk underneath."

### Sim2Real

- **Domain randomization**：训练时随机化视觉（纹理/光照/相机）+ 动力学（质量/摩擦/延迟/电机参数），逼策略对「真实世界只是分布中一个样本」鲁棒。类比：数据增广 + 对抗鲁棒性训练。
- **System identification**：反向标定仿真参数贴合真机；legged robotics 的杀手锏是 **actuator net**——小网络学真实电机的非线性响应，替代解析模型。
- **为什么 locomotion 赢了、manipulation 还没有（高频考点）**：
  - Locomotion：脚-地接触结构简单、观测以本体感知为主（仿真几乎免费精确）、奖励好写（前进速度）、误差可被反馈控制吸收 → 已被「大规模并行 sim RL + 蒸馏」彻底解决（Figure 的 S0 行走控制器同样出自仿真训练）。
  - Manipulation：接触丰富的动力学（摩擦/柔性物体/衣物/线缆/液体在仿真里根本不保真）、感知 gap（毫米级几何、透明/反光物体）、任务长横、奖励难定义、误差不可自愈（杯子掉了就是掉了）。
- **新趋势**：real2sim（3D 高斯泼溅扫描真实场景建数字孪生，RL 后回真机）；sim+real co-training（仿真当「便宜的多数」、真机当「昂贵的锚点」）；用 world model 替代仿真器（GR00T N2/DreamZero——学出来的仿真器没有手写物理引擎的保真度天花板）。

> "Sim-to-real is solved for locomotion but not manipulation: walking has simple foot-ground contact, proprioceptive observations, and an easy reward, so massively parallel sim RL plus distillation just works. Manipulation breaks simulators—friction, deformables, and liquids aren't faithful, perception gaps are at millimeter scale, and a dropped cup can't be recovered by a feedback controller."

---

## §5. Policy Evaluation：全行业公认的未解难题（这个岗位大概率会聊）

对 LLM eval 出身的人，这一节既是最大文化冲击，也是你最大的卖点。

### 为什么难（四点，必背）

1. **贵**：一次 rollout 数分钟 + 人工 reset。要区分两个相差 20 个点的 checkpoint，每边要 ~50 次试验才有统计功效——一轮 eval 一整天。没有「跑一遍 MMLU」这种东西。
2. **方差大且不可复现**：光照、物体摆位、物体磨损、机器人标定漂移全是混杂变量。今天 70% 明天 50% 很常见；换个实验室完全无法复现。
3. **人为偏差**：reset 摆位时评估者可能无意识地「喂」自己的策略。
4. **Checkpoint selection 无信号**：validation action MSE 与真机成功率**相关性很差**（动作分布多模态所致）——相当于没有 validation loss 可看。这是 LLM 人最不适应的一点。

### 常见做法

- **Sim eval 当 proxy**：
  - **LIBERO**：130 个任务、四个泛化维度，学术界刷分主场，已接近饱和（出了 LIBERO-Plus 加扰动）。
  - **SimplerEnv**：专门设计来与真机表现相关的仿真复刻，分 visual matching 和 variant aggregation 两种协议。
  - 共识：**sim 分数只能看相对排序趋势，不能信绝对值**。
- **真机统计规范**：成功率 + Wilson/Clopper-Pearson 置信区间；**blind A/B**（评估者不知道在跑哪个策略）；配对试验（两策略用相同初始摆位）。
- **部署指标（工业界更信）**：**intervention rate**（每小时人工接管次数）、MTBF、吞吐量（π\*0.6 的「翻倍」就是吞吐指标）、自主时长（Figure 的 8 小时班次本质是一次公开 eval）。
- **2026 新基建**：**RoboArena**（多实验室分布式双盲真机 A/B + Elo，机器人版 Chatbot Arena，GR00T N2 引用的就是它）、RoboChallenge（大规模真机评测）、用 world model 做「免真机 eval」的探索。

### 你的经验怎么卖（准备好这段）

> "Robot evaluation is where my LLM eval background transfers most directly. The field's problems—underpowered comparisons, evaluator bias, benchmark overfitting, no reliable validation signal for checkpoint selection—are exactly the problems LLM eval went through. I'd bring the same discipline: confidence intervals on success rates, blind paired A/B protocols, sim benchmarks treated as relative-ranking proxies rather than absolute truth, and deployment metrics like intervention rate as the north star, the way production LLM teams treat online metrics over offline benchmarks."

---

## §6. 15 道自测 Quiz（先自答，再看一句话答案）

1. **What is a VLA model?**
   → A vision-language-action model: a VLM backbone fine-tuned to also output robot actions, treating action as a new output modality.

2. **Why is behavior cloning "just SFT"? What's its signature failure mode?**
   → It's supervised learning on teleop demonstrations; its signature failure is compounding error—small deviations lead to OOD states and snowballing mistakes.

3. **Why do we need diffusion/flow policies instead of a regression head?**
   → Demonstrations are multimodal (left-around and right-around are both valid), and regression averages the modes into an invalid action; generative heads commit to one mode.

4. **Flow matching vs diffusion for actions—why did π0 pick flow matching?**
   → Same expressiveness family, but simpler training and far fewer integration steps at inference, which matters at 50Hz.

5. **What is action chunking and its three motivations?**
   → Predict the next 50–100 actions per forward pass: amortize latency, fewer decision points (less compounding error), and match non-Markovian human demos.

6. **How do robots reconcile a 3B VLM's latency with 200Hz control?**
   → Hierarchical dual-system architectures: slow VLM emits semantic intent at a few Hz, small policies execute at 200–1000Hz (e.g., Helix S2/S1/S0), with chunks executed open-loop between replans.

7. **What is the robotics equivalent of RLHF?**
   → RL from human interventions: operator takeovers serve as both negative labels and corrective demonstrations (HIL-SERL, RECAP), largely replacing pairwise preferences.

8. **What is RECAP / π\*0.6 and why is it a milestone?**
   → Advantage-conditioned offline RL that unifies demos, corrections, and autonomous experience—the first convincing real-robot RL post-training recipe, doubling task throughput.

9. **What's the significance of π0.7?**
   → A single steerable generalist matched RL-specialized expert models—the generalist-eats-specialist story from LLMs replaying in robotics.

10. **Name the four hard problems of real-robot RL.**
    → Resets need physical labor; rewards aren't verifiable; exploration must be safe; samples are expensive in a non-stationary environment.

11. **Why is there "no internet of robots," and what's the data pyramid?**
    → Actions must be physically collected (total teleop data is 5–6 orders of magnitude below text); the pyramid stacks cheap-but-indirect (sim, human video) under expensive-but-direct (teleop).

12. **What is Open X-Embodiment and the cross-embodiment analogy?**
    → A 22-robot, 1M+ trajectory joint dataset; cross-embodiment training is like multilingual pretraining—bodies are languages, and transfer is positive.

13. **Why did sim2real work for locomotion but not manipulation?**
    → Locomotion has simple contacts, proprioceptive observations, easy rewards, and self-correcting errors; manipulation has unfaithful contact simulation, millimeter-scale perception gaps, and irreversible failures.

14. **Why can't you pick checkpoints by validation loss in robotics?**
    → Validation action MSE correlates poorly with real success rates because action distributions are multimodal—you have to run physical (or sim-proxy) evals.

15. **How would you make robot evaluation rigorous?**
    → Wilson confidence intervals on success rates, blind paired A/B with matched initial conditions, sim benchmarks (SimplerEnv/LIBERO) as relative-ranking proxies, and deployment metrics like intervention rate and MTBF.

---

## 附：最后一晚补课清单（来自定位建议）

1. **切入点选 post-training/RL**：RECAP → SimpleVLA-RL → LWD 这条线的方法论直接搬 LLM RL 骨架（advantage conditioning ≈ conditional SFT/RCSL、GRPO 变体、offline-to-online）。懂 RLHF 工程化的人在机器人公司是稀缺物种。
2. **第二切入点是 evaluation**：全行业没人满意现状，懂统计功效、A/B 基建、benchmark 设计的人可以直接建立话语权。
3. **常识底线名词**（能一句话解释即可，不会被深挖）：
   - **PD control**: "A feedback controller that corrects error proportionally to its magnitude and its rate of change—the workhorse of low-level joint control."
   - **MPC (model predictive control)**: "Replan a short-horizon optimal trajectory at every timestep using a dynamics model, execute the first action, repeat."
   - **Inverse kinematics**: "Solving for the joint angles that put the end-effector at a desired pose—the inverse of the forward geometry."
   - 「数据比算法值钱」的行业文化——面试里表现出你理解这一点。
4. 若有半天空档：跑一次 LeRobot/SmolVLA 或 openpi 的上手教程，面试里能说 "I've run openpi locally" 价值很大。
