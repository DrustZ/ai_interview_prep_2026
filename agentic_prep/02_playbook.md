# 02 · Agent System Design Playbook

⏱ 约12分钟读完 ｜ 面试前只看 ⭐⭐⭐ 部分

目标：任何 agent 题都能在 60 分钟内给出"可执行、可恢复、可评估"的设计，而不是只画模型和箭头。

## 一、开场 90 秒 ⭐⭐⭐

> 我先定义用户目标、完成条件、风险与允许自主性；然后给 API 和状态模型，再展开 agent loop、tools/context/memory；最后讨论恢复、安全、eval 和 rollout。模型只处理模糊判断，权限与状态由确定性 control plane 管理。

这句话让 interviewer 知道你会覆盖全局，且不会把可靠性寄托在 prompt 上。

## 二、60 分钟时间盒 ⭐⭐⭐

| 时间 | 阶段 | 必做 | 产出 |
|---|---|---|---|
| 0–7 | 需求与成功 | 问满六项，把目标写成谓词 | 目标：给定 $S_0$，在 policy $C$、budget $B$ 下达成 $P(\text{env})$ |
| 7–14 | 接口与状态 | 轻量类型 + 5 个 API | `ModelClient`/`ToolCall`/`ToolResult`/`RunState` |
| 14–25 | 主流程 | 走一条 success path，每个箭头讲清 | intake→…→finalize 全链 |
| 25–36 | Tools/Context/Memory/多 agent | 五个必答问题 | registry、context 预算、memory 分层 |
| 36–46 | 可靠性、安全、恢复 | 固定过一遍失败清单 | timeout/幂等/injection/租户 |
| 46–54 | Eval、observability、cost、rollout | offline/online/rollout/trace + **两个 cost 必答点** | shadow→canary→rollback |
| 54–60 | Trade-offs | 主动说三个 | 边界与 v2 信号 |

<details><summary>0–7：需求与成功（六问 + 目标谓词）</summary>

至少问六项：

1. 用户是谁，真实 job-to-be-done 是什么？
2. 输出是建议、proposal，还是会产生真实副作用？
3. 怎样从环境观察"完成"？
4. latency、cost、throughput、availability SLO？
5. 数据敏感度、租户、region、retention？
6. 人在哪些节点必须介入？

把目标写成一行：`Given initial state S0, achieve predicate P(environment) under policy C and budget B.`

</details>

<details><summary>7–14：接口与状态（轻量类型 + 最小 API）</summary>

先写这些轻量类型：

```python
class ModelClient(Protocol):
    def complete(self, messages, tools) -> "ModelTurn": ...

@dataclass(frozen=True)
class ToolCall:
    call_id: str
    name: str
    arguments: dict

@dataclass(frozen=True)
class ToolResult:
    call_id: str
    status: str
    output: object | None
    error_code: str | None
    retryable: bool

@dataclass
class RunState:
    run_id: str
    status: str
    step: int
    budget_used: int
    checkpoint_version: int
```

API 最少包含：

- `POST /runs`：创建 immutable TaskSpec。
- `GET /runs/{id}`：状态、结果、下一步需求。
- `POST /runs/{id}/cancel`：请求取消。
- `POST /runs/{id}/approvals`：批准 exact proposal。
- `GET /runs/{id}/events?after=`：trace 增量读取（同一条 event log 也支撑 streaming 续传，见 [03_gaps/streaming.md](03_gaps/streaming.md)）。

</details>

<details><summary>14–25：主流程（success path）</summary>

按一条 success path 走完：

`Task intake → classify/plan → context+tools → model turn → validate → policy → execute → observe → grade → finalize`

每个箭头回答三件事：谁调用、读写什么状态、失败返回什么。细节见 [01_core/01_loop_and_tools.md](01_core/01_loop_and_tools.md)。

</details>

<details><summary>25–36：Tools、Context、Memory、多 agent（五个必答）</summary>

- Tool registry 如何过滤到少量相关工具？
- 输入/输出 schema、risk、timeout、version 在哪里？
- 当前 context 为什么包含这些 token？
- 哪些信息属于 run state，哪些值得长期 memory？
- 子任务是否真的独立并行？谁聚合和验证？

</details>

<details><summary>36–46：可靠性、安全、恢复（失败清单）</summary>

固定过一遍：timeout、429、tool partial success、worker crash、stale result、重复副作用、取消竞态、prompt injection、越权、secret、租户泄露。逐条答法见下方"可靠性追问模板"。

