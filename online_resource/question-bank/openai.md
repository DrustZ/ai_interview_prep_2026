# OpenAI 题库（爬取全量）

> 由 raw/build_question_bank.py 从爬取数据自动生成（2026-07 抓取）。每条含来源 URL 可回查原文。

## 流程与情报

### 2026 全套流程时间线：screen→VO→hiring committee→team match；原组满员需重新 match、常见 downlevel
*unknown · 频率: very high (5+ reports) · 2026-06*

thread-1181608（2026-06-29 过经）时间线：Recruiter 主动捞→店面→screen 完第二天通知进 VO→VO 完几天后 hiring committee 过→但被告知原组已满，重新 team match→HR 继续跟进。thread-1180939（2026-06-22 挂经）：被 match 到 Sr Staff 级别导致按更高 bar 评估而挂，正在和 recruiter 谈 down level 到 Staff 找组。thread-1180678：onsite 通过后 team matching = HM chat。Blind 'Openai post onsite'（2026-05-09）：过了面试但原 team 拒了，recruiting 转其他组。interviewing.io：OpenAI 有 downlevel 名声，别锚定当前 title；全程 6-8 周。Blind feed 显示 phone screen 结果 1-3 天，onsite 结果数天到 4+ 工作日。

来源: <https://www.1point3acres.com/bbs/thread-1181608-1-1.html>

### OpenAI 面试流程结构 megathread（2026）：店面=系统设计+coding；onsite 4-5 轮；'Run Test Case vs Run Main'环境坑
*unknown · 频率: very high (10+ corroborating reports) · 2026-05*

Hack2Hire megathread（2026-05）+ 多帖交叉：Stage1 店面 45-60min，最常见=system design + coding 双拼，也有两道 coding；题面可能长达数页——考点之一是从冗长上下文里提取真实问题（一手评论：'前10分钟光读题和澄清，实际问题很简单'）。Stage2 虚拟 onsite 4-5 轮：Coding 1-2 轮（~45min）、System Design 1 轮（~60min）、Deep Dive 1 轮（~60min，完全跟着你的背景走、evaluating 标准不透明）、Behavioral 1 轮（~45min）。编码环境坑：有 'Run Test Case' 和 'Run Main' 两个按钮，Run Main 无输出，多人浪费 5-10 分钟。NG/Intern 轨（recruiter 官方页面）：Application→OA→60min 虚拟 coding→final（coding+behavioral）→team matching→professional references→offer。团队制招聘（group-based hire）时无 team match 步骤、流程更快。HM 轮后通常半周内回复。

来源: <https://www.reddit.com/r/Hack2Hire/comments/1tqdmyr/openai_interview_process_experience_megathread/>

### Reference check：hiring committee 阶段、offer 前、1 manager + 1 peer、电话形式（流程无 2026 变化迹象）
*unknown · 频率: high (4+ Blind threads) · 2026-02*

Blind 'OpenAI reference checks'（jgwe8kc6，2月24日帖）：reference check 在面试全部通过后、正式 offer 前（背调在 offer 后，两者分开）；需 1 manager + 1 peer，最好来自现/最近雇主；真人电话（有人警告别自己冒充）；到 reference 阶段基本意味着过了面试但非保证。其他 Blind 帖佐证：'如果 OpenAI 要进 hiring committee 阶段会要 references（1 manager+1 peer），情况特殊可用类似角色替代'；电话内容：共事时间段、合作体验、你主导的项目、是否愿意再次雇用/共事。一个 2026 时间线样本：周二面完→周三晚 decision→周五完成 reference→周一书面 offer。相关帖：teamblind.com/post/open-ai-reference-checks-k5qab3dh、/post/reference-check-for-open-ai-offer-n6kxj5ra、/post/openaianthropic-offer-chances-reference-check-go224g3c。未发现 2026 年 4 月后流程变化的报告。

来源: <https://www.teamblind.com/post/openai-reference-checks-jgwe8kc6>

### 电面评分标准与挂点（2026 年 4-6 月 Blind 反馈）：coding 有硬性完成度门槛、bar 极高、题可能刚改过
*unknown · 频率: high (5+ reports Apr-Jun 2026) · 2026-06*

(1) Blind 'OpenAI failed interview'（2026-06-16，ML 二面）：除最后一题没写完外全做出来仍次日被拒；Meta 员工评论：'他们对 coding 有很明确的通过标准，你没达到晋级的最低完成度'。(2) Blind 'Failed OpenAI and Anthropic onsite'（2026-04-15，10 YOE 前 Meta）：自认为所有 coding 全解出、SD 答得不错仍挂，无 feedback；评论：'top companies 现在只要 100% 完美的面试'、'多数 OpenAI/Anthropic 员工自己重面也过不了自家 bar'。(3) 1p3a thread-1181416（2026-06-26 店面挂经）：'不知道最近改题了还是大家一直没说破'——暗示 2026 年 6 月底题库可能有更新（正文回复可见，未能读取）。(4) Blind 'OpenAI Phone Screen'（2026-04-08）：coding 强 SD 弱，问能否重面。(5) thread-1180670（2026-06-18 加面）：recruiter 说'coding 不重要 design 好就行'，结果 coding 挂掉加面——不要轻信 recruiter 的降权说法。

来源: <https://www.teamblind.com/post/openai-failed-interview-hae7gz3v>

### （顺带发现，供 OpenAI 线使用）OAI Research Engineer 全套面经帖，2025 下半年
*unknown · 频率: single report · 2025-12*

搜索 GDM 时发现《OAI Research Engineer 全套面经》thread-1168926（约 2025 年末，海外面经版，正文积分墙）。标题表明含 OpenAI RE 全流程。建议负责 OpenAI 的检索线单独深挖此帖及 1p3a 的 openai 题库页（/interview/problems/company/openai，标注 183 questions）。

来源: <https://www.1point3acres.com/bbs/thread-1168926-1-1.html>

### OpenAI 面试流程/轮次/时间线（Hack2Hire 2026 汇总，基于14份一手面经）
*unknown · 频率: single authoritative writeup (aggregates 14 reports 2025-2026) · 2026-06*

完整流程：1) 申请/recruiter screen；2) Phone Screen 45-60min（最常见 System Design + Coding 组合；变体：CICD+Coding、两道 Coding、或 mobile 专项）；3) Virtual Onsite 4-5 轮（通常1天内或分几次）；4) Hiring Committee：需要 2+ 个 strong hire 才能过；5) Team match（1周到1.5个月）；6) offer/拒。各轮：Coding 1-2 轮每轮45min，偏 design-heavy 而非纯算法；System Design 60min（分布式/规模/AI 基础设施，白板或协作文档）；Deep Dive 60min（过往项目/架构决策，内容因背景差异极大）；Behavioral/Culture 45-60min（LP 题 + OpenAI 特有哲学题）。关键细节：Coding 环境有坑——用 'Run Main' 没有输出，必须用 'Run Test Case'，面试官通常不提示，踩坑者损失5-10分钟。题目描述常'像读小说'一样长但核心问题很直接，资深候选人(10+ YOE)常觉得'意外地简单'。System Design 若面试官本人造过该系统，会直接跳过功能需求深挖 scalability，可能60min内答不完。Behavioral 特有哲学题：为什么想加入 OpenAI、如何看待 AI 造成的失业、如何评估某事是否有益于人类——这些不是暖场题，权重等同技术轮。结果：phone screen 几天到1周出；强信号1周内出 offer，进 team match 可拖到1-1.5月；'the team is considering you' 但无下一步通常=停滞；'close call' 是最常见结果，6个月后才能重面。

**解法**: 针对该候选人（post-training/agentic RS）：务必准备 OpenAI 哲学题（AI 与人类福祉/失业观），因其权重等同技术轮且是最常见的 strong-hire 缺口来源；Coding 采用 design-first 拆解（先定义资源模型/API 边界/状态转移再写代码）。

来源: <https://www.hack2hire.com/blog/openai-interview-process-rounds-format-timeline-2026>

### OpenAI 到底考什么 & 为什么被拒（Hack2Hire 2026）
*unknown · 频率: single authoritative writeup (14 reports) · 2026-06*

核心：'过每一轮'不够——hiring committee 要 2+ strong hire，多轮 'close call' 不累加为通过而是直接拒（6个月冷却）。四大评估维度：(1) Design-Heavy Coding——大量题是全新/未在论坛出现过的，考的是对资源约束和 API 契约的推理，不是算法效率/模板识别；要求 multi-part 从零拆解；直接开写代码的人会在 follow-up 约束下暴露漏洞。(2) System Design at Scale——考分布式推理和运维权衡，不是功能覆盖；领域专家面试官深度超出常规 SD 准备。(3) ML Implementation（MLE 岗）——要求现场调试大规模生产代码库、口算矩阵运算复杂度；纯理论 ML 知识没用，缺乏 hands-on 框架经验者会在第一部分就超时。(4) Behavioral & Philosophy Alignment——权重等同技术轮，包含 OpenAI 特有的 AI 影响/对人类有益的问题；泛泛而谈的职业价值观回答会持续失败。'不考'的：算法模板识别速度、孤立的理论 ML 知识、单轮 pass/fail、SD 的功能完整性。真正的过滤器=behavioral/philosophy 轮是最常被低估的 non-strong-hire 信号来源。

**解法**: （我的推断）对该候选人特别关键：MLE 方向要练现场读/改生产级 ML 代码 + 复杂度口算，而非只讲算法原理；behavioral 要用'价值观曾与什么冲突、你如何选择'的具体故事，而非陈述正确价值观。

来源: <https://www.hack2hire.com/blog/what-openai-actually-tests-and-what-gets-candidates-rejected-2026>

### AI Infra 岗 VO 结构（2026-06）：ML coding 60min + System coding 75min + SD 60min + HM + Technical Deep Dive
*unknown · 频率: single report · 2026-06*

thread-1180594（2026-06-18，ai infra 岗）：HR 发的 VO 有五轮——ML coding (60min)、System coding (75min)、System Design (60min)、hiring manager、technical deep dive。楼主注：地里 SWE 一般是 SD+coding，infra 岗多了 ML coding 轮。这是 2026 年 infra/ML 系岗位 onsite 的标准配置参考。

来源: <https://www.1point3acres.com/bbs/thread-1180594-1-1.html>

### AAI org Research Engineer onsite 含 45 分钟 Technical Deep Dive（自选 topic go deep）
*hard · 频率: multiple reports (deep dive 是 RE/RS onsite 标配) · 2026-06*

thread-1181194（2026-06-24）：AAI（Applied AI）org 的 research engineer onsite 要做 technical deep dive，45 分钟，官方建议'选一个 topic and go deep'，楼主求 structure 建议。结合 oavoservice 分析：Research Director/Bar Raiser 轮用三层追问模型——What（1 分钟项目概述+指标）→ Why（为什么选这个方案、量化边界、被否掉的替代方案）→ What if（主方案失效时的 Plan B/C/D）；只吹项目不谈失败模式是主要挂点。interviewing.io 确认 onsite 有准备 slides 的 presentation 环节（技术+业务、tradeoffs、个人贡献）。

**解法**: 45 分钟结构建议：5min 问题背景与为什么难 → 10min 方案空间与决策（含否决项）→ 15min 深入一个核心技术点到可被追问的深度（公式/系统图/数据）→ 5min 结果与量化影响 → 5min 失败教训与 next steps → 留 5min buffer 给打断。准备好 3 层 zoom：能在任意点位被 'why not X' 打断并给出量化答案（我的推断+oavoservice 框架）。

来源: <https://www.1point3acres.com/bbs/thread-1181194-1-1.html>

### 新流程试点：onsite 增加 agentic coding round（beta，给现有 codebase + 允许/要求用 AI agent）
*unknown · 频率: single source (interviewing.io, 2026) · 2026-06*

interviewing.io 的 OpenAI 流程页（2026 年在更新）：OpenAI 正在 onsite 试点 agentic coding 轮——候选人拿到一个现有 codebase，解决'复杂到无法从零手写'的问题，期望使用 AI coding agents；并非所有候选人都会遇到该 beta 轮。除此轮外全程严格禁止 AI 工具。其余流程：recruiter call 30min → tech phone screen 1h (CoderPad) → SD screen 1h (Excalidraw) → onsite 4-6h（coding、SD、presentation slides、HM/BQ）。SD 轮警告：'点名任何具体技术就要准备好深入讲它'。

**解法**: 练习：用 Codex/Claude Code 在陌生 repo 里做中型 feature（定位→改→测试），重点展示任务拆解、给 agent 的 prompt 质量、验证 agent 输出的方法论（我的推断）。

来源: <https://interviewing.io/openai-interview-questions>

### Research/MTS 岗位 loop 综述（2026）：1-2 practical coding + SD + BQ + research/ML 环节（读 paper 或 ML 深挖）；录取率约 0.5-1%
*hard · 频率: aggregate · 2026-06*

jobright.ai 2026 汇总：MTS/Research Engineer 预期 1-2 轮 practical coding（CoderPad，实现小 feature 或修 buggy class，跑真实测试）、1 轮 SD、1 轮 behavioral/culture fit，外加 research/ML 环节——提前发 paper 阅读后讨论（idea/方法/发现/优缺点），或 ML 理论深挖。DL 基础考点：attention 机制与 self-attention 复杂度、vanishing gradients、BatchNorm vs LayerNorm、单卡放不下的训练（DP vs MP）。IGotAnOffer：recruiter screen → 两个 60min tech screen → 3 轮附加技术面，final 共 4-6 小时/4-6 人/1-2 天；RE 平均 18 天 hire（全公司 31 天）。风格：比其他公司更偏 coding 而非 research 讨论，coding 题很难。

来源: <https://jobright.ai/blog/openai-technical-interview-questions-2026-and-how-to-answer/>

### 1point3acres 官方题库统计快照（2026-07-09）：184 题；感染题/GPU scheduling/payment/Why OpenAI 全部 last asked 2026-06-29 Very High
*unknown · 频率: aggregate database · 2026-07*

1p3a interview 产品页（2026-07-09 抓取）：OpenAI 共 184 题（coding 183 页显示 26 可见+44 锁定、SD 16、BQ 2、deep dive 1 类）。免费预览题即感染题（M×N grid，5 sub-parts，60 分钟，标注适用 SWE/MLE/RE/RS，last asked 2026-06-29）。SD 区 top：GPU Scheduling & Messaging（Very High）、Payment System（Very High），另有 WebSocket、Redis、Kafka、RAG retrieval、CI/CD pipeline 主题。BQ：Why OpenAI（Very High，17 讨论）。锁定题涵盖：scheduling、数值稳定性、分布式树操作、transformer debugging、data cleaning、autograd/PyTorch 实现、内存分配、线程、文件系统持久化、图算法、解析、OOP 设计。近期帖子流：7/8 SWE onsite 'DSA Grid Path Maximum Score'（网格路径最大得分，新题名）、7/8 coding challenge '无公开题解的独特题'、6/24 ML technical deep dive、6/23 tech screen 'Virus Spread'。

来源: <https://www.1point3acres.com/interview/problems/company/openai>

### OpenAI interview process & reported questions (interviewing.io company guide)
*unknown · 频率: aggregated from many reports · 2026-01*

Pipeline (mid-senior eng, decentralized/varies by team): recruiter call → technical phone screen (CoderPad; 'more practical than LeetCode', includes information theory & probability) → system design screen (Excalidraw, architect a complete system from scratch) → onsite 4-6 hrs: agentic coding beta round (existing codebase, expected to use an AI coding agent), behavioral w/ senior manager (45 min, ethics & safety in AI, may have veto power), presentation round (45 min, slides expected, technical problem you solved), coding (1 hr, practical ~4-part question, 'time is tight'; weak coding score can cap the offer), second system design (1 hr, may include coding), team-collaboration behavioral (30 min, cross-functional conflict). Math-heavy coding examples quoted: 'Implementing KL divergence for continuous distributions', 'Calculating the expected number of iterations for a probabilistic function', 'Finding the minimum error of a distribution using cross entropy'. Niche topics: time-based data structures, versioned data stores, coroutines/concurrency, OOP. SD screen scenarios: Yelp/Foursquare-like, Twitter, notification systems; 'if you name a technology, be ready to go deep'. Warnings: OpenAI has a reputation for downleveling; 6-8 week timeline; AI use prohibited except agentic beta round.

来源: <https://interviewing.io/openai-interview-questions>

