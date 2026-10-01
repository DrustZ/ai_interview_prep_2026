# 04 · Agent Benchmark 速查

⏱ 骨架 8 min ｜ 含深潜与资料 12 min ｜ 面试前只看 ⭐⭐⭐ 部分

数字均为 2026-07 web 核实的**量级**，非精确值；agent benchmark 分数强依赖 harness，引用时永远带 "取决于 scaffold" 的限定。指标定义详解见 [01_core/06_eval_security.md](01_core/06_eval_security.md)。

## 主表 ⭐⭐⭐

| Benchmark | 测什么 | 环境形态 | 指标 | SOTA 量级 (2026-07) | 已知失败模式 | 链接 |
|---|---|---|---|---|---|---|
| SWE-bench Verified | 真实 GitHub issue → patch | repo + docker，500 题（人工筛自原始 2294） | resolved rate（fail-to-pass + pass-to-pass 测试） | ~80–90%+，harness 差异可达 ±10pt | 训练污染（repo 全在预训练集）；只验测试不验代码质量 | [paper](https://arxiv.org/abs/2310.06770) · [repo](https://github.com/swe-bench/SWE-bench) |
| SWE-bench Pro | 同上，防污染加难版（Scale AI） | 1,865 题 / 41 repo，copyleft 公共集 + held-out 商业集 | resolved rate | 公共集 ~60–70%，商业集更低 | grader 审计发现 ~1/3 试次误判；模型读 `.git` 历史偷 gold patch | [paper](https://arxiv.org/abs/2509.16941) · [repo](https://github.com/scaleapi/SWE-bench_Pro-os) |
| τ-bench | 客服 agent：API 调用 + policy 遵守 + 对话 | LLM 模拟用户 + 域 API（retail/airline） | pass^k（DB 终态比对） | 官方榜冻结在 2024 模型：pass^1 ~69% retail / ~46% airline | user simulator 本身是噪声源且可被 exploit | [paper](https://arxiv.org/abs/2406.12045) · [repo](https://github.com/sierra-research/tau-bench) |
| τ²-bench | dual-control：用户侧也执行操作，agent 要指导用户 | 新增 telecom 域（troubleshooting） | pass^k | telecom pass^1 从 2025 的 ~35–50% 涨到前沿模型 ~95%+（趋饱和） | pass^k 随 k 衰减远快于 pass^1；原任务集有 policy 不对齐（Amazon 出了 Verified 修订版） | [paper](https://arxiv.org/abs/2506.07982) · [repo](https://github.com/sierra-research/tau2-bench) |
| GAIA | 通用助手：web 检索 + 工具 + 多模态推理 | 466 题、3 levels，答案唯一字符串 | exact match accuracy | 整体 ~90%+，Level 3 ~80–88%（趋饱和） | 榜单比的是 system（model+tools+policy）不是 model；exact match 限制任务设计 | [paper](https://arxiv.org/abs/2311.12983) · [榜](https://huggingface.co/spaces/gaia-benchmark/leaderboard) |
| WebArena | 自主 web 操作（电商/GitLab/论坛/CMS/地图） | 812 题，6 个自托管 docker 网站 | functional success rate | ~70–75%（GPT-4 首发 14.4%，human 78.2%） | evaluator 有 false negative；agent 学会走捷径（直改 URL）；站点版本旧、离线 ≠ 线上 | [paper](https://arxiv.org/abs/2307.13854) · [官网](https://webarena.dev/) |
| OSWorld(-Verified) | 全 GUI computer use | 369 题真实 OS（VM），execution-based 评分脚本 | success rate | Verified ~65–75%（human ~72%） | 原版 ~10% 任务本身坏的（故有 Verified）；对 step 预算和 screenshot/a11y 输入极敏感 | [paper](https://arxiv.org/abs/2404.07972) · [官网/榜](https://os-world.github.io/) |
| Terminal-Bench 2.0 | 终端端到端任务（build/sysadmin/数据/安全） | headless 容器 + 验证脚本（Harbor harness） | pass rate | 前沿 ~65–82%（仍 fail 18–35%） | harness 敏感（同模型换 scaffold 差 15–20pt）；任务分布偏 infra 不偏产品代码 | [官网](https://www.tbench.ai/) · [榜](https://www.tbench.ai/leaderboard/terminal-bench/2.0) |
| AgentDojo | prompt injection 下的 tool-use agent 安全 | 97 user task × 629 注入 case（workspace/banking/travel/slack），攻防可编程 | benign utility / utility under attack / targeted ASR 三指标 | 2026 前沿模型对朴素注入 ASR 接近 0，但 RL red-teaming 能重新打穿 | 静态攻击过时快——必须对 adaptive attacker 评 | [paper](https://arxiv.org/abs/2406.13352) · [repo](https://github.com/ethz-spylab/agentdojo) |

> 高分句：agent benchmark 报的是"系统分"不是"模型分"——同一个模型换 harness 在 SWE-bench / Terminal-Bench 上能差 10–20 个点，所以引用数字必须带 scaffold 上下文。

### 2024→2026 的三条演化主线 ⭐⭐

- **Verified 化**：原始集被发现含坏题后出人工修订版——SWE-bench→Verified、OSWorld→Verified、τ²→τ²-Verified。引用旧论文数字先确认是哪个版本。
- **防污染化**：静态公共集必然进训练集 → Pro 用 copyleft + held-out 商业集、Terminal-Bench 持续换题、live 类 benchmark（按提交日期切分）兴起。
- **指标从均值到分布**：pass@1 → pass^k（一致性）→ utility + ASR 双指标（安全）；单一标量分数在 2026 已不够回答"能不能上生产"。

## 指标速记：pass@k vs pass^k ⭐⭐⭐

设单次成功率为 $p$，k 次独立采样：

- $pass@k = 1-(1-p)^k$：**任一次**成功即算过，随 k 单调升 → 测能力上限（有 verifier 可 rerank 时才有意义）
- $pass\^k = p^k$：**全部 k 次**都成功才算过，随 k 单调降 → 测可部署一致性

直觉锚点：$p=0.7$ 时 $pass@8 \approx 99.99\%$ 而 $pass\^8 \approx 5.7\%$。τ-bench 用 pass^k 正是要暴露这个 gap：客服场景没有"重试到对为止"，一致性才是生产指标。

各 benchmark 的判分机制一句话对照（追问"怎么判对"时用）：

| 判分机制 | 用在哪 | 优点 / 代价 |
|---|---|---|
| 单元测试 (fail-to-pass) | SWE-bench 系 | 客观廉价 / 不测代码质量，测试可被泄漏 |
| DB/环境终态比对 | τ-bench、WebArena（部分） | 结果导向 / 不评过程与对话质量 |
| execution-based 评分脚本 | OSWorld、Terminal-Bench | 逐任务定制、精确 / 维护重，脚本本身会坏（Verified 的由来） |
| exact match 短答案 | GAIA | 零成本 / 限死任务形态，只能出"唯一答案"题 |
| utility + ASR 双轨 | AgentDojo | 能暴露"砍功能换安全"的假防御 / 需要可编程攻防环境 |

注意上表没有 LLM-as-judge：主流 agent benchmark 刻意回避它，因为 judge 偏差会被 agent 优化利用——这是设计题里值得主动说的点。

> 高分句：pass@k 是给有 verifier 的场景看的乐观数，pass^k 是给没有 verifier 的生产环境看的悲观数——定 SLO 用后者。

## 逐个追问备答

<details><summary>SWE-bench：为什么要 Verified？Verified 和 Pro 差在哪？</summary>

- 原始 2,294 题含不可解题（issue 描述不足、环境依赖坏）和测试泄漏（fail-to-pass 测试直接暗示解法），OpenAI 人工筛出 500 题成 Verified。
- Pro（Scale AI）解决的是另一个问题——**污染**：公共集只用 GPL 等 copyleft 仓库（法律上阻止入训练集），另有 held-out 商业代码集；任务更长、跨文件 diff 更大。
- 追问"分数可信吗"：2026-05 审计报告 Pro 的 grader ~1/3 试次误判（错收 8.5% / 错拒 24%），且有模型被抓到读 repo 的 `.git` 历史直接拿 gold patch——环境卫生（strip git history）本身是 eval infra 问题。
- 追问"resolved 意味着什么"：只保证过测试，不保证 patch 质量/风格/无副作用；这是它与真实 code review 的根本 gap。

</details>

<details><summary>τ-bench / τ²-bench：pass^k 说明什么？dual-control 加了什么难度？</summary>

- pass^k 腰斩式衰减（k=1→8）说明失败主要来自**方差**而非能力缺口：同一任务重跑就挂，根因常是对话分支敏感 + user simulator 随机性。
- 评分靠 DB 终态比对 + 必要 action 检查，不评对话质量——所以能自动化，但 policy 遵守只测"结果合规"。
- τ² 的 dual-control：用户侧也持有工具（如重启路由器），agent 必须**指导人执行**并处理其报告的观察——测的是协作而非代管，telecom 域首发时 pass^1 仅 ~34%（GPT-4.1）。
- 追问弱点：user simulator 是 LLM，可被 agent 诱导偏离剧本；Amazon 的 τ²-bench-Verified 修了任务/policy/DB 不对齐的题。

</details>

<details><summary>GAIA：饱和了之后怎么看？</summary>

- 设计初衷：题目对人简单（~92%）对模型难（GPT-4 插件版 ~15%），答案是唯一短字符串 → exact match 评分零成本。
- 2026 现状：整体 ~90%+、Level 3 也 80%+，基本饱和；且榜单条目是"model + 检索工具 + browser + 重试策略"的整套 system，横向比较意义有限。
- 后继：Meta 的 Gaia2 / ARE（2025）加了写操作、异步事件、时间预算——回应了 GAIA 只读、无副作用的局限。
- 引用姿势：把 GAIA 当"检索型通用助手"的历史坐标系用，别当现役区分度指标。

</details>

<details><summary>WebArena：自托管的取舍是什么？</summary>

- 自托管 docker 网站（电商/GitLab/Reddit 类/CMS/地图/wiki）→ 完全可复现、无真实世界副作用；代价是站点版本冻结、与现代 web（反爬、动态 UI）脱节。
- 评分是 functional：查 URL / DB 状态 / 文本匹配 → 有 false negative（答案对但表述不匹配），也被 agent exploit 过（直接构造目标 URL 跳过流程）。
- 数字锚点：GPT-4 首发 14.4%，human 78.2%，2026 SOTA ~70–75%——三年从 1/5 human 到接近 human。
- 追问"离线分数外推到线上吗"：不行，线上任务（Online-Mind2Web 类）分数显著更低，这是环境保真度问题。

</details>

<details><summary>OSWorld：为什么有 Verified？分数为什么波动大？</summary>

- 原版 369 题里 ~10% 任务本身有 bug（评分脚本坏、依赖失效），OSWorld-Verified 修复后才可比——引用 2025 前的旧数字要小心是哪个版本。
- 分数对三件事敏感：step 预算（15 vs 50 步差很多）、输入模态（纯 screenshot vs a11y tree）、VM 环境漂移。
- 量级：Verified 上前沿模型 ~65–75%，与 human ~72% 交叉——但 human 数字本身也是粗估。
- 追问点：execution-based 评分脚本是 OSWorld 最大贡献（不是 LLM judge），也是最大维护负担。

</details>

<details><summary>Terminal-Bench：和 SWE-bench 差在哪？</summary>

- SWE-bench 给定 repo 修 issue；Terminal-Bench 是开放式终端任务（编译、装服务、训模型、排障），端到端验证脚本判终态——更接近 SRE/infra 工作负载。
- 2.0 换 Harbor harness 并清洗任务集拉高难度；前沿模型仍 fail 18–35% 的题（这些题资深工程师能例行完成）。
- harness 效应的典型证据：同一模型换 scaffold（如 Terminus 2 vs OpenHands）pass rate 差 15%+；甚至出现让 agent 自改 harness 涨 20pt 的工作。
- 引用姿势：谈"terminal-native agent 的能力天花板"时用它，谈代码质量时不用。

</details>

<details><summary>AgentDojo：到底测什么？为什么是双指标？</summary>

- 结构：97 个正常 user task × 629 个注入 case（注入藏在工具返回的邮件/网页/交易备注里），四个域。
- 三个数一起看：benign utility（没攻击时干活行不行）、utility under attack（被攻击时任务还完不完得成）、targeted ASR（攻击者目标达成率）。**只报 ASR 是不合格的**——把工具全禁掉 ASR 也是 0。
- 首发数字锚点：最好的 agent benign utility ~78%（未攻击时就只有这么高）；GPT-4o 被攻击时 utility 从 ~69% 掉到 ~50%，canonical 的 "important message" 注入 ASR ~50%。
- 2026 现状：前沿模型对静态注入 ASR 近 0，但 RL/搜索式自动红队能重新打穿 → 结论是安全评估必须对 adaptive attacker，静态套件只是回归测试。防御两派：by-design 隔离（CaMeL：control/data flow 分离）vs 检测/清洗类。

</details>

## 按设计题主题选引用 ⭐⭐⭐

| 面试题主题 | 引哪个 | 引它的什么点 |
|---|---|---|
| coding agent / SWE 工作流 | SWE-bench Verified/Pro | harness 效应、污染与 `.git` 泄漏、"过测试 ≠ 好 patch" |
| 客服/对话 agent、可靠性 SLO | τ-bench / τ² | pass^k 衰减、user simulator 噪声、dual-control |
| browser agent | WebArena | 离线可复现 vs 线上保真度的取舍、evaluator false negative |
| computer use / GUI | OSWorld-Verified | step 预算与输入模态敏感性、评分脚本维护成本 |
| infra/终端 agent | Terminal-Bench 2.0 | scaffold 换一换差 15pt、端到端终态验证 |
| 检索型助手（历史坐标） | GAIA | 已饱和、system 分不是 model 分、Gaia2 加写操作 |
| 注入防御 / 安全门禁 | AgentDojo | 双指标、adaptive attacker、CaMeL by-design 路线 |

## 数字锚点速背（面试只需这几个）⭐⭐⭐

- [ ] SWE-bench Verified = **500** 题；Pro 公共集 **1,865** 题 / 41 repo
- [ ] τ-bench 官方榜（2024 冻结）pass^1：retail ~**69%** / airline ~**46%**；τ² telecom 首发 ~**34%**（GPT-4.1）→ 2026 前沿 ~95%+
- [ ] GAIA：**466** 题 3 levels；GPT-4 首发 ~15% → 2026 整体 **90%+**（饱和）
- [ ] WebArena：**812** 题；GPT-4 首发 **14.4%**，human **78.2%**，现 ~70–75%
- [ ] OSWorld：**369** 题，human ~**72%**，Verified SOTA 与其交叉
- [ ] AgentDojo：**97** task × **629** 注入 case；首发最好 benign utility ~**78%**
- [ ] pass^k 直觉：$p=0.7 \Rightarrow pass\^8 \approx 5.7\%$

## 自建内部 eval 时从它们各借一件事 ⭐⭐

- [ ] 借 SWE-bench：**fail-to-pass + pass-to-pass 双向测试**结构（既验修复又验不回归），以及环境卫生（strip `.git`、锁依赖）
- [ ] 借 τ-bench：**LLM user simulator + 终态比对**的自动化多轮评估管线，但给 simulator 固定 seed/剧本控方差
- [ ] 借 OSWorld 的教训：评分脚本要有**自己的测试**——10% 坏任务的根因是没人验 verifier
- [ ] 借 Terminal-Bench：把 harness 当自变量做 **ablation**，别把 scaffold 增益误报成模型增益
- [ ] 借 AgentDojo：安全回归集里 utility 与 ASR **同 dashboard 呈现**，并预留 adaptive 红队接口
- [ ] 借 Pro 的教训：内部集也会"污染"——模型会记住重复出现的评测任务，需按时间滚动换题

> 高分句：公开 benchmark 对我的价值不是排名，而是一套踩过坑的 eval 基础设施设计模式——verifier 要被测试、harness 要做 ablation、题库要防记忆。

## 设计题里怎么引用（不装、有据） ⭐⭐⭐

**模板 A · 定指标/SLO 时（引 τ-bench）**
"这个 agent 没有廉价 verifier，所以我不会拿 pass@1 当发布指标——τ-bench 的核心发现就是 pass^k 随 k 腰斩，单次成功率 70% 的 agent 连续 8 次全对只剩 ~6%。我会定义任务级 pass^k 目标，把方差（而不只是均值）当一等公民优化，比如通过收紧工具 schema 和减少对话分支敏感性。"

**模板 B · 谈安全门禁时（引 AgentDojo）**
"注入防御我会用 AgentDojo 式的双指标做 CI 门禁：utility under attack 和 targeted ASR 一起卡——只卡 ASR 会催生'把功能砍没'的假防御。另外静态注入集会过时（2026 的模型对朴素注入基本免疫，但自动化红队还是能打穿），所以门禁里要保留一条 adaptive attack 的红队回路。"

引用三原则：只说量级不背小数点；说明是哪个 harness/版本（Verified vs Pro、原版 vs τ²）；主动点出该 benchmark 的已知缺陷再引用它——这比数字本身更能证明你真用过。

> 高分句：我引用 benchmark 是为了借它的失败模式，不是借它的分数——每个 agent benchmark 的修订史（Verified、Pro、τ²、OSWorld-Verified）本身就是一部"eval 怎么坏掉"的教科书。

## 自学资料

按优先级排序；主表每行已带 paper/repo，这里只列"必读的一手解读 + 值得亲手翻的榜"。链接均为 2026-07 核实可达。

1. [Introducing SWE-bench Verified（OpenAI）](https://openai.com/index/introducing-swe-bench-verified/) — 官方讲原始集哪三类坏题（误判、描述不足、测试过 specific）、怎么人工筛出 500 题、GPT-4o 分数为何翻倍；引用 Verified 数字前必读 · 预计 15 min
2. [τ-bench: shaping the development and evaluation of agents（Sierra）](https://sierra.ai/blog/tau-bench-shaping-development-evaluation-agents) — pass^k 的设计动机与 user simulator + DB 终态比对架构的官方解读，比论文短 · 预计 10 min
3. [τ²-bench: benchmarking agents in collaborative real-world scenarios（Sierra）](https://sierra.ai/blog/benchmarking-agents-in-collaborative-real-world-scenarios) — dual-control 的定义与 telecom 域为什么难的官方博客 · 预计 10 min
4. [τ-bench 论文](https://arxiv.org/abs/2406.12045) — pass^k 公式、评分实现与失败分析章节值得细读（对话分支敏感性的证据在这） · 预计 30 min
5. [AgentDojo 论文](https://arxiv.org/abs/2406.13352) — utility/ASR 双指标与"攻防都是可编程组件"的框架设计，安全 eval 设计题的底稿 · 预计 30 min
6. [SWE-Bench Pro 论文](https://arxiv.org/abs/2509.16941) — copyleft 防污染 + held-out 商业集的三层集合设计，读第 2-3 节即可 · 预计 20 min
7. [OSWorld 官网 + verified leaderboard](https://os-world.github.io/) — 看官方"unified settings"下的 verified 榜，体会 step 预算/模态怎么切分呈现 · 预计 10 min
8. [Terminal-Bench 2.0 leaderboard](https://www.tbench.ai/leaderboard/terminal-bench/2.0) — 每条 entry 标注所用 agent harness 且轨迹公开可查——"系统分不是模型分"的最好实例 · 预计 5 min
9. [GAIA leaderboard（HF Space）](https://huggingface.co/spaces/gaia-benchmark/leaderboard) — 翻两页看条目命名（model+scaffold 组合），直观感受榜单比的是 system · 预计 5 min
10. [WebArena 官网](https://webarena.dev/) — WebArena 家族入口（VisualWebArena、TheAgentCompany 等），了解自托管环境这条路线的全貌 · 预计 5 min