</details>

<details><summary>46–54：Eval、observability、cost、rollout（含两个 cost 必答点）</summary>

- Offline：held-out tasks、deterministic outcomes、policy tests、adversarial tests。
- Online：success proxy、human correction、escalation、cost、latency、unsafe action。
- Rollout：shadow → canary → gradual → rollback。
- Trace：model/tool/state/approval/artifact，同时 redaction。

**两个 cost 必答点**（细节见 [03_gaps/cost_latency.md](03_gaps/cost_latency.md)）：

1. **Prompt cache 命中率靠前缀稳定性设计**：system prompt、tool 定义、few-shot 固定为 immutable 前缀；messages append-only；动态内容（timestamp、检索结果）放后缀，不打散前缀；cache hit rate 作为一级 cost 指标监控。
2. **模型分级路由**：classify/extract/routine 走 small model，plan/复杂推理走 frontier model；按 confidence/失败信号 escalate；路由决策写入 trace，eval 按 tier 分层报告质量与成本。

</details>

<details><summary>54–60：trade-offs（至少主动说三个）</summary>

1. 为什么现在用 single agent/workflow，而非更多 agents。
2. 哪一部分牺牲 latency 换 safety/correctness。
3. v1 不做什么，什么信号出现后再做。

</details>

## 三、白板架构模板 ⭐⭐⭐

```text
Client
  │ create/cancel/approve
  ▼
API + Auth ───────► Policy / Approval
  │
  ▼
Run Controller / State Machine ─────► Event Store / Checkpoints
  │                         └───────► Trace / Metrics
  ├── Context Builder ──────────────► Source + Memory + Artifacts
  ├── Model Adapter
  ├── Tool Scheduler ───────────────► Sandboxed Tool Workers
  └── Grader / Verifier ────────────► Final Domain State
```

如果是 multi-agent：在 controller 下增加 typed task queue；每个 worker 独立 context/artifact，不能直接共享模型消息或修改全局 plan。

## 四、关键数据模型 ⭐⭐

四个模型：TaskSpec（immutable 任务合同）、TraceEvent（可重放审计）、ActionProposal/Approval（精确审批）、EvalTask/TrialResult（可复现评估）。字段展开见折叠。

<details><summary>TaskSpec / TraceEvent / ActionProposal / EvalTask 字段与不变式</summary>

**TaskSpec**

```text
task_id, tenant_id, actor_id
goal, constraints, acceptance_checks
environment_version, tool_policy_version
max_steps, deadline, cost_budget
created_at
```

创建后 immutable。用户改变目标时生成新 version/event，不在背后改 prompt。

**TraceEvent**

```text
event_id, run_id, seq
span_id, parent_span_id
event_type, status
payload_pointer, schema_version
occurred_at, recorded_at
```

`seq` 提供 run 内确定顺序；`occurred_at` 处理分布式延迟。大 payload 存 object store，event 只存 pointer、hash 和 redacted summary。

**ActionProposal / Approval**

```text
proposal_id, action_name, canonical_args_hash
human_readable_effect, risk, expires_at
policy_version, created_by_run

approval_id, proposal_id, approver_id
decision, decided_at
```

任何参数改变、过期、policy version 不兼容都要求重新批准。

**EvalTask / TrialResult**

```text
EvalTask: task + initial snapshot + policy + graders + seed
TrialResult: outcome + trace + scores + cost + latency + error category
```

不要只保存最终文字，否则无法 debug trajectory 或发现 policy violation。

</details>

## 五、八类题一览 ⭐⭐⭐

| # | 题型 | 高分句（背） | 细节 |
|---|---|---|---|
| 1 | Tool-use agent | 工具描述影响选择，但权限不在描述里；executor 再做 authn/authz 与 validation | [01_core/01_loop_and_tools.md](01_core/01_loop_and_tools.md) |
| 2 | Memory/personalization | 先建可治理的 MemoryRecord，再选检索技术；相似度不是权限，也不是事实性 | [01_core/02_state_and_memory.md](01_core/02_state_and_memory.md) |
| 3 | Multi-agent collaboration | 按可独立验证的 artifact 分工，而不是让多个 agent 重复思考再投票 | [01_core/04_multi_agent.md](01_core/04_multi_agent.md) |
| 4 | Long-horizon/durable agent | 恢复的是 durable state，不是把旧聊天原样重新塞回模型 | [01_core/02_state_and_memory.md](01_core/02_state_and_memory.md) |
| 5 | Coding agent harness | 最有价值的改进往往是给 agent 更好的环境和 verifier，而不是让它"再努力一次" | [01_core/03_harness_env_swe.md](01_core/03_harness_env_swe.md) |
| 6 | Eval/training harness | 先问 eval 是否预测 production，而不是先优化 leaderboard | [01_core/06_eval_security.md](01_core/06_eval_security.md) |
| 7 | RAG/知识 agent | 先定权限与新鲜度，再谈 chunking 与 rerank | [03_gaps/rag.md](03_gaps/rag.md) |
| 8 | 用户可见的 streaming agent | streaming 是 UX 合同，不只是传输优化 | [03_gaps/streaming.md](03_gaps/streaming.md) |