### OpenAI 2026 年中完整面试流程/时间线/信号（1p3a 官方题库 briefing 全文）
*unknown · 频率: 聚合（17+ 来源帖） · 2026-07（题库 last updated 2026-07-08）*

流程：1) Recruiter/HR screen ~30min（why OpenAI/why leave/薪资/地点；HR 事后不给轮次反馈是公司政策）。2) Phone screen coding 60min——几乎总是单一 prompt 占满全场、3-5 个递进小问，前 2-3 问需 clean code+边界处理。3) Final loop '4-6 小时、4-6 人、1-2 天'：1-2 轮 coding（RS/RE 另有独立 ML programming 轮）、1 轮 system design 或 ML system design、1 轮 technical deep dive（做 slides 讲最强项目）、1 轮 HM behavioral（最终关卡）。Infra/AI-infra 轨五轮：ML coding 60min + systems coding 75min（偏 concurrency）+ SD 60min + HM + deep dive。时间线：简历审 ~1 周；recruiter→HR call→电面 2-3 周；电面→loop 1-2 周；loop→决定目标 1 周（team match 可拖 1-2 周+）。默认 virtual，可申请去 SF onsite。信号：deep dive+HM BQ 是 gated（技术轮过了才解锁）；面完次日 HR 要内部 reference = 边缘信号；HM 在 BQ 轮不推销角色 = 负信号；loop 后可能插入'15 分钟 HM call'——说是 no prep 实际计分。2026 年中：recruiter 报价 base 上限 ~$327K(L5)/~$385K(L6)；debrief 周二/周五；技术轮全 positive 仍可能被加轮（director match）后以'not enough positive signal for hiring committee'拒；6 月底案例：组满员后 packet 需 1-2 个 'spike/strong-hire' 信号才进 HC。团队匹配 2026 年中普遍很慢（headcount 紧）。

来源: <https://www.1point3acres.com/interview/problems/company/openai>

### 题库切换时间点判断（2026-04 ~ 06 证据链）：4 月新增 GPU Credits 与 Design Sora，prompt 改为从题池抽题
*unknown · 频率: 聚合推断（40+ 帖） · 2026-04 ~ 2026-06*

关键证据：(a) 官方题库元数据显示 gpu-credits（coding, high, 11 帖）与 design-sora-video-generation（SD, very-high, 19 帖）的 reported_from 均为 2026-04-01——即 4 月初上新，且一直问到 6/26-6/29；(b) 2026-04-14 thread-1172835 回复区：『我看面经说根据 prompt 可以看出来要考哪道题，但是最近好像都是从一个 pool 里选』——4 月中起 prompt 不再唯一对应题目；(c) 2026-04-29 thread-1174920《open爱最近出新题了吗？》：当时大家反馈仍以老题为主；(d) 2026-04-19 thread-1173645：research org 面试已『没有 prompt，变成一个 general 的 PDF』；(e) 旧题淘汰侧：design-cloud-ide last_asked 2026-02-01、code-reading-pytorch-refactor last 2026-03-09、chatgpt-enterprise-rag last 2026-03-22 后未再报；而 infection/payment/chess/monster/social-network/transformer-bug-hunt 等主力题 4-6 月持续被问（last_asked 2026-06-26~29）。结论：2026-04 上旬为增量换题窗口（新增题+抽题池化），非整体题库推倒重来；6/26 挂经（1181416）说的『最近可能改题』更可能指抽中低频新题而非再次大换。

**解法**: 备战策略（我的推断）：主力老题（infection/GPU credits/payment/sora/chess/monster/social network）仍是最高 ROI；同时按题池准备同类变体，不赌 prompt 对应单题。

来源: <https://www.1point3acres.com/bbs/thread-1174920-1-1.html>

### [目标帖 1181416] 2026-06-26 开放爱店面挂经（'回复可见'帖，部分旁路）
*unknown · 频率: single report · 2026-06-26*

Telegram 镜像还原：标题《开放爱 店面 挂经》，2026-06-26 19:00 UTC 发布，标签 码农类General@全职/技术电面/在职跳槽。1p3a 英文镜像 AI 摘要：'Candidate shares insights on a recent openai software engineer tech phone screen. Discusses coding and system design questions faced during the interview.'——即店面为 coding + system design 两轮、双双涉题。该帖即此前 openai:fresh 中提到的『6/26 挂经明示最近可能改题』的原帖。'回复可见'正文无 Wayback 快照、无 Google snippet，未能进一步还原。

来源: <https://www.1point3acres.com/bbs/thread-1181416-1-1.html>

### [高价值] OpenAI Research/RS 轨 2026 面试结构：四轮题型+4 分制+过线 bar（thread-1173645）
*hard · 频率: single report（但称与多位朋友互证题目相同） · 2026-04-19*

Wayback 还原正文开头（2026-04-19 发帖，RS 岗，Fail）：『今年 research org 面试没有 prompt，变成了一个 general 的 pdf。面试题目分成 3 种：AI coding、general coding、math reasoning。一般面四轮：两道 AI coding、一道 general coding、一道 math reasoning。根据我和身边朋友交流，大部分题目都是一样的（题池小、高度重叠）。每道题总分 4 分，一般要全部做出来才有 4 分。bar 至少 4433，4443 比较稳。如果你不能 overfit，这个题目还是很有难度的。』回复区补充：有 6 个 subproblem 的题也有少于 4 个的；AI coding I 是 autograd（60/75min 存疑）；楼主 onsite 挂。镜像摘要另提 entropy calculation 在列。对 RS 候选人这是最重要的单帖。

**解法**: 备战映射（我的推断）：AI coding 池≈{autograd/matmul backward、streaming entropy、transformer bug hunt、noisy-annotator 分类器、1-NN→NN}；general coding 池≈{infection、GPU credits、social network 等 SWE 店面题}；math reasoning≈stopping-time 类概率题。目标 4433=四轮里至少两轮全对。

来源: <https://www.1point3acres.com/bbs/thread-1173645-1-1.html>

### Onsite 全套组合与流程细节实录（4-6 月）：八轮马拉松、reference check、组合样本
*unknown · 频率: 12+ 帖聚合 · 2026-04 ~ 2026-06*

断档期 onsite 组合样本：thread-1172810（4/13 挂）coding=GPU credit + SD=chess + deep dive + BQ；thread-1176087（5/8）machine topology + chess + social network + payment + BQ；thread-1176089（5/8 过）coding+SD+project deep dive+BQ 四轮；thread-1176677（5/14）算法+SD+BQ+project deep dive；thread-1176875（5/15）coding+SD+BQ，SD 重点 fault tolerance 与 IPv4/IPv6；thread-1179591（6/8）GPU scheduling+failure handling 为 SD 重点；thread-1179174（6/4《OpenAI 八轮 挂》）八轮马拉松仍挂。流程细节：thread-1173997（4/22）reference check 很细——按项目问角色/职责，楼主担心简历夸大被戳穿，需找能背书细节的 reference；thread-1175708（5/6）recruiter screen 里突然问技术+SD 问题（非常规）；thread-1179048（6/3）recruiter 阶段问 remote 选项与 role expectations 后被刷；thread-1177414（5/20）VO 后时间线讨论；thread-1176475（5/12）店面过但 HM call 挂（印证'15 分钟 HM call 计分'）；thread-1178850（6/2）工程类电面=coding+SD+BQ 三合一。平台：coderpad+Google Meet（coding）、excalidraw（SD）、部分轮 Colab（recruiter 会提前确认）。

**解法**: 组合规律（我的推断）：onsite=1-2 coding（题池同店面但小问更多）+1 SD（payment/sora/chess 三选一为主）+deep dive+HM BQ；八轮案例说明加轮≠好信号；reference 要提前对齐项目细节口径。

来源: <https://www.1point3acres.com/bbs/thread-1179174-1-1.html>

### OpenAI Senior MLE onsite 完整结构（2026-06）：7 轮含 research presentation 和 real-time sensor system 设计
*hard · 频率: single detailed report · 2026-06*

OfferEngineering 面经：7 轮=Collaboration Interview（研究领域 SOTA、现有方法优劣、未来方向、如何落地产品）、System Design（设计端到端 real-time sensor system：传感器选型、产品用例、ML 需求、模型设计、数据来源、算法选择、延迟/功耗——与目标团队强相关，是硬件约束+实时推理+数据管线+产品需求的混合设计）、Research Presentation（讲自己论文：动机、为什么此方法、实验有效性、结论是否被结果支撑——被 challenge 时要能守住实验设计）、Team Lunch（非正式但仍在评估）、Team Chat×2（行为面：协作/XFN/模糊性处理，其中一场含技术经历）、HM（未来项目、长期兴趣、research vs product 偏好、与团队方向对齐——OpenAI team matching 权重极高）。考生准备：重读领域论文+自己工作的动机与实验选择。

**解法**: Research presentation 备考：为自己每篇工作准备'为什么这个 baseline/这个消融/这个指标'的辩护，预演被质疑实验有效性的应答。

来源: <https://www.reddit.com/r/OfferEngineering/comments/1u2buut/openai_senior_mle_onsite_7_rounds_research/>

### OpenAI Data Scientist 面试 megathread（2026-07）：实验设计/因果推断是最重信号，AI 产品指标案例
*medium · 频率: aggregated megathread · 2026-07*

OfferEngineering megathread（chillinterview 整理）：Stage1 recruiter/HM screen（DS 含义因团队大异：Product/Business/Codex/Platform/Infra/Safety/Preparedness/Core Experimentation）；Stage2 SQL/Python/技术评估（cohort/漏斗/留存、实验 assignment join、窗口函数、去重、数据验证、ChatGPT/API/Codex 产品指标、延迟成本质量信任安全 guardrail）；Stage3 实验/统计/因果（A/B、SRM、power、CI、CUPED/方差缩减、guardrail、异质效应、randomization 不干净时怎么办——弱答案='跑个A/B'，强答案=决策→分析单元→主/次/guardrail 指标→有效性检查→launch/ramp/rollback 判据）；Stage4 AI 产品指标案例（激活留存、开发者生产力、任务完成、模型回答质量、离线 eval vs 在线行为）。对 RS 候选人价值：Stage3/4 与 post-training eval 设计面高度重合。

来源: <https://www.reddit.com/r/OfferEngineering/comments/1us5x6m/openai_data_scientist_interview_process/>

### OpenAI 时间线/薪酬数据点（2026）：referral 两周内必回、无 referral 可能沉没；Staff RS $2.64M、Senior SWE $930K 首年
*unknown · 频率: multiple data points · 2026-03*

时间线（FAANGrecruiting 2026-02 帖）：有 referral 基本保证 2 周内回复；无 referral 有人 2 天内被约店面、也有人 2 周+无声；2026 有招聘放缓传闻（Altman 公开说要 dramatically slow hiring）但 AI infra 仍狂招。薪酬数据点（chillinterview 聚合，二手）：Staff AI Research Scientist：base $440K + RSU $8.8M/4yr → 首年 ~$2.64M；Senior SWE（PhD，8YoE，Bay Area）：base $325K + stock $2.42M/4yr → 首年 ~$930K。流程速度：group-based hire 无 team match、明显更快；final loop 后加'director follow-up'轮=信号不足的红旗（一例最终 no-hire）。

来源: <https://www.reddit.com/r/FAANGrecruiting/comments/1s14p15/26m_openai_staff_ai_research_scientist_offer/>

## Coding 题

### OpenAI · GPU Credits（经典高频题，站内 companyFreq=8/10）
*medium · 频率: very high — 站内标注 OpenAI 出现频率 8/10，被 blog 称为 'the defining signal of an OpenAI coding round' · 2025-11 首发，最近报告 2026-06*

题干：设计管理 GPU credits 的系统。每个 credit grant 有唯一 ID 且在特定时间窗口内有效，grants 时间窗口可重叠。由于网络延迟，add/consume 等事件可能相对其 timestamp 乱序到达并处理。任意时刻可查询某 timestamp 的可用总 credits，或在指定时间 revoke/consume credits。实现 CreditSystem 类：CreditSystem() 初始化；（子操作含）添加 grant、在某 timestamp 消费/撤销、查询某 timestamp 总可用。若某 timestamp 请求扣减超过可用，返回 -1。约束：事件乱序到达。考点：区间管理+时间线聚合、hash map 快速查找、差分数组/前缀和、把有状态更新与瞬时查询解耦。Follow-up：如何把查询优化到 sub-linear（timestamp 范围极大时）？相同 timestamp 并发操作如何处理？分布式最终一致下如何高效持久化？

**解法**: 站内提示：不要把每个 grant 展开成逐个 timestamp，只记录边界变化；把状态分成两套跟踪机制——一套记累积区间效应（差分数组+前缀和），一套记瞬时点扣减。因乱序，先分桶存事件、查询时再按时间线计算。

来源: <https://www.hack2hire.com/question-bank/companies/openai/coding-questions/69117144869dd6a56c434053/practice>

### OpenAI · GPU Credits II（Hard 版，companyFreq OpenAI=10, Perplexity=7）
*hard · 频率: very high — OpenAI 频率标注 10/10 · 2025-11 首发，最近报告 2026-07-02*

题干：同 GPU Credits 设定（grant 有唯一 ID + 时间窗口、可重叠、事件乱序到达），但强化为：模拟一个 grant/usage 事件乱序到达的 credit 管理系统；查询某时间的总余额需按严格时间线顺序 replay 所有已知事件；扣减 credits 时用贪心策略优先消耗最早过期的 credits。实现 CreditSystem 类。考点：HEAP + HASH_TABLE。Follow-up：时间范围到 10^9 如何优化？如何支持并发读写不阻塞整个模拟？若扣减应优先最大额度 grant 而非最早过期怎么改？如何设计持久层在崩溃后高效恢复状态？

**解法**: 站内提示：乱序事件分桶存、查询时才算；按过期时间取/删 grant 用能高效按过期时间检索的结构（min-heap by expiration）；每次扣减都作用于最早过期的 active grant（贪心）。

来源: <https://www.hack2hire.com/question-bank/companies/openai/coding-questions/6913b4290ac116974ccedd12/practice>

### 感染/传染病模拟（infection spread）2026年6-7月仍为电面+onsite最高频题，新增免疫/动态免疫/死亡阈值 follow-up
*medium · 频率: very high (6+ reports in Jun-Jul 2026 alone) · 2026-06*

多个 2026 年 6 月帖确认：thread-1181047（2026-06-23，tech screen）：类似 LC994 腐烂橘子，分部：Part1 几乎 994 原题（多源 BFS 逐天扩散）；Part2 识别'免疫'的 unit；Part3 动态免疫——被感染 x 天之后的 unit 会变免疫，此时不能再用普通 BFS（需逐天模拟+状态机）。楼主止步 Part3。thread-1181839（2026-07-01 过经）：onsite coding 是 infection，共做出 5 问。thread-1180717（2026-06-19）：电面第一轮是传染病，'真的要练熟，不然很多 followup 写不完'。thread-1180678（2026-06-19）：onsite 含'植物感染'。thread-1180670：电面两题之一是'植物'。thread-1181079（2026-06-23）：病毒传播+国际象棋。1p3a 官方题库显示该题 last asked 2026-06-29，频率 Very High，60 分钟 5 个 sub-part 递进。PracHub 2026-06-20 上报变体'Infection Spread Simulation with Death Threshold'（m×n grid，离散天数同时更新，加死亡阈值规则）。

**解法**: Part1 多源 BFS/逐层扩散；后续 part 往往破坏 BFS 单调性（免疫、按天变化的规则、死亡阈值），正确做法是切换为逐天全网格模拟（simultaneous update：先收集本天所有变化再统一应用），把 cell 状态建成显式状态机（susceptible/infected(day)/immune/dead），代码结构留好 rule 扩展点。这是我的推断+帖子共识：拼手速和干净的状态管理，不拼算法。

来源: <https://www.1point3acres.com/bbs/thread-1181047-1-1.html>

### Versioned KV store + follower/followee 社交图查询（social network 题 2026-06 新组合）
*medium · 频率: single report (but both components individually very high frequency) · 2026-06*

thread-1181536（2026-06-28 phone screen）原文：'Coding: Versioned KV store. Maintain a friend follower/followee graph. Query a (a,b) to see if a follows b. Followup: With friends(follower) list and top K recommendations'。即一场电面把 versioned KV store 和 social network 两个已知高频题合并：先实现带版本/时间戳的 KV 存储，再在其上维护关注图，支持 a 是否 follow b 的查询，follow-up 是基于好友列表做 top-K 好友推荐。

