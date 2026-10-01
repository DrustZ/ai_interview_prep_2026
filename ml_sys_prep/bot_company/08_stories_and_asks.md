# 08 · 个人故事与提问清单（Stories & Asks）

> 配套：[01_company_brief](01_company_brief.md)（公司事实）· [02_interview_rounds_intel](02_interview_rounds_intel.md)（轮次推断）· [03_robot_learning_crash_course](03_robot_learning_crash_course.md)（术语映射）
> 事实来源：你的背景事实来自 `ml_sys_prep/12_personal_bridge.md`、`projects/bridgewater_aia/01_project_deepdive.md`、记忆库中的 CV 摘要（drustz.com/assets/pdfs/CV-research.pdf）；The Bot Company 事实只来自本目录调研简报。

---

## TL;DR — 只有 20 分钟就看这段

1. **一句话定位**：*"I've owned the exact loop they're hiring for — data mixtures, RL post-training, eval — just on LLM agents instead of robots. Robot learning is adopting the LLM playbook, and I bring the playbook."*
2. **自我介绍严格 60–90 秒**（你在 Decagon 讲了 11 分钟被打断——这次开场就说 "I'll do 60 seconds, we can go deep later"）。逐字稿见 §1。
3. **主打故事只有一个**：Reflection 的 RL 数据难度筛选（S1）——「以为是质量问题→被数据证伪→改成在线难度探测→12% 算力花在筛选上→能说出自己方案的失效条件」。这正中 JD 原话 *"diagnosing failure modes, improving data mixtures"*。
4. **第二故事**：Anthropic take-home 的 grader vs ROUGE（S3）——全数字可公开（AUROC 0.569 vs 0.838），对口 robotics 公认未解的 evaluation 难题。
5. **失误故事必备**（S5，Decagon 项目）：指标与天花板一位不差→逐字复现训练目标→教训「指标好得反常先看原始输出」。真实、有数字、有后续断言化动作。
6. **弱点预案核心句**：*"What's not missing is the training loop; what's missing is physical intuition — and I've closed a similar gap before at Meta Reality Labs, working one layer above raw EMG sensors."*
7. **Why Bot Company 三条**：HCI PhD → 家用机器人是 HRI 终极场景；no-teleop 立场逼出真正的 fleet data engine（正是你的专长的 hard mode）；<100 人全 IC、飞轮最早期 = 你这种「数据→模型改进」角色杠杆最大。
8. **反问的总原则**：每个问题都应暴露你已经想过 data engine / eval / product cadence 的具体细节，而不是要信息。最强的一问：*"Given you've ruled out in-home teleop, what does the intervention signal look like — and who closes the loop on a failure clip today?"*
9. **地雷**：别提 Airbnb 诉讼和合同工集体诉讼；别逼问产品形态（stealth）；别问 remote（全员 SF onsite）；Reflection 细节讲方法不讲绝对数字。
10. **每轮都是生死轮**（单轮否决制，见 02）——所以 S1 + 弱点预案 + founder 轮的 Why 必须练到脱口而出，其余按需调用。

---

## §1 · 60 秒英文自我介绍（定制版）

> 目标岗位假设：Multimodal Foundation Models 一类的 ML 岗（JD 要求 pretraining/post-training/RL、data mixtures、edge 部署）。若面 ML Infra-Data Infrastructure，把第二段换成 data pipeline 侧重（见 §1.1 变体）。

**逐字稿（~150 词，practice 到 55–70 秒）：**

> I'm Ray. For the last three years I've done LLM post-training, and before that a decade in human-computer interaction.
>
> Most recently I was at Reflection AI, where I owned mid-training and RL data pipelines — synthetic data generation, difficulty-based curriculum, and async rollout inference on GPU clusters. Before that, at Meta AI, I post-trained LLM ranking agents with SFT and RL — our multi-agent RL work on table reasoning hit #1 on TableBench and is in ACL 2026. Earlier, at Meta Reality Labs, I built EMG-based text input for AR glasses — real sensors, noisy signals, tight on-device latency budgets. My PhD at UW was in HCI.
>
> Why I'm here: robot learning is adopting the LLM playbook — behavior cloning is SFT, interventions are preference data, and the real bottlenecks are data mixtures and evaluation. That's the exact loop I've owned end-to-end, and I want to run it where the flywheel is just starting: robots in homes.

