# 07 — 高概率题库与答案要点（Question Bank）

> 52 道题，按 7 类分组。**★ 的 15 道**给出可以直接照着说的英文 bullet；其余每题一行中文提示，指向对应备考文件的章节——本文不重复 05/06 已有的完整答案，只做索引和浓缩卡。
> 用法：今天通读一遍（30–45 min）→ 面试当天早上把 52 道英文题目当 flashcard 自测，卡壳的题回看提示。

---

## TL;DR — 只有 20 分钟就看这段

1. **只背 5 道也要背这 5 道**：Q1 自我介绍、Q2 why robotics、Q9 项目 deep-dive 开场、Q29 "bot stopped working"（完整版在 05 §1，480 词背诵稿）、Q36 fleet 数据管线（hook："450 TB/day is neither feasible nor necessary"）。
2. **单轮否决制**（02 的结论）：没有热身题，每道都当生死题答；答完主动收尾，不要拖泥带水。
3. 官方评分标准就三条（01/02）：**mental acuity（快、跨域推理）/ engineering curiosity / high performance mindset**。每个回答至少对齐一条——概念题秀第一条，deep-dive 秀第三条，品味题秀第二条。
4. **Deep-dive 是权重最高轮型**：主打项目按「30 秒头版 → 给地图让面试官选 → 主动讲 failure modes → 每个决策带被否掉的替代方案」讲，JD 原话 "diagnosing failure modes, improving data mixtures" 就是追问方向（对应 Q9/Q10/Q12）。
5. Debugging 题的骨架 = 05 的六层栈 + 「一台 vs 一批」分叉 + cohort 切片；本文 Q29/Q30 只是浓缩卡，**答题时以 05 为准**。
6. System design 四道全在 06，本文 Q36–Q41 只给开场 hook 和必背数字：450 TB/天、~905 trials/组检出 5pp、glass-to-glass <100ms。
7. 概念快问的**兜底套路**：任何答不上的 robotics 概念，先映射回 LLM 概念再推理（03 §0 的映射表），"Let me reason from the LLM analogy" 本身就是加分动作。
8. 品味题（⑦类）没有标准答案，考 reasoning 结构：**先定义术语 → 给 2–3 个论点 → 表明立场 → 主动说反方**。准备好两个 opinionated take：GPT-3 moment 缺什么（Q48）、no-teleop 立场（Q49）。
9. 关于公司的事实只用 01 §6 那 ≤10 条（拒绝入户 teleop、端到端、<100 人全 IC、先做低风险任务等）；没证据的别说，说推断时明说 "my read is…"。
10. 时间紧就只看 15 道 ★：①类 2 道、②类 3 道、③类 3 道、④类 2 道、⑤类 2 道、⑥类 1 道、⑦类 2 道。

### 15 道 ★ 速查

| # | 题 | 类 |
|---|---|---|
| Q1 | Tell me about yourself | 开场 |
| Q2 | Why robotics / why us, with zero robotics background? | 开场 |
| Q9 | Walk me through your best post-training project | 简历 |
| Q10 | Your RL run isn't learning — what do you do? | 简历 |
| Q12 | How did you build your data mixture? | 简历 |
| Q19 | How does LLM post-training map to robot learning? | 概念 |
| Q20 | What is a VLA? Why did flow matching win? | 概念 |
| Q21 | Why isn't RLHF-style preference learning mainstream in robotics? | 概念 |
| Q29 | A bot stopped working — walk me through it | Debug |
| Q30 | Model dumber vs hardware broke vs environment changed? | Debug |
| Q36 | Design data collection for 10k home robots | 设计 |
| Q37 | Design the eval system — how many trials? | 设计 |
| Q43 | How do you decide what data to collect next? | 数据 |
| Q48 | What's missing for home robots' GPT-3 moment? | 品味 |
| Q49 | They reject in-home teleop — do you agree? | 品味 |

---

## ① 开场 / Behavioral（8 题）

