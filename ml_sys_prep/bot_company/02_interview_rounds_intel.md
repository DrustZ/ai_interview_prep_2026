# 02 — 轮次形式与情报（The Bot Company Onsite, 13:00–17:00）

> 事实来源纪律：本文关于 The Bot Company 的全部事实来自 2026-08-08 调研简报（Ashby JD 全文、CTO 推文、媒体报道）。凡是推断均标注。公开面经为零，所以「轮次配置」一节全部是推断，但推断链条已写明。

---

## TL;DR — 只有 20 分钟就看这段

1. **公开面经 = 零。** Glassdoor / Blind / Reddit / 一亩三分地 / X 全部交叉搜过，没有任何一篇 The Bot Company 面经。别再去搜了，时间花在下面的推断和练习上。
2. 但 JD 里有罕见的官方剧透："Throughout the process, we expect candidates to demonstrate: exceptional mental acuity / engineering curiosity / high performance mindset" —— **考快速思考、跨域推理、高压表现，不考背题**。预期节奏快、追问密、可能故意丢不熟悉领域的问题。
3. 最可能配置（概率 ~50%）：**实战 ML coding/debug（60–75min）→ 项目 deep-dive（60–75min）→ founder/开放设计（30–60min）**。4 小时 2–3 轮 ⇒ 每轮 60–90 分钟，全是深挖式；「常提前结束」最合理解释是**单轮否决制**（推断）——每一轮都是生死轮。
4. 面试官母体 = Cruise + Tesla 系。他们会用 **Tesla data engine 思维**（数据闭环、corner case 挖掘、eval 驱动迭代）审你的 post-training 经历。CTO Paril Jain 招聘推文单独点名 "scaling models **and evals**" —— **eval 方法论几乎必考**。
5. 同类公司（Skild）的评价哲学："**Hand-wave and you're done**"。说 domain randomization 会被追问随机化了哪些参数、什么范围。每个论断都要能落到参数、数字、具体实验。
6. 三大备战优先级：① 最硬的 post-training 项目按「failure mode → 诊断手段 → data/eval 改动 → 量化增益」四段式打磨到能被追问 30 分钟；② PyTorch 训练循环 debug + 向量化数值题（Skild 样题 + 手写 attention）；③ 一套「家用机器人 post-training 数据引擎 + eval 体系」开放设计答案。
7. Culture/founder 轮的正确姿势：聊 **high agency、IC ownership、in-person、愿意下场碰硬件**；**绝对不要聊晋升/带人/管理轨道**（公司明文 "Everyone is an IC"，Vogt 公开反层级）。
8. 「为什么是家用机器人、为什么是现在」要有真诚答案——Vogt 明言不卖公司、要长期做，founder 轮会测使命认同。
9. 判别信号：**如果 recruiter 提前让你准备任何材料（slides），Tesla 式 presentation 情景立刻升为第一**，当晚就做 30 分钟 slides。
10. 当天节奏：12:15 前吃完轻午餐 + 咖啡因，每轮间隙 2 分钟重置（水 + 深呼吸 + 翻一眼 cheat sheet），把「提前结束」当中性信号处理，最后一轮（16:00+）血糖低谷靠 snack 顶住。

---

## 1. 直接面经汇总：明说，没有

**结论先行：截至 2026-08-08，公开渠道不存在任何一篇 The Bot Company 候选人面经或员工评论。** Glassdoor 无公司页面，Blind 无公司帖，一亩三分地无 tag，Reddit / X 多关键词交叉搜索无结果。这与公司状态一致：~94 人、拒绝一切 PR、招聘大概率靠 Tesla/Cruise 校友内推，样本极少且都不发帖。

**所以本文的情报结构是：一手官方材料（少但含金量高）+ 类比公司面经（多且风格高度相关）+ 推断（标注）。**

### 一手材料 → 面试含义对照表