**讲法纪律：**

| 规则 | 原因 |
|---|---|
| 结尾主动收：*"Happy to go deep on any of these."* | 把深挖的选择权交给面试官，显得有存货 |
| 三段各 20 秒：现在→轨迹→为什么来 | Bridgewater 备考里验证过的结构（04_mock_questions Q1） |
| 不要展开 EMG 细节 | 它是弱点预案（§4）的弹药，别提前打光 |
| "owned" 只用于真属于你的部分 | 单轮否决制下被追穿一次就完了 |

### §1.1 变体：如果面的是 Data Infrastructure 岗

把第二段 Reflection 部分换成：

> At Reflection I built the data side of mid-training: synthetic data generation at scale, async inference over a shared GPU cluster to score and filter millions of samples, and the internal tooling that let researchers iterate on data mixtures without touching infra. [填入你的具体规模数字：每天处理多少 token/样本、多少 GPU]

---

## §2 · Why robotics / Why The Bot Company（英文示范）

> 会在 founder/culture 轮被问，也可能是 deep-dive 轮开场。90–120 秒。真诚版——三条理由都是真的，所以经得起追问。

**逐字稿：**

> Three honest reasons.
>
> First, the HCI one. I spent my PhD and years at Meta studying how intelligent systems should behave around people — text entry, accessibility, AR input. A robot living in someone's home is the final exam of that entire field: it has to be capable, but it also has to be trustworthy, predictable, and privacy-respecting to people who never read a manual. I've wanted to work on that problem since grad school; the technology finally caught up.
>
> Second, timing. Robot learning is being rebuilt around the LLM recipe — VLM backbones, behavior cloning as SFT, RL on top. The binding constraints right now are the data engine and evaluation, not architecture. Those are exactly the two things I've done for LLM agents in production. I'd rather carry a proven playbook into a new domain at the moment it matters than run the same playbook again where it's already commoditized.
>
> Third, this company specifically. Two decisions tell me the engineering culture is serious: choosing a non-humanoid form factor — solving the task, not the demo — and publicly ruling out in-home teleoperation. That second one is a hard constraint: no teleop means the data flywheel has to actually work — triggers, mining, curation, OTA. That's the hard version of my specialty, and with a team under a hundred people, the person who owns "fleet data becomes model improvement" has enormous leverage. I want that seat.

**追问弹药：**

| 可能追问 | 接法 |
|---|---|
| "You could do this at PI / Figure / Tesla, why us?" | Humanoid 公司在卖形态，你们在卖任务完成；no-teleop 立场在业界是少数派但你认为它对 privacy 和 scaling 都是对的（Kyle 在播客里讲过——No Priors / Cheeky Pint，你听过，可自然引用）；<100 人全 IC 意味着不用等平台团队排期 |
| "What if the flywheel takes years?" | 先做低风险任务（捡玩具、收包裹，容错 90–99%）本身就是数据策略——低风险任务先上量，数据反哺高风险任务。这个排序你认同且正是 data engine 思维 |
| "HCI 听起来像做 UI 的" | 一句话反转：*"HCI taught me that the metric that matters is what the human experienced, not what the model scored — which is exactly the eval problem robotics hasn't solved."* |

---

## §3 · 六个 STAR 故事（英文要点版）

> **用法**：S1 是主菜，必练到三层深度（结果→为什么这么选→什么时候是错的）。S3、S5 次优先。S2/S4/S6 按面试官背景调用。
> **保密纪律（S1/S2）**：讲方法论和判断，不讲模型规格、内部指标绝对值、未公开路线图。主动说 *"Some specifics I can't share, so I'll speak in methods and relative magnitudes"* ——比含糊其辞好。

### 故事 → 考点映射表