> 考察点：culture fit 三条标准 + all-IC/onsite 的自选择。founder chat 被压缩到 20 分钟是好信号（02 §3.5）。

### ★ Q1. "Tell me about yourself." （每轮开场都会来，60–90 秒版本）

- "I'm an ML engineer focused on **LLM post-training and agentic RL** — most recently at Reflection.ai, and before that a PhD at the University of Washington at the intersection of ML and HCI."（一句话身份 + 两个锚点，具体项目名自己填）
- "The through-line of my work: I like to **own the whole training loop** — data curation, training, evals, and shipping — not just one slice."（直接呼应 JD 原话 "Own the Training Loop End-to-End"）
- "I'm here because robot learning is converging on the LLM playbook — VLM base models, SFT on demonstrations, RL from corrections, data mixtures — and the bottleneck has shifted from architectures to **post-training and the data engine**. That's exactly my stack."
- "And frankly, I want to work within ten feet of the thing my model controls."（一句收尾表 intent，止住，把话头交回去）
- 纪律：≤90 秒，落点必须是 why here，不要复述简历时间线。

### ★ Q2. "Why The Bot Company? Why robotics — you've never worked on a robot."

- 先直面 gap，不绕："You're right — I've never shipped a robot. What I bring is the other half of the problem."
- "Robot learning is being rebuilt around LLM-style training. Your own ML posting asks for **LLM-style pretraining, post-training, and RL mastery** — the field decided my skill set is the scarce one."（事实来自 JD，01 §5a）
- "What specifically attracts me here: the bets are data-engine-first — **end-to-end neural nets on near-raw signals, fleet learning, and explicitly no in-home teleoperation**. That makes data strategy the whole game, and data engines are where I've lived."（事实来自 01 §4a）
- "Team shape matters to me: fewer than 100 people, ~95% engineers, all-IC. I'm optimizing for maximal ownership and the shortest loop from idea to robot."
- 收尾给学习速度的证据："On the gap — I close it fast. I've spent this prep going deep on VLAs, intervention-based RL, and real-robot eval; test me on any of it."

### Q3. "Why did you leave your last role / why are you on the market?"
→ 一句话正向叙事（求职背景见自己的 story），落点转向「想做 physical agent + 全栈 ownership」；不贬前司，不超过 30 秒。

### Q4. "We're all-IC, no managers, fully onsite, sub-100 people. How do you feel about that?"
→ 01 §5d 全 JD 通用文化题：这是自选择题，答「这正是我挑公司的过滤条件」，举一个自己无人管理下 ship 东西的例子。

### Q5. "Tell me about a time you had extreme ownership / shipped something end-to-end under time pressure."
→ 用自己最近的 take-home / trial 冲刺类经历套 STAR，量化 deadline 和产出；对齐 "high performance mindset"。

### Q6. "Tell me about a project that failed or a time you were badly wrong."
→ 选一个技术判断错误（不是人际故事），重点讲「怎么发现错的 + 数据怎么打脸 + 改了什么流程」；呼应 05 的可证伪假设方法论。

### Q7. "What would you do in your first 90 days here?"
→ 框架：先跑通一遍现有 training loop 当用户 → 接手一个 eval/data 痛点拿 quick win → 90 天内 own 一条 pipeline；引用 04 §7 指标体系显得具体。

### Q8. "What questions do you have for us?"
→ 备 3 个：eval 瓶颈现状（联动 06 C）、intervention/纠正数据从哪来（联动 Q49）、当前 data mixture 里 sim vs real 的比例——全是「我已经在想你们的问题」信号。

---

## ② 简历深挖：LLM post-training / agent RL 经历（10 题）

> 考察点：Tesla 式盘问（02 §3.1）——failure modes、data mixture、评估、"你自己做了哪部分"。每个数字都可能被追问三层。

### ★ Q9. "Walk me through the post-training project you're most proud of, end to end."

