# Anthropic 题库（爬取全量）

> 由 raw/build_question_bank.py 从爬取数据自动生成（2026-07 抓取）。每条含来源 URL 可回查原文。

## 流程与情报

### 流程核心机制：recruiter 提前告知题号，题库小而透明
*unknown · 频率: very high (10+ reports) · 2025-06 至 2026-06*

多个 2026 帖交叉验证：Anthropic 技术题库非常小且编号化（coding Q1-Q21、system design Q1-Q7），recruiter 通常在店面/onsite 前几天邮件告知你会被问哪个题号或题目家族（如 'Q6'），候选人可完全定向准备。代价是 bar 极高：题目人尽皆知后几乎零容错，有候选人反馈'题目和 follow-up 都答对了仍然挂'，评分校准在解题速度和 follow-up 深度而非新颖性。题号在 recruiter 邮件里看（thread 1142737 '题目的编号在哪里看啊'、thread 1165216 'How to Know Your Coding Question for Onsite'）。Offer 由 hiring committee + reference check 决定。

**解法**: 备考策略：拿到题号后把该题所有 1p3a 报告的 follow-up 全部过一遍，练到一次通过、主动讲 trade-off；margin for error 接近零。

来源: <https://www.1point3acres.com/interview/problems/company/anthropic>

### Anthropic SWE 完整流程结构（2026）：OA→recruiter→(HM)→店面→5轮 onsite + 硬性 gate（技术轮挂了直接静默取消后续）
*unknown · 频率: very high (10+ corroborating reports) · 2026-05*

Hack2Hire megathread + 多个 onsite 面经交叉确认的 2026 结构：Stage1 店面 ~45-55min，CodeSignal notebook 无补全（部分轨可选 ML configuration/ML fundamentals 替代 coding）。Stage2 虚拟 onsite 5 轮：Coding（1-2轮，~45min）、System Design（1-2轮）、Culture（~45min）、HM 轮、Project deep dive/retro（~20min 展示+Q&A，有人被并入 HM 轮共 50min）。关键机制：onsite 有硬性 gate，技术轮先行，若不过剩余轮次立即取消——'日历邀请不再出现'就是被刷了，无邮件通知。Staff+ 可能跳过 OA 和店面直接进 loop（2 例）。安全工程师 coding 轮与 SWE 相同。决策 10 天-3 周，HR 响应慢是普遍抱怨；最终决策可能与轮次表现脱节（有人 HM 轮好评仍被拒）。重新申请有 6 个月冷却期，且申请表会问'是否面过'并调阅旧记录。

来源: <https://www.reddit.com/r/Hack2Hire/comments/1t6ncgs/anthropic_interview_process_experience_megathread/>

### RE/RS 电面 2026 新政：四选一 track
*hard · 频率: high (5+ reports, 2026-05/06 集中出现) · 2026-05*

Research Engineer/Scientist 店面（55 min）recruiter 给四个选项自选其一：(1) Coding problem-solving（传统题，如 Q1 crawler/Q6 tokenizer）；(2) Coding & Design（如 Weighted Data Batcher）；(3) ML Configuration System（实现/设计 ML 实验配置系统）；(4) Prompting and Engineering with LLMs（在 Colab 里用 prompting 搭 pipeline，55 min Google Meet）。多个 2026 年 5-6 月帖（bbs thread 1165574 '人类学RE/RS店面问题+求组队'、thread 1167940 'RE面试讨论 RL,Code and Design,ML config'、interview thread 1166655/1166993/1164302）。有 RS 候选人（15+ 顶会论文、1000+ 引用、无 PhD）分享电面挂经（bbs thread 1137751）。

**解法**: 候选人背景是 post-training/RL，建议选 Coding & Design 或 ML Configuration System track；ML config 轮考实验配置系统的 schema 设计、继承/覆盖、验证、sweep 展开（我的推断，基于题名和 ML 实验管理惯例）。

来源: <https://www.1point3acres.com/bbs/thread-1165574-1-1.html>

### SWE/RE Virtual Onsite 结构（2026）：coding + system design + project deep dive + culture，新增 AI-assisted coding 轮
*unknown · 频率: high (5+ reports) · 2026-05*

标准 VO 四轮：(1) Coding（题库题，如 Q6 tokenizer/Bootloader/dedupe 3-part 版）；(2) System Design（Prompt Playground / inference API / image processing）；(3) Project deep dive / technical presentation（讲自己项目，40 min HM 轮问 career development 和 impact 的经典 behavioral）；(4) Culture/values（AI safety alignment，最常见挂点）。RE onsite 为 coding + ML task + behavioral + culture fit（interview thread 1137418）。2026 新增：有 onsite coding 轮明确允许并要求'使用 AI 工具编写和审查代码'，提供 Claude Code CLI 访问（Telegram 镜像）。店面规则：不许用 AI 工具，但从网上正当搜到的代码可以抄。流程前置：OA→recruiter chat（有人 OA 完 2 小时就被联系）→HM chat 20 min team match→店面→VO。EM loop 另有：HR、HM、culture fit、leadership、coding、tech project discussion、performance modeling、design review（interview thread 1137727）。

**解法**: AI-assisted 轮考察点是驾驭 agent 的工作流：任务拆解、给 Claude Code 写清晰 spec、review 生成代码、验证；平时用 Claude Code 做真实项目即最好的准备。

来源: <https://www.1point3acres.com/interview/thread/1137418>

### Research Fellowship / Alignment 轨道第一人称全流程（Goncharov）
*hard · 频率: single report（HN 高热度讨论） · 2025-02*

2025 年初 Research Fellowship 申请者（HN 热帖）。流程：(1) 在线 coding 1.5h，无真人，实现一个 class 的公开 API，4 级渐进解锁，过测试才能推进，作者勉强做完——结论：速度优先于算法优化；(2) 真人 coding 1h：单道 LeetCode medium，'比 FAANG 简单'，标准刷题准备足够；(3) 虚拟 onsite 三部分（可跨多天）：3.1 Research Brainstorm 15 分钟——与 head of alignment 通话，两个开放式 ideation 问题（考创造力和观察力，不需要专门 LLM 知识），作者第一题卡壳沉默约 3 分钟，面试官明显 disengaged，流程就此终止；3.2 Take-home 5 小时（作者因流程取消但意外收到）：把 Anthropic API 当 black box 探索研究，之后在通话中汇报发现；3.3 Culture fit 1h（未到达）。Reference check：候选人提前提供联系方式，Anthropic 在流程早期就书面+电话联系 references（作者被拒后 references 仍被联系过）。教训：实时 ideation 有运气成分，建议并行面多家。

**解法**: Research brainstorm 轮 15 分钟节奏极快：提前用'安全研究点子清单'训练自己（misalignment 检测/诱因/评测/数据毒化/奖励黑客等主题各准备 2-3 个可展开的 idea），卡壳时先大声拆解问题而不是沉默。

来源: <https://blog.faillearnrepeat.net/blog/i-failed-my-anthropic-interview-and-came-to-tell-you-all-about-it-so-you-dont-have-to>

### Anthropic Applied AI / FDE / Product Engineer 轨完整流程：prompt-engineering OA、build-an-agent 店面、数据分析+SQL onsite
*medium · 频率: high (6+ threads) · 2026-06*

多帖交叉（2026-01~07）：该轨（Sales org 下的 FDE/SA-Applied AI/Product Engineer）OA 不是 4-part ICA 而是 prompt engineering 测试（较短）；店面是 55 分钟 CodeSignal 'build an agent'（recruiter 说可能可用 Claude SDK 但禁 AI 辅助），实践中含：优化 prompt 达到特定输出、理解模型局限、debug 为什么某些 prompt 输出不稳定、改进 chatbot 边缘案例响应（教练转述）。onsite（2026-06 FDE 面经）：动机与 culture fit（'为什么 Anthropic'要接公司使命）、dataset analysis 轮（云容量管理与优化场景：资源利用率/瓶颈/浪费/成本-延迟-可靠性权衡）、project presentation（讲 ownership/判断/权衡/影响）、XFN 协作轮（含 SQL 现场题）。HM 轮考察 ML 系统经验、如何把 research 转化为生产系统。另一 sales-side 帖：recruiter screen→45min HM→take-home→final loop 6 轮（含 take-home 展示+role play pitch），申请到 offer 约 6 周。

来源: <https://www.reddit.com/r/OfferEngineering/comments/1upc38m/anthropic_jun_2026_forward_deployed_engineerfde/>

### Anthropic Research Fellow / Safety Fellowship 完整流程（对 RS 候选人最相关）：OA→references→55min 纯Python live→55min LLM prompting Colab→15min research brainstorm→5h take-home
*hard · 频率: high (8+ threads on Fellows track) · 2025-02*

两大一手来源。(1) 著名失败复盘帖（r/Anthropic 2025-02，Research Fellow/alignment 方向）：90min CodeSignal 4-level API 实现（拼速度不拼优化）→60min 真人技术面（一道 LC medium，比 FAANG 温和）→书面 reference check（流程中途就联系推荐人）→虚拟 onsite 三部分：与 head of alignment 的 15min research brainstorm（两个开放研究问题、现场出 idea，作者在此挂掉——教训：考快速创造性思维）、5 小时 take-home（API exploration/实验项目）、60min culture fit。全程禁 AI（申请材料也要求承诺不用 AI）。(2) 2025-09 Safety Fellow 帖列出的官方下一步：55min Google Meet 纯核心 Python 编码（无 ML、无库）+ 55min 'prompting and engineering with LLMs' Colab 实操 + 15min 与研究员的 research brainstorming。2026 cohort 补充：OA 换成更难 6-part；references 要求 3 封且'必须 glowing'；take-home 阶段有人 OA 满分+好评仍被拒（名额极少）。

**解法**: research brainstorm 备考（我的推断）：准备 5-6 个自己领域（post-training/RLHF/agentic evals）的开放问题和 novel 实验设计，练 15 分钟内从'问题→假设→最小实验→预期信号'的快速 ideation；LLM prompting Colab 练：写 eval harness、few-shot 构造、用 API 做 self-consistency/judge。

来源: <https://www.reddit.com/r/Anthropic/comments/1intqvv/i_failed_my_anthropic_interview_and_came_to_tell/>

### Timeline 与 offer 数据（2025-2026）
*unknown · 频率: medium (5+ data points) · 2026-03*

Timeline：OA 后最快 2 小时 recruiter 联系；VO 后 2 天内通知 reference check；reference check 后到 HC 决定可能 1 周+（bbs thread 1076641 'Anthropic最近大家多久收到面试结果'）。Offer 数据：Job多多聚合 base 平均 $250,000、股票平均 $150,005（jobs.1point3acres.com/companies/anthropic）；一例 OpenAI research offer 被 Anthropic 完全 match（bbs thread 1096908 'Open AI-Anthropic' 晒工资帖）；6 年 ML Infra 经验者面 10 家拿 2 个 offer 的 2026 求职总结含 Anthropic（bbs thread 1153543）。招聘为 rolling basis（bbs thread 1131723）。IC7 内推可跳过 OA/店面直接 full loop（Telegram 镜像）。

**解法**: 有竞对 offer（尤其 OpenAI）时 Anthropic 会 match，谈判时先拿齐 offer。

来源: <https://www.1point3acres.com/bbs/thread-1076641-1-1.html>

### 2026 Q2 面经帖索引（正文在登录墙内，值得登录后精读）
*unknown · 频率: unknown · 2026-06*

2026 年 4 月后关键帖清单：interview/thread/1177660 'SWE Onsite Interview Experience and Tips'（4-6月）；1167684 'SWE Onsite Experience and Coding Summary'；1153213 'Full Onsite SWE Interview Experience Overview'（coding challenges + culture discussions + project deep dives 全记录）；1161406 'ML Fulltime Onsite CodeSignal Prompt'；1162037 'Onsite Coding and Design for ML Role'；1159633 'ML Onsite Interview Experience'；bbs thread-1173464 'Anthropic店面 Coding Design 面经'（2026-06 最新 Coding&Design track 店面）；bbs thread-1172086 'Agent Interview 题目求助'；bbs thread-1167940 'RE面试讨论 RL/Code and Design/ML config 组队'；interview/thread/1160254 '重交 CodeSignal 分数是否影响店面'；1165216 '如何提前知道 onsite coding 题号'。这些帖标题+摘要已确认主题，正文需 1p3a 账号（部分需积分）解锁。

**解法**: 建议用已有 1p3a 账号登录后按此清单逐帖解锁；优先 1173464（最新 Coding&Design）和 1167940（RE track 汇总讨论）。

来源: <https://www.1point3acres.com/interview/company/Anthropic>

### Anthropic Interview Process: Rounds, Format & Timeline (2026) - hack2hire aggregate of 15 firsthand reports
*unknown · 频率: aggregate of 15 firsthand reports collected April 2026 · 2026-06-04*

FULL article captured. Process: application/recruiter screen -> phone screen (~45min, CodeSignal configured as a JUPYTER NOTEBOOK with NO autocomplete; candidates lose 10+ min if unprepared for the format; three tracks: coding (most common - data processing or web crawling tasks), ML configuration, ML fundamentals; recruiter hints upfront that concurrency/parallelism familiarity is expected regardless of track; coding track requires external library knowledge, especially PIL/Pillow for image processing and Python concurrency primitives) -> virtual onsite of 5 rounds (up to 6-7 if two SD rounds): (1) Coding ~45min x1-2: live coding, concurrency/parallelism follow-ups standard, PROACTIVE TESTING explicitly weighted - interviewers score how you test and narrate reasoning, library familiarity is a hard gate; (2) System Design ~45min x1-2: the 'Prompt Playground' SD round runs ENTIRELY as a written Google Doc discussion, no diagrams expected; interviewers press equally on requirements/schema/scaling and drive pacing aggressively - you must hold your own structure; a separate first SD round covers topics like batch inference API design in conventional format; (3) Culture ~45min: hard-gated - only runs after technical rounds pass; most failures here are technically-passing candidates; requires Anthropic-specific values with concrete personal examples and critical thinking about Anthropic's own tradeoffs, generic professional values answers consistently fail; interviewers hard to read; (4) Hiring Manager ~45min: deep dive on one complex past project + mentorship approach + roadmap influence; interviewer may appear cold/disengaged - not a signal; poor team fit here can block offer independent of other rounds; (5) Project Retro ~45min: structured 20-min presentation candidate must drive unprompted, then sustained challenge phase attacking every detail, circling back to things you skipped past. HARD GATING: one failed coding or SD round cancels ALL remaining rounds (incl. culture and HM) with rejection typically within 24h. Timeline: phone screen result 1-3 days; onsite result 1-2 days; rejection within 24h of onsite = technical gate failure; 2-3 days later = culture/HM stage.

**解法**: Prep implications stated by the article: practice in a Jupyter-notebook-without-autocomplete environment; drill PIL/Pillow and Python threading/multiprocessing/asyncio; rehearse the 20-min project presentation under adversarial questioning; prepare Anthropic-specific values examples (concrete conflicts and choices, not stated values).

来源: <https://www.hack2hire.com/blog/content/6a2199e28b879849ebc11ff2>

### Anthropic 面试流程/轮次/时间线（Hack2Hire 2026，基于15份一手面经，2026年4月收集）
*unknown · 频率: single authoritative writeup (15 reports) · 2026-04*

流程共6-7轮（视是否安排1或2轮 SD）：Phone Screen ~45min（跑在 CodeSignal，打开是 Jupyter notebook，无自动补全；三个 track：coding 最常见/ML config/ML fundamentals；recruiter 会预先提示需熟悉 concurrency & parallelism）；Virtual Onsite 5轮（硬门控 hard gating：coding 或 system design 任一轮 fail 会立即取消所有剩余轮包括 culture 和 HM，24小时内出拒信）。Onsite 各轮：Coding ~45min（1-2轮，concurrency/parallelism follow-up 是标配，coding track 常需外部库知识——图像处理用 PIL/Pillow、多线程用 Python concurrency 原语；主动写测试并解释推理被明确计分）；System Design ~45min（1-2轮，其中 Prompt Playground 轮是纯 Google Doc 书面讨论无需画图，考 batch inference API 设计等；面试官主导节奏很激进）；Culture ~45min（只在技术轮通过后才排；面试官难读，考对 Anthropic 特定价值观的具体个人例证 + 对公司 tradeoff 的批判性思考，泛泛价值观必挂）；HM ~45min（一个复杂过往项目 deep dive + mentorship/roadmap；面试官可能显得冷淡，团队 fit 差可独立否决 offer）；Project Retro ~45min（20分钟结构化 presentation 需自主驱动 + 挑战式追问）。时间线：phone screen 1-3天出；onsite 1-2天出；24小时内拒=技术门控失败，2-3天后拒=culture 阶段。

**解法**: （我的推断）该候选人务必：(1) 用 Jupyter/CodeSignal 无补全环境练手；(2) 复习 Python threading/multiprocessing/asyncio 及 PIL；(3) Prompt Playground SD 轮练纯文字表达 requirements/schema/scaling 深度；(4) Culture 轮准备'价值观曾发生冲突并如何取舍'的具体故事，锚定 Anthropic 特定 tradeoff 而非泛泛安全叙事。

来源: <https://www.hack2hire.com/blog/anthropic-interview-process-rounds-format-timeline-2026>

### Anthropic 到底考什么 & 为什么被拒（Hack2Hire 2026）
*unknown · 频率: single authoritative writeup (15 reports) · 2026-04*

核心洞察：Anthropic 在 culture 轮拒掉的技术合格候选人比任何技术轮都多，主导失败模式不是价值观分歧而是'表达框架'。四维度：(1) Concurrency & Library Fluency——库知识是真正的门（PIL/Pillow、Python concurrency 原语），标准数据结构知识无法绕过 follow-up；主动测试/叙述推理/验证边界与解题同等计分，静默解题者得分低于展示可见推理但不完整者。(2) Written System Design Reasoning——Prompt Playground 轮纯书面 Google Doc，不评图；考 requirements/schema/scaling 的书面深度；面试官激进主导节奏，能守住自己结构不被带偏才是评分点。(3) Anthropic-Specific Values Alignment——大多数 late-loop 拒发生在此；'我关心负责任的 AI'/'我重视技术严谨'这类在任何公司都能过的回答会持续失败；要求命名具体 Anthropic 价值、用具体经历证明、并对公司自身 tradeoff 做批判思考。(4) Sustained Challenge Defense——project retro 20分钟需自主驱动，挑战阶段针对每个细节反复追问；只排练正向陈述而无对抗准备者会中途失守。真正过滤器=alignment-as-stated vs alignment-as-demonstrated 的差距。