<details><summary>1. Tool-use agent 展开重点</summary>

消息协议、schema、选择、并行、错误、预算、注入、审批。

</details>

<details><summary>2. Memory/personalization 展开重点</summary>

写入 authority、provenance、scope、time、TTL、纠错、删除、retrieval budget。

</details>

<details><summary>3. Multi-agent collaboration 展开重点</summary>

TaskSpec、独立 context、artifact handoff、global budget、conflict、verifier、single-agent baseline。

</details>

<details><summary>4. Long-horizon/durable agent 展开重点</summary>

state machine、event log、checkpoint、lease/fencing、幂等、unknown outcome、cancel、schema version。

</details>

<details><summary>5. Coding agent harness 展开重点</summary>

repo map、isolated worktree、tests/logs/UI 可读、小步验证、diff review、PR evidence、architecture invariants。

</details>

<details><summary>6. Eval/training harness 展开重点</summary>

task distribution、environment reset、outcome/process/policy graders、leakage、reward hacking、multi-trial statistics、rollout。

</details>

<details><summary>7. RAG/知识 agent 展开重点</summary>

- **ACL 前置过滤**：permission filter 在 retrieval 阶段进 query（metadata filter 或按 principal 分 index），绝不"检索完再删"——rank、count、snippet 都会泄露文档存在性；ACL 变更要能使缓存结果失效。
- **Chunking/hybrid/rerank**：结构感知切分（heading/section/code block 边界），chunk 带 doc_id、heading path、updated_at、acl metadata；BM25 + dense 融合（RRF）后 cross-encoder rerank 进 context 预算；先量 retrieval 的 recall@k，再调生成。
- **Citation 验证**：每个 claim 映射到具体 chunk span；无支撑的 claim 降级为"未找到依据"，而不是删 citation 留结论；grounding check 用 deterministic span 匹配 + judge 抽查。
- **Freshness**：index staleness SLO，写路径 event-driven re-index；版本冲突按 source authority + updated_at 裁决；答案附 as-of 时间。

细节见 [03_gaps/rag.md](03_gaps/rag.md)。

> 高分句：先定权限与新鲜度，再谈 chunking 与 rerank。

</details>

<details><summary>8. 用户可见的 streaming agent 展开重点</summary>

- **传输**：SSE（单向、proxy 友好），每个 event 带单调 event id；断线用 last event id 恢复，服务端从 event store replay——streaming 和 trace 共用 `GET /events?after=` 一条 event log。
- **中断语义**：用户 interrupt 是一级输入：当前 model turn 立即 abort；in-flight tool call 区分可 abort（read）与必须等结果或标 unknown（write）；中断后的 state 必须落在合法 checkpoint 上，可续跑。
- **Partial result 可信标注**：token stream 尚未过 validate/policy/grader，UI 必须标 provisional；工具副作用只在 confirm 后展示为事实，不能让用户把中途文本当最终承诺。
- **续传**：刷新页面 = 用 run_id + last event id 重放历史 events 再订阅增量，而不是重新起一个 run。

细节见 [03_gaps/streaming.md](03_gaps/streaming.md)。

> 高分句：streaming 是 UX 合同，不只是传输优化——event id、可中断、可续传、provisional 标注都是 API 承诺。

</details>

## 六、可靠性追问答题模板 ⭐⭐

六个高频追问，模板在折叠里，逐条能 30 秒答完。

<details><summary>"工具 timeout 怎么办？"</summary>

先区分 read/write。read 可 bounded retry；write 若有 operation key，先查状态再同 key retry；若 provider 无幂等或查询接口，标记 unknown 并人工 reconcile。所有 attempt 进入 audit。

</details>