- 30 秒头版先行："The problem was [X]; my role was [Y]; the model/scale was [Z]; the outcome was [metric before → after]."——先给结论再展开。
- 然后给地图并交出选择权："The interesting parts were the data mixture, the RL setup, and the eval design — which do you want to go deep on?"（同 06 §0 的深挖话术，显得知道难点在哪）
- **主动讲 failure modes**，别等追问："The first two runs failed because [具体原因] — here's how I caught it"——这正是 JD 点名的能力。
- 每个设计决策带被否方案："We chose [A] over [B] because [数据/约束]；in hindsight [B] would have been better if [条件]."
- 数字必须张口即来：数据量与配比、GPU 数、训练时长、失败 run 数、eval delta。含糊 = hand-wave = 挂（02 的 Skild 教训）。
- 自己收尾："If I redid it today, I'd change [one thing] — 抢在面试官前面自我批判。"

### ★ Q10. "Your RL run isn't learning — or reward goes up but the policy gets worse. What do you actually do?"

- 先给排查顺序，展示不是瞎试："I debug the loop in a fixed order: **environment & reward → data → optimization → eval**. Most 'RL bugs' are reward or env bugs, not optimizer bugs."
- "First I verify the reward is measuring what I think it measures — print trajectories the reward loves and hates, read them by hand. Reward-hacking shows up here."
- "Then the update mechanics: I keep a standing dashboard — KL, entropy, advantage stats, clip fraction, grad norm. Each has a healthy band; the first curve to leave its band usually names the bug."
- "Then the smallest reproducible experiment: overfit one batch, one task. If that fails, it's mechanics, not scale."
- 插一个自己的真实 war story（哪条曲线暴露了哪个 bug），这是整题的可信度来源。
- 桥接："The same discipline transfers to robot RL — the reward-verification step just becomes success-detector accuracy and sim fidelity."（联动 03 Stage 3）

### Q11. "How did you evaluate your agent? How did you know model B was actually better than A?"
→ 用自己项目答（eval set 构成/防泄漏/统计显著性），收尾桥到 03 §5「你的经验怎么卖」：真机 eval 贵且高方差正是我这套的用武之地。

### ★ Q12. "How did you construct your SFT/RL data mixture? What did you up-weight, down-weight, and why?"

- "I treat the mixture as a **first-class, versioned artifact** — a manifest with ratios and provenance, not a folder of files."（联动 06 B 的 manifest 设计）
- "Weights start from task priors, then get set empirically: small proxy runs, ablate-by-removal, watch per-source held-out evals so one source can't silently poison the mix."
- "Dedup and quality filtering before any reweighting — 讲一个自己「删数据反而涨点」的具体案例，这是最有说服力的一句。"
- "The failure mode I watch for: optimizing average metrics while a minority slice regresses — per-slice evals are non-negotiable."
- 桥接："Robotics has the identical problem with a harder version: mixing teleop, sim, human video, and fleet corrections — the data pyramid. Re-Mix-style reweighting and diversity-over-volume carry over directly."（联动 03 §4、04 §5）

### Q13. "What was your training infra — framework, GPU count, what broke?"
→ 报自己真实配置；准备一个 infra 层的坑（OOM/通信/数据加载瓶颈）及修法，对齐「95% 工程师」文化。

### Q14. "Tell me about a subtle bug in your training pipeline that cost you the most time."
→ 讲一个 silent failure（如预处理/tokenization 不一致），复盘时点出与 05 §2 L4「预处理不匹配是经典 silent failure」同构。

### Q15. "Did you hit reward hacking? How did you handle it?"
→ 自己案例 + 通用三招（更好的 reward 设计/约束、人工审查 top-reward 轨迹、held-out 真实指标）；桥接 robotics：物理世界的 reward hacking 更贵（03 Stage 3）。

### Q16. "How is your agent-RL setup different from classic RLHF?"
→ 一行对比：单步偏好 vs 多步稀疏 reward、credit assignment、env 工程占大头；正好预演 Q21 的 intervention 论点。