| 一手材料（verbatim 或实证） | 对面试的直接含义 |
|---|---|
| JD 通用段："Throughout the process... exceptional mental acuity / engineering curiosity / high performance mindset" | 官方剧透面试哲学：快速思考、跨域推理、高压表现。预期追问密集、可能故意给你不熟的领域 |
| Multimodal Foundation Models JD："Pretraining & RL Mastery... post-training... RL at scale" | post-training 直觉是核心深挖点，不是加分项 |
| 同一 JD："Own the Training Loop End-to-End... diagnosing failure modes, improving data mixtures, and tightening evaluation" | 这一句就是 deep-dive 轮的提纲：failure mode 诊断、data mixture、eval——你的项目故事必须按这三个词组织 |
| 同一 JD："Ship and Iterate on Real Systems... edge inference"；"Very strong coding skills in Python, C++, or Rust" | 会问真机部署/推理优化；coding 轮语言以 Python 为主但可能碰 C++ 话题 |
| CTO Paril Jain 推文："High agency to get shit done"；"Scaling models **and evals** for robot learning"；"sim2real for control" | evals 被 CTO 单独点名 → 聊 post-training 时 eval 方法论几乎必考；sim2real 是他们的日常语言 |
| "Something Else" 通用岗 + 所有 JD 的 "work across the stack" | generalist 优先。表现出对硬件/固件/感知的好奇心是加分，说「这不是我的方向」是减分 |
| SF Standard 报道：员工假扮游客租 Airbnb 秘密测试原型机（设备箱、贴墙线缆、连机器人的笔记本，3 人刷了 12+ 个 Airbnb） | field ops = 工程师自己拎笔记本进真实住宅调机器人。「现场机器人行为异常，你怎么从数据定位」类题概率高，且他们要确认你**愿意干这种活** |
| Vogt："I don't think you have to walk more than 10 feet... to go from your desk to running code on a robot"；"Everyone is an IC... massive scope, radical ownership" | culture 轮的标准答案方向：in-person、快迭代、IC ownership、无层级 |

---

## 2. 最可能的 2–3 轮配置推断（13:00–17:00）

**先读约束（推断的根基）：** 4 小时窗口 / 2–3 轮 ⇒ 每轮 60–90 分钟，明显长于大厂 45 分钟制。长轮次几乎必然意味着**深挖式（deep-dive / practical）而非题库式**。「通常提前结束」最合理解释是**单轮否决制**（每轮后同步拍板，不行就送客；行的话 founder 轮可 20 分钟收尾）——没有「走完流程」的缓冲，**每一轮都是生死轮**（推断）。

| 情景 | 概率 | 轮次结构 | 依据 |
|---|---|---|---|
| **A：三轮标准式** | **~50%** | ① 实战 ML coding/debug（60–75min）② 项目 deep-dive（60–75min）③ founder/culture + 开放设计（30–60min，常被砍短） | 与 Cruise 3 轮制（coding / design / BQ）同构；JD 三条能力项一一对应；三个 ML 岗 JD 都强调 "Own the Training Loop End-to-End" |
| **B：两轮长 practical** | **~30%** | ① 现场数据/日志分析 debug（~2h pair session）：给真机 log 或训练数据，定位「为什么抓取失败 / 为什么不收敛」② deep-dive + founder 合并轮（~1.5h） | 「2 轮」下限的存在说明可能走大块 practical；Figure 的 case-study-to-panel 模式；90 人公司没有专职面试官，倾向「直接看你干活」；提前结束 = practical 半小时内见分晓 |
| **C：Tesla 式 presentation 开场** | **~20%** | 自带 slides 讲过往工作 30–45min + Q&A → coding 一轮 → design/culture 一轮 | Tesla Autopilot onsite 标准打法（presentation + coding + design），面试官一半 Tesla 系。压低概率：stealth 公司要求外部候选人备 slides 会泄露关注方向，且 4 小时塞 presentation 偏紧 |

**情景切换信号：**
- recruiter 提前要求准备任何材料 → C 升为第一，立刻做 slides（30 分钟版：1 页背景、3 页最硬项目按四段式、1 页「为什么家用机器人」）。
- 邮件里出现 "pair session" / "bring your laptop" / "working session" 字样 → B 升为第一。
- 什么都没说 → 按 A 准备，A 的准备内容天然覆盖 B 和 C 的 80%。

### 各情景下的轮次考察点速查

| 轮次 | 时长 | 考察点 | 对应 JD 原文 |
|---|---|---|---|
| 实战 coding/debug | 60–75min | Python/PyTorch 现场写或修：训练循环 bug、数据管道、向量化数值代码、手写 attention 级实现。重速度和代码直觉，非 hard LeetCode | "Very strong coding skills in Python, C++, or Rust" |
| 项目 deep-dive | 60–75min | 你的 post-training/数据工作被 Cruise/Tesla 式盘问：failure modes 怎么诊断、data mixture 怎么调、eval 怎么设计、数字是多少 | "diagnosing failure modes, improving data mixtures, and tightening evaluation" |
| 开放设计 / founder | 30–60min | 类似「为家用机器人从零设计 post-training 数据引擎」；同时测 high agency、in-person 投入、无层级接受度 | "mental acuity... reason across unfamiliar domains"；Vogt 反层级语录 |