**解法**: KV: dict[key] -> sorted list of (version/timestamp, value)，get(key, t) 二分（LC981 模式）；图: adjacency set 存 following；top-K 推荐: 好友的好友计数（排除已关注和自己），heapq.nlargest 按共同好友数取 K——注意讲清楚打分函数可插拔（我的推断）。

来源: <https://www.1point3acres.com/bbs/thread-1181536-1-1.html>

### 既有高频实现题 2026 年持续在库（KV store 序列化/时间版本、in-memory DB/SQL、spreadsheet、web crawler、Excel 依赖）
*medium · 频率: very high (staples, cross-verified 2026) · 2026-06*

Hello Interview 2025-2026 汇编 + linkjob 2026 题库（与 2026 年帖子交叉验证仍活跃）：(1) KV Store：真实 timestamp 的 time-based KV + 文件持久化 + 自研序列化（禁用内置 JSON；delimiter 冲突用 length-prefix 编码 3:key5:value，Redis protocol 同款）+ 多线程锁策略（全局锁 vs per-key 锁 vs 乐观锁）+ future timestamp 查询。(2) In-Memory DB：select(table, where=None, order_by=None)，AND 过滤、多列排序、向后兼容 API。(3) Excel/Spreadsheet：getCell/setCell 支持公式依赖，循环依赖检测，Part2 优化 setCell 使 getCell O(1)（拓扑传播）。(4) 多线程 web crawler：worker pool、visited 去重线程安全、失败处理、限速。这些与 2026 年 6 月 thread-1181536 的 versioned KV 报告互证。

来源: <https://www.hellointerview.com/blog/openai-coding-questions>

### Infection Spread / Cellular Automata（传染病网格模拟）——OpenAI 第一高频 coding 题，33 帖
*medium · 频率: very high（33 帖） · 2025-11-01 ~ 2026-06-29（断档期 4-5 月至少 6 帖）*

官方题库免费预览原文：'M×N grid with infected cells (X) and susceptible cells (./*); infection propagates each day under escalating rules. 5 sub-parts in 60 min; passing bar is typically solving the first 3 with clean BFS.' 角色 SWE/MLE/RE/RS，phone screen+tech screen，60min，status='ai-forbidden'（明确禁 AI 工具），首报 2025-11-01，last_asked 2026-06-29。变体细节（断档期帖子）：thread-1176381（2026-05-11, MLE 店面《开放爱-传染病(1-4问)》）四问=感染扩散/免疫 immunity/康复 recovery/细胞死亡 cell death；thread-1175440（2026-05-03, MLE 挂经）=virus spread simulation + immunity modeling，求迭代感染天数与 herd immunity 时间线；thread-1177818（2026-05-24 onsite）算法轮=植物感染 5 小问（回复区在问第 4 问 death 的条件）；thread-1173136（2026-04-15, B2B 岗挂经）coding 轮即 2D matrix infection，楼主只做到 part3 挂掉，『面完才发现有原题，亏死…把地里题都刷一遍吧』，3 天出 feedback；thread-1174012（2026-04-22）经典 infection+变体+debug；thread-1178391（2026-05-29）geography+plant infection。OJ 变体：'Minimum Time to Infect a Network'、'Plant Infection by Neighbor Count'、'Infection Spread with Immune Units and Expiring Contagiousness'、'Minimum Time to Infect All Plants'、'Cell Simulation / Conway's Game of Life'。

**解法**: 多源 BFS 按天分层模拟；免疫格不传播、康复格设冷却计数、死亡条件按连续感染天数；后面小问常加'感染力过期/免疫单元'等状态机——用 per-cell 状态 struct + 每日事件队列，避免整格全扫。写干净的 simulate(day) 接口便于加规则。（前半来自帖子，扩展为我的推断）

来源: <https://www.1point3acres.com/interview/problems/company/openai>

### OpenAI 最高频编码题：病毒/感染网格模拟（Rotting Oranges 994 强化版，5 段渐进 follow-up）
*medium · 频率: very high (4+ independent reports) · 2026-01*

三个独立来源（2026-01 r/leetcode 店面实拍帖被版主删但评论存活、PichupOrg 完整题面、2026-07 onsite 面经'Virus Spread in a Storage Room'）确认这是店面+onsite 都在用的高频题。完整 5 部分：P1 基础感染——X 感染 8 邻域（或4邻域变体），每天一轮，返回稳定所需天数（多源 BFS，答案=最后一层深度）；P2 加免疫植物 'I'（永不感染、阻挡传播）——好的 P1 抽象应一行改完；P3 感染 D 天后恢复为 '.' 且可再感染——层数计数失效，改事件驱动模拟（按恢复日 keyed 的优先队列 + 每日 frontier），小 D 可能振荡，需 maxDays 上限+重复状态检测并主动说出来；P4 死亡条件——恢复时若 ≥K 个感染邻居则死亡变 'D'（永久墙）；P5 开放优化——每天开始可烧掉一行/列作永久防火带，最小化总死亡数：无闭式解，要给可辩护的启发式（贪心烧感染最多的线）+说明其局限。评分 rubric：核心算法（多源 BFS vs 每天重扫）、可扩展性（cell 类型与步进逻辑分离）、事件建模、边界（全免疫/再感染/振荡）。

**解法**: 骨架：multi-source BFS + (cell, infect_day) 队列；P3 起改为 heapq 事件队列 {day: [(cell, event_type)]}，每天先处理恢复/死亡再传播；把 can_spread_to(cell) 和 on_day_end(cell) 抽成函数让 P2-P4 都是小 diff。

来源: <https://www.reddit.com/r/leetcode/comments/1qsca8h/openai_phone_screen_question/>

### OpenAI · Cellular Infection Spreading（'感染题'，Rotting Oranges 变体，companyFreq OpenAI=10）
*medium · 频率: high — OpenAI 频率标注 10/10（站内整体 freq 显示 3，但公司维度极高） · 2026-04 首发，最近报告 2026-06-18*

题干（LeetCode 994 Rotting Oranges 变体）：研究实验室监测植物病害在网格上的传播。给定 m x n 网格，每株植物为 healthy(0) 或 infected(1)。病害每天同时传播：一个健康植物当其 8 邻域（含对角）中至少 threshold 个当前已感染时，下一天变感染；一旦感染永久感染。求直到疫情稳定所需天数；若第一天评估时没有健康植物能满足 threshold，立即返回 0。约束：更新必须逐天同时应用（不能同一天内连锁）。考点：BFS 分层。Follow-up：网格极稀疏或过大无法全放内存怎么办？threshold 因 cell 而异或依赖历史感染状态怎么改？为何 BFS 比 DFS 更自然地建模'天'的推进？

**解法**: 站内提示：为每个健康 cell 维护'被感染邻居计数器'，评估完整个网格当天后再统一标记感染（避免同一天连锁）；用队列初始化所有初始感染 cell，按 level 处理，用 level 边界递增天数。注意 8 邻域 + threshold 与原版 994（4 邻域+1）不同。

来源: <https://www.hack2hire.com/question-bank/companies/openai/coding-questions/69d4147079bf03c0074bcec0/practice>

### OpenAI · Toy Language Grammar（类型系统递归序列化，companyFreq OpenAI=10）
*hard · 频率: high — OpenAI 频率标注 10/10 · 2025-11 首发，最近报告 2026-07-08*

题干（站内正文因锁定未完整暴露，据 AI insights 还原）：为一个含 primitives、generics、嵌套 tuples 的分层类型系统实现递归字符串序列化。格式化函数签名时，用特定 arrow 语法把参数类型 join 起来并追加返回类型。处理边界：空参数列表、任意深度嵌套、无多余空格。考点：RECURSION + HASH_TABLE。Follow-up：如何扩展支持 arrays 或 function pointers 等额外类型构造子？能否写迭代版或用 Visitor 模式避免极深嵌套的栈溢出？如何把字符串反解析回类型树并校验语法？若要求可定制空格/pretty-print 如何改？

**解法**: 站内提示：每个节点自己知道如何序列化、必要时委托子节点；tuple 节点先收集所有子节点序列化串再用逗号 join 并用括号包裹；用 StringBuilder 递归构建，空集合自然产生 '[]'。

来源: <https://www.hack2hire.com/question-bank/companies/openai/coding-questions/69166e4e10632c00111ca0ea/practice>

### OpenAI · Design In-Memory SQL（LeetCode 2408 变体，companyFreq OpenAI=7, Meta=2）
*medium · 频率: high — OpenAI 频率标注 7/10 · 2025-11 首发，最近报告 2026-07-09*

题干（LeetCode 2408 Design SQL 变体）：设计内存 SQL 数据库，支持建表、带动态类型推断的插入、以及带过滤和排序的查询。实现 SQLManager 类：SQLManager() 初始化空库；createTable(tableName, columnNames) 建表（tableName 唯一，列初始无类型，插入数据时推断为 int 或 string）；（还含）插入行（自增 ID）、select（多条件 AND 过滤 + 按一或多列升序排序）。约束：数值字符串需按数字而非字典序比较。考点：DESIGN + HASH_TABLE。Follow-up：如何安全支持并发读写？如何加 JOIN 或 OR 条件？如何做列级索引优化频繁 SELECT？

**解法**: 站内提示：每表用结构对象把列名映射到位置索引并维护有序行集合；比较/排序前显式把存储值与查询参数转成匹配类型，避免字典序 vs 数值比较错误。建议先刷 LeetCode 2408。

来源: <https://www.hack2hire.com/question-bank/companies/openai/coding-questions/691cfb44ba2fba0a9e173e8b/practice>

### OpenAI · Snapshot Social Graph（版本化关注关系，companyFreq OpenAI=9）
*hard · 频率: high — OpenAI 频率标注 9/10 · 2026-03 首发，最近报告 2026-06-18*

题干：设计追踪用户关注关系并通过 snapshot 维护历史状态的社交网络。支持随时间 follow/unfollow，并能查询某个 follow 关系在任一历史 snapshot 时是否存在。实现 SocialNetwork 类：SocialNetwork() 初始化空网络；follow(followerId, followeeId) 在当前工作态记录关注；unfollow(followerId, followeeId) 记录取消关注；（还含）takeSnapshot 递增 snapshot ID；query 查询某 snapshot 时某关系是否 active。考点：GRAPH + 版本化 + 二分。Follow-up：边数随 snapshot 指数增长时如何省空间？delta 方案 vs 每 snapshot 存全图拷贝的权衡？如何支持并发更新或 rollback？query 能否做到 O(1) 而非 O(log S)？

**解法**: 站内提示：不要每个 snapshot 复制整图，只记录每个 (follower,followee) 对的状态变化——为每对维护 (snapshotId, isActive) 的时间序日志；查询时对 snapshotId 做二分找到 <= 目标的最近一次更新。

来源: <https://www.hack2hire.com/question-bank/companies/openai/coding-questions/69b070d6a4e93c007df3fc35/practice>

### OpenAI · Dependency Version Check（单调二分 + API 调用最小化，companyFreq OpenAI=8）
*hard · 频率: high — OpenAI 频率标注 8/10 · 2025-11 首发，最近报告 2026-05-11*

题干：软件公司管理版本发布，版本按时间升序排列。某关键 feature 在某版本被支持，且一旦支持则所有后续版本都支持（单调）。给定排序的版本字符串列表 versions（格式 'MAJOR.MINOR.PATCH'，如 '103.3.2'），用提供的 VersionChecker API（布尔）找到第一个含该 feature 的版本，并最小化 API 调用次数。考点：BINARY_SEARCH。Follow-up：若列表未排序如何做？API 有严格限流/延迟约束怎么办？能否按字典序或数值比较版本串而非依赖索引？若多个独立 feature 各有起始版本如何改？

**解法**: 站内提示：单调性把数组分成 false 段 + true 段；probe 返回 true 时记为候选答案但继续搜左半找更早匹配；据 probe 结果调整边界，不要提前丢弃当前候选。经典'找第一个 True'二分。

来源: <https://www.hack2hire.com/question-bank/companies/openai/coding-questions/6913fa95fa8a311e42671e68/practice>

### OpenAI · Design Persistent Key-Value Store（二进制序列化持久化，companyFreq OpenAI=9, Onsite）
*hard · 频率: high — OpenAI 频率标注 9/10 · 2025-11 首发，最近报告 2026-07-08*

题干：设计支持通过二进制中间件 medium 保存/恢复数据的持久化 KV 存储。只存 string key 和 string value，能把整个状态序列化成二进制 blob 以在重启间保持持久。提供 Medium 接口（save/retrieve 单个二进制 blob，实现为 InMemoryMedium）。需实现 put/get/shutdown/restore，并在 shutdown 后强制不可变。考点：手动序列化/反序列化变长 string、HASH_TABLE、Onsite。Follow-up：如何支持增量/部分持久化而非 shutdown 时全量重写？如何优化二进制 schema 以在百万小 KV 时减少开销？如何安全支持并发读写而不阻塞序列化？能否扩展支持每条 entry 的过期时间/元数据？

**解法**: 站内提示：定义自描述二进制 schema，每个变长字段前紧跟其精确字节长度；用顺序字节缓冲拼 header + entries 再提交给 medium；string 一律转显式 UTF-8 字节数组，跟踪字节数而非字符数以正确处理 Unicode 和空串。

来源: <https://www.hack2hire.com/question-bank/companies/openai/coding-questions/691523c93f8671d8f7a56570/practice>

### OpenAI · Design Cluster Message Aggregation（n-ary 树分布式消息协议，companyFreq OpenAI=8）
*hard · 频率: high — OpenAI 频率标注 8/10 · 2025-11 首发，最近报告 2026-07-08*

题干：为组织成 rooted n-ary 树的分布式系统实现基于消息的协议。每个节点是一台机器，有唯一 string ID(0..n-1)、父 ID(-1 为 root)、子 ID 列表。节点只能通过消息 API 与直接父/子双向通信。需支持两个由外部客户端向 root 触发的操作：1) 'count' 统计集群所有节点数；2) 'topology' 把集群拓扑重建为字符串。考点：分布式消息传递状态机、DESIGN。Follow-up：如何处理节点失败/丢消息？多操作能否并发互不干扰？重建拓扑串时如何优化带宽？若通信从异步变同步如何改？

**解法**: 站内提示：追踪一条命令从 root 到 leaf 再返回、明确每个节点每阶段需本地存什么；把每个节点当独立状态机，等所有子节点 ack 后再向上转发部分结果；用不同操作 tag/request ID 避免不同命令的响应污染共享状态。

来源: <https://www.hack2hire.com/question-bank/companies/openai/coding-questions/6916140a3f8671d8f7a56641/practice>

### OpenAI · Design ChatBot System（可扩展多 bot 聊天系统，companyFreq OpenAI=8）
*hard · 频率: high — OpenAI 频率标注 8/10 · 2025-11 首发，最近报告 2026-06-12*

题干：构建支持人类用户和自动 bot 的聊天系统。用户向共享 channel 发消息（channel 含多用户多 bot），bot 可响应特定命令。系统需可扩展——新增 bot 类型不改现有逻辑（假设只有一个共享 channel）。实现 ChatApp 类管理 channel 与处理消息：用户发消息先加入 channel 消息日志，随后各 bot 可对消息反应并把自己的输出加入同一日志。需支持三种 bot 类型（含跨 bot 交互，如 MeetBot 影响 AwayBot 状态）。考点：OOD/DESIGN、开闭原则、发布订阅。Follow-up：如何控制多 bot 对同一消息的执行顺序？如何防止 bot 相互触发的无限递归？如何扩展到数千并发 channel 且不同路由规则？如何实现历史检索/持久化而不与 bot 逻辑强耦合？

**解法**: 站内提示：为所有 bot 定义公共接口，别让它们直接相互调用；用 pub-sub——channel 广播解析后的用户命令作为事件，任意注册 bot 消费自己需要的；跨 bot 交互通过发布状态变更事件保持松耦合。

来源: <https://www.hack2hire.com/question-bank/companies/openai/coding-questions/69190ae16723130c5456345b/practice>

### OpenAI · 其余 5 道 Coding（Monster Team Battle / Shard Rebalancing / Design IP Range Iterator / Design a Spreadsheet / Data Labeling Task Scheduler）
*medium · 频率: medium-high — 各 companyFreq: Monster 8, Shard 7, IP Iterator 8, Spreadsheet(OpenAI 5/Ramp 9), Data Labeling 7 · 2026-03 至 2026-05*

