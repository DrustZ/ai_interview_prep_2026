# Google DeepMind 题库（爬取全量）

> 由 raw/build_question_bank.py 从爬取数据自动生成（2026-07 抓取）。每条含来源 URL 可回查原文。

## 流程与情报

### GDM RS Intern 完整 4 轮流程（2022 Summer）：HR screening 起步，senior RS 主动挖人+referral
*medium · 频率: high（intern technical 轮 3 帖同格式：819210/813950/942891） · 2021-11*

《Deepmind 2022 Summer Research Scientist Internship 面经》2021-11-13。原文首段："AI 第三年博士，突然被Deepmind一位senior research scientist 联系要不要来summer intern，然后网申加上他给的referral，就进入了Deepmind 4 轮面试：1、HR screening……"（第 2-4 轮正文积分墙隐藏）。结合同期帖子可拼出 intern 轨全貌：1) HR screening；2) technical interview（813950：1 小时，一位 scientist 全程口头问基础数学概念——linear algebra、statistics 主要是 probability、ML，最后跟一个代码阅读；942891 同款：简单数学题+code comprehension+基本 ML 问题）；3) research/team 面；4) team match/final。Glassdoor 交叉数据：GDM intern 全程平均 120 天，极慢。

来源: <https://www.1point3acres.com/bbs/thread-819210-1-1.html>

### Official GDM interview process: 4 stages, 4-10 weeks, competency-based, no AI in live interviews
*unknown · 频率: official source · 2025*

From DeepMind's official candidate PDF: stages are Initial interviews → Skills interviews → Final interviews → Decision and offer. Candidates sign an NDA (Ironclad) before interviewing. Interviews are virtual (Google Meet), competency-based; DeepMind explicitly recommends STAR (Situation/Task/Action/Result) answers and 'clearly defined criteria' scoring for fairness. Timeline 4-10 weeks depending on role. AI policy: 'You're free to use AI to help you prepare... but unless told otherwise, please don't use any AI tools during live interviews, or during interview tasks.' Interviewing in parallel with Google is allowed but must be disclosed. Internships run through Google recruiting, not GDM. Tips emphasized: think out loud, admit uncertainty ('curiosity and intellectual honesty'), use data to demonstrate impact, prepare questions.

来源: <https://storage.googleapis.com/deepmind-media/DeepMind.com/Assets/Docs/interviewing-at-google-deepmind.pdf>

### Research Engineer loop structure (IGotAnOffer guide): recruiter → gated coding screens → ML rounds → final round
*hard · 频率: aggregated from many reports · 2025*

Recruiter screen is conversational; recruiter decides whether you fit the research-focused or applied side, sometimes adds a hiring-manager interview probing ML+engineering background. Skills round = 2-3 calls: two coding rounds (algorithmic, in a real coding environment) plus a set of ML rounds testing depth/breadth of ML knowledge including the math and application to design problems. The two parts are gated — you must clear coding before ML, sometimes with a ~2 week wait. Key difference vs Google: 'DeepMind expects your code to actually run by the end of the round' (CoderPad-like environment). Final round = (1) team lead interview: background, ML experimentation/modeling experience, open-ended ML problems; (2) senior team lead interview: explicit team-fit assessment; (3) People & Culture partner: motivation/culture ('why do you want to join DeepMind'). Anything on your resume can come up; be ready to defend design decisions and discuss conflict with coworkers. ML rounds are consistently described as the toughest part of the process.

来源: <https://igotanoffer.com/en/advice/google-deepmind-research-engineer-interview>

### Blind: full RE loop report (Amazon MLE, L5) — 2 coding screens, 2 ML screens, virtual onsite, rejected at team fit
*hard · 频率: single detailed report; structure corroborated by IGotAnOffer and Reddit · 2023*

6-7 weeks total. Round 1: two coding screens with Google-style questions from Google's internal bank. First screen: one LC-medium coded + LC medium/hard follow-up (explanation only) + LC easy + LC easy/medium (explanation only). Second screen: an LC-hard not found on LeetCode requiring knowing a polynomial-time solution. 'You have to run the code and it's expected that by the end you have a solution which runs in CoderPad.' Round 2 (only after clearing coding): two ML screens. First probed depth of ML knowledge — probability, Bayes-theorem questions ('a number of balls style question on Bayes theorem'), plus design problems; emphasis on mathematical intuition (e.g., not just that L1 gives sparse features but WHY, in terms of gradients acting on weights). Second ML screen: 'hardest ML round I ever gave' — design-style question where interviewer kept adding constraints; discussed 7-8 different techniques with 7-8 constraints layered onto each solution. Round 3: virtual onsite = two non-technical interviews with team leads on background and ML experimentation experience + one People&Culture behavioral. Outcome: rejected with feedback 'didn't have enough experience in ML experimentation and modeling.'

来源: <https://www.teamblind.com/post/deepmind-research-engineer-interview-process-wp1gjgyb>

### techinterview.org 2026: RS track round-by-round (paper discussion, research problem framing, ML coding, math/theory, behavioral)
*hard · 频率: prep-site synthesis (unverified but consistent with candidate reports) · 2026*

Research Scientist loop per this 2026 process guide: (1) Paper discussion, 60 min — present a recent paper of yours (or one you know deeply if unpublished); interviewer probes methodology, motivation, weaknesses, extensions; 'interviewers will push hard on assumptions'; candidates often do 2-3 paper discussions with interviewers from different subdomains. (2) Research problem framing, 60 min — open-ended problem; propose experiments, metrics, theoretical analysis, and what would falsify the approach; tests scoping under ambiguity. (3) ML coding, 60 min — implement a piece of ML pipeline by hand: custom loss, attention mechanism, sampling routine, or small training loop; 'almost always unaided.' (4) Math and theory, 60 min — probability, linear algebra, optimization, gradient flow, Bayesian inference, convergence, information theory. (5) Behavioral, 45 min — mission alignment, collaboration, past disagreements with collaborators. Overall funnel: recruiter screen → HM screen → 1-2 phone screens → 5-7 round loop → hiring committee (written packet, decision-makers are not your interviewers) → team match/offer. 8-12 weeks for research roles. PhD 'effectively yes' for RS.

来源: <https://www.techinterview.org/post/3233474918/deepmind-interview-process-2026/>

### 2026 AI-tool policy in technical rounds: prohibited/heavily limited — unaided reasoning is filtered for
*unknown · 频率: multiple sources · 2026*

Multiple 2026 sources agree DeepMind is 'AI-prohibited or heavily limited in all technical rounds'; research roles explicitly filter on unaided foundational reasoning — implement algorithms and ML primitives without AI assistance. Official DeepMind PDF confirms: no AI tools during live interviews or interview tasks unless told otherwise. Positioning vs peers: more conservative than Anthropic (which grades AI-collaboration in some rounds), more uniform than OpenAI. Exceptions possible for applied roles — verify with recruiter.

来源: <https://www.techinterview.org/post/3233474918/deepmind-interview-process-2026/>

### Blind 2023-06: the math/stats 'quiz' still exists but format loosened from 2-hour exam
*medium · 频率: multiple corroborating comments · 2023-06*

Ex-Googler (PhD, 3 YOE) preparing for RE asked whether DeepMind still asks 'math/stats knowledge questions such as definitions from the textbooks.' Answers: one commenter initially said the quiz was discontinued, then edited: 'incorrect, they still do'; another confirmed 'I am interviewing in couple of weeks and first interview is about that'; a third noted the format has evolved — 'some math/stats questions are asked, [but] it does seem different from previous years, when they had a 2h exam-like format.' IGotAnOffer corroborates: candidates call the ML fundamentals round 'the quiz'; it used to be a rigid set of textbook questions but has loosened in recent years; recruiters flag maths/stats coverage in advance. Historical variant (Blind): 'DeepMind for Google Research' vs 'DeepMind for Google' applications differed, the former involving a 2-hour quiz with ML and coding components.

来源: <https://www.teamblind.com/post/interviews-for-research-engineer-at-deepmind-kd1tfu6b>

### Aleksa Gordić (hired 2021, Medium): 6-stage RE loop incl. 2 back-to-back quiz interviews covering math/stats/CS/ML + OS
*hard · 频率: single detailed report (pre-2024 but structurally consistent with current loop) · 2022-07*

Historical but detailed first-person account of getting RE (Core team) offer: stages = (1) recruiter chat (Core vs Applied fit); (2) quiz round: TWO back-to-back interviews on fundamentals across maths (linear algebra, probability, calculus), stats (hypothesis testing, distributions, inference), CS (algorithms/data structures, sorting/searching, formal big-O, operating systems: deadlocks, threads, virtual memory), ML (RL fundamentals: MDP/agent-environment-reward, classical ML, core DL); (3) coding interview (classic big-tech style); (4) team lead interview (resume deep-dives, open-ended ML problems, behavioral); (5) senior team lead interview (team fit, ML systems design); (6) People & Culture ('What do you like about DeepMind?', 'Why DeepMind and not some other company?', 'Tell me about your favorite project'). Prep resources he used: Cracking the Coding Interview, CLRS DP chapter, Mathematics for Machine Learning book, jbstatistics + StatQuest, GeeksForGeeks. Advises researching each interviewer's papers/profiles beforehand.

来源: <https://gordicaleksa.medium.com/how-i-got-a-job-at-deepmind-as-a-research-engineer-without-a-machine-learning-degree-1a45f2a781de>

### Entry bar and RS-vs-RE routing (2026 Reddit + Blind): RS effectively needs PhD + strong pubs; RE flexible; recruiters are the main channel
*unknown · 频率: multiple corroborating reports · 2026-01*

r/MachineLearning 2026-01 thread (Amazon Applied Scientist II, no PhD, asking RE vs RS): top comment — 'You're not getting an RS interview unless you've published heavily... Apply for RE. Try and connect with a recruiter first. All my interviews with DeepMind came from recruiters and having a relationship with them.' GDM staff commenter: no hard publication rule — 'I would take a candidate that only wrote one paper if that paper was revolutionary'; being at another respected lab or doing relevant applied ML work counts; 'I was doing applied ML engineering before joining GDM'; once inside, RE→RS is fluid given research taste. Another academic: 'My PhD students graduate with 3+ tier-1 papers and ~100 cites and aren't getting RS interviews' — bar is high and noisy. Blind (2023): 'For research scientist they hire only PhDs but for research engineer they go for masters too.' 2026-05 Reddit RE candidate got the interview via cold LinkedIn application with an ACL first-author paper + senior GenAI SWE experience; used Claude to rewrite CV with JD keywords.

来源: <https://old.reddit.com/r/MachineLearning/comments/1q2wiub/d_google_deepmind_research_engineerscientist/>

### Glassdoor overall stats and stage pattern (2024-2026): recruiter → 2 coding + 1 ML fundamentals → ML design + lead researcher
*medium · 频率: aggregate of ~18 RE + 13 RS reports · 2026*

Glassdoor aggregate for GDM Research Engineer: stages reported as '1) Recruiter call, 2) 2 Coding Interviews + 1 ML Fundamentals interview, 3) ML Design + an interview with the Lead Researcher.' Coding = two DS&A problems per virtual interview, standard LeetCode medium/hard; unlike standard Google interviews, code must RUN in a CoderPad-like environment with a working solution by end of round. Candidates also 'describe research papers and answer coding questions plus technical and theoretical questions in deep learning relevant to the role.' RE: difficulty 3.3/5, 61% positive, 46 days avg (18 reports). RS: difficulty 3.2/5, 49 days avg. Both Glassdoor interview pages are bot-blocked; data recovered via search snippets.

来源: <https://www.glassdoor.com/Interview/Google-DeepMind-Interview-Questions-E1596815.htm>

### Interviewing.io: no DeepMind guide exists (only OpenAI/Anthropic company pages)
*unknown · 频率: n/a · 2026-07*

Checked interviewing.io for a DeepMind guide as requested: the site has dedicated company pages for Anthropic (interviewing.io/anthropic-interview-questions) and OpenAI (interviewing.io/openai-interview-questions) but no DeepMind-specific interview page as of 2026-07. Their generic AI-era interviewing posts don't cover GDM's loop. Use IGotAnOffer/techinterview.org/Glassdoor instead for GDM.

来源: <https://interviewing.io/blog>

### GDM Research Engineer 挂经（2025-09，唯一确认的 2025 年 RE 全流程面经帖）
*unknown · 频率: single report · 2025-09*

帖子标题《Deepmind Research Engineer面经（挂经）》，发于 2025-09-23，海外面经版。正文在登录+积分墙后，无 Wayback 快照，无法恢复具体轮次内容。可确认：岗位 Research Engineer，结果为挂。这是 1p3a 上 2024-2026 期间唯一一篇 GDM RE 正式面经帖。结合 1p3a interview 聚合页（/interview/company/deepmind）显示的条目：有一条 2025 年 7-9 月的 Machine Learning 面试记录和一条 2023 年 10-12 月伦敦 Research Scientist 面试记录。若需正文，需要 1p3a 账号且积分达标。

来源: <https://www.1point3acres.com/bbs/thread-1147017-1-1.html>

### GDM RE 伦敦 2022 改版流程：两大轮，第一大轮 = math / ML / CS+coding 三个一小时（GDM vs Google 区别的核心证据）
*medium · 频率: 流程结构被 3+ 帖交叉印证（918169/837817/825115） · 2022-08*

《deepmind伦敦 RE面试》2022-08-09。原文首段："recruiter联系就面了一下 之前不太了解RE的面试流程 不知道是整体都改了 还是RE和RS不同。目前RE是两大轮面试 第一大轮是三个一个小时的面试 分别是math, ML, cs+coding……"（后文积分墙隐藏）。即 RE 流程：第一大轮 3×1h 独立场（数学、机器学习、计算机科学+编码），过了再进第二大轮（结合其他帖为 ML design / Hiring Manager+BQ / team match）。这与 Google 普通 SWE 的 4-5 轮纯 LC + Googleyness 完全不同：GDM 由自己的 recruiter 驱动、按 RE/RS 分轨、显式考数学统计与 ML 理论。

