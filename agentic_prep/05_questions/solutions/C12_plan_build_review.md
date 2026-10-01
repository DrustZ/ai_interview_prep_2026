# [C12] Sierra 官方 AI-native onsite：Plan→Build→Review · 完整作战计划

⏱ 读完 12 min ｜ 必须提前彩排：用自己的 AI 环境跑一次"2h 从零到 demo"，盲看计划没用
题库原文：[../C_live_ai_coding.md#c12](../C_live_ai_coding.md#c12) ｜ v1 rubric：[../../../agentic/data/questions.json](../../../agentic/data/questions.json) → `q-sierra-plan-build-review`
同 onsite 其他轮：[C9 禁 AI debugging](C9_debugging_round.md) ｜ [C13 draft PR + agents](C13_draft_pr_round.md)

## 题目还原：这题真正在考什么

三段式：(1) **Plan**——与面试官共同构思产品；(2) **Build**——2 小时，自选 AI 工具，官方明确可裁 scope、可跳过 CRUD/auth boilerplate；(3) **Review**——现场 demo + 产品决策讨论 + code review + **解释自己怎么用的 AI**。
官方明说的信号：**agency**（卡住会不会 pivot）、**judgment**（scope 裁剪）、product sense、系统理解、数据模型与 extensibility、如何用 AI 本身。v1 rubric 权重：30% scope/product judgment、25% 可工作的 vertical slice、20% 技术边界、15% demo/review、10% AI 使用复盘——**scope 判断比代码量值钱**。

## 开场澄清（Plan 阶段该问的 5 个问题）

1. "用户最痛的**单一 journey** 是什么？"——逼出 vertical slice 的切口，防止做平铺 CRUD
2. "有哪些**不可违反的规则**（policy）？"——agent 题的差异化就在 policy check，这是你要 demo 的核心
3. "接真实 API 还是 **sandbox/fake service**？"——答案永远选 fake：demo 可复现、不用等外部依赖
4. "demo 时你想看到**成功还是失败**场景？"——埋钩子：我会准备 success + policy-denied 两条，失败处理才是产品判断的展示位
5. "2 小时结束时的最低验收是什么？"——把口头共识写成 3 条 acceptance，Review 时逐条对照（这就是 agency 的证据）

## 答案主线

### 总时间轴（Plan ~20min / Build 120min / Review ~20min）

| Build 阶段 | 时间 | 目标 | 砍点 |
|---|---|---|---|
| 骨架 | 0–30 | repo 初始化、fake service、agent loop 空转跑通、**先让 demo 路径 e2e 出字** | 不写 auth、不建 DB，内存 dict 即数据库 |
| 核心 slice | 30–90 | 一条 journey 完整：用户消息 → agent 调 tool → policy check → 执行/拒绝 → 带解释的回复 + audit log | 只做 1 个 write tool + 1 个 read tool；UI 用 CLI 或最简 chat 页 |
| 打磨 demo | 90–120 | 三个 scenario 脚本化可复现；写 README（跑法+架构 5 行）；**freeze——最后 20 min 不加 feature** | 样式、边缘 case、第二条 journey 全砍 |

硬规则：**60 分钟必须有可 demo 的东西**，哪怕 policy 还是硬编码。90 分钟一到强制切打磨——半成品第二 feature 是 0 分，能讲的取舍是满分。

### Plan 文档模板（Plan 阶段现场写给面试官看，10 行以内）

```markdown
# Order-Modification Support Agent — MVP Plan
User & journey: 已下单客户改收货地址（发货前）
Acceptance:
  A. 用户能用自然语言完成一次地址修改，agent 调 tool 真正改到 fake order
  B. 违反 policy 的请求（已发货）被拒绝，且给用户可读解释
  C. 每个 action 有 audit 记录（who/what/when/policy 结果）
Non-goals: auth、真实 DB、多轮澄清、退款/取消（说得出为什么砍）
Stack: Python + Anthropic API + fake OrderService（内存）+ CLI chat
Risk: LLM 输出不稳 → tool schema 强约束 + policy 在代码里而非 prompt
```

面试官改需求时改这个文档，不口头飘——"需求变更进文档"本身是信号。

### 架构（Build 前 2 分钟画，口述用）

```text
User (CLI/chat)
   │
Agent loop (LLM + tools)          ← 模型只做：理解意图、选 tool、组织解释
   │  propose ToolCall
Policy engine (纯函数, 确定性)     ← 规则不进 prompt：can_modify(order, change) -> allow/deny+reason
   │  allow → execute / deny → 把 reason 回给模型生成解释
Fake OrderService (内存 dict)
   └── Audit log (append-only list: actor, action, args, policy_result, ts)
```

一句话讲清技术边界（20% 分）："**模型处理模糊判断，policy 与状态由确定性代码管**——policy 写在 prompt 里模型会绕过，写在代码里我能单测。"这与 [../../02_playbook.md](../../02_playbook.md) 开场 90 秒同源。

### Build 阶段怎么驾驶 AI（现场 narration 配套）

1. 第一条 prompt 就把 Plan 文档整个喂给 agent："按此 plan 生成骨架：fake OrderService + 3 个 tool schema + agent loop，policy engine 留空函数我来写"——**policy engine 自己写**，它是 Review 时被 code review 的核心，必须每行都能辩护
2. 之后一次一个窄任务；每个 diff 跑 demo 路径验证再要下一个（详见 playbook 第八节）
3. 卡住 15 分钟 = pivot 信号：换实现方案或砍掉该子功能，**口头宣布 pivot 及理由**——这正是官方要看的 agency
4. 每 30 分钟 git commit——demo 崩了可以回退到上一个能跑的版本

### Review 讲稿结构（10 分钟，背这个骨架）

1. **对照验收**（1 min）："Plan 里三条 acceptance，A/B 完成，C 完成到 in-memory audit，没做持久化。"
2. **Demo**（4 min）：三条脚本按序跑——① success：改地址成功，指给面试官看 audit entry；② policy denied：已发货订单被拒 + 用户可读解释；③ missing info：agent 主动问单号（有就演，没有就口头讲设计）。**失败场景是主菜，放在讲解最细处**
3. **数据模型与扩展点**（2 min）：Order/Change/AuditEntry 三个模型；"加退款 = 新 tool + 新 policy 函数，agent loop 不动"——extensibility 是官方点名信号
4. **AI 使用复盘**（2 min）："骨架和 fake service 是 AI 写的，我逐个验收；policy engine 和 tool schema 我手写，因为它们是正确性核心；AI 有一处把 policy 检查放进了 prompt，我拒绝并改成代码检查。"——**必须有一个"我拒绝了 AI 建议"的实例**
5. **生产 gap**（1 min）：真实 API 的幂等与重试、eval harness、审批流、多租户——点到为止，展示知道 demo 与生产的距离

## 深挖 2-3 处（rubric 原生 follow-up）

**「如何从 0→1 扩到 1→N（更多 policy/journey）？」**
"Policy 从硬编码函数升级为声明式规则表（condition + action + reason 模板），policy engine 变成解释器；journey 增多后 tool registry 按意图分类过滤，避免 context 塞满所有 tool；每条新 policy 上线前跑回归 eval set——历史对话重放，确认旧行为不变。"

**「如何监控错误退款/错误修改？」**
"三层：(1) 事前——write tool 全走 policy engine，高风险 action（金额>阈值）转人工审批；(2) 事中——audit log 每条含 policy 判定依据，可回放；(3) 事后——线上抽样人工复核 + 用户投诉率/撤销率作 online metric，异常上升自动收紧自主权限（降级为 proposal-only）。"

**「怎样让业务用户改 policy 而无需改 prompt？」**
"这正是我把 policy 放代码不放 prompt 的原因：升级为规则配置（JSON/DSL + 后台界面），业务改的是数据不是代码；每次变更带 version，audit 记录用的哪个 version；变更先在 shadow mode 对历史流量重放看 diff，再生效。"

## 失败模式与恢复（现场）

- **90 min 核心 slice 还没通**：砍到只剩 policy-denied 路径（它不依赖 write 成功），demo 讲"拒绝+解释+audit"，这仍覆盖最有差异化的信号
- **demo 现场崩**：git 回退上一个 commit；同时口头走读代码讲设计——判断力分还能拿
- **LLM 输出不稳定**：demo 前把三条 scenario 各跑 2 遍；不稳就 temperature=0 + 在 system prompt 固定输出格式；再不稳就 demo 时念准备好的输入而非即兴
- **面试官中途加需求**：更新 Plan 文档，明说"接受，代价是砍掉 X"——scope 重协商本身是评分项

## Trade-offs 三条（Review 时主动说）

1. **Fake service 换 demo 可复现性**：牺牲真实性，换来 2h 内可控可重放；生产第一步就是替换为真实 API + 幂等 key
2. **单 journey 深做 vs 多功能平铺**：vertical slice 证明 e2e 能力，平铺 CRUD 什么都证明不了——官方原话允许跳过 boilerplate
3. **policy 硬编码 vs 配置化**：v1 硬编码换开发速度；出现"业务周更 policy"信号再上规则表（v2 路线已在深挖里给出）

## 现实参照

- Sierra 官方博客 "The AI-native interview"（题库与 v1 rubric 引用源）：官方案例是候选人 2h 做了 AI 游戏、面试官现场试玩——**demo 体验本身是产品分**
- 注意：社区面经仍报告 take-home + debugging 旧流程与此并存，**面前向 recruiter 确认场次格式**（题库 [C12] 原注）
- Agent 边界设计的完整语言见 [../../02_playbook.md](../../02_playbook.md)；coding agent 环境准备见 [../../01_core/03_harness_env_swe.md](../../01_core/03_harness_env_swe.md)