**解法**: （我的推断）备考重点：coding 一定练 PIL + Python 并发库并全程口头叙述+主动测试；culture/retro 准备'价值观冲突取舍'的具体故事和对抗式项目答辩。

来源: <https://www.hack2hire.com/blog/what-anthropic-actually-tests-and-what-gets-candidates-rejected-2026>

### Anthropic interview process & reported questions (interviewing.io company guide)
*unknown · 频率: aggregated from many reports · 2026-01*

Process: recruiter call (30 min, tests mission alignment) → coding challenge 60-90 min (CodeSignal take-home, 4 progressive levels, spec more complex per level, must pass all tests to advance, 2 hours total; widely-circulated example: 'implement a bank with multiple transaction types'; another reported ladder: L1 SET/GET/DELETE → L2 SCAN/SCAN_BY_PREFIX → L3 timestamped ops + TTL → L4 file compression/backup-restore) → onsite 4-5 hrs. Team match after onsite. Coding themes: data mutation, concurrency (appears across multiple rounds), multithreading, hash maps, parsing, arrays, strings, sorting. Reported system design questions: 'Design a system that enables a GPT to handle multiple questions in a single thread', 'Design a Claude chat service', 'Design a banking app'; SD emphasis on 'serving large language models efficiently, covering request batching, queuing, and GPU utilization'; advice: 'don't worry about memory constraints, focus on interesting architectural considerations'. Values round is 'where most candidates fail' — reflective + hypothetical ethical scenarios with no clean answer; they 'actively look for skepticism and pushback', not alignment-signaling; read Dario Amodei's essays. AI-assistant use in live interviews is prohibited. References are probed on conflict and ethical friction.

来源: <https://interviewing.io/anthropic-interview-questions>

### 官方：面试形式与工具（careers 页）
*unknown · 频率: 官方信息 · 2026-07*

Anthropic 官方 careers 页说明：所有面试远程通过 Google Meet 进行，时区灵活。技术岗使用 Colab 和 CodeSignal 等 live coding 工具；官方原话："You can look things up—just be comfortable with basic syntax and standard libraries so it doesn't eat up your time."（允许查文档，但要熟悉基本语法和标准库）。强调看重能力而非出身：约一半 technical staff 之前没有 ML 经验、约一半没有 PhD；建议把独立研究、博客、开源贡献放在简历最顶部；有工程背景的人建议按 engineer 轨道申请（"Engineers here do lots of research, and researchers do lots of engineering—if you have an engineering background, apply as an engineer as you'll perform better in the interviews"）。每轮都留时间让候选人提问，定位为 two-way conversation。

来源: <https://www.anthropic.com/careers>

### 官方：候选人 AI/Claude 使用政策（candidate-ai-guidance）
*unknown · 频率: 官方信息 · 2025-07*

Anthropic 官方政策页，分阶段规定：【允许】申请材料——"create your first draft yourself, then use Claude to refine it"（自己写初稿、用 Claude 润色）；面试准备——鼓励用 Claude 研究公司、练习回答、准备提问；简历/申请问题——可用 Claude 找出与 JD 最匹配的经历。【禁止】take-home 作业——"without Claude unless we indicate otherwise"；live 面试——"This is all you–no AI assistance unless we indicate otherwise"（现场实时解题不允许 AI，除非明确说明例外，例外如 performance take-home 明确允许 AI）。核心原则："We want to see your actual experience and how you think—not AI-generated responses." 注意：interviewing.io 和多个面经证实有候选人因在 live coding 用 AI 被移出流程。

来源: <https://www.anthropic.com/candidate-ai-guidance>

### AI 使用政策演变史（2025.2 禁用 → 2025.7 反转）
*unknown · 频率: 多家媒体报道（Fortune/Entrepreneur/Dataconomy） · 2025-07*

Fortune 报道：2025 年 2 月 Anthropic 要求申请者 "please do not use AI assistants during the application process"（尤其 "why do you want to work here?" essay，要考察 non-AI-assisted communication skills）；2025 年 5 月重申；2025 年 7 月政策 U-turn，允许用 Claude 打磨简历/求职信/申请材料，但 assessment 和 live 面试仍禁用。官方理由："At Anthropic, we use Claude every day, so we're looking for candidates who excel at collaborating with AI." Head of Talent Jimmy Gould 在 LinkedIn 称此变化 "isn't revolutionary, but it's intentional"。对 2026 年 7 月面试的含义：申请阶段大方用 Claude，笔试/live 阶段严格不用（除非题目说明允许）。

来源: <https://fortune.com/2025/07/21/billion-dollar-giant-anthropic-ai-ban-hiring-policy-change-job-seekers-interview-process/>

### RE/MTS 完整流程（interviewing.io 汇总）
*hard · 频率: 平台聚合多个真实候选人数据 · 2026*

interviewing.io 数据：3 个主要环节，全程 3-4 周。(1) Recruiter Call 30min——非走过场，考 mission alignment，需说出具体为何选 Anthropic（不是泛泛 AI 兴趣）；此阶段建议不透露薪资期望和竞争 offer 状态。(2) Coding Challenge 60-90min——CodeSignal 平台（异步或 live，视岗位），渐进式难度+黑盒测试判分，例题 "Implement a bank with multiple transaction types"，普遍反映时间不够用，Python 必备；有 referral 可能跳过。(3) Onsite 4-5 小时共 5 场：Hiring Manager Call 1h（项目深挖）；Coding 1h（CodeSignal 环境）；System Design 1h（共享 Google Doc 里做）；第二场 Coding 1h（岗位相关）；Company Values 1h（非技术）。技术高频主题：并发/多线程（reccurring theme）、数据变更、hash map、解析、数组/字符串/排序。System design 与真实业务相关，如 "Designing an API for serving large language models efficiently, covering request batching, queuing, and GPU utilization under variable load"。决策方式：consensus-based，无共识时 HM 拍板；reference check 做得很认真。Values 轮必读材料：Dario 的 "Machines of Loving Grace"(2024)、"The Adolescence of Technology"(2026.1)、"Core Views on AI Safety"(2023)。AI 政策："AI use in Anthropic interviews is strictly prohibited"（live 轮）。

来源: <https://interviewing.io/anthropic-interview-questions>

### Recruiter screen 与 Hiring Manager screen 细节
*medium · 频率: 多来源一致 · 2026*

Recruiter screen 30min：会挂人，考 mission alignment。样题（leonstaff 聚合）："Why Anthropic, not OpenAI or DeepMind?"、"What is your understanding of AI safety and why does it matter?"、"Walk me through your background and what you are looking for." 通过标准：对 Anthropic mission 的具体认知 + 真诚的 safety 动机，模糊的 AI 热情不够。Exponent 面经：recruiter 很有用，会透露后面轮次的考察重点并预警 values 轮。HM screen 45-60min：单个项目深挖（架构决策、tradeoff、failure modes、教训），不是多项目走马观花；Exponent 候选人：HM 'looking for signals'，快速过 conflicts 和 major projects。Glassdoor MTS 摘要版流程：recruiter call → CodeSignal pre-screen → video code-screening → onsite 4 场（1 coding、1 system design、2 behavioral）。

来源: <https://leonstaff.com/blogs/anthropic-interview-process/>

### AI Safety Fellow 完整流程与分数线（Exponent 指南）
*hard · 频率: 指南级汇总（与第一人称面经交叉一致） · 2026*

5 个阶段：(1) 申请书面材料：动机、研究兴趣、team fit、简历、可选 code sample/论文，必须提供 3 个 references；verbatim 申请题："Why are you interested in participating in the Fellows program?"、"Tell us briefly about one or more research areas you're excited about right now"、"How likely are you to accept a full-time offer at Anthropic if you receive one?"。(2) CodeSignal OA 90min、4 个渐进 stage、满分 1000：官方公布 cutoff 480，但实际通过线接近 600（'most aggressive filter'）；样题即 in-memory database with TTL / "Build a bank account system that maintains accounts in a fake bank" / file system 渐进复杂度。(3) Live coding screen 90min，与 Anthropic 工程师在 CodeSignal 平台。(4) Prompting & LLM Engineering 轮：55min Google Colab 编码任务 + 15min research brainstorm。(5) Reference checks：3 个 references 可能在流程任意时点被联系。节奏快：过轮后 3 天内约下一轮。Fellowship 本身 4 个月带薪（约 $61,600 津贴 + $60,000 算力），约 25-50% 转正。

**解法**: Colab 的 Prompting/LLM engineering 轮对 post-training 背景候选人是主场：练熟 Anthropic API 调用、结构化 prompt、简单 eval harness（生成→判分→聚合）的现场手写。

来源: <https://www.tryexponent.com/guides/anthropic-ai-safety-fellow-interview>

### 官方博客：AI-resistant 评估设计哲学（take-home 三次改版）
*unknown · 频率: 官方信息 · 2026-01*

Anthropic 工程博客（2026 初）：解释为何用 take-home 而非纯 live 面试（更长时间线、真实环境、允许上手工具与理解成本），好评估的原则：不 hinge on a single insight、给候选人多次展示机会、代表真实工作、高信号、不需要窄域专业知识、有趣。为何 take-home 允许 AI："longer-horizon problems are harder for AI to solve completely, so candidates can use AI tools (as they would on the job) while still needing to demonstrate their own skills." 三个版本演化：V1（2024，4h）被 Opus 4 超过几乎所有人类 → V2（2025 中，2h）被 Opus 4.5 一小时内达到通过线 → V3（现行）改为微型受限指令集的约束优化谜题（类 Zachtronics），Claude 表现不佳。对候选人的含义：Anthropic 的评估会随模型能力持续换题，live 轮禁 AI、take-home 轮明确说明才可用。HN 讨论补充（paxys）：公开版 take-home 打线只是'进入招聘管道'，之后仍要走标准面试轮。

来源: <https://www.anthropic.com/engineering/AI-resistant-technical-evaluations>

### 第一人称（RE 轨道，2025）：pre-screen 易、live screen 挂（Zharkov）
*medium · 频率: single report（多处与其他来源交叉一致） · 2026-03*

Senior ML/RE 候选人 2025 年面约 15 家 AI 公司的总结（2026-03 发布）。Anthropic 部分：无 referral 申请，3 个月才收到回复（他见过的最慢）；pre-screen 即 90min 4 级解锁式 OA——他认为比传闻容易：45 分钟做完前 3 级，提前 20 分钟完成第 4 级；确认'没人看测试之外的代码——测试全过就行，代码质量和效率不重要，忘掉花哨算法'；也辟谣'对摄像头答题'传闻不存在。之后过 recruiter call，但在与工程师的 live technical screen 挂掉（自述当周工作 80 小时状态极差，题目本应轻松做出）。另记录 Anthropic 申请表书面题："Why Anthropic? [Why do you want to work at Anthropic?] (We value this response highly - great answers are often 200-400 words.)"——同一公司各职位申请表问题基本复用，答案可存档复用。

来源: <https://reyzharkov.com/blog/posts/interviews-2025-ml-research-engineer-uk>

### Offer 阶段：reference check、team matching、薪酬数据点
*unknown · 频率: 多来源交叉 · 2025-2026*

多来源一致的流程尾部特征：(1) Reference check 异常严格且发生在流程中（而非 offer 后）——Exponent 候选人：'References were requested early and specifically from senior-level former managers and coworkers'；Goncharov：被拒后 references 仍被联系；Sundeep Teki 指南：'conducts rigorous reference checks during the interview cycle'。(2) 多轮有 shadow interviewer（面试官校准）。(3) Team matching / headcount 可能在通过后卡人：Blind 有'过了 onsite 无反馈被拒'的报告；leonstaff：有人因 headcount 而非表现在此阶段被拒，1-2 周或更久。(4) 薪酬数据点（Blind，登录墙、来自搜索摘要）：IC5/6 SWE 一例 400k base + 4M/4yr vesting ≈ 1.4M TC；前端一例 $405k base + $1.2M RSU/年。聚合站范围（参考）：SWE L4/L5 TC $250-400K；RS/RE TC $300-600K。谈判：第一个 offer 很少是最终值，书面竞争 offer 杠杆最强。

**解法**: 提前准备好 3 个高质量 senior references（前 manager 优先）并打好招呼，Anthropic 会真的深聊。

来源: <https://www.teamblind.com/company/Anthropic/posts/anthropic-interview>

### 整体时间线与通过率参考
*unknown · 频率: 多来源统计 · 2026*

时间线：interviewing.io 称全程 3-4 周；Sundeep Teki 称平均约 20 天、'one of the hardest interview processes in tech'、CodeSignal 需要接近满分才推进；Glassdoor（129 份提交，搜索摘要）平均 19 天，面试体验 36.1% positive，难度 3.26/5；研究岗因 take-home/presentation 和 team matching 拉长到 4-8 周。Exponent Safeguards 候选人因有竞争 offer 被 fast-track 到 2 周。各轮间隔短（过轮后约 3 天内约下轮）。回复速度方差大：Zharkov 无 referral 等了 3 个月才开始流程。挂点分布（多来源）：CodeSignal OA 是最大漏斗；values 轮是 onsite 最高挂率轮（recruiter 原话）；recruiter screen 也会挂人。

来源: <https://www.glassdoor.com/Interview/Anthropic-Interview-Questions-E8109027.htm>

### DevRel 等非工程岗也有 take-home（taylor.town 案例）
*unknown · 频率: single report · 2025-09*

Taylor Troesh（2025 年中，HN 热帖 'Flunking my Anthropic interview again'）申请 Developer Relations 岗：完成了 take-home 作业后被拒（未披露题目细节）；此前 2022 年曾因在自动化 coding challenge 中误点按钮而挂。作者为申请额外做了 side project（diggit.dev）+ 博客并上了 HN 首页、有内部朋友 referral，仍未通过——说明 take-home 评审标准严格且不透明。信息价值：非工程岗位同样有 take-home 环节；参考 Anthropic 官方政策，take-home 默认禁用 Claude。

来源: <https://taylor.town/flunking-anthropic>

### Anthropic 薪酬/offer 数据点与谈判背景（2025H2-2026）
*unknown · 频率: multiple data points · 2026-04*

OfferEngineering/FAANGrecruiting 数据点：Staff MLE（L6，Bay Area，2025-10 offer）base $430K + stock $11M/4yr → 首年 TC ~$3.18M，被拒签。社区讨论 RSU 估值随融资轮波动。offer 时间线：final 后 10 天到 3 周；有人 HM 好评后一周无声，跟进后收到模板拒信——'不到 position filled 不告诉你被拒'是常见抱怨。谈判杠杆：竞争 offer 可 expedite（Fellows 有人以竞争 offer 期限成功提前）。注：该 sub 由 chillinterview.com 运营，数据为二手聚合。

来源: <https://www.reddit.com/r/OfferEngineering/comments/1sgbm8r/anthropic_staff_mle_l6_offer_318m_firstyear_tc/>

### Anthropic Staff 轨 Technical Project Discussion / Project Deep Dive 轮：2年期项目全维度拷问 + ROI 判断题
*hard · 频率: 3 reports · 2026-07*

Staff/Sr Staff onsite 面经（2026-06/07）：单独一轮 45-60min 由资深面试官深挖一个过往项目：架构决策、权衡、瓶颈、引入的技术债、监控方案、事后复盘会怎么重设计。真实 follow-up：'如果项目花了约 50 engineer-years、每个工程师年成本 $400K，这项目值不值 $20M 投资？'——考 staff 级 ROI/业务判断。L4 面经同样强调此轮'被普遍低估，拷问深度远超一般准备'。FDE 轨对应为 project presentation（ownership/判断/权衡/影响/反思）。

**解法**: 选一个有真实权衡和量化影响的项目，准备三层深度：系统图与关键决策点、被挑战时的备选方案对比、成本收益量化（工程师年成本×人数 vs 节省/收入）。

来源: <https://www.reddit.com/r/OfferEngineering/comments/1umrpmp/anthropic_jun_2026_staff_swe_infra_interview/>

## Coding 题

### Coding Q1：Concurrent Web Crawler（题库最高频经典题，完整题面）
*medium · 频率: very high (High 标注, 16+ 讨论) · 2026-05*

55 min。实现 crawl(startUrl, htmlParser) -> list[str]：给 htmlParser.getUrls(url) helper（LeetCode 1242 风格），BFS 抓取同 hostname 的所有 URL 并去重，在 CodeSignal 里跑通。Follow-up 链：(1) 用 ThreadPoolExecutor 并发化——线程安全的 visited set + work queue，或 asyncio 版本；(2) 论证 threads vs processes vs asyncio 的选择（IO-bound）；(3) 口头分布式扩展：多机 sharding、跨机去重（Redis/中心队列）、per-host 限流、故障恢复；(4) asyncio.gather vs as_completed vs semaphore 限流池的语义区别。注意：2025 年中起环境从 Replit 换成 CodeSignal，第一次 run 常要修 import；先澄清 URL fragment/规范化范围；不要过度设计。Last asked 2026-05-03，roles: SWE/MLE/Infra。

**解法**: 单线程 BFS 打底 → ThreadPoolExecutor + lock 保护 visited + queue.Queue，或 asyncio + Semaphore；hostname 用 urllib.parse 提取；重点是把每个 follow-up 讲透而非代码量。

来源: <https://www.1point3acres.com/interview/problems/company/anthropic/coding-q1-web-crawler>

### OA（CodeSignal，90 min，4 levels）：题目家族全景 + 2026 新变种
*medium · 频率: very high (10+ reports) · 2026-05*