---

## 3. 五种轮型的应对策略

### 3.1 Technical deep-dive（项目盘问）— 权重最高，必然出现

**风格预判：** Cruise/Tesla 系面试官 = "hand-wave and you're done" 文化（Skild 同款）。他们不听叙事听参数：每个决策都会被追问「为什么不是另一个方案」「数字是多少」「怎么知道是这个原因」。

**准备动作：** 把你最硬的 post-training 项目重构成四段式，每一段都能独立扛 5–10 分钟追问：

1. **Failure mode**：模型/系统具体怎么坏的（不是「效果不好」，是「在 X 类输入上出现 Y 行为，占比 Z%」）。
2. **诊断手段**：你看了什么（loss 曲线分段？per-slice eval？logit/entropy 分布？rollout 逐条读？），怎么排除了其他假设。
3. **改动**：data mixture 怎么调（比例、来源、过滤规则）/ eval 怎么收紧（新增什么 slice、什么 held-out）/ 训练配方改了什么（LR、KL 系数、reward shaping）。
4. **量化增益**：改前改后数字，以及**哪些没修好**——主动交代残留问题是高级信号。

**面试时怎么说（转折句示范）：**

> "Let me give you the concrete version. The failure mode was X — I can quantify it: about N% of eval rollouts showed this pattern. My first hypothesis was A, but the per-slice breakdown ruled that out because Z. What actually fixed it was changing the data mixture from P to Q, which moved the metric from M1 to M2. What it did NOT fix — and I want to be upfront about this — is Y, which I believe needs a different intervention."

**关键姿态：** 被问到不知道的数字时，不要糊弄。说 "I don't remember the exact number, but it was on the order of X, and here's how I'd verify" —— mental acuity 考的是推理透明度，不是记忆力。

**跨域追问预案：** 他们明文说会 "reason across unfamiliar domains"。你没有机器人经验，大概率会被问「你的 LLM post-training 经验怎么迁移到 robot policy」。提前想好映射：SFT ↔ behavior cloning；RLHF/RLVR ↔ RL fine-tuning on real rollouts；LLM eval slices ↔ per-task/per-scene success rate；data mixture ↔ teleop/sim/real 配比。**不要假装懂机器人，要展示你能用一手原理把两边接起来。**

### 3.2 ML system design（开放式：数据引擎 / eval 体系）

**最可能的题面（推断，基于 JD + CTO 推文 + field ops 实证）：** "Design the post-training data engine for a home robot: teleop data + real-robot rollouts + data from customer homes. How do you close the loop?"

**答题骨架（用 Tesla data engine 语言讲，面试官一听就是自己人）：**

1. **先问清目标和约束**（2 分钟）：什么任务分布？多少台机器人在真实家庭？隐私约束？标注预算？—— 不问就开讲会被判 hand-wave。
2. **数据分层**：teleop（高质量、贵、覆盖窄）/ sim（便宜、无限量、有 sim2real gap）/ 真机 rollout（分布对但质量混杂）/ 用户家庭数据（分布最真实但有隐私和长尾噪声）。给出每层的角色和大致配比逻辑，以及**配比怎么随阶段演化**。
3. **闭环机制（核心得分点）**：failure mining —— 线上失败案例自动回流（触发条件：human intervention、task timeout、anomaly detector），进入 triage → 分类 → 定向补数据（针对性 teleop 重演 / sim 复现）→ 重训 → shadow eval → 灰度部署。这就是 Tesla data engine 的 corner-case 循环，明说这个类比。
4. **Eval 体系（CTO 点名，必须主动展开）**：分层 eval —— 离线（held-out per-task/per-scene success、回归集 = 历史 failure 案例全量重跑）、sim eval（快、可控变量）、真机 eval（金标准、贵，设计 sampling 策略）、线上 proxy metrics（intervention rate、task completion）。强调「每修一个 failure mode 就把它固化成回归 eval」。
5. **主动交代 trade-off**：eval 真机吞吐是瓶颈 → 怎么用 sim eval 做预筛并定期校准 sim-real 相关性；用户数据的隐私 → on-device 过滤 / opt-in。

**面试时怎么说（开场示范）：**

> "Before I design anything, let me pin down the loop we're optimizing: I assume the bottleneck is not model capacity but data coverage of the long tail of real homes. So I'll structure this as a data engine — the same philosophy as an autonomy data engine: deploy, mine failures, target data collection at those failures, retrain, and gate redeployment on evals. Let me walk through each stage, and I'll flag the two places where I think this breaks first."