**解法**: 我的推断：math 场以概率+线性代数口头快问快答为主（见 813950/825115 帖佐证），ML 场考基础概念深挖，CS+coding 场为 LC medium 级现场写码+复杂度分析。按三场分开准备。

来源: <https://www.1point3acres.com/bbs/thread-918169-1-1.html>

### GDM ML Research Engineer 正式面试三轮结构：coding / ML / Hiring Manager+BQ（终轮面经）
*medium · 频率: 单帖，但三轮结构与 825115 完全一致 · 2022-01*

《DeepMind ML research eng终轮面经》2022-01-11。原文首段："DeepMind ML research engineer，正式面试有三轮，一轮coding，一轮ML，第三轮Hiring manager + BQ。前两轮之前有发过面经。第三轮12/2, 12/3。"（终轮具体问题在积分墙后）。与 918169 相互印证：recruiter 聊天 → coding 轮 → ML 轮 → HM+BQ 终轮。时间线：11 月面前两轮，12 月初终轮。

**解法**: 我的推断：HM 轮一半以上时间会深挖简历里某个具体 model/项目的技术细节（825115 楼主终轮实录佐证），BQ 为标准冲突/失败/协作题。

来源: <https://www.1point3acres.com/bbs/thread-837817-1-1.html>

### GDM Research Scientist 终轮格式：research talk + 与每位 teammate 各聊 30 分钟（含与大佬面试求教帖）
*hard · 频率: 2 reports（942817 + 875411 流程互补） · 2022-11*

《DeepMind Research Scientist 最后一轮 求教如果跟citation 15w+的大佬面试》2022-11-05。原文首段："LZ是ML PhD……阴差阳错的面到了deepmind的最后一轮。最后一轮出了要做research talk，还要跟公司的teammate每个人都聊半个小时的那个环节"，且其中一位面试官是 citation 15w+ 的大佬。印证 RS 轨终轮 = job talk（研究报告）+ 逐个团队成员 1:1。结合 875411：RS 流程入口为 LinkedIn 看到职位→官网投递→2 周后 recruiter email→先与 team manager 面谈（岗位为 DeepMind London，与研究方向高度匹配）。

**解法**: 我的推断：research talk 按 job talk 标准准备 45-60 min 报告+被打断问细节；对大佬面试官不必迎合其领域，重点讲清自己工作的 motivation、与 DM 研究方向的连接、未来 1-2 年 research agenda。

来源: <https://www.1point3acres.com/bbs/thread-942817-1-1.html>

### GDM RE 面试 timeline 实录（进行时长帖，3 页）：1 月海投→3 月 HR 联系→可自选推迟 1 个月，招聘周期极长
*unknown · 频率: single report（长帖多人跟更） · 2022-04*

《Google DeepMind Research Engineer 面试 （进行时）》2022-04-02 开帖，持续更新至 2023-10（3 页、回复量大）。原文首段："一月初海投的以为没有什么戏，3月HR联系我，和HR聊了一下，问我什么时候面试，我说能不能1个月之后，HR说完全没问题，招聘周期长……"（后续各轮 update 在积分墙后）。要点：GDM 海投有响应但周期以月计；HR 允许候选人大幅自定面试时间（备考窗口可谈）；与 Glassdoor 数据一致（RE 平均 46 天从面到 offer，全岗位平均 40-41 天，intern 120 天）。

来源: <https://www.1point3acres.com/bbs/thread-878129-3-1.html>

### GDM RS 伦敦电面（两个组同时面）：HR screening 内容 + 跨组共享轮次机制
*unknown · 频率: 2 reports (682678, 579309) · 2020-10*

《deepmind伦敦电面》2020-10-29。原文首段："面了伦敦两个组的research scientist 一个是朋友内推的 一个是自己海投 面试内容两个组有共同的部分 就都一起面的。HR screening基本上就是问你想做啥 介绍一下面试流程……"（后续隐藏）。要点：可同时进两个组的 RS 流程，技术轮跨组共享结果；HR screening 主要问研究意向并讲解流程。另《DeepMind DMG research scientist Intern》(thread-579309, 2019-12) 印证：第一轮 HR 聊天的目的是"HR想给你找合适的组来面你"，即先 team match 后技术面。

来源: <https://www.1point3acres.com/bbs/thread-682678-1-1.html>

### GDM 薪酬数据点（1p3a 晒工资版）：2022 L4 RE offer 谈到 4 年均 400k/首两年 520k；2024-2025 另有 Refresh 与 RE 包裹帖
*unknown · 频率: 4 data points · 2022-08 / 2024-03 / 2025-01*

三个薪酬帖：(1)《DeepMind L4 报一波》thread-906852，2022-08："上面报的是initial offer，后来DeepMind加到了4年平均400k，第一年第二年520k"（美元/年，含股票；初始包数字隐藏）；(2)《Google Deepmind Refresh》thread-1051085，2024-03（数字隐藏）；(3)《Google Deepmind Research Engineer包裹》thread-1105016，约 2025 初（数字隐藏）。另《Deepmind Research Scientist London包裹》thread-662595，2020-08：伦敦 RS 包裹无 sign-on，为谈过一轮后的数字（具体隐藏）。用于谈包参考：GDM offer 有较大谈判空间（906852 案例 initial→400k avg）。

来源: <https://www.1point3acres.com/bbs/thread-906852-1-1.html>

### 组织背景：2023 年 Google Brain 与 DeepMind 合并为 GDM，招聘/面试流程与 Google 普通 SWE 仍分离
*unknown · 频率: unknown · 2023-04*

《🐶家合并了research和deepmind》thread-989608，2023-04："新的pa还叫deepmind，但是不是other bet"——合并后 GDM 成为 Google 内的 PA（product area）而非 Alphabet other bet。对面试的含义（多帖综合）：GDM 仍有独立 recruiter、独立面试轨（RE：coding+ML+math quiz+ML design+HM；RS：manager chat+technical quiz+research talk+team 1:1s），不走 Google SWE 的统一 HC/packet 流程；但 coding 轮题风与 Google 题库趋同（1116355 帖策略佐证）。另有《[公司评价] Google的经历》thread-1114328（2023 年入职 GDM 者吐槽代码质量）可作团队体验参考。

来源: <https://www.1point3acres.com/bbs/thread-989608-1-1.html>

### 1p3a GDM 面经索引（deepmind 标签页全量清单，截至 2026-01 共 29 帖）
*unknown · 频率: 29 threads total · 2019-2026*

deepmind 标签页（tag/deepmind-3761-1.html，2026-01-16 时 29 主题/344 回复）经 Wayback 恢复的全部面试相关帖：2025: 1147017(RE挂经), 1116355(DS求米), 1105016(RE包裹)；2024: 1051085(Refresh)；2022-2023: 989608(合并讨论), 942891(RS intern tech), 942817(RS终轮), 938855(ML design), 938777(SWE intern), 918169(伦敦RE流程), 906852(L4包), 878129(RE进行时), 875411(RS technical), 865383(research lab做eng体验讨论), 837817(RE终轮)；2021: 825115(RE二轮ML), 824784(research SDE职责讨论), 819265(RE电面), 819210(RS intern 4轮), 813950(RS intern quiz)；2019-2020: 695950(RS intern), 689380(research tech店面), 682678(伦敦RS电面), 662595(RS London包), 637871(London电面), 628812(英国实习/applied scientist), 579309(DMG RS intern), 578953(RE一面), 540650(RE quiz), 482242(intern一二轮), 475151(面经), 467663(SDE intern挂经), 455587/432949/444088/426795(2018-19老帖)。另有淘帖合集 collection/229692。所有正文均需登录+积分。

来源: <https://www.1point3acres.com/bbs/tag/deepmind-3761-1.html>

### Google DeepMind RS/RE interview process summary (Sundeep Teki company guides; details paywalled)
*unknown · 频率: single source (commercial guide) · 2026*

Visible summary: 5-8 rounds through Google's hiring-committee structure; technical assessment spans 'maths, statistics, ML, coding, and system design' with emphasis on 'first-principles mathematical fluency' and 'JAX-native implementation'; cultural signals: intellectual curiosity, scientific rigour, 'Googleyness & Leadership'; comp cited $336-406K + GOOG equity. Contrast drawn: OpenAI = 3-6 rounds incl. research discussion round where 'OpenAI sends you a paper to analyze', practical coding (LRU caches, rate limiters) not pure LeetCode, 'AGI focus / intense & scrappy' culture signal; Anthropic = CodeSignal 4-level assessment with 520+/600 passing threshold, 4-6 rounds incl. explicit safety round, focus on 'practical coding, LLM system design, Constitutional AI fundamentals', 'do the simple thing that works' culture. Full guides are paid (Stripe links); only these summaries are free.

来源: <https://www.sundeepteki.org/company-guides.html>

### GDM Research Engineer 完整面试流程（2026 版，IGotAnOffer 聚合指南）
*hard · 频率: 聚合指南（基于 Glassdoor+Blind 多条报告） · 2026-06*

全程 6-7 周（含 hiring committee 可更长）。流程：简历筛（~90% 淘汰）→ 30min recruiter call（判定你适合 Applied 还是 Core 方向，有行为面成分）→ 可能加 HM 面 → Skills 轮 2-3 场：2 轮 coding + 一组 ML 轮（fundamentals + design）；coding 与 ML 轮是 gated 的——必须先过 coding 才安排 ML，中间可能等两周 → 终面：Team Lead 面（简历任何内容+开放式 ML 问题）+ Senior Team Lead 面（更明确考察团队匹配）+ People & Culture 行为面 → 每轮面试官填标准化反馈表（Strong no hire→Strong hire），打包送第三方 hiring committee → 4 种结果：录用 / 先 team match / 加面 1-2 轮 / 拒。Coding 轮特点：LC medium-hard，题目多出自 Google 内部题库，CoderPad 环境，要求代码最终真正跑通（与普通 Google 面不同）；每题约 20 分钟；建议刷 LeetCode Google-tag 最新 top 50；明确限制/禁止 AI 编程助手。级别（L3/L4/L5）全程不告知，过 loop 后才定。ML 轮被普遍称为整个流程最难部分。

来源: <https://igotanoffer.com/en/advice/google-deepmind-research-engineer-interview>

### 【重要情报】2025 起 RE 岗 recruiter 确认取消 maths/stats quiz，保留 ML/AI quiz + coding
*unknown · 频率: 2 条独立报告（2023、2025） · 2025-03*

Blind 2025-03-01（Meta 员工，10 天后面 GDM RE）：“Recruiter confirmed that there is no maths / stats quiz anymore”，评估组件为 ML/AI quiz 和 coding 轮。佐证：Blind 2023-06 帖（kd1tfu6b，ex-Googler PhD）评论区称“仍会问一些 math/stats 问题，但与前几年 2 小时考试式格式不同”——即 quiz 逐年软化：2 小时笔试 → 对话式快问快答 → （2025 部分岗位）并入 ML/AI 轮。备考含义：数学不再单独设轮，但会揉进 ML fundamentals 轮里问直觉与推导。

来源: <https://www.teamblind.com/post/deepmind-re-interviews-z8txzan3>

### Research Scientist 2025 实报 loop：ML 面 + coding(1M+1H) + paper presentation + senior scientist chat
*hard · 频率: multiple reports (2025) · 2025-05*

Glassdoor RS 页 2025-05 报告（原页 403，经搜索摘要还原）：4 轮——1) ML Interview；2) Coding interview（LC 风格，1 道 medium + 1 道 hard）；3) Paper presentation（自选一篇论文做 ~1 小时展示）；4) 与 senior scientist 对话。全程 1.5-2 个月。另一条 RS 报告：总计 7-9 轮（视候选人而定），每轮 1-3 名 scientist，考 leetcode 式题、AI fundamentals、Transformers、Finetuning、以及 Gemini/DeepSeek 等大模型的训练方法。RS 整体难度评分 3.2/5，平均 45-49 天，54% 正面体验。

**解法**: 对候选人（post-training 背景）：ML 面重点准备“从 pretraining 到 SFT 到 RLHF/RLAIF 的完整训练流程”并能对比 Gemini/DeepSeek(-R1/V3) 的技术路线（MoE、MLA、GRPO、蒸馏）。

来源: <https://www.glassdoor.com/Interview/Google-DeepMind-Research-Scientist-Interview-Questions-EI_IE1596815.0,15_KO16,34.htm>

### techinterview.org 2026：Research Scientist track 五类轮次拆解
*hard · 频率: 聚合指南 · 2026*

1) Paper Discussion 60min：讲自己近期论文，面试官“会狠戳假设、弱点与扩展”，跨领域可能有多场；2) Research Problem Framing 60min：开放问题的实验设计、指标选取、理论分析提案；3) ML Coding 60min：实现自定义 loss、attention 机制、采样例程或训练循环，几乎总是 unaided（禁 AI）；4) Math & Theory 60min：概率/线代/优化，覆盖 gradient flow、Bayesian inference、收敛性证明、信息论；5) Behavioral 45min：使命认同、科研协作、过往分歧。整体时间线 6-10 周，研究岗 8-12 周。

**解法**: ML coding 备考：numpy/torch 手写 MHA（含 mask、shape 管理）、top-p/top-k 采样、完整 training loop（zero_grad/backward/step/eval）。

来源: <https://www.techinterview.org/post/3233474918/deepmind-interview-process-2026/>

### RE 4 轮结构 + 各轮内容细节（Blind 2024-08，Snap 员工亲历）
*medium · 频率: single detailed report（与其他来源互洽） · 2024-08*

Amazon 候选人确认 RE loop：4 轮 = 2 coding + 1 ML system design + 1 ML fundamentals。Snap 员工（亲历者）细节：ML fundamentals 轮考“经典 ML（SVM、naive bayes、回归、树）+ 现代 ML（卷积、transformers、优化算法等）的基础问题”，数学很少；coding 轮一场是“typical leetcode (medium-hard)”，另一场考“software fundamentals：class design、multithreading、memory fundamentals 等”；并提醒“Don't sleep on the final hiring manager interview”。

**解法**: 第二场 coding 按 OOD+并发准备：设计类（LRU/限流器/线程安全队列）、GIL、进程 vs 线程、内存模型/引用计数。