| # | 故事 | 对口 JD/考点 | 公开度 |
|---|---|---|---|
| S1 | Reflection · RL 数据难度筛选 | "diagnosing failure modes, improving data mixtures"；curriculum；数据飞轮 | ⚠️ 讲相对量 |
| S2 | Reflection · mid-training 数据管线 0→1 | data infra、GPU 集群、"own the training loop end-to-end" | ⚠️ 讲相对量 |
| S3 | Anthropic take-home · grader vs ROUGE | evaluation（robotics 公认未解）、指标批判 | ✅ 全数字可讲 |
| S4 | Meta AI · ranking agent SFT+RL | 生产级 post-training、multi-agent RL、发表 | ✅ 已发表 |
| S5 | Decagon 项目 · 完美指标 = 泄漏 | 最大失误题、debug 方法论、数据划分 | ✅ 自研项目 |
| S6 | Meta Reality Labs · EMG 穿戴输入 | 传感器/噪声/edge——你最接近硬件的经历 | ✅ 已发表方向 |

---

### S1 ⭐ Reflection: Adaptive difficulty curriculum for RL data（主打）

- **S** — RL training on math/STEM data hit a wall: reward curve flattened early despite plenty of open-source data. Team assumption (mine included) was **data quality**.
- **T** — I owned the data side: figure out why training stalled and fix the data pipeline.
- **A1** — First attacked quality: cleaning, format validation, dedup. **Minimal gains — hypothesis falsified.** The telling signal: a large fraction of rollout groups were all-correct or all-wrong → zero gradient signal either way (GRPO-family advantage is group-normalized; uniform outcomes = wasted batch).
- **A2** — Reframed as a **difficulty distribution** problem. Built online difficulty probing: small rollout batch per problem (16 probes vs 128 formal, ~12% of compute), drop problems with no discrimination, keep the informative band.
- **A3** — Rejected two alternatives deliberately: static difficulty labels (stale — difficulty is relative to a moving model) and proxy-model scoring (adds an approximation layer). Online probing is costlier but measures the **current** model's solve rate, which is the actual quantity that drifts.
- **R** — Eval resumed climbing by a clear margin (specifics confidential; happy to describe the measurement design).
- **失效条件（第三层，主动说）** — Two real costs: (1) 12% of compute goes to probing — pure waste if data is already balanced; (2) it **systematically discards the hardest problems**. If the goal were raising the ceiling rather than steady climb, this policy is harmful — the most valuable problems are the ones just beyond current ability. Right call for our goal, wrong call for a different one.
- **→ robotics 接口** — *"This maps one-to-one onto robot RL: if your fleet only uploads episodes the policy already handles or total failures, you're paying for batches with no gradient. Curating for the informative band is the same problem."*

### S2 · Reflection: Mid-training data pipeline & async GPU inference, 0→1

- **S** — Mid-training needed synthetic data generated, scored, and filtered at a scale where naive sequential inference on the shared GPU cluster was the bottleneck.
- **T** — Build the pipeline end-to-end: generation → async scoring → filtering → mixture assembly, plus internal tooling so researchers could iterate without touching infra.
- **A1** — Built async inference over the shared cluster to keep utilization high under preemption [填入：吞吐/利用率的相对提升，或「从 X 天缩到 Y 小时」量级].
- **A2** — Made data versioned and auditable: every mixture traceable to sources and filters, so a bad eval could be root-caused to a data decision [填入：一个具体的 root-cause 案例].
- **A3** — Built the internal ML tools / agentic workflows around it so the loop ran without me in it [填入：工具名或功能一句话].
- **R** — The pipeline became the standard path for the team's mid-training data work [填入：被多少人/多少 run 使用的量级].
- **→ robotics 接口** — *"A robot fleet's data engine is this pipeline with a harder ingestion problem: triggers and bandwidth instead of API calls. The curation, versioning, and mixture logic transfer directly."*
- ⚠️ 此故事细节最薄——面前必须把 [占位] 补成你能为每个数字辩护的版本，补不出的就删掉那条 bullet。

### S3 · Anthropic take-home: When the standard metric is a coin flip（eval 主打，全数字公开）