### Q17. "Knowing what you know now, what would you redo in that project?"
→ 提前想好一个真诚的技术翻案（通常是「eval 应该更早建」或「数据应该先去重」），显示反思深度。

### Q18. "Which parts did YOU personally do versus your team?"
→ ownership 探针：诚实切分，报自己写的代码/做的决策；含糊其辞比份额小更致命。

---

## ③ Robot Learning 概念快问（10 题）

> 考察点：mental acuity——不是考背诵，是考「用已有知识跨域推理」。答不上就现场从 LLM 类比推（03 §0），推理过程本身给分。Figure 式 30 分钟无码概念聊就是这类（02 §4）。

### ★ Q19. "You come from LLMs. How does your experience actually map onto robot learning?" （必考桥梁题，主动抢答也行）

- "A VLA is literally a VLM used as a base model, with **action as a new output modality** — so the whole post-training playbook transfers."
- "SFT maps to behavior cloning on teleop demonstrations — same curation problems, noisier labels."
- "RLHF maps, but the dominant signal isn't pairwise preference — it's **human interventions**: when an operator takes over, the timestamp marks a failure state and the correction is the label. HIL-SERL, and at fleet scale, RECAP."
- "RLVR maps to sim RL with task-success rewards — including reward hacking, which now has a physical cost."
- "Hallucination maps to confidently executing a wrong action out-of-distribution, made worse by **compounding error** — the robot's mistake changes its next input."
- "The genuinely new hard parts I respect: 50Hz control vs ~1s inference (solved by action chunking and dual-system designs), and **evaluation** — real-robot evals are expensive and noisy, which is the industry's open problem and where I think I add the most."（联动 03 §0/§5）

### ★ Q20. "What's a VLA? Walk me through π0's design — why flow matching instead of discrete action tokens?"

- "Vision-language-action model: take a pretrained VLM, so you inherit web-scale semantics for free, and teach it to output robot actions."
- "Generation one — RT-2, OpenVLA — discretized actions into token bins. Simple, reuses the LM machinery, but bins cost precision and autoregressive decoding is too slow for high-rate control."
- "π0's answer: a **flow-matching action expert** that outputs a continuous action *chunk* — roughly 50 timesteps at 50Hz — so one slow VLM forward pass buys a second of high-rate control."
- "Why flow matching won over diffusion: same ability to model continuous, multimodal action distributions, but far fewer sampling steps — fast enough for real-time. It's the de facto standard now."
- 展示时效性一句："The frontier has moved to π0.7 — a steerable generalist that folded in RL-from-experience from the RECAP line — plus Figure's Helix 02 dual-system and NVIDIA's GR00T N1.7."（03 §1）

### ★ Q21. "Why doesn't RLHF-style preference learning dominate robotics? What replaces it?"

- "Pairwise preference is an awkward fit: you can't cheaply generate two rollouts from the same state to compare — every sample costs real robot time."
- "The natural currency is the **intervention**: a human takes over mid-rollout. You get, for free, an on-policy failure state *and* the expert correction."
- "Formally that's DAgger-flavored — expert labels on the states the policy actually visits — which is exactly the cure for behavior cloning's compounding-error problem."（联动 Q23）
- "Concrete systems: HIL-SERL for real-robot RL with takeovers; RECAP / π*0.6 pushing it to fleet-scale offline-to-online with corrections plus autonomous experience."
- "Trajectory-preference methods exist — GRAPE is the DPO analog — but they're niche."
- 观点句收尾："Interventions are RLHF where **the deployed fleet is the annotator** — every robot in the field generates them continuously. That's why I think the data engine, not the algorithm, decides who wins."（联动 04）

### Q22. "What is action chunking and why does everyone use it?"
→ 03 §3：≈多 token 预测，调和 VLM ~1s 延迟 vs 50Hz 控制；附带 ACT 出处和「chunk 内开环」的代价。

### Q23. "Explain compounding error in behavior cloning. How do people fix it?"
→ 03 §2 Stage 2：训练分布 vs 自身 rollout 分布漂移；解法 DAgger/interventions/RL fine-tune——顺势引到 Q21。

