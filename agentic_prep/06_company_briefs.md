# 06 · 公司速记卡（面试前 15 分钟专用）

⏱ 约 8 分钟读完 ｜ 面试前只看 ⭐⭐⭐ 部分（对应公司那一张卡 + 万能结尾）

来源等级见 [companies.json](../agentic/data/companies.json)；`🧪/role-derived` 练习绝不能在面试里说成真题。题号 → [05_questions/README.md](05_questions/README.md)。

## 通用前 15 分钟节奏

| 分钟 | 动作 |
|---|---|
| 0–2 | 确认时长、coding/design、**AI/联网/已有代码权限**（本页每张卡的 AI policy 行） |
| 2–6 | 背该公司五句必背 + 主练题题面 |
| 6–10 | 闭卷画 agent loop + state + tool policy |
| 10–13 | 准备一个失败恢复回答 + 一个 eval 回答 |
| 13–15 | 选个人素材：如何 scope、发现 AI 错误、用证据验证（Reflection 一手经历） |

---

## ⭐⭐⭐ Applied Compute · 7/14（今天）

- 形式与证据: 60min technical（official 排期，联系人 Zijian）；**零公开面经**（Glassdoor/Blind/1p3a 全空，2026-07-14 检索）；inferred 实操型——agent loop/eval runner/grader，或围绕 Agent Cloud 支柱（evals/sandbox/RL post-training/traces）的 design；创始人 ex-OpenAI Codex/o1（[出 stealth 报道](https://siliconangle.com/2025/10/30/former-openai-researchers-launch-applied-compute-80m-funding/)）。
- AI policy: 无任何公开政策 → **开场必问**；默认能解释每一行生成代码。
- 五句必背:
  1. EvalTask 固定 model/tool/data/environment/policy versions——可复现是一切的前提。
  2. outcome、policy、process graders 分开，deterministic 优先；grader 本身要防 reward hack（他家字面卖点）。
  3. 训练与 held-out 按 tenant/time 隔离；online RL 把 production traces 喂回训练时污染风险加倍。
  4. paired multi-trial + slices + confidence interval，不只报均分。
  5. production failure 先变可复现 eval，再决定改 tool/context/harness/model——这就是他们的 continual improvement loop。
- 主练题: [B5](05_questions/B_general_design.md)（🧪 对口）、[B6](05_questions/B_general_design.md)；快问 [D10–D14](05_questions/D_rapid_fire.md)。
- 若已面完 → 复盘六问见 [00_day_plan.md](00_day_plan.md#复盘六问每天睡前-5-分钟)，被问倒的点记进 [08_cheatsheet.md](08_cheatsheet.md) 页边。

> 高分句：production trace 先变成 versioned、可复现的 eval case，才有资格变成训练信号。

<details><summary>追问预演 + 个人素材</summary>

- 追问 1「grader 被 reward hack 怎么发现？」→ score 分布异常监控 + trajectory 抽样人工审计 + outcome/process grader 交叉验证；自动分涨而 human eval 不动就 gate 发布。
- 追问 2「production traces 回流 online RL，held-out 怎么防污染？」→ tenant/time 双维 split + trace 近重复指纹去重 + eval set 版本冻结、只增不改。
- 追问 3「sandbox 隔离怎么做？」→ Firecracker/gVisor microVM、网络出口白名单、执行预算与超时、Temporal 编排（全是他家 infra 原词）。
- 个人钩子：Reflection 做 post-training + agent infra，正好有 trace→eval→RL 信号这条 pipeline 的一手经验，直接讲你踩过的 leakage/reward-hacking 坑。

</details>

## ⭐⭐⭐ Sierra · 7/15

- 形式与证据: official [AI-native onsite](https://sierra.ai/blog/the-ai-native-interview)（Plan→Build 2h 自选 AI→Review）+ pilot debugging 轮（中型 codebase + 同事 draft PR，与 coding agents 迭代）；reported 经典 loop（Exponent/1p3a）= 60min 递进实用电面（markdown 分块/日志区间/循环引用）+ TS/React debugging（4–6 bugs，**禁 AI**）。7/15 这轮 60min 最可能是递进电面或 debugging。
- AI policy: **按环节而异**——Build 鼓励自选 AI，debugging 禁 AI；提前问 recruiter 本轮是否允许 AI、是否涉及 TS/React（多人报告的隐形硬门槛）。
- 五句必背:
  1. 递进电面：每个小问干净收尾（边界/空输入）再接下一层需求，前 2–3 问的完成质量决定印象。
  2. Plan 主动定义用户、价值、scope、done；Build 做独特 vertical slice，敢砍 CRUD/auth boilerplate。
  3. AI 先只读侦察，再给窄任务；Review 要解释 AI 用法，你对每个关键结论负责。
  4. 第 40 分钟冻结 scope，保测试和 demo。
  5. 可靠性用他家语言讲：τ-bench / pass^k（k 次全成的概率，k 增大 SOTA 骤降）、回放式回归 evals、guardrail/policy 遵从、resolution rate。
- 主练题: [C10](05_questions/C_live_ai_coding.md)、[C11](05_questions/C_live_ai_coding.md)、[C14](05_questions/C_live_ai_coding.md)（电面族）；[C9](05_questions/C_live_ai_coding.md)（debugging）；[A1](05_questions/A_scenario_design.md)、[A2](05_questions/A_scenario_design.md)。

> 高分句：客服 agent 的敏感操作（退款/取消）authority 放在 deterministic policy 层，模型只产 proposal——这也是 pass^k 上不去时最先该查的地方。

<details><summary>追问预演 + 个人素材</summary>

- 追问 1「markdown 为什么要 header-aware 分块？」→ 对应 RAG chunking 真实工程：块内语义完整、父 header 重复进块保上下文、size limit 下按层级递归切。
- 追问 2「agent 一致性怎么在生产拉上去？」→ 约束式 policy/guardrail + 回放回归 evals 防 regression + 轨迹蒸馏；pass^k 是度量不是目标。
- 追问 3「debug 时 AI 给了错误修复怎么办？」→ 先复现 bug 再让 AI 提案，用测试/日志证据验证；讲一个你真实否决 AI 的例子。
- 个人钩子：HCI PhD + Reflection agent infra——product sense 和 scope 裁剪正是他们 Review 的显式评估维度，主动展示。

</details>

## ⭐⭐⭐ Hark AI · 7/16

- 形式与证据: **先消歧**——目标是 hark.com（Brett Adcock 的 Hark Labs，San Jose），不是 gethark.ai/能源 Hark，用招聘邮件域名确认；零公开面经（2026-03 才[出 stealth](https://techcrunch.com/2026/03/24/meet-the-former-apple-designer-building-a-new-ai-interface-at-hark/)，~70 人）；inferred 60min 由 CUA/post-training 团队主持（lead Tanmay Gupta，CodeNav 作者），围绕 JD：RL post-training for coding agents、sandbox、reward modeling、SWE-bench。
- AI policy: 无公开政策 → 开场必问。
- 五句必背:
  1. 浏览器/VM 每 run 隔离；network/file/clipboard/credential policy 由 executor 强制，credential 永不进模型 context。
  2. Observation/Action typed 且绑定 page version，防 stale click；环境漂移要能检测 + 恢复。
  3. 模型产 proposal；validator 查 risk/target/authority/budget；不可逆操作过 human approval gate。
  4. Post-training reward 分 task success、policy compliance、efficiency；JD 原词：outcome/execution/process-based signals、GRPO/DPO、trajectory distillation。
  5. Held-out 加 indirect injection 与 irreversible-action canaries。
- 主练题: [B4](05_questions/B_general_design.md)（🧪 对口）、[C15](05_questions/C_live_ai_coding.md)；快问 [D16](05_questions/D_rapid_fire.md)、[D20](05_questions/D_rapid_fire.md)。

> 高分句：click 已发出但观察 timeout 时，副作用状态未知——重新观察页面判定，靠 operation key 幂等恢复，绝不盲重试。

<details><summary>追问预演 + 个人素材</summary>

- 追问 1「能力放端到端多模态模型还是 scaffold？」→ 按可靠性瓶颈分配：grounding 差→模型侧，long-horizon 规划/漂移恢复→typed actions + planner/verifier；这正是问他们的好问题（Adcock："digital humanoid that can navigate the entire internet"）。
- 追问 2「coding agent 的 reward 怎么设计防 hack？」→ execution-based reward（测试真跑）+ process 信号混合、held-out canaries、改 tests 直接判负（Anthropic take-home 事故是现成例子）。
- 追问 3「轨迹训练要不要 mask tool return？」→ 要，环境输出不是模型行为，进 loss 会算错 importance ratio（[D20](05_questions/D_rapid_fire.md)，2026 跨公司固定考点）。
- 个人钩子：Reflection post-training（GRPO 系）+ agent harness 一手经验，与该团队 JD 逐条对口，直接报你训过的规模和 eval 结果。

</details>

## ⭐⭐⭐ Humans& · 7/17

- 形式与证据: 零公开面经（含 1p3a 本地缓存，2026-07-14 检索）；official 四支柱：long-horizon & multi-agent RL、memory、user understanding（[TechCrunch $480M seed](https://techcrunch.com/2026/01/20/humans-a-human-centric-ai-startup-founded-by-anthropic-xai-google-alums-raised-480m-seed-round/)）；产品方向 "AI version of an instant messaging app"；工程栈 Convex(TS)/Next.js/React Native；**团队含 Reflection 校友**。
- AI policy: 无公开政策 → 提前问 recruiter（inferred 同类 lab 可能鼓励 AI 实操，未证实）。
- 五句必背:
  1. room event log 是事实源；summary 是可重建 view。
  2. Goal/Task/Artifact/Decision 都有 owner、version、provenance。
  3. worker 写 proposal/branch，不直接覆盖 shared state。
  4. preference、proposal、team decision 分开建模——个人偏好不等于团队决定。
  5. 多 agent 必须与 single-agent baseline 比 coverage/cost/latency；"是否真理解用户"这类 EQ 指标是他们真实在解的 eval 难题。
- 主练题: [B3](05_questions/B_general_design.md)（🧪 对口）、[B2](05_questions/B_general_design.md)、[B7](05_questions/B_general_design.md)；快问 [D14](05_questions/D_rapid_fire.md)。

> 高分句：memory 写入要有门槛、衰减和冲突消解，且对用户可见可编辑——user understanding 不是无限记录。

<details><summary>追问预演 + 个人素材</summary>

- 追问 1「跨会话用户画像怎么防串扰和隐私泄漏？」→ per-user namespace + 群聊内引用他人信息需 provenance 与权限检查；遗忘是 feature 不是 bug。
- 追问 2「怎么在线评估'模型理解了这个用户'？」→ 行为代理指标（建议采纳率、用户纠正率、re-ask 率）+ 回放固定轨迹离线对照 + human calibration 抽样。
- 追问 3「多 agent 在 messaging 里最常见失败模式？」→ authority 不明与 artifact 冲突：显式 owner、optimistic concurrency、冲突走 team decision 流程（[B3](05_questions/B_general_design.md) 主答案）。
- 个人钩子：双重连接——Reflection 校友在他们团队 + UW HCI PhD 与 "human-centric" 定位完全同频；主动讲你做过的 human-agent collaboration 研究。

</details>

## ⭐⭐⭐ Extend · 7/17

- 形式与证据: 无公开面经（Glassdoor 两个同名 "Extend" 都不是它，勿引用）；official [JD 五条](https://www.ycombinator.com/companies/extend) 几乎就是题单：layout-aware 多模态、长文档 novel chunking、data pipeline + eval、self-correcting system、复杂 LLM 技巧；YC W23、NYC ~25 人、客户 Brex/Chime/Checkr；inferred 60min = 文档抽取 agent 管线设计 + 评测，或 AI 辅助实操。
- AI policy: 无公开政策 → 开场必问。
- 五句必背:
  1. parse→split→classify→extract→validate→review 是 versioned artifact DAG。
  2. upload content hash、job id、webhook event id 分别防不同层的重复；`NEEDS_REVIEW` + correction 回流 API 是他家 HITL 核心机制。
  3. schema + domain invariants 比模型 confidence 更可靠；confidence 只用来路由人工。
  4. 模型路由双模式：performance（layout model/手写 VLM/frontier）vs light（小模型+启发式）——accuracy/latency/cost 三角是架构主轴。
  5. 文档是 untrusted data，不能修改 system/tool policy；eval 用 field-level accuracy + LLM-as-judge + semantic similarity，per-customer 回归。
- 主练题: [A4](05_questions/A_scenario_design.md)（🧪 对口）、[A3](05_questions/A_scenario_design.md)；快问 [D11](05_questions/D_rapid_fire.md)、[D13](05_questions/D_rapid_fire.md)。

> 高分句：低置信自动转人工、人工修正经 correction API 回流成回归 eval 和训练数据——这才叫 self-correcting system。

<details><summary>追问预演 + 个人素材</summary>

- 追问 1「跨页嵌套表格怎么处理？」→ semantic chunking 检测表格跨页边界 + table-to-HTML（markdown 表达不了嵌套单元格）+ bounding box citation 保可溯源——全是他家产品原词。
- 追问 2「correction 数据怎么形成 flywheel 而不学进噪声？」→ 修正带 reviewer id/时间/理由，先进 eval set 验证一致性再进训练；per-customer slice 防止一个客户的怪癖污染全局。
- 追问 3「500 页 mortgage package 怎么办？」→ 先 classify→split 按文档类型切、置信路由，低置信段落人工；长文档分层 chunking + 页级并行抽取再合并校验。
- 个人钩子：把 agent infra 经验翻译到文档域——HITL correction 就是 trace→eval→训练信号的同构问题，你在 Reflection 做过这个 loop。

</details>

## ⭐⭐⭐ Anthropic · 7/22

- 形式与证据: 60min technical screen = live Python、practical 递进非 LeetCode（interviewing.io/Exponent，reported）；agent/tool-use coding 轮频率上升（1p3a `agents-coding-llm-tool-use`，最近 2026-06-29）；**recruiter 会提前发不点名题目 blurb——把 blurb 映射到题族是最大备考杠杆**；2026 onsite 新增 AI-assisted coding 轮（Claude Code CLI）；性能 take-home 被 Opus 4.5 打穿后退役并[开源](https://github.com/anthropics/original_performance_takehome)（official blog）。
- AI policy: [官方现行版](https://www.anthropic.com/candidate-ai-guidance)（2025-07-10）：**live 与 take-home 默认禁 AI**，除非明确说明；店面允许查文档/网页（考察 research 能力）；收到 blurb 邮件时一并跟 recruiter 确认本轮是否 "may use Claude"。
- 五句必背:
  1. 完整 assistant `tool_use` content 进 history；下一条 user message 一次回传所有匹配 ID 的 `tool_result`。
  2. tool exception 是 observation：以 error result 回传，不把整个 run 打死。
  3. 只读独立 calls 有界并行；副作用不自动并行。
  4. max steps/time/tokens/cost 在模型外层强制。
  5. workflow 优先；只有路径不可预知且收益明确时才提高自主性（他家 blog 原则）。
- 主练题: [C1](05_questions/C_live_ai_coding.md)、[C2](05_questions/C_live_ai_coding.md)、[C5](05_questions/C_live_ai_coding.md)、[C6](05_questions/C_live_ai_coding.md)、[C8](05_questions/C_live_ai_coding.md)；SD 备选 [A5](05_questions/A_scenario_design.md)、[A6](05_questions/A_scenario_design.md)；快问 [D20](05_questions/D_rapid_fire.md)。

> 高分句：payment tool timeout 后不重试也不放弃——用 operation key 查外部真实状态，按结果决定 resume 还是补偿。

<details><summary>追问预演 + 个人素材</summary>

- 追问 1「GRPO loop 里 importance ratio 恒 ≠ 1，哪错了？」→ tool return 没 mask：环境输出被当成模型行为进了 loss/ratio 计算（[C6](05_questions/C_live_ai_coding.md) + [D20](05_questions/D_rapid_fire.md)，Reflection 一手经验直接讲）。
- 追问 2「tool 结果里出现'ignore previous instructions'？」→ tool result 是 untrusted data：只作 observation 参与推理，权限与状态迁移在 deterministic 层，模型无法自我提权。
- 追问 3「为什么不并行执行这两个 write calls？」→ 副作用顺序依赖 + 失败补偿复杂度；只读才自动并行，write 走顺序 + operation key。
- 流程暗知识：技术轮挂了会静默取消后续；culture/values 轮是技术全过后最常见挂点——提前备好 AI-safety 立场的真诚回答。
- 个人钩子：Reflection post-training + agent infra 双覆盖 C1/C6 两大题族；HCI PhD 讲 Prompt Playground（A6）的产品视角。

</details>

---

## 附录：后续公司 5 行速记（不做新挖掘，压缩自 v1）

### OpenAI · TBD（in process，联系人 Tiancheng）

1. 形式: phone 60min 单题 3–5 渐进小问（前 2–3 问要干净写完+边界）→ loop 4–6 轮，HM BQ/deep dive 是 gated 轮；onsite 试点 agentic coding beta（现有 codebase + 期望用 AI，其余轮严格禁 AI）。
2. 给 agent 地图而非千页说明书；tests/logs/metrics/UI 对 agent 可读，缩短 feedback loop。
3. architecture/taste invariants 用 lint/CI enforce；plan/progress/decisions 存 repo artifact，不依赖聊天记忆。
4. 现有代码任务流程：侦察→验收标准→窄修改→最小测试→完整回归→diff review；题面超长化是刻意考需求提取。
5. 主练: [C16](05_questions/C_live_ai_coding.md)、[C18](05_questions/C_live_ai_coding.md)、[A9](05_questions/A_scenario_design.md)（Design Sora＝GPU job scheduler）、[A10](05_questions/A_scenario_design.md)。

### xAI · TBD

1. server-executed 与 client-executed tools 的信任/责任边界不同。
2. opaque continuation state 也要加密持久化 + expiry。
3. 实时回答标 cutoff time、sources、uncertainty；搜索内容永远 untrusted。
4. 多 agent 放大 token/tool cost，controller 必须有 global budget。
5. 主练: [B8](05_questions/B_general_design.md) 变体 + `q-xai-tool-runtime`；追问 provider schema 变化与 code sandbox。

### Physion Labs · 7 月底/8 月初 co-work session

1. 先定义 physics failure ontology 与事件级 annotation，再谈模型。
2. 可测属性用 tracking/geometry/simulator；模糊属性才用 calibrated judge（judge 引用 frame/time span + confidence）。
3. 实验保存 data/model/code/seed/environment provenance。
4. uninterrupted 与 checkpoint-resume 序列必须完全对照；备好同源 judge bias 回答。
5. 主练: `q-physion-video-eval`；co-work 前确认工具/数据/联网范围。

### Valkai · **7/17 周五 3:30–4:30 PM EDT**（technical，Lauren Zhu）

- **形式已确认（official 邮件）**：60 min live working session（Google Meet）——**build a CLI chat agent with memory**。开场才给 starter repo + brief（含 basic test harness）；工程师只观察不 pair。提前装好 git/uv/python，**AI 环境明确允许**（Claude Code 等）。
- **评分点（邮件原文）**：memory system 的思考 ｜ architecture & code taste ｜ scope 与优先级 ｜ 在 test harness 上扩展 + edge cases + 验证 ｜ **结尾 walkthrough 权重很大**。
- **备战材料**：`../projects/valkai_agent/`（模拟题 + 实现计划 + 练习实现）；memory 设计对齐 [01_core/02](01_core/02_state_and_memory.md) 的写入 gate/supersede。
- 领域底色（聊产品时用）：
  1. source/version/ACL 是事实层，embedding 只是检索索引。
  2. claim graph 保留支持/反驳/未知 + exact citation；撤稿按 provenance 传播。
  3. 模型产 ActionProposal；policy engine 决定 allow/deny/approval。
  4. 批准绑定 exact args/hash/expiry/policy version。
  5. 主练: `q-valkai-regulated-approval` + [A16](05_questions/A_scenario_design.md)（受限域题族）。

### Miru · TBD（Jimmy 面聊）

1. 公司身份未核实——先确认公司、岗位、面试形式、AI 权限，不猜产品。
2. shared object versioned，写入用 optimistic concurrency。
3. draft/propose/approve/send 分离；handoff 带 evidence、未决问题、next action。
4. 准备一个你用 AI scope、验证、纠错的真实故事。
5. 主练: `q-miru-shared-inbox` 仅作通用协作练习。

---

## 万能结尾（任何公司时间到时用）

1. "v1 的完成条件是环境状态 X，验证由 Y 完成。"
2. "最大风险是 Z，所以 authority 放在 deterministic policy/approval 层。"
3. "崩溃后从 checkpoint/event 恢复，外部副作用按 operation key 查状态。"
4. "上线走 offline held-out → shadow → canary；同时看 outcome、policy、cost、latency。"

> 高分句：AI 使用权限不能从题型或公司文化推断——除非明确书面/口头允许，一律按不允许处理。
