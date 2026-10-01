# 分布式水平扩展（单机 harness → 集群）

⏱ 骨架 7 min ｜ 含深潜与资料 45 min ｜ 面试前只看 ⭐⭐⭐ 部分

## 30 秒版本（3 句话）

1. 单机 SQLite harness 走向分布式只需外部化三样东西：task queue（typed queue 解耦提交与执行）、event log（Postgres 单表 → 分区 → Kafka）、调度（按 run_id 分片的 orchestrator）——每一步由明确的瓶颈指标触发，不提前做。
2. 分布式后唯一必须守住的不变量：任意时刻每个 run 只有一个 writer（lease + fencing token）；重试、replay、shard rebalance 的正确性全是这条不变量的推论。
3. Agent loop 天然 long-running 且非确定（LLM 输出），Temporal 式 durable execution 不能照搬——LLM/tool 调用必须作为 activity 持久化结果、replay 时跳过，workflow 本体保持 deterministic；面试里讲清这层映射是 senior 信号。

## 核心概念 ⭐⭐⭐

| 概念 | 要点 | 面试一句话 |
|---|---|---|
| Typed task queue | SQLite 表轮询 → Redis Stream / SQS / Postgres `FOR UPDATE SKIP LOCKED`；消息只带 run_id + step 指针，payload 留在 DB；按 task 类型分 queue，独立扩缩容与限流 | 「queue 传指针不传状态，source of truth 永远在 DB」 |
| Worker lease / fencing | lease 到期即失去写权，单调递增 fencing token 拒绝僵尸 worker 的迟到写入——细节见 [state & memory](../01_core/02_state_and_memory.md)，此处不重复 | 「lease 管活性，fencing 管安全性」 |
| Orchestrator 分片 | 按 run_id 一致性哈希，同一 run 的全部事件路由到同一 shard → shard 内单线程串行处理，免分布式锁；shard 挂/rebalance 时从 event log replay 重建内存态 | 「分片买到的是 per-run 串行化，不只是容量」 |
| Event log 外部化 | Postgres append-only 单表（`(run_id, seq)` 唯一索引做写幂等）→ 按租户/时间分区 → 写 QPS 或 fan-out consumer 数撑不住再上 Kafka（run_id 做 partition key 保 per-run 有序） | 「别一步跳 Kafka，单表分区能扛到超乎想象的量级」 |
| Durable execution | workflow code 严格 deterministic（同输入产生同 command 序列），crash 后 replay Event History 恢复；activity 至少执行一次 → 副作用必须幂等 | 「非确定性全部隔离进 activity，这是 replay 成立的前提」 |
| 两阶段放置 🤖 | reserve（DB 占位）→ node agent ack → commit；agent 静默靠 lease 超时回收 reservation；再配 reconciliation loop 对账 desired vs actual | 「placement 是跨 scheduler/DB/agent 的分布式提交，不是一次 RPC」 |
| 全局 budget / 热点租户 | token/cost 本地累加 + 异步聚合到中心，接受有界软超支；硬 cap 才走中心化 rate limiter；热点租户独立 queue/shard，隔离 noisy neighbor 保其他人 p99 | 「精确扣减和热路径低延迟不可兼得，选有界超支」 |