### Q24. "What causes the sim-to-real gap? Standard mitigations?"
→ 03 §4：视觉/动力学/接触三类 gap；domain randomization、system ID、sim 只当回归 gate 不当真值（联动 06 C）。

### Q25. "Why is real-robot evaluation so hard?" 
→ 03 §5 四点必背（贵、方差、不可复现、环境不可控）+ RoboArena；数字弹药在 06 C（905 trials）。

### Q26. "Why do dual-system architectures (like Helix's System 1/2) exist?"
→ 03 §3：大模型管语义低频、小控制器管 1kHz 全身闭环；类比 LLM 里的 router/speculative 思想讲直觉。

### Q27. "What's the robotics equivalent of hallucination?"
→ 03 §0：OOD 状态下自信执行错误动作 + compounding error；一句话题，答完停。

### Q28. "Compare the data sources: teleop vs human video vs simulation."
→ 03 §4 数据金字塔（越上越贵越对口）+ 04 §3.3 成本数字（高质量 teleop ~$118–136/h，第三方市场口径、未证实——口头说 "on the order of $100+ an hour"）。

---

## ④ Debugging 现场题（7 题）

> 考察点：结构化 + 数据优先 + 软硬都敢碰。**Q29 的完整 3.5 分钟背诵稿在 05 §1，此处只放浓缩卡**；硬件深水区的体面撤退话术在 05 §6。

### ★ Q29. "A bot stopped working. Walk me through how you debug it." （用户点名题，05 §1 背诵版优先）

- **Clarify 五连问先行**（这步本身就是得分点）："What does 'not working' mean concretely — no power, no motion, wrong behavior, or intermittent? **One robot or many?** Sudden or gradual? What changed recently — model, firmware, config, environment? Any safety risk — if so, e-stop first and **preserve logs before anyone reboots**."
- "One-vs-many is the biggest fork: single robot with healthy fleet-mates → hardware or per-unit config; a whole cohort at once → OTA, software, config, or environment."
- "My mental model is a six-layer stack — power/hardware, firmware, middleware, the classic autonomy stack, ML policy, cloud/OTA — and I **trace the data flow to the first level where it goes wrong**; everything above that is downstream contamination."
- "Two binary-search tools: hardware **swap test** — does the fault follow the part or stay with the robot; software **version rollback / replay diff** — same recorded inputs into old and new versions."
- "Every hypothesis becomes a falsifiable prediction before I act — if it's thermal derating, failures should only appear after 30+ minutes with motor temps past the threshold. Then I pull the curve and check."
- "Fixed isn't 'this robot works again' — it's: a monitor now catches this failure class automatically, and the case feeds our failure taxonomy and data engine."

### ★ Q30. "Fleet success rate dropped 90% → 70% over a week. Model got dumber, hardware broke, or the environment changed?"

- "I don't guess — I slice. **Cohort analysis**: success rate cut by robot ID × model version × firmware × site × time."
- "The signatures: one robot down → hardware. Drops tracking a new model version across sites → model regression. One site down across all versions → environment. Gradual drift on old units → wear or calibration."
- "Then align the drop's start time against the deployment timeline — OTA events, config pushes, trigger changes. A changepoint that matches a ship date is nearly a confession."
- "**Counterfactual replay** settles model-vs-environment: feed the new week's recorded inputs to the old checkpoint offline. Old model also fails → world changed; old model succeeds → model regressed."
- "And the meta-answer: canary rollouts make this question answer itself — if every release hits 10% of robots first, the dashboard IS the control group."（05 §4 判别决策表有完整版）

### Q31. "The model looks great in offline eval but performs badly on the robot. Where do you look?"
→ 05 §2 L4：先查 artifact hash/量化导出，再查**预处理不匹配**（经典 silent failure），最后推理延迟 p99——golden input 两端 diff 一把梭。