OpenAI Coding 题库剩余5题（各有独立 practice 页，postId 见下）：(1) Monster Team Battle [Medium, Simulation, id 69a3a99d6e73e4abccc9c106]：模拟两支有序怪物队伍确定性回合制战斗，按'主攻→死亡检查→有条件反击→二次死亡检查→指针推进'严格顺序处理，输出完整战斗日志；提示：为每队维护独立索引而非改原列表。(2) Shard Rebalancing [Medium, id 69a3c4396e73e4abccc9c14c]：分布式 KV 分片，shards 格式 '<id>:<start>:<end>' 各负责闭区间；实现 rebalance(limit, shards) 使任一 key 被覆盖的分片数不超 limit，并填补 gap；提示：按 start 排序 + min-heap 存 accepted 分片终点，扫描线贪心。(3) Design IP Range Iterator [Medium, id 69a5f7bb3d95612a1782be6a]：前向 IPv4 迭代器，hasNext/next 均 O(1)；提示：把 IPv4 当 base-256 大整数，位移/模256 取回各 octet。(4) Design a Spreadsheet with Formula Evaluation [Medium, LeetCode 3484 变体, id 69f789f030f41dfd539fc6bb]：A-Z 列 1-100 行，cell 可存数值或引用其他 cell 的公式，getCell 时动态求值；提示：DFS 解引用 + getCell 内每次新建 memo cache；follow-up：如何检测/防止循环依赖。(5) Data Labeling Task Scheduler [Hard, Greedy, id 69fc0e7f574d87bc49005a3c]：给 totalTask/totalModel/totalHuman/k，分配 [task,model,human]，使每个 human 完成至少 k 个不重复 task，返回任一合法方案或空；提示：先算单 human 最大可处理 unique task 数判可行性，分轮次每轮每人一个分配，用 task 索引模运算保证 (task,human) 不重复。

**解法**: 各题 practice URL 形如 https://www.hack2hire.com/question-bank/companies/openai/coding-questions/{postId}/practice ；均已含站内 hints + follow-ups。

来源: <https://www.hack2hire.com/question-bank/companies/openai/coding-questions>

### GPU Credit / GPU Credit II —— screen coding 原题续集，follow-up 问真实系统实现
*medium · 频率: high (3+ reports Jun 2026; long-running staple) · 2026-06*

thread-1181418（2026-06-26 全套）：'店面 Coding: GPU Credit II 原题，大约半小时写完 one pass all test cases，然后面试官问现实中怎么实作'（即从内存数据结构升级到真实 billing 系统的讨论）。thread-1179591（2026-06-08 VO）：'Coding 那轮是 GPU Credit，地里原题，不过 follow-up 有点磨'。题面（1p3a interview DB post 7100064 + linkjob）：实现 GPU credit 账本，支持 add(t, amount, expire_time)、cost/charge(t, amount)、balance 查询；credit 有过期时间，扣费用最早到期的 credit 优先；请求可能乱序到达（需按时间轴重放/维护事件排序）；余额不足返回 False。interviewdb.io 'GPU Credit Calculator' 3 周前（约 2026-06-18）仍被报告。

**解法**: 用按 expire_time 的 min-heap（或 sorted list）存活跃 credit，charge 时贪心从最早过期扣；乱序请求是 II 的核心考点——维护全部事件按 timestamp 排序后重放，或每次查询时惰性结算到时间 t。follow-up（现实实现）：事件溯源 + append-only ledger、并发下的悲观锁/序列化、防负余额（我的推断+帖内提示）。

来源: <https://www.1point3acres.com/bbs/thread-1181418-1-1.html>

### cd/pwd 路径解析题 2026-07 仍在考（Blind 新帖，四 part 递进：normalize→绝对路径→~→symlink）
*medium · 频率: high (Jul 2026 Blind + Hello Interview + linkjob 多来源) · 2026-07*

Blind 帖（约 2026-07-04，'OpenAI interview question - Implement a CD command'）：实现 cd(current_dir, destination) -> 归一化绝对路径，四个递进 part，每 part 加一个参数。Part 1：处理 ..、.、重复斜杠 foo//bar、尾斜杠、越过根目录停在 /。例：cd('/usr/local','../A/B/')→'/usr/A/B'；cd('/','..')→'/'；cd('/a/b/c','../../x/./y//')→'/a/x/y'。Part 2-4：绝对路径 destination、~（home）展开、symlink 解析（含环检测；更长/更具体的 symlink 路径优先匹配）。评论（Meta 工程师）：'stack 题起手'，且'这题用了很多年，最早在 Twitter 见过'。Hello Interview 也收录 symlink 版（cycle detection 是难点）。

**解法**: 栈处理 segment；symlink part 用 dict{path_prefix: target}，每次解析后从最长前缀开始替换并重新归一化，用 visited set 检测环；注意 symlink 替换后可能再次产生 ..（我的推断+社区共识）。

来源: <https://www.teamblind.com/post/openai-interview-question-implement-a-cd-command-fuw1arri>

### GPU Credits（GPU 额度消耗模拟）——2026-04 上新，SWE 店面 75min 主力题
*medium-hard · 频率: high（11 帖） · 2026-04-01 ~ 2026-06-26*

官方题库：gpu-credits，coding，high，11 帖，75min phone screen，reported_from 2026-04-01，last_asked 2026-06-26，tags: algorithm/data-structure/simulation。断档期细节：thread-1172810（2026-04-13 onsite 挂经）coding 轮=gpu credit：楼主先 clarify 按什么顺序 consume credit，面试官答'自己看 unit test'；写完过全部 test 后 follow-up 要求把 timestamp 从 integer 改成 float 且『不应该从 timestamp 0 开始 loop』（即事件驱动而非逐 tick 模拟）；平台 coderpad+google meet。thread-1174310（2026-04-24《被贵版误导》）称做的是'GPU credit II'变体，test case 有坑+时间紧。thread-1176829（2026-04 电面挂经）coding=GPU Credit，SD=Payment System。thread-1176291（2026-05-11）同组合。thread-1171972（2026-04-08 电面）60min coding + 60min SD：GPU credit management + scalable AI inference design。

**解法**: （我的推断）credit 有授予时间/过期时间/额度，请求按时间戳消耗：维护按过期时间排序的 min-heap，先消耗最早过期的 credit；float 时间戳 → 不能按整数 tick 循环，把 grant/expire/usage 全部作为事件排序后线性扫描；II 变体大概率加 refund/优先级/并发 job。先读懂给定 unit tests 再动笔是本题的隐性考点。

来源: <https://www.1point3acres.com/bbs/thread-1172810-1-1.html>

### Monster Battle System（打怪模拟，OOP 多小问）+ 常见 chess follow-up
*medium · 频率: high（9 帖） · 2025-12-18 ~ 2026-06-29*

官方题库：monster-battle-system，coding，high，9 帖，phone screen+onsite coding，首报 2025-12-18，last_asked 2026-06-29，tags: oop-design/simulation。断档期细节：thread-1176587（2026-05-13 店面挂经）：用 C++ 做 monster battle，需自己写 custom test cases，附 chess 相关 follow-up；thread-1178049（2026-05-26 MLE 过经）回复区确认 monster battle 与'捉虫'同池出现，提问者问'有没有 code template 和 test，还是从头写'。OJ 镜像标题：'Monster Fighting (Multi-part)'。

**解法**: （我的推断）实体类 Monster/Player/Battle + 回合制状态机，逐小问加技能/属性克制/队伍；评分点在类设计清晰、可扩展、自带单测。C++/Python 皆可但要求能现场写测试。

来源: <https://www.1point3acres.com/bbs/thread-1176587-1-1.html>

### Social Network Follow Graph（关注图 + snapshot 版本化）——SWE/RE 店面 60min
*medium · 频率: high（13 帖） · 2026-01 ~ 2026-06-28*

官方题库：social-network-follow-graph，coding，high，13 帖，60min phone screen，roles SWE/RE，tags: algorithm/graph/hashmap，last_asked 2026-06-28。断档期细节：thread-1172554（2026-04-11 电面）：coding 'a social network with snapshots'（关注关系图支持打快照/回溯），同场 system design 是 'elo bucket matching'（按 elo 分桶匹配对手）；thread-1172752（2026-04-13）social media network coding 变体；thread-1176085（2026-05-08 店面）coding social network + SD crossword puzzle。OJ 镜像：'Social Network Query/Computation (Graph-Based Social Problem)'；external 库有 'Social Network with Snapshots' 独立条目。

**解法**: （我的推断）follow/unfollow/getFollowers + snapshot()：为每条邻接表维护版本号或 copy-on-write（persistent data structure），snapshot 返回句柄，查询带版本参数；进阶问共同关注/N 度关系用 BFS。

来源: <https://www.1point3acres.com/bbs/thread-1172554-1-1.html>

### Toy Language Type Inference（玩具语言类型系统）——SWE/RE 店面 60min
*medium · 频率: high（8 帖） · 2025-12 ~ 2026-05-26*

官方题库：toy-language-type-inference，coding，high，8 帖，60min phone screen，roles SWE/RE，tags: algorithm/oop-design/recursion，2025-12-01 ~ 2026-05-26。佐证：thread-1172199（2026-04-09, Applied AI Research Engineer 店面挂经）镜像摘要：'machine learning debugging and coding on toy languages'——RE 店面同场考 ML debug + toy language。external 库 'Toy Language Type System'（tid 7100065）。

**解法**: （我的推断）解析表达式 AST 后做类型推断：递归下降 parser + 环境 dict，小问递进加函数类型/泛型统一（unification）；重点是干净的递归结构与错误报告。

来源: <https://www.1point3acres.com/bbs/thread-1172199-1-1.html>

### OpenAI 编码题库（2026 面经提及名称）：GPU Credit、Machine Topology、Sequential IPv4 Generator、implement cd command
*medium · 频率: high (each named 1-2x, pattern 5+) · 2026-06*

OfferEngineering 2026-06/07 面经点名：(1) 'GPU Credit'（onsite coding，senior SWE，考生 20 分钟提前完成含 debug 仍挂——沟通思路不足；推断为 credit 授予/消费/过期的区间记账题，类似 LC 1109 航班预订+过期语义）；(2) 'Machine Topology'（店面 coding，细节未披露，推断为机器连接图的连通性/拓扑排序类）；(3) Design a Sequential IPv4 Generator（店面 coding，'classic'——顺序生成/分配 IPv4 地址，处理保留段、回收、并发分配 follow-up）；(4) implement a cd command（PichupOrg 题库样题，路径规范化=LC71 Simplify Path 扩展：相对/绝对路径、.和..、follow-up 符号链接解析与环检测）。另有 2025-03 报告：'in-memory data store 类 class 设计题'、'file downloader library'、店面题=类设计不难但实现量大。共同特征：不是 puzzle，是'写大量代码的真实工程题'，重复率高（教练：'cover 他们的题库这个 loop 很 crackable'）。

**解法**: IPv4 generator：u32 计数器 + 跳过保留网段 + 释放池（heap/free list）+ 线程安全；cd：栈处理 '..'，symlink 解析加 depth limit 防环。

来源: <https://www.reddit.com/r/OfferEngineering/comments/1udnofy/openai_senior_swe_full_journey_smooth_sora_design/>

### OpenAI intern/NG 编码轮难度与真题风格：60min DSA（graph/DP hard）、CoderPad 递增难度多题、OA 防作弊
*hard · 频率: high (6+ threads) · 2026-01*

多帖（2025-10~2026-02）：intern 技术店面=60min DSA，'比 LC tagged 难'，建议练 graph 和 hard DP；CoderPad live，'several problems in increasing difficulty'；2024 final：Q1 medium + Q2 hard；2025-03 final 复盘：7 个 LC tag、偏 program design；OA（EMT intern）类似录屏 CodeSignal：摄像头+屏幕录制+禁复制粘贴。NG 完整时间线实例（2026-01 offer）：12/15 60min coding → 01/13 VO（60min coding + 30min behavioral）→ 01/20 15min recruiter call + offer。行为面真题：'你认为 AI 是不是可能毁掉美国经济的泡沫？'。背景数据点：拿到面试者多有 FAANG+量化实习。

来源: <https://www.reddit.com/r/csMajors/comments/1qk24qy/openai_swe_intern_interviews/>

### [目标帖 1179374 已完全旁路] Memory Allocator：75min 店面设计内存分配器（malloc/free + coalescing）
*medium · 频率: medium（6 帖，2025-12 ~ 2026-06-11） · 2026-06-06*

thread-1179374（2026-06-06,《OAI screen》, Positive/Easy/Pass, hardware 相关 infra 岗）Wayback 快照回复区还原：题为设计 memory allocator，要求 malloc/free、free block 合并（coalescing）、减少碎片（fragmentation reduction）；楼主用 C++，『每次从头 linear scan 来 malloc 和 coalesce free memory block』达到 O(N)；75 分钟轮，仅最后 5 分钟 Q&A。官方题库：memory-allocator，coding，频率 medium，6 个来源帖，75min phone screen，首报 2025-12-01，last_asked 2026-06-11。相关 OJ 变体标题：'In-Memory Memory Allocator with malloc/free, First-Fit and Best-Fit'、'Implement malloc and free with First-Fit Allocation and Discuss Best-Fit Optimization'、'Design a Memory Allocator with Coalescing'。

**解法**: 维护按地址有序的 free list（链表或有序 map）；malloc 用 first-fit 线性扫描并分裂块；free 时与相邻 free 块合并（检查前驱/后继地址连续性）；follow-up 讨论 best-fit 的碎片-速度权衡、size-class/segregated free lists、O(log n) 用平衡树/按大小索引。（快照含楼主亲述+我的补全）

来源: <https://www.1point3acres.com/bbs/thread-1179374-1-1.html>

### Data Labeling Task Scheduler（数据标注任务调度器）——SWE/RE 60min
*medium · 频率: medium（7 帖） · 2026-02 ~ 2026-05-31*

官方题库：data-labeling-task-scheduler，coding，medium，7 帖，60min，phone screen+onsite coding，roles SWE/RE，tags: algorithm/simulation/scheduling，2026-02-01 ~ 2026-05-31。external 库独立条目 'Data Labeling Task Scheduler'（tid 7100239）。另 external 库含 'LLM Inference Timeout and Restart Strategy'（tid 7100488）同属调度/容错类新题。

**解法**: （我的推断）任务带优先级/技能匹配/超时重派：优先队列 + worker 池模拟，小问递进加'标注员标错要重标/任务依赖/公平性'；与 GPU credits 同族的 event-driven 模拟题。

来源: <https://www.1point3acres.com/interview/problems/company/openai>

### Shard Rebalance（分片再均衡）——SWE 店面 60min，问到 2026-06-26
*medium · 频率: medium（4 帖） · 2026-03 ~ 2026-06-26*

官方题库：shard-rebalance，coding，medium，4 帖，60min phone screen，roles SWE，2026-03-01 ~ 2026-06-26。OJ 镜像 'Shard Rebalancing'（tid 7100238）。3 月上新、持续到 6 月底，属于'新题池'成员，值得优先准备。

**解法**: （我的推断）给节点→shard 分布，目标最小迁移量达到均衡：贪心从超载节点移最大/最合适 shard 到欠载节点（two-pointer/heap）；follow-up 常加副本约束、一致性哈希对比、迁移代价加权。

来源: <https://www.1point3acres.com/interview/problems/company/openai>

### IPv4/CIDR Iterator（55min 店面）与 Version Dependency（75min 店面）
*medium · 频率: medium（各 5 帖） · 2026-01 ~ 2026-05-15*

两道 medium 店面题：(1) ip-address-cidr-iterator，coding，medium，5 帖，55min phone screen，SWE，tags: algorithm/string/bit-manipulation，2026-02-01 ~ 2026-05-15；OJ 镜像 'IPv4 Address Iterator with CIDR Support'、'Restore Valid IPv4 Addresses'。(2) version-dependency，coding，medium，5 帖，75min phone screen，SWE/RE，tags: algorithm/graph/dependency-resolution，2026-01-01 ~ 2026-05-08。

**解法**: （我的推断）CIDR iterator：把 CIDR 段转成 [start,end) 整数区间做惰性迭代器，支持多段合并去重（排序+merge intervals），位运算取网络地址；version dependency：包版本约束解析→构建依赖图，拓扑排序+回溯选版本（类似简化版 pip resolver），环检测报错。

来源: <https://www.1point3acres.com/interview/problems/company/openai>

### Distributed Cluster Count / Machine Topology（机器拓扑推理 + 流式数据）
*medium · 频率: medium（5 帖） · 2025-10 ~ 2026-06-19*