**Temporal 一段话**（[docs](https://docs.temporal.io/workflow-execution)）：每步执行持久化为 Event History，worker crash 后在新 worker 上 replay——已完成的 activity 直接返回存储结果不重跑，所以 LLM 调用、tool 执行、时间、随机数一切非确定性都必须包进 activity；agent 场景两个额外约束：history 有上限（约 50K events），long-horizon run 要 continue-as-new 截断；模型/prompt 升级会破坏 replay 兼容，需 versioning API 或按 run 固定版本。自建时你在复刻的就是这套 event sourcing + replay，只是把「determinism 约束」换成「显式状态机 + event log」。

## 面试常问 3 题 ⭐⭐⭐

### Q1：设计 Sora 视频生成后端（unreliable GPU 上的 durable job orchestration）

真题锚点：OpenAI 1p3a 高频（[原题与完整题解](../../online_resource/1p3a-openai.md)，约 L3508）；考点明确写在题干里：durable job orchestration、capacity-aware scheduling、preemptible compute 上的故障恢复。

<details><summary>参考打法</summary>

- 开场定性：这不是视频题，是「每 worker 同时只跑一个 job + GPU 随时被 preempt」的调度题。建模上 job/attempt 分离——`GenerationJob 1:N JobAttempt`，job 是逻辑意图，attempt 是一次物理执行，每个 attempt 带自己的 fencing_token 和 lease。
- 数字先行：20 jobs/s × 180s 生成时长 = 3,600 并发 running → ~4,000 worker（10% buffer）；heartbeat 360/s、progress 720/s——主动说出「control plane 不是瓶颈，GPU 容量、冷启动和 preemption 损失才是」。
- Worker 走 pull 模型：register → lease 一个 job → heartbeat 续 lease → 定期 checkpoint 上传（bound 损失 < 30s GPU 时间）→ complete/fail；所有回写带 fencing_token，stale worker 一律拒。
- 恢复路径一句话：lease 过期 → attempt 标 lost → job 回 queue → 新 attempt 从 latest checkpoint 续跑；失败要分类 retryable（preemption/网络）vs non-retryable（bad input），后者直接 fail 不空转。
- 容量不足时诚实：暴露 ETA + admission control，不假装容量无限；priority tier 决定排队顺序和被 preempt 顺序；checkpoint 存储量可能超过成品，讲 TTL/只保最近几个。

</details>

> 高分句：「我把 job 和 attempt 分开建模——job 是逻辑意图，attempt 是物理执行——preemption 恢复就退化成『开一个新 attempt 从 checkpoint 续跑』这一句话。」

### Q2：你的单机 agent harness 怎么扩到 10K 并发 run？

<details><summary>参考打法</summary>

- 讲演进不讲终态，每步报出触发指标：单机 SQLite（几百并发内别动它）→ 状态外部化到 Postgres、worker 无状态化（加机器=加容量）→ typed task queue 解耦提交与执行（提交峰值 > 执行吞吐时）→ orchestrator 按 run_id 一致性哈希分片（单调度进程 CPU/内存到顶时）。
- 第一刀永远切在 state：worker 无状态 + 状态全在 DB 之后，扩容变成纯容量问题，其余步骤才有意义。
- 分片讲收益而不只是机制：同 run 事件同 shard → shard 内单线程串行，免掉所有 per-run 分布式锁；被问「shard 挂了怎么办」答 event log replay 重建内存态 + 一致性哈希最小化迁移面。
- Event log 同样渐进：单表 append-only（幂等靠 `(run_id, seq)` 唯一约束）→ 分区 → Kafka；上 Kafka 的信号是多下游 fan-out（eval、billing、analytics 各自独立消费），不是单纯写量。
- 收尾点题：全程唯一不变量是 per-run single writer（lease + fencing），组件都可替换，不变量不可妥协。

</details>

> 高分句：「扩展路径上每一步我都能说出触发它的瓶颈指标——没有指标驱动的分布式是简历驱动的分布式。」

### Q3：设计共享 GPU 集群的调度平台（placement 的分布式提交）

真题锚点：hack2hire 题库（OpenAI 频率 10/10、Databricks 6、Anthropic 3，[题目与推断解法 🤖](../../online_resource/question-bank/anthropic.md)）；题干自带陷阱：node 可在「决定放置」和「job 启动」之间失联。

<details><summary>参考打法（🤖 题解为推断，非官方答案）</summary>

- 先点破核心难点：每次 placement 是跨 scheduler、DB、node agent 三方的分布式提交，任何一方可在中途挂 → 两阶段放置：DB reserve 占位（容量预扣）→ node agent ack 接单 → commit；agent 静默用 lease 超时回收 reservation，杜绝容量泄漏。
- 必配 reconciliation loop（K8s controller 式）：desired vs actual 持续对账兜底——比「把每条失败路径都处理对」更可靠，这句是 senior 信号。
- 调度策略分层给：priority queue + preemption policy 打底；fairness 用 per-team quota / DRF；追问再上 gang scheduling（分布式训练全有或全无）和 bin-packing 碎片化。
- 主动迁移到 agent 场景：LLM API quota 就是同构资源——中心 budget 表先 reserve token 预算再执行 run，超时未 commit 自动释放；这一步把题拉回你的主场。
- Budget 全局视图：热路径本地累加、异步聚合，接受有界软超支；硬 cap 才同步走中心 limiter；热点租户（一个租户打满全池）独立 queue + 独立 worker pool 配额隔离。

</details>

> 高分句：「所有资源放置本质是 reserve-ack-commit 两阶段协议加一个 reconciliation loop——前者保证正确性，后者兜住所有你没想到的失败路径。」

## 常见坑 ⭐⭐

- [ ] 开场直接上 Kafka/K8s/微服务——说不出每步演进的触发指标，senior 面大忌
- [ ] 把完整 run state 塞进 queue 消息——queue 是投递机制不是 source of truth，at-least-once 重投即状态错乱
- [ ] 讲 replay 不讲 determinism 约束——LLM 调用不包 activity/不存结果，replay 直接产生分叉执行
- [ ] 分片只讲 hash 不讲 rebalance——答不出「从 event log 重建 shard 内存态」等于没做过
- [ ] 全局 budget 每个 token 同步扣中心 DB——热路径上造全局锁；正解是本地累加异步聚合 + 有界超支

## 现有系统怎么做

| 系统/方法 | 核心机制一句话 | 适用场景 | 链接 |
|---|---|---|---|
| Temporal | history shard 持有 per-workflow 状态机、matching 托管 task queue，event sourcing + replay 实现 durable execution | 要「代码即工作流」级持久性，能接受 determinism 约束 | [architecture](https://github.com/temporalio/temporal/blob/main/docs/architecture/README.md) |
| Postgres `SKIP LOCKED` 队列 | 一条 `FOR UPDATE SKIP LOCKED` SQL 实现无争抢 claim，队列与业务状态同库同事务 | < 几千 jobs/s、想少一个组件、需要事务性入队 | [Neon guide](https://neon.com/guides/queue-system) |
| Redis Streams consumer group | PEL 追踪未 ack 消息 + `XAUTOCLAIM` 收养孤儿，at-least-once | 低延迟 dispatch，可接受 Redis 持久性弱一档 | [docs](https://redis.io/docs/latest/develop/data-types/streams/) |
| Kafka 分区 | partition = 有序单元 + 并行单元，run_id 做 key 保 per-run 有序，consumer group 各自独立 fan-out | event log 多下游消费；不适合长任务 dispatch | [semantics](https://docs.confluent.io/kafka/design/delivery-semantics.html) |
| Lease + fencing token | epoch 单调递增，续约与提交全部条件校验，僵尸 writer 的写在存储层被拒 | 一切「per-run single writer」场景的地基 | [Kleppmann](https://martin.kleppmann.com/2016/02/08/how-to-do-distributed-locking.html) |
| run_id 分片 orchestrator | 固定虚拟 shard + 可移动 ownership，shard 内单线程 = per-run 全序免锁 | 自建调度面；与 Temporal history service 同构 | [history-service](https://github.com/temporalio/temporal/blob/main/docs/architecture/history-service.md) |
| LLM 网关（LiteLLM / 自建） | 逻辑模型名 → 多 deployment，rpm/tpm 感知路由 + cooldown + fallback，Redis 共享跨实例计数 | 多 provider failover、按租户限流、interactive/batch 分池 | [routing](https://docs.litellm.ai/docs/routing) |

<details><summary><b>Temporal：durable execution 的工业实现</b></summary>

【技术机制】

- 组件拆分：**frontend** 无状态网关（鉴权/限流/路由）；**history service** 是唯一有状态组件，按 shard 管 per-workflow 的 mutable state + event history；**matching service** 托管 task queue，worker 长轮询取任务；worker 全在用户侧、无状态可随意扩缩。
- 数据结构：每个 workflow execution = 一条 mutable state 记录 + append-only event history。history service 启动时把固定数量 shard（数千个）经 membership ring 分给实例；实例获得 shard 时 `rangeID++`，之后该 shard 的所有持久化写都带 rangeID 条件校验——fencing token 的工业实现，shard 迁移后旧 owner 的写直接被存储层拒绝。
- 一次 step 的完整流程：client → frontend → run 所在 shard 的 history 实例 → 追加 event + 写 transfer task → matching 入队 WorkflowTask → worker poll 到、replay/推进 workflow 代码 → 返回 commands（`ScheduleActivityTask` 等）→ history 校验后追加新 events，循环。
- replay：worker 崩溃后任意新 worker 拉 event history 重放 workflow 函数，已完成 activity 的结果直接从 history 返回、不重跑 → workflow 代码必须 deterministic，一切非确定性（LLM 调用、tool 执行、时间、随机数）包进 activity。
- agent loop 映射骨架：

```python
@workflow.defn
class AgentRun:
    @workflow.run
    async def run(self, state: RunState):
        while not state.done:
            # LLM/tool = activity：结果持久化进 history，replay 时直接返回不重跑
            decision = await workflow.execute_activity(
                call_llm, state.context,
                start_to_close_timeout=120s, retry_policy=...)
            if decision.tool_call:
                result = await workflow.execute_activity(
                    exec_tool, decision.tool_call)   # 副作用必须幂等（at-least-once）
                state.append(result)
            # history 上限 ~50K events / 50MB，long-horizon run 必须截断
            if workflow.info().is_continue_as_new_suggested():
                workflow.continue_as_new(state.compact())  # 压缩后带入下一代
```

- 关键参数/约束：history 超限（~50K events / 50MB）会被 server 直接 terminate → 官方建议轮询 `GetContinueAsNewSuggested()`；activity 是 at-least-once → 幂等；大 payload（agent 的长 context）不进 history，放 blob store 传引用。
- 失败模式：① 改代码/换 prompt/model 版本破坏 replay 兼容 → `NonDeterministicError`，需 patching/versioning API 或按 run 固定版本；② 把 LLM 调用直接写进 workflow 本体 → replay 时分叉执行；③ event 粒度太细（每个 token 一个 event）迅速打爆 history 上限。
- 面试映射：自建 = 「显式状态机 + event log」替代「隐式 replay + determinism 约束」，两者是同一 event sourcing 的两种编程模型；自建换来对 LLM 非确定性的宽容，代价是状态机得自己写对。

</details>

<details><summary><b>Postgres SKIP LOCKED 队列：claim SQL 与 lease 式租约</b></summary>

【技术机制】

- 表结构：`tasks(id, run_id, type, priority, run_at, status, attempt, locked_by, lease_expires_at)`，partial index `ON (type, priority, run_at) WHERE status = 'pending'`——index 只覆盖待领取行，扫描量与积压量成正比而不是与历史总量成正比。
- claim SQL（原子领取一批，无锁等待、无争抢）：

```sql
WITH next AS (
  SELECT id FROM tasks
  WHERE status = 'pending' AND run_at <= now() AND type = $1
  ORDER BY priority, run_at
  LIMIT $2
  FOR UPDATE SKIP LOCKED          -- 已被其他 worker 锁住的行直接跳过
)
UPDATE tasks t
SET status = 'running', locked_by = $worker,
    attempt = attempt + 1,        -- attempt 递增，回写时可当 fencing token 用
    lease_expires_at = now() + interval '60 seconds'
FROM next WHERE t.id = next.id
RETURNING t.id, t.run_id, t.attempt;
```

- 两种持锁风格：① 事务持锁——整个处理期间不 commit，行锁即所有权，崩溃自动释放；但 agent task 一步几分钟（LLM 调用），长事务占连接、阻塞 vacuum，**不可用**。② lease 式（上面这条 SQL）——短事务 claim 后立即 commit，heartbeat 定期续 `lease_expires_at`，reaper 定期把 `status='running' AND lease_expires_at < now()` 的行改回 `pending`。agent 场景只能选 ②。
- 回写校验：complete/fail 时 `UPDATE tasks SET status='done' WHERE id=$id AND locked_by=$worker AND attempt=$my_attempt`——0 行说明任务已被 reaper 回收并被别人重领，本次结果作废（attempt 就是本地 fencing token）。
- 关键参数：batch size（吞吐 vs 单 worker 积压）；lease TTL ≥ 3× heartbeat 间隔；轮询间隔可用 `LISTEN/NOTIFY` 压到近零延迟（NOTIFY 只当唤醒信号，claim 仍走 SQL，丢通知无所谓）。
- 失败模式：① status 频繁翻转产生大量 dead tuples → autovacuum 跟不上、partial index 膨胀，需激进 autovacuum 或定期把 done 行搬走；② `ORDER BY priority` + SKIP LOCKED 的优先级是近似的（高优行被锁住时会先发低优）；③ 每 worker 一连接，几百 worker 就得上 pgbouncer。量级参考：单表撑到每秒几千 jobs 没问题，瓶颈先出现在 vacuum 而不是锁。

</details>

<details><summary><b>Redis Streams consumer group：PEL + XAUTOCLAIM</b></summary>

【技术机制】

- 数据结构：stream 本体是 radix tree + listpack 的 append-only log；每个 consumer group 维护一个游标 `last_delivered_id` 和一张 **PEL（Pending Entries List）**——已投递未 `XACK` 的消息，记录 owner、投递次数、最后投递时间。
- 消费循环骨架：

```python
while True:
    # 1) 先收养孤儿：偷走 idle 超过阈值的 pending 消息（原 owner 视为已死）
    claimed = XAUTOCLAIM(stream, group, me, min_idle_time=300_000, start='0-0')
    # 2) 再拿新消息：'>' = 还没投递给本 group 任何 consumer 的消息
    fresh = XREADGROUP(group, me, {stream: '>'}, count=16, block=2000)
    for msg_id, task_ref in claimed + fresh:
        if delivery_count(msg_id) > 5:          # XPENDING 里带的投递次数
            XADD(dead_letter, task_ref)          # poison pill 进 DLQ
            XACK(stream, group, msg_id); continue
        process(task_ref)                        # 消息只带 run_id + step 指针
        XACK(stream, group, msg_id)              # ack 后才从 PEL 移除
```

- 关键参数：`min_idle_time` 必须 > 最大正常处理时长，否则活着的慢 consumer 会被误判偷单；`COUNT` 控制预取；`XADD ... MAXLEN ~ N` 给 stream 封顶防内存爆；delivery_count 阈值决定 DLQ 时机。
- 失败模式：① **没有 fencing**——`XAUTOCLAIM` 偷单时原 consumer 可能只是慢不是死，两边并发处理同一消息，所以下游必须自带幂等/fencing（这正是「queue 只传指针、状态回 DB 校验」的理由）；② Redis 持久化默认 AOF everysec，宕机可丢最近 1s 的 ack/消息——把它当 dispatch 层而非 source of truth；③ 全量数据在内存，积压深度受内存上限约束。

</details>

<details><summary><b>Kafka 分区语义：per-run 有序与 zombie fencing</b></summary>

【技术机制】

- 分区即契约：partition 是**有序单元**（分区内 offset 全序）也是**并行单元**（一个分区同一时刻只被 group 内一个 consumer 消费）。`key = run_id` → 同 run 事件同分区 → per-run 有序天然成立，跨 run 无序、也不需要。
- 投递语义：默认 at-least-once（处理完再 commit offset；先 commit 后处理则退化为 at-most-once）。exactly-once 依赖两件事：idempotent producer（PID + 序列号在 broker 端去重）+ 事务（`transactional.id` 绑定 **producer epoch**，旧 epoch 的 producer 写被 broker 拒绝——又是 fencing token，与 lease/fencing 同构）。
- 关键配置骨架：

```properties
partitions=128                      # 上限并行度，只能加不能减；改分区数会改 key→partition 映射，破坏历史有序
enable.auto.commit=false            # 处理完 commitSync → at-least-once
partition.assignment.strategy=CooperativeStickyAssignor  # 增量 rebalance，不 stop-the-world
group.instance.id=worker-7          # static membership：滚动重启不触发 rebalance
transactional.id=orch-shard-7       # EOS 场景：producer epoch 做 zombie fencing
```

- 失败模式：① **分区内 head-of-line blocking**——一个慢 run（长 LLM 调用）卡住同分区所有其他 run，这是「Kafka 适合 event log fan-out、不适合长任务 dispatch」的根本原因（任务分发交给 SKIP LOCKED/Streams，Kafka 只做事件广播）；② rebalance 风暴：consumer 处理超过 `max.poll.interval.ms` 被踢出 group 引发连锁 rebalance；③ 消费失败没有原生 per-message retry/DLQ，得自建 retry topic。
- 面试一句话：「上 Kafka 的信号是多下游独立 fan-out（eval/billing/analytics 各带各的 offset），不是写吞吐。」

</details>

<details><summary><b>Lease + fencing：多 worker 下的完整实现（含 commit 校验伪码）</b></summary>

【技术机制】

- 数据结构：`runs(run_id, owner, epoch bigint, lease_expires_at)`；epoch 是全局单调递增的 fencing token，每次所有权变更 +1；worker 拿到 lease 后，**所有**对该 run 的写都携带自己的 epoch。
- 三段伪码（acquire / renew / guarded write）：

```sql
-- 1) acquire：抢占空缺或过期的 lease，epoch++ 即换代
UPDATE runs SET owner = $worker, epoch = epoch + 1,
       lease_expires_at = now() + interval '30 seconds'
WHERE run_id = $run
  AND (owner IS NULL OR lease_expires_at < now())
RETURNING epoch;                    -- 0 行 = 别人持有，走开

-- 2) renew（heartbeat，间隔 ≤ TTL/3）：只能续自己这一代
UPDATE runs SET lease_expires_at = now() + interval '30 seconds'
WHERE run_id = $run AND owner = $worker AND epoch = $my_epoch;
-- 0 行 = 已失位（被抢/epoch 已翻代）→ 立即停止工作，不做任何收尾写

-- 3) guarded write（commit 校验）：校验与写必须在同一原子操作里
INSERT INTO events (run_id, seq, epoch, payload)
SELECT $run, $seq, $my_epoch, $payload
WHERE EXISTS (SELECT 1 FROM runs
              WHERE run_id = $run AND owner = $worker AND epoch = $my_epoch);
-- 0 行 = 僵尸写被拒；配合 (run_id, seq) 唯一约束同时挡重复写
```

- 为什么必须 epoch 而不只是 lease：GC pause / 网络分区期间 worker 不知道自己已失位，pause 结束后带着旧内存态继续写——lease 只保证「大概率单 writer」（活性），epoch 条件校验保证「写入层面绝对单 writer」（安全性）。Kleppmann 对 Redlock 的核心批评就是它发不出 fencing token。
- 关键参数：TTL 与时钟漂移——`lease_expires_at < now()` 依赖 DB 单一时钟就没有多机时钟问题（所有比较都在 DB 侧做）；renewal 失败要重试 2 次再自杀，避免网络抖动误杀。
- 失败模式与边界：① 先 `SELECT` 校验再单独 `UPDATE` 写 = check-then-act 竞态，两步之间可能翻代——必须像上面一样一条语句原子完成；② fencing 只保护「会校验 token 的存储」，打到第三方 API 的 tool 副作用挡不住 → 只能靠幂等键（`run_id:seq:epoch`）+ 结果提交时再过一次 guarded write；③ attempt 递增（Q1 的 JobAttempt）就是 per-job 粒度的 epoch，同一套机制。

</details>

<details><summary><b>Orchestrator 分片：路由、单线程全序、rebalance 正确性论证</b></summary>

【技术机制】

- 数据结构：固定 N 个虚拟 shard（如 4096，远大于机器数）；`shard_id = hash(run_id) % N`；shard → owner 映射存 coordination store（etcd / DB 一张表），每个 shard 带自己的 `shard_epoch`。「固定虚拟 shard + 可移动 ownership」优于裸一致性哈希：key→shard 映射永不变，迁移单位是整个 shard，Temporal history service 就是这个设计。
- 事件路由：producer 本地算 `shard_id`，投到 per-shard inbox（Kafka 一 shard 一 partition，或 DB 队列按 shard_id 过滤）；shard owner **单线程**消费自己的 inbox → shard 内全序 ⊇ per-run 全序，per-run 的所有锁、乐观并发控制全部消失；跨 run 无序无所谓——run 之间本就无因果关系。
- owner 主循环骨架：

```python
def owner_loop(shard_id):
    epoch = cas_acquire(shard_id)          # coordination store 里 CAS：epoch++
    state = replay(event_log, shard_id)    # 内存态只是 cache，正确性来自 log
    for event in inbox(shard_id):          # 单线程 → shard 内全序
        commands = state.apply(event)      # 纯内存状态机推进
        ok = store.append(shard_id, epoch, commands)  # 条件写：epoch 不匹配即拒
        if not ok:
            return                         # 已被新 owner 接管，安静退出，不收尾
```

- **rebalance 正确性论证（三步，面试可直接背）**：① 所有权转移 = coordination store 里对该 shard `epoch++`（CAS），这是唯一的真相源；② 新 owner 从 event log replay 重建内存态——内存态是纯 cache，丢了不影响正确性，只影响恢复时长；③ 旧 owner 可能还活着还在写（分区/pause），但它的每次持久化写都带旧 epoch、被存储层条件校验拒绝 → **正确性不依赖旧 owner 及时知道自己失位，只依赖存储层的单调 epoch 校验**；最坏情况 = 旧 owner 白干一段、写全部失败，绝不会出现两个 writer 同时写成功。
- 关键参数：虚拟 shard 数（迁移粒度 vs 元数据量）；replay 时长 → 定期 per-shard snapshot/checkpoint，replay 只从 snapshot 之后开始；ownership 判定加 grace period 防 coordination store 抖动引发 flapping。
- 失败模式：① 热 shard——单租户海量 run 哈希进同一 shard，单线程吃满一核 → 租户级二次打散或热点租户独立 shard 段；② snapshot 缺失时 shard 迁移 = 全量 replay，分钟级不可用；③ 忘了给「新 owner 的第一次写」也做条件校验——acquire 和第一次写之间同样可能翻代。

</details>

<details><summary><b>LLM 网关层：并发上限、租户限流、failover、分池 backpressure</b></summary>

【技术机制】

- 核心抽象：逻辑模型名 → deployment 列表（同模型多 region/多 provider）。LiteLLM Router 的策略可全抄：weighted shuffle（按 rpm/tpm 权重）、rate-limit aware v2（过滤掉将超 tpm/rpm 的 deployment）、latency-based、least-busy、cost-based；失败处理三层——retry（指数退避 + jitter）→ cooldown（429 立即冷却该 deployment，默认按 allowed_fails/时间窗）→ fallback（本组耗尽后跨模型组降级）。多实例网关的 rpm/tpm 计数放 Redis 共享，否则每实例各算各的、总量超限。
- 自建骨架（分池 + 租户限流 + failover 一体）：

```python
async def complete(req):
    await tenant_bucket[req.tenant].acquire(req.est_tokens)  # 租户 token bucket，防 noisy neighbor
    pool = interactive_pool if req.interactive else batch_pool  # 分池：池各自有 semaphore
    async with pool.limit(req.model):        # 并发上限 per (pool, provider, model)
        for dep in router.pick(req.model):   # 已过滤 cooldown 中/将超限的 deployment
            try:
                return await dep.call(req, timeout=pool.timeout)
            except (RateLimited, ProviderOverloaded):
                router.cooldown(dep, seconds=60)   # 立即冷却，换下家
        raise AllDeploymentsExhausted        # 上层决定：排队 / 降级模型 / 对提交端 429
```

- 分池与 backpressure：interactive（人在等）与 batch（长任务）**物理分开两组 semaphore**，batch 池上限设为 provider quota 的 ~70%，永远给 interactive 留余量；backpressure 逐级向上传——batch 队列深度超阈值 → 停止 dequeue → task queue 积压 → admission control 对新提交返回 429/排队 ETA。绝不在网关内部无界缓冲。
- 关键参数：per-deployment rpm/tpm（从 provider 控制台抄）、cooldown 时长、client 侧并发 ≤ provider 并发上限（宁可 client 排队也别打出 429）、streaming 场景用 TTFT 当健康信号（比总时延灵敏得多）。
- 失败模式：① retry 风暴——429 后全体立刻重试放大过载，必须 jitter + budget（如每请求最多 2 次 retry）；② failover 到另一 provider 后 prompt/KV cache 全失效，成本和 TTFT 陡增——failover 是救命手段不是负载均衡手段，粘住（sticky）同 deployment 优先；③ 只做全局限流不做租户隔离——一个跑批租户吃光 quota，所有人 p99 爆炸。

</details>

## 自学资料

1. [Temporal 架构文档（temporalio/temporal repo）](https://github.com/temporalio/temporal/blob/main/docs/architecture/README.md) — frontend/history/matching 拆分、shard、event sourcing 的第一手描述，自建 durable execution 前必读的工业参照 · 25 min
2. [How to do distributed locking（Kleppmann）](https://martin.kleppmann.com/2016/02/08/how-to-do-distributed-locking.html) — fencing token 的原始论证 + 为什么 Redlock 不安全；本页所有 lease/fencing 说法的出处 · 15 min
3. [Temporal Workflow Definition（官方 docs）](https://docs.temporal.io/workflow-definition) — determinism 约束的精确表述与 versioning/patching，回答「LLM 调用为什么必须包 activity」的依据 · 15 min
4. [Redis Streams（官方 docs）](https://redis.io/docs/latest/develop/data-types/streams/) — consumer group / PEL / XACK / XAUTOCLAIM 完整语义，读完能手写可靠消费循环 · 20 min
5. [Queue System using SKIP LOCKED（Neon guide）](https://neon.com/guides/queue-system) — 带完整 SQL 的 Postgres 队列实现走查，对照本页 claim SQL 复习 · 10 min
6. [Message Delivery Guarantees for Apache Kafka（Confluent docs）](https://docs.confluent.io/kafka/design/delivery-semantics.html) — at-most/at-least/exactly-once 的准确定义与实现边界，面试说投递语义别口胡 · 10 min
7. [LiteLLM Router 文档](https://docs.litellm.ai/docs/routing) — 6 种路由策略 + cooldown/retry/fallback 全部参数；自建网关也照这份 API 抄作业 · 15 min
8. [ContinueAsNew in Temporal（indeedeng/iwf wiki）](https://github.com/indeedeng/iwf/wiki/ContinueAsNew-in-Temporal-%28or-Cadence%29-workflow) — 为什么 replay 模型必须截断 history、状态怎么安全跨代，long-horizon agent run 直接相关 · 10 min

## 相关

- lease/fencing、event sourcing 细节：[state & memory](../01_core/02_state_and_memory.md)
- Sora 真题全文（数据模型/API/failure 章节都值得背）：[1p3a-openai.md](../../online_resource/1p3a-openai.md)
- GPU Scheduling Platform 原题：[question-bank/anthropic.md](../../online_resource/question-bank/anthropic.md)
- 系统设计答题框架：[SYSTEM_DESIGN_PLAYBOOK](../../agentic/content/SYSTEM_DESIGN_PLAYBOOK.md)