来源: <https://www.teamblind.com/post/deepmind-research-engineer-interview-help-keaohhu8>

### RE loop = coding + math + ML 三类技术面（Blind 2023-11，亲历者）
*unknown · 频率: single report · 2023-11*

3 篇论文+1.5 YOE 候选人（Amazon/GS/AllenAI 实习）：recruiter 主动接触；第二阶段包含“a coding interview, math interview and ML interview”三场；自评“75% okay”；全程未被告知级别（L3 vs L4），佐证 GDM 定级不透明。此帖为此前 0J58GiRf 短链无法打开的原帖，已用 slug URL 恢复。

来源: <https://www.teamblind.com/post/research-engineer-interview-at-deepmind-0j58girf>

### Gordic Aleksa：DeepMind RE 全流程亲历 + 备考资源清单（Medium 长文）
*hard · 频率: 经典一手长文（社区广泛引用） · 2021-10*

2021 年被引荐入 GDM 的完整记录。流程：recruiter chat（判定 Applied vs Core）→ “the quiz”= 2 场 back-to-back 面试考 maths/stats/CS/ML 基础 → 1 场经典 SWE coding → Team Lead 面 → Senior Team Lead 面 → People & Culture 面。备考资源（quiz）：算法书 ~340 页（线性/非线性数据结构、排序、查找）、Mathematics for ML book（数学+经典 ML）、统计用 jbstatistics + StatQuest + Cambridge IB Statistics sheets 1-2；coding 用 CTCI 前 8 章。行为面真题：What do you like about DeepMind? / Why DeepMind and not some other company? / Tell me something about your favorite project；他还专门研读 AGI 相关论文以应对使命类问题。结局：挂在第 6 场 Senior Team Lead（反馈：显得对 research 比 engineering 更有热情，而岗位是 RE）→ 作为 technically strong 候选人被转到 Incubation/Applied 组重面，4 个 YES 拿 offer。教训：研究每位面试官的论文；RE 岗要强调工程热情。

来源: <https://gordicaleksa.medium.com/how-i-got-a-job-at-deepmind-as-a-research-engineer-without-a-machine-learning-degree-1a45f2a781de>

### 官方文档《Interviewing at Google DeepMind》PDF
*unknown · 频率: 官方文档 · unknown*

官方 6 页候选人指引（storage.googleapis.com/deepmind-media 托管）：面试通过 careers portal 排期；轮次含技术评估+文化契合；备考建议：研读 deepmind.google、Gemini 等产品、目标团队项目；面试日测试设备、准备无干扰环境、box breathing 呼吸法减压；技术环节 think aloud、用数据支撑成就；推荐 Google Interview Warmup 工具、DeepMind podcast/blog。无具体题目，但可作为官方流程与期望的权威出处。已下载至 /tmp/gdm_official.pdf。

来源: <https://storage.googleapis.com/deepmind-media/DeepMind.com/Assets/Docs/interviewing-at-google-deepmind.pdf>

### Data Scientist（Gemini/Quant Engineering）岗面试情报（Blind 2025-12 + 4dayweek）
*medium · 频率: 1 条 Blind 报告 + 1 份聚合指南 · 2025-12*

Blind 2025-12-31：GDM Data Scientist (Gemini) 岗（产品向，内部或称 Quant Engineering），TC $250K，recruiter 提供信息极少；候选人推测考察：统计（A/B testing、因果推断）、ML（线性回归、随机森林）、coding（SQL+Python）、进阶 AI（agents、LLMs、多模态，可能以 case study 形式）；Google 员工评论称与 DSR（前 Quantitative Analyst）岗结构类似。4dayweek.io：GDM DS 流程 4-6 周 5 阶段（recruiter → 2+ 轮 coding 45-90min → 2+ 轮 ML 面 45-90min → HM 面 60-90min → culture fit 60-90min），难度 3.2/5；样题 15 条：特征选择方法、超参调优、推荐系统构建步骤、模型评估、L1 vs L2、梯度下降及变体、类别不平衡、时间序列分析步骤、缺失值处理、CNN 原理、bias-variance trade-off 等。

来源: <https://www.teamblind.com/post/interview-tips-for-google-deepmind-data-scientist-x0xpjsi2>

### Glassdoor RE 页聚合数据与其余零散真题（distributed system / NN from scratch / research paper）
*hard · 频率: 聚合（多条 review） · 2024-2026*

Glassdoor（原页 403，搜索摘要还原）：RE 面试整体：先讲自己的 research papers，然后 coding + deep learning 理论技术问题；DSA 为 medium/hard LC 级，虚拟面试。零散真题：Implement a distributed system to process large-scale data efficiently；Design and implement a neural network from scratch in Python；Describe a research paper you implemented；ML fundamentals 覆盖 loss functions、classification vs regression、降维、正则化、CNN、RL、模型训练。RE 难度 3.3-3.4/5，平均 46 天，整体 66.3% 正面 / 难度 3.23（255 题 226 条 review，login 墙内）。另 QTN_8056849：“一上来就直接问 LC 式 coding 题”。

**解法**: NN from scratch：numpy 实现 2 层 MLP——forward、BCE/softmax-CE loss、手推 backward、SGD 循环，20 分钟内写完的版本要提前练熟。

来源: <https://www.glassdoor.com/Interview/Google-DeepMind-Research-Engineer-Interview-Questions-EI_IE1596815.0,15_KO16,33.htm>

### Blind 零散 2025-2026 SWE/移动岗情报汇总（低信息量帖）
*unknown · 频率: 4 条低信息量报告 · 2025-10 ~ 2026-03*

1) SWE（Bloomberg 候选人，2025-10，notaegsj）：唯一实质评论“yeah, leetcode medium”。2) Mobile Engineer（Meta 候选人，2026-03，0wz2srt8）：Meta 员工评论“The bar is higher than the bar at Meta. Grind hard algorithms and mobile system design”。3) 2026-01 mj3zcuiy：确认 DeepMind 面试流程与 Google 分开。4) 2026-02 Waymo/DM loop（5mcv3okv）：ML infra 候选人称 DM 可走普通 Google 轮+后置 team match（无人证实）。这些帖无具体题目，但反映 2025-2026 SWE 侧 bar 与流程认知。

来源: <https://www.teamblind.com/post/deepmind-swe-interview-experience-0wz2srt8>

### DeepMind Research Engineer 全流程挂经 (RE, PhD, 2025-09)
*hard · 频率: single report (2025 唯一确认的 RE 全流程挂经帖) · 2025-09*

岗位: Google DeepMind Research Engineer (RE). 楼主背景: 'NG很一般的PhD + 没啥强工业经验'（NG=new grad/应届），走完全流程后被拒（'铁挂经验'）。可确认的流程/轮次: (1) HR电面 —— 聊签证情况 / 毕业情况 / 对 DeepMind 的看法等 general 问题; (2) ML 电面/讨论 —— 英文摘要标注为 'ML discussion'（正文在188积分墙后，具体题未取到）; (3) Coding 电面/轮次 —— 楼主给出的经验教训: 'corner/edge cases 要能够做到对答如流; Coding 至少要 3-4 个月狂刷, 楼主只用了一周高强度来刷, 之前面试别家太顺利以至于掉以轻心, 只刷了些高频题' —— 暗示挂在 coding 准备不足。这是当前唯一确认的 2025 年 GDM RE 全流程一手挂经帖。正文核心内容被 1point3acres 188 积分隐藏，以上为可见摘要 (Startpage/英文翻译摘要旁路获取)。

**解法**: 复盘教训(楼主原话)：DeepMind RE 的 coding 门槛不低，需 3-4 个月系统刷题而非临时抱佛脚高频题；ML 轮要对基础八股/corner case 对答如流。

来源: <https://www.1point3acres.com/bbs/thread-1147017-1-1.html>

### DeepMind ML 全流程面筋 + Offer (2025-09 面试, 时间线明确)
*unknown · 频率: single report · 2025-09*

岗位: DeepMind Machine Learning 全职 (英文翻译摘要: 'DeepMind machine learning interview process ... offer status for a full-time role'). 楼主吐槽 '许久没在地里看到 GDM 的 dp 了' 且 '按着地里五六年前的面筋准备的一点都没用上'。明确时间线: 9/15 HR call (介绍面试流程/介绍公司/各种介绍) → 9/23 SD (system design 轮) → 9/24 Coding (页面显示 'Coding non-...' 疑为 non-standard/non-leetcode，正文被 188 积分墙截断)。英文摘要提到内容覆盖 HR calls / coding / project discussions / offer。这是 2025 年 GDM 少见的带 offer 结果的全流程帖。具体 SD 与 coding 题干在积分墙后未取到。

**解法**: 推断(基于同期 GDM ML 帖 1141654/1141656/1141657 组合): SD 轮很可能是 ML system/ML design 类而非通用分布式系统; coding 轮为 non-standard leetcode（如实现 generator / 概率分布类）。建议按 2025 新帖而非 5-6 年前老面筋准备。

来源: <https://www.1point3acres.com/bbs/thread-1155040-1-1.html>

### GDM RS Intern 技术电面结构 (research 也会八股, 2025-10)
*medium · 频率: single report · 2025-10*

岗位: Google DeepMind RS intern (gdm RS intern)。楼主提醒: '给其他面 research 家/组的 PhD 提个醒——说是聊 research, 有时候还是会八股'。电面时间分配被规划为: 25 分钟八股 (fundamentals) + 5 分钟讲我的 research + 20 分钟 AI system design 八股 (详细问)。英文摘要: 'technical phone interview including research discussion and AI system design questions'。这颠覆了 'RS intern 只聊 research' 的预期。

**解法**: 推断: '八股' 指 ML 基础快问快答 (loss/optimizer/正则/attention/transformer 等); 'AI system design 八股' 指 LLM/训练系统设计的结构化提问。备考不能只准备 research pitch，要把 ML 基础和 AI system design 当成主要考点。

来源: <https://www.1point3acres.com/bbs/thread-1152313-1-1.html>

### GDM Student Researcher (SR) 项目/流程解密 (2025-11)
*unknown · 频率: single report · 2025-11*

岗位: Google DeepMind Student Researcher (俗称 gdm SR)。信息性帖子(非题目): 对 early PhD '还是很香的'; 现在也开放本科和硕士生岗位; 本质上是 '临时科研 agent', 和暑期实习不一样——一般没有固定实习期结构。英文摘要: 'Google GDM Student Researcher internship details, application tips, and interview insights for early PhD and other candidates in ML'。适合了解 SR 与正式 intern/RS 的区别及申请路径。正文细节在积分墙后。

来源: <https://www.1point3acres.com/bbs/thread-1153821-1-1.html>

### DeepMind London Research Scientist 面筋 (2024-01)
*unknown · 频率: single report · 2024-01*

岗位: DeepMind London Research Scientist (RS)。楼主 2023 下半年网申 DeepMind 伦敦多个岗位, 约不到一个月获面试(自评因背景匹配)。英文摘要: 'firsthand account of DeepMind London Research Scientist interview rounds and preparation materials for ML positions'。这是 2024 年初的 RS 全流程帖(轮次结构与备考材料), 正文细节在积分墙后。可作为 RS 岗流程基线参考。

来源: <https://www.1point3acres.com/bbs/thread-1041792-1-1.html>

### DeepMind London RE 两大轮流程 (2022, 历史基线)
*hard · 频率: 历史帖 (2022), 与其他老 RE 帖 878129/837817/825115 互为佐证 · 2022-08*

岗位: DeepMind London Research Engineer (RE)。楼主(recruiter 联系): 'RE 是两大轮面试。第一大轮是三个一个小时的面试, 分别是 math, ML, cs+coding'(第二大轮细节被截断)。指出 RE 与 RS 流程可能不同。这是较早(2022)但结构清晰的 RE 流程基线: 第一大轮 = 3×1hr (数学 / 机器学习 / CS+coding)。注意 2025 帖楼主反馈老面筋已不完全适用, 仅作对照。

**解法**: 对照 2025: math+ML+coding 的三合一大轮结构可能仍在, 但 2025 RE 挂经楼主强调 coding 难度上升、需长期刷题, 说明标准比 2022 更高。

来源: <https://www.1point3acres.com/bbs/thread-918169-1-1.html>

### DeepMind ML Research Engineer 终轮 (三轮结构, 2022, 历史基线)
*hard · 频率: 历史帖 (2022) · 2022-01*

岗位: DeepMind ML Research Engineer。楼主: '正式面试有三轮: 一轮 coding, 一轮 ML, 第三轮 Hiring manager + BQ'。前两轮(coding/ML)之前另发过面经; 第三轮时间 12/2、12/3。可确认 RE 三轮结构: Coding → ML → HM+BQ。2022 历史帖, 与 2025 帖对照可见流程主干延续(coding/ML/HM)。

**解法**: 备考三轮: coding(见需长期刷题的 2025 反馈), ML(基础八股+研究讨论), HM+BQ(动机/项目/协作/最自豪项目, 见 1141654)。

来源: <https://www.1point3acres.com/bbs/thread-837817-1-1.html>

### DeepMind Research Engineer/Scientist 入口难度（Reddit 补充数据点）：简历关极难、quant 向岗位考统计概率而非 leetcode
*unknown · 频率: 2 threads · 2026-03*

r/cscareerquestions + r/MachineLearning 双发帖（2026-03）：新毕业生（数学/物理，有 string theory 引用论文）问 DeepMind RE 多难进。关键评论：'即使 top5 PhD 毕业、无 referral，~10 人无一通过简历筛到 HM'；infra 岗比 research 岗好进；发帖人自己的 quant-research 面试经验是'没有 leetcode，主要是 stats 和 probability'；Anthropic Fellow OA 后即挂。r/csMajors AI research intern 帖（2026-05）补充：顶级 lab research intern 面'不考 leetcode，考 conceptual ML + 简历项目深挖'。（GDM 主体面经已由前次 gdm:english 爬取覆盖，此为增量。）

来源: <https://www.reddit.com/r/cscareerquestions/comments/1ry1h4c/how_hard_is_it_to_get_research_engineer_role_at/>

## Coding 题

### Implement Trie for prefix matching（LC 208）
*medium · 频率: very high（多来源反复出现，含此前已确认） · 2025*