SWE/MLE/Fellowship 通用入口 OA：90 分钟 4 个 level 递进（同一系统逐级加功能），满分 1000，有人 800/1000 过线且 2 小时后 recruiter 主动联系。题目家族（多帖汇总）：(1) Banking System（交易系统：开户/存取/转账/调度）；(2) In-Memory Database（简化内存数据库：set/get/delete/scan+TTL+backup/restore）；(3) Cloud Storage System（文件→元信息映射，纯内存，ADD/COPY/GET/FIND+用户容量+压缩备份，Dropbox 风格）；(4) Student Course Registration（存储设计、重复处理、学分约束，interview thread 1059593）；(5) Task Management System（CRUD+优先级排序+用户配额+历史查询）；(6) 2026 新变种：Recipe Manager（两个独立报告：一人提前 40 分钟满分）。bbs 帖：1075137 'OA完整4问'、1049492、1088828、1094617、1134890、1042058、1078644。

**解法**: CodeSignal Industry Coding Framework 套路：用 dict-of-dataclass 建模，先读完 4 个 level 再设计，Level 3/4 常加 TTL/时间戳、备份恢复、按字段排序查询；目标 90 分钟内做完 4 级，练 2-3 套模拟即可迁移到任何变种。aonecode 有 Cloud Storage 4-level 结构：https://aonecode.com/iq/docs/antropic/online-assessment/cloud-storage-system

来源: <https://www.1point3acres.com/bbs/thread-1075137-1-1.html>

### Anthropic · Concurrent Web Crawler（并发爬虫，companyFreq Anthropic=10）
*medium · 频率: very high — Anthropic 频率标注 10/10（phone screen 常见 coding track 之一） · 2025-12 首发，最近报告 2026-03-24*