### Q32. "A failure happens once a day and you can't reproduce it. Approach?"
→ 05 §2 L0 连接器微松动 + §5 案例卡：ring buffer 保现场，故障事件与温度/振动/uptime/姿态做相关性分析，wiggle test。

### Q33. "New checkpoint beats the old one in sim but is worse on real robots. Why might that be?"
→ 三条腿：sim2real gap（03 §4）、真机 eval 方差本身（06 C：50 trials 的 CI 是 ±8pp——先问真机测了几次！）、sim 过拟合（policy 钻 sim 漏洞）。先质疑测量再质疑模型是高手信号。

### Q34. "Here's a loss curve that spikes mid-training / loss falls but task success is flat. Diagnose."
→ 用自己 LLM 训练经验答（data ordering/坏 batch/lr 事件 vs 目标与任务脱钩）；这是主场题，给 checklist 式回答。

### Q35. 现场数据分析: "Here's a CSV of fleet episodes (robot_id, model_ver, site, task, success, ts). Find why failures went up."
→ 05 §4 cohort 切片照搬成 pandas groupby 三板斧：按版本切、按站点切、按时间对齐部署事件；面试前练一遍 10 分钟写完。

---

## ⑤ ML System Design（6 题）

> 四道标准题的完整 playbook（题干变体、估算表、架构图、深挖组件、tradeoff）全在 06，此处只给开场 hook + 必背数字。45 分钟节奏模板见 06 §0。

### ★ Q36. "Design the data collection & telemetry pipeline for 10,000 home robots."

- 开场就算数："5 cameras per robot is ~45 GB/day each — **450 TB/day fleet-wide. Neither feasible nor necessary.** So the real design question is deciding on-device what NOT to upload."
- "Architecture: an on-device **ring buffer** holding 2–4 hours, a trigger engine cutting ±30–60s clips, on-device PII blurring, overnight uploads — 1–2 GB per robot per day, 10–20 TB fleet."
- 七类 trigger 一口气列全："interventions, task failures, high policy uncertainty, safety events, novelty, cloud-pushed campaigns, and a slice of uniform random sampling."
- "Proprioception is the exception — dense, tiny, high value: keep 100% of it. Video is the only expensive thing."
- Privacy 必讲："Blurring happens on-device before upload, and deletion requests pierce the episode → dataset → model lineage."
- Tradeoff 收尾："**Your triggers define your data distribution** — you only see the failures you already knew to look for. That's why random sampling and campaigns exist."（完整版 06 A）

### ★ Q37. "Design the evaluation system for a home-robot policy. How do you know a new model is better?"

- "Structure it as a pyramid: offline metrics → large-scale sim → a real-robot eval farm → human review → fleet A/B. Cost rises, fidelity rises, volume shrinks."
- 杀手数字先砸："To detect 80% → 85% at α=0.05 and power 0.8 you need **~905 trials per arm**. A real robot does 100–200 trials a day. So real robots physically cannot detect a 5-point difference — **sim carries the statistical power; real robots do calibration, gross-regression checks, and the safety gate**."
- "Trial-saving toolkit: paired design — same seeds and object layouts, McNemar's test; sequential testing so you stop early; stratify by task and correct for multiple comparisons."
- "And monitor **sim-to-real correlation itself** as a first-class metric — the day sim rank-ordering stops predicting real rank-ordering, the whole pyramid is lying to you."
- "Last layer is fleet A/B with intervention rate as the primary metric — it's more sensitive and accumulates faster than success rate."（完整版 06 C；桥接自己 LLM eval 经验用 03 §5 话术）

### Q38. "Design the post-training pipeline: fleet data → retrain → safely ship to 10k robots, with rollback."
→ 06 B：manifest 版本化、eval gate、签名 OTA A/B 双分区（回滚=切分区）、金丝雀按 **household** 分桶、主监控指标干预率。