RE coding 轮真题：实现支持前缀匹配的 Trie（insert / search / startsWith）。CoderPad 上要求跑通。IGotAnOffer 基于 Glassdoor 最新 RE coding 报告将其列为 GDM 最常考 coding topic 之首。

**解法**: 节点用 dict children + is_end 标志；三个操作均 O(L)。注意 startsWith 与 search 只差 is_end 判断。

来源: <https://igotanoffer.com/en/advice/google-deepmind-research-engineer-interview#q1>

### Reported RE coding questions: Trie prefix matching, Snapshot Array, Manhattan-distance meeting point, add two numbers as linked lists
*medium · 频率: high (multiple aggregated reports) · 2025*

Coding examples reported for DeepMind research engineer coding screens (via IGotAnOffer's collection of candidate reports): (1) Implement a Trie supporting insert and prefix matching; (2) Implement a Snapshot Array supporting a pre-defined interface (LeetCode 1146: set(idx,val), snap(), get(idx,snap_id)); (3) A group of people want to meet; minimize total travel distance where distance is Manhattan distance (LeetCode 296 Best Meeting Point); (4) Add two non-negative integers represented as linked lists with digits in reverse order (LeetCode 2). Level: LC medium/hard, Google-style; code must actually run by end of round; expect several follow-ups per problem and complexity analysis.

**解法**: Snapshot Array: per-index list of (snap_id, value) pairs + binary search on get — O(log S) get, O(1) amortized set. Best Meeting Point: Manhattan distance decomposes by dimension; optimal point is (median of xs, median of ys); collect coordinates and sum |xi−median|. Trie: dict-of-dicts or array-of-26 children with is_word flag. Add-two-numbers: carry propagation while either list or carry remains.

来源: <https://igotanoffer.com/en/advice/google-deepmind-research-engineer-interview>

### Google/DeepMind · Coding 题库总览（46 题，站内 DeepMind 归入 Google）
*hard · 频率: 高 — Google 页面共 46 道 coding（OA/Screening/Onsite 混合），是三家中题量最大的 · 2024-12 至 2026-06*

重要说明：Hack2Hire 后端无独立 DeepMind 枚举，DeepMind 归到 GOOGLE；/companies/deepmind/ 与 /companies/google-deepmind/ 页面为空壳，实际题库看 /companies/google/。Google coding 全 46 题按主题分布：DP/记忆化(Ball Picking Game、Subset Sum Equals K、Max Fly Distance、Color a Row of Houses、Fill Equation with Operators)、图/BFS/DFS(Keyboard Jump Challenge、Maximum Building Height、Maximum Island Perimeter、Find Valid Tile Moves、Dual Car Destinations)、树(Max Sum Between Leaf Nodes、Largest Common BST Value、N-ary Tree Leaf Node Removal、Minimum Distance in N-ary Tree、Build Binary Tree From Character Counts)、字符串/解析(Simplify Expression、Evaluate String Expression、Split Text into Lines、Grep With Context Lines、String Tokenization/Trie、Highway Checkpoint)、滑窗/双指针/前缀和(Bank Service Maximization、Windowed Average excluding Largest K、Count Distinct Elements in Window、Find K Distinct Element Subarray、Find Common Free Days、Merge Two Interval Lists、Game Machine)、设计(Design Unix Find Command、URL Router Design、Search History System、MinMax Queue、Count Intervals Covering Point、Subarray-First Iterator、Winner in a Dot Grid Game)、贪心(Minimum Coins to Form All Amounts、Find Greatest Triple、Find Optimal Moves、Cake Order Fulfillment Check、Rearrange Houses in Neighborhoods)、二分(Dependency 类、Find Median In Large Array)、其他(Date Validator、Employee Shift Timeline Table、ATM Queue、Kth Greatest in Growing Prefix、Group Elements by Shared Properties/Union-Find)。每题 practice URL：.../google/coding-questions/{postId}/practice。

**解法**: 多数题是知名 LeetCode 变体（站内明确标注：224 Basic Calculator→Evaluate String Expression、282→Fill Equation、486→Ball Picking、39→Subset Sum、56→Merge Intervals、200→Max Island Perimeter、236→Min Distance N-ary、253→Count Intervals、703→Kth Greatest、992→K Distinct、366→N-ary Leaf Removal、134 Gas Station→Game Machine）。Google 更偏经典算法+清晰复杂度分析，与 OpenAI/Anthropic 的 novel design 题不同。

来源: <https://www.hack2hire.com/question-bank/companies/google/coding-questions>

### Google/DeepMind · 系统类 Coding 高值题（Design Unix Find / URL Router / Search History / MinMax Queue / Grep）
*hard · 频率: 高 — Google 频率：Design Unix Find Command 10(Onsite)、Search History System 7(Onsite)、URL Router Design (Google 4/Atlassian 6)、Grep With Context Lines 7、MinMax Queue (Google 2/Bloomberg 7) · 2025-04 至 2026-04*

Google 偏爱的'设计型' coding（practice URL .../google/coding-questions/{id}/practice）：(1) Design Unix Find Command [Hard, id 683e7b308d3dfb7c9bd756aa]：内存文件系统 + add files(带 size/extension) + 按 size/extension/name-prefix 过滤递归搜索；给定 abstract Filter 类需实现三种 filter；提示：文件系统建为通用树 + map 存 children，HashSet 存绝对路径做 O(1) 去重，Filter 用策略模式遵循开闭原则。(2) URL Router Design [Hard, id 68fa76eb0fa32e4d82f4fc1a]：注册 URL 模式→handler，支持精确匹配 + 任意段 '*' 通配，查询返回最具体匹配（通配符最少），无匹配返回空串；提示：按段拆分 + Trie，查询时遍历所有可行分支含通配跳转、记录通配最少的匹配。(3) Search History System [Hard, id 678878d0402dc47b67a14945]：容量受限，add(term) 重复项移到最前，取最近 k 个 unique；提示：hash map + 双向链表（LRU）。(4) MinMax Queue [Medium, id 68d84f7eae12841706c1fc80]：队列 + O(1) 取 min/max；提示：两个辅助单调 deque。(5) Grep With Context Lines [Medium, id 69c2f1cc21f6ab422696534e]：返回匹配行 + 前后 linesAround 上下文行（大小写敏感子串匹配、去重保序）；提示：差分数组 + 前缀和标记落在任意上下文窗口的行索引。

**解法**: 这几道最贴近'工具/系统'风格，对 RE 岗最有区分度。URL Router/Unix Find 建议手写 Trie 与树遍历；Search History=LRU 变体；MinMax Queue=单调队列经典。

来源: <https://www.hack2hire.com/question-bank/companies/google/coding-questions/683e7b308d3dfb7c9bd756aa/practice>

### Implement Snapshot Array（LC 1146）
*medium · 频率: high（多来源确认） · 2025*

RE coding 轮真题：实现 SnapshotArray，支持预定义接口 set(index,val)、snap() 返回 snap_id、get(index,snap_id)。要求处理大量 snap 时的空间效率。

**解法**: 每个 index 维护 append-only 的 (snap_id, value) 列表；get 时对该列表按 snap_id 二分找 <= snap_id 的最新值；snap() O(1)，get O(log k)。

来源: <https://igotanoffer.com/en/advice/google-deepmind-research-engineer-interview#q1>

### Best Meeting Point：曼哈顿距离最小总和会面点（LC 296 hard）
*hard · 频率: high（多来源确认） · 2025*

RE coding 轮真题：2D 网格中若干个 1 表示每个人的家，求一点使所有人曼哈顿距离之和最小，distance(p1,p2)=|p2.x-p1.x|+|p2.y-p1.y|。

**解法**: 曼哈顿距离 x、y 可分离：分别收集所有行坐标（天然有序）和列坐标（按列扫描保证有序），最优点取各自中位数；再线性求和，整体 O(mn)，无需排序。

来源: <https://igotanoffer.com/en/advice/google-deepmind-research-engineer-interview#q1>

### Add Two Numbers：逆序链表相加（LC 2）
*medium · 频率: high（多来源确认） · 2025*

RE coding 轮真题：两个非空链表逆序存两个非负整数，逐位相加返回链表。即此前记录的“linked-list 题”的具体题面确认。

**解法**: 双指针同步走+进位变量，dummy head；注意最后 carry=1 要补节点。follow-up 常问正序存储版本（用栈）。

来源: <https://igotanoffer.com/en/advice/google-deepmind-research-engineer-interview#q1>

### r/leetcode 2026-05: RE London (Gemini-adjacent) coding rounds — modified LC mediums with probability twists; Dijkstra framing
*medium · 频率: single detailed report · 2026-05*

Candidate (senior SWE, GenAI/agents, 1 ACL first-author paper, master's, no PhD) passed technical rounds after 3 weeks of Blind-75 prep. Both coding interviews used 'modified LeetCode Medium with some probability twist' — both problems involved probability. Interview 1: coded optimal solution, ran it, several basic follow-ups, then one hard follow-up where a wrong assumption about the problem definition led to an incorrect solution; described correct suboptimal logic after a nudge. Interview 2: problem reduced to probability + graph shortest-path — recognized Dijkstra framing quickly, coded optimal solution using placeholder functions (code never ran, minor bugs tolerated), then in-depth math discussion; gave wrong complexity for Dijkstra and even basic heap ops but still passed. Interviewers nudge a lot if you narrate clearly. Found the problems 'significantly easier and more intuitive than most mediums.' Outcome: passed 2 coding + 1 ML, then 3 additional experience/team interviews — another candidate was selected.

**解法**: Probability-on-graph problems typically become shortest/most-probable path: maximize product of edge probabilities = minimize sum of −log p, so run Dijkstra (or directly use max-heap variant keeping max probability per node, cf. LC 1514 Path with Maximum Probability). Know heap op complexities: push/pop O(log n), Dijkstra O((V+E) log V) with binary heap. (my inference)

来源: <https://old.reddit.com/r/leetcode/comments/1tfu311/how_i_passed_deepmind_technical_rounds_with_3/>

### r/leetcode 2025-05: DeepMind SWE coding rounds treated as Google-style; prep = Google tagged questions (graphs/trees)
*medium · 频率: single post (corroborates pattern) · 2025-05*

Candidate (6 YOE applied scientist) with a DeepMind Software Engineer interview prepared ~60 Google-tagged questions focused on graphs and trees, asking whether GDM coding is like Google's. No substantive answers in thread, but consistent with all other reports: GDM coding bar ≈ Google (LC medium/hard, Google internal question bank per Blind), with the delta being that code must execute. Useful as corroboration that Google-tagged LeetCode lists (graphs/trees emphasis) are the standard prep for GDM coding screens.

来源: <https://old.reddit.com/r/leetcode/comments/1kehvqu/i_have_deepmind_software_interview_for_tomorrow_i/>

### GDM RE 电面：两轮背靠背 coding（recruiter LinkedIn 主动联系非科班 MLE）
*unknown · 频率: single report（outreach 模式 3+ 帖印证） · 2021-11*

《DeepMind research engineer电面》2021-11-13。原文首段："非科班，MLE有2年多经验，不在大厂，误打误撞被DeepMind的recruiter在linkedin上联系，面试research engineer岗位。……电面两轮背靠背。两个面试官感觉都[很nice]……"（具体题目积分墙隐藏，2 页帖）。要点：GDM 大量通过 recruiter 在 LinkedIn 主动 outreach（825115、918169 同样如此），电面为两轮连续背靠背。

来源: <https://www.1point3acres.com/bbs/thread-819265-2-1.html>

### GDM SWE Intern（London Platform team）technical onsite：CS 理论轮 + Coding 轮分开考
*unknown · 频率: 2 reports (938777, 467663) · 2022-10*

《Deepmind SWE intern 2022 technical店面》2022-10-21。原文："london的Platform team给了technical onsite 分为First Technical Interview (Computer Science) b. Second Technical Interview (Coding)"。即 GDM SWE 轨也保留『CS 概念口头轮』+『写码轮』分离的结构（与 RE quiz 的 CS section 一脉相承），区别于 Google SWE 全部轮次都是写码。另有 2019 年《Deepmind SDE Intern 三轮面试挂经》（thread-467663）佐证 SDE 轨为三轮。

来源: <https://www.1point3acres.com/bbs/thread-938777-1-1.html>

### 2025 求米帖（数科版）附带：楼主自己整理的谷歌系 coding 高频 Top 30（按出现频率排序，适用于 GDM coding 轮按 Google 题库准备的策略）
*medium · 频率: single report · 2025-03*

《Deepmind面试求米》2025-03-09，数科面经版。楼主将面 DeepMind（评论提到 GDM 数据科学岗多为 12 个月 contract）。正文积分墙（188 分），但楼主在评论区贴出自己统计的 Google 高频题 Top30（含频次）：Find Leaves of Binary Tree(75)、Evaluate Reverse Polish Notation(73)、Two Sum(44)、Snapshot Array(36)、Stock Price Fluctuation(30)、Minimum Time Difference(30)、Text Justification(24)、Meeting Rooms II(22)、Happy Number(22)、Logger Rate Limiter(22)、Number of Islands(21)、Max Points from Cards(17)、Subarray Sum Equals K(15)、Number of Matching Subsequences(15)、Median of Two Sorted Arrays(14)、Student Attendance Record II(14)、Find Original Array From Doubled Array(14)、Find Duplicate Subtrees(13)、Longest Substring Without Repeating(13)、Longest Palindromic Substring(12)、Best Time to Buy and Sell Stock(12)、Longest Common Prefix(12)、Bulls and Cows(12)、Basic Calculator(12)、Time to Inform All Employees(11)、Tic Tac Toe Winner(11)、Course Schedule II(11)、Maximum Subarray(11)、Insert Intervals(11)、Palindrome Number(11)。另一条重要评论："感觉地里应该找不到gdm的面筋"→"相当赞同 去找CS顶尖校的那群PhD问绝对问得到"——1p3a 社区自认 GDM 面经沉淀极少。全文见 Wayback：http://web.archive.org/web/20250405164855/https://www.1point3acres.com/bbs/thread-1116355-1-1.html

**解法**: 该清单是 Google 通用高频题非 GDM 专属；GDM coding 轮风格接近 Google（LC medium 为主+现场写可运行代码），用此清单打底合理（我的判断）。

来源: <https://www.1point3acres.com/bbs/thread-1116355-1-1.html>

### 【新增真题】DFS 题 + 贪心刷栅栏最少笔刷数（Glassdoor QTN_8409177）
*medium · 频率: single report · 2024~2025（QTN id 较新）*

一场 GDM coding 面（报告地点 London/Bengaluru）包含两题：一道 DFS 题 + 一道贪心题“用最少的 strokes 刷完栅栏”（经典 painter's partition/fence painting 变体：每一笔可以沿水平方向连续刷一段等高区域，或垂直刷完一块木板，求覆盖给定高度数组的最少笔刷数，类似 LC 1526 的变形）。Glassdoor 原页面 403，题面来自搜索摘要。

**解法**: （我的推断）分治+贪心：solve(l,r,base)=min(r-l+1（全部竖刷）, minH-base + Σ solve(高于 minH 的每个连续子段)）；等价于 LC 1526 的一遍扫描解法 ans=h[0]+Σmax(0,h[i]-h[i-1])（当只允许水平刷时），面试中先给分治再优化到 O(n)。

来源: <https://www.glassdoor.com/Interview/DFS-question-and-greedy-question-about-painting-fence-with-min-number-of-strokes-QTN_8409177.htm>

### 【新增真题】在 Jupyter notebook 里解 hackerrank 式 Python 题（Glassdoor QTN_3268927）
*medium · 频率: single report（但 notebook/可执行环境是 GDM 普遍格式） · unknown*

RE 面试真题报告：“Solve a hackerrank-esque python problem in a Jupyter notebook”——不是白板 LC，而是在 notebook 环境里写可运行的 Python（偏数据处理/实现类），需要真正执行验证。与“DeepMind 要求代码跑通”的多方说法一致。

**解法**: 练习：在 notebook 中边写边测、用小样例断言；熟悉 pandas/numpy 常用操作与纯 Python 实现。

来源: <https://www.glassdoor.com/Interview/Solve-a-hackerrank-esque-python-problem-in-a-Jupyter-notebook-QTN_3268927.htm>

### 【新增真题】随机数生成类 LC medium（live coding 轮）
*medium · 频率: 2 条独立报告（含此前已确认的概率变体） · 2025*

Glassdoor 摘要：某场 GDM live coding 轮被问“与随机数生成相关的 medium 难度题”。与此前确认的“概率变体 LC medium”相互印证——GDM coding 轮存在概率/随机化题型。

**解法**: （我的推断）高频形态：rand7 由 rand10 生成（拒绝采样，证明期望调用次数）；LC 528 按权重随机选择（前缀和+二分）；LC 382 蓄水池采样。准备这三类并会推导正确性。

来源: <https://www.glassdoor.com/Interview/Google-DeepMind-Research-Scientist-Interview-Questions-EI_IE1596815.0,15_KO16,34.htm>

### Coding 轮节奏基准：37 分钟完成并测试通过 2 题（Blind 2021 被拒者复盘）
*hard · 频率: single report · 2021-07*

RE loop 第 4 轮 coding：“2 questions in 37 minutes complete + tested”，两题都写完且过测试用例，但把图算法复杂度说成 O(N)（应为 O(V+E)）成为挂点之一；另一挂点是没听懂面试官问题也不 clarify。前一轮（第 3 轮 research）考 CS 基础+概率统计+数学+ML/DL/RL，备考用了 David Silver RL lectures 4-8 和论文。评论区 Google 员工称“多数从 Google 内部转 DeepMind 的人也挂”。

**解法**: 教训：图/树题复杂度必须用 V、E 表述；不确定题意立即 clarify；每题预算 ~18 分钟并留测试时间。

来源: <https://www.teamblind.com/post/got-rejected-by-deepmind-lwftrbpv>

### Google DeepMind Android Contractor Onsite (算法/DFS + Gemini app 系统设计, 2025-11)
*medium · 频率: single report · 2025-11*

岗位: 谷歌 DeepMind 安卓 (Android) Contractor, Onsite。英文摘要明确考点: 'algorithms, DFS challenges, and Gemini app system design'——即 (1) 算法轮含 DFS 类题; (2) 系统设计轮 = 设计一个 Gemini app。这是 GDM 侧偏工程/contractor 的面试，区别于 RE/RS 研究岗。具体题干在积分墙后。

**解法**: 推断: DFS 类题准备图/树遍历、连通分量、回溯; 'Gemini app system design' 准备移动端 LLM 应用架构 (客户端/服务端流式响应、鉴权、缓存、多模态输入、限流、隐私)。

来源: <https://www.1point3acres.com/bbs/thread-1154955-1-1.html>

### Gemini Coding 面: 栅栏刷漆最少笔画数 (Minimum Brush Strokes to Paint Fence, 2026-04)
*medium · 频率: single report (2026 首个 Gemini coding 题) · 2026-04*

岗位: Google Gemini, 技术电面 coding。楼主: '地里很少见 Gemini coding 题, 贡献一道'。题目(据英文翻译标题/摘要): 给定一个栅栏(fence)的高度/形状, 求把它涂满所需的最少刷子笔画数 (minimum brush strokes)——两种刷法: 竖刷 (vertical, 一次刷一列) 和 横刷 (horizontal, 一次刷一段连续等高区域)。要求返回最小笔画数。正文完整题干被作者隐藏 (需加米)。

**解法**: 推断解法(经典 '刷墙/栅栏最少笔画' 分治): 设 heights[l..r], base 为已刷到的高度。答案 = min( 全部竖刷 = (r-l+1)-列数已刷, 或 先横刷该段最矮部分 (min_h - base) 笔, 再在高于 min_h 的若干子段递归 )。即 solve(l,r,base)= min(r-l+1, (min_h-base) + Σ solve(子段)); 在最矮列处分裂递归。O(n^2) 朴素或用线段树求区间最小做到 O(n log n)。等价于 LeetCode 'Strange Printer'/直方图涂色思路。

来源: <https://www.1point3acres.com/bbs/thread-1174769-1-1.html>

### DeepMind Coding 面: 实现 Python generator + 单元测试 (非常规 leetcode, 2025-08)
*easy · 频率: 1 (2025-08 同一套 GDM ML 面) · 2025-08*

岗位: Google DeepMind ML Engineering, Coding 轮。楼主: '非常规 leetcode 题, 非常幸运遇到比较简单的题'。题目 a: 给一个 list input, 要求写一个 Python generator, 可以 generate list 里的数字, 并且写 unit tests; 需要考虑 probability distribution 和 corner cases (英文摘要: 'Python generator tasks and unit testing. Focus on probability distribution and corner cases')。(后续小题 b... 被积分墙截断)。考察工程/测试素养而非纯算法。

**解法**: 推断: 若是 '按给定概率/权重从 list 采样的 generator', 用累积分布 + bisect (或 random.choices) 实现 weighted sampling; generator 用 yield 无限/有限产出。unit tests 覆盖: 空 list、单元素、重复值、权重和不为1的归一化、大样本频率逼近期望分布 (统计检验)、非法输入。用 pytest / unittest。

来源: <https://www.1point3acres.com/bbs/thread-1141656-1-1.html>

### Google/DeepMind Coding: 硬币放置游戏 (coins placed/removed from a table, 2025-09)
*easy · 频率: single report · 2025-09*

关联岗位: Google/DeepMind 系 coding (帖子 '两道 easy 新人求加米', 2025-09-25, 与 RE 挂经同期出现)。题干(英文原题, 可见部分): 'A player is playing a game in which coins are placed on and removed from a table. The game may consist of multiple rounds. At the beginning...'(后续被积分墙截断)。属多轮硬币放置/移除的模拟或计数题。因原帖正文隐藏, 完整规则与输出定义未取全; 记录以备 GDM/Google coding 轮参考。

**解法**: 推断(信息不全): 多轮 place/remove 类题通常是模拟 + 计数/栈或差分统计每轮桌面硬币数或某种最大值。拿到完整题干前无法确定; 建议按 '逐轮维护当前集合 + 查询统计量' 的模拟思路准备。此为我的推断，非来源提供。

来源: <https://www.1point3acres.com/bbs/thread-1147017-1-1.html>

## ML Coding 题

### ML coding round content: implement attention/custom loss/sampling/training loop by hand, unaided
*medium · 频率: multiple sources · 2026*

Converging reports (techinterview.org 2026, Sundeep Teki, dataford, Reddit): DeepMind ML coding rounds ask candidates to implement ML primitives by hand rather than solve puzzles: custom loss functions, an attention mechanism / multi-head attention block, a sampling routine (e.g., top-k/nucleus/temperature), a small training loop, gradient descent for logistic regression, backprop for an MLP. Unaided (no AI tools). RS version is smaller-scope; RE version involves larger pipeline pieces. Also reported (interviewnode): 'Implement gradient descent for logistic regression', 'Design a hash map from scratch in Python'.

**解法**: Practice set: (1) scaled dot-product + MHA with masking in numpy (watch shape bugs, softmax stability via max-subtraction); (2) BCE/CE/focal loss with logits (log-sum-exp trick); (3) top-p sampling (sort, cumsum, renormalize); (4) minimal training loop with manual backprop for 2-layer MLP: dL/dW2 = h^T·(p−y) etc.; (5) logistic regression GD: w ← w − α·X^T(σ(Xw)−y)/n.

来源: <https://www.techinterview.org/post/3233474918/deepmind-interview-process-2026/>

### Logistic regression 实现题 + 1 道 hard LC（Blind 2024-10）
*hard · 频率: single report · 2024-10*

Blind 帖“Deepmind research engineer coding questions”中 Google 员工评论：他面 GDM 相关岗位被问了“logistic regression”（实现/推导）和“1 hard leetcode”。追问“是否要求现场跑通代码”无人回答。

**解法**: （我的推断）准备 numpy 手写 logistic regression：sigmoid、BCE loss、梯度 X^T(p-y)/n、训练循环、数值稳定（log-sum-exp / clip）；并能推导梯度。

来源: <https://www.teamblind.com/post/deepmind-research-engineer-coding-questions-cuqxxu8r>

### InterviewNode：GDM ML 面试样题（coding/理论/设计 verbatim）
*medium · 频率: 聚合指南（部分与其他来源重合） · 2025*

五阶段权重：简历筛 10% / 技术筛 20% / ML problem solving 30% / system design 20% / behavioral 20%。Coding：Implement gradient descent for logistic regression；Design a hash map from scratch using Python；Merge overlapping intervals。ML 理论：L1 vs L2 何时用；overfitting 及缓解；What is the intuition behind reinforcement learning?（RL 是 GDM 特色考点：policy gradients、Q-learning）。System design：Design a scalable recommendation system for YouTube videos；How would you scale an ML model to handle billions of queries per second?；Design a distributed pipeline for training a neural network on terabytes of data。Behavioral：跨学科协作、ML 模型偏见处理、失败项目复盘。

**解法**: merge intervals：按起点排序后线性合并 O(n log n)；hash map：数组+链地址/开放寻址、扩容 rehash、讨论 load factor。

来源: <https://www.interviewnode.com/post/google-deepmind-ml-interview-prep-what-to-expect-and-how-to-prepare>

## ML 理论

### Glassdoor RE math/ML quiz questions: convex functions, gradient descent, Newton's method, second-order methods, Bayes' formula
*medium · 频率: very high (recurring across Glassdoor, Blind, Reddit, IGotAnOffer) · 2024*

Reported verbatim on the Glassdoor DeepMind Research Engineer interview page: 'Why do we want convex functions?', 'What is gradient descent?', 'Describe Newton's method', 'What are second-order optimisation algorithms?', 'How can the 2nd derivative be used in an optimisation algorithm?', 'What is Bayes' Formula?'. These come from the ML/math fundamentals interview (the 'quiz'). Recruiters usually tell candidates in advance that maths and stats will be covered. Page stats: RE interview difficulty 3.3/5, 61% positive experience, avg 46 days to hire, ~18 RE interview reports. Direct page is bot-blocked (403) — content recovered via search snippets.

**解法**: Convexity: any local min is global; gradient descent has convergence guarantees (O(1/k) for convex, linear rate for strongly convex). Newton's method: x ← x − H⁻¹∇f, second-order Taylor approximation, quadratic local convergence but O(d³) Hessian inversion — motivates quasi-Newton (L-BFGS) and diagonal approximations (Adam as preconditioned SGD). Bayes: P(A|B)=P(B|A)P(A)/P(B); be ready for ball/urn-style application problems. (standard textbook answers)

来源: <https://www.glassdoor.com/Interview/Google-DeepMind-Research-Engineer-Interview-Questions-EI_IE1596815.0,15_KO16,33.htm>

### GDM 经典第二轮 Quiz：2 小时 Hangouts 四连考——数学/CS/统计/ML 各 30 分钟
*medium · 频率: very high（同格式 5+ 帖：540650/813950/942891/918169/825115） · 2019-03*

《DeepMind Research Engineer 面试经验分享》（2019，thread 540650）。流程：第一轮 casual conversation（非标准 BQ），聊研究兴趣、为什么来 DeepMind；第二轮为 quiz，通过 Google Hangouts 进行，覆盖四大块：Mathematics、Computer Science、Statistics、Machine Learning，总时长两小时，每块约 30 分钟。该 quiz 形式是 GDM 区别于 Google 普通 SWE 面试的标志性环节，在 813950（intern 版 1 小时精简 quiz：linear algebra + probability 为主的 statistics + ML 概念 + 代码阅读）、942891（数学题+code comprehension+基础 ML）、825115（Math&Statistics 1h + ML 1h）等帖中反复出现。

**解法**: 我的推断+多帖佐证的高频考点：线代（特征值/SVD/正定性/矩阵求导）、概率（贝叶斯、期望方差、常见分布、大数定律）、统计（假设检验、MLE/MAP、bias-variance）、CS（复杂度、数据结构、递归）、ML（过拟合与正则化、SVM/logistic/树模型原理、backprop、CNN/RNN 基础）。口头快答形式，重反应速度和第一性原理推导，不重写码。

来源: <https://www.1point3acres.com/bbs/interview/deepmind-machine-learning-540650.html>

### Quiz 考点全景：线代/概率/统计/CS 四领域（Glassdoor 多条报告）
*hard · 频率: very high（quiz 是 GDM 区别于 Google 的标志性环节，报告极多） · 2019-2024 各年报告*

QTN_2480984（RE）：“Linear algebra, probability theory, statistics and cs fundamental questions”。QTN_2186118：“四个领域的 quizzes，之后是一场 software engineering 面试和与 research engineering lead 的对话”。其他 Glassdoor 摘要补充的具体考点：Bayes rule、可逆矩阵（invertible matrices）、凸函数、梯度下降、gradient computation、KL divergence 的性质、采样算法、收敛性证明、数据结构、Python 与 C++ 对比。历史格式为 2 小时笔试式 quiz（CS/Math/ML/Stats 各一部分），后演变为 2 场 back-to-back 口头快问快答，2025 起部分岗位取消（见另条）。

**解法**: 复习清单：MML book（线代/概率/优化）、Bayes/共轭先验、MLE vs MAP、CLT、假设检验、KL/交叉熵性质、SGD 收敛条件、排序/查找/图算法复杂度。

来源: <https://www.glassdoor.com/Interview/Linear-algebra-probability-theory-statistics-and-cs-fundamental-questions-QTN_2480984.htm>

### ML fundamentals signature question: mathematical intuition for L1 vs L2 regularization sparsity
*medium · 频率: high (multiple sources) · 2023*

Reported on Blind and highlighted by IGotAnOffer as emblematic of DeepMind's ML fundamentals bar: it is NOT enough to say L1 produces sparse features — you must 'explain the intuition, in terms of how the gradients affect the weights in L1 to cause that sparsity.' Also seen as 'What is the difference between L1 and L2 regularization? When would you use each?'. DeepMind ML rounds systematically ask WHY, not just WHAT; every claim gets a first-principles follow-up.

**解法**: L1 gradient is constant magnitude λ·sign(w) regardless of |w|, so it keeps pushing small weights all the way to exactly 0 (and subgradient at 0 lets them stay there); L2 gradient 2λw shrinks proportionally, so updates vanish as w→0 and weights never reach exactly zero. Geometric view: L1 ball has corners on axes where the loss contour typically touches. Bayesian view: Laplace vs Gaussian prior.

来源: <https://www.teamblind.com/post/deepmind-research-engineer-interview-process-wp1gjgyb>

### Glassdoor RS loop: math + ML + coding/CS technical rounds; AI fundamentals, transformers, finetuning, Gemini/DeepSeek training approaches
*hard · 频率: high (13+ Glassdoor RS reviews) · 2025*

From Glassdoor DeepMind Research Scientist page (27 questions, 13 reviews; difficulty 3.2/5, avg 49 days): typical loop = HR chat → hiring manager chat → 3 technical interviews: math, ML, and coding/CS → interviews with several research scientists → program manager behavioral. Rounds with 1-3 scientists included 'leetcode style questions, AI fundamentals, Transformers, Finetuning, Training approach of large models like Gemini, Deepseek etc.' Other reports: basic maths, stats, ML, CS concepts; programming language basics and style; implement an algorithm in a language of your choice; linear algebra, calculus, algorithms, big-O, statistics + a coding challenge. One 2025 Cambridge RS report: explain your research projects in detail with follow-up questions, then technical questions about transformers, reinforcement learning, and LLM reasoning. ML fundamentals interviews covered optimization, regularization, loss functions, transformers, plus practical training and inference questions. ML system design for research roles described as 'more ML focused than system focused.'

**解法**: For 2025-26 loops expect LLM-era content: transformer architecture details, SFT/RLHF/DPO finetuning tradeoffs, MoE (DeepSeek/Gemini), RL for reasoning (GRPO/PPO), scaling laws, inference-time compute. Candidate's Meta post-training background maps directly. (my inference)

来源: <https://www.glassdoor.com/Interview/Google-DeepMind-Research-Scientist-Interview-Questions-EI_IE1596815.0,15_KO16,34.htm>

### r/leetcode 2026-05: RE ML fundamentals round — toy ML problem + binary classification loss + deep transformers/NLP + evaluation
*hard · 频率: single detailed report; topic mix corroborated by Glassdoor RS reports · 2026-05*

Same candidate's ML round (1 hour): asked to solve a toy ML problem and go very deep on fundamentals. Details: initially couldn't think of a solution and forgot which loss to use for binary classification (noted softmax over 2 classes ≈ sigmoid/BCE); eventually produced an unusual working solution ('first time I hear a solution like this' per interviewer). Then went 'very deep on NLP and transformers' (candidate reports no linear algebra beyond QKV in transformers, only basic DL, 'lots of transformers though'), finishing with a discussion of evaluation. Takeaway per candidate: 'it's a lot about the fundamentals and not so much about memorizing specific techniques and models.' Passed despite a disastrous first 30 minutes — recovery and reasoning mattered.

**解法**: Binary classification: sigmoid output + binary cross-entropy (equivalent to 2-class softmax + CE). Expect derivations: attention QKV mechanics, why scaling by sqrt(d_k), positional encodings, tokenization, decoding strategies, and eval methodology (held-out metrics, human eval, contamination). (my inference on likely probe areas)

来源: <https://old.reddit.com/r/leetcode/comments/1tfu311/how_i_passed_deepmind_technical_rounds_with_3/>

### r/MachineLearning 2026-01: topic list from a past GDM candidate — derive SGD/Newton-Raphson, Taylor expansion, covariance, floating point, information theory, ELBO
*medium · 频率: single thread, multiple corroborating commenters incl. GDM staff · 2026-01*

A commenter who previously interviewed at DeepMind lists what to review for the quantitative/ML rounds: 'a lot of linear algebra, basic optimisation (derive SGD or Newton-Raphson, Taylor expansion), basic probability, understanding of covariance, dot product and intuitive understanding of similarity metrics, precision, how numbers are stored, I would guess information theory (CE, KL, entropy etc)'. ML depth questions are tailored to your claimed expertise — for them it was deep learning (thorough understanding of training CNNs/transformers); they skipped RL entirely since it wasn't their area. Also: 'can you easily derive the ELBO' for graphical-model people. Same thread has current GDM staff confirming: publication bar 'it depends'; RE→RS transition is fluid internally once hired; recruiter relationships are the main interview channel. Also a Prepfully coach: technical rounds cover 'gradient descent variants, attention mechanisms, optimization theory — not just implementation but the math behind it', and behavioral genuinely matters (research collaboration, handling ambiguity).

**解法**: Drill: SGD derivation from empirical risk minimization; Newton-Raphson from 2nd-order Taylor; KL(p||q)=Σp log(p/q), CE = H(p)+KL; ELBO: log p(x) = E_q[log p(x,z)/q(z)] + KL(q||p(z|x)) ≥ ELBO; float32/bf16/fp16 layouts (sign/exponent/mantissa) and why bf16 preserves dynamic range for training.

来源: <https://old.reddit.com/r/MachineLearning/comments/1q2wiub/d_google_deepmind_research_engineerscientist/>

### Sundeep Teki 2026 cross-lab guide: DeepMind's rapid-fire fundamentals quiz fails industry veterans; core content areas
*hard · 频率: prep-site synthesis · 2026*

Guide covering OpenAI/Anthropic/DeepMind notes DeepMind uniquely 'consistently tests undergraduate-level fundamentals via a rapid-fire quiz round' and that 'candidates who have been in industry for years often fail the quiz round because they've forgotten formal definitions of linear algebra concepts they use implicitly every day. Reviewing textbooks is mandatory.' Content areas: (1) math/linear algebra — eigenvalues/eigenvectors, rank, singularity, SVD, PCA; (2) ML coding — implement Transformer / multi-head attention blocks, neural nets from scratch; (3) ML debugging — identify bugs in models that don't learn; (4) system design — distributed training (data/pipeline/tensor parallelism); (5) research discussion — paper analysis and extensions; (6) safety & ethics — alignment, responsible scaling. Overall vibe: 'PhD defense mixed with a rigorous engineering exam'; values 'research taste'. Sells a paid DeepMind-specific guide (JAX-native implementations, TPU-optimized training, 5-8 rounds, hiring committee decides, RS median TC $336-406K).

**解法**: Refresh formal definitions: eigendecomposition conditions, rank-nullity, positive definiteness, SVD vs eigendecomposition, PCA as variance-maximizing projection / low-rank approximation (Eckart-Young). Practice writing multi-head attention + AdamW + training loop from scratch in numpy/PyTorch/JAX within 30 min.

来源: <https://www.sundeepteki.org/advice/the-ultimate-ai-research-engineer-interview-guide-cracking-openai-anthropic-google-deepmind-top-ai-labs>

### Dataford RS guide question bank (ML fundamentals + research design)
*medium · 频率: prep-site question bank (partially candidate-sourced, unverified) · 2025*

Google DeepMind Research Scientist guide (dataford.io): process = HR screening → technical rounds (quiz-style + practical coding) → research discussions with senior staff/team leads, 3-5 weeks. Sample questions: derive backpropagation for a multi-layer perceptron; manage bias-variance tradeoff in deep networks; mathematical properties of a metric space; compare loss functions for classification vs regression; explain Bayes' theorem to non-technical stakeholders; CNN vs Transformer architectural differences; data-structure tradeoffs under memory constraints; concurrency in HPC; systematically debug an underperforming model; design real-time data ingestion for large-scale models; describe influential recent papers; scope a research experiment. Most-frequent tagged questions: 'Explain Transformer Architecture and Attention Mechanisms' (Hard), 'Supervised vs Unsupervised Learning' (Easy). Requirements listed: advanced Python, JAX/PyTorch/TF, strong math; nice-to-have: large-scale distributed training, C++, publications. STAR for research discussions.

来源: <https://dataford.io/interview-guides/google-deepmind/research-scientist>

### Educative 'Top 20 GDM questions' (editorial list — breadth checklist)
*easy · 频率: editorial/synthesized — treat as checklist, not reports · 2025*

Editorially compiled question list (NOT verified candidate reports, useful as breadth checklist). Coding/algorithms: explain time/space complexity of favorite sorting algorithm; implement a hash table from scratch; detect cycle in linked list; find duplicates in large dataset efficiently. AI/ML: supervised vs unsupervised; CNN advantages for images; how RL works + real-world example; GD vs SGD. System design: recommendation system for music streaming; scalable AI for autonomous vehicles (perception/prediction/planning); NoSQL vs SQL tradeoffs in AI systems; fault-tolerant AI application requirements. Research/theory: importance of MDPs in RL; overfitting and mitigation (L1/L2, dropout, cross-validation); how to evaluate model success (metrics + interpretability + efficiency); ethical considerations in AI research. Behavioral: collaborative problem-solving experience; handling team disagreements; a failed AI project and response; task prioritization across projects. Educative also describes phases: online assessments → technical interviews → research interviews (past projects, recent papers) → behavioral (teamwork, ethics, mission alignment).

来源: <https://www.educative.io/blog/google-deepmind-interview-questions>

### 4dayweek.io DeepMind data science interview: 5-stage process + 15 sample ML questions
*medium · 频率: prep-site synthesis · 2025*

Data-science-flavored but DeepMind-branded guide: process = recruiter screen (30-60 min, ~1 wk after application) → 2+ technical coding interviews (45-90 min each) → 2+ technical ML interviews (45-90 min) → hiring manager (60-90 min) → cultural fit (60-90 min); 4-6 weeks total; difficulty 3.2/5, 62% positive. Sample questions (likely editorial): feature selection methods; hyperparameter tuning process and significance; build a recommendation system with collaborative filtering; model performance assessment and key metrics; L1 vs L2 regularization in linear/logistic regression; gradient descent and its variants; handling imbalanced datasets; time series analysis steps; missing data imputation techniques; CNN working principles and CV applications; bias-variance tradeoff; feature selection/engineering in high-dimensional data; plus behaviorals (data-driven decision story; multidisciplinary team role). Notes interviewers are 'generally kind and supportive, though occasionally lacking deep subject expertise'; little post-interview feedback.

来源: <https://4dayweek.io/interview-process/deepmind-interviews>

### Informal LLM post-training probe from GDM-adjacent commenter: GRPO rollout assumptions
*hard · 频率: single informal exchange · 2026-01*

In the 2026-01 r/MachineLearning DeepMind thread, a commenter stress-tested an aspiring candidate with a post-training depth question of exactly the style GDM ML rounds favor (why-not-what): 'What is the assumption on the rollouts while doing GRPO?' — expected answer: GRPO replaces the critic with empirical statistics (mean/std) of rollout rewards per prompt, which requires rollouts to be IID samples from the behavior/old policy and enough of them for the advantage estimate to be reliable. Follow-up: 'How would you modify the optimization objective for independent but non-identical rollouts (e.g., rollouts from different models/prompts)?' — expected: adjust the importance-sampling denominator so each rollout's policy ratio uses the actual policy it was sampled from (pi_theta_old_i per source model), and rethink the group-normalized advantage across heterogeneous sources. Not a confirmed GDM interview question, but a realistic sample of the depth expected from a post-training candidate.

**解法**: Included above; also be ready to derive GRPO objective from PPO by substituting group-relative advantage Â_i=(r_i−mean(r))/std(r), and discuss bias introduced by std normalization and non-IID sampling.

来源: <https://old.reddit.com/r/MachineLearning/comments/1q2wiub/d_google_deepmind_research_engineerscientist/>

### GDM RE 第二轮 ML 面（背靠背 2 小时）：实际工业信号数据的 ML 应用题 + 基础概念深挖（含完整评论区，Wayback 全文）
*medium · 频率: single report（细节最全的 RE ML 轮实录） · 2021-11*

《DeepMind research engineer 第二轮ML过经》2021-11-30，物理 PhD 转 MLE 两年半，LinkedIn 被 GDM tech recruiter 主动联系，先 1 小时友好交流，11/11 第一轮 coding，第二轮 ML 背靠背两小时（题目正文积分墙，但评论区楼主透露关键内容）：题目围绕机器运转遥测信息——"就是一些机器运转信息，比如温度啦，机器型号啦，读写load啦之类的信号"，让你设计 ML 方案，不需要 NLP 知识；另一位面试者补充自己的 loop 是 1-hour Math&Statistics + 1-hour ML。楼主经验总结："math的部分没有很难或者很深，但我也按照地里之前发的准备了一些probability和linear algebra的题"；"面试官并不在意你的背景，更在意你在你了解的领域是不是真的知识点扎实……比如你提到了SVM，你就应该知道SVM是什么，切忌不懂装懂"。结果 timeline：第二轮次日 HR 电话通过；终轮 manager 面"有大概一半甚至以上的时间是问简历上的经历里的某个具体model，以及BQ"；面完一周内出结果，intern final round 面完次日 HR 说 working out offer。备考材料：楼主推荐 medium 上的 ML 面试题清单（link.medium.com/b1SNS3VxMlb）及地里 deepmind 相关 cheat sheet，花一两天速览。

**解法**: 针对遥测信号题（我的推断）：按 ML design 框架答——明确预测目标（故障预测/异常检测）、特征工程（温度/负载时序聚合、机型类别 embedding）、标签稀疏与类别不平衡处理、时序 train/test split 防泄漏、指标选 PR-AUC、冷启动与部署监控。面试官要的是基础扎实+变通，不是堆 SOTA。

来源: <http://web.archive.org/web/20220813055622/https://www.1point3acres.com/bbs/thread-825115-1-1.html>

### GDM research tech 电面（统计 PhD）：HR 发官方备考 PDF；实考 functional analysis + RL + deep learning（超纲）
*hard · 频率: single report · 2020-11*

《deepmind research，tech店面》2020-11-20。原文："hr给的pdf介绍的很全了，补充几个：楼主被问到了functional analysis, reinforcement learning, deep learning。functional anlysis似乎不在pdf的推荐阅读里。可能统计phd[会被问]……"。两个关键信息：(1) GDM 会给候选人官方 prep PDF（含推荐阅读清单，覆盖 quiz 四大块）；(2) 实际提问会根据候选人背景超出 PDF 范围（统计 PhD 被问泛函分析），印证 825115 楼主观察：面试官按你自称懂的领域往深挖。

**解法**: 注：此条目原帖为 thread-689380（tag 页恢复），正确直链应为 https://www.1point3acres.com/bbs/thread-689380-1-1.html。我的推断：拿到 recruiter PDF 后逐条过推荐阅读，同时把自己 PhD 领域的研究生级核心课内容复习到能口头推导。

来源: <https://www.1point3acres.com/bbs/interview/google-machine-learning-628812.html>

### （补充来源，知乎转载性质）GDM 面试实录：BQ+简历项目+RNN/GRU/LSTM 对比+链表基础，面试官控制提问节奏
*easy · 频率: single report · 2024-10*

知乎专栏《谷歌DeepMind面试惊险通过！面试官不让多问！》(p/983167020，约 2024-10)。zhihu 正文被反爬，搜索快照可见内容：一位博士生的 GDM 面试（疑似 student researcher/intern 轨第一轮），面试官温柔，先 BQ 和简历项目深挖，技术部分考：RNN vs GRU vs LSTM 的优劣对比（序列建模场景选型）、链表等数据结构概念；标题含义为面试官限制候选人反问时间。通过。非 1p3a 来源，作为 2024 年 GDM 中文面经补充。

**解法**: RNN/GRU/LSTM 标准答案（我的补充）：RNN 梯度消失难捕长依赖；LSTM 三门+cell state 解决长依赖但参数多；GRU 两门更省参数、小数据上常更好；实践中长序列/大数据选 LSTM 或直接 Transformer，资源受限选 GRU。

来源: <https://zhuanlan.zhihu.com/p/983167020>

### ML fundamentals（quiz）真题集（IGotAnOffer 六题 verbatim）
*hard · 频率: 聚合（多条 Glassdoor/Blind 报告） · 2026-06（指南更新时间）*

RE ML fundamentals 轮（候选人俗称 the quiz，现为对话式）真题：1) Explain the difference between gradients and weights；2) What are convex functions, and what's special about them?；3) 袋中有不同颜色的球，给定若干观察，求下一个抽到某颜色的概率（贝叶斯/后验预测）；4) Why would you prefer L1 over L2 regularization? 必须讲清梯度如何作用于权重导致稀疏的数学直觉；5) Walk me through how regression, SVMs, kernel SVMs, and Bayesian networks work, and when you'd use each；6) Derive the ELBO for a graphical model。评分核心是数学直觉：不能只背结论，要能推导并联系模型实际行为。