官方题库：distributed-cluster-count-topology，coding，medium，5 帖，onsite coding，SWE，tags: tree/tree-broadcast/distributed-systems/recursion，2025-10-05 ~ 2026-06-19。断档期细节：thread-1171426（2026-04-03 店面）镜像摘要：'machine count and topology, stream data handling, and distributed systems debugging'——楼主求助 stream of incoming data 和 debug 部分；thread-1176087（2026-05-08《开放爱全套》onsite）四轮=machine topology + chess + social network + payment system + BQ，feedback 很快。OJ 镜像 'Machine Topology Reasoning (Topology / Dependency Graph)'。

**解法**: （我的推断）由心跳/邻接消息流推断集群拓扑：维护并查集/树结构统计连通分量数；tree-broadcast 小问=设计沿树广播消息的递归/容错；流式部分=乱序消息按时间窗聚合去重。

来源: <https://www.1point3acres.com/bbs/thread-1171426-1-1.html>

### 新题：monster battle / battle simulation（2026年6月电面）
*unknown · 频率: 2 reports (Jun 2026) · 2026-06*

thread-1180067（2026-06-12 电面）：'SD-design Sora, Coding-monster battle'。interviewdb.io 独立收录 'Battle Simulation'（coding，phone/onsite，最后上报约 2026-06）。题面细节两个来源都未公开完整版本，推测为回合制战斗模拟类多 part 实现题（实体属性、回合规则、状态更新），与感染题同属'规则模拟'家族。这是已知题库外的较新条目。

**解法**: 按 simulation 题套路准备：清晰的实体类建模（Monster/Player: hp, attack, speed...）、回合循环、同时结算 vs 顺序结算的规则澄清、规则可扩展的接口设计。先问清 tie-break 和死亡时机（我的推断，无公开题面）。

来源: <https://www.1point3acres.com/bbs/thread-1180067-1-1.html>

### 新题：机器拓扑（machine topology）+ remote IDE 环境（2026年5-6月 screen）
*unknown · 频率: single report (Jun 2026); node-counting 家族另有多个历史报告 · 2026-06*

thread-1180678（2026-06-19 发帖，面试在 5 月底 6 月初）：'店面是 机器拓扑 + remote IDE'。即 screen 在远程 IDE 环境（非 CoderPad 裸编辑器）中做一道机器/节点拓扑相关题。可能与已知的'分布式树上数点/异步消息传节点数'（distributed node counting, linkjob Q6：树形集群 parent-child 异步消息，实现 receiveMessage/sendAsyncMessage 统计总机器数）同族。onsite = BQ + Tech Presentation + 支付系统 + 植物感染，之后进 team matching（HM chat）。

**解法**: 若是异步消息数节点：每个节点向所有 child 发 count 请求，收齐 child 回复后向 parent 回复 1+sum(children)；需处理 leaf 直接回 1、用 pending counter + 回调而非阻塞等待（我的推断）。remote IDE 意味着可能要跑真实测试、读已有代码，练习在陌生 codebase 里快速定位。

来源: <https://www.1point3acres.com/bbs/thread-1180678-1-1.html>

### 新题：IP address 题（screen coding，2026年7月过经）+ chess design 作为 screen SD
*unknown · 频率: single report for IP address; chess 多次出现 (2 reports Jun-Jul + PracHub) · 2026-07*

thread-1181839（2026-07-01 过经）：'店面 coding 是 IP address，design 是 chess。Onsite coding 是 infection（做出 5 问），design 是 design Sora（核心 GPU 调度）'。IP address 题细节未公开（可能是 IP 解析/校验/CIDR 范围合并/restore IP addresses 类）。确认象棋（chess）已从 onsite 题挪到 screen 的 design 轮也在考。PracHub 另收录 'Design Online Chess Matchmaking'（2026-05-24，hard：ranked/casual 匹配后端）。

**解法**: IP 题准备三个方向：validate/parse IPv4/IPv6、CIDR 区间合并与查找（trie 或排序区间）、LC93 restore。chess design：棋盘表示、Piece 类继承 vs 数据驱动 move rules、move 合法性（含 check 检测）、游戏状态机；matchmaking 变体加 ELO 桶+等待时间放宽的匹配队列（我的推断）。

来源: <https://www.1point3acres.com/bbs/thread-1181839-1-1.html>

### 新题（2026-05/06）：memory allocator 实现（malloc/free + free-block coalescing）
*medium · 频率: 2 reports (May 2026) · 2026-05*

PracHub 两个版本：'Implement a Simple Memory Allocator'（2026-05-29，SWE，medium：在固定大小 heap 上实现 malloc/free）；'Implement A Contiguous Memory Allocator With Free-Block Coalescing'：管理 N 字节连续内存，初始全空闲，alloc 返回偏移、free 后相邻空闲块合并。1p3a 官方题库的 membership 区也列有 memory allocation 类题。属于 2026 年较新的 infra 实现题方向。

**解法**: free list（按偏移排序的空闲区间，first-fit/best-fit），free 时与前后邻居合并；进阶用按 size 的平衡结构或 buddy allocator 谈 fragmentation tradeoff（我的推断）。

来源: <https://prachub.com/interview-questions/implement-a-simple-memory-allocator>

### 新题（2026-06/07）：refactor chatbot into clean OOP / extensible ChatApp —— 重构与代码质量轮
*medium · 频率: 2-3 reports (Jun 2026) · 2026-06*

PracHub：'Refactor Chatbot into Clean OOP'（2026-06-22，SWE，medium）：给一段 messy chatbot 代码，在保持行为不变的前提下重构；'Implement an Extensible Chatbot App'：实现 ChatApp 类，处理用户消息并路由到多种 bot responder，要求支持多 bot 类型可扩展。interviewdb.io 另有 'General Template'（3 周前）和 'Editor'（2 个月前）两个未公开题。coditioning 也确认 OpenAI 有'给一段代码：debug、提性能、重构但不改行为'类题。对应 2026 年'从零写'向'读改现有代码'的趋势（与 agentic coding 试点同向）。

**解法**: 路由用 registry/strategy 模式（bot 注册 handler + can_handle 谓词），消息管线 middleware 化；重构题先补测试锁行为再动刀，边讲边归纳 code smell（我的推断）。

来源: <https://prachub.com/interview-questions/refactor-a-chatbot-into-clean-object-oriented-components>

### interviewdb.io 2026 年 6-7 月新上报：Board Game（7 月上报）、Biological Hazards（OA）、File Directory Utility Command
*unknown · 频率: each single recent report · 2026-07*

interviewdb.io OpenAI 页（'Updated today'，2026-07-09 前后）：'Board Game'（coding，phone/onsite，昨天上报=2026-07-08）；'Battle Simulation'（1 个月前）；'Biological Hazards'（OA 形式，3 个月前≈2026-04——注意出现了 OA/异步笔试形式）；'File Directory Utility Command'（1 个月前，即 cd 题）；'GPU Credit Calculator'（3 周前）；'General Template'（3 周前）；'Editor'（2 个月前）；'Beat Notations'（4 个月前）。System design 区多题被锁（3-4 个月前）。'Biological Hazards' 疑似感染题的 OA 版本。题面均在付费墙后。

来源: <https://www.interviewdb.io/question/openai>

### 2026-04 中文汇总确认的 coding 题谱系：感染扩展、toy language/类型推断、iterator/allocator/KV/时间序列——'重点不在算法'
*medium · 频率: aggregate (Apr 2026) · 2026-04*

learncswithus 2026-04-04 OpenAI 面经汇总（整理自 1p3a 等）：coding 三大类——(1) 感染问题：2D grid 多源 BFS + 免疫 unit、感染阈值等扩展；(2) 结构设计：toy language、类型推断（AST、泛型绑定）——确认已知 toy language 题 2026 年仍在库；(3) 工程实现：iterator、memory allocator、KV store、时间序列系统。特征：'重点不在算法'而在问题建模、状态管理、边界处理。SD 覆盖 chat 系统、URL shortener、支付、日历、在线游戏，强调实现细节而非纯高层架构。ML 岗：NumPy 基础实现、数据分析、代码 debug 而非复杂建模。流程：recruiter call → 2 轮技术（coding+SD）→ onsite（coding、SD、technical deep dive、HM），全程约 4-5 周；面试官友好但拒信不透明（有人每轮反馈积极仍被拒）。

来源: <https://learncswithus.com/2026/04/04/openai-interview-problem/>

### OpenAI practical coding set reported in 2026 compendium (100+ real interviews)
*medium · 频率: multiple reports · 2026*

Reported OpenAI coding rounds: 'KV Store Serialize/Deserialize'; 'In-Memory Database: implement SQL-like operations' (cf. LeetCode 2408 Design SQL); 'Versioned key-value store (Time-Travel Hash variant)' (cf. LC 981 Time-Based KV Store); 'Credits management system' — track credit state across issued/used credits with different expiration rules, complexity increases across iterations; 'Refactoring round: 100-120 lines of intentionally convoluted, deeply nested code — refactor for maintainability while keeping existing tests green and extending to new ones.' Also OpenAI behavioral: 'Is there an actual eval framework, or is it vibes-based?' (asked about your projects) and 'Give a specific example of conflict with another person, how resolution took form, and the rationale behind your choices.'

**解法**: Versioned KV: dict key -> sorted list of (timestamp, value), binary search on get(key, ts); TTL = store expiry and filter lazily. Credits system: ordered list of credit lots with expiry, consume greedily from earliest-expiring lot; design for O(log n) via heap keyed on expiration.

来源: <https://adilshamim8.medium.com/every-ai-engineer-interview-question-you-need-to-know-in-2026-from-100-real-interviews-b5b7ae4b961a>

### Onsite coding 长尾题清单（单/低频，来自官方题库+external 库）
*medium-hard · 频率: low/single 各 1-3 帖 · 2025-10 ~ 2026-06*

单报/低频但在 2026 仍在池内的 onsite coding 题：ModalLock and FairModalLock（concurrency/threading/python，hard，2026-03-30，单报）；Resumable Iterator with Multi-Dimensional Support（low，3 帖，last 2026-06-20，iterator/oop/recursion）；Implement a cd Command（路径解析 stack，2025-12-27 单报）；OpenSheet: Spreadsheet with Cell Dependencies（2025-11-21 单报，graph/dfs/topological-sort）；In-Memory Database with SQL Operations（low 3 帖）；Durable Key-Value Store Serialization（io/filesystem/persistence，low 3 帖）；Chat Bot System Refactoring（refactoring/testing，low 3 帖）；Time-based KV Store（low）；Code-reading PyTorch Refactor（RE/MLE 60min，low 2 帖，last 2026-03-09）。另 DS 轨（thread-1178922, 2026-06-02 过经）：case study + 基础 SQL（filtering/aggregation/join/window）+ debug A/B test Python 代码。OJ 库另含 'Message Event Aggregation in a 5-Minute Sliding Window'、'Design a Distributed Rate Limiter with Persistence (Clock Skew, Redis Fallback)'、'Draw Paths / Strokes on a Set of Points'、'Maximum Falling Path with Limited Vertical Jumps and Bonus Scoring' 等。

**解法**: ModalLock（我的推断）：可重入模态锁+公平版=条件变量+FIFO 等待队列，考 threading 正确性；resumable iterator：迭代器可 checkpoint/restore（序列化游标栈），支持嵌套结构。

来源: <https://www.1point3acres.com/interview/problems/company/openai>

### Fullstack/Frontend 轨：看视频复刻 ChatGPT 流式聊天 UI（背靠背两轮 tech screen）
*medium · 频率: 3 帖 · 2026-03-31 ~ 2026-05-18*

thread-1177102（2026-05-18《开放爱前端 Tech Screen 背靠背》，Positive/Fail）Wayback 还原：recruiter 聊完同一天约背靠背两轮。第一轮 FrontEnd Coding：给一个视频——简单输入框+submit button（的 ChatGPT 式界面），照着实现；含 streaming text response 处理（回复区确认有提供 utility 直接调用，不用纯手写 SSE 解析）；挂点提示：『（要把）情况都主动讨论出来，而不是面试官提出 follow-ups 让我们解决』——主动性是评分项。第二轮镜像摘要：SD 聚焦 ChatGPT 功能与异常处理。同轨佐证：thread-1170911（2026-03-31 fullstack）React coding + ChatGPT-like 应用 SD（错误处理重点）；thread-1171773（2026-04-06 fullstack 两轮 phone screen）：coding + AI playground 功能 + prompt 共享隐私设计。

**解法**: （我的推断）React 组件：消息列表+受控输入+streaming append（用给定 utility 消费 chunk 流）；主动讨论：loading/error/retry、乱序 chunk、自动滚动、防抖、可访问性；SD 轮讲 SSE vs WebSocket、断流恢复、token 计费显示。

来源: <https://www.1point3acres.com/bbs/thread-1177102-1-1.html>

### 店面 coding+SD 60min 双轮标准配置：4-6 月实测题目组合清单
*medium · 频率: 15+ 帖聚合 · 2026-04 ~ 2026-06*

断档期店面组合实录（镜像摘要还原）：4/8 thread-1171972：GPU credit management coding + scalable AI inference SD；4/11 thread-1172554：social network snapshots + elo bucket matching；4/16 thread-1173146：SD=design chatbot（hack2hire 风格）；4/22 thread-1174105：经典算法（return 条件有坑）+ 神经网络分类 bug fixing——SWE 店面也可能抽到 ML 味题；4/24 thread-1174280：systems coding（state management+性能）；5/5 thread-1175677：Slack-like messaging SD + chatbot coding；5/8 thread-1175992：infection coding + payment SD（大交易文件生成）；5/9 thread-1176099：distributed rate limiting SD；5/13 thread-1176587：monster battle（C++）+chess follow-up；5/29 thread-1178391：geography+plant infection coding + scheduler failure cases SD；6/3 thread-1178966：architecture + coding 双轮。prompt 情报：4/14 thread-1172983 infra 组新 prompt=practical systems coding+debugging；5/22 thread-1177617：60min live coding prompt 强调 real-world twists；4/26 thread-1174549 与 4/28 讨论：部分 recruiter 只给 generic prompt，无法反推题目（题池化的又一证据）。

**解法**: 配置规律：店面=60min coding（infection/GPU credits/social network/monster 四大主力）+60min SD（payment/sora/chess/rate limiter/Slack）；4433 心态：coding 至少干净做完前 3 小问。

来源: <https://www.1point3acres.com/bbs/thread-1175992-1-1.html>

### OpenAI 其他角色轮次数据点：React 前端考察（E5 意外挂）、支持工程师 vibe-coding debug（race condition 脚本）、T&S/TPM 案例面
*medium · 频率: scattered single reports · 2026-03*

(1) r/leetcode E5/6 面经（2025-09，Meta/Rippling/Datadog offer holder）：OpenAI 店面挂在'比预期更重的 React 技能考察'——全栈岗会真考前端；同帖 Anthropic 挂在没准备的 concurrency。(2) Support Engineer（2026-03）：vibe coding 轮较易（debug 脚本/写自动化，一例：排查间歇性失败的 Python 脚本=race condition），但 HM 轮 bar 极高（考生挂在 HM，建议深学 OpenAI API）。(3) TPM/PM（2026-06）：recruiter LI 主动联系→次日店面→30min HM 行为面→final loop=两个 45min case 轮+两个 30min 行为轮（其一含 mini case)，签 NDA，recruiter 发详细 prep 材料。(4) Trust & Safety Analyst 帖无实质回复。

来源: <https://www.reddit.com/r/leetcode/comments/1norf2d/e56_interview_experiences_at_meta_rippling_datadog/>

### OpenAI 店面题面超长化趋势（2026）：多页题干埋一个简单问题，考'从噪声中提取真实需求'
*medium · 频率: 2+ reports · 2026-05*

Hack2Hire megathread 一手评论（2026-05）+ 官方总结确认：店面 coding 题干可以长达数页，第一次见这种格式的考生前 10+ 分钟全花在读题和澄清；埋在里面的实际问题反而简单。这被认为是刻意设计：测试候选人能否从冗长模糊 spec 中提取核心问题（映射日常工程中读 RFC/需求文档）。与 InterviewCoderHQ 教练观察一致：'代码量感觉荒谬的多，coding speed 至关重要，follow-up 极多'。

**解法**: 练限时读长 spec：先扫 IO 格式和最后一段（约束/性能豁免常写在末尾——一位考生因没读'最后一句：不用担心性能'被面试官点破），列 bullet 需求清单向面试官复述确认后再动手。

