# Design an Agentic AI System That Adapts to New Tasks

这是一道独立的 ML system-design 题，不是股票 tool-use coding 题的下一 Level。
目前本地只有公开题目标题和准备方向，以下是面试答案框架，不冒充官方标准答案。

## 1. 目标与边界

输入一个过去没见过的自然语言任务。系统应发现可用工具和相关经验，制定计划、执行、
观察结果并修正，最终返回可验证答案或升级给人。这里的“适应”优先指运行时检索工具、
示例和记忆后重新规划，而不是在线修改基础模型权重。

首先澄清：任务类型、允许的副作用、延迟/成本目标、数据敏感度、成功标准，以及哪些动作
必须人工批准。

## 2. 核心架构

```text
User/API
   │
   ▼
Orchestrator ──► Policy / Budget / Approval Gate
   │                         │
   ├──► Planner              └── reject / dry-run / human approval
   ├──► Tool Registry + typed schemas
   ├──► Sandboxed Executors
   ├──► Working Memory / Context Manager
   ├──► Episodic + Semantic Memory / Example Retrieval
   └──► Verifier / Termination Controller
```

Orchestrator 把一次运行保存成可恢复状态机：`PLANNING → ACTING → OBSERVING →
VERIFYING → DONE/FAILED/WAITING_FOR_HUMAN`。每一步都有 trace、输入输出摘要、成本和
幂等键，进程崩溃后可以继续，而不会重复付款或发送消息。

## 3. Plan → Act → Observe

1. **Plan**：分解目标，声明每一步的预期结果和成功条件。
2. **Discover**：根据任务检索少量相关工具 schema、过去成功案例和领域规则。
3. **Act**：policy engine 校验权限、参数和副作用；只读独立调用可并行，有副作用的调用
   串行并使用幂等键。
4. **Observe**：工具结果作为不可信数据进入 context，不允许覆盖 system policy。
5. **Verify/Reflect**：用确定性校验器优先验证；必要时让模型反思失败并生成下一步。
6. **Terminate**：成功条件满足才结束，否则在预算内继续，或明确失败/请求人工帮助。

## 4. Memory 与适应新任务

- **Working memory**：当前目标、计划、最近观察；通过摘要和 context budget 控制长度。
- **Episodic memory**：历史 trajectory、工具错误和最终结果；只写入经过验证的成功经验。
- **Semantic memory**：产品知识、政策和文档，带版本、来源与权限。
- **适应流程**：任务 embedding/分类 → 检索相似成功案例 → 发现候选工具 → 组合新计划 →
  执行后验证。低置信度或高风险任务交给人，而不是让 agent 自行扩大权限。

不要把未经验证的模型输出直接写成长久记忆，否则错误会通过 retrieval 被持续放大。

## 5. 安全与可靠性

- 工具 allowlist、最小权限 token、参数 schema、网络/文件 sandbox。
- 写操作先 dry-run；付款、删除、外发消息等经过人工批准。
- 最大 steps、wall-clock、tokens、费用、重复动作次数和输出大小限制。
- timeout、有限重试、指数退避、circuit breaker；区分可重试和永久错误。
- tool output 与网页内容视为潜在 prompt injection，只作为数据块传递。
- PII/secret redaction、审计日志、租户隔离和数据保留策略。
- stagnation detector：连续计划近似、同一错误重复或没有新证据时提前停止。

## 6. Evaluation

离线 golden tasks 使用 mock tools 保持可重复，覆盖正常、缺工具、工具失败、恶意结果、
长任务和高风险动作。主要指标：

- task success / verifier pass rate；
- tool selection、参数和调用顺序准确率；
- groundedness、引用完整性和幻觉率；
- unsafe-action / policy violation rate；
- steps、tokens、成本、p50/p95 延迟和人工升级率；
- 新任务类别上的成功率，以及记忆检索带来的增益。

LLM-as-judge 只用于难以程序化的质量维度，必须用人工标注校准；安全和业务不变量使用
确定性检查。上线先 shadow/canary，再按风险等级逐步开放动作权限。

## 7. 扩展路线

股票小项目已经实现了这个系统的最小切片：messages 是 working memory，模型产生计划，
registry 分发动作，`tool_result` 是观察，`end_turn/max_steps` 是终止。生产化再增加持久化
状态机、动态工具发现、memory retrieval、policy/approval 服务、sandbox 和 eval 平台即可。