**解法**: L1：次梯度幅度恒为 λ·sign(w)，与 w 大小无关，可把小权重直接推到 0；L2 梯度 2λw 按比例收缩、不为零。ELBO：log p(x)=E_q[log p(x,z)/q(z)]+KL(q||p(z|x))≥E_q[log p(x,z)]-E_q[log q(z)]，用 Jensen 或 KL 非负两种推法都要会。

来源: <https://igotanoffer.com/en/advice/google-deepmind-research-engineer-interview#q2>

### RS/RE ML 深度题：解释 transformer 训练全流程（SFT+RL）与 attention O(n²) 内存及替代方案
*hard · 频率: multiple reports · 2025*

Glassdoor RS 报告：被要求“在 LLM 语境下解释 transformers、解释训练 transformers 的过程、其中的 supervised finetuning 和 RL”。letsdatascience 汇总：GDM ML theory 轮要求解释“为什么 attention 在内存上是 O(n²)”并讨论替代方案；强调架构内部机理而非 API 使用。

**解法**: O(n²) 来自 QK^T 注意力矩阵的显式物化；替代：FlashAttention（tiling+重计算，内存 O(n)）、滑窗/稀疏注意力、linear attention（kernel 化）、MQA/GQA 减 KV heads、PagedAttention 推理侧。SFT→RL：预训练 next-token → SFT 指令数据 → RM/偏好建模 → PPO/GRPO/DPO，讲清每步目标函数与 KL 正则。

