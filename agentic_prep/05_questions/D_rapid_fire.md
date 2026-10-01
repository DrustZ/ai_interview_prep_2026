# D 类 · 概念快问 20 条

⏱ 约 8 分钟读完 ｜ 20 条全部过一遍，答不顺的条目回 [../01_core/](../01_core/README.md) 定点重读

来源：agentswarms.fyi（42+ 题聚合，称源自 Glassdoor/Blind）与 buildml substack 两个独立整理源高度重合的清单（标 ✅），加两条单源真题（标 ⚠️）。每条答案 ≤2 句，是"开口第一句"而非完整答案；追问展开见各条链接。

## Agent 基础与编排

**[D1] ✅ Agent 和 workflow/chain 的区别是什么？**
Workflow 是代码预先编排的固定步骤，agent 是模型在循环中根据 observation 自主决定下一步（选工具、终止）。生产默认从 workflow 起步，只有分支不可枚举时才上 agent。

**[D2] ✅ 最小 agent loop 需要哪些组件？**
Model + tool registry/执行器 + 状态（消息历史）+ 终止条件（得到答案 / max steps / 成本预算）。缺终止条件就是 runaway agent。

**[D3] ✅ 解释 ReAct，什么时候不用它？**
交替 reasoning/acting，每步基于最新 observation 决策，比单步 prompt 更能纠错。单跳任务、延迟敏感、步骤可预排时不用——改单次调用或 plan-and-execute。

**[D4] ✅ Plan-and-Execute vs ReAct 的取舍？**
前置 plan 省 token/延迟、子任务可并行，但 plan 错了成本高、必须有 replan 机制。环境反馈密集或不可预测时 ReAct 更稳。

**[D5] ✅ 怎么防止 agent 陷入无限循环？**
Max steps + token/成本预算是硬护栏；再加进度检测（state/action 哈希去重、连续无进展计数），触发即降级或升人工。

**[D6] ✅ 生产 agent 的 tool-call 失败怎么处理？**
先分类：可重试（超时/限流→指数退避）vs 不可重试（参数错→把结构化 error 回传给模型让它自修复）。连续失败降级到备用路径或升人工，错误信息不泄内部栈。

**[D7] ✅ RAG 和 tool-calling 的区别、各用在什么时候？**
RAG 解决知识注入（静态语料问答，无状态单趟），tool-calling 解决行动和实时数据。RAG 可以只是 agent 的一个 tool；"觉得检索不够就改写 query 重试"就是 agentic RAG 的分界（New Relic 真题 "What do you know about RAG and Agentic AI?" 同此答）。

**[D8] ✅ 什么时候不用 agent framework、自己写编排？**
核心循环不到百行时自写更可控——framework 的抽象在 debug、eval、版本锁定上反而加成本。编排逻辑放 orchestrator 代码里，不塞进 prompt。

**[D9] ✅ Agent 怎么决定"继续想"还是"动手"？**
本质由 prompt 契约 + loop 设计决定：每步要求模型输出显式的 thought→action/final 选择，外层用预算和进度信号裁决。信息不足时鼓励先调只读工具而不是空想。

## Eval 与可靠性

**[D10] ✅ 什么是 eval harness？为什么生产 agent 必须有？**
版本化的任务集 + 环境 + grader 组成的自动评估管线。没有它，任何 prompt/模型/工具变更都是盲改——eval 是 agent 系统的 CI。详见 [../01_core/06_eval_security.md](../01_core/06_eval_security.md)。

**[D11] ✅ LLM-as-judge 有哪些失败模式？**
位置偏差、长度偏好、自我偏好（judge 与被测同源）、judge 随版本漂移。必须用人工标注校准一致率，并把 judge 本身纳入回归监控。

**[D12] ✅ 非确定性 agent 怎么测试？单测不管用怎么办？**
协议层 mock 模型照常单测；行为层用 golden set 统计通过率（pass@k / pass^k）、trace 断言（"必须调过 X 工具"）和 trajectory 级评估，设显著性阈值而非期待逐位相同。

**[D13] ✅ Prompt/RAG/agent 的回归测试长什么样？**
任何 prompt、模型版本、工具 schema 变更都要过离线 eval gate，按 slice 与基线做 paired 比较。生产失败 trace 去敏后回填成新回归用例。

**[D14] ✅ 长多步交互的 agent 行为怎么评估？**
单步指标不够，要 trajectory 级：目标完成率、步数/成本效率、中途违规、以及关键节点的 milestone 断言。τ-bench 的 pass^k 衡量"同一任务跑 k 次全成功"的一致性（见 [../04_benchmarks.md](../04_benchmarks.md)）。

**[D15] ✅ 凌晨 3 点生产 agent 对某客户出错，怎么 debug？**
拉 trace 回放完整决策链→查工具调用 I/O→diff 最近 prompt/模型/工具变更→判断模型漂移还是数据问题；先用一键降级/关自治的开关止血，事后把案例回填回归集。

## 安全

**[D16] ✅ Prompt injection 有哪些注入面，怎么防？**
直接（用户输入）和间接（检索文档、网页、工具返回值里的指令）。Prompt 层防御不充分，要靠架构：untrusted 数据标记、权限最小化、敏感操作确认、输出过滤。

**[D17] ✅ 部署自治 agent 要考虑哪些安全风险？**
最小权限工具 + 沙箱执行 + 审计日志是底线；风险面包括数据外泄、预算失控、被注入后"代表用户"行动。高风险写操作一律 proposal→human approval→幂等执行。

**[D18] ✅ MCP 是什么，为什么重要？**
模型-工具连接的开放协议（tools/resources/prompts 三原语），把 M×N 集成变成 M+N。代价是第三方 server 引入供应链与注入新风险——详见 [../03_gaps/mcp.md](../03_gaps/mcp.md)。

## Memory 与 Context

**[D19] ✅ Lost in the Middle 是什么，对 agent 设计有什么影响？**
长 context 中部信息召回率显著下降。所以关键指令/证据放头尾，宁可检索精选注入，也不塞满窗口；大窗口≠免费——成本线性涨、注意力稀释、prefill 延迟涨。

**[D20] ⚠️ Agentic training 时工具返回内容要不要 mask？（快手真题，2026 agentic 后训练岗高频）**
要 mask：tool observation 是环境产生而非策略产生，计入 LM loss 会让模型学"预测环境"并稀释决策信号。SFT 对 tool-return span 置 loss mask，RL 的 importance ratio 也只在策略生成的 token 上算——与 Anthropic GRPO debug 轮（[C6](C_live_ai_coding.md#c6)）的 masking 考点直接呼应。