### Q39. "Design a teleoperation system for data collection."
→ 06 D：glass-to-glass <100ms 闭环抓取 / >250ms 不可行、控制通道「最新覆盖+过期丢弃」、watchdog 冻结、1:N 调度。加分动作：主动点出「注意，这家公司明确拒绝入户 teleop（01 §4a），所以我按 staged 环境设计」。

### Q40. "You have 10k hours of teleop and 100 hours of real-robot autonomous rollouts. How do you combine them?"（Skild 原题，02 §4）
→ 03 Stage 3：BC on teleop 打底 → offline RL / advantage 加权吸收 rollouts（失败也有信息）→ 少量 online 纠偏；关键词 distribution shift、RECAP 式 offline-to-online。

### Q41. "Design the continuous-learning loop: fleet failures in, better model out, weekly."
→ 04 §1 飞轮七步 + 06 B 串起来讲；瓶颈点名 auto-labeling 和 eval gate 吞吐，别把时间花在训练 infra 上。

---

## ⑥ Data Collection / 数据分析（6 题）

> 考察点：把数据当产品管理。数字弹药全在 04（teleop 经济学、curation、指标体系）。

### Q42. "You have $1M and 3 months to bootstrap data for a new task (say, folding laundry). Spend it."
→ 04 §3：全摊 $28–60/操作员小时、20–40 demos/h、高质量数据 ~$118–136/h（未证实市场口径）现场算产能；先小批量测 10→60h 边际曲线再 scale（Figure logistics 曲线），留预算给 QA 和多样性采样。

### ★ Q43. "How do you decide what data to collect next?"

- "Failure-driven, not intuition-driven: mine fleet failures, **cluster them by embedding**, rank clusters by frequency × severity × fixability, then launch targeted collection campaigns per cluster."
- "Maintain a **coverage matrix** — task × object × scene — and fill the cells where success is low and data is thin, not the cells that are easy to collect."
- "Track **marginal value**: success-rate gain per 100 added demos, per cluster. When the curve flattens, stop and move budget — diversity beats volume, per the data-scaling-laws result."
- "Dedup aggressively — near-identical demos add cost, not information."
- "And treat **interventions as gold**: they're exactly on-policy failure states with expert corrections attached — the highest-value data class per byte."（完整方法论 + 英文示范段落在 04 §5）

### Q44. "What does an hour of teleop data actually cost, and is it worth it?"
→ 04 §3.3 关键数字表：工资/全摊/单位产出，和 2024 年 ~$340/h 的历史对比；值不值取决于任务边际曲线位置。

### Q45. "100 hours of clean demos vs 1,000 hours of noisy demos — which do you want?"
→ 04 §4 curation：先说 it depends on noise type（次优 vs 错误标签），再站 quality+diversity 一边：SCIZOR 去劣、Re-Mix 重加权可以两头吃。

### Q46. "Robots with cameras inside homes — how do you collect data responsibly?"
→ 04 §6：iRobot×Scale 反面案例 + 1X 四件套（no-go zone/人像模糊/预约授权/分级 opt-in）+ deletion 沿 lineage 穿透；这题答好直接对齐公司拒绝入户 teleop 的隐私立场。

### Q47. "What metrics would you put on the wall for a data engine team?"
→ 04 §7：demos/h、QA 良率、coverage 矩阵填充率、飞轮周期（failure→重训上线天数）、每 100 demo 的成功率边际增益。

---

## ⑦ Research 品味讨论（5 题）

> 考察点：engineering curiosity + 有立场的推理。结构：定义 → 论点 2–3 个 → 立场 → 主动给反方。**不要背结论，背论证。**

### ★ Q48. "What do you think is missing for home robots to have their GPT-3 moment?"（用户点名题）

