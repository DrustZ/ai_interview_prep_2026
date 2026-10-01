# Humans& 终轮冲刺（2026-08-10 周一）— 45 分钟消化版

## ① TL;DR（8 行）
1. 日程：Humans& onsite 2h（30min talk = ~15min presentation + 提问，之后数个 1-1）；同日 13:00–17:00 The Bot Company onsite——Humans& 应在上午，今晚和 recruiter 确认开始时间与结束缓冲。
2. 一句话战略：全场我可能是唯一同时懂 post-training 和 HCI 的候选人——presentation 就讲这个交集，别复述第一轮设计题。
3. 最重要三件事之一：把叙事弧钉死——HCI（理解人）→ Reflection post-training（把人的信号变成模型能力）→ 7–8 月限时交付战绩（ship 速度）→ 这正是 Humans& "tightly integrate science and product" 需要的人。
4. 之二：战绩页只用最新素材（Exa work trial 8/4–、AC Express 8/6–8/7、Mirendil 7/19、Anthropic take-home），每条带可验证数字。
5. 之三：1-1 反问要带信息量——核心问题：协作/社会智能没有 verifiable reward，reward signal 从哪来？"multiplayer rollouts" 里人怎么被建模？
6. 避坑：第一轮（7/17）大概率已考 shared workspace / 跨会话 memory 设计——那些五句必背是 1-1 追问弹药，不进 presentation。
7. 钩子：团队含 Reflection 校友（官网确证列了 Reflection）+ Product Engineer JD 原话 "how humans and computers interact" 几乎为 HCI PhD 定制。
8. 时长纪律：Decagon 教训——开场先声明 "I'll take about 14 minutes, then happy to take questions"，每页卡时间。

---

## ② Presentation 骨架（15 分钟，6 页）

### P1. Opening：The thesis（1.5 min）
- "I'm Mingrui. My career has one through-line: I study how people interact with intelligent systems, and I train models to be better at that interaction."
- "Three chapters: an HCI PhD at UW, agent post-training at Reflection.ai, and an intense July–August of timed, independent deliveries I'll show you."
- "I'll take about 14 minutes and leave room for questions."

### P2. Chapter 1 — HCI PhD at UW: understanding people（2.5 min）
- "My PhD was about people: designing interactive systems, running human studies, and learning that evaluation with humans in the loop is a discipline, not an afterthought."
- "Also at Meta Reality Labs I worked on EMG input — literally sensing human signals at the edge. Noisy human data has been my raw material for a decade."
- "The lasting lesson: an ML system is a socio-technical loop — the model, the interface, and the person co-adapt. You can't optimize one in isolation."
- （避开：不讲第一轮聊过的 memory/workspace 设计细节。）

### P3. Chapter 2 — Reflection.ai: turning human signals into model capability（3.5 min）
- "At Reflection I was MTS on agent post-training: mid-training and RL data pipelines — the machinery that converts signals about what's good into a stronger model."
- 主打故事（S1，可讲 90 秒）："We assumed data quality drove RL gains; the data falsified that. I built online difficulty probing — 16 cheap probes instead of 128 formal rollouts, ~12% of the compute — to filter by difficulty instead. I can also tell you its failure mode: it systematically drops the hardest problems."
- "Earlier, at Meta AI, I did SFT+RL for a ranking agent — TableBench #1, published at ACL 2026 — so the post-training claim has a public artifact behind it."
- "I'll respect confidentiality on Reflection specifics, but the methodology is fair game." （保密纪律句）

### P4. Chapter 3 — July–August 2026: proof of ship speed（3.5 min）
- "Anthropic take-home: in 13 hours I built a source-grounded claim-level grader for clinical notes — AUROC 0.838 vs 0.569 for ROUGE (a coin flip), validated with a 137-pair perturbation suite. I reported two of my own priors the data refuted."
- "Mirendil take-home: a chat-trace viewer for RL rollout debugging — 36 commits, 273 tests, production build, 1,202-trace corpus with logprobs, spans, and judge scores, in two days. TypeScript/React — same family as your stack."
- "Two paid work trials this month: Exa — multi-query vector retrieval, training a query tower on a remote H100; and Applied Compute — turning 334 production support traces into a configurable simulator plus evaluation tooling, replay validation at 96.8% over 836 pairs, in ~20 hours."
- "Pattern across all four: independent, timed, verifiable numbers, and I say out loud when the data proves me wrong."

### P5. The intersection — what human-AI collaboration actually requires（2.5 min）
- "Human-centric AI has a specific technical problem: there's no verifiable reward for 'this interaction went well.' The signal lives in human behavior — corrections, adoption, re-asks — and extracting it is jointly an interaction-design problem and a post-training problem."
- "Most people are on one side of that line. HCI people can read the human signal but can't train on it; post-training people can train but treat the human as a static rater. I've spent my career on both sides."
- "That's also why I care about evaluation so much — my grader work is exactly 'how do you measure whether a model understood a person,' which I believe is one of your hardest problems."

### P6. Why Humans&（1.5 min）
- "Your own words: this needs innovations in long-horizon and multi-agent RL, memory, and user understanding — and you'll tightly integrate science and product. That integration is the job I've been training for."
- "I read the NVFP4 RL blog — the 'multiplayer rollouts' line stuck with me; it's the research agenda I'd bet on too."
- "And you have Reflection alumni here, so you can check my references from people who watched me work."

---

## ③ Q&A 预测（6–8 题，英文答案要点）

**Q1. 你同时面这么多家——为什么选我们？**
- "I left my job to run a deliberate search, and I've been transparent about it. The take-homes and trials you saw are that search — each one taught me what I want."
- "What I want is the intersection: human-centered + frontier post-training. Most labs make me pick a side; Humans& is the only one whose founding thesis IS the intersection."