### 3.3 Debugging 现场题（log / 训练数据分析）

**两种子形态：**

**(a) 训练不收敛 / 训练异常。** 标准排查树背熟并现场说出声：
- 先看**曲线形状**：loss 不降（LR/数据/初始化/bug）、降了又炸（LR 过大、数值溢出、bad batch）、train 降 eval 不降（过拟合/eval 泄漏或错位）、周期性尖刺（数据顺序/特定 shard 脏数据）。
- 再做**二分隔离**：固定 seed 缩小到单 batch 能否 overfit（能 → 数据/规模问题；不能 → 代码 bug）；关掉 augmentation/mixed precision/分布式逐项排除。
- 常见 PyTorch 现场 bug 清单：忘 `zero_grad`、`train()/eval()` 模式错、loss 没 `mean` 导致 scale 错、label 错位 off-by-one、`softmax` 后又接 `CrossEntropyLoss`、dataloader shuffle 泄漏、fp16 溢出、梯度未 clip、tokenizer/padding mask 错。

**(b) 真机行为异常（贴合他们 Airbnb field-test 日常）。** 你没有真机经验，但可以用通用的分层定位法 + 数据人视角：

> "I haven't debugged a physical robot before, so let me reason from first principles and you can correct my priors. I'd bisect the stack: first, is the input wrong — replay the sensor stream, check timestamps and calibration drift. Second, is the model wrong — run the same observation through the policy offline, compare action distribution against a known-good checkpoint. Third, is the execution wrong — compare commanded vs. actual trajectories. The fastest discriminator is usually replaying logged observations offline: if the policy output matches the bad behavior, it's a model or data problem, and then I'm in my home territory — I'd look at whether this scene is out-of-distribution relative to training data."

这个回答同时展示了：诚实（没碰过真机）、跨域推理（JD 明文要的）、以及把问题拉回自己主场（数据分布）的能力。

**通用纪律：出声思考 + 每一步说「我预期看到什么、看到什么说明什么」。** 这类轮考的是排查过程的结构，不是撞对答案。

### 3.4 Coding（实战向，非 LeetCode）

**预判题型（按类比公司概率排序）：**
1. 向量化数值代码（Skild 风格：单遍 reverse 迭代算 discounted returns；rolling statistics；masked mean）。
2. 手写 attention / 简版 transformer block（Tesla 电面高频）。
3. 修一段有 bug 的训练循环（结合 3.3a 的 bug 清单）。
4. 数据管道题：清洗/去重/流式处理大文件。

**策略：**
- 先 30 秒复述题目 + 确认边界（shape、dtype、空输入），再写。他们要 mental acuity，磨蹭比小 bug 更减分。
- **先写对再写快**：先给 naive 循环版本说 "let me get a correct baseline first, then vectorize" —— 这句话本身就是加分项。
- 写 NumPy/PyTorch 时把 shape 注释写在行尾（`# [B, T, D]`），Tesla 系面试官吃这套。
- 手写 attention 提前默写到肌肉记忆：`scores = q @ k.transpose(-2,-1) / sqrt(d_k)` → mask → softmax → `@ v`，加上 causal mask 和 padding mask 两个变体。
- 如果被丢 C++ 相关问题：不硬写，聊你懂的（内存布局、为什么推理侧用 C++/Rust），承认 Python 是主语言。JD 写的是 "Python, C++, **or** Rust"。

### 3.5 Founder / culture chat（可能被砍到 20 分钟——那是好信号）

**红线（来自 Vogt 公开语录，非猜测）：**
- 不聊晋升、管理轨道、带团队（"Everyone is an IC"；"manager, senior manager, director... become horribly inefficient"）。
- 不表现出对 remote/hybrid 的任何留恋。全岗位 SF onsite，卖点是 "10 feet from desk to running code on a robot"。
- 不把公司当跳板叙事。Vogt 明言不再卖公司、要长期做大。

**必答题预案：「为什么家用机器人、为什么是现在、为什么是你」——** 答案要真诚且个人化。示范（按 Ray 的背景起草，需自己校准细节）：