来源: <https://letsdatascience.com/blog/how-to-land-a-job-at-openai-anthropic-or-google-deepmind>

### Dataford：GDM Research Scientist 题库样题 15 条（442 题库）
*hard · 频率: 题库聚合（标注 Very common/Common） · 2025~2026*

流程：HR screening → technical rounds（quiz 式+实操 coding）→ research discussions，3-5 周。ML/研究基础：Explain the derivation of the backpropagation algorithm for a MLP；How do you manage the bias-variance trade-off in deep neural networks?；Describe the mathematical properties of a metric space；Compare loss functions for classification vs regression；How would you explain Bayes' theorem to a non-technical stakeholder? Coding/CS：实现特定数据变换/文本解析函数；内存受限场景数据结构 trade-off；高性能计算中的并发/线程；给定算法优化时空复杂度；CNN vs Transformer 架构差异。研究设计：走查研究项目方法论与技术难点；设计大规模模型的实时数据摄取系统；模型表现不佳时的系统化 debug 流程；讲一篇影响你方法论的近期论文；如何确定研究实验的合理 scope。

来源: <https://dataford.io/interview-guides/google-deepmind/research-scientist>

## System Design

### Google/DeepMind · System Design 题库（20 题，经典分布式系统）
*hard · 频率: onsite 高频 — Google 频率：Design Job Scheduler 9、Design News Feed 9、Design Typeahead 8、Design Youtube 8、Design Distributed Rate Limiter 7、Design Instagram 7、Design TinyURL 7 · 2025-12 至 2026-04*