来源: <https://www.reddit.com/r/Hack2Hire/comments/1tqdmyr/openai_interview_process_experience_megathread/>

## ML Coding 题

### MLE 面试（2026-06 通过）：transformer 抓虫 + cell simulation + post-training 细节追问
*medium · 频率: single report; transformer debugging 本身 very high · 2026-06*

thread-1179644（2026-06-09 前后，MLE 全职 onsite，已通过）：'面试主要是 transformer 抓虫（debugging），coding 是 cell simulation，另外考了 post-training 的细节。我主要面试的材料是 Andrej Karpathy 的 youtube'。确认 2026 年 Research/Applied ML 轮 = transformer debugging + 模拟类 coding + post-training（SFT/RLHF/数据）知识性追问三件套。对候选人（Meta post-training 背景）来说 post-training 细节追问是主场。

**解法**: transformer debug 常见 bug 点：causal mask 方向/位置（pre-softmax）、softmax 维度、√d_k 缩放缺失、位置编码未加、训练/eval 模式、loss 的 target 未 shift。post-training 追问按自身项目准备：RLHF/DPO 对比、reward hacking 处理、SFT 数据配比、eval 设计。Karpathy 的 'Let's build GPT' 和 'Deep Dive into LLMs' 是面经作者点名的备考材料。

来源: <https://www.1point3acres.com/bbs/thread-1179644-1-1.html>

### PracHub 2026-04-03 MLE tech screen：Debug MiniGPT + 手推 matmul 反向 + KV cache 实现
*medium · 频率: transformer debugging 家族 very high；此具体版本 single report · 2026-04*

两 part，共约 1 小时（MLE technical screen，上报 2026-04-03）。Part A：decoder-only transformer 代码语法正确但自回归解码输出错误文本，要求 debug 并加 KV cache。考点：各阶段 tensor shape、causal mask 机制、attention 计算、位置编码、loss 对齐（next-token shift）、train/eval 模式、greedy/sampling。期望交付：找出并修复 bug（mask 错误/softmax 轴/√d_h 缩放/位置编码/target shift/模式类 bug）、prefill 与 decode 干净分离、O(T) decode vs O(T²) 重算、内存讨论（MQA/GQA/量化）。Part B：自定义 C=A@B 的 forward+backward：从 C_ij=Σ_r A_ir B_rj 逐 index 推导 dA=dC@Bᵀ、dB=Aᵀ@dC，支持 batch/broadcast，用 torch.autograd.Function + save_for_backward，gradcheck 验证。追加 follow-up：Hillis-Steele prefix scan 的 O(n log n) work / O(log n) depth，及 scan vs reduction 何时划算；Blelloch scan 对比。

**解法**: 来源已给完整解法框架（见 detail）。补充：dA/dB 的 broadcast 情形要对被广播的轴求和还原形状；KV cache 只改 attention 的 K/V 拼接与 mask 的增量部分，Q 只算新 token。

来源: <https://prachub.com/interview-questions/debug-minigpt-and-backpropagate-matmul>

### MLE 电面（2026-06）：resumable iterator 存状态——recruiter 提前给 topic 且很准
*medium · 频率: high (staple; 1 new report Jun 2026) · 2026-06*

thread-1180787（2026-06-20，MLE 电面详细面经）：LinkedIn recruiter reach out，给了大概的面试 topic，'实际上还是挺准的'。题目：'设计一个 resumable iterator，能够存状态并且[恢复]...'（预览截断）。与已知高频 resumable iterator 一致：getState()/setState()，list→多文件 JSON→async 递进。Hello Interview 社区版本（OpenAI，2024-12 senior/2025-10 mid 两次上报）要求 async 版：AsyncCompositeIterator 跨多文件，state 可序列化（JSON dict），多 iterator 并发互不干扰；常见坑：直接存不可序列化的 iterator 对象、把 byte offset 当逻辑位置、漏 await。另注意 thread-1181120（2026-06-24 MLE）专门讨论'recruiter 给的 onsite problem prompt 有多准'——社区共识是大体准但建议全面准备。

**解法**: 分层实现：ResumableListIterator(index state) → MultiFileIterator(state=(file_idx, inner_state))，处理空文件（advance 逻辑放 helper，setState 后也要 skip empty）→ async 版把 next() 变 coroutine。必须写单测覆盖 get/set state 各时刻和 StopIteration。

来源: <https://www.1point3acres.com/bbs/thread-1180787-1-1.html>

### Transformer Bug Hunt（变形金刚抓虫）——MLE/RS/RE tech screen 60min，4 处 bug
*medium · 频率: high（12 帖） · 2025-11 ~ 2026-06-09*

官方题库：transformer-bug-hunt，coding，high，12 帖，60min，roles MLE/RS/RE，tech screen+onsite coding，tags: ml-knowledge/transformer/debugging，首报 2025-11-01，last_asked 2026-06-09。断档期细节：thread-1171609（2026-04-05, MLE 店面《变形金刚抓虫细节问题》）镜像摘要：讨论 transformer 实现中 4 个主要 bug，明确提到 MLP dimensions（FFN 维度错）和 positional encoding initialization（位置编码初始化错）两处；thread-1179644（2026-06-09 MLE onsite）三件套：transformer debugging + cell simulation coding + post-training 细节 deep dive（对口 post-training 背景候选人）。thread-1178049 回复区称其'捉虫'。

**解法**: （我的推断+社区常见 bug 清单）逐模块跑 shape/数值检查：常见 4 类=①attention scale 忘除 sqrt(d_k) 或 mask 加错；②FFN/MLP 隐层维度写反（d_model↔4·d_model）；③positional encoding 初始化/相加位置错（如 embed 后忘加或训练中被覆盖）；④residual/LayerNorm 顺序或 softmax 维度错。现场先写 sanity test（小 batch 过拟合、输出分布对称性）再定位。

来源: <https://www.1point3acres.com/bbs/thread-1171609-1-1.html>

### Classifier with Noisy Annotators / Human-Data 分类器——MLE/RS/RE tech screen 60min
*medium · 频率: high（9 帖） · 2026-01 ~ 2026-05-26*

官方题库：classifier-noisy-annotators，coding，high，9 帖，60min tech screen，roles MLE/RS/RE，tags: ml-knowledge/data-cleaning，last_asked 2026-05-26。断档期细节：thread-1178049（2026-05-26 MLE 视频面过经）两轮 screening 共 4 题，其一为 'human data 分类器'（回复区问是否用 pandas——楼主答有 utility）；thread-1176684（2026-05-14《OAI research technical 整套面经》）镜像摘要含 'noisy data handling'。OJ 镜像：'Find the Incorrect Data Labeler'、'Human Labeling and Training a Classifier (ML Coding)'。与候选人 post-training 数据管线背景高度对口。

**解法**: （我的推断）给多标注员对同一样本的标签：先算 inter-annotator agreement / 每标注员与多数票的一致率找出坏标注员；清洗后训练简单分类器（logistic regression / 小 NN）；进阶讨论 Dawid-Skene 式标注员置信度加权、类别不平衡与置信区间。

来源: <https://www.1point3acres.com/bbs/thread-1178049-1-1.html>

### NumPy 1-NN → 改写成 Wx+b 神经网络 + entropy 计算——MLE/RE 60min
*medium · 频率: high（8 帖） · 2026-01 ~ 2026-05-20*

官方题库：numpy-1nn-wx-b，coding，high，8 帖，60min tech screen+onsite，roles MLE/RE，tags: ml-knowledge/numpy/linear-algebra，last_asked 2026-05-20。断档期细节：thread-1177444（2026-05-20《OpenAI ML Coding》onsite）镜像摘要：'entropy calculation and 1-NN implementations with vectorization and neural networks'——即同场先手写 entropy、再向量化 1-NN、再把 1-NN 改写为神经网络前向（权重构造）。OJ 镜像：'Implement 1-Nearest Neighbor (1NN) Classifier with NumPy; Rewrite as Neural Network Weights'、'Vectorized 1-NN and Neural Network Forward Pass'。

**解法**: （我的推断）1-NN 向量化：dist²=||x||²+||c||²-2xCᵀ 一行广播实现；改写为 NN：W=2C, b=-||c||²，argmax(Wx+b) 等价于最近邻（负平方距离线性化），可讲成'1-NN 是特定权重的线性层'；entropy 部分注意 0·log0=0 与数值稳定。

来源: <https://www.1point3acres.com/bbs/thread-1177444-1-1.html>

### Streaming Entropy（流式熵，online + block-wise 更新）——RS/RE tech screen 60min
*medium · 频率: medium（4 帖） · 2026-04-01 ~ 2026-06-22*

官方题库：streaming-entropy，coding，medium，4 帖，60min tech screen，roles RS/RE，tags: numerical-stability/streaming，reported_from 2026-04-01（4 月上新），last_asked 2026-06-22。OJ 镜像标题：'Streaming Entropy with Online and Block-wise Updates'。与 thread-1173645（RS 四轮）中 'entropy calculation task' 呼应——熵计算是 research 轨 AI-coding 题池成员。

**解法**: （我的推断）维护词频 dict + 两个累积量 N 与 S=Σc·log c，则 H=log N − S/N；单元素更新 c→c+1 时 S += (c+1)log(c+1)−c·log c，O(1)；block-wise 合并两个直方图同理可加；讨论 log-sum 数值稳定与大流量下的近似（count-min sketch）。

来源: <https://www.1point3acres.com/interview/problems/company/openai>

### Autograd / 矩阵乘 forward+backward / Hillis-Steele scan——RS/RE 75min ML coding
*medium-hard · 频率: medium（6 帖） · 2026-02 ~ 2026-05-31*

官方题库：autograd-hillis-steele-scan，coding，medium，6 帖，75min，roles RS/RE，tech screen+onsite，tags: ml-knowledge/autograd/pytorch/parallel-algorithm，last_asked 2026-05-31。佐证：thread-1171922（2026-04-07《OpenAI onsite coding 新题 + 求 75min ML coding》）楼主明言 75min ML coding 与 'linear algebra or autograd' 相关；thread-1173645 回复区问 'AI coding I (autograd) 是 60min 还是 75min'——autograd 是 research 轨 AI coding 题池固定成员。OJ 镜像：'Implement Matrix Multiplication Forward and Backward (Autograd-Style) in PyTorch'。

**解法**: （我的推断）实现 Tensor 类 + 计算图：matmul forward 存 (A,B)，backward dA=dC·Bᵀ, dB=Aᵀ·dC；拓扑序反向传播；Hillis-Steele 部分=O(log n) 步并行前缀和（每步 stride 翻倍），考并行思维与 work-efficiency 对比 Blelloch scan；用 numpy/pytorch 张量原语表达'并行'。

来源: <https://www.1point3acres.com/bbs/thread-1171922-1-1.html>

### OpenAI Research Engineer 全套面经（2026-03）：5 技术轮 + 1 BQ + 1 deep dive，含 transformer debugging
*hard · 频率: single report · 2026-03*

thread-1168926 'OAI Research Engineer 全套面经'（约 2026 年 3 月）：完整 loop = 5 个技术轮 + 1 个 behavioral + 1 个 deep dive，技术轮含 transformer debugging 成分。正文在登录墙后未能获取完整题目清单。（候选人若已有 4 月前整理可能已覆盖此帖；列出备查。）

来源: <https://www.1point3acres.com/bbs/thread-1168926-1-1.html>

### PracHub 2026-04-24 MLE onsite：数值稳定的流式 entropy（logits 分块）+ 向量化 1-NN 及其神经网络等价形式
*medium · 频率: 2 reports (Apr & May 2026) · 2026-04*

Part 1：给 logits z，p=softmax(z)，计算 H(p)=−Σ pᵢ log pᵢ；要求 (a) log-sum-exp 防溢出；(b) 流式：logits 分块到达、全量放不进内存，单 pass、O(1) 状态。关键恒等式：H = log Z − E_p[z]，Z 为配分函数；流式维护 running max M 和两个累加器 Σe^{zᵢ−M}、Σzᵢe^{zᵢ−M}，M 更新时 rescale（online softmax 同款技巧）。Part 2：X_train(n,d), y_train, X_query(m,d)：(a) 全向量化 L2 1-NN（禁 Python 循环）：‖q−xᵢ‖²=‖q‖²+‖xᵢ‖²−2q·xᵢ，一次 matmul + broadcast，argmax 时 ‖q‖² 项可丢；(b) 把 L2 1-NN 表示成 linear layer + softmax（W=2X_train, b=−‖xᵢ‖²，argmax 恢复最近邻）；(c) L1 变体为什么仿射层不够——需要 ReLU 网络（分段线性）。Follow-ups：为何 argmax 下 softmax 单调性重要、O(1) 状态维护 logits 的 running variance、L1 网络隐层数随 n,d 如何扩展、训练集固定时的预计算。另一独立上报：'Implement 1NN with NumPy'（2026-05-19，MLE screen）。这与 2025 面经中的 KL divergence/cross-entropy 数学题一脉相承，确认 2026 年 ML 轮仍考数值稳定+向量化基本功。

**解法**: 来源含完整解法（见 detail）。

来源: <https://prachub.com/interview-questions/compute-entropy-and-implement-1-nn>

### Research Engineer 高难轮（Exponent 详细复盘）：分布式 all_gather + 噪声信道误差界推导；transformer 四区域找 bug + KV cache
*hard · 频率: single detailed report; 各子题均另有多个独立报告 · 2025-06*

Exponent 上的 RE 面经（约 2025 年中，7 周流程，技术轮后被拒）：(1) 最难轮（ML statistics/information theory）：实现多节点 all_gather → 信道有噪声时推导达到目标误差所需轮数的 worst-case 公式 → naive bound 太慢如何改进 → 利用'传的是 float 而非任意实数'设计更优算法（利用浮点表示的有限性）。研究生级信息论，面试官几乎不给提示。(2) ML debugging 轮：transformer 实现有四个标注区域各藏一个 bug，逐一找出；然后实现 KV caching 并讨论需要改哪些部分和进一步优化。(3) 算法轮：'给一个 Python package，找支持它的最新 Python 版本'——分层二分查找（对应已知 version dependency 题）。(4) 手速轮：乐器 beat string → 乐谱记法转换，扩展多乐器、建模休止符（对应 interviewdb 'Beat Notations'）。(5) 系统轮：KV store serializer/deserializer + 关机后持久化恢复 + 关机状态下的查询处理。总体评价：比 FAANG 少提示、不可套路（'less gameable'）。

**解法**: all_gather 噪声题思路：重复传输+多数表决使错误概率指数衰减（Chernoff bound 给轮数 O(log(1/ε))），float 优化利用有限位宽做逐位纠错/校验和而非整值重传（我的推断）。version 题：外层对版本序列分段（major 变更点），内层二分。

来源: <https://www.tryexponent.com/experiences/openai-machine-learning-engineer-interview-c7b6a2>

### 新题（2026）：Debug a Concurrent Job Scheduler（MLE 向并发 debug 题）
*medium · 频率: single report each (2026) · 2026-06*

PracHub（MLE，medium）：给一个有 bug 的 Python 并发 job scheduler——多个独立 job 并发执行，每个 job 有 ID、callable、依赖等，要求找出并修复并发 bug。与 coditioning 记录的'race condition 识别与修复'方向一致（read-modify-write 原子性、锁/原子操作修复）。DS 轨还有 'Debug and fix a PyTorch Transformer training loop'（hard：极小 causal decoder LM 的训练循环 debug+优化）。

**解法**: 常见植入 bug：共享 dict/counter 无锁、future 结果未 join、依赖图有环时死锁、异常吞掉导致 job 静默失败；用 threading.Lock/queue.Queue/concurrent.futures 规范化并补上失败重试与超时（我的推断）。

来源: <https://prachub.com/interview-questions/debug-a-concurrent-job-scheduler>

### MLE/RE 轨 recruiter prompt 原文合集（4-5 月）：ML coding 轮考纲
*medium-hard · 频率: 4 帖互证 · 2026-04-14 ~ 2026-05-07*