- **S** — Take-home: evaluate LLM-generated clinical notes. The benchmark's official graders (ROUGE / BERTScore family) only compare against a reference note — they never read the source conversation.
- **T** — Decide whether the standard metric measures what matters, and build something better if not — in ~13 hours.
- **A1** — Built a source-grounded, claim-level grader: extract claims from the generated note, verify each against the conversation, arbitrate disagreements with a stronger model.
- **A2** — Validated **out-of-sample**: froze grader v2 *before* touching the physician labels. On 85 physician "unsafe" annotations: 1−ROUGE got AUROC **0.569 — a coin flip**; my grader **0.838**, non-overlapping CIs.
- **A3** — Perturbation suite (137 pairs of injected known errors): ROUGE-2 was *inverted* (AUC 0.32 — rewards the corrupted note); grader 0.79; span-level negation detection 100%.
- **A4** — Reported two **refuted priors** honestly in the writeup (e.g., under paired stats ROUGE *can* stratify — it measures a different construct, not nothing). Honest negatives made the headline credible.
- **R** — The deliverable's core claim: the field was optimizing a metric uncorrelated with clinician-judged safety, and a verifiable grader fixes it at known cost.
- **→ robotics 接口** — *"Robotics eval has the same disease: offline metrics that don't predict task success, and real-robot trials too expensive to run at power. The discipline — freeze the grader before the labels, perturb with known failures, report what refuted you — is domain-independent."*

### S4 · Meta AI: Post-training LLM ranking agents (SFT+RL), TableBench #1, ACL'26

- **S** — Recommendation/ranking surface at Meta; task: make LLM agents do structured (table) reasoning well enough to rank/decide in production context.
- **T** — Own post-training: SFT to establish behavior, RL to sharpen decisions.
- **A1** — Built the SFT→RL pipeline [填入：数据来源、reward 设计的一句话]; research line became **Mixture-of-Minds** — multi-agent RL for table understanding.
- **A2** — [填入：一个具体的技术决策与被否掉的替代方案]
- **R** — **#1 on TableBench**; paper accepted to **ACL 2026**.
- **→ robotics 接口** — *"This was my first full pass of the loop the JD calls 'own the training loop end-to-end' — data, SFT, RL, eval — with a public scoreboard at the end."*
- 用途：需要「有发表、有排行榜」的硬凭证时用；面试官是 researcher 背景时优先于 S2。

### S5 · The metrics were too perfect（最大失误题 · 必备）

- **S** — Fine-tuning practice project (customer-support domain, fully public — my own repo). One SFT run came back with metrics matching the ceiling **digit for digit** — even average word count identical (27.37).
- **T/失误** — My first reaction should have been suspicion. Instead I started writing the report. Halfway through, "this is too clean" — went back and looked at raw outputs.
- **A** — The model was reproducing training targets verbatim: my split let the same topic span train and dev, labels were templated, so the task had degenerated into template recall. **The entire run was wasted.**
- **R1（教训 1）** — When metrics look anomalously good, the first action is **read raw outputs**, not proceed.
- **R2（教训 2）** — Hardened it into an assertion: the test suite now requires meaningful headroom between baseline and ceiling — anyone who breaks the data design turns the build red.
- **Bonus（同项目，如追问再给）** — Also caught auto-generated DPO preferences that were noise *before* training: independent-metric check showed chosen beat rejected only 46.2% of the time — worse than a coin. A five-second check that saves a full training run.
- **→ robotics 接口** — *"In robotics this instinct matters more, because a policy that memorized its eval scenes looks perfect right up until it meets a real living room."*

### S6 · Meta Reality Labs: EMG text input for AR glasses（硬件桥梁故事）

- **S** — Building text input for AR glasses from wrist EMG — decoding neuromuscular signals into keystrokes/gestures.
- **T** — Make a model work on noisy, drifting, person-dependent physiological sensor data under real-time, on-device latency budgets.
- **A1** — Lived one layer above raw hardware: sensor placement variance, session-to-session drift, electrode contact quality — "the data lies to you and the device fights back."
- **A2** — [填入：一个具体技术决策——例如个性化 vs 通用模型的取舍、校准流程设计]
- **A3** — Designed data collection with humans in the loop: protocol design, participant sampling, label provenance — collection design determined model ceiling more than architecture did.
- **R** — [填入：可公开的结果——demo/发表/性能量级]
- **→ robotics 接口** — 这是弱点预案（§4）的主要弹药：不是机器人，但同属「近原始传感器信号 → 神经网络 → 实时行为」——恰是 The Bot Company 的技术路线（端到端网络直接吃近原始传感器/电机信号）。