<details><summary>"如何恢复？"</summary>

从 durable RunState + events 找最后一个 committed transition；检查 lease/attempt/fencing token；对 pending effect 查询外部 status；重建最小 context；继续下一合法 transition。不能直接重复最后一次 model/tool call。

</details>

<details><summary>"模型无限循环怎么办？"</summary>

max steps/wall time/tokens/cost/tool counts；检测重复 call signature 和无进展；budget 临界时要求 summary/partial artifact；最终返回明确 incomplete，而不是伪装成功。

</details>

<details><summary>"并行 tool call 呢？"</summary>

只有无依赖、只读、parallel-safe 才并行；有界 fan-out；结果按 call ID 对齐，不依赖完成顺序；全局 deadline/cost；一个失败按任务语义决定收集全部或取消其余。

</details>

<details><summary>"memory 被污染？"</summary>

写入需 source、confidence、scope、policy；candidate 与 committed 分层；冲突不静默覆盖；用户/权威 source 可 supersede；所有派生 retrieval 可按 provenance 撤销；加入 false-memory eval。

</details>

<details><summary>"多 agent 结果冲突？"</summary>

保留两个 claim 与 source，不立刻平均；verifier 检查 source independence、freshness、authority；能确定则按规则裁决，不能则把 disagreement 和缺少证据呈现给用户。

</details>

## 七、Evals 答题八步 ⭐⭐

1. 定义 production task distribution 和风险 slice。
2. 固定 environment，保证能 reset/replay。
3. 写 deterministic outcome/policy graders。
4. 模糊质量才用 rubric judge，并用人工 gold 校准。
5. 多次 trial，报告 pass、consistency、cost、latency、policy。
6. 看 trace 做 failure taxonomy，不只看 aggregate。
7. held-out 与训练/调 prompt 数据隔离。
8. shadow/canary/rollback；线上失败变成新 regression task。

> 高分句：先问 eval 是否预测 production，而不是先优化 leaderboard。

## 八、AI-assisted coding 现场脚本 ⭐⭐⭐

### 开场

> 我先确认允许的 AI、联网、题面粘贴和已有代码范围。接着我会只读探索，给出小计划，再让 AI 处理窄任务；每个建议我都会用代码和测试验证。

### 给 AI 的第一条任务

不要说"修这个 repo"。说：

> 只读探索，不修改文件。找出请求入口、核心数据流、测试命令与与本需求相关的现有约定。每个结论引用文件和 symbol；列未知项。

### 第二条任务

> 基于验收 A/B/C，提出最小修改计划。不要实现。说明每步修改面、验证命令和最高风险假设。

### 实现时

一次只下一个窄任务；AI 产出后你检查：需求覆盖、边界、错误、并发、security、tests、diff scope。

### 最后 4 分钟

> 完成了 X/Y；证据是 tests A/B 和 demo C。选择方案 P 是为了……。没有做 Z，因为……。生产前还需要 load test、migration canary 和 metric M。

## 九、常见低分表现 ⭐

- 一上来画模型和向量存储，却没定义用户目标或完成条件。
- 把 authentication、retry、termination 都写进 prompt。
- 所有资料永久写 memory，无 scope/provenance/delete。
- 多 agent 只说"多个 specialist"，没有任务 ownership 和 merge。
- 声称 exactly-once，却没有外部 idempotency/status API。
- 只用另一个模型打分，没有环境 outcome 或人工校准。
- 只展示 happy path，不讨论 timeout、partial success、取消和攻击。
- AI coding 时接受大 diff，不读测试，不解释为何正确。

## 十、结束检查单 ⭐⭐⭐

- [ ] 用户、SLO、风险、自主性明确。
- [ ] API、状态、合法迁移明确。
- [ ] 模型决策与 deterministic control 分开。
- [ ] tool schema、permission、timeout、retry、idempotency 明确。
- [ ] context/memory 有选择、scope、provenance、删除。
- [ ] long horizon 有 checkpoint、lease、cancel、recovery。
- [ ] 多 agent 有独立 task/artifact/verifier 和 baseline。
- [ ] eval 同时看 outcome、policy、cost、latency、consistency。
- [ ] prompt injection、secret、tenant、安全审批覆盖。
- [ ] shadow/canary/rollback 和 observability 覆盖。
- [ ] token/cost 预算与 caching 策略（前缀稳定、分级路由）。
- [ ] 用户中断/续传语义（event id、abort、provisional 标注）。
