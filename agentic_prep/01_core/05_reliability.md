# 05 · Reliability 与 Failure Recovery

⏱ 骨架 6 min ｜ 含深潜与资料 40 min ｜ 面试前只看 ⭐⭐⭐ 部分

## 1. 七类 failure taxonomy ⭐⭐⭐

| # | 类别 | 典型失败 |
|---|---|---|
| 1 | Specification | 目标/约束/完成条件缺失或冲突 |
| 2 | Model decision | 选错工具、参数、计划或事实 |
| 3 | Tool/runtime | timeout、429、schema drift、坏结果、partial side effect |
| 4 | Coordination | 重复任务、handoff 丢信息、共享 state 冲突 |
| 5 | Verification | grader 漏洞、模型自评、错误 source、测试不覆盖 |
| 6 | Security/authority | 注入、越权、secret 泄露、confused deputy |
| 7 | Operations | worker crash、stale result、queue backlog、成本爆炸 |

> 高分句：「agent 出错了」不是一个 failure mode——先分类到七类之一，才能谈 detection 和 recovery。

## 2. 每个失败回答四问 ⭐⭐⭐

| 问题 | 要回答什么 |
|---|---|
| Detection | 什么 signal 能发现？ |
| Containment | 如何缩小 blast radius？ |
| Recovery | 如何回到已知状态？ |
| Prevention | 加什么 invariant/eval/tool 改进？ |

<details>
<summary>示例：三类高频失败的四问速答</summary>

| 失败 | Detection | Containment | Recovery | Prevention |
|---|---|---|---|---|
| write 类工具 timeout | executor timeout 信号 | 状态标 `unknown`，暂停同类写 | 按 `operation_key` 查外部 status 再决定重试 | idempotency key + retry matrix（见 [./01_loop_and_tools.md](./01_loop_and_tools.md)） |
| prompt injection | context 中 source/trust level 标记 + adversarial eval | 权限在 executor 层，注入无法提权 | 撤销未审批 proposal，审计 trace | security 控制清单（见 [./06_eval_security.md](./06_eval_security.md)） |
| worker crash | lease 过期 | fencing token 拒绝过期 worker 的迟到写 | 重新 claim，retry 前查 operation status | lease + attempt 机制（见 [./02_state_and_memory.md](./02_state_and_memory.md)） |

</details>

> 高分句：「再问模型一次」不是完整 recovery strategy——四问缺一个，答案就不完整。

## 3. Budget 是可靠性功能 ⭐⭐⭐

- 同时限制：step、wall time、tokens、money、tool calls、并发、某类高成本 action。
- 预算耗尽返回明确状态和已有 artifact；不要静默给一个像完成品的半成品。

> 高分句：budget 不只是成本控制，是 blast radius 控制——它给每类失败一个确定的上界。

## 4. 现有系统怎么做 ⭐⭐⭐

一句话总纲：retry 只有在 write 幂等时才是免费的；幂等不是免费的，总要有人存 key、有人 enforce token。下面 6 个模式从"网络层重试"一路覆盖到"agent loop 特有失败"，折叠块内是实现级细节。