> "Two reasons. First, I've spent my career on the interface between humans and intelligent systems — my PhD was in HCI, and my recent work is post-training LLMs to act, not just talk. A home robot is the most extreme version of that interface: it lives in your space, and the gap between a demo and a product is entirely in the long tail of real human environments. That long tail is a data and evaluation problem, which is exactly the work I love. Second, I want the sub-100-person version of this: everyone an IC, no layers, walk ten feet and run your code on a robot. I've seen what process-heavy orgs do to iteration speed, and I'm deliberately choosing the opposite."

**High agency 证据准备：** 挑 1–2 个「没人叫我做、我发现问题直接把它做完」的故事，30 秒能讲完，有结果数字。founder 轮问 "tell me about a time" 时直接用。

**你反问的问题（准备 3 个，测你 curiosity 的环节）：**
- "What does the data flywheel look like today — how does a failure observed in a test home end up changing the next training run, and where's the biggest friction in that loop?"
- "How do you split eval between sim and real robots today, and how do you keep sim eval honest?"
- "What's the sharpest disagreement inside the team right now about the training recipe?"（测他们，也展示你）

---

## 4. 类比公司面经中可复用的具体题目

这些是**真实出现过的题**（来源标注），风格与 The Bot Company 面试官母体高度重合，直接拿来练：

| # | 题目 | 来源 | 练法 / 答题要点 |
|---|---|---|---|
| 1 | "10,000 小时 teleoperation 数据 + 100 小时真机 rollout，怎么合起来训一个 policy?" | Skild AI problem session | 核心张力：teleop 量大但 off-policy/分布偏、rollout 量小但 on-policy。答：先 BC on teleop 打底 → rollout 做 RL fine-tune 或 filtered BC（只学成功轨迹）→ 关键是 rollout 数据加权/重放策略 + 用 rollout 分布做 eval 集。**这题就是 LLM 的 SFT→RLHF 结构，明说这个映射** |
| 2 | "BC 为什么会 compounding errors，DAgger 修了什么、没修什么?" | Skild AI | 答：BC 只见过 expert 状态分布，policy 一步偏离就进入没见过的状态 → 误差随 horizon 累积（quadratic in T vs. DAgger 的 linear）。DAgger 修了 distribution shift（在 policy 自己的状态上收 expert 标注），没修：expert 本身不可达/次优、标注成本、多模态动作分布的模式平均问题 |
| 3 | "quadruped 上没见过的冰面，sim-to-real 哪里先崩?" | Skild AI | 答摩擦系数在训练时的 randomization 范围外 → 接触动力学首先崩。被追问时给具体参数：randomize 了 friction coefficient 什么范围、质量/电机延迟/地形怎么随机化。**这题的元教训：说 domain randomization 必须能报出参数和范围，否则 "hand-wave and you're done"** |
| 4 | 手写 attention / transformer 模块 | Tesla 电面高频（1p3a/Blind） | 默写到 5 分钟内无 bug，含 causal mask + padding mask 变体，shape 注释齐全 |
| 5 | Importance sampling 实现/推导 | Tesla 电面（1p3a） | 能写估计量、说明高方差问题和 clipping；顺手连到 PPO ratio clipping——面试官是 RL at scale 背景 |
| 6 | Circular array / 环形缓冲实现 | Tesla 电面（1p3a） | 15 分钟内写完带测试；机器人语境 = 传感器流缓冲，可主动点破这个联系 |
| 7 | 单遍 reverse 迭代算 discounted returns（向量化） | Skild coding 轮 | `G[t] = r[t] + γ·G[t+1]`，先写 reverse 循环版，再讨论能否向量化（`scipy.signal.lfilter` 或 log-space 前缀技巧），并处理 episode boundary mask |
| 8 | 对简历 ML 项目的技术难点连环追问（电面前 15–20 分钟就开始） | Cruise MLE 流程 | 用 3.1 的四段式；准备好被打断和跳问 |
| 9 | 开放式 CV/ML 设计题 + 基础知识混考（有人挂在这轮） | Figure AI 1p3a | 弱区自查：经典 CV/ML 基础（BN vs LN 为什么、优化器差异、为什么 policy 输出用 diffusion/action chunking——至少能讲一手原理） |
| 10 | "讲你自己的工作并接受盘问"（project talk 独立成轮） | Skild AI | 等同情景 C 的 presentation 轮，练一个 15 分钟无 slides 口头版 |

**练习优先级（时间只够练一半时）：** #1、#2（开放推理，直接对口他们的业务）→ #4、#7（coding 最可能形态）→ #3（sim2real 是 CTO 点名词）→ 其余。

---

## 5. 当天临场策略（13:00–17:00）

### 5.1 时间与状态管理