三份断档期 prompt/考纲：(1) thread-1174800（2026-04-28, RE 岗）prompt 原文：'60 minute ML coding interview - We'll cover math and coding and have an open-ended discussion/brainstorm about research ideas. A basic understanding of NumPy is [expected]… evaluated on your problem solving ability and ability to write clean, well-designed code.'（数学+编码+研究想法头脑风暴三合一）。(2) thread-1175470（2026-05-03《MLE 提示词分享》）镜像摘要考纲：ML coding、debugging、mathematical coding、dataset analysis，核心概念=modern ML architectures 与 PyTorch autograd。(3) thread-1172952（2026-04-14, MLE onsite prompt 求助）镜像摘要：四轮 coding，聚焦 backpropagation、PyTorch、simulation design。另 thread-1175861（2026-05-07）讨论 MLE vs SWE track 怎么选（MLE 轨换掉部分算法轮为 ML coding）。

**解法**: 考纲映射（我的推断）：math+coding=streaming entropy/stopping time；debugging=transformer bug hunt；dataset analysis=noisy annotators；autograd=matmul forward/backward。research ideas 讨论环节提前备 2-3 个 post-training/agentic 方向的开放式想法。

来源: <https://www.1point3acres.com/bbs/thread-1174800-1-1.html>

### [RS 挂经] 2026-05-31 全新 RS onsite 题面：推断时间概率、矩阵乘、负载均衡、softmax 实现
*hard · 频率: 3 帖（RS 轨 5 月密集采样） · 2026-05-14 ~ 2026-05-31*

thread-1178705（2026-05-31《[爱开放]挂经 RS - 新鲜》，MLE 标签/Onsite）镜像 AI 摘要：'detailed probability and coding challenges including inference time, matrix multiplication, load balancing, and softmax implementations'——即四类题：①推断时间（inference time）概率/期望计算（math reasoning 变体）；②矩阵乘实现（autograd 族）；③负载均衡（load balancing，算法/系统混合）；④softmax 数值稳定实现。与 thread-1173645 的 RS 四轮结构（2 AI coding+1 general coding+1 math reasoning）完全吻合，是 5 月底 RS 题池的最新采样。另 thread-1177093（2026-05-17 Research 岗电面）：coding+ML debugging+SD 三轮，反馈强调 communication；thread-1176684（2026-05-14 research technical 整套）：infectious disease modeling + noisy data handling + matrix operations，附改进建议。

**解法**: （我的推断）softmax：max-shift 数值稳定+log-sum-exp；inference time：排队论/期望递推（如 batch 推理延迟分布）；load balancing：一致性哈希或 power-of-two-choices 并分析尾延迟；矩阵乘：分块+backward 推导。RS 轨四题全部可提前 overfit——原帖作者原话『如果你不能 overfit，这个题目还是很有难度』。

来源: <https://www.1point3acres.com/bbs/thread-1178705-1-1.html>

### OpenAI Research Engineer / Applied ML 轨流程变化（2025-12）：新增 general coding + ML coding 双轨编码面
*unknown · 频率: 2 threads (same OP) + 1 corroboration · 2025-12*

csMajors/leetcode 双发帖（2025-12）：'Recently they changed process to include both general coding and ml coding'——RE 轨现在同时考通用编码和 ML 编码。发帖人询问 general coding 是否与 SWE 相同（评论区确认走同一题库方向）。结合其他情报：ML coding 部分为实现训练/推理组件（社区通识：如 attention/采样器/数据管线），60min DSA 店面（intern/NG RE 轨'no ML knowledge'）。AI research intern 轨（2026-05 帖）：'不考 leetcode，考 conceptual ML + 讲解简历上的项目'。注意区分轨道。

**解法**: 我的推断：ML coding 按业界惯例练——numpy/torch 手写 multi-head attention、KV cache 采样循环、BPE tokenizer、简单训练 loop debug；这与 GDM/Meta 的 ML coding 轮同构。

来源: <https://www.reddit.com/r/csMajors/comments/1ps0cd2/openai_interview_for_research_engineer_roles/>

## ML 理论

### ML 理论/推导考点（2026-05 Blind 多 lab 对比帖）：手写 MHA 是 table stakes、backprop 推导刷掉 80%、log-sum-exp 是隐形过滤器
*hard · 频率: high (cross-company pattern, May 2026) · 2026-05*

Blind 'Recent ML interview loops at OpenAI/Anthropic/Databricks/Mercor'（2026-05-03，Apple 员工发帖，面完 7 家）：(1) 手写 Transformer/MHA（不用库）已是所有 AI lab 的 table stakes；(2) backprop 推导（chain rule 落地、softmax+cross-entropy 梯度）淘汰约 80% 候选人，senior 也大量挂；(3) softmax 数值稳定性/log-sum-exp 是隐形筛子，会被要求实现并解释；(4) infra 向岗位要求 Megatron-LM 源码级理解（TP/PP/SP）、ZeRO、FlashAttention——'只读 paper 已经不够'；(5) quant firm 重 latency/确定性/统计，AI lab 重 scaling/分布式/模型行为。注：评论区质疑发帖人夹带私货（卖题），核心观察与其他来源一致可采信。PracHub 对应收录：'Implement Backprop for a Tiny Network'、'Derive Backpropagation for Matrix-Product Layers'、'Compute Matrix Prefix Products and Gradients'（N 个 D×D 矩阵的前缀积及其梯度）、'Explain KV cache in Transformer inference'。

来源: <https://www.teamblind.com/post/recent-ml-interview-loops-at-openai-anthropic-databricks-mercor-what-i-learned-xl3yizf4>

### Math Reasoning / Stopping Time（数学推理题，RS/RE 专属轮）
*hard · 频率: medium（4 帖） · 2026-01 ~ 2026-05-31*

官方题库：math-reasoning-stopping-time，coding，medium，4 帖，60min tech screen，roles RS/RE，tags: ml-knowledge/math-reasoning/probability/algorithm-design，2026-01-01 ~ 2026-05-31。来自 thread-1173645（2026-04-19）：research org 四轮中固定一轮 math reasoning（回复区确认约面时 recruiter 会说明是 math reasoning，且需要写 code 验证）。stopping time = 停时概率问题。

**解法**: （我的推断）典型形态：随机过程何时首次满足条件的期望/分布（如随机游走首达、抽卡集齐、鞅停时）——先建递推/线性方程组解析解，再写 Monte Carlo 模拟对拍验证；面试评的是建模+验证闭环，不是背公式。

来源: <https://www.1point3acres.com/bbs/thread-1173645-1-1.html>

## System Design

### Design Sora video generation orchestration —— 2026年6月电面/onsite SD 最高频题，本质是 GPU job scheduler
*hard · 频率: very high (5+ reports Jun 2026) · 2026-06*

thread-1180717（2026-06-19）原题面：'Design a scalable system to orchestrate Sora video generation, where users can submit...'（用户提交 prompt 生成视频）。thread-1179591（2026-06-08 VO）：'SD 那轮是设计 Sora，别被名字唬到，本质就是 job scheduler'。thread-1181839（2026-07-01 过经）：'design 是 design sora 那题，核心是 GPU 调度，感觉和其他任何 resource scheduling 没区别'。thread-1180067（2026-06-12 电面）也考 design Sora。PracHub 多条 2026 上报变体：'Design the GPU Job Scheduler for Text-to-Video'（2026-06-26，跨 region 调度，hard）、'Design GPU Scheduling for Video Generation'（2026-06-27，可变时长/优先级/容量需求）、'Design Video Generation Orchestration'（2026-06-12）、'Design a Text-to-Video Generation System (Sora-like)'（2026-05-12，prompt/settings/model selection）。1p3a 题库 'GPU Scheduling & Messaging' last asked 2026-06-29，Very High。

**解法**: 按异步任务编排系统设计：API 层收 prompt → 任务持久化（queue + DB 状态机 queued/running/failed/succeeded）→ GPU worker pool 调度（考虑 job 时长不均、优先级、抢占、multi-GPU 分片、region/容量约束）→ 进度通知（webhook/WS 轮询）→ 结果存储 CDN。重点谈：幂等重试、checkpoint 恢复长任务、公平性 vs 利用率（weighted fair queuing）、backpressure 和 admission control。多位面经作者确认按 generic resource scheduler 讲即可得高分（此为帖子共识+我的展开）。

来源: <https://www.1point3acres.com/bbs/thread-1180717-1-1.html>

### Payment system（商家→payment provider）—— 2026年6月电面 SD 高频题
*hard · 频率: very high (4+ reports Jun 2026) · 2026-06*

thread-1181247（2026-06-25 电面 SD）：'高频题 支付系统，不用考虑用户行为，纯纯考虑商家到 payment provider（发卡商）之间的系统'。thread-1180678（2026-06-19 onsite）也考支付系统。PracHub 2026 上报变体：'Payment Processing System with Exactly-Once Charging'（2026-06-26，marketplace 防重复扣款，hard）、'Design a Payment Processing System'（2026-06-14，web/mobile checkout 后端）、'Design Offline Merchant Payment System'（2026-06-22，authorization/capture/ledgering/bank reconciliation）、'Payment Processing Service (Merchant to Payment Provider)'。1p3a 题库 last asked 2026-06-29，Very High。

**解法**: 核心考点是 exactly-once/幂等：idempotency key + 状态机（created→authorized→captured→settled/refunded）+ 双写账本（ledger 双分录）+ 与外部 provider 的异步对账（reconciliation job 处理 timeout/未知态）+ retry with backoff 且区分可重试/不可重试错误。PracHub 的 exactly-once 变体直接点名防 double-click/客户端重试/网关重发三类重复（我的推断整合）。

来源: <https://www.1point3acres.com/bbs/thread-1181247-1-1.html>

### Payment Processor / Coffee Shop Payment（OpenAI 第一高频 SD，20 帖）
*medium-hard · 频率: very high（20 帖） · 2026-01 ~ 2026-06-29*

官方题库：payment-coffee-shop，system-design，very-high，20 帖，60min，phone screen+onsite，roles SWE，2026-01-01 ~ 2026-06-29。断档期细节：thread-1178674（2026-05-31《Payment Processor 系统设计题分享》）镜像摘要：讨论 'synchronous confirm phase and asynchronous batch processing'——同步确认段+异步批处理段的组合是题眼；thread-1176829（4 月挂经）SD=Payment System，回复区问 'payment system deep dive 部分大致问了什么'；thread-1175992（2026-05-08 店面）SD=payment 场景含 'large transaction file generation'（大交易文件生成）；thread-1176087/1176291 亦考。external 库 'Payment Processing System (Stripe-like)'（tid 7100485）。

**解法**: （帖子+我的推断）两阶段：同步 authorize/confirm（低延迟、幂等键防重复扣款）+ 异步 capture/settlement batch（队列+定时对账文件）；重点讲 idempotency key、exactly-once 语义、重试与死信、对账 reconciliation、DB 事务边界 vs 消息投递原子性（outbox pattern）。

来源: <https://www.1point3acres.com/bbs/thread-1178674-1-1.html>

### Design Sora（视频生成服务调度）——2026-04 上新的 very-high SD 题，19 帖
*medium-hard · 频率: very high（19 帖） · 2026-04-01 ~ 2026-06-29*

官方题库：design-sora-video-generation，system-design，very-high，19 帖，60min，phone screen+onsite，roles SWE/Infra/EM，reported_from 2026-04-01，last_asked 2026-06-29。断档期细节：thread-1177818（2026-05-24 onsite 分享，Positive/Easy）：『SD：设计 Sora（说白了就是任务调度器，别被题目唬到）』；工具=coderpad + excalidraw；回复区技术讨论：有人 mock 后认为 'postgres + FOR UPDATE SKIP LOCKED' 单表任务队列即可，不必上 Kafka。external 库 'Design Sora Video Generation Scheduling'（tid 7100240）。

**解法**: （帖子+我的推断）本质=GPU 上的长任务调度器：提交→排队（优先级/配额）→分配 GPU worker→进度回调/断点续跑→结果存储 CDN；核心讨论点：队列选型（DB row-lock SKIP LOCKED vs Kafka/Redis stream）、任务幂等与重试、GPU 利用率与抢占、多租户配额、状态机+webhook 通知。

来源: <https://www.1point3acres.com/bbs/thread-1177818-1-1.html>

### OpenAI 2026 最高频系统设计题：Design Sora——正解是转化为 GPU 资源调度问题
*hard · 频率: very high (3 loops in 2 months) · 2026-07*

三份 2026 面经（一挂一过×2 复盘）：onsite 系统设计'Design Sora'（文生视频服务）。通过者的关键打法：不纠结产品表层，把它当 GPU 资源调度问题——昂贵算力在生成任务间的分配：job queues、优先级、GPU 容量上限、batching、重试、job state tracking、公平性、失败处理、保持 GPU 高利用率同时避免不可预测延迟。面试官明显被这个框架打动（'两个设计轮都强信号'）。失败案例反而是设计聊得太顺提前结束（面试官问不出 follow-up）但总体 no-hire——说明信号采集在别处。同一 loop 其他设计题：店面 payment system（支付流、可靠性、一致性、重试、防重复支付、对账、外部支付商故障）、Design a Real-Time Online Chess Platform（店面设计题）。

**解法**: 分层：API/提交层（幂等、配额）→ 调度层（多级优先队列、抢占 vs 非抢占、gang scheduling 多 GPU job）→ 执行层（diffusion 多阶段流水线、checkpoint 恢复）→ 存储/CDN 分发；讨论利用率 vs 尾延迟、bursty 流量的 admission control、按 tier 的 SLO。

来源: <https://www.reddit.com/r/OfferEngineering/comments/1up0tsl/openai_jul_2026_senior_swe_interview_experience/>

### Design Chess Game / Chess.com（high，9 帖，问到 2026-06-26）
*medium · 频率: high（9 帖） · 2026-02 ~ 2026-06-26*

官方题库：design-chess-game，system-design，high，9 帖，phone screen+onsite，roles SWE/Infra，2026-02-01 ~ 2026-06-26。断档期佐证：thread-1172810（2026-04-13 onsite）SD 轮=chess；thread-1176587（2026-05-13）monster battle 后 follow-up chess；thread-1176087（2026-05-08 全套）四轮之一=chess。external 库 'Design Chess.com (Online Chess Game)'（tid 7100178）。相关 SD：elo bucket matching（thread-1172554 店面 SD）可视为其匹配子系统。

**解法**: （我的推断）实时对弈：WebSocket 会话+服务器权威棋局状态机、走子合法性校验、断线重连（事件溯源恢复棋局）、观战 fan-out、elo 匹配（按分桶+等待时间放宽）、反作弊（引擎相似度）——面试官常聚焦匹配与断线一致性。

来源: <https://www.1point3acres.com/bbs/thread-1172810-1-1.html>

### Design Cloud IDE / Google Colab（500k 用户、workspace 管理、快速恢复）
*medium-hard · 频率: medium（4-6 帖） · 2026-02 ~ 2026-05-06*

官方题库：design-cloud-ide，system-design，medium，4 帖，onsite SD，roles SWE/Infra，last_asked 2026-02-01（4 月后未再报，疑似降频/淘汰）。断档期佐证：thread-1171984（2026-04-08《OAI 电面系统设计》）镜像摘要：'designing a scalable Google Colab system supporting 500k users with workspace management and quick resume'；thread-1175749（2026-05-06 店面過經）60min coding + SD 'cloud-based IDE'——5 月仍有出现。external 库 'Design a Cloud IDE'（tid 7100129）。

**解法**: （我的推断）每 workspace=容器/microVM：冷启动 vs 快速恢复（快照+分层镜像+预热池）、代码持久化（对象存储+增量同步）、内核会话状态、空闲回收与配额、500k 用户下的调度装箱；quick resume 是题眼=内存快照或分层 checkpoint。

来源: <https://www.1point3acres.com/bbs/thread-1171984-1-1.html>

### OpenAI · System Design 题库（14 题，含 AI 基础设施特色题）
*hard · 频率: onsite 常见 — 站内各题 OpenAI 频率：Design GPU Scheduling Platform 10、Design A Nearby POI Service 10、Design Online Chess Game 10、Design Payment System 10、Design ChatGPT 9、Design CICD System 9、Design Slack-like Chat System 9、Design AI Chatbot App 7、Design Webhook Delivery System 7 · 2025-12 至 2026-02*