---

## §4 · 弱点预案："You have no robotics / hardware experience"

> 一定会被问（可能以更委婉的形式：*"What would be hardest for you here?"*）。原则：**先承认，再精确切分缺什么/不缺什么，给两个「缺口会快速闭合」的证据，落在 day-one 贡献上。** 不辩解，不说 "robotics is just software"。

**主答（~60 秒）：**

> You're right — I haven't shipped a robot, and I won't pretend otherwise. Let me be precise about what's missing and what isn't.
>
> What isn't missing: the training loop. Robot learning has converged on the LLM recipe — a VLM backbone, behavior cloning as SFT, RL on top, data mixtures as the main lever, and evaluation as the open problem. I've owned that exact loop in production, including the failure modes: reward curves that flatten because of difficulty distribution, metrics that lie, preference data that's secretly noise.
>
> What is missing: physical intuition — contact dynamics, controls, sim-to-real, how hardware fails. Two reasons I believe that gap closes fast. First, I've closed a similar one before: at Meta Reality Labs I worked one layer above raw EMG sensors — noisy, drifting, person-dependent signals with millisecond latency budgets. Not robotics, but the same discipline. Second, my ramp-up pattern: [填入你最快上手新领域的一个实例，如「x 周内在陌生领域交付了 y」——可用 Exa work trial：两天在多查询向量检索命题下交付可复跑实验]。
>
> And frankly — your bet is end-to-end networks eating near-raw sensor data, which moves the leverage *away* from hand-engineered robotics and *toward* data and post-training. That's where I contribute from day one, while I learn the physical stack from people ten feet away from the robot.

**追问预案：**

| 追问 | 要点 |
|---|---|
| "What's the hardest thing you'll have to learn?" | 诚实指名：real-time control loop 的思维方式（50Hz、action chunking、延迟即正确性的一部分）——但指出你在 EMG 实时解码里碰过它的边（latency budget 决定架构）。别答 "nothing much" |
| "How would you spend your first 30 days?" | ① 跟一台机器人 + 采数据的 operator 轮几个班（数据是怎么长出来的）；② 跑通现有训练→eval→部署一整圈，不改任何东西；③ 挑一个 eval 或 data-curation 的小痛点做出第一个可合入的改进 |
| "sim-to-real 你懂多少？" | 不装深：知道 domain randomization / 知道 sim 是高功效回归 gate 而真机是终审（引 [06](06_system_design_playbooks.md) 的 eval 金字塔思路）；说明你会先把 sim-vs-real 的评估相关性当数据问题来量化——这是你的母语 |
| "我们招过 pure-ML 背景的人失败了，为什么你不会？" | 差异点不在 ML 强弱，在于你的专长恰好是他们卡住的两件事（data engine、eval），且你有跨域重启的前科（HCI→wearable→LLM，每次都到了能发表/上产品的深度） |

---

## §5 · 反问清单（按轮次分组）

> 原则：每个问题都要**携带信息**——让面试官意识到你已经想过这个问题的具体形态。每轮备 4 个，实际问 2–3 个。所有问题用英文原文准备。

### 轮次 1 · Practical / coding 轮（面试官大概率是 ML engineer）

| # | 问题（英文原话） | 为什么问（你的意图） |
|---|---|---|
| 1 | *"When a new policy checkpoint looks worse, what does the debugging loop look like today — replay, sim, or someone walking over to a robot? And how long is one iteration?"* | 探 eval/debug 基建成熟度；铺垫你 [05](05_debug_playbook.md) 的 cohort 切分思路 |
| 2 | *"What fraction of your failures turn out to be data problems versus model problems versus hardware? Do you have the observability to even attribute that today?"* | data-first 思维信号；attribution 正是你的 S1/S3 强项 |
| 3 | *"What's the most annoying tooling gap in your day right now?"* | IC 对 IC 的真话题；也探你入职后第一个可交付物 |
| 4 | *"How much of the training stack is shared across World Models, the foundation model, and whole-body control — one data platform or three?"* | 显示你读过他们 2026/2 的岗位拆分；探组织形态 |

### 轮次 2 · Project deep-dive 轮（面试官可能是 senior ML / research）