**Q2. HCI 和 post-training 怎么真正结合，不只是简历上的并列？**
- "Concretely: reward design from behavioral signals. HCI gives me the instrumentation — what user corrections, re-asks, and adoption actually mean; post-training gives me the machinery to optimize against them without reward hacking."
- "Second: evaluation. My Anthropic grader is the pattern — replace a proxy metric with a claim-level, human-calibrated one. 'Does the model understand this user' needs exactly that treatment."

**Q3. 没有多模态经验怎么办？**
- "Correct, I haven't trained multimodal models. But my track record this summer is entering unfamiliar verticals and shipping in days — retrieval at Exa, clinical eval at Anthropic. I state my assumptions explicitly and let the data correct me."
- "And your public agenda — long-horizon RL, memory, user understanding — is mostly text-and-interaction-shaped, which is my home turf."

**Q4. 讲一个失败。**
- "Decagon prep: my fine-tuned model matched the ceiling to the digit — too good, so I audited and found data leakage. Same project: measured my DPO preference noise at 46.2%, worse than a coin flip, so the preference data was unusable. Lesson: results that flatter you are the first to audit."

**Q5. 你要 research 还是 product engineer？（他们只有这两个公开 JD）**
- "Honestly, both halves; that's the point of me. Default: research-side on evaluation and human-signal reward, but I ship product-grade TypeScript — Mirendil viewer is the evidence. In a ~25-person company I'd expect to cross the line weekly."

**Q6. 为什么离开 Reflection？**
- "Great team, and I'm proud of the work — but I wanted to move from making agents autonomous to making them collaborative, and to be somewhere the human side is the mission, not a wrapper." （按需补个人真实原因，保持一致。）

**Q7. 社会智能没有 ground truth，你会怎么评估？**
- "Layered: offline replay against logged interactions; behavioral online metrics — suggestion adoption, user-correction rate, re-ask rate; and periodic human calibration of any judge model. Never trust a judge you haven't audited — my ROUGE-vs-grader result is why."
- （注意：若第一轮已答过类似题，开头加 "building on what we discussed last round"。）

**Q8. 产品还没发布（【未证实·截至 2026-08 无公开产品】），你怎么看加入 pre-launch 团队的风险？**
- "You raised $480M with the strongest cap table I've seen this year; the risk I price is thesis risk, and I'm long this thesis. Pre-launch means I can still shape the data flywheel — that's a feature."

---

## ④ 1-1 策略（四类人）

**Founder（Zelikman / Peng / He 等）**：他们要判断的是 taste 和 conviction，不是细节。用 P5 的论点开场，主动聊 STaR 谱系——self-improvement RL 从 math/code 搬到社交场景时 reward 怎么办。Andi Peng（ex-Anthropic，Claude RL/post-training）是最对口的：聊 S1 难度筛选、S3 grader，用她的语言（behavioral RL）。
- "For social intelligence there's no verifiable reward — what's your current best source of signal: human feedback, multi-agent self-play, or product telemetry?"
- "In the multiplayer rollouts, how are the humans modeled — real users, simulated personas, or logged replays?"

**研究员**：直接下沉到方法。可调用：async RL 的 staleness/稳定性（关联 NVFP4 博客的 policy drift 讨论 + 自己 Reflection RL 经验）、eval 方法论（S3 全数字可公开）。别怕说 "I haven't run that experiment, but here's my prior and how I'd test it."
- "How do you evaluate memory and personalization — is there an offline benchmark, or is it all online behavioral metrics?"
- "The blog's 'one-step trap' framing — component interactions over components — how does that change what you log during rollouts?"

**产品工程（Convex/TS 栈）**：证明能 ship：Mirendil viewer（TS/React、273 tests、两天）+ traceviewer 持续演进到 v1.0.0-beta.2。承认没用过 Convex，但事件流/append-only 心智模型相通（valkai_agent 的 JSONL 事件流）。若被问设计题，B3/B2 弹药此时才上场。
- "What does the messaging product look like today — and where does the boundary sit between product events and training data?"
- "What's the hardest thing Convex has forced you to rethink versus a classic backend?"

**Reflection 校友**：最强人脉钩子，但守纪律：聊共同方法论与文化，不聊未公开细节，当面也一样——这本身是加分信号。问他们为什么跳、两家 lab 的研究文化差异。
- "What made you leave Reflection for this — what did the thesis here unlock that agents-for-work didn't?"
- "What surprised you most in your first month here?"

---

## ⑤ Sample code（被问 "show us something" 时）
同目录 `sample_code/` 是一个「从人类反馈中学习的 agent」最小演示——正对 Humans& 的 human-signal→model 主题，可现场跑。讲法直接按 `sample_code/README.md` 里的口径走（运行命令、演示顺序、每步说什么都在里面），不要临场即兴改结构。出门前跑通一遍确认无环境问题。

## ⑥ 当天后勤（3 行）
1. 双 onsite 精力管理：Humans& 结束到 Bot Company 13:00 之间必须吃饭+20 分钟静默复位；今晚 Humans& 材料就到本文档为止，剩余时间全给 Bot Company；今晚 23:30 前睡。
2. 今晚给 recruiter 发一句话确认：presentation 要不要投屏/自带 slides、房间有无屏幕；若无 slides 要求，就按本文档 ② 口述（打印或手机备份本骨架）。
3. 带：笔记本（充满电，sample_code 已跑通）+ 转接头 + 纸质骨架一页；地址与到场时间今晚一并和 recruiter 确认。