OpenAI SD 全 14 题（均 Onsite，站内 SD 正文需登录，仅可得标题/难度/频率；practice URL 形如 .../openai/system-design/{id}/practice）：Design Payment System(Hard, id 69c9f9a3ff3ebde766ced6b4)、Design Slack-like Chat System(Hard, 69c9fe5dff3ebde766ced6f4)、Design CICD System(Hard, 69c9ff24ff3ebde766ced6fa)、Design Online Chess Game(Medium, 69cb09edff3ebde766cedb20)、Design AI Chatbot App(Medium, 69cb3259ff3ebde766cedc1f)、Design Webhook Delivery System(Medium, 69cb3b1aff3ebde766cedc63)、Design TinyURL(Easy, 69cc73c2ff3ebde766cee30b)、Design Youtube(Hard, 69cd3e3cff3ebde766cee66e)、Design Job Scheduler(Medium, 69ce7e9a4f38b199f9e49099)、Design Google Calendar(Medium, 69d0903c17b72775cc49bcf0)、Design ChatGPT(Hard, 69d6f527c4c1bc791ee229e3)、Design GPU Scheduling Platform(Hard, 69d71cbfc4c1bc791ee22b22)、Design Distributed Web Crawler(Medium, 69dc41c3e4441834b3f736bb)、Design A Nearby POI Service(Hard, 69f9729772a3d3fe39f8d21b)。对该候选人最相关：Design ChatGPT、Design GPU Scheduling Platform、Design AI Chatbot App。

**解法**: （我的推断）AI 基础设施题（ChatGPT/GPU Scheduling/AI Chatbot）应准备：推理服务架构（KV cache、continuous batching、多副本路由）、GPU 集群调度（gang scheduling、抢占、公平性/配额）、成本与延迟 SLO 权衡——契合该候选人 post-training 背景。注意 blog 提示：若面试官造过该系统会直接深挖 scalability。

来源: <https://www.hack2hire.com/question-bank/companies/openai/system-design>

### 2026 年 4-5 月新增 SD 题：distributed rate limiter、CI/CD build caching、Slack-like messaging、Instagram feed、crossword solver、cloud IDE/DevBox
*medium · 频率: each 1-2 reports (Apr-May 2026) · 2026-05*

PracHub 2026 年上报的非 Sora/payment 类 SD 新题：(1) 'Design a Distributed Rate Limiter'（2026-05-11，medium）+ coding 版 'Implement a Distributed Rate Limiter'（跨多 app server 的限流库）；(2) 'Design CI/CD Build Caching'（2026-05-26：YAML workflow 多 job 共享缓存）；(3) 'Design a Slack-Like Messaging System'（2026-04-26：channel/workspace 实时消息）；(4) 'Design an Instagram-like Feed System'（2026-05-25）；(5) 'Design a Distributed Crossword Solver'（2026-05-12，hard：分布式填字求解服务，输入 2D grid）+ 'Design a crossword puzzle solver system'；(6) 'Design a Sandboxed Cloud IDE'（Colab 式多租户浏览器 IDE，隔离执行）、'Design a Hosted Notebook Platform'、'Design a Cloud DevBox Platform'（一次性/持久远程开发机）；(7) 'Prevent Duplicate Request Processing'（双击/重试/网关重发下的幂等）；(8) 'Aggregate Recent Message Events And Active Chats'（内存事件聚合器：user_id/chat_id/timestamp/event_type，滑窗统计活跃 chat）；(9) 'Consistent Hashing Ring with Virtual Nodes'（coding 版，shard rebalancing）。

**解法**: rate limiter：token bucket/sliding window + Redis Lua 原子操作 vs 本地+异步同步的精度权衡；CI cache：content-addressed storage + cache key(lockfile hash) + 失效层级；crossword：约束满足，中心 coordinator 分支定界分发子问题（我的推断）。

来源: <https://prachub.com/interview-questions/design-a-distributed-rate-limiter-2>

### 前端/移动端方向新题（2026-07）：streaming chat UI、ChatGPT playground、iOS chat interface（40min 实机）
*medium · 频率: each single report (Jun-Jul 2026) · 2026-07*

非候选人主方向但佐证题库扩张：PracHub 'Implement a Mobile Chat Interface'（2026-07-03，iOS senior+，在现有 codebase 里 40 分钟实现 ChatGPT 式聊天屏——再次印证'现有 codebase'趋势）；'Build a Reliable Streaming Chat UI'（React token 流式渲染，断线清理/backpressure）；'Design a ChatGPT Playground'（prompt 测试台）；'Design an AI playground editor'（文档式交错 UI，hard）；'Design a ChatGPT-Style Assistant Product'（对话状态、消息流式、模型调用）；Android：Compose rating card、MVVM API 架构、mobile model usage quotas。1p3a thread-1180018（2026-06-12）：Android mobile screen 挂经（正文未公开）。

来源: <https://prachub.com/interview-questions/implement-a-mobile-chat-interface-in-an-existing-codebase>

### OpenAI system design round: reported questions & 10x-1000x scale pressure-testing (Exponent guide)
*hard · 频率: multiple reports per question · 2026-02*

Reported phone-screen questions: 'Design the OpenAI Playground' (front-end wireframes + API layer + DB schema for thread/message history — full-stack expected, recruiter tells candidates this explicitly), 'Design Slack' (real-time messaging, channels, presence, scale), 'Design a job scheduler' (distributed task orchestration, fault tolerance). Onsite: 'Design a streaming platform at scale' (global distribution, variable frame rates, 10x-1000x growth projections), 'Design a high-scale chat application' (WhatsApp/Teams-style, hundreds of millions of users). Two SD rounds total (screen + onsite) at 60 min each, plus a 45-60 min 'reverse system design' deep dive presenting a past project. Interviewer pattern: validate initial design, then push 'what if we 10x/100x/1000x scale?' — must pinpoint which component breaks first and redesign it. Key advice: ask explicitly whether model-inference/ML-infra layers should be designed or treated as a black-box API. Leveling (senior vs staff) decided after the interview.

来源: <https://www.tryexponent.com/blog/openai-system-design-interview>

### SD 长尾题池（低频但在池）：Slack、限流器、CI/CD、crossword、webhook、日历、短链、YouTube、Yelp 等
*medium · 频率: low（各 1-3 帖） · 2025-10 ~ 2026-06-11*

官方题库+断档期帖子：design-slack（low，3 帖，last 2026-05-05；thread-1175677 2026-05-05 店面=Slack-like messaging + chatbot 实现）；分布式限流器（thread-1176099，2026-05-09 店面 SD='distributed rate limiting'；OJ 有带持久化/时钟偏移/Redis fallback 版本）；multi-tenant-ci-cd-workflow（low，3 帖，last 2026-06-11）；crossword-puzzle-solver（SD，low，2 帖；thread-1176085 2026-05-08 出现）；webhook-delivery-system（2025-11-19）；design-google-calendar（2026-01-22）；design-url-shortener（2026-01-10）；points-of-interest-yelp（2025-10-07）；external 库另有 Design YouTube、GPT-3 Playground（2025-10-18）。另 thread-1172835（2026-04-14 infra 组店面 prompt 原文）：'No coding is expected, but you'll be expected to be able to go deep in the details. These are modeled after co… down the requirements, discuss trade offs and edge cases'——SD 轮明确不写代码但要深挖细节；thread-1174549（2026-04-26 prompt 原文）：'[Architecture 60 min] - This collaborative architecture question focuses on designing large cloud-native infrastructure, allowing you to choose OSS components or cloud providers. You are expected to demonstrate deep expertise in at least one system component, such as Kubernetes, networking, queues, databases etc.'

**解法**: prompt 提示（原帖）：SD 轮至少对一个组件（K8s/网络/队列/DB）展示深度专长；准备一个'王牌组件'讲到 mechanism 级。

来源: <https://www.1point3acres.com/bbs/thread-1174549-1-1.html>

### OpenAI 系统设计风格情报（教练汇总+一手佐证）：店面就可能考设计、product+infra 混合、中途改需求
*hard · 频率: aggregated (coach) + 3 first-hand confirmations · 2026-03*

InterviewCoderHQ 帖（drCounterIntuitive，2026-03，附 'Design an MVP for a Slack-like app' 例题解法 gist）：(1) 店面和 onsite 都可能有 system design（按团队而异）；(2) 不只考 backend plumbing——会 probe 产品视角（类似 Meta product design + infra design 合体），前端出身也要会 backend 设计（一位前 Meta 前端的 loop 与后端相同，只是可用 TS 写码）；(3) 面试官会中途抛新约束/新产品需求/twist——考实时信息处理与认知灵活性，背模板会翻车。已知设计题：Slack-like app MVP、Design ChatGPT（社区确认 OpenAI/Anthropic 都在考，考 LLM 产品的 API/流式/推理层而非训练）、real-time sensor system（MLE 轨）、payment、chess、Sora。

**解法**: Design ChatGPT 准备：会话管理、SSE/WebSocket 流式 token、推理层（batching/KV cache）、历史存储、限流计费、内容安全管线；引用 codemia.io/HelloInterview 上的题解结构。

来源: <https://www.reddit.com/r/InterviewCoderHQ/comments/1sax4f9/targeting_openai_swe_roles_insights_on_what_to/>

## ML System Design

### ML 轮新考法（2026）：噪声标注/数据质量题族（filter bad annotations、multi-annotator labels）——直接对口 post-training 数据工作
*hard · 频率: 3+ variants collected (2026) · 2026-05*

PracHub 收录三道 OpenAI MLE 变体：(1) 'Filter Bad Human Annotations'（medium）：大规模人工标注训练集中有低质/不一致标注，设计方法过滤；(2) 'Improve Training With Noisy Annotators'（hard）：Pandas DataFrame，含 feature 列和 observed label，提升训练效果；(3) 'Improve classifier with noisy multi-annotator labels'（hard）：二分类文本数据，每条样本有多个标注员的标注，如何建模/聚合/加权提升 classifier。另有 'Mine Novel Images from Unlabeled Data'（从海量无标注图库挖掘新颖图像的 ML 系统）和 'Design a RAG system with evaluation'（含评测设计的 RAG 系统）。这批题是 2026 年 Applied/Research ML 轮相对新的方向，考数据为中心的 ML 工程判断。

**解法**: 标准工具箱：annotator agreement（Cohen/Fleiss kappa）、Dawid-Skene/GLAD 类标注员能力建模、confident learning（cleanlab 思路：用模型置信度找错标）、loss-based 过滤/reweighting、soft label 聚合 vs majority vote、留出金标集校准标注员、主动重标预算分配。答题时结合自己 post-training 数据管线经验讲 tradeoff（我的推断+经验性解法）。

来源: <https://prachub.com/interview-questions/improve-classifier-with-noisy-multi-annotator-labels>

### OpenAI-style AI-infra design questions (DesignGurus compilation)
*hard · 频率: unknown (prep-site compilation, not first-person reports) · 2025*

(1) 'Design a large-scale AI model deployment system — e.g., how would you serve a model like GPT-4 to millions of users concurrently?' (model serving architecture, LB + GPU model servers, autoscaling, model loading/versioning, low-latency handling). (2) 'Design a real-time chatbot API for AI-driven conversations' (REST vs WebSocket, conversation context/state management, strict latency targets, safety filters, rate limiting). (3) 'Design a distributed training system for deep learning models' (data vs model parallelism, job scheduling, cluster management, parameter server vs all-reduce, failure handling/checkpointing, GPU/TPU monitoring). (4) 'Design a scalable data pipeline for machine learning applications' (Kafka/PubSub ingestion, Spark/Flink processing, storage, data quality).

来源: <https://www.designgurus.io/blog/openai-system-design-interview-questions>

### ML 系统设计题池：RAG 检索/企业 ChatGPT/从未标注语料挖掘新数据（MLE/RE 轨）
*hard · 频率: low（各 1-2 帖） · 2025-11 ~ 2026-05-26*

官方题库三条：(1) rag-search-ml-design，low，2 帖，60min onsite SD，roles RE/MLE，2026-01-01 ~ 2026-03-22；(2) chatgpt-enterprise-rag，single，60min，MLE/RE，2025-11-01 ~ 2026-03-22；(3) mining-novel-data-unlabeled-corpus，single，MLE onsite SD，2025-11-18 ~ 2026-05-26（tags: mlsd/data-mining）——external 库 'Mining Novel Data from Large Unlabeled Corpus'（tid 7100044）。佐证：thread-1178049（2026-05-26 MLE 过经）回复区：『好像有一阵子 ML SD 没了，现在加回来了吗』——ML SD 轮 2026 春季一度取消后恢复。对 mid-training 数据管线背景候选人，(3) 几乎是本命题。

**解法**: （我的推断）mining novel data：去重（MinHash/embedding 聚类）→质量打分（分类器/困惑度过滤）→新颖性度量（与已训语料的 embedding 距离/n-gram 覆盖）→人审采样闭环→数据配比实验；RAG：chunking/混合检索（BM25+向量）/rerank/引用与权限隔离/评测（faithfulness）。

来源: <https://www.1point3acres.com/interview/problems/company/openai>

## BQ / Culture

### BQ/HM 轮（2026）：Why OpenAI、加速项目 tradeoff、不 ship 的项目、AI 安全观点
*medium · 频率: very high (Why OpenAI); others 1-2 reports each · 2026-06*

(1) 1p3a 题库：'Why OpenAI?' 类 BQ last asked 2026-06-29，Very High，17 条讨论。(2) Blind TPM 帖：'如果这个项目要做得更快你会怎么做'——期望答加资源/并行化/砍 scope/减少跨团队冗余等 tradeoff，并被解读为 OpenAI 高强度文化信号。(3) PracHub 'A Project You Decided Not to Ship'（SWE，hard）：讲一个做完/接近做完但决定不发布的项目——考产品判断与止损。(4) PracHub 'Explain Your Engineering Ownership'：初筛电话里就异常深入地考 ownership。(5) interviewing.io：senior manager 轮会挖简历细节并讨论 AI ethics/safety 观点（建议读 OpenAI 安全相关 blog）；跨职能协作轮'generic teamwork 故事不够用'。(6) oavoservice：recruiter 轮会抽查简历里不起眼的数字（'这个 0.3% latency 提升怎么测的'）并要求说清想去的子方向（alignment/RLHF/pretraining/multimodal）。

来源: <https://prachub.com/interview-questions/a-project-you-decided-not-to-ship>

### HM BQ（最终关卡）：Why OpenAI / AGI 安全观 / 为什么不去 Google 或 Anthropic
*medium · 频率: very high（17 帖） · 2025-11 ~ 2026-06-29*

官方题库：hm-bq-why-openai，behavioral，very-high，17 帖，60min onsite BQ，all roles，2025-11-01 ~ 2026-06-29。断档期细节：thread-1174510（2026-04-26《openAI MTS 面经》，Hard/Pass, MLE onsite）BQ 原文：『为什么要加入 OpenAI 而不是去谷歌或 Anthropic？』『你对 AGI 的安全边界怎么看？』；官方 briefing：mission alignment 是明列的招聘轴，why OpenAI/AGI/safety 有专门一轮，是 real gate 不是走过场；HM 沉默不推销角色=负信号，要主动 pitch role fit；loop 后 15min HM call 也计分。recruiter-hr-screen-bq（medium，6 帖，30min）为前置版本。

**解法**: （我的推断）准备三件套：①与 post-training/agentic 背景绑定的 mission 叙事（为什么是 OpenAI 的产品形态而非 GDM 的科研纵深/Anthropic 的安全叙事——注意不要贬损对家）；②对 AGI 安全边界给出工程化观点（能力评估、部署门槛、红队/RLHF 局限），展示 nuance；③一个 timeline-pressure 故事。

来源: <https://www.1point3acres.com/bbs/thread-1174510-1-1.html>

### Technical Deep Dive（slide 讲最强项目）——very-high，gated 轮，挂点=沟通清晰度
*medium · 频率: very high（17 帖） · 2025-12 ~ 2026-06-29*

官方题库：technical-deep-dive，other，very-high，17 帖，60min onsite，roles SWE/MLE/RE，2025-12-01 ~ 2026-06-29，tags: deep-dive/presentation/project-deep-dive。断档期细节：thread-1174510（MTS onsite）第一轮即 'Technical Project Presentation：讲解你过去做过的最牛的项目'；thread-1172810（2026-04-13 挂经）deep dive 挂因（recruiter 转述面试官 notes）：『核心就是我没有提 api，我讲的他 follow 不上，不够 clear』——不讲清接口/边界、听众跟不上=直接挂；briefing：deep dive 考察 collaboration+communication 信号，且与 HM BQ 同为 gated（技术轮过了才解锁，进入即正信号）。

**解法**: （我的推断）按'问题→约束→架构图（明确 API/数据流）→我的决策与权衡→量化结果→反思'做 slides；每 5 分钟一次听众 check-in；面向非本领域工程师校准术语密度——1172810 的挂点就是没交代 API 边界。

来源: <https://www.1point3acres.com/bbs/thread-1174510-1-1.html>