- 先定义再答："Let me define the analogy: a GPT-3 moment means one generic pretrained model that handles unseen tasks with a tiny prompt or finetune — economically useful without per-task engineering. Robotics today is more like GPT-1: general within a lab, not general across homes."
- "**Missing piece one: the internet of robot data doesn't exist.** Text got trillions of tokens for free; robotics is hand-stitching a pyramid of teleop, human video, and sim — π0-class models train on the order of 10k hours. The data gap is many orders of magnitude."
- "**Missing piece two: evaluation.** There's no cheap, reproducible perplexity-equivalent. You can't run a scaling-law era without a measurement instrument — real-robot evals are expensive, high-variance, and unreproducible. I'd argue this is the most under-invested piece."
- "**Missing piece three: the error-tolerance asymmetry.** A bad text completion costs a re-prompt; a bad grasp costs a broken glass or worse. That caps how much autonomy you can deploy, which caps how fast the data flywheel spins."
- 表立场（顺便贴公司论点）："My bet: the unlock is **fleet-scale corrections** — deployment itself generating the data text got for free. Which is why starting with low-risk, high-tolerance tasks to get robots into homes early is, I think, the right wedge."（公司先做容错 90–99% 任务的路线，01 §4a）
- 主动给反方："The counter-argument: there may be no single 'moment' at all — capability might arrive tier by tier, because physical risk gates deployment per task class. I'd put maybe 40% on that world."

### ★ Q49. "We explicitly don't do in-home teleoperation. Do you agree with that call? How would you get correction data without it?"

- 先 steelman："I think it's the right product call, and I'd steelman it on both grounds: **privacy** — a stranger literally looking into your home is a trust-killer — and **unit economics** — an operator-hour per robot-hour doesn't amortize at fleet scale."（公司立场是事实，01 §4a；两条理由是他们公开说法）
- 再说代价，显示不是拍马屁："But let's be honest about the cost: you're giving up the richest label source in robot learning — on-policy interventions, the RLHF-equivalent. So the training loop has to replace that signal, not just skip it."
- 替代方案给一串："One: lightweight user feedback — a voice 'no, not that one', an app thumbs-down, physically nudging the robot — sparse but it scales with the fleet. Two: self-supervised success detection plus autonomous retry, so failures label themselves. Three: **offline RL on fleet logs** — RECAP-style, where failed episodes still teach. Four: replicate top fleet-failure clusters in sim for targeted practice."
- "Five: correction-grade teleop still happens — just in consented, staged environments, operated by staff, before deployment. My read is that's how they square the circle, given reports of a large contractor workforce doing collection."（后半句是推断——staged 采集属合理推测但未证实，口头要带 "my read is"）
- 收尾表忠诚但留脑子："So: agree with the constraint, and I find it generative — it forces the harder, more scalable version of the data engine. That's the problem I want to work on."

### Q50. "Will the home robot be one end-to-end model, or a modular stack?"
→ 立场题：公司押端到端（01 §4a），但答题别无脑站队——用 03 §3 双系统讲「end-to-end 学习 + 结构化延迟分层」不矛盾；safety layer 永远在学习模型外（06 万能原则）。

### Q51. "Humanoids are raising billions. This company went non-humanoid. Who's right?"
→ 01 §1：他们的原型是轮/履底盘+机械臂（Reuters/诉讼证实）。论证框架：form factor 应由任务分布+成本+可靠性反推，家庭地面多数任务不需要双足；反方（人形通吃人类环境+数据可迁移）也要说到。

### Q52. "What recent robotics result excited you most? Why?"
→ 03 §1 挑一个讲深：推荐 RECAP/π*0.6（贴自己 RL 背景，能讲 offline-to-online 细节）或 Helix 02 的 8 小时自主班次；讲「为什么它改变了我对瓶颈的判断」而不是复述摘要。

---

## 附：面试当天早上的用法（10 分钟）

1. 只看「15 道 ★ 速查表」，每题在脑内用英文说 30 秒版本；说不顺的翻到对应卡片读一遍。
2. Q29 的完整版去 05 §1 把 Beat 1 和 Beat 5 再背一遍（一字不差）。
3. Q36/Q37 的三个数字默写一遍：**450 TB/day、~905 trials/arm、±8pp @ 50 trials**。
4. Q48/Q49 各选定一个立场句，别到现场再想站哪边。