题干（正文锁定，据 insights）：实现多线程爬虫，从给定起始 URL 探索页面；只保留与起始页 hostname 完全相同的链接；所有 URL 去除 fragment(#) 后再去重和比较 hostname。考点：CONCURRENCY + GRAPH。Follow-up：如何实现 crawl delay / 限流以免压垮目标服务器？如何在并发下支持 BFS vs DFS 优先级？如何架构成跨多 worker 节点而非单进程？

**解法**: 站内提示：多线程安全读写 visited 集合避免重复/死锁；用 ExecutorService 异步派发任务 + 线程安全 Set + Phaser 或原子计数器判定所有爬取完成。（我的推断）这正是 Anthropic blog 强调的 concurrency/parallelism 门槛题——务必熟练 Python threading/ThreadPoolExecutor 或对应并发原语。

来源: <https://www.hack2hire.com/question-bank/companies/anthropic/coding-questions/692f5158cd79766b0b310122/practice>

### Anthropic · Find Duplicate Files（LeetCode 609 变体，二进制内容去重，companyFreq Anthropic=10）
*hard · 频率: very high — Anthropic 频率标注 10/10（Screening+Onsite） · 2025-12 首发，最近报告 2026-06-29*

题干（LeetCode 609 变体）：在模拟文件系统（根 '/'）中找二进制内容完全相同的重复文件组。两文件重复当且仅当完整二进制内容完全一致（文件名/路径无关）。文件内容可能很大，只能作为二进制流访问，无直接字符串内容访问。需设计能在大量文件/目录中高效找重复的方法。考点：RECURSION + 哈希。Follow-up：如何扩展到分布式文件系统？如何减少哈希碰撞的误报？百万文件时如何降内存？能否检测部分相似/修改过的文件？

**解法**: 站内提示：先递归遍历目录收集所有候选路径；用 file size 等元数据快速排除不可能重复的；对通过 size 过滤的文件读一次二进制流算稳定 hash（如 SHA）分组。建议先刷 LeetCode 609。

来源: <https://www.hack2hire.com/question-bank/companies/anthropic/coding-questions/6934db5e5f306485cc5f08b9/practice>

### Anthropic · Find Cluster Mode and Median（分布式求众数/中位数，companyFreq Anthropic=10）
*hard · 频率: very high — Anthropic 频率标注 10/10（Screening+Onsite） · 2025-12 首发，最近报告 2026-01-17*

题干：大型分析公司把海量整数数据集分布到 k 个 worker（0..k-1），每个 worker 只能访问自己那份未排序、均匀分区的数据切片。设计分布式算法计算整个数据集的 mode（出现最频繁的整数），同时确保没有 worker 拿到全部原始数据且最小化网络使用。平局（多个整数并列最高频）时返回最小的那个。考点：DESIGN / 分布式聚合。Follow-up：如何优雅处理 worker 崩溃/网络超时？某些数字远比其他频繁时如何缓解 hash skew？能否扩展到 top-K 而非仅 mode？异步消息延迟如何影响同步与终止逻辑？

**解法**: 站内提示：先本地按频率压缩（传 (value,count) 元组而非原始数据）；避免中央收集器——用只依赖 value 的确定性公式把每个唯一 value 路由到恰好一个 worker；路由后各 worker 聚合分到的计数、找本地 leader，再做最终 reduction 定全局赢家。（我的推断）本质是 MapReduce/shuffle-by-key 的手写版。

来源: <https://www.hack2hire.com/question-bank/companies/anthropic/coding-questions/6935ba711553144e303f6769/practice>

### Anthropic · CRUD/内存数据库风格 OA 题组（Banking / In-memory DB w/ Backup / Cloud Storage / Worker Mgmt / Note-Taking / Task Assignment / Recipe Mgmt）
*medium · 频率: very high — 多为 CodeSignal 4-level 演进式 OA；Anthropic 频率：Banking 10、Cloud Storage 7、In-memory DB 9、Worker Mgmt 6、Note-Taking 7、Task Assignment 7、Recipe 7（这些题也高频出现在 Coinbase/HubSpot/Ramp） · 2025-07 至 2026-05*

Anthropic 的 OA/coding 常见一类'渐进式设计题'（practice URL 形如 .../anthropic/coding-questions/{id}/practice）：(1) Design Banking System [Medium, id 687c23f9aa2b26b0b64b39d4]：createAccount/deposit/transfer，每操作带递增时间戳；扩展常含 top-K 转账账户、定时支付/cashback、账户合并（这是著名的 CodeSignal 4-level 银行题）。(2) Design In-memory Database with Backup [Hard, id 689505de3a1d9e6d6042d519]：setData/getData/deleteData 字段级 + scan/backup/restore。(3) Cloud Storage System [Hard, id 689cf808aee746eb1c84ba37]：addFile/copyFile/getFilesize + 前缀查询/用户容量/压缩（4-level）。(4) Design Worker Management System [Medium, id 68a4bbdfc11d63d6052ea306]：worker 进出办公室时间戳、累计工时。(5) Design Note-Taking System 'SecondBrainSystem' [Medium, id 69b351ffa4e93c007df404fd]：CRUD + 唯一自增 ID + 大小写不敏感标题。(6) Design a Task Assignment System 'TaskManager' [Hard, id 69efc8e696981f58ae1f6d73]：addTask 返回 'taskId<n>'、updateTask、按 name/priority 检索。(7) Design Recipe Management System [Medium, id 69f2664c42791c82ab992693]：CRUD + 唯一大小写不敏感名 + 不复用 ID。

**解法**: 站内提示统一：用两层/多个 hash map（ID→实体、规范化名→ID 做唯一性）；操作前先做全部校验再提交状态变更；ID 计数器只增不减。（我的推断）建议按 CodeSignal 4-level 模式练：level1 基础 CRUD→level2 加过滤/排序→level3 加时间/TTL→level4 加合并/回滚，这是这批题的通用演进。

来源: <https://www.hack2hire.com/question-bank/companies/anthropic/coding-questions>

### CodeSignal OA 题型一：In-memory Database（4 levels，90 分钟）
*medium · 频率: very high（Blind/Glassdoor/博客 10+ 独立报告） · 2026-04*

Anthropic 标志性 OA（也用于 live coding 轮），90 分钟 4 个递进 level，逐级解锁（当前 level 测试全过才能看下一级），黑盒测试判分。具体拆解：Level 1：基本操作 SET/GET/DELETE；Level 2：加 SCAN、SCAN_BY_PREFIX（要求排序和严格输出格式）；Level 3：加 TTL——SET_AT/GET_AT/DELETE_AT/SCAN_AT（带时间戳的状态管理）；Level 4：backup/restore（数据库快照与恢复）。常见坑：TTL 边界条件应为 ts < start_time + ttl 而不是 <=。Blind 汇总：满分 600（也有 1000 分版本报告），基本要接近满分才能进下一轮，但满分也不保证通过（还看简历匹配）；大多数人做不完 4 级。

**解法**: 速度题不是算法题：暴力解完全可以（O(n) scan 都行），别上花哨数据结构。用一个 dict 存 (value, expire_ts)，把 GET/SCAN 的过期判断抽成公共函数，Level 4 快照直接 deepcopy + 记录时刻。写法要模块化，新 level 尽量是增量改动；每写完一小块就跑测试，别攒到最后调试。（来源：Blind 多帖 + Zharkov 博客一致建议）

来源: <https://medium.com/@programhelp/anthropic-interview-questions-2026-oa-technical-interview-breakdown-08d68034a47d>

### CodeSignal OA 题型二：Banking System（4 levels，90 分钟）
*medium · 频率: very high（5+ 独立报告，interviewing.io 称跨 Glassdoor/Blind 一致确认） · 2026-04*

与 in-memory DB 二选一出现的另一套 OA 题（多个渠道确认为 Anthropic 最高频编码题，OA 和 live coding 轮都出现过）。Level 1：开户与存款；Level 2：转账与支付；Level 3：账户合并（合并余额、交易历史、支付记录、账户状态）；Level 4：cashback 逻辑（需要回头重构 Level 2 的支付实现）。interviewing.io 的表述为 "Implement a bank with multiple transaction types"。这类题在 CodeSignal 官方叫 Industrial Coding Framework 风格。

**解法**: 同 in-memory DB：模块化 + 增量应对需求变化是评分核心。把'交易'建模为统一记录（type/amount/timestamp/counterparty），合并账户=合并记录列表+重算派生状态；cashback 若 Level 2 写死了支付流程就会很痛，提前把支付拆成 create-payment / settle 两步。（我的推断+多来源提示）

来源: <https://medium.com/@programhelp/anthropic-interview-questions-2026-oa-technical-interview-breakdown-08d68034a47d>

### Blind 聚合：CodeSignal OA 实战情报
*medium · 频率: very high（Blind 10+ 帖） · 2025*

Blind 多帖（登录墙，内容来自搜索聚合摘要）：邮件说明 OA 为 4 parts、90 分钟、涉及一个 toy simulator；题目二选一：banking app 或 in-memory database；定位是 speed test——"coding is not complicated, but you have to code VERY FAST"；CodeSignal 官方邮件即承认大多数人做不完 4 级。技巧共识：不需要算法优化、暴力省时间；逐块写代码逐块验证，比全部写完再 debug 好；满分 600（另有 1000 分制报告）；速度比优雅重要；perfect score 也可能因简历不匹配被拒。相关帖：Anthropic codesignal experience (eh3Kq1mc)、Anthropic CodeSignal: what to expect (Gc7vZ81T)、Anthropic OA (ue2vvwWk)、Anthropic codesignal score (Dv1aFZY3)、Anthropic Interview Megathread (6estt896)。

**解法**: 练法：CodeSignal 的 Industrial Coding Framework 练习题 + 限时模拟；用 Python dataclass + dict 起手模板；先通读所有可见需求再动手。

来源: <https://www.teamblind.com/post/Anthropic-codesignal-experience-eh3Kq1mc>

### Anthropic CodeSignal OA：90分钟4段渐进式 industry coding（银行系统/内存数据库/图书馆系统等变体）
*medium · 频率: very high (15+ reports across 10 threads, 2024-09 to 2026-06) · 2026-01*

所有 SWE/RE/Fellows 轨都先过这个无人监考 CodeSignal OA。格式：一道渐进式 CRUD 类系统构建题，4个 level（250/500/750/1000 分，部分显示折算为 600 满分），必须先全过当前 level 的测例才解锁下一 level，后期 level 要求回头重构前面的代码。已知题目变体：银行系统（开户/转账→定时交易→计息）、内存数据库（CRUD + TTL + 配额 + 辅助函数）、图书馆系统（add book/borrow/return，第4段有性能测试，超时算失败）、progressive filesystem。评分极严：多人报告 570/600、850/1000 被拒，社区共识'基本要满分'（Fellows 项目官方口径 480/600 以上才推进）；也有人 750/1000 被拒后重考通过（可申请 retake）。无自动补全/intellisense，切出浏览器 tab 可能取消资格，禁 AI。时间压力是最大难点：90 分钟要全速写代码，брute force 够用、别追求最优解；先设计可扩展的数据结构避免后期重构。2026 年起部分轨（Fellows/MATS）换成自研 6-part 版本，'难一个数量级'，题面像 essay 而非 leetcode 式题干。

**解法**: 练 CodeSignal Industry Coding Assessment 原题集（banking system 等）；用 Python（写得快）；第一层就把实体抽象成 class + dict 索引，留好扩展点；每层限时分配（6/20/30/30分钟）；测试已给、TDD 风格跑测例。来源+我的推断：这类题社区题库在 CodeSignal 官方 ICA 白皮书和 hack2hire/prachub 有仿真题。

来源: <https://www.reddit.com/r/leetcode/comments/1qx0hyj/anthropic_technical_interview_55_min_codesignal/>

### Anthropic 店面/onsite 高频题：web crawler（先串行后并发）+ 并发知识清单
*medium · 频率: very high (6+ independent reports) · 2026-05*

多个独立来源确认：'implement a web crawler and return all unique urls' 是 Anthropic 店面的招牌并发题——先写串行逻辑，再加 concurrency/parallelization。Senior SWE 店面邀请明确写'需要会 concurrency'。考察点（辅导教练总结+考生确认）：locks/mutexes、线程安全数据结构、producer-consumer 模式、死锁、spin lock vs sleep lock、进程 vs 线程、async/await、race conditions。E5 大厂工程师因没准备并发直接挂掉店面（r/leetcode E5/6 面经帖）。Applied AI/SWE 的 live 轮也可能是'debug 或扩展已有代码'而非从零写。

**解法**: Python 版标准解：ThreadPoolExecutor + queue.Queue + visited set 加 lock（或用 asyncio + aiohttp + asyncio.Queue + set，配 semaphore 限并发）；讲清楚为什么 visited 检查和插入要原子。准备 BFS 深度限制、同域名过滤、失败重试 follow-up。

来源: <https://www.reddit.com/r/leetcode/comments/1t40v4c/anthropic_concurrency_questions/>

### Coding Q6：Tokenizer（2026 店面/onsite 高频）
*medium · 频率: high (5+ reports, 2026 Q1-Q2) · 2026-04*

实现 tokenizer，核心是贪心最长匹配（longest match）分词：给 vocab，对输入串反复取最长可匹配 token。考察点：bug finding（给带 bug 的实现让你修）、longest match 正确性、实现细节。一位候选人先写朴素 for 循环做最长匹配，再升级 trie 结构。相关帖：interview thread 1169657 'Q6 Tokenizer Technical Phone Screen'（bug finding + longest match + implementation）、1156951 'SWE Onsite Q6 Coding Question Details'、1160525 'What is the Coding Q6'、1143701 'Tech Phone Screen Prompts for Q2 and Q6 (MLE)'。

**解法**: 我的推断：先写 dict+按长度倒序尝试的 O(n·L) 版本保证正确（含无法匹配时的 fallback/unk 处理），follow-up 优化用 trie 做单遍最长匹配；准备讨论 BPE 与贪心最长匹配的区别、流式输入、词表更新。

来源: <https://www.1point3acres.com/interview/thread/1169657>

### File Deduplication（找重复文件）——店面/onsite 常青题，完整题面
*medium · 频率: high (5+ reports, 2024-2026 持续出现) · 2026-01*

遍历目录树，按字节内容（非元数据）找出完全相同的文件，输出 size≥2 的重复组，每组一行空格分隔路径。例：/a/1.txt='hello', /b/2.txt='hello', /c/3.txt='world' → 输出 /a/1.txt /b/2.txt。要求处理大文件：不能一次读进内存。Follow-up：IO-bound（磁盘读是瓶颈）怎么优化 vs CPU-bound（hash/比较是瓶颈）怎么优化。多个报告：店面出现（interview thread 1141385），有 3 个 part 的 onsite 版本（bbs thread 1097726），有人被要求自己写 filesystem 遍历方法；一人因 runtime 执行问题挂掉。

**解法**: 三级分组：size → 首块 hash → 全文 hash/逐字节比较；分块读（如 1MB chunk）；IO-bound：并行读多盘/减少读放大（size 预筛掉大部分）；CPU-bound：更快 hash（xxhash）、多进程、只 hash 采样块后精确比对。

来源: <https://www.1point3acres.com/interview/problems/42afe615-f6b2-494c-807f-37c309841f8b>

### Concurrent Web Crawler (LC 1242 variant with URL sanitization)
*medium · 频率: Anthropic freq 10/10 (their highest); last reported 2026-03-24 · 2025-12 (published)*

UNLOCKED - full statement captured. Stage: phone screen. Variation of LeetCode 1242 Web Crawler Multithreaded. Given startUrl and htmlParser.getUrls(url) (each call has simulated ~10-15ms network latency), return all unique URLs with the EXACT same hostname as startUrl. Twists vs LC1242: must strip URL fragment (everything from '#') BEFORE hostname comparison and dedup ("http://example.com/page#s1" == "http://example.com/page"); hostname = substring between "://" and next '/'; graph may contain cycles; must use concurrency because of per-call latency (<=1000 urls, <=1000 edges, each getUrls <=15ms). 3 worked examples captured. Site follow-ups: rate limiting/crawl delay; BFS vs DFS priority under concurrency; scaling to multiple worker nodes (distributed crawler). Acceptance 56.4%. This matches the widely-reported Anthropic screen 'async web crawler' question.

**解法**: Official editorial (captured): concurrent BFS with ThreadPoolExecutor; thread-safe visited set guarded by a lock, add-before-submit to avoid duplicate scheduling; completion tracking via task counter/phaser; sanitize (strip '#') then compare host then dedup. O(N+E) time, O(N) space. Full reference solutions in Python (threading + lock + task_count), Java, C++, TS captured.

来源: <https://www.hack2hire.com/question-bank/companies/anthropic/coding-questions/692f5158cd79766b0b310122>

### Anthropic · Repair Bootloader Program（指令模拟找首个重复执行，companyFreq Anthropic=8）
*hard · 频率: medium-high — Anthropic 频率标注 8/10 · 2026-06 首发，最近报告 2026-07-09*

题干：bootloader 把程序存为文本指令数组，需找到执行首次开始重复的位置。给定 instructions，每条形如 '<operation> <value>'，operation 为 'plus'/'next'/'jump'：'plus x' 给全局累加器加 x 然后移到下一条；'next x' 累加器不变移到下一条（x 保留在格式中但本题忽略）；'jump x' 累加器不变，跳到当前索引+x 的指令。从索引0开始执行，返回首次重复执行的指令索引，若程序正常终止返回 -1。考点：SIMULATION / 函数图环检测。Follow-up：若指令集含条件跳转如何改？能否在仍高效检测环的同时降低空间复杂度？跳转越界怎么办？此题如何映射到函数图的环检测（Floyd）？

**解法**: 站内提示：记录每个访问过的指令索引；在执行当前指令前检查是否重复；用布尔数组或 hash set 做 O(1) 查找，整体 O(N)。类似 AoC 2020 Day 8。

来源: <https://www.hack2hire.com/question-bank/companies/anthropic/coding-questions/6a373b2b6849fecc81442861/practice>

### Anthropic · Generate Function Profiling Events（LeetCode 636 变体，栈快照转事件，companyFreq Anthropic=9）
*hard · 频率: high — Anthropic 频率标注 9/10 · 2025-12 首发，最近报告 2026-05-31*

题干（LeetCode 636 Exclusive Time of Functions 变体）：采样 profiler 周期性记录单线程执行状态。每条 samples 形如 '<time>:<stackTrace>'：time 是严格递增整数时间戳；stackTrace 是 '->' 分隔的函数名列表，从最外层到当前执行的最内层（如 'main->worker->parse' 表 main 调 worker 调 parse）；栈可能为空（如 '42:'）。需把周期性栈快照转换成按时间顺序的 start/end 事件。考点：HASH_TABLE + STRING。Follow-up：如何扩展到多并发线程？如何计算每函数 exclusive vs inclusive 时间？样本历史无限增长时如何优化内存？

**解法**: 站内提示：从最外层向内比较相邻两次栈快照找首个不匹配点；不匹配点后消失的帧=已结束，新增的帧=最近开始；把每个栈位置当独立调用帧，忽略不同深度的重名。建议先刷 LeetCode 636。

来源: <https://www.hack2hire.com/question-bank/companies/anthropic/coding-questions/69308191cd79766b0b310224/practice>

### Anthropic 55分钟 live 技术店面（CodeSignal notebook）真题：图像处理管线（Pillow + JSON 配置）
*medium · 频率: high (4+ independent reports) · 2026-06*

多个独立报告的高频店面题（前端/后端/senior 都有人抽到）：给一组图片和一个 JSON 定义的 pipelines 列表，每个 pipeline 含变换序列（转黑白、resize、水平翻转等），实现主函数把每张图按其 pipeline 顺序处理并导出。需要现场选图像库（Python 基本只能 Pillow）、快速读文档、把每种变换映射到库调用。Follow-up：图片变大后的性能优化——判断 I/O-bound vs CPU-bound；I/O: 流式读取/批量文件操作；CPU: 跨图片并行（进程池）、避免重复变换。环境是 Jupyter 式 notebook、无自动补全、可 Google（不能点 AI 摘要）、禁 AI。一人用 Java 被允许但 Pillow 题基本锁 Python。有人因此挂掉，有人过（评论：'每一步都能 google，不难但时间极紧，一个错误选择就完了'）。

**解法**: 提前背熟 Pillow API：Image.open/convert('L')/resize/transpose(Image.FLIP_LEFT_RIGHT)/save；写一个 dict 把操作名映射到函数的 dispatcher；先跑通单图单变换再泛化。

来源: <https://www.reddit.com/r/OfferEngineering/comments/1ub6od5/anthropic_frontend_phone_screen_not_leetcode_but/>

### Anthropic 店面/onsite 编码真题：Repair Bootloader Program（=Advent of Code 2020 Day 8 变体）
*medium · 频率: high (3 reports Jun-Jul 2026) · 2026-07*

2026 年 6-7 月三个独立报告（店面 + Staff/Sr Staff onsite coding 轮都出过）。题目：给一个指令文件（自造小语言），三种操作——plus（累加器加值）、next（顺序下一行）、jump（相对偏移跳转）。从第一行开始执行直到跑出文件末尾或死循环。要求：检测何时陷入无限循环（重复访问同一行）、找出导致循环的行——bug 是某一行的 jump 和 next 被互换，修复（换回来）使程序正常终止，并返回进入循环前的累加器值/终止时累加器值。onsite 版约 50 分钟做完含 debug。考生评价：理解题意花 10 分钟，实现本身不难；考的是仔细模拟、循环检测、debug、确保修复后程序终止。

**解法**: 即 AoC 2020 Day 8（acc/nop/jmp）：先写解释器 + visited set 检测循环；然后对每个 jump/next 指令试着翻转一次，重跑看是否终止（O(n²) 足够）；返回对应累加器值。

来源: <https://www.reddit.com/r/Hack2Hire/comments/1umm6xj/anthropic_phone_screen_experience/>

### Anthropic SDE 编码真题（近3个月高频）：从调用栈快照重建函数 start/end 事件
*medium · 频率: high (2 independent sources, flagged 'recent 3 months') · 2026-07*

完整题面（OfferEngineering 2026-07 收录，另有 InterviewCoderHQ 独立佐证'converting profiler stack snapshots into function start/end events'）：给定周期性调用栈快照列表，每条格式 "<timestamp>:<callPath>"，timestamp 严格递增，callPath 是 'app->load->parse' 形式（外到内），空路径表示无函数运行。对比相邻快照：共同前缀之后新出现的函数产生 start 事件，前一快照中消失的函数产生 end 事件（end 按最内到最外输出）。递归调用视为独立栈帧；最后一个快照后仍活跃的函数不产生 end。实现 List<String> buildEvents(List<String> snapshots)，输出 "start:<time>:<fn>" / "end:<time>:<fn>"。例：["1:app->load","3:app->load->parse","5:app->load","8:app"] → [start:1:app, start:1:load, start:3:parse, end:5:parse, end:8:load]。

**解法**: 每步求前后两栈的最长公共前缀长度 k（注意递归同名帧按位置比较）；prev[k:] 逆序发 end，curr[k:] 顺序发 start。边界：首快照全 start、空路径、连续相同栈不发事件。

来源: <https://www.reddit.com/r/OfferEngineering/comments/1urq3za/anthropic_coding_question_reconstruct_call/>

### Coding Q2：LRU Cache 及其 VO 变种'可持久化的 Memoization LRU Cache'
*medium · 频率: medium (3+ reports) · 2026-03*

店面 Q2 = LRU cache（interview thread 1152730 'Fulltime SWE Tech Phone Screen Q2 Coding Question'）。VO 出现新变种：'可持久化的 Memoization LRU Cache'（Telegram 镜像帖，SWE onsite）——在 LRU 基础上加 memoization decorator 语义和持久化（save/load）。另有 'Thread-Safe Linked List Task Queue Transformation'（把链表任务队列改造成线程安全）出现在题库。

**解法**: 标准 OrderedDict/双链表+dict 打底；变种考点（我的推断）：decorator 包装函数签名做 key（args 需 hashable/序列化）、eviction 与持久化一致性、线程安全加锁粒度。

来源: <https://www.1point3acres.com/interview/thread/1152730>

### Fellows/Safety Fellowship OA（2026）：DNS resolver + Python debugging；prompts→GPT servers 哈希映射
*medium · 频率: medium (3 reports, 2026 Q2) · 2026-05*

(1) Anthropic Fellows（ML intern，2026 July cohort）两轮 CodeSignal OA：第一轮 DNS resolver 实现，第二轮 Python debugging（interview thread 1177056，2026-05-16）。(2) Safety Fellowship CodeSignal OA：'mapping prompts to GPT servers using a hash table'——用哈希表把 prompt 路由到服务器（interview thread 1163421，详情在登录墙内）。(3) AI Safety Fellow 5 小时 in-home assessment：给定 codebase，在小模型上做 PyTorch 实验并回答 research questions（interview thread 1165094）。

**解法**: DNS resolver（我的推断）：实现递归/迭代解析+缓存 TTL+CNAME 链；prompts→servers 是 consistent hashing 风格路由题。5h 评估重点是实验设计和写作，不是代码量。

来源: <https://www.1point3acres.com/interview/thread/1177056>

### Coding Q3：debugging 题（非 LeetCode 风格）
*medium · 频率: medium (3+ reports) · 2026-02*

搜索摘要提及：'Coding Q3, with feedback that it focuses on debugging rather than LeetCode-style problems'——给一段有 bug 的代码/最少 helper code 的文件做 debug（Telegram 镜像也有 'Fresh Onsite Coding: File debugging with minimal helper code' 一条）。Q1/Q3/Q4/Q5 的提示词在 bbs thread 1138904 '人类学电面新提示词' 有分享（正文需登录），thread 1143701 分享了 Q2 和 Q6 的 prompt。收到新提示词求辨认的帖：bbs thread 1125221。

**解法**: debug 类轮的通用打法：先跑通复现→读测试→二分定位→修一个验一个并解释 root cause；Anthropic 喜欢看系统化 debug 过程而非直觉猜。

来源: <https://www.1point3acres.com/bbs/thread-1138904-1-1.html>

### Anthropic · Design Durable Function Call Cache（memoization 缓存键设计，companyFreq Anthropic=8, Onsite）
*hard · 频率: medium — Anthropic 频率标注 8/10（较新，Onsite） · 2026-06 首发，最近报告 2026-07-09*

题干：数据管线常用 memoization——包装昂贵函数使相同输入的重复调用返回缓存结果。给定部分实现的 FunctionCallCache 类（已处理缓存查找/插入/命中/未命中/LRU 淘汰），唯一缺失的是 create_cache_key，需为每次函数调用生成确定性、可哈希的键。子问：规范化 kwargs 顺序使等价调用产生相同键；序列化含嵌套结构的输入为可哈希格式。考点：DESIGN。Follow-up：如何处理不可 JSON 序列化的参数（如自定义类实例）？序列化字符串 vs 值元组作缓存键的权衡？如何扩展成基于函数签名或源码变化的缓存？访问缓存时的线程安全考量？

**解法**: 站内提示：kwargs 无关顺序，对 keys 排序得一致视图；对嵌套 dict 递归规范化以深度相等匹配；最终键=函数名 + 规范化 kwargs + args 组合成不可变容器或字符串。对 agentic/工具调用缓存场景很相关。

来源: <https://www.hack2hire.com/question-bank/companies/anthropic/coding-questions/6a2db6215117d1b543565e12/practice>

### String Tokenization (Trie, longest-match)
*medium · 频率: Anthropic freq 6/10, Google 4/10; last reported 2026-05-26 · 2025-12 (published), seen through 2026-05*

UNLOCKED - full statement captured. Stage: phone screen. Given `text` and `dictionary` of strings "<key>:<id>". Segment text into tokens: (1) Longest Match Priority - at each position pick the longest dictionary key matching there; (2) Greedy Consumption - consume the matched token, continue from next unconsumed char; (3) Literal Preservation - if nothing matches, emit the single char as a literal token; (4) Output the id for matched keys, the char itself otherwise. Constraints: 1<=text.length<=1e9, 0<=dictionary.length<=1e9, tokens unique. Examples: text="applepiepear", dict=["app:10","apple:20","pie:30"] -> ["20","30","p","e","a","r"]; "acdebe",["a:1","b:2","cd:3"]->["1","3","e","2","e"]; "programmingprogrampropro" with pro/program/programming/gram/ming/pr/og -> ["3","2","1","1"]. 8 official test cases captured incl. empty text, empty dict, "thetheatertheme". Site follow-ups: dictionary too large to fit / stored externally; fuzzy or partial matching; space optimization when keys share prefixes. Acceptance rate on site: 36.6%.

**解法**: Official editorial (captured): build a trie of keys storing id at terminal nodes; scan text left to right; from each position walk the trie as far as chars match, remembering the last terminal node passed (longest match); emit its id and jump pointer to bestEnd, else emit literal char and advance 1. O(N*L) time, O(S+N) space. Full Python/Java/C++/TS reference solutions captured (Python in /tmp/h2h_questions_full.json).

来源: <https://www.hack2hire.com/question-bank/companies/anthropic/coding-questions/6941b6aeb9d646bec48c68b7>

### Repair Bootloader Program (2 parts; AoC-2020-Day-8 style)
*hard · 频率: Anthropic freq 8/10; last reported 2026-07-09 (15h before crawl - very active) · 2026-06 (published)*

LOCKED (preview + per-part insights captured). Stages: Onsite + Screening. Instructions array of "<operation> <value>" with ops plus/next/jump: "plus x" adds x to accumulator then next instruction; "next x" no-op then next (x ignored); "jump x" moves to current index + x. Part 1 (q 6a373b356849fecc81442862): simulate from index 0, return the index of the first instruction that is about to execute a second time (first repeat), or -1 if the program terminates normally (falls off the end). Part 2 (q 6a373b366849fecc81442863): exactly one corrupted branch instruction may exist; flip at most one jump<->next so the program terminates; return the final accumulator after the minimal correction. Site follow-ups: conditional jumps; reduce space for cycle detection; out-of-bounds jump offsets; mapping to cycle detection in a functional graph; multiple flips; avoiding the reverse graph via forward simulation.

**解法**: Site hints (captured): Part 1 - visited boolean array/hash set, check repetition BEFORE executing, O(N). Part 2 - model instructions as directed graph; simulate original path and only consider flipping branch instructions on that path; precompute the set of nodes that can reach the terminal state by BFS/DFS on the REVERSE graph from the exit, then a flip is valid iff its new target is in that reach-exit set (O(1) validation, O(N) total). My note: this is essentially Advent of Code 2020 Day 8 (jmp/nop/acc) with renamed ops.

来源: <https://www.hack2hire.com/question-bank/companies/anthropic/coding-questions/6a373b2b6849fecc81442861>

### Design Durable Function Call Cache (2 parts: cache key + WAL crash recovery)
*hard · 频率: Anthropic freq 8/10; last reported 2026-07-09 (7h before crawl - very active) · 2026-06 (published)*

LOCKED (preview + insights captured). Stage: Onsite. You get a partially implemented Python `FunctionCallCache` class wrapping arbitrary functions with an LRU cache; lookup/insert/evict already written. Part 1 (q 6a2db7bc5117d1b543565e24): implement `create_cache_key` producing a deterministic, hashable key per call - must normalize kwargs order (sorted keys), recursively normalize nested dicts, combine function name + args + normalized kwargs into an immutable/hashable container or serialized string. Part 2 (q 6a2db7be5117d1b543565e25): durability - maintain an append-only log (WAL) of cache operations; on restart replay records sequentially to reconstruct both cached values AND LRU recency ordering; must gracefully skip trailing corrupted/truncated log entries without failing startup. Site follow-ups: non-JSON-serializable args (custom class instances); serialized-string vs tuple keys tradeoff; keying on function source/signature changes; thread safety; multi-process concurrent access; batched writes to cut disk I/O; checkpoint/secondary index to speed recovery; unbounded log growth (compaction).

**解法**: Site hints (captured): Part 1 - sort kwargs keys, recurse into nested dicts, emit tuple/canonical-JSON of (fn_name, args, sorted_kwargs). Part 2 - log individual key-value updates, not whole cache snapshots; during replay, delete-and-reinsert existing keys so LRU order reflects recency correctly; wrap parsing in try/except to skip malformed tail records. This is a very realistic 'engineering-flavored' Anthropic onsite question (matches their durable-cache/memoization take-home family).

来源: <https://www.hack2hire.com/question-bank/companies/anthropic/coding-questions/6a2db6215117d1b543565e12>

### Design Recipe Management System (4-level OA, CodeSignal industrial style)
*medium · 频率: Anthropic freq 7/10 (also Coinbase/HubSpot/Ramp); last reported 2026-07-07 · 2026-04 (published)*

LOCKED (preview + all 4 levels' insights captured). Stage: OA (online assessment). RecipeManager class; each recipe: unique name (case-insensitive), ordered ingredients, ordered steps. Level 1 (q ...694): addRecipe(name, ingredients, steps) -> "recipe<n>" sequential from 1, IDs never reused after deletion, "" if name exists case-insensitively; plus get/update/delete CRUD; updateRecipe must allow renaming to same name with different casing. Level 2 (q ...697): searchRecipesByIngredient with case-insensitive WHOLE-string ingredient match excluding deleted recipes; listing sorted by metric (count/name) with NATURAL NUMERIC ordering of recipe IDs (recipe2 < recipe10); tie-break by ID. Level 3 (q ...69a): addUser registration and editRecipe with ownership; enforce name uniqueness while permitting self-renames. Level 4 (q ...69b): immutable version snapshots on every update/edit; getVersionHistory sorted ascending by version; restoreVersion validating name collisions against other active recipes. Site follow-ups: inverted index for ingredient search; lazy vs eager delete; wildcard/partial matches; memory reduction for 10k+ versions; lock-free concurrent edits.

**解法**: Site hints: two hash maps (id->recipe, lowercased-name->id); extract integer suffix for natural ID ordering; deep-copy ingredients/steps per version snapshot (defensive copying); store versions as append-only list per recipe id.

来源: <https://www.hack2hire.com/question-bank/companies/anthropic/coding-questions/69f2664c42791c82ab992693>

### Design a Task Assignment System (4-level OA; sweep-line quota check at level 3)
*hard · 频率: Anthropic freq 7/10 (also Coinbase/HubSpot/Ramp) · 2026-04 (published)*

LOCKED (preview + all 4 levels' insights captured). Stage: OA. TaskManager class. Level 1 (q ...d74): addTask(timestamp,name,priority)->"taskId<n>" sequential from 1 (duplicate name+priority allowed); updateTask(timestamp,taskId,name,priority)->bool; getTask retrieval. Level 2 (q ...d75): searchTasks with case-sensitive substring matching, result limiting (empty filter = wildcard, non-positive limit = empty list); listTasksSorted by priority DESC then creation order ASC where creation order = NUMERIC comparison of taskId suffix (taskId1 < taskId10). Level 3 (q ...d76): user management with per-user quota of simultaneous active tasks; assignTask(user, task, [start,finish)) must validate interval overlaps and that the dynamic quota is never exceeded at any point in the window - requires sweep-line over interval boundary events, processing end events before start events at equal timestamps (half-open intervals). Level 4 (q ...d77): completeTask frees the user's quota; getOverdueAssignments = assignments whose finishTime <= query time and never completed; track completedAt to shorten active interval without deleting. Site follow-ups: interval tree/segment tree instead of linear scan; O(1) completeTask; thread safety; sparse/huge timestamps; DB schema for persistence.

**解法**: Site hints: quota check only needs critical moments at interval boundaries, not every time point - clip existing assignments to the new window, emit +1/-1 events, sort with end-before-start tie-break, sweep and track max concurrent count; per-user map keyed by taskId for O(1) completion.

来源: <https://www.hack2hire.com/question-bank/companies/anthropic/coding-questions/69efc8e696981f58ae1f6d73>

### Design Note-Taking System / SecondBrainSystem (4-level OA; backlinks, workspaces, versioning+merge)
*medium · 频率: Anthropic freq 7/10 (also Coinbase/HubSpot/Ramp); last reported 2026-05-12 · 2026-03 (published)*

LOCKED (preview + all 4 levels' insights captured). Stage: OA. In-memory SecondBrainSystem with CRUD notes, unique sequential IDs, case-insensitive unique titles, created/modified timestamps, pipe-delimited retrieval format. Level 1 (q ...4fe): CRUD + uniqueness + metadata; counter never decrements after deletes. Level 2 (q ...5de): resolve bidirectional [[title]] wiki-links - parse content line-by-line, a link counts only if the [[...]] stands ALONE on its own line; case-insensitive resolution against current titles; exclude self-references; return sorted results; links are resolved dynamically (renames/deletes change resolution). Level 3 (q ...5e6): workspaces with maximum capacity; notes tracked across workspaces plus a 'default' unassigned state (treat default as routing case, not a physical container); retrieval sorted by creation timestamp then note ID. Level 4 (q ...5f1): getNoteAt(id, timestamp) point-in-time historical state via immutable snapshots; mergeNotes(source,target) appends source content to target, redirects title-based links to target, safely removes source. Site follow-ups: persistence across restarts; hierarchical folders; thread-safety; caching/incremental updates for backlink queries at millions of notes; non-destructive branching/revert.

**解法**: Site hints: two hash maps (id->note, lowercase-title->id); snapshot-per-update list for time-travel queries; for merge link-redirection remap source's lowercase title to target's ID in the central index instead of rewriting note contents.

来源: <https://www.hack2hire.com/question-bank/companies/anthropic/coding-questions/69b351ffa4e93c007df404fd>

### Find Cluster Mode and Median (distributed algorithm design-coding, 2 parts)
*hard · 频率: Anthropic freq 10/10; last reported 2026-01-17 · 2025-12 (published)*

LOCKED (preview + insights captured). Stages: Screening + Onsite. Massive integer dataset partitioned across k workers (0..k-1), each worker only sees its own unsorted slice. Part 1 (q ...76a): distributed MODE (most frequent integer, ties -> smallest) such that no worker ever receives all raw data and network usage is minimized. Part 2 (q ...805): distributed MEDIAN under the same constraints, handling odd/even sizes. Site follow-ups: worker crashes/network timeouts; hash skew mitigation for hot values; extend to top-K frequent; async messaging effects on synchronization/termination; complexity vs sort-and-merge; k-th smallest generalization; skewed data distribution.

**解法**: Site hints (captured): Mode - each worker aggregates local (value,count) tuples first; shuffle by deterministic hash partition value->owner worker (no central collector); each owner sums its assigned counts, finds local leader; final reduction picks global winner with smallest-value tie-break. Median - binary search on the VALUE range: each round broadcast candidate, workers reply with counts of elements < and == candidate; combine ranks to steer the search; average two adjacent ranks for even n. This is effectively a mini MapReduce/binary-search-on-answer design question done as code.

来源: <https://www.hack2hire.com/question-bank/companies/anthropic/coding-questions/6935ba711553144e303f6769>

### Find Duplicate Files (LC 609 variant: binary streams, chunked hashing, 2 parts)
*hard · 频率: Anthropic freq 10/10; last reported 2026-06-29 (1 week before crawl) · 2025-12 (published)*

LOCKED (preview + insights captured). Stages: Screening + Onsite. Variation of LC 609. Find groups of duplicate files with identical BINARY content in a simulated file system rooted at "/". Names/paths don't matter; content only accessible as a binary stream (no direct string access); must be efficient over huge file counts. Part 1 (q ...8ba): recursive traversal, filter candidates by metadata (file size) before reading, group by cryptographic hash. Part 2 (q ...8be): very large files must be read in constrained CHUNKS under strict I/O and memory limits - incremental/running hash updated per chunk, group by size first, defer content reads until a size-bucket has >=2 candidates. Site follow-ups: distributed file system scaling; hash-collision false positives (byte-by-byte confirm); memory for millions of files; partially-similar/modified file detection; parallelization and its synchronization issues; complexity when chunk limit is tiny.

**解法**: Site hints: DFS/BFS to collect paths; size-bucket first (cheap metadata) -> only hash buckets with multiple files; streaming/incremental hash (e.g., hashlib update per chunk); optional first-chunk prefilter. This matches candidate reports of Anthropic's 'dedupe files with an API that reads bytes' interview.

来源: <https://www.hack2hire.com/question-bank/companies/anthropic/coding-questions/6934db5e5f306485cc5f08b9>

### Generate Function Profiling Events (LC 636 variant: stack-trace samples -> start/end events, 3 parts)
*hard · 频率: Anthropic freq 9/10; last reported ~2026-05-31 · 2025-12 (published)*

LOCKED (preview + all 3 parts' insights captured). Stage: Screening. A sampling profiler records entries "<time>:<stackTrace>" where time is strictly increasing int and stackTrace is "main->worker->parse" outermost-to-innermost; stack may be empty ("42:"). Part 1 (q ...225): convert consecutive samples into chronological function start/end events by diffing consecutive stacks - find first mismatch from outermost inward; frames removed after that point ended, frames added started; handle recursion (duplicate names at different depths are independent frames) and empty stacks. Part 2 (q ...228): debounced events - emit start/end only for call paths persisting >= n consecutive samples; reset counter when path vanishes; defer start event until streak reaches n; batch events per timestamp then order by stack depth (outer starts before inner; inner ends before outer). Part 3 (q ...229): suffix-based variant - generate all stack SUFFIXES per sample, track streaks per suffix with original first-seen timestamp, use longest matching suffix chain on transitions to separate newly-valid from expired paths. Site follow-ups: multiple threads; exclusive vs inclusive time; bounded-memory streaming; per-depth debounce thresholds; removing the per-sample sort for strict O(N); trie for suffix matching; out-of-order samples.

**解法**: Site hints captured per part (prefix-diff two-pointer for part 1; hashmap streak counters + depth-sorted event batching for part 2; suffix enumeration + longest-common-suffix transition for part 3).

来源: <https://www.hack2hire.com/question-bank/companies/anthropic/coding-questions/69308191cd79766b0b310224>

### Design Banking System (4-level OA/onsite; the classic CodeSignal banking series)
*medium · 频率: Anthropic freq 10/10 (also Coinbase/CapitalOne/HubSpot 10, Ramp 9); last reported 2026-05-18 · 2025-07 (published) - one of 4 posts hidden behind client-side pagination, recovered via API*

LOCKED (preview + all 4 levels' insights captured). Stages: OA + Onsite. BankingSystem class, all ops timestamped with increasing ints. Level 1 (q 687c3a5e...): createAccount(ts,accountId)->bool (false if exists); deposit(ts,accountId,amount)->new balance or -1; transfer with validations (existence, distinct IDs, sufficient funds) all checked before committing. Level 2 (q 687c4741...): topSpenders(n) - rank accounts by cumulative OUTGOING transaction totals desc, tie-break alphabetical ID asc, format top N; maintain running outgoing sums instead of recomputing. Level 3 (q 687c4e56...): pay(ts,accountId,amount) deducts and schedules 2% cashback credited exactly 24h (86400000ms) later; getPaymentStatus(ts,accountId,payment)-> IN_PROGRESS/CASHBACK_RECEIVED; cashbacks due at a timestamp must be applied BEFORE any other operation at that timestamp; rounding down on 2%. Level 4 (q 687c5c0b...): mergeAccounts(id1,id2) consolidating balances, transaction history and pending cashbacks; getBalance(ts,accountId,timeAt) historical balance queries incl. accounts merged away before query time; self-merge invalid. Site follow-ups: thread safety; audit logging; float precision for currency; scaling to millions of tx; atomicity; prefix-sum/indexed history for O(log n) historical queries.

**解法**: Site hints: hashmap accounts; event-sourcing style immutable per-account transaction log in chronological order enables both merge and time-travel getBalance (replay or prefix sums); process due cashbacks lazily at the start of every operation.

来源: <https://www.hack2hire.com/question-bank/companies/anthropic/coding-questions/687c23f9aa2b26b0b64b39d4>

### Design In-memory Database with Backup (4-level OA; TTL + timestamped versions + backup/restore)
*hard · 频率: Anthropic freq 9/10 (Coinbase/HubSpot 10, Ramp 9); last reported 2026-04-21 · 2025-08 (published) - hidden post recovered via API*

LOCKED (preview + all 4 levels' insights captured). Stage: OA. InMemoryDB storing records key->(field->value), all strings. Level 1 (q 689505e7...): setData(key,field,value) upsert; getData->"" if missing; deleteData->bool. Level 2 (q 68961c87...): scanData(key) returns all fields formatted "field(value)" lexicographically sorted; scanDataByPrefix(key,prefix) same but filtered by field prefix. Level 3 (q 689641c8...): timestamped variants setDataAt/getDataAt/scanDataAt with TTL support - field expires after specified duration; timestamps strictly increasing; legacy methods must keep working (backward compat); store per-field chronological version history and binary-search the valid state at query time; lazy expiration. Level 4 (q 689bb206...): backupDatabase(ts) captures only records alive at ts along with their REMAINING TTLs; restoreDatabase(ts, backupTs) restores newest backup <= backupTs and re-bases expirations relative to the restore timestamp (remaining lifespan preserved). Site follow-ups: concurrency; lazy vs background expiry; memory for full version history; non-monotonic timestamps; snapshot vs incremental diff tradeoffs; distributed/eventually-consistent variant.

**解法**: Site hints: nested dict key->field->list of (ts,value,ttl) versions; binary search for at-time reads; backup = filtered snapshot storing remaining-TTL; restore = fresh inserts with clock re-based at restore time. This is the well-known CodeSignal Industrial Coding Framework database question family.

来源: <https://www.hack2hire.com/question-bank/companies/anthropic/coding-questions/689505de3a1d9e6d6042d519>

### Cloud Storage System (4-level OA; files, prefix/suffix search, users+capacity, compression)
*hard · 频率: Anthropic freq 7/10 (Ramp 10, Coinbase/HubSpot 9, eBay 7); last reported 2026-03-08 · 2025-08 (published) - hidden post recovered via API*

LOCKED (preview + all 4 levels' insights captured). Stage: OA. Level 1 (q 689cf810...): addFile(name,size)->bool (fail if exists); copyFile(nameFrom,nameTo)->bool (source must exist and not be a directory, target must not exist); getFileSize(name)->size or -1; treat paths as opaque unique strings. Level 2 (q 689e4cd5...): findFile(prefix,suffix) returning "name(size)" entries where name starts with prefix AND ends with suffix, sorted size DESC then name ASC. Level 3 (q 689e4cd8...): multi-user - addUser(userId,capacity); per-user capacity limits with global file-name uniqueness; addFileBy(user,...) returns remaining capacity; admin has unlimited; updateCapacity(user,newCap) shrinks quota and auto-removes largest files (lexicographic tie-break) until fit, returning count removed. Level 4 (q 689e4cd9...): compressFile/decompressFile - compressed file takes size/2, gets naming-convention suffix (.COMPRESSED), ownership preserved, all capacity constraints validated atomically (compute net space delta first, no temporary overflow). Site follow-ups: hierarchical directories + recursive delete; concurrency/distribution; content dedup; billions of files; rollback for failed compression jobs.

**解法**: Site hints: hashmaps for file->size/owner, user->capacity, user->used; linear scan + custom comparator for findFile; sort-by-(size desc, name asc) removal loop for capacity shrink; strict precondition checks before any mutation for atomicity.

来源: <https://www.hack2hire.com/question-bank/companies/anthropic/coding-questions/689cf808aee746eb1c84ba37>

### Design Worker Management System (4-level OA; clock-in/out, top-N, promotions, double-pay intervals)
*medium · 频率: Anthropic freq 6/10 (Coinbase/HubSpot/Ramp 7); last reported 2026-03-16 · 2025-08 (published) - hidden post recovered via API*

LOCKED (preview + all 4 levels' insights captured). Stage: OA. Level 1 (q 68a4bbec...): addWorker(workerId,position,compensation)->"true"/"false" if exists; registerWorker(workerId,timestamp) toggles enter/leave (timestamps increasing) -> "registered"/"invalid_request"; get(workerId) -> total office time from COMPLETED sessions only, -1 if unknown worker. Level 2 (q 68a4bbf8...): topNWorkers(n,position) - filter by position, sort by accumulated time DESC then workerId ASC, formatted string output. Level 3 (q 68a4bbfa...): promote(workerId,newPosition,newCompensation,startTimestamp) - promotion is DEFERRED, activates only at the worker's NEXT office check-in after startTimestamp; calcSalary(workerId,startTs,endTs) sums compensation over completed sessions intersected with the query window, using the compensation rate in effect during each session. Level 4 (q 68a4bbfb...): setDoublePay(startTs,endTs) marks time ranges double-paid; overlapping periods must be consolidated (merged) and each minute double-counted at most once in salary calculations - intersect each session with merged double-pay periods and the query window. Site follow-ups: thread safety; non-monotonic timestamps; historical range reports; selection algorithm instead of full sort for top-N; sparse/huge timestamp ranges.

**解法**: Site hints: per-worker profile + nullable in-office-since timestamp; session list of (start,end,compensation); pending-promotion metadata applied at next check-in; keep double-pay intervals sorted+merged on insert, then interval-intersection arithmetic for salary.

来源: <https://www.hack2hire.com/question-bank/companies/anthropic/coding-questions/68a4bbdfc11d63d6052ea306>

### Live 技术 screen 真题：call stack 采样 → execution trace 转换
*medium · 频率: 2 个独立报告 · 2026-01*

两个独立第一人称报告的同一题：(1) Exponent 上 Safeguards Senior SWE（约 2025 年末-2026 年初）：Technical Interview 1 为 "Transform call stacks or samples into execution traces"，非 LeetCode，像处理 profiling-style data；(2) Andrey Zharkov（2025，RE 轨道）列出的被问题目中有 "Convert call stack trace from one format to another (sampling profiler)"。即给定采样式 profiler 的输出（每个时刻的调用栈快照），转换为进入/退出事件流或调用树/火焰图聚合格式。Zharkov 在 Anthropic 的 live 技术 screen 挂掉（自称当周工作 80h 太累），说明该轮虽不算难但要求扎实执行。

**解法**: （我的推断）对相邻两个采样栈求最长公共前缀：公共前缀之上的旧帧依次产生 exit 事件（逆序），新帧依次产生 enter 事件（正序）；聚合成树时按 (depth, frame) 累计样本数即得火焰图。注意首末样本的边界、递归同名帧要按位置而非名字匹配。

来源: <https://www.tryexponent.com/experiences/anthropic-senior-software-engineer-interview-2ffa5f>

### Onsite coding 真题：LRU cache 分层加需求（持久化/序列化）
*medium · 频率: 3+ 报告（含变体） · 2026-01*

Exponent Safeguards SWE 面经：Technical Interview 2 为 LRU cache 实现，随后 layered complexity additions——加文件处理（file handling）和序列化 tradeoffs 讨论。jobright 聚合亦记录变体 "Implement an LRU Cache. Now, how would you make it persistent?"（讨论 JSON vs pickle 等 tradeoff）。leonstaff 记录另一变体：build LRU Cache, then make it concurrent（线程安全）。这与 Anthropic 'build from scratch + 渐进加需求' 的 coding 风格一致：先正确实现，再层层加约束并讨论取舍。

**解法**: OrderedDict 或 dict+双向链表标准实现；持久化讨论点：全量 snapshot vs append-only log（WAL）、序列化格式取舍（pickle 快但不安全/不跨语言，JSON 安全但类型受限）、崩溃一致性；并发版：单锁先行，再谈分段锁/读写锁与 LRU 顺序维护的冲突。（我的推断）

来源: <https://www.tryexponent.com/experiences/anthropic-senior-software-engineer-interview-2ffa5f>

### 其他被报告的 live coding 题：rate limiter、流式数据处理、sequence packing
*medium · 频率: 各 1-3 个报告 · 2025*

聚合与第一人称混合来源：(1) Rate limiter：实现 rate limiter，follow-up 依次为并发安全（为 tool-calling agent 的 API 设计线程安全限流器）、多机部署、sliding window、降载策略；(2) 实时流数据处理：去重、排名、聚合、故障检测；(3) Zharkov 被问过（跨公司列表中，很可能即 Anthropic RE 轨道）："Implement sequence packing for LLM training"——list[list[int]]（变长序列）→ 打包成每条不超过 max_length 的 list[list[int]]，要求 'as optimal as you can'；(4) 其他被多个聚合站提到：tokenization 引擎（文本流+缓冲）、duplicate file finder（哈希+文件系统遍历）、log processing、图遍历。Glassdoor 摘要将 Anthropic coding 总结为 'software development assignment with a bit of leetcode baked in'。

**解法**: sequence packing：本质是 bin packing（NP-hard），面试期望 first-fit decreasing 贪心（按长度降序，放入第一个能容纳的 bin），讨论与最优解差距和 O(n log n) 实现（用有序结构找剩余容量）；rate limiter：token bucket 单机 + Redis/一致性哈希分布式 + sliding window log vs counter 的内存/精度 tradeoff。（我的推断）

来源: <https://reyzharkov.com/blog/posts/interviews-2025-ml-research-engineer-uk>

### Performance Engineering take-home（官方已开源，含全部规格）
*hard · 频率: 官方（1000+ 候选人经历过此轮） · 2026-01*

Anthropic 性能团队 2024 年起使用、2026 年 1 月开源的 take-home（1000+ 候选人做过，直接促成数十人入职；由 Tristan Hume 团队设计）。任务：优化运行在模拟加速器（类 TPU）上的 kernel，最小化时钟周期。机器模型：单核 VLIW SIMD 处理器，每周期槽位：ALU×12（标量）、VALU×6（8 宽向量）、LOAD×2、STORE×2、FLOW×1；手动管理的 scratchpad 1536 words；瓶颈是每周期仅 2 load + 2 store。Kernel：batched tree traversal（决策树推理启发）——深度 10 的完美二叉树（2047 节点）、batch 256、16 轮遍历共 4096 步；每步：读 index/value → 取树节点值 → hash(value XOR node)（6 段 hash，约 18 个 ALU 操作，类 Bob Jenkins）→ next = 2*idx+1/2（奇偶分支）→ 越界回绕。原版 4 小时（baseline 147,734 cycles）；2 小时版 starter 18,532 cycles。分数参照：Opus 4 长时间 2,164；Opus 4.5 两小时 1,579；Opus 4.5 最好 1,487 = '打过它就发邮件 performance-recruiting@anthropic.com（附代码+简历）'的招聘线。此 take-home 明确允许用 AI 工具（官方 candidate 政策的例外）。开源后警告：第一天收到的所有 <1300 cycles 提交全是模型改测试作弊；提交前必须 git diff origin/main tests/ 证明测试未改、跑 tests/submission_tests.py。因 Claude 表现超过人类，真实招聘已换到 V3 版本：Zachtronics 风格、极小受限指令集的约束优化谜题（Claude 尚不擅长）。

**解法**: 优化路线（trirpi.github.io 深度拆解）：SIMD 向量化（8 items/op）→ VLIW 打包（跨引擎塞满每 cycle）→ software pipelining（跨迭代重叠隐藏依赖链）→ branchless（select 替代跳转）→ 跨 batch item 并行掩盖单条遍历的串行 hash 链；load/store 带宽是最终瓶颈，把 tree 热点层预载进 scratchpad。深拆见 https://trirpi.github.io/posts/anthropic-performance-takehome/ 与 Anthropic 官方设计博客。

来源: <https://github.com/anthropics/original_performance_takehome>

### 公开版 performance take-home 的社区解题记录（供练习对标）
*hard · 频率: 公开挑战（多篇解题记录） · 2026*

两篇公开解题记录可作练习材料：(1) trirpi.github.io 'Deep Dive: Anthropic's Performance Take-Home (The One Claude Beat Humans At)'——完整拆解机器模型（ALU×12/VALU×6/LOAD×2/STORE×2/FLOW×1、scratch 1536 words、8 宽向量）、kernel（深度 10 树、batch 256、16 轮、6 段 hash）与五步优化法（VLIW packing、SIMD、software pipelining、branchless select、跨 item 并行）；(2) matthewtejo.substack.com 'Taking on Anthropic's Public Performance Engineering Interview Challenge' 与 (3) medium.com/@indosambhav 的挑战记录。这是 2026 年 7 月准备 Anthropic 性能向岗位（或想走 performance-recruiting 邮箱内推通道）最直接的实战训练集：目标把 starter 18,532 cycles 压到 <1,487。

**解法**: 练习顺序建议：先只做向量化拿 10x，再学着读 watch_trace.html 找每 cycle 空槽，最后做 software pipelining；对照仓库 tests/submission_tests.py 验证，不要动 tests/ 目录。

来源: <https://trirpi.github.io/posts/anthropic-performance-takehome/>

### Anthropic Fellows/MATS 新版 OA 真题细节：一致性哈希 + 请求路由到虚拟节点 + RAM/GPU 显存驱逐
*hard · 频率: multiple (5+ reports in thread) · 2026-01*

r/Anthropic 帖（2026-01，评论持续到 2026-05）：Fellows Program（AI Safety Research）OA 已从 CodeSignal ICA 换成自研更难版本。一位考生透露被问：consistent hashing、chat request 路由到 virtual nodes、基于 RAM/GPU memory 的 eviction（缓存驱逐）。2026-07 cohort 邀请函明确写 6 parts 且提到 concurrency（asyncio/threading）。仍是渐进式 system-building（类似 banking system 但'题面像论述题'）。流程：OA1 → OA2 → references（3封，会真联系）→ take-home → 面试。旧版 cut line 480/600。

**解法**: 练：实现 consistent hash ring（虚拟节点、增删节点时的 key 迁移）、LRU/加权容量驱逐（按内存占用而非条目数）、asyncio 生产者-消费者。我的推断：这是模拟 LLM 推理集群的 KV-cache/模型分片路由场景，把三者组合成一个渐进题。

来源: <https://www.reddit.com/r/Anthropic/comments/1qovmbs/assessment_for_anthropic_fellows_program_for_ai/>

### Anthropic L4 SWE onsite 编码轮题目清单（2025 offer 面经）：线程安全缓存/流式 tokenizer 性能 debug/并发预订系统
*hard · 频率: single detailed report (corroborated by 4+ partial reports) · 2026-05*

InterviewCoderHQ 详细 offer 面经（L4 remote，6 YoE backend）：技术店面=用 ThreadPoolExecutor 构建 async 处理管线、处理并发安全、debug 性能瓶颈（55-90分钟）。onsite 编码轮三题型：(1) build a thread-safe cache with configurable eviction policy；(2) debug a performance bottleneck in a streaming tokenization system；(3) design and implement a reservation service with concurrency constraints。共同主题：multithreading、async processing、API design、streaming、pipeline debugging。评分看代码可读性、并发正确性、架构决策、debug 方法论，而非时间复杂度。作者称没刷 LeetCode 是正确选择，备考 6 周聚焦 Python 并发原语 + 生产级代码（错误处理/日志）。注：该 sub 由面试辅导产品运营，细节与多个独立报告吻合但属二手整理。

**解法**: 线程安全缓存：dict + OrderedDict/heap 驱逐 + RLock，讨论锁粒度和 read-heavy 优化；预订系统：per-resource lock 或乐观并发 + 幂等；tokenizer debug：找 GIL 争用/重复分配/无缓冲 IO。

来源: <https://www.reddit.com/r/InterviewCoderHQ/comments/1tirugm/anthropic_swe_interview_experience_2025_l4_remote/>

### Anthropic SWE 技术店面结构（2025-01 一手，帖子已删但 pullpush 存档到正文）：30min code review+debugging + 30min coding
*medium · 频率: single report (structure corroborated later) · 2025-01*

r/leetcode 2025-01 帖（原帖已删除，selftext 经 pullpush 存档恢复）：SWE 岗流程=CodeSignal OA→recruiter call（含薪酬说明）→1小时技术店面：前 30 分钟 code review 和 debug 已有代码，后 30 分钟 coding。recruiter 明确说'不强调高级算法和数据结构，熟悉所选语言和标准库即可，不是 leetcode'。评论区印证当期其他人报告的是 concurrency/multiprocess 题。这是 code-review-as-interview 形式的最早报告之一，与 2026 年'debug 或扩展已有代码'的报告连续。

**解法**: 练 code review：找并发 bug（race、死锁）、资源泄漏、错误处理缺失、边界条件；练口头表达 review 意见的礼貌与优先级。

来源: <https://www.reddit.com/r/leetcode/comments/1ibskkp/anthropic_tech_screening_what_to_expect_in_the/>

## ML Coding 题

### Agent Coding 轮：用 Claude API 搭 agent loop（tool use 答股票价格问题）
*medium · 频率: high (4+ reports, 2026 Q2 上升) · 2026-05*

SWE/RE 技术店面 track 之一：'写代码把 LLM 当 building block'，实现 Claude agent loop——定义 tools、解析模型 tool call、执行并回传结果、循环到回答完成。Telegram 镜像具体版本：'Claude agent loop，用 tools 回答关于股票价格的问题'。相关帖：interview thread 1178346 'Technical Phone Screen: LLM Agent Coding Interview'（2026-05）、bbs thread 1172086 '人类学Anthropic求助 Agent Interview题目'（Agents Interview 测试 writing code with LLMs as a building block + prompting to create an agent）、interview thread 1141199 'RE Interview: Agent Coding and Coding Design Topics'。

**解法**: 熟练手写 Anthropic messages API 的 tool use 协议：tools schema、stop_reason=='tool_use' 分支、tool_result 回传、while 循环+最大步数保护、错误处理（tool 抛异常回传 error 让模型重试）；准备讨论 prompt 设计、防幻觉（强制引用 tool 结果）、并行 tool call。

来源: <https://www.1point3acres.com/interview/thread/1178346>

### RL Fundamentals 轮：debug GRPO training loop + 解释 ratio ≠ 1（RE 高频新题）
*hard · 频率: medium (3+ reports, 2026 Q2 新增) · 2026-05*

给一份简化的 GRPO（on-policy RLHF）训练 step 实现，含 3 个埋好的 bug，常见 bug 类型：log-prob 计算错误（未对齐 autoregressive shift）、loss/KL 里 token masking 错误、advantage normalization 错误（组内奖励全相同时除零/无信号）、新旧 policy 混用（rollout 与 update 的 policy 不一致）。每个 bug 要求给出检测方法+具体修复，不能只点名。核心追问：明明设计上严格 on-policy，为什么 importance ratio = exp(log πθ − log π_old) 不等于 1？要求设计判别实验区分'设计内偏差'（推理引擎与训练器 forward 路径不同、bf16/fp32 数值精度、每个 rollout batch 走多次 optimizer step）与真 bug。Follow-up：clipped surrogate 如何防崩、组内奖励全相同怎么办、engine-to-trainer log-prob 修正、process vs outcome supervision、KL penalty 放 reward 里还是 loss 里的 trade-off。应主动澄清：reward 类型、每 batch optimizer 步数、生成与打分是否同一 forward 路径、采样温度/top-p、KL 实现、数值精度。1p3a 对应帖：interview thread 1167043 'RL Fundamental Interview: Code, Design, and Configuration'、1166898、bbs thread 1167940。

**解法**: prachub 页面给了完整评分维度（见 detail）。ratio≠1 三大合法原因：多次 minibatch update 后 πθ 已漂移、vLLM 采样与 HF 训练 forward 的 kernel/精度差异、bf16 舍入；判别实验：同一 checkpoint 用训练器重算生成 log-prob 对比、fp32 复算、第一次 optimizer step 前检查 ratio 是否恰为 1。

来源: <https://prachub.com/interview-questions/debug-a-grpo-training-loop-and-explain-ratios>

### Coding & Design：Weighted Data Batcher with Checkpointing（research track，MLE/RE 向）
*hard · 频率: medium (2026-05 last asked) · 2026-05*

55 min，research-track 1-of-N coding-and-design 题，难度标 hard。构建 DataBatcher：从 DataRegistry 按权重采样生成 batch，要求确定性的 save/resume——用 offset 参数实现 checkpoint 后精确恢复采样流。标签：sampling/checkpointing/iterator/Python/MLE。Last asked 2026-05，frequency: Medium。与候选人 mid-training 数据管线背景高度相关。相关：interview thread 1162037 'Onsite Coding and Design Interview for Machine Learning Role'。

**解法**: 我的推断：seeded RNG + 可序列化状态（rng state + per-source offset/epoch 计数）；确定性恢复的关键是把随机流做成 offset 可重放（如 counter-based RNG 或 rng.getstate/setstate）；讨论加权采样（别名法 vs 前缀和二分）、数据源动态增删对确定性的影响、多 worker 分片。

来源: <https://www.1point3acres.com/interview/problems/company/anthropic/coding-design-data-batcher>

### Prompting & Engineering with LLMs 轮（55 min Colab）
*medium · 频率: medium (3+ reports) · 2026-02*

55 分钟 Google Meet，在 Colab 里做 prompting and engineering with LLMs：用 prompt 工程解决任务（评估/迭代 prompt、处理模型输出）。是 RE/RS 和 MLE 店面四选一 track 之一。一位 MLE 候选人路径：OA（Recipe 题）→ 55-min 'Prompting and Engineering with LLMs' 店面。interview thread 1147266 'Anthropic Interview Experience: 55-Minute Google Meet Coding Challenge on LLM Prompting'。

**解法**: 我的推断：典型形态是给一个分类/抽取任务和小数据集，要求写 prompt+评估 loop，迭代提升准确率；准备结构化输出解析、few-shot 选择、失败案例分析话术。

来源: <https://www.1point3acres.com/interview/thread/1147266>

### Take-home 汇总：RS 4 小时作业；Accelerator 团队 4 小时多核模拟器（performance 向）
*hard · 频率: medium (3 reports) · 2026-01*

(1) RS（Research Scientist）take-home assignment：4 小时，非 OA 形式（bbs thread 1103094 '请问Anthropic的take home assignment'）。(2) Accelerator/performance 团队 take-home：4 小时，Python multi-core simulator（多核处理器模拟器），发帖人建议提前复习 VLIW 和 pointer 概念（bbs thread 1135727 'Anthropic 挂经'）。(3) 题库'Other'类还有 interpretability / ML experiments / GPU performance analysis 类 take-home（题库页可见分类，正文需登录）。

**解法**: 多核模拟器（我的推断）：实现指令级模拟（VLIW bundle 并行发射、内存/指针语义、核间同步），先写单核正确版本再扩展；时间盒 4 小时，优先正确性+清晰 README。

来源: <https://www.1point3acres.com/bbs/thread-1135727-1-1.html>

### RE/MLE 轨道 ML 轮主题（聚合来源，置信度中等）
*hard · 频率: 聚合站信息（部分与 Glassdoor 碎片交叉） · 2026*

多个聚合指南（finalroundai/jobright/linkjob 等，非第一人称，作交叉参考）：RE 轨道 = SWE 流程 + ML 深挖轮，coding OA 与 SWE 相同（题目领域会提前邮件告知）。ML 轮内容：从零实现 Transformer 组件（multi-head attention）、BPE、采样（sampling）；调试损坏的训练代码；手推梯度；MoE/Mamba/attention 变体的数学推导；scaling laws 与小规模实验外推大模型性能的讨论。ML 理论样题："Explain the architecture of a Transformer model"、"How would you optimize a model for inference latency?"（量化/蒸馏/硬件加速）、"Design a distributed training pipeline for a LLM. How would you handle fault tolerance?"。Research Scientist 轨道额外：research presentation（30-45min 报告 + 30min Q&A，深挖假设/方法/局限）、48 小时 take-home（问题集或小数据集，评审重 reasoning 过程——写清试了什么、为何失败、有更多时间会做什么，胜过干净但缺推理的报告）。Glassdoor 碎片：有候选人收到 QKV attention 预习材料但面试官问的是 attention-free transformers。

**解法**: 对 post-training 背景：把 attention/BPE/采样三件套练到 20 分钟内裸写无 bug；准备一个 45 分钟版本的自己代表作 research talk，预演'假设-证据-局限-下一步'追问。

来源: <https://www.finalroundai.com/blog/anthropic-interview-process>

## ML 理论

### ML Configuration System 轮（RE/MLE 店面 track，2026 新）
*unknown · 频率: medium (3+ 求经帖, 2026-05/06) · 2026-06*

四选一 track 之一，2026 年 5-6 月多帖求经/组队但正文均在登录墙内：interview thread 1164302 'ML Configuration System Tech Phone Screen'（含店面后 HR call 和 onsite 流程说明）、1166993 'ML Configuration System Interview Experience Exchange'、1166655。已知只有题目家族名'ML Configuration System'——实现/设计管理 ML 实验配置的系统。

**解法**: 我的推断（基于题名+同类公司考法）：实现 config 系统支持嵌套配置、默认值+覆盖合并、类型/约束验证、实验 sweep（笛卡尔积展开）、序列化与 reproducibility；用 Python dataclass/dict merge 实现，重点在 API 设计和 edge case（冲突、循环引用、deep merge 语义）。

来源: <https://www.1point3acres.com/interview/thread/1164302>

### ML Fundamentals 轮（MLE/RE）：transformer attention 等基础
*medium · 频率: medium · 2026-01*

interview thread 1127361 'Machine Learning Fundamentals Interview Experience and Preparation Tips'（正文需登录）。题库 member-only coding 题标签中包含 'transformer attention'、'reinforcement learning'、'performance optimization'，说明 ML fundamentals/ML coding 轮会考 attention 实现类题。结合 RL fundamentals 轮（GRPO debug）判断：RE loop 的 ML 轮在 attention 实现 / RL 训练 debug / ML config 之间取样。

**解法**: 手写 multi-head attention（含 mask、KV cache 版本）+ 能解释 GRPO/PPO/DPO 细节，覆盖此轮绝大部分考法（我的推断，与候选人背景匹配度高）。

来源: <https://www.1point3acres.com/interview/thread/1127361>

### Research brainstorm 轮样题（AI Safety Fellow，verbatim）
*hard · 频率: 官方轨道固定轮次（指南级来源） · 2026*

Exponent 的 Anthropic AI Safety Fellow 指南给出该 15 分钟 research brainstorm（附在 55 分钟 Prompting & LLM Engineering 轮之后）的 alignment 方向样题："How would you prevent bad actors from misaligning an LLM?"；"How would you detect misalignment?"；"How would you train models to be more robustly aligned?"。考察实时研究 ideation：提出可操作的实验/评测/训练方案，而非背诵文献。

**解法**: （我的推断）回答框架：威胁建模（谁、什么能力、什么入口：微调 API/数据投毒/越狱）→ 检测（行为评测集、激活探针/linear probe、一致性测试、红队自动化）→ 训练（对抗训练、RLHF+过程监督、unlearning、水印/审计）。每个方向给出一个可以两周内跑出的最小实验设计。

来源: <https://www.tryexponent.com/guides/anthropic-ai-safety-fellow-interview>

## System Design

### System Design：Prompt Playground（onsite 高频）
*medium · 频率: high (5+ reports) · 2026-04*

设计一个类 ChatGPT Playground / Anthropic Console 的 prompt 工程平台。1p3a 题解页结构：需求定义→规模成本估算→API 定义→DB schema→架构总览→组件深挖→性能问题修复→方案对比（正文需登录）。多个 onsite 报告：SWE onsite 'Prompt Playground + Coding Q6' 组合（interview thread 1152158）；Telegram 镜像两例：一人 VO 四轮之一考 Prompt Playground，另一人店面挂在 image processing system design + Prompt Playground。

**解法**: 考点（我的推断）：prompt 版本管理与 diff、多模型/多参数并行试验、流式 SSE 输出、API key 与配额、prompt/completion 存储 schema（含大文本）、评估集与 A/B、成本追踪；性能部分常问长 prompt 渲染与缓存。HelloInterview 有公开同题讨论：https://www.hellointerview.com/community/questions/prompt-playground/cmjd4xmkg04nf08adwd3m0bvs

来源: <https://www.1point3acres.com/interview/problems/post/7100017>

### System Design Q5：Data Infrastructure（数据平台题，与候选人数据管线背景对口）
*medium · 频率: single report · 2026-03*

55 min，medium 难度，单一报告，last asked 2026-03-07。题面（公开部分）：设计一个系统，ingest 大规模数据、处理后 serve 给多个 stakeholder，各方 access needs 和数据敏感度不同。标签：data-engineering/ingestion/ETL/access-control。Roles: SWE/DS/Infra。完整题面需登录。

**解法**: 我的推断：分层 lake/warehouse 架构（raw→cleaned→curated）、批流双路 ingest、schema registry、行/列级 ACL 与 PII 脱敏、audit log、数据血缘；对 Anthropic 场景可映射到训练数据管线+安全分级。

来源: <https://www.1point3acres.com/interview/problems/company/anthropic/sd-q5-data-infrastructure>

### 其他 onsite 设计/分析题：image processing system design、dataset analysis (cloud capacity)、Bootloader 新 coding 题
*unknown · 频率: single reports each · 2026-05*

Telegram 镜像（1p3a 转载）三条 2026 onsite 新信息：(1) 店面/onsite 设计轮考 image processing system design（一人挂在此轮）；(2) onsite 有 dataset analysis 轮：给云容量管理（cloud capacity management）数据集做分析，配合 'why Anthropic' 和 project presentation；(3) VO coding 出现新题 'Bootloader'（与 Prompt Playground SD、project deep dive、culture 同一 loop）。

**解法**: dataset analysis 轮类似 take-home 现场版：EDA→假设→容量预测/异常检测→建议，重讲清 reasoning。Bootloader 题无公开细节（我的推断：实现分阶段加载/依赖解析的模拟器类题）。

来源: <https://t.me/s/usinterview?q=%23anthropic>

### System Design: Slack-like Chat System (DMs to 100K-member channels)
*hard · 频率: Anthropic freq 7/10 (shared: OpenAI 9, Snapchat 10, Meta 9, +9 more companies); last reported 2026-07-09 · 2026-03 (published)*

LOCKED (long preview captured). Stage: Onsite. Core messaging layer: DMs and group channels from 2 to 100K members. Preview clarifying Q&A gives the constraints: both small and announcement-scale channels in scope; delivery latency budgets differ - <=200ms for small conversations, <=500ms for large channels; central tension is eager per-member push for small channels vs pull/fan-out-on-read for huge channels (channel size becomes a first-class input to delivery strategy). Full solution paywalled.

**解法**: My inference: hybrid fan-out - write-time fan-out to per-user inboxes/connections below a membership threshold; read-time pull + lightweight 'channel updated' signal above it; per-channel message log (ordered, partitioned by channel id) as source of truth; WebSocket gateway layer with connection registry; unread counts via async counters; follow-ups usually cover ordering, presence, typing indicators, and hot-channel partitioning.

来源: <https://www.hack2hire.com/question-bank/companies/anthropic/system-design/69c9fe5dff3ebde766ced6f4>

### System Design: Facebook Messenger (durable ordered history + realtime layers)
*medium · 频率: Anthropic freq 4/10 (Uber/Meta 7, Google/Microsoft 6); last reported 2026-07-08 · 2026-04 (published)*

LOCKED (long preview captured). Stage: Onsite. 1:1 and small-group realtime chat across devices. Preview clarifying Q&A pins scope: groups capped ~250 members (personal communication, not broadcast - keeps synchronous-path fan-out manageable); new group members can read FULL prior history by default (membership semantics = full shared history); durable ordered conversation history is the single source of truth, while presence/read-receipts/notifications are fast lossy layers around it. Full solution paywalled.

**解法**: My inference: per-conversation ordered log with server-assigned sequence numbers; multi-device sync via per-device cursors; push notifications + WebSocket delivery as best-effort layers reconciled against the durable log on reconnect; small-group fan-out done synchronously on send path; idempotent sends with client message ids.

来源: <https://www.hack2hire.com/question-bank/companies/anthropic/system-design/69d2bf7307421ca06eb8e38c>

### Anthropic classic-infra system design set: P2P file distribution, file cache, KV store, web crawler
*medium · 频率: multiple reports each · 2026-01*

Reported Anthropic onsite/phone-screen questions: (1) Peer-to-peer file distribution — distribute a large file to thousands of bandwidth-constrained machines; core tension: sequential transfers maximize per-transfer speed but force waiting vs simultaneous distribution splitting bandwidth (BitTorrent-style chunking is the expected insight). (2) File cache system — caching strategies, eviction, consistency. (3) Key-value store — storage engines, replication, partitioning, consistency models. (4) Web crawler — follow-ups on multi-threading, deduplication, crawl politeness. Guidance: 'abstract AI terminology immediately'; toolkit patterns = queuing, batching, consistent hashing, P2P distribution; address failure modes automatically for every component. Problems are often novel with no predetermined optimal solution.

**解法**: P2P: chunk the file, tree/swarm topology so each recipient becomes a seeder — total time O(log N) rounds instead of O(N); discuss rarest-first chunk selection and stragglers.

来源: <https://www.tryexponent.com/blog/anthropic-system-design-interview>

### System design 真题：1B 文档 1M QPS 分布式搜索系统
*hard · 频率: single report（主题目）；变体各 1 报告 · 2025*

Medium 上 2025 年 SWE 候选人面经：system design 轮为设计 distributed search system，规格 1B documents、1M QPS，需要处理 sharding、caching、LLM inference scaling；面试官重点追问避免 hotspot 和 GPU 显存优化。其他被报告的 system design 题（jobright 聚合）：分布式 job queue（类 Kafka + workers）、"Implement a GPU Scheduling System Using Credits"（抢占逻辑、防资源垄断、容错）、"Design a 1-on-1 Chat System"（SQL vs Cassandra、离线投递、消息顺序、WebSocket 扩展）、为开发者设计访问 Anthropic 模型的 API。

**解法**: 倒排索引分片（doc-sharding）+ 多副本读扩展；两层缓存（query result cache + posting list cache）；热 term 用 replication+随机路由避免 hotspot；若含语义检索：ANN 索引（HNSW/IVF）分片 + embedding 服务批量化；GPU 显存：embedding 模型量化、动态 batching。（我的推断）

来源: <https://medium.com/@anqi.silvia/my-2025-anthropic-software-engineer-interview-experience-9fc15cd81a99>

### Anthropic Staff/Sr Staff Infra onsite 系统设计真题 1：Model Downloader（模型分发）
*hard · 频率: 2 reports (Jun 2026) · 2026-06*

两份 2026-06/07 onsite 面经（同一候选人两处发帖+社区确认为常考题）：设计把大模型权重分发到大量机器的 Model Downloader。考生用 chunk-based pipeline 设计；讨论了 chunk size 如何影响 pipeline 式 vs tree 式分发的差异；先用 coordinator 分配 chunk 和做恢复，follow-up：没有 coordinator 时如何恢复（去中心化）。该轮被认为通过。这是 Anthropic 真实基础设施场景（把 checkpoint 快速分发到推理/训练集群）。

**解法**: 类 BitTorrent/HDFS 混合：源分 chunk + 校验和，节点间 P2P 传播（tree 减少源带宽，pipeline 利用全双工），无 coordinator 用 gossip + 一致性哈希决定 chunk 归属 + 本地清单对账拉取缺失 chunk。讨论小 chunk=更好流水线但元数据开销大。

来源: <https://www.reddit.com/r/OfferEngineering/comments/1udgir6/anthropic_sr_staff_infra_swe_onsite_model/>

### Anthropic 近期系统设计题库汇总（辅导教练整理）：Claude chat service、分布式/混合搜索、p95 延迟排查、1B 文档爬虫管线
*hard · 频率: aggregated from multiple loops (coach-reported) · 2026-03*

InterviewCoderHQ 'Targeting Anthropic' 帖（drCounterIntuitive，面试教练，2026-03）汇总近期 loop 真题：(1) Design a Claude chat service；(2) Design a distributed search system；(3) Design a hybrid search system（关键词+向量）；(4) Debug performance degradation：p95 延迟从 100ms 飙到 2000ms，如何排查、建监控、排序修复优先级；(5) Design data pipeline with concurrent web crawler for ~1B documents。风格提醒：interviewer-driven、time-box、中途 pivot，可能不让你按'需求→估算→API→高层→深挖'模板走；另确认 reference check 可能在流程走完前就开始；并发题常态化；表现好也可能不发 offer（决策不透明）。senior 还有 technical presentation 轮（讲自己项目）。

**解法**: p95 排查题按层讲：先定位（USE/RED 指标、tracing 分段）→常见根因（GC/连接池耗尽/热分区/缓存击穿/重试风暴）→监控（p50/p95/p99 分位 + burn-rate 告警）→修复排序按影响面。

来源: <https://www.reddit.com/r/InterviewCoderHQ/comments/1rxinyi/targeting_anthropic_insights_from_recent/>

## ML System Design

### System Design Q1：LLM Inference Batch API（题库最高频 SD 题）
*hard · 频率: very high (16+ 讨论) · 2026-06*

55 min，'Very High' 频率，16+ 关联讨论，标签 llm-inference/batching/kv-cache/gpu。题面（公开部分）：设计一个 HTTP API，对外暴露 LLM 推理的 batch 处理功能。1p3a 题解页结构：The Challenge → 需求澄清 → 规模/资源估算 → API 设计 → 数据存储 → 基础架构 → 组件深挖 → 修复潜在问题（正文需登录）。SD Q3 也是 inference API 主题，有帖专门对比 Q1 vs Q3（interview thread 1158532）；另有 SD Q4 求助帖（thread 1169228、1163059）。变种：'API batch string function combining API requests for LLM APIs'（infra SDE 设计轮，bbs thread 1123616 区域）。

**解法**: 核心考点（我的推断+行业标准答案）：continuous batching（Orca 式 iteration-level scheduling）、KV cache 管理/PagedAttention、prefill vs decode 分离、排队与 SLA（p99 TTFT/TPOT）、prefix caching、backpressure 与 rate limit、GPU 池扩缩容 vs 冷启动、幂等重试与结果存储（batch job 异步 API：提交→轮询/webhook）。

来源: <https://www.1point3acres.com/interview/problems/post/7100012>

### Design a GPU inference batching system (Anthropic's most-reported system design question)
*medium · 频率: very high (called 'most commonly reported' Anthropic SD question) · 2026-01*

Prompt: 'You have a single GPU that can process up to 100 inputs per batch. Users submit requests synchronously and wait for results. Design the system that receives inputs, batches them, processes them on the GPU, and returns responses to the correct users.' Extension version: end-to-end LLM query batching — request intake, batching policy, GPU routing, load balancing, response delivery. Follow-ups: how do you determine GPU capacity; failover handling; what happens when a batch member fails; queueing vs latency trade-off. Asked in the 50-55 min phone screen and/or onsite (4-5 rounds, 45-55 min each). Exponent notes Anthropic questions 'use AI framing but test classic distributed systems infrastructure' and staff candidates must drive the conversation. Same question appears in Exponent's question bank tagged Anthropic + 7 other companies.

**解法**: Core pattern: request queue + batch scheduler with dual trigger (max batch size 100 OR max wait timeout, e.g. 10-50ms) to bound tail latency; correlation IDs / futures to route responses back to blocked callers; backpressure via bounded queue + 429s; discuss dynamic/continuous batching (vLLM-style) as improvement since sequences finish at different times; multi-GPU extension = consistent-hash or least-loaded dispatch, health checks, retry-on-failure with idempotency. Mention SLO split: TTFT vs throughput, and priority queues for paid tiers.

来源: <https://www.tryexponent.com/blog/anthropic-system-design-interview>

### System design 高频真题：LLM 采样/推理 API（Google Doc 共享文档轮）
*hard · 频率: very high（3+ 独立报告 + 多聚合站） · 2026-01*

Anthropic system design 轮的标志性形式：不用画图工具，在共享 Google Doc 里写设计。最高频题（多个独立报告）：Exponent Safeguards 面经原文 "Design an API to let users sample from large language models efficiently, with good batching and request orchestration"；interviewing.io 版本 "Designing an API for serving large language models efficiently, covering request batching, queuing, and GPU utilization under variable load"。相关变体（聚合站）：LLM 推理系统架构（batching、延迟优化、GPU 调度、部署、容错）、"Design an API for an LLM with a Safety Layer"、KV cache 管理、多区域部署。考察点：变负载下的批处理与排队、吞吐 vs 延迟 tradeoff、GPU 利用率。

**解法**: 核心词：continuous/in-flight batching、paged KV cache（vLLM 思路）、prefill 与 decode 分离调度、按 SLA 分级队列 + backpressure、流式返回（SSE）、speculative decoding、prefix cache 命中、按 token 计费与配额。给出容量估算（单卡 tokens/s、显存 = 权重+KV）会加分。（我的推断，基于业界标准实践）

来源: <https://www.tryexponent.com/experiences/anthropic-senior-software-engineer-interview-2ffa5f>

### Anthropic 系统设计真题：设计高并发 batched LLM 推理 API（含完整需求）
*hard · 频率: high (recurring theme across 3+ sources) · 2026-07*

OfferEngineering 2026-07 完整收录（与 L4 面经'distributed inference API/GPU scheduling and batching for LLM inference workloads'相互印证）。题面：设计服务 LLM 请求的高并发推理 API。客户端提交 prompt+model+生成参数+优先级+是否流式；GPU worker 池有限，核心挑战是 batching——把兼容请求合批提高吞吐和 GPU 利用率同时满足交互路径 <500ms-1s 延迟目标。功能需求：同步/流式响应、重试+request ID+幂等、过载时排队/背压/限流/按优先级丢弃。非功能：吞吐 vs 延迟平衡（等待凑批 vs 尾延迟）、GPU 显存（长 prompt、KV-cache 增长、prefill vs decode 行为差异）、突发流量稳定性、worker 崩溃时受影响请求的安全重试、可观测性（队列深度/批大小/GPU 利用率）。

**解法**: 讲 continuous batching（vLLM 式 iteration-level scheduling）、PagedAttention 管 KV-cache、prefill/decode 分离、admission control + token-bucket 限流、per-tier 队列 + deadline-aware flush（max_wait_ms 或凑满 batch 先到先触发）、worker 心跳 + 请求级 checkpoint 重试。候选人有 post-training 背景，这题应主答推理系统细节。

来源: <https://www.reddit.com/r/OfferEngineering/comments/1us7dqf/anthropic_system_design_question_design/>

### System Design: Design ChatGPT (conversational AI backend with SSE token streaming)
*hard · 频率: Anthropic freq 6/10 (OpenAI 9, Amazon 4, xAI 4) · 2026-04 (published)*

UNLOCKED - FULL 37KB expert-reviewed solution captured (saved at /tmp/h2h_chatgpt_content.md). Stage: Onsite. Design the backend for a ChatGPT-like service: multi-turn conversations, durable history (resume days later), context assembly, GPU-cluster inference dispatch, token streaming via Server-Sent Events. Given targets: TTFT <=500ms p50 / 2s p95; durable conversation persistence. Full doc structure: clarifying Q&A (6 items with interviewer answers + takeaways), functional/non-functional requirements, back-of-envelope estimation, data model + access patterns + storage tradeoff, API design (send-message + SSE event contract + history fetch), high-level architecture, chat completion flow, TTFT budget breakdown, admission control and caching, deep dives (GPU inference scheduling and CONTINUOUS BATCHING; context window management and token budget assembly; streaming delivery contract and failure/reconnect recovery), other considerations (safety guardrails pipeline latency budget, multi-model routing and gradual rollout, conversation summarization for extended context, cost management and tier-based throttling), and explicit interviewer expectations broken down by Junior/Intermediate/Senior level.

**解法**: Full official solution captured locally; key spine: API gateway -> conversation service (durable store) -> context assembler (token budget: system prompt + summarized history + recent turns) -> inference scheduler with continuous batching on GPU pool -> SSE streamer with resumable event ids; separate fast path for streaming vs durable write path.

来源: <https://www.hack2hire.com/question-bank/companies/anthropic/system-design/69d6f527c4c1bc791ee229e3>

### System Design: Distributed AI Model Downloader (500GB model to 1000 hosts)
*hard · 频率: Anthropic freq 8/10 (Anthropic-only tag); last reported 2026-07-08 · 2026-04 (published)*

LOCKED (long preview captured). Stage: Onsite. Internal datacenter tool: fetch a ~500GB model from an external repository and replicate to every host in a 1000-host GPU cluster in minutes not hours, under strict per-link bandwidth caps. Preview's clarifying Q&A establishes: on-demand command-driven distribution of specific model versions (not continuous registry sync); goal is minimizing total distribution time within SLA (~10-20 min window discussion); every host needs a complete verified copy (integrity checking). Core tension: external egress is the bottleneck, so download once (or few times) from the source and fan out peer-to-peer inside the cluster. Full requirement analysis/architecture/deep dives paywalled.

**解法**: My inference (consistent with the preview): chunk the model file; a small set of seed hosts pull distinct chunks from the external repo in parallel (respecting egress cap); then BitTorrent-style peer-to-peer chunk exchange / tree- or pipeline-based multicast inside the cluster so aggregate internal bandwidth scales with host count; per-chunk checksums + final manifest hash for verification; scheduler tracks chunk availability maps, handles stragglers/failed hosts by re-replication. Time lower bound ~ size/per-host-NIC-bandwidth with pipelining.

来源: <https://www.hack2hire.com/question-bank/companies/anthropic/system-design/69dbccaee4441834b3f72fae>

### System Design: AI Prompt Playground (this is the written-Google-Doc SD round)
*medium · 频率: Anthropic freq 9/10 (Anthropic-only tag) · 2026-04 (published)*

LOCKED (long preview captured). Stage: Onsite. Web-based tool for iterative prompt engineering against LLMs: each run is a stateless one-shot request (no conversational memory); user edits prompt/parameters, runs, inspects output, repeats; winning prompts saved/exported. Preview clarifying Q&A: single-user projects only (no realtime collaboration -> one writer per project simplifies versioning); prompts up to 100K tokens / several hundred KB payloads must be handled gracefully; playground must feel instant despite slow external LLM calls; every iteration durably versioned so users can experiment without losing a good prompt. Per hack2hire's process blog, Anthropic runs this SD round entirely as a WRITTEN Google Doc discussion - no diagrams expected; interviewers press on requirements, schema, and scaling roughly equally and drive pacing aggressively. Full solution paywalled.

**解法**: My inference: focus on (1) prompt/version data model - append-only version chain per project, content-addressed blobs for large prompts, autosave drafts vs committed versions; (2) run execution - async job + streaming partials to feel instant, timeout/retry on LLM provider, idempotency keys; (3) large payload handling - chunked upload, size limits, server-side token counting; (4) run history storage linking prompt-version + params + output + cost/latency metrics; (5) scaling reads and provider rate-limit queueing. Practice writing this as prose in a doc, not diagrams.

来源: <https://www.hack2hire.com/question-bank/companies/anthropic/system-design/69dbcc73e4441834b3f72fad>

### System Design: GPU Inference Serving System (dynamic batching under tight latency budget)
*hard · 频率: Anthropic freq 10/10 (Anthropic-only tag, their most-reported SD); last reported 2026-07-05 · 2026-04 (published)*

LOCKED (long preview captured). Stage: Onsite. Layer between user prompts and GPU models: accept many concurrent HTTP requests, group into batches, dispatch to GPU worker pool, return individual responses. Preview clarifying Q&A pins the constraints: SINGLE synchronous completion per request (explicitly NO token streaming); end-to-end p99 <= 500ms total, of which inference execution itself is ~100ms, leaving ~400ms budget for queueing + network + coordination; GPUs cost-effective only with large batches; slow GPU warm-up makes dynamic scaling hard under traffic spikes. Core tension: batch size (throughput) vs queueing delay (latency). Full solution paywalled.

**解法**: My inference: central (or per-model) batching queue with a max-wait timer (e.g., dispatch when batch full OR after T ms, T tuned so queue wait + inference fits p99); size-aware batching by sequence length; per-GPU worker loop pulling batches; admission control/load shedding when queue depth implies SLA miss; warm pool + predictive pre-scaling because of slow warm-up; request hedging/retries on worker failure; metrics on queue delay vs batch occupancy. Discuss why continuous batching applies to autoregressive generation vs fixed batching for single-shot scoring.

来源: <https://www.hack2hire.com/question-bank/companies/anthropic/system-design/69db22a2e4441834b3f72b81>

### System Design: GPU Scheduling Platform (shared training/batch-job cluster)
*hard · 频率: Anthropic freq 3/10 (OpenAI 10, Databricks 6); last reported 2026-06-22 · 2026-04 (published)*

LOCKED (long preview captured). Stage: Onsite. Scheduling + execution layer for a shared GPU cluster: users submit containerized batch jobs (ML training, fine-tuning, batch inference) with resource requirements and priority; platform queues by priority, places on nodes with capacity, runs in containers, monitors, auto-handles failures. Preview clarifying Q&A: each job fits on a single node (gang scheduling for distributed training explicitly deferred to follow-up); node can become unreachable between placement decision and job start - every placement is a distributed commitment across scheduler, database, and remote node agent, any of which can fail mid-assignment. Full solution paywalled.

**解法**: My inference: priority queues with preemption policy; two-phase placement (reserve in DB -> ack from node agent -> commit; lease/timeout to reclaim on agent silence); reconciliation loop comparing desired vs actual state (Kubernetes-controller style); heartbeat-based node health, job checkpointing and restart policy; fairness (per-team quotas, DRF) as follow-ups; gang scheduling and bin-packing/fragmentation for multi-GPU as advanced follow-ups.

来源: <https://www.hack2hire.com/question-bank/companies/anthropic/system-design/69d71cbfc4c1bc791ee22b22>

### Anthropic · System Design 题库（7 题，重 AI 推理基础设施 + Prompt Playground 书面轮）
*hard · 频率: onsite 常见 — Anthropic 频率：Design GPU Inference Serving System 10、Design AI Prompt Playground 9、Design Distributed AI Model Downloader 8、Design ChatGPT 6、Design Slack-like Chat System 7、Design Facebook Messenger 4、Design GPU Scheduling Platform 3 · 2025-12 至 2026-02*

Anthropic SD 全 7 题（均 Onsite，正文需登录；practice URL 形如 .../anthropic/system-design/{id}/practice）：Design GPU Inference Serving System(Hard, id 69db22a2e4441834b3f72b81, Anthropic 频率10)、Design AI Prompt Playground(Medium, 69dbcc73e4441834b3f72fad, 频率9)、Design Distributed AI Model Downloader(Hard, 69dbccaee4441834b3f72fae, 频率8)、Design ChatGPT(Hard, 69d6f527c4c1bc791ee229e3, 频率6)、Design Slack-like Chat System(Hard, 69c9fe5dff3ebde766ced6f4, 频率7)、Design Facebook Messenger(Medium, 69d2bf7307421ca06eb8e38c, 频率4)、Design GPU Scheduling Platform(Hard, 69d71cbfc4c1bc791ee22b22, 频率3)。据 process blog：其中 Prompt Playground 轮为纯 Google Doc 书面讨论无需画图；另有一轮更常规 SD（如 batch inference API 设计）。

**解法**: （我的推断）对该 post-training 候选人极对口：GPU Inference Serving（KV-cache、continuous/dynamic batching、tensor/pipeline 并行、token 流式、多租户 SLO）、Model Downloader（大权重分发、P2P/BitTorrent 式、分片校验、断点续传）、Prompt Playground（多版本 prompt/eval、A-B、trace 存储）。练书面表达 requirements/schema/scaling 深度，别依赖画图。

来源: <https://www.hack2hire.com/question-bank/companies/anthropic/system-design>

### Handle 100,000 requests/sec for an LLM token-generation service (Anthropic)
*hard · 频率: multiple reports · 2026-01*

Prompt: 'Handle up to 100,000 requests per second for an LLM token-generation service.' Tests throughput reasoning, horizontal scaling, request routing at volume. Related Anthropic-tagged question from Exponent's bank: 'Implement a streaming database with the given constraints and requirements.' Evaluation criteria reported: abstraction ability (strip AI framing to find the core infra problem), trade-off articulation, proactive failure-mode reasoning, scale reasoning under real constraints (not generic 'add servers').

**解法**: My inference: size in tokens/sec not RPS — 100K RPS × avg output tokens dictates GPU pool; per-node continuous batching, KV-cache memory as the binding constraint (KV bytes = 2·layers·kv_heads·head_dim·dtype per token), paged KV allocation; layered routing (edge LB → regional cell → model replica group), sticky sessions for multi-turn to exploit prefix cache; admission control + token-bucket rate limiting; degrade gracefully (shorter max_tokens, smaller fallback model, cached responses).

来源: <https://www.tryexponent.com/blog/anthropic-system-design-interview>

### Design an agentic AI system that autonomously adapts to new tasks (Anthropic, ML roles)
*hard · 频率: single-to-few reports · 2026-01*

Prompt from Exponent's Anthropic guide and question bank: 'Design an agentic AI system that can autonomously adapt to new tasks.' More domain-specific than Anthropic's infra-flavored questions; expected coverage: agent loop (plan → act → observe), tool/function-calling interfaces, short/long-term memory, termination conditions, sandboxing and safety guardrails, evaluation of agent behavior.

**解法**: My inference: orchestrator with typed tool schemas (reduces hallucinated calls), task decomposition + reflection step, episodic memory store (vector DB) + working-memory context budget, guardrails before tool execution (allowlists, dry-run), bounded loop with max-steps + cost budget, eval harness with golden tasks + LLM-as-judge + human escalation; adaptation to new tasks via tool registry discovery and few-shot exemplar retrieval rather than retraining.

来源: <https://www.tryexponent.com/questions?role=ml-engineer&type=system-design>

## BQ / Culture

### Culture/Values 轮：技术全过后最常见挂点，reference check 后仍可能被拒
*hard · 频率: very high (10+ reports提及) · 2026-04*

多帖一致：culture round 聚焦 AI-safety alignment（为什么是 Anthropic、对 AI 风险的看法、与 Anthropic 使命一致性），是'技术每轮都过仍被拒'的最常见单点。流程尾部：VO 后 2 天内通知进 reference check，之后 hiring committee 决定，有人 reference check 完成后等一周以上无消息，也有'人类学新鲜挂经 reference check后被拒'（bbs thread 1141359，2026 Q1）——reference check 不等于 offer。reference check 流程讨论：bbs/interview thread 1171272。全流程挂经（每一步都详细）：bbs thread 1130596 '答谢地理人无私share面经，anthropic全部挂经'。

**解法**: 准备真实、具体的 safety 观点（读 Core Views on AI Safety、RSP），避免背稿感；准备'为什么从 Meta/前司离开'、对 scaling 与 alignment 关系的个人立场；reference 人选提前打招呼。

来源: <https://www.1point3acres.com/bbs/thread-1141359-1-1.html>

### Values/Culture 轮完整拆解（含 verbatim 真题）——最高挂人轮
*hard · 频率: very high（每个候选人必经，多来源一致称最高淘汰率轮） · 2026-01*

所有岗位所有级别必过的 45-60min 非技术轮，由非技术面试官主持。Exponent Safeguards 候选人：招聘者明确预警 "the company values round was the one where people usually fail"；体验 "almost like a therapy session"——不断追问情绪感受而非逻辑复盘。Verbatim 真题（Exponent 面经）："Tell me about a time you had to build something that was against your values"；"Why Anthropic?"；"How were you feeling at that time? And how do you feel about it now?"；"Tell me about a time you had a conflict"；"Tell me about a time you made something outside your job description"；"Do you have any feedback on Anthropic's mission?"。其他多来源真题：与自己价值观冲突的经历、被分配到认为不安全的项目怎么办、改变强烈观点的经历、push back 但输了的经历。有效策略（该候选人实证）：真诚的怀疑立场比表忠心更好——他说 "I am not totally confident anyone can reach the level of safety they say they want" 反而 resonate；interviewing.io 同样结论："Thoughtful disagreement lands better than alignment-signaling"。失败模式第一名：套用预制 STAR 故事（Ridhima Substack："face-plant"；考察 4 项：hold complexity without collapsing into a tidy narrative、承认知识盲区、二阶效应推理、intellectual honesty > polish）。准备材料：Machines of Loving Grace（2024）、The Adolescence of Technology（2026.1）、Core Views on AI Safety、RSP。该候选人建议："I would prep the behaviorals way harder than the technicals for this one."

**解法**: 准备 3-5 个真实的道德灰色/冲突/犯错故事，重点练'当时的情绪+现在的反思'两层表达；对 Anthropic 的 mission 准备一条真诚的批评/保留意见；读完上述三篇必读并形成自己不同意的点。

来源: <https://www.tryexponent.com/experiences/anthropic-senior-software-engineer-interview-2ffa5f>

### Anthropic Culture/Values 轮真题与淘汰机制：技术全过也会在此挂掉
*hard · 频率: very high (8+ reports of culture-round eliminations/questions) · 2026-05*

多个 2026 报告确认 culture 轮是真实过滤器且常放最后。真题：(1) 'What do you think Anthropic is getting wrong?'——要求对 Anthropic 具体决策有真实批评观点，泛泛的 AI safety 立场会被追问到哑（一人因此挂）；(2) '你最讨厌哪类工作？'→follow-up：'如果我也讨厌它，说服我去做'；(3) '你做过什么道德上不正确的事吗？'；(4) 2026 职业目标；(5) AI safety 权衡、模糊部署场景下的伦理决策、结果与预期冲突时的 intellectual honesty。多例：非工程背景面试官、频繁打断、极难读出反馈；有人所有技术轮过了在 values 轮被刷。教练整理的常规问题：Why Anthropic specifically / Why this role / 对 Anthropic AI safety 路线的看法。备考建议（offer 获得者）：把 culture 轮当独立 track 准备——读 Anthropic 发表的 research、RSP、对齐博客，形成自己的一致立场。Recruiter 首轮也会问'What's your personal mission?'。

**解法**: 准备一个对 Anthropic 具体决策的有理有据的批评（如模型发布节奏 vs RSP、Claude Code 商业化与安全使命的张力），并能与'安全与能力并进'的世界观自洽；诚实优先于讨好——候选人被反复打断时要能简洁收束观点。

来源: <https://www.reddit.com/r/Hack2Hire/comments/1t6ncgs/anthropic_interview_process_experience_megathread/>

### What Anthropic Actually Tests - And What Gets Candidates Rejected (2026) - hack2hire analysis
*unknown · 频率: aggregate of 15 firsthand reports collected April 2026 · 2026-06-04*

FULL article captured. Key claims: (1) Anthropic rejects more technically-passing candidates in the CULTURE round than any technical stage; dominant failure mode is NOT values disagreement but generic framing - answers like 'I care about responsible AI' or 'I value technical rigour' that would pass at any tech company consistently fail; passing requires naming a specific Anthropic value, demonstrating personal history with it via a concrete example, and critical thinking about Anthropic's OWN tradeoffs; the round requires showing where your values CONFLICTED with something and what you chose. (2) Coding rounds: library knowledge (PIL/Pillow, Python concurrency primitives) is the actual gate, not algorithmic skill - questions are designed to require them with no data-structure-only workaround; silent solvers score lower than candidates showing visible reasoning on incomplete solutions; proactive testing/edge-case verification explicitly scored. (3) SD: Prompt Playground round is written Google-Doc, typed reasoning depth on requirements/schema/scaling is scored; diagram completeness and breadth NOT evaluated; holding your structure against aggressive interviewer-led redirection is the actual criterion. (4) Project retro: 20-min self-driven presentation then adversarial challenge of every detail; rehearsing only the forward presentation loses depth midway. What they DON'T test: pure DS&A theory without library application (standard LeetCode prep 'does not transfer'); whiteboard/diagram SD; broad SD coverage; generic values alignment. Rejection-timing tell: <=24h = technical, 2-3 days = culture/HM.

**解法**: Actionable: prepare 2-3 stories where your values conflicted with incentives and what you chose; read Anthropic's published positions well enough to critique tradeoffs; drill Pillow + concurrency; practice narrating tests aloud; practice written (doc-style) design prose under time pressure.

来源: <https://www.hack2hire.com/blog/content/6a219a818b879849ebc11ff6>

### Culture interview 独立分析（Ridhima Khurana Substack）
*hard · 频率: single analysis（与多面经交叉一致） · 2026-03*

2026-03-17 发布（作者有 Google Gemini/Workspace 背景）：45 分钟，PM/工程师/研究员/销售所有角色所有级别必面，是 6 阶段流程之一。两类问题：Type 1 AI safety reasoning，例 "What are your thoughts on AI safety and the risks of advanced AI systems?"——要求给出 specific, concrete risks，泛泛说 'AI could be dangerous' 直接挂；Type 2 project deep-dive，例 "Walk me through a project you're most proud of. What decisions did you make, and what tradeoffs did you navigate?"——通过工作选择考察价值观。评估 4 项能力（见上条）。备考：完成指定阅读（Core Views、RSP、研究论文）、用 Claude 加深理解、批判性 engage（找出自己不同意之处）。对应 Anthropic 三条公开价值观：Act for the global good / Hold light and shade / Be good to our users。

来源: <https://ridhimakhurana.substack.com/p/inside-anthropics-culture-interview>

### 行为面样题汇总（多来源）
*medium · 频率: 各题 1-3 报告 · 2026*

OA/HM/onsite 行为轮被报告的问题："Why do you want to work at Anthropic?"、"Why are you interested in AI safety?"、与队友技术分歧如何解决、处理模糊性、speed vs quality tradeoff（medium programhelp）；"Tell me about a time you made a safety-first decision in a project, even if it meant a trade-off"、导致项目延期的技术误判及教训（Anqi Silvia 面经）；"What would you do if, midway through a project, you realized it was actually unfeasible?"；哲学向："What do you think is the biggest risk of anthropomorphizing language models?"（jobright 聚合，标注为 final 轮开放题）。Glassdoor 碎片："You're overqualified — why would you want this job?"（追问 "How would you flip that into a positive without losing credibility?"）。注意与 values 轮区分：行为轮更常规，values 轮才是'therapy session'式。

来源: <https://jobright.ai/blog/anthropic-technical-interview-questions-complete-guide-2026/>

### 申请表书面题（written form，代替或先于行为面）
*medium · 频率: 官方申请表（所有申请者） · 2025*

Anthropic 申请表包含开放式书面题（无限时，答案高权重）。已确认的 verbatim："Why Anthropic? [Why do you want to work at Anthropic?] (We value this response highly - great answers are often 200-400 words.)"（Zharkov 记录，官方申请表原文）；早期版本还有 "why do you want to work here?" essay（Fortune 报道，曾要求不用 AI 写，2025.7 起允许 Claude 润色但需自己起草）。Zharkov 同批记录的同类公司书面题（Anthropic/SSI/Mistral/Recraft 混合，供准备参考）：一段话举例说明你做过的符合自身价值观的有意义的事；理想的一周时间分配（开会/写码/读论文 %）；贴一个你觉得 impressive 的 commit 链接并解释（不必是自己写的）；"What do you optimize for in life?"；"How intensely do you like working?"。同公司不同职位的表格题基本复用，答案值得存档。

**解法**: 'Why Anthropic' 按 200-400 词写：具体到某篇 Anthropic 论文/政策立场 + 自己经历的衔接 + 一条真诚的保留意见，避免泛泛的 AI 热情。

来源: <https://reyzharkov.com/blog/posts/interviews-2025-ml-research-engineer-uk>
