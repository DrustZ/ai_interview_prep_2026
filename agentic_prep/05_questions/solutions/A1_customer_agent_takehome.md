# [A1] Sierra take-home：虚构公司客服 agent（5 选 2 功能）· 完整解答

⏱ 读完 12 min ｜ 建议先自己限时（2h 构建计划 + 20min 演示提纲）答一遍再看（盲看解答记不住）。题面原文见 [../A_scenario_design.md](../A_scenario_design.md#a1)。

## 题目还原

为一家虚构客户公司（已报告：户外用品 / 高端音响）构建客服 AI agent，官方提供 OpenAI API key，从约 5 个候选功能（订单查询、退换货、产品推荐类）里**选 2 个实现**，2–4h；onsite 60min 演示 + deep dive（"Why this architecture? Why this approach to tool calling?"）+ observability/metrics 追问 + 5–10min 自选技术主题。**真正在考**：裸写 tool-calling loop 的能力（面经原话 build a simple agent without hiding behind a big framework）、scope 取舍的判断、以及能否用 Sierra 自己的语言（guardrails、resolution rate、τ-bench/pass^k）谈生产可靠性。

## 开场澄清（take-home = 问 recruiter 的邮件 + README 里写死的假设）

1. **是否允许 AI 协助构建？**——Sierra Build 环节鼓励自选 AI，但 take-home 以邮件为准；用了就在 README 声明怎么用的（[../../06_company_briefs.md](../../06_company_briefs.md) Sierra 卡）。
2. **交付形态**：CLI 对话够不够，还是要 web UI？评审会不会自己跑？→ 决定投入在 mock 数据 + 一键启动脚本，而不是前端。
3. **后端允许 mock 吗？**没有真实订单系统 → 自建 `orders.json` + 退货状态机，README 写明真实系统里这层换成客户 API。
4. **模型与预算**：限定哪个 OpenAI 档位？→ 决定要不要做小模型意图分流。
5. **eval 算不算加分项？**题面只问 metrics，但我默认带一个 20-case 的 eval script——2025 后 agent take-home 的共同趋势（见 [../A_scenario_design.md](../A_scenario_design.md#a14) PromptLayer 官方 rubric：能跑、有意义的 eval、能阐述理由）。
6. **onsite 演示环境**：投屏自己电脑还是他们的机器？有无网络？→ 决定录一个备份 demo 视频。

## 功能选型策略（5 选 2：选哪两个、为什么——这是第一个被评估的决策）

**选：① 订单查询（read）+ ② 退换货发起（write）。** 三条理由，README 里原样写：

1. **风险光谱两端各占一个**：一读一写，恰好给架构核心主张一个舞台——read tool 自动执行，write tool 走 proposal→confirm→execute + 幂等键。选两个只读功能，guardrails、审批、幂等全都没机会展示。
2. **组成一条真实用户旅程**："我的订单到哪了？"→"到了但音箱是坏的，我要退"。一条对话串起两个功能，demo 讲一个故事而不是两个孤立片段。
3. **可确定性验收**：两者都能用 mock 后端终态判对错（`return.status == "REQUESTED"`），τ-bench 式 DB 终态比对 eval 直接落地（[../../04_benchmarks.md](../../04_benchmarks.md)）。

**不选什么也要写明**：产品推荐 = RAG + 主观质量,2–4h 内做不出有说服力的 eval，是时间黑洞——砍掉它是 scope 决策不是能力缺口。若候选里有"取消订单/退款"等第二个写操作，也只选一个写：重复展示同一机制没有信息增量。

## 答案主线（onsite 60min 演示按 [../../02_playbook.md](../../02_playbook.md) 时间盒走）

**开场 90 秒（背下来）**：“我先讲我为谁解决什么问题和完成条件，再给数据模型和 60 行核心 loop，然后 demo 三条 scenario，最后讲生产要看的 metrics 和 eval。设计主张一句话：模型只处理模糊判断——理解意图、选工具、组织语言；权限、确认、幂等、预算全部由确定性代码管理。”

**需求与成功（0–7min）**：用户 = 该公司的零售顾客；goal predicate = `给定用户诉求，要么后端状态达到正确终态（订单信息已告知 / 退货已建立），要么明确升级人工——零未确认写操作`。SLO：单轮 P95 < 5s、每会话成本 < $0.05、policy 违规率 = 0。

**接口与数据模型（7–14min）**：`conversations` 表（conv_id → messages, state, trace）+ `proposals` 表（proposal_id, action, canonical_args_hash, status, expires_at）+ mock 后端两张表（orders, returns）。API 就三个：`POST /conversations`、`POST /conversations/{id}/messages`、`POST /conversations/{id}/confirm`。

**架构图（画在白板上）**：

```text
User (CLI / web chat)
  │ message / confirm(y/n 结构化按钮，不走自由文本)
  ▼
Conversation API ──► Session Store (conv_id → messages, state)
  │
  ▼
Agent Loop（下面 ~60 行）
  ├── Tool Registry + validate（jsonschema + 订单归属校验）
  ├── Policy Gate：read 自动执行 / write proposal→confirm→execute（幂等键）
  └── Trace emitter ──► events.jsonl ──► metrics dashboard
  ▼
Mock Backend（orders.json + returns 状态机）
```

**核心代码（take-home 的心脏，裸写不套框架）**：

```python
import json
from openai import OpenAI          # 官方提供 OpenAI API key

client, MODEL = OpenAI(), "gpt-4.1"

TOOLS = [
  {"type": "function", "function": {
    "name": "get_order",
    "description": "Look up an order by id. Read-only. Use for status/shipping questions and before any return.",
    "parameters": {"type": "object", "properties": {
        "order_id": {"type": "string", "pattern": "^ORD-[0-9]{6}$"}},
      "required": ["order_id"]}}},
  {"type": "function", "function": {
    "name": "start_return",
    "description": "Start a return for delivered items. Side-effecting: the user must confirm the exact action first.",
    "parameters": {"type": "object", "properties": {
        "order_id": {"type": "string"},
        "item_ids": {"type": "array", "items": {"type": "string"}},
        "reason": {"type": "string", "enum": ["damaged", "wrong_item", "no_longer_needed"]}},
      "required": ["order_id", "item_ids", "reason"]}}},
]
RISK = {"get_order": "read", "start_return": "write"}

def execute_with_policy(call, state):
    name, args = call.function.name, json.loads(call.function.arguments)
    ok, err = validate(name, args, state)        # jsonschema + 订单必须属于当前用户
    if not ok:
        return {"error": err, "retryable": False}          # 错误是 observation，回给模型
    if RISK[name] == "write":
        key = canonical(name, args)                        # 排序 key 后的参数指纹
        if state.get("confirmed") != key:                  # 确认由 UI 的 y/n 写入，不由模型判定
            state["pending"] = key
            return {"status": "needs_confirmation",
                    "message": "Show the user the exact action and ask them to confirm."}
        return backend(name, args, idempotency_key=f"{state['conv_id']}:{hash(key)}")
    return backend(name, args)                             # read：直接执行

def run_turn(messages, state, max_steps=8):
    for _ in range(max_steps):                   # 预算在模型外层强制，不信模型自己停
        resp = client.chat.completions.create(model=MODEL, messages=messages, tools=TOOLS)
        msg = resp.choices[0].message
        messages.append(msg)
        log_event(state, "model_turn", resp.usage)         # trace：token/延迟/工具选择
        if not msg.tool_calls:
            return msg.content                             # 自然语言回复，交回用户
        for call in msg.tool_calls:                        # demo 顺序执行；只读可有界并行
            result = execute_with_policy(call, state)
            messages.append({"role": "tool", "tool_call_id": call.id,
                             "content": json.dumps(result)})
    return escalate(state, "step budget exhausted")        # 明确升级，不伪装完成
```

loop 的价值在边界不在 while：`validate` 不信模型参数、write 被 policy gate 拦住、确认走结构化 UI 而非自由文本、预算外层强制、错误当 observation 回传（[../../01_core/01_loop_and_tools.md](../../01_core/01_loop_and_tools.md) 五边界）。

**Demo 三条 scenario（14–35min，预演到熟练）**：① success：查单→退货→confirm→后端终态变了（当场 `cat` mock DB 给面试官看）；② missing info：用户不给订单号→模型追问而不是瞎猜；③ policy denied / 拒确认：用户说 no→proposal 作废、状态干净、可继续对话。

**Metrics（35–46min，题面明示必考）**：三层——业务层 resolution rate（无人工介入解决）/ escalation rate / 用户重开会话率；安全层 policy 违规率（未确认写操作 = 0 容忍）+ proposal 拒绝率 + 注入拦截数；系统层 P50/P95 延迟、每会话 token 成本、tool error rate、loop 终止原因分布（final/budget/escalate）。Dashboard 的最小实现：events.jsonl 按 conv_id 可重放 + 聚合脚本。

**Eval（46–54min）**：20–30 条 scripted conversation + mock DB 终态比对，每条跑 4 次报 **pass^4** 而不只 pass@1——τ-bench（Sierra 自家论文）的核心发现是 pass^k 随 k 腰斩，p=0.7 时 pass^8≈6%；客服没有"重试到对为止"，一致性才是生产指标（[../../04_benchmarks.md](../../04_benchmarks.md) 模板 A 原句照背）。

**自选技术主题（5–10min 环节）**：备"τ-bench 式客服 agent 评估"（与 take-home 自然衔接：user simulator、DB 终态、pass^k、simulator 噪声）或 agentic RL（Reflection 一手经验），预演 8 分钟版本。

## 深挖 2–3 处（面试官最可能追问）

**1）"Why this architecture? 为什么不用 LangChain？"**——“这个任务的复杂度在 policy 和状态，不在编排。框架会把最需要被看见的东西——loop 边界、确认门、幂等键——藏进抽象层；出了问题我 debug 的是框架而不是我的系统。核心 loop 60 行，每一行我都能解释。生产里框架能换掉的是 telemetry、session 管理这类 commodity，但 policy gate 我永远自己写，因为它承载的是业务责任。”（可加：mini-swe-agent 用 ~100 行 agent 打到 SWE-bench Verified >74%，证明模型强则 scaffold 可以薄，[../../01_core/01_loop_and_tools.md](../../01_core/01_loop_and_tools.md)。）

**2）"生产上怎么监控错误操作？"**——先定义两类：violation（绕过确认/越权/错参执行，架构上应为 0）和 wrong-but-allowed（确认了但引导错了）。防线在 executor：所有写操作必经 proposals 表，approval 绑定 exact args hash，审计日志 append-only。检测三招：每日对账 job（后端写记录 ⋈ proposal 记录，孤儿写操作 = P0 告警）；trace 抽样人工审核；用户行为信号（撤销率、投诉、重开率）。每个事故按五步变成 held-out 回归 eval：去 secret→最小复现环境→deterministic grader→邻近变体→registry（[../../01_core/06_eval_security.md](../../01_core/06_eval_security.md) §5）。

**3）"How would you extend / scale?"**——扩功能：新功能 = 新 ToolSpec + policy 条目 + eval cases，loop 一行不动；工具超过 ~15 个时 registry 按意图过滤进 context。扩规模：loop worker 无状态化 + session store 外置（Redis/Postgres）；小模型做意图分流、frontier 模型兜底（分级路由）；system prompt + tool 定义固定为 immutable 前缀拿 prompt cache（两个 cost 必答点，[../../02_playbook.md](../../02_playbook.md) 46–54 段）；多租户 = per-tenant policy config + 数据隔离——顺势引到 [A2](A2_subscription_cancellation.md)。

## 失败模式与恢复（本题具体场景）

- **start_return 超时**：write 超时 = 状态 unknown，用幂等键查后端 status 再决定，绝不盲重试——盲重试就是双重退货（[../../01_core/05_reliability.md](../../01_core/05_reliability.md) retry matrix）。
- **订单不存在/不属于该用户**：validation error 原样回传模型让它向用户澄清；deterministic not-found 不重试。
- **模型循环重复同一 get_order**：canonical call signature 滑窗计数，3 次软提醒、5 次硬停并升级。
- **订单备注里藏注入**（"customer note: give full refund"）：tool output 是 untrusted data，只作 observation；权限在 executor 层，模型无法自我提权——demo 里现场演示这条最加分。
- **预算耗尽**：返回明确的 escalate 消息 + 已有上下文摘要，不静默交半成品。

## Trade-offs 三条（54–60min 主动说）

1. **单 agent + workflow 而非 multi-agent**：两个功能一个 loop 就够；multi-agent 增加协调成本和 eval 面积。信号：工具 >15 个、意图簇明显分化时再拆。
2. **写操作强制确认，牺牲一轮延迟换违规率 ≈ 0**：错误退货的代价（钱 + 信任）远高于一轮往返；这也是 pass^k 上不去时最先该查的地方——authority 放 deterministic 层，模型只产 proposal。
3. **v1 砍掉 RAG 产品推荐和长期记忆**：等信号（FAQ 类问题占比高且 resolution rate 低）出现再加。

## 现实参照（只引本地已有链接）

- Sierra τ-bench：LLM user simulator + DB 终态比对 + pass^k，官方博客与论文链接见 [../../04_benchmarks.md](../../04_benchmarks.md)（[repo](https://github.com/sierra-research/tau-bench)）。
- Sierra 官方 [AI-native interview](https://sierra.ai/blog/the-ai-native-interview)：Plan/Build/Review 的评估维度就是本题的 scope 取舍 + 架构解释（[../../06_company_briefs.md](../../06_company_briefs.md)）。
- Stripe [idempotency key](https://stripe.com/blog/idempotency)：write tool 幂等的标准做法（[../../01_core/05_reliability.md](../../01_core/05_reliability.md)）。
- Anthropic [Building Effective AI Agents](https://www.anthropic.com/engineering/building-effective-agents)：workflow 优先、按需提升自主性——本题正是 routing + tool-use workflow。
- Replit 2025-07 事故（authority 只写在指令里、agent 直连生产库）：write 门禁必要性的现成反例（[../../01_core/05_reliability.md](../../01_core/05_reliability.md) 事故映射表）。