| 时间 | 动作 |
|---|---|
| 11:30–12:15 | 轻午餐（蛋白质为主，避免大量碳水——14:30 血糖崩不起）。正常咖啡因剂量在 12:15 前摄入完毕，作用峰值恰好覆盖第一轮 |
| 12:15–12:45 | 最后翻阅：只看本文 TL;DR + 四段式项目卡片 + attention 默写一遍。**不看新材料**，新信息此时只会增加焦虑 |
| 12:45 | 到场/上线。带：笔记本电脑（PyTorch 环境提前验证可跑、编辑器配好）、充电器、水、能量小食（坚果/能量胶，第 2–3 轮间隙吃） |
| 13:00–14:15 | 第一轮。开场 30 秒自我介绍（见 5.2），前 5 分钟语速刻意放慢 10%——高压开局最容易语速失控 |
| 轮间隙（~5min） | 固定重置仪式：上厕所 → 喝水 → 3 次深呼吸 → 只看一眼四段式卡片。**不复盘上一轮**：单轮否决制下，复盘上一轮既无法改变结果又污染下一轮状态 |
| 14:15–15:45 | 第二轮（大概率 deep-dive）。这是权重最高的一轮，能量分配上留足 |
| 15:45 | 吃 snack。16:00 后是全天认知低谷 + founder 轮，靠这口顶住 |
| 15:50–17:00 | 第三轮。如果是 founder 轮且 20 分钟就结束——**这是好信号不是坏信号**（前面轮次已过，founder 只做确认） |

**关于「提前结束」的心理预案：** 提前结束既可能是否决也可能是提前通过，你无法从时长读出结果，所以规定自己**不解读**。每轮开始时的唯一目标：让这一轮的面试官愿意拍板要你。

**被问懵时的 3 秒话术（背下来，防大脑空白）：**

> "Good question — let me think out loud for a second."

然后从「这个问题在优化什么 / 约束是什么」开始重建。JD 要的 mental acuity 是可见的推理过程，沉默 20 秒才是真扣分。

### 5.2 每轮开场 30 秒自我介绍（英文模板）

> 与 08 §1 的分工：**首轮**用 08 §1 的 60–90 秒完整版；本节 30 秒版用于第 2/3 轮快速开场。两套都要练，别混。

**基础版（技术轮通用）——** 结构：身份一句 + 最相关经验一句 + 与岗位的钩子一句。方括号处按自己实际数字填：

> "Hi, I'm Ray. Until recently I was a member of technical staff at Reflection AI, where I worked on post-training LLMs for agentic tasks — my day-to-day was the full loop: designing data mixtures, running and debugging large-scale training experiments, and building the evals that tell us whether a change actually helped. Before that I did my PhD at the University of Washington on human-computer interaction, so I've always worked at the boundary between models and the messy real world. That's exactly why this role excites me — home robots are the hardest version of that boundary, and the bottleneck is the data and eval loop, which is where I live."

**Coding/debugging 轮变体（更短，快速进入干活状态）：**

> "Quick version: I'm Ray — I did post-training at Reflection AI, most of my time in PyTorch training loops and data pipelines, and I've debugged my share of runs that silently went wrong. Happy to dive right in."

**Founder 轮变体（使命 + agency 前置）：**

> "I'm Ray. Short version of my path: HCI PhD at UW, then post-training LLMs at Reflection AI — teaching models to act reliably, not just talk. I'm here because I think the gap between a robot demo and a robot product is a data-engine and evaluation problem, and I want to work on it in a sub-100-person team where everyone's an IC and the robot is ten feet from my desk."

**使用纪律：**
- 每轮都主动给这 30 秒，即使面试官没要——它设定你想被追问的方向（data mixture / eval / debug），把 deep-dive 引到你的主场。
- 30 秒是硬上限。练到 25 秒说完，留 5 秒缓冲。
- 三个版本各朗读 5 遍以上，做到脱稿且不背书腔。

### 5.3 一页 cheat sheet（轮间隙唯一允许看的东西）

打印或手写一张卡片，只放：
1. 四段式项目卡：failure mode / 诊断 / 改动 / 数字（每段一行关键词）。
2. 训练 debug 排查树的 5 个分支关键词。
3. Attention 一行公式 + 两个 mask。
4. Data engine 设计答案的 5 个节点：目标澄清 → 数据分层 → failure mining 闭环 → 分层 eval → trade-off。
5. Founder 轮三红线：no 管理话题 / no remote / no 跳板叙事。
6. 反问的 3 个问题。