Google SD 全 20 题（Onsite，正文需登录；practice URL .../google/system-design/{id}/practice）：Design Payment System(Hard)、Design Slack-like Chat System(Hard)、Design News Feed(Medium, id 69ca9b37ff3ebde766ced8eb)、Design TinyURL(Easy)、Design Metrics System(Medium, 69cc94b2ff3ebde766cee3f2)、Design Youtube(Hard)、Design Distributed Rate Limiter(Hard, 69cd9871ff3ebde766cee7fe)、Design Dropbox(Hard, 69cdf6feff3ebde766ceea74)、Design Job Scheduler(Medium)、Design Notification System(Medium, 69cfaa8f4f38b199f9e49615)、Design Facebook Messenger(Medium)、Design A Top K Popular Items System(Medium, 69d2ef0707421ca06eb8e53b)、Design Typeahead Suggestion(Medium, 69d55ecf60ca00f1f2f5f100)、Design Spotify(Medium)、Design S3-like Object Storage System(Medium, 69d84a1bc4c1bc791ee2309f)、Design Quota Service(Medium)、Design Key-value Store(Hard, 69dc51e8e4441834b3f7376f)、Design Instagram(Hard, 69e1b8b295e80ae213e5d4a2)、Design Google News(Medium)、Design A VM Bandwidth Rate Limiter(Hard, 6a074964906c2652b8dd4616)。多为跨公司通用经典题（非 Google 独有）。

**解法**: （我的推断）Google 侧重规模化与一致性：Rate Limiter（令牌桶/滑窗、分布式计数）、Key-Value Store（一致性哈希、复制、quorum、LSM）、Top-K（count-min sketch + heap）、Typeahead（Trie + 前缀聚合缓存）。对 RE 岗建议至少熟练其中 5-6 道 Hard。

来源: <https://www.hack2hire.com/question-bank/companies/google/system-design>

### techinterview.org 2026：SWE track 轮次（含 ML serving domain depth）
*hard · 频率: 聚合指南 + 1 条 Blind 佐证 · 2026*

SWE 4-5 轮：2 场 coding（medium-hard；数组/字符串/图/树/DP，unaided）+ 1 场 system design 60min（端到端设计可扩展服务：需求澄清、API、存储选型）+ 1 场 domain depth（按团队考 ML serving / API 设计 / infra：latency、batching、deployment）+ behavioral。2026 政策：技术轮普遍禁止或严格限制 AI 工具，仅个别 applied 岗例外。佐证（Blind 2025-12 xhrkeb8z）：L4 SWE 称 system design 题“very weird and ambiguous”。

来源: <https://www.techinterview.org/post/3233474918/deepmind-interview-process-2026/>

## ML System Design

### IGotAnOffer ML design round: system-design-style but ML-first; constraints added iteratively; justify from first principles
*hard · 频率: high (multiple reports agree this is the hardest round) · 2025*

After the fundamentals round, RE candidates face one or more ML design interviews — 'the heart of the technical loop... regularly described as the hardest part of the process.' Format: like system design in that you outline a high-level approach, but you must develop a machine-learning solution and walk the full pipeline: data collection, preprocessing, model architecture, training, evaluation, deployment. Interviewers iteratively add constraints (Blind report: 7-8 constraints layered over each of 7-8 techniques discussed). You must justify every decision from first principles: if you choose a particular loss function, optimizer, or architecture, expect to explain why it's the right call. Related ML-aware design prompts circulating in prep material: 'Design a serving system for a 100B-parameter model at scale', 'Build an evaluation pipeline that runs thousands of benchmarks nightly', 'Design a feature store for an ML experimentation platform'.

**解法**: Practice the constraint-escalation game: take any design (recsys, LLM serving, eval pipeline) and re-solve under: 10x less labeled data → weak supervision/synthetic data; strict latency → distillation/quantization/caching; distribution shift → monitoring + continual finetuning; no user feedback → offline eval + proxy metrics. Always tie back to the objective/loss. (my inference)

来源: <https://igotanoffer.com/en/advice/google-deepmind-research-engineer-interview>

### Applied AI Engineer 面试大纲（recruiter 官方给出，Blind 2025-09）
*hard · 频率: single report（但为 recruiter 官方大纲，可信度高） · 2025-09-30*

GDM Applied AI Engineer，recruiter 明确列出 ML system design 考察范围：1) System Architecture：high-level model choice, designing for scale；2) Retrieval (RAG)：factuality, grounding, implementation；3) Efficiency：quantization, distillation, optimization；4) Agent Frameworks：LangChain, LangGraph 等；5) Evaluation：aligning evals with problem formulation。楼主追问三点：设计题是否聚焦大规模生成式 AI（code assistant、RAG 系统）；“ML Debugging”轮的 bug 是什么样（社区共识：bugs are stupid, not hard）；理论 ML vs 分布式系统工程的比重。评论建议：“通常是 transformer based……读 ML system design 和 GenAI system design 教科书”。

**解法**: ML debugging 轮备考：练习找“蠢 bug”——张量 shape/broadcast 错误、softmax 维度错、CrossEntropyLoss 前多加 softmax、忘 zero_grad、dataloader 没 shuffle、train/eval 模式混用。

来源: <https://www.teamblind.com/post/deepmind-applied-ai-engineer-interview-ml-system-design-deep-dive-j5n8qh3k>

### Google/DeepMind · ML System Design 题（Bot Detection + Address Autofill）
*medium · 频率: medium — Google 频率：Design A Bot Detection System 7(Onsite)、Design An Address Autofill System 4(Onsite) · 2026-02 至 2026-03*

Google 页面下仅有的 2 道 ML System Design（Onsite，正文需登录；practice URL .../google/ml-system-design/{id}/practice）：(1) Design A Bot Detection System [Medium, id 69f67e5830f41dfd539fbf82, companyFreq Google=7/Amazon=5]：区分真人流量与自动化 bot 的 ML 系统。(2) Design An Address Autofill System [Medium, id 6a094f91c84b6e8a3be17ce4, companyFreq Google=4/Amazon=4/Uber=6]：地址自动补全。这是站内 ML System Design track（较新上线）中与 Google 关联的题。

**解法**: （我的推断）Bot Detection 应覆盖：特征工程（行为/设备指纹/频率）、在线 vs 离线特征、标签获取与延迟反馈、对抗性演化下的模型再训练、精度/召回与误伤权衡、实时低延迟打分。Address Autofill：候选生成（Trie/倒排 + geo）+ 排序模型（学习排序）、个性化、拼写纠错、延迟预算。对该候选人的 post-training/数据管线经验是加分点。

来源: <https://www.hack2hire.com/question-bank/companies/google/ml-system-design>