| # | 问题 | 意图 |
|---|---|---|
| 1 | *"You've publicly ruled out in-home teleoperation — which I think is the right call. So what does the correction signal look like at deployment: interventions by field operators, user feedback, autonomous retries? And who closes the loop on a failure clip today?"* | 全场最强一问：引用他们的公开立场 + 直击 intervention→DAgger 数据这条你最懂的线（[04](04_data_engine.md)） |
| 2 | *"How do you decide a checkpoint is good enough to OTA to the fleet? Is there an eval gate you trust, and what's its false-pass rate — has a model that passed eval ever regressed in homes?"* | eval 金字塔 + 统计功效（[06](06_system_design_playbooks.md)：90% 成功率 50 trials CI ±8pp）——问完可自然接一句你对配对设计/sequential testing 的看法 |
| 3 | *"On data mixtures: as the fleet grows, how do you weigh fresh fleet data against the original demonstration corpus? Have you hit catastrophic forgetting or distribution collapse when re-training on your own deployment data?"* | mixture/curation 是你 S1 的主场；self-training feedback loop 是前沿痛点 |
| 4 | *"Is RL from real deployment experience on the roadmap, or is post-training mostly BC on curated data for now?"* | 直接对位你的 RL post-training 背景；答案决定你入职后的位置 |

### 轮次 3 · Founder / culture 轮（Kyle 或 Paril）

| # | 问题 | 意图 |
|---|---|---|
| 1 | *"You've said the team stays under a hundred people. As the fleet scales from tens to thousands of robots, which functions do you refuse to grow headcount for — and what has to become software instead?"* | 引用 Vogt 公开立场；本质在问 automation-first 文化，而「把人力变软件」正是 data engine 的核心命题 |
| 2 | *"You and Paril both watched the AV industry build data engines at enormous cost. What's the one thing from Tesla or Cruise you're deliberately *not* copying?"* | 让 founder 讲他最有观点的话题；显示你知道他们的师承（Tesla trigger/auto-label、Cruise CLM——见 [04](04_data_engine.md)） |
| 3 | *"For the first tasks — the 90-to-99-percent-tolerance ones — what's the metric that tells you a task is ready to ship to real customers? Success rate alone, or something closer to 'user never had to think about it'?"* | product cadence + 你的 HCI 视角：shipping bar 是行为指标不是模型指标 |
| 4 | *"What does the company look like in twelve months if everything goes right — and what's the single riskiest assumption between here and there?"* | 经典但有效的 founder 收尾；听 risk 排序（data? hardware? cost?），你可当场接上自己对口的那条 |

### ⚠️ 不要问 / 不要提

| 雷 | 原因 |
|---|---|
| Airbnb 诉讼、合同工集体诉讼 | 你知道 ≠ 该在面试提；负面法务话题零收益 |
| "机器人到底长什么样？能给我看看吗？" | Stealth 公司，逼问产品形态显得不懂规矩（他们主动展示当然最好） |
| Remote / hybrid 可能性 | 全员 SF onsite 是明牌，问了 = 没做功课或意愿存疑 |
| 融资/估值细节 | 全是公开信息，问了浪费反问额度 |
| Reflection 内部细节被反问时 | 主动说保密边界（§3 开头那句），透露反而减分——面试官也在测你会不会将来泄他们的密 |

---

## §6 · 面前 10 分钟自检清单

- [ ] 自我介绍能在 70 秒内说完，结尾是 "happy to go deep"
- [ ] S1 三层都能脱口而出，尤其**第三层失效条件**（12% 探测成本 + 系统性丢最难题）
- [ ] S3 三个数字：**0.569 vs 0.838**、扰动套件 ROUGE-2 **AUC 0.32 倒挂**、grader **先冻结后验证**
- [ ] S5 失误故事的两个教训 + 断言化动作
- [ ] 弱点主答的切分句：*"What isn't missing / what is missing"*
- [ ] 本轮面试官对应的 3 个反问已选好，第一问是带信息量的那个
- [ ] 保密边界句已备：*"Some specifics I can't share — I'll speak in methods and relative magnitudes."*
- [ ] S2/S4/S6 的 [占位] 数字要么已补实，要么对应 bullet 不讲