| 方法 / 系统 | 核心机制一句话 | 适用场景 | 链接 |
|---|---|---|---|
| Stripe idempotency key | client 每个操作带唯一 key，server 持久化首次响应，重试同 key 返回同一结果 | 不可靠网络上的 write API；agent 的 write tool | [Stripe blog](https://stripe.com/blog/idempotency) |
| Transactional outbox | 业务状态与"待发事件"写进同一本地事务，relay 异步投递（at-least-once） | 状态变更必须可靠触发后续动作 | [microservices.io](https://microservices.io/patterns/data/transactional-outbox.html) |
| Lease + fencing token | 锁服务发单调递增 token，资源端拒绝旧 token 的迟到写 | worker crash / GC pause 后防 zombie write | [Kleppmann 2016](https://martin.kleppmann.com/2016/02/08/how-to-do-distributed-locking.html) |
| Temporal timeout + retry policy | 4 种 timeout 各检测生命周期的一段 + 声明式指数退避 | durable execution、长任务编排 | [Temporal blog](https://temporal.io/blog/activity-timeouts) |
| Backoff + jitter + circuit breaker | 随机化退避摊平重试洪峰；断路器让持续失败快速失败 | 一切远程调用（LLM API、tool backend） | [AWS Builders' Library](https://aws.amazon.com/builders-library/timeouts-retries-and-backoff-with-jitter/) |
| LLM guardrails 层 | schema 校验 + 自修复、输出截断、循环检测、run 级预算断路 | agent loop 内模型特有的失败 | [MAST (arXiv)](https://arxiv.org/abs/2503.13657) |

<details>
<summary>Stripe idempotency key —【技术机制】</summary>

**数据结构**（server 侧一张表）：

```sql
CREATE TABLE idempotency_keys (
  key            text PRIMARY KEY,     -- client 生成，UUIDv4
  request_hash   text NOT NULL,        -- 参数指纹，防同 key 不同 payload
  locked_at      timestamptz,          -- 正在处理的互斥标记
  response_code  int,                  -- 首次结果（成功或失败都缓存）
  response_body  jsonb,
  recovery_point text NOT NULL DEFAULT 'started',  -- 多阶段操作的断点
  created_at     timestamptz NOT NULL DEFAULT now()
);
```

**处理流程**：

```python
def handle_post(key, request):
    row = upsert_and_lock(key, hash(request))        # 事务内 SELECT ... FOR UPDATE
    if row.request_hash != hash(request):
        return 422                                   # 同 key 不同参数 = client bug，报错
    if row.response_code is not None:
        return row.response_code, row.response_body  # 重放：直接回缓存
    if row.locked_at and not expired(row.locked_at):
        return 409                                   # 并发同 key：让 client 稍后再试
    for phase in phases_from(row.recovery_point):    # 从断点续跑，不是从头
        result = phase.run()                         # 每个 phase 是一个原子步骤
        advance_recovery_point(key, phase.next)      # 与 phase 的 DB 写同一事务
    save_response(key, code, body)
    return code, body
```

**关键参数**：key TTL = 24h（过期后同 key 会被当成新请求——client 的重试窗口必须小于它）；key 用 UUIDv4 级别的熵；只对 POST 生效（GET/DELETE 定义上幂等）。agent 场景推荐 `key = hash(run_id, step_id, tool, canonical_args)`——重试同一步天然同 key，新的一步天然新 key。

**为什么这样设计**：分布式系统里不存在真正的 exactly-once 传输，工程真相是 **at-least-once + server 端按 key 去重 = 表象上的 exactly-once**。缓存"失败响应"同样关键：否则重试可能得到与首次不同的结果，client 永远无法收敛。

**失败模式**：① 只做 key 去重、没做 recovery point——多阶段操作中途 crash 后重试会卡在 409 或从头重做（brandur 那篇专讲这个）；② client 重试跨过了 key TTL → 重复执行；③ 幂等只保到本 server 边界，下游第三方仍可能看到重复。

**对应 v1 lab03**：crash point 正是 `crash_after_external_start`（外部已 start、本地未 commit）——重启后用同一 `operation_key` 先查外部 status 再决定重放，等价于 client 视角的 idempotent retry。

</details>

<details>
<summary>Transactional outbox —【技术机制】</summary>

**要解决的问题**：`UPDATE orders ...` 和 `publish(OrderCreated)` 无法原子——先 commit 后 crash 则消息永远丢；先发消息后事务回滚则发出了假事件。2PC 太重且 broker 多半不支持。

**数据结构**：

```sql
CREATE TABLE outbox (
  id           bigserial PRIMARY KEY,   -- 单调，天然定序 + 可作 message_id
  aggregate_id text NOT NULL,           -- 分区键，保证同实体内有序
  event_type   text NOT NULL,
  payload      jsonb NOT NULL,
  published_at timestamptz              -- NULL = 未投递
);
```

**流程**：

```python
# 写侧：业务写与事件写同一个本地事务 → 原子
with db.transaction():
    db.execute("UPDATE orders SET state='paid' WHERE id=%s", oid)
    db.execute("INSERT INTO outbox(aggregate_id, event_type, payload) VALUES (...)")

# relay 侧（polling publisher 版）
while True:
    rows = db.query("SELECT * FROM outbox WHERE published_at IS NULL "
                    "ORDER BY id LIMIT 100 FOR UPDATE SKIP LOCKED")
    for r in rows:
        broker.publish(r.event_type, r.payload, message_id=r.id)   # 可能重复！
        db.execute("UPDATE outbox SET published_at=now() WHERE id=%s", r.id)
    sleep(poll_interval)    # 100ms–1s
```

**两种 relay**：polling publisher（简单，代价是 DB 轮询压力 + poll_interval 的延迟）；transaction log tailing / CDC（Debezium 读 WAL，低延迟、无额外查询，运维更重）。

**关键性质**：消息**当且仅当**本地事务 commit 才会发出；但 relay 在 publish 之后、标记 published 之前 crash → 重复投递。整条链路是 at-least-once，**consumer 必须按 message_id 去重**——又回到上一个模式。

**agent 对应**：durable agent harness 的 intent journal 就是 outbox——"决定调用 tool X" 作为一条 intent 与 run state 同事务落库，executor 从 journal 拉取执行。lab03 的 start/poll 分离本质相同：intent 先落库、副作用后执行，crash 后能从 journal 恢复"我当时打算做什么"。

**失败模式**：① 某处代码忘了走 outbox 直接 publish（模式靠纪律，易错，可用 lint/封装堵住）；② 跨 aggregate 的全局有序做不到，只能按 aggregate_id 分区有序；③ outbox 表无限膨胀，需要归档 job。

</details>

<details>
<summary>Lease + fencing token —【技术机制】</summary>

**为什么超时锁不够**：client 拿到 lease 后可能 GC pause / 网络分区任意久；lease 过期、锁已易主，老 client 醒来仍以为持锁并继续写。Kleppmann 的核心论点：**锁的正确性不能靠持锁方自觉，必须由资源端 enforce**。Redlock 被判不安全正是因为它没有 fencing token，且依赖"有界延迟、有界暂停、准确时钟"这类同步系统假设——真实系统全都违反。

**机制（两半，缺一不可）**：

```
锁服务侧：每次成功获取锁，返回单调递增 token
          （ZooKeeper zxid / raft term+index / DB 序列，不能用本地时间戳）
资源侧：  记录已见过的最大 token，拒绝更小 token 的写

client A: acquire() -> lease + token=33
client A: [GC pause 45s，lease 过期]
client B: acquire() -> lease + token=34
client B: write(data, token=34)   -> OK，storage 记住 34
client A: write(data, token=33)   -> REJECTED (33 < 34)  ← 挡下 zombie write
```

```sql
-- 资源端的条件写（DB 版）
UPDATE runs SET state = %s, fence = %s
WHERE id = %s AND fence < %s;
-- rowcount == 0 → 你是 zombie：放弃本地结果并自杀重启
```

**参数怎么定**：lease 时长 >> 持锁操作 P99（常见 10–30s）——太短误判频繁、太长 failover 慢；持锁方以 lease/3 周期续约（heartbeat）；token 必须来自锁服务的共识日志序号，本地时钟会回拨。

**失败模式**：① 资源端不支持条件写 → fencing 落不了地，锁退化为 "efficiency lock"（防重复劳动，不保正确性——此时要靠资源自身的幂等）；② 一次持锁写多个资源时，每个资源要各自 check token；③ 把 Redlock 当 correctness lock 用。

**对应 v1 lab03**：worker 带 `attempt` 号写 run state，DB 侧 `WHERE attempt = ?` 条件更新——attempt 就是 fencing token 的极简版；lease 过期触发 re-claim 即 §2 表格里的 worker crash 行。

</details>

<details>
<summary>Temporal timeout + retry policy —【技术机制】</summary>

**模型**：workflow 是 event-sourced 的确定性代码（crash 后 replay history 恢复到崩溃前的位置），一切副作用下放到 activity；server 负责调度 activity、检测超时、执行 retry policy。activity 语义是 **at-least-once**，所以 activity 内部要幂等（模式一）。

**四种 timeout 各检测生命周期的一段**：

| Timeout | 检测什么 | 官方建议 |
|---|---|---|
| Schedule-To-Start | 任务在队列里等太久（worker 容量不足） | 很少需要设，靠 metrics + 扩容 |
| Start-To-Close | 单次尝试卡死 / worker 拿了任务就崩 | **永远要设**，server 靠它触发 retry |
| Heartbeat | 长任务执行中 worker 死掉 | 长 activity 必设，发现故障远快于等满 Start-To-Close |
| Schedule-To-Close | 含所有重试的总时长（用户体验上界） | 用它表达"最多等多久"，比数 max_attempts 直观 |

```python
# Python SDK 骨架
await workflow.execute_activity(
    deploy_step,
    start_to_close_timeout=timedelta(minutes=5),      # 单次尝试上限
    schedule_to_close_timeout=timedelta(minutes=30),  # 含重试总上限
    heartbeat_timeout=timedelta(seconds=30),
    retry_policy=RetryPolicy(
        initial_interval=timedelta(seconds=1),
        backoff_coefficient=2.0,
        maximum_interval=timedelta(minutes=1),  # interval = min(init * coeff^(n-1), max)
        maximum_attempts=0,                     # 0 = 不限次数，由 schedule_to_close 兜底
        non_retryable_error_types=["InvalidArgument"],  # permanent 错误不重试
    ),
)

# activity 内：heartbeat 携带进度，重试时从断点续跑而非从零开始
async def deploy_step(items):
    start = activity.info().heartbeat_details or 0
    for i, item in enumerate(items[start:], start):
        process(item)
        activity.heartbeat(i + 1)
```

**关键设计点**：Start-To-Close 设成"最长合理单次执行时间"而非总预算——设太长的代价是每次故障都要等满它才重试；heartbeat details 是免费的 checkpoint；`non_retryable_error_types` 把 transient（timeout/5xx/429）与 permanent（参数错/权限拒）分开，对应 [./01_loop_and_tools.md](./01_loop_and_tools.md) 的 retry matrix。

**失败模式**：① 只设 Schedule-To-Close 不设 Start-To-Close → 一个 hang 住的 attempt 吃光全部预算才触发重试；② 长任务不 heartbeat → worker 死了要等满 Start-To-Close 才被发现；③ 非幂等 activity + retry → 重复副作用（Temporal 只保 workflow 代码 effectively-once，从不保 activity 只执行一次）。

**agent 对应**：每个 tool call = 一个 activity；LLM 调用（纯读、幂等）可放心 retry；write tool 必须带 operation_key。lab03 的 start/poll/crash-replay 三段路径就是一个手写迷你 Temporal。

</details>

<details>
<summary>Backoff + jitter + circuit breaker —【技术机制】</summary>

**为什么必须 jitter**：后端故障恢复的一瞬间，所有 client 的退避定时器同时到期 → 同步重试洪峰把后端再次打挂（retry storm）。AWS 的模拟结论：**full jitter**（区间内完全随机）在总调用次数和整体完成时间上都优于无 jitter 和 equal jitter。

```python
# full jitter（AWS 推荐形态）
def backoff(attempt, base=0.5, cap=30.0):
    return random.uniform(0, min(cap, base * 2 ** attempt))

# retry 预算：防止重试放大 outage（本地 token bucket）
class RetryBudget:                        # 例：重试流量 ≤ 正常流量的 10%
    def on_request(self): self.tokens = min(self.tokens + 0.1, self.cap)
    def allow_retry(self):
        if self.tokens < 1: return False
        self.tokens -= 1; return True

# circuit breaker 三态机
# CLOSED --10s 窗口失败率>50% 且样本≥10--> OPEN --冷却 30s--> HALF_OPEN
# HALF_OPEN --连续探测成功 k 次--> CLOSED；--探测失败--> OPEN
def call_tool(tool, args):
    if breaker[tool].is_open():
        return ToolError("tool temporarily unavailable, try an alternative")
    try:
        r = invoke(tool, args); breaker[tool].on_success(); return r
    except TransientError:
        breaker[tool].on_failure(); raise
```

**参数怎么定**：base 0.1–1s（≈ 后端恢复时间量级），cap 20–60s，attempts 2–3（更多次数几乎不提高成功率、只放大负载）；**retry 只放在一层**——client、gateway、service 各 retry 3 次会叠乘成 27 次。breaker 冷却 30s 起步，half-open 只放极小流量探测。

**分类先于重试**：429/503/连接超时 → 可重试；400/401/403/422 → 不可重试；**write 超时 → 状态 unknown**，必须先查外部 status 再决定（模式一），盲目重试就是双重扣款。

**agent 场景的 tool 级 breaker**：某 tool 进入 OPEN 后，向模型返回结构化的 "unavailable, try alternative"——让模型改计划，比静默重试烧 token 好，也比直接杀掉整个 run 好。这是把分布式系统的快速失败翻译成模型能理解的信号。

**失败模式**：① 对 permanent 错误重试（纯浪费）；② 多层重试叠乘；③ breaker 粒度太粗——应按 tool × endpoint 分桶，别让一个坏依赖拖垮所有工具；④ 无 jitter 的整点 cron 同样制造洪峰（jitter 适用于一切定时器，不只重试）。

</details>

<details>
<summary>LLM guardrails 层 —【技术机制】</summary>

前五个模式管"分布式系统会坏"；这一层管"模型会自信地做错事"。四道防线全部实现在 harness/executor 层，不在 prompt 层——prompt 是请求，不是 enforcement。

**① Schema 校验 + 自修复 repair loop**：

```python
def parse_tool_args(model_output, schema, max_repair=2):
    for attempt in range(max_repair + 1):
        try:
            args = lenient_json_parse(model_output)   # 先过宽松解析（修引号/尾逗号）
            jsonschema.validate(args, schema)
            return args
        except (ParseError, ValidationError) as e:
            # 把错误作为 tool result 回给模型自修，而不是抛给用户
            model_output = llm(ctx + [tool_error(f"invalid args: {e}; fix and retry")])
    raise HardFail("schema repair exhausted")          # 显式失败，不静默吞
```

constrained decoding / structured outputs 能把解析错误消灭在生成阶段，但 **schema 合法 ≠ 语义正确**（删错文件的 path 也是合法 string），高危参数还要业务级校验：path 白名单、金额上限、目标环境检查。

**② Tool output 大小上限**：`result[:CAP] + "\n[truncated: N of M bytes; use pagination]"`，CAP 常见 10–50KB/call。防单次 tool 结果撑爆 context、挤掉 system prompt——那是失忆和注入放大的温床。截断必须显式标记，否则模型基于残缺数据自信决策。

**③ 循环检测（重复 call signature）**：

```python
sig = hash((tool, canonicalize(args)))   # canonicalize: 排序 key、归一化空白
window.append(sig)                        # 滑动窗口 N = 10–20
if window.count(sig) == 3:                # 软阈值：先提醒
    inject("You repeated this exact call 3 times with the same result. "
           "Change approach or report the blockage.")
elif window.count(sig) >= 5:              # 硬阈值：终止，交回已有 artifact
    terminate(reason="loop detected")
```

先软后硬：多数循环是模型没意识到结果相同，一句提醒就能打破；硬停兜底防烧钱。

**④ Budget 断路（§3 的实现版）**：run 级 counters（tokens / cost / steps / tool_calls / wall_time）每步扣减；高危 action（写库、发邮件、花钱）单独小额度，超出转 human approval。耗尽时返回 `BUDGET_EXHAUSTED` + 已完成 artifact，绝不静默交半成品。

**事故 → 防线映射（Replit 2025-07：agent 在 code freeze 期间删了生产库，还谎称无法 rollback，实际可恢复）**：

| 事故环节 | 缺的防线 |
|---|---|
| "code freeze" 只写在指令里 | authority 在 executor 层 enforce——instruction 不是 enforcement |
| agent 能直连生产库 | dev/prod 凭据隔离，agent 默认只持有 dev 凭据 |
| 删除类命令直接执行 | 破坏性操作走 human approval 通道（④ 的高危额度） |
| 模型声称"无法 rollback" | recovery 依据外部事实（备份系统 status API），永远不信模型自述 |

事发后 Replit 官方补的正是前两条：自动分离 dev/prod 数据库 + planning-only mode（[The Register 报道](https://www.theregister.com/2025/07/21/replit_saastr_vibe_coding_incident/)，[AI Incident Database #1152](https://incidentdatabase.ai/cite/1152/)）。

**失败模式**：① repair loop 无上限 → 模型和 validator 打乒乓烧 token；② 循环检测只看 exact match → 模型每次微调一个无关参数就绕过（canonicalize 要够狠，必要时加语义近似）；③ guardrail 触发后只在 log 里留一行 → 没有回到模型的反馈信号，同类失败反复发生。

</details>

> 高分句：这六个模式其实是一条防线的六段——client 侧 retry（五）打到 server 侧幂等（一），状态变更靠 outbox 原子化（二），并发写靠 fencing 排他（三），全生命周期靠 timeout 分段检测（四），模型特有失败靠 guardrails 兜底（六）。面试时能把任意一个失败沿这条链走一遍，就赢了。

## 5. 自学资料

按优先级排序；前 4 条覆盖面试 80% 的追问。

1. [How to do distributed locking — Martin Kleppmann](https://martin.kleppmann.com/2016/02/08/how-to-do-distributed-locking.html) — fencing token 的正典出处；看懂"为什么 Redlock 不安全"就看懂了分布式锁的全部争论 · 预计 20 min
2. [Designing robust and predictable APIs with idempotency — Stripe](https://stripe.com/blog/idempotency) — idempotency key 的设计动机与 client 重试规范；配合 [API 参考页](https://docs.stripe.com/api/idempotent_requests)（24h TTL、只对 POST、失败响应也缓存）· 预计 15 min
3. [The four types of Activity timeouts — Temporal](https://temporal.io/blog/activity-timeouts) — 四种 timeout 各检测什么、怎么配，durable execution 面试的标准答案来源 · 预计 15 min
4. [Timeouts, retries, and backoff with jitter — AWS Builders' Library](https://aws.amazon.com/builders-library/timeouts-retries-and-backoff-with-jitter/) — retry storm、单层重试、"幂等才可重试"的第一手工程经验 · 预计 20 min
5. [Transactional outbox — microservices.io](https://microservices.io/patterns/data/transactional-outbox.html) — 状态与事件原子化的标准模式页，短小，直接对应 agent 的 intent journal · 预计 10 min
6. [Implementing Stripe-like Idempotency Keys in Postgres — brandur.org](https://brandur.org/idempotency-keys) — 前 Stripe 工程师的完整实现：recovery point、原子 phase、并发锁竞争，比官方 blog 深一层 · 预计 25 min
7. [Why Do Multi-Agent LLM Systems Fail? (MAST) — arXiv](https://arxiv.org/abs/2503.13657) — 3 大类 14 种 failure mode 的实证 taxonomy（150 条 trace 人工标注，κ=0.88），与本文件七类互补 · 预计 30 min（只看 taxonomy 图表 10 min）
8. [Exponential Backoff And Jitter — AWS Architecture Blog](https://aws.amazon.com/blogs/architecture/exponential-backoff-and-jitter/) — full / equal / decorrelated jitter 的模拟对比，backoff 公式选型的依据 · 预计 15 min
9. [Detecting Activity failures — Temporal docs](https://docs.temporal.io/encyclopedia/detecting-activity-failures) — timeout + retry policy 的权威语义定义，写 config 时的查阅页 · 预计 15 min