### techinterview.org 2026: RE track rounds — distributed training design and evaluation infrastructure design
*hard · 频率: prep-site synthesis (unverified but consistent with candidate reports) · 2026*

Research Engineer loop per same guide: (1) ML coding, 60 min — larger pipeline implementation pieces than the RS version. (2) Distributed training systems design, 60 min — design a training system for models exceeding single-accelerator capacity; expected topics: data/pipeline/tensor parallelism, ZeRO, DeepSpeed-style optimizations. (3) Evaluation infrastructure, 60 min — design an evaluation harness for a frontier model across many benchmarks; must address test-set contamination and reproducibility. (4) Standard coding, 60 min — medium-to-hard algorithmic problem, 'often unaided'; talk through approach and complexity out loud BEFORE typing. (5) Behavioral — collaboration in research teams, shifting priorities under research uncertainty, end-to-end ownership. Prep guidance: study Megatron/DeepSpeed/FSDP, build eval-harness design skills, practice ML coding without AI tools.

**解法**: Distributed training answer skeleton: memory math (params+grads+optimizer states ≈ 16 bytes/param for Adam mixed precision), then DP→ZeRO stages→TP within node→PP across nodes→activation checkpointing; interconnect-aware placement; failure recovery via checkpointing. Eval harness: versioned datasets, hermetic runs, seed control, contamination detection (n-gram/embedding overlap), CI-style nightly runs with regression alerts. (my inference)

来源: <https://www.techinterview.org/post/3233474918/deepmind-interview-process-2026/>

### r/MachineLearning 2025-04: Gemini team ML system design — insider + coach guidance (sharding, KV cache, quantization, MoE)
*hard · 频率: single thread with insider + coach corroboration · 2025-04*

Thread by a candidate interviewing with the Gemini team for LLM system design. A self-identified DeepMind employee replied: for system design look at 'zero-1, zero-3 and megatron', linking the EEML tensor-parallelism tutorial (github.com/eemlcommunity/PracticalSessions2023/tree/main/tensor_parallelism); for culture fit, be collaborative and don't say anything offensive (people genuinely fail this); ask recruiter for Google mock interviews. An interview coach added, based on multiple Gemini-team candidates: ML system design differs from SWE system design — heavy focus on throughput, memory constraints, and latency tradeoffs specific to LLM deployments; be ready to discuss sharding strategies, KV cache optimization, quantization techniques; read up on MoE architecture (Gemini Ultra uses it); brush up distributed training (FSDP, DeepSpeed); read 'Transformer Inference Arithmetic'; articulate tradeoffs (precision vs latency, model size vs perf). Behavioral: prepare examples showing rapid progress amid ambiguity — 'apparently a big thing for them'; team moves very fast, values collaborative problem solving over solo brilliance.

**解法**: Core LLM-serving numbers to know: KV cache size = 2·layers·kv_heads·head_dim·bytes·seq_len per sequence; batching (continuous batching), paged attention, speculative decoding, quantization (int8/int4, AWQ/GPTQ), distillation. For training: ZeRO stage tradeoffs, TP communication cost (all-reduce per layer) vs PP bubble.

来源: <https://old.reddit.com/r/MachineLearning/comments/1k8gy12/d_preparing_for_a_deepmind_gemini_team_interview/>

### Blind 2025-09: Applied AI Engineer loop — recruiter-listed ML system design focus areas (RAG, efficiency, agents, evals)
*hard · 频率: single report · 2025-09*

Candidate preparing for GDM Applied AI Engineer ML system design round shared the recruiter's stated focus points verbatim: (1) System Architecture: 'high-level model choice, designing for scale'; (2) Retrieval (RAG): 'factuality, grounding, implementation'; (3) Efficiency: 'quantization, distillation, optimization'; (4) Agent Frameworks: 'LangChain, LangGraph, etc.'; (5) Evaluation: 'aligning evals with problem formulation.' OP asked whether design problems center on large-scale generative AI systems (code assistants, RAG), expected depth on vector DBs and prompt orchestration, ML debugging round bug types (convergence issues, data leaks), and theory-vs-distributed-systems balance — no insider answers in comments, but the recruiter list itself is the signal.

**解法**: Design template for GDM applied rounds: problem formulation → model choice (API LLM vs finetuned vs distilled) → RAG pipeline (chunking, embeddings, hybrid retrieval, reranking, grounded generation with citations) → eval design FIRST-CLASS (offline evals aligned to task, LLM-judge with human calibration, regression suites) → efficiency levers (quantization, distillation, caching) → agent orchestration and failure handling. (my inference)

来源: <https://www.teamblind.com/post/deepmind-applied-ai-engineer-interview-ml-system-design-deep-dive-j5n8qh3k>

### GDM RE 流程中的 ML Design 轮（2022 新增，地里公认无具体面筋）
*unknown · 频率: single report · 2022-10*

《Deepmind ML Design》2022-10-22。原文："楼主正在面deepmind的re，貌似会有一轮ml design，有没有朋友能指点一下他们大致会怎么面吗？地里好像没太有具体的面筋：（"。确认 2022 起 RE loop 含 ML design 轮，且 1p3a 上没有该轮的具体题目沉淀。可参照 825115 的遥测信号题风格：给一个实际业务/研究场景让你端到端设计 ML 方案。

**解法**: 我的推断：GDM 的 ML design 更偏 research-flavored（如何设计实验/训练方案/评估），不是 Meta 式推荐系统八股。按『问题定义→数据→模型选型与 scaling 考量→训练与评估→迭代』框架，主动讨论 ablation 和 failure mode 会加分。

来源: <https://www.1point3acres.com/bbs/thread-938855-1-1.html>

### techinterview.org 2026：Research Engineer track——分布式训练与评测基础设施设计轮
*hard · 频率: 聚合指南 · 2026*

RE 4-5 轮：1) ML Coding 60min（比 RS 版更工程化——实现更大的 pipeline 片段）；2) Distributed Training Systems Design 60min：为多加速器大模型设计训练系统，考 pipeline parallelism、tensor parallelism、ZeRO、DeepSpeed 式优化；3) Evaluation Infrastructure 60min：设计跨 benchmark 的评测 harness，必须处理 test set contamination 和 reproducibility；4) 标准算法 coding（medium-hard，与普通工程 loop 同一 bar）；5) Behavioral：与研究团队协作、优先级在不确定性下的切换。备考建议原文：“distributed training systems (Megatron, DeepSpeed, FSDP), evaluation harnesses, ML coding without AI tools”。

**解法**: 评测 harness 设计要点：版本化数据集+prompt 模板、n-gram/embedding 去污染检测、固定 seed+温度记录、并行调度与缓存、人工/LLM-judge 校准——正中候选人 Reflection.ai 数据管线经验，可主动映射。

来源: <https://www.techinterview.org/post/3233474918/deepmind-interview-process-2026/>

### ML design 轮真题四道（IGotAnOffer verbatim）
*hard · 频率: 聚合（多条报告） · 2026-06*

RE ML design 轮（被普遍称为整个 loop 最难）真题：1) How would you build, train, and deploy a system that detects if multimedia and/or ad content violates terms or contains offensive materials?（多模态内容审核系统全链路）；2) Design autocomplete and/or spell check on a mobile device（端侧约束）；3) Design autocomplete and/or automatic responses for email（Smart Compose/Smart Reply）；4) Design the YouTube recommendation system。要求从第一性原理为 loss/optimizer/架构选择辩护，讲清 pipeline：数据收集→预处理→模型→训练→部署→评测。

**解法**: 每题按：需求/约束澄清 → 指标（在线+离线）→ 数据与标注 → baseline→ 模型迭代（说明 trade-off）→ serving（延迟/端侧量化）→ 监控与反馈回路。移动端题要主动谈模型压缩（蒸馏/量化/剪枝）。

来源: <https://igotanoffer.com/en/advice/google-deepmind-research-engineer-interview#q3>

### Applied AI Research Manager onsite：coding + ML Design + Applied Fundamental ML（Blind 2025-09）
*hard · 频率: single report · 2025-09-07*

Meta Ads Ranking 背景候选人报告 GDM Applied AI research manager onsite 构成：coding 面（bar 类似 Google/Meta）、ML Design 轮、Applied Fundamental ML 轮。其焦虑点是被要求“design an LLM based system end to end”而自己缺 LLM 系统设计实战。Google 员工建议：“Practice designing popular LLM products”（练习设计主流 LLM 产品）。

**解法**: 准备 3-4 个端到端 LLM 产品设计模板：RAG 问答/企业搜索、代码助手、聊天助手（含安全护栏）、Agent 工作流，每个含数据飞轮与评测方案。

来源: <https://www.teamblind.com/post/what-to-expect-for-deepmind-applied-ai-research-manager-interview-os1sve2c>

### DeepMind ML Design 面: 化学分子反应预测建模 (2025-08)
*medium · 频率: 1 (2025-08 同一套 GDM ML 面) · 2025-08*

岗位: DeepMind ML Engineering, ML Design/建模 视频面 (伦敦小哥面试官, 友好)。题目: 有一个 chemistry molecule dataset, 数据形式为 (molecule1_name, molecule2_name, reaction factor)。要求建模预测 reaction factor。英文摘要点明期望方向: EDA techniques + transformer models ('molecule reaction prediction using transformer models and EDA techniques')。开放式 ML 建模讨论，从数据探索到特征化到模型选择到评测。

**解法**: 推断解题框架: (1) EDA: 分子名分布/去重/reaction factor 分布(是否长尾/需 log 变换)、数据泄漏(molecule pair 对称性)检查; (2) 特征化: 把 molecule_name 转成结构表示 (SMILES tokenize / 指纹 Morgan fingerprint / 学习 embedding); (3) 模型: 分子对 -> transformer/GNN 编码后回归 reaction factor, 或对称双塔; (4) 评测: RMSE/MAE, 按分子 scaffold split 防泄漏, 交叉验证; (5) 讨论冷启动/未见分子泛化。

来源: <https://www.1point3acres.com/bbs/thread-1141657-1-1.html>

## BQ / Culture

### Final round / team match: 2 team-lead conversations + People & Culture; team match can still reject after passing technicals
*medium · 频率: high (multiple reports) · 2026*

Final round = team lead + senior team lead + People & Culture partner. Team-lead rounds probe background, ML experimentation/modeling experience, open-ended ML problems, resume defense (design choices, favorite projects, conflict with coworkers). P&C covers motivation ('why do you want to join DeepMind'), mission alignment, collaboration. Framed as mutual assessment through the lens of team goals/culture. Critical caveat from 2026-05 Reddit report: candidate passed all technical rounds, then had THREE additional experience interviews and lost to another candidate — i.e., final stage is competitive team match, not a formality. Blind report similarly rejected at the end for 'not enough experience in ML experimentation and modeling.' Prepare concrete experiment-design war stories: hypotheses, ablations, metrics, failures, iteration speed.

**解法**: For a post-training background: prepare 3-4 STAR stories on SFT/RL experiment cycles — reward hacking found and fixed, data-mixture ablations, eval-driven iteration, cross-team collaboration with infra/data teams. (my inference)

来源: <https://igotanoffer.com/en/advice/google-deepmind-research-engineer-interview>

### 行为面/HR screen 真题集（Glassdoor QTN 多条）
*easy · 频率: high（几乎每条 review 都含） · 2019-2025 各年*

HR 初筛真题（QTN_4920046）：How are you today? / How was your weekend? / Why DeepMind? / When do you think we will have AGI?（AGI 时间线是 GDM 特色题）。其他：Why do you want to work at DeepMind?（QTN_4156589，intern）；Why do you want to join Deepmind?（QTN_3044738，PhD）；Have you got any questions for us?（QTN_1982513）。多来源强调：要能讲“为什么是这个 lab 而不是泛泛的 AI”，引用其近期研究（AlphaFold、Gemini）。

**解法**: AGI 时间线题：给出有依据的个人观点+不确定性区间，并落到“因此现在做 X 研究最重要”，忌空谈。

来源: <https://www.glassdoor.com/Interview/Initial-HR-screening-How-are-you-today-How-was-your-weekend-Why-DeepMind-AGI-do-you-think-we-will-have-QTN_4920046.htm>

### DeepMind Gemini RS Hiring Manager 视频面 (2025-09)
*medium · 频率: single report · 2025-09*

岗位: Google DeepMind Gemini Research Scientist (RS), Hiring Manager 轮 (视频面)。楼主原话: '都是开放式的问题, 但是很 domain-specific'。英文翻译摘要: 'key open-ended, domain-specific questions for Google DeepMind Gemini RS video interview'。具体问题列表在 200 积分墙后（本帖隐藏内容需要积分高于200）。可确认: Gemini 组 RS 的 HM 轮 = 开放式 + 强领域相关（针对候选人研究方向深挖）。

**解法**: 推断准备方向: 针对 Gemini/LLM 领域的开放式研究讨论——准备好讲清自己 post-training(SFT/RL) 与 mid-training 数据管线工作的动机、trade-off、失败案例，并能就 LLM 训练/评测/scaling 的 domain-specific 追问深入对答。

来源: <https://www.1point3acres.com/bbs/thread-1145755-1-1.html>

### DeepMind Hiring Manager 面 + 技术快问快答 (ML 岗, 2025-08)
*medium · 频率: 1 (与 1141656/1141657 同一楼主同期一套 GDM ML 面, 2025-08) · 2025-08*

岗位: DeepMind Machine Learning Engineering, Hiring Manager 轮。可见题目清单: (1) 自我介绍; (2) 最自豪的项目; (3) modeling 遇到过什么 challenge 怎么解决的; (4) Technical 快问快答, 例如: 你都知道哪些 regularization 的方法? 多 GPU 情况下[如何训练/同步]...(后续问题被积分墙截断)。英文摘要: 'technical questions and problem-solving challenges'。

**解法**: regularization 参考答案: L1/L2(权重衰减)、dropout、early stopping、data augmentation、batch/layer norm、label smoothing、mixup、梯度裁剪。多 GPU: data parallel(DDP, all-reduce 梯度同步)、model/tensor parallel、pipeline parallel、ZeRO/FSDP 分片、梯度累积、混合精度。

来源: <https://www.1point3acres.com/bbs/thread-1141654-1-1.html>
