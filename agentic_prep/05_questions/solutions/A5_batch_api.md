# [A5] LLM Inference Batch API（Anthropic 最高频 SD）· 完整解答

⏱ 读完 15 min ｜ 建议先自己限时 50min 答一遍再看（盲看解答记不住）。题面原文见 [../A_scenario_design.md](../A_scenario_design.md#a5)，原始题解见 [../../../online_resource/1p3a-anthropic.md](../../../online_resource/1p3a-anthropic.md)（LLM Request Batching API 一节）。

## 题目还原

**Exponent 版原文**："You have a single GPU that can process up to 100 inputs per batch. Users submit requests synchronously and wait for results. Design the system that receives inputs, batches them, processes them on the GPU, and returns responses to the correct users."**batchstring 变体**给定固定后端 `batchstring(inputs: list[str]) -> list[str]`：每批 1–100 条、固定 ~100ms 延迟（与批大小无关）、每 GPU 一次只跑一批；要求 1000+ RPS、P95<500ms、GPU 利用率 70–80%。**真正在考**：同步 HTTP 外壳 + 异步内部 batching 的桥接——这是一道 correlation（结果路由回正确用户）+ 排队论（双触发凑批、背压、容量数学）的分布式系统题，AI 只是皮。评分标准（面经原话）：剥掉 AI 皮找核心 infra 问题 + 主动做 failure-mode 分析。

## 开场澄清（6 问 + 为什么问）

1. **"Batch API" 指哪种形态？**在线动态 batching（用户同步等、P95<500ms），还是 Anthropic Message Batches 那类异步产品（提交后 poll、-50% 定价、24h SLA）？——两者架构完全不同。已报告题面是前者，我以前者为主线，末尾给异步形态。
2. **后端合同确认**：100ms 真的与批大小无关？每 GPU 严格串行一批？——固定延迟意味着凑大批几乎免费，batching 收益极大；真 LLM 的 decode 随输出 token 增长，那要谈 continuous batching（深挖 3）。
3. **规模与增长**：当前 RPS、峰值倍数（按 3× 设防）、增长目标（1K→10K→100K）？真 LLM 要追问 input/output token 分布——**容量按 tokens/sec 定，不按 RPS**。
4. **租户与优先级**：free/paid/enterprise 要区别对待吗？过载时允许丢谁？——决定队列结构与 load shedding 策略。
5. **失败与重试语义**：纯推理无副作用，重试安全；但计费怎么算？客户端重试要不要服务端幂等去重？
6. **GPU 池归我管吗**：数量固定还是可 autoscale？——"新 GPU 启动 5 分钟"的追问在等着，先把 warm pool 铺垫出来。

## 答案主线（按 [../../02_playbook.md](../../02_playbook.md) 时间盒）

**开场 90 秒（背下来）**："这题核心是用异步内部 batching 撑起同步外部 API。我先做容量数学定 GPU 数，再给 API 与请求信封，然后画『handler 持连接 + 有界优先级队列 + 双触发 batcher + GPU worker pool + 结果按 correlation ID 路由回去』的主线，深挖凑批参数、多节点结果路由和真 LLM 化，最后过失败清单：worker 崩溃、过载背压、半数 GPU 挂掉。"

### 0–10min 需求与容量数学（这题必须当场算）

FR：单请求 HTTP 入 → 凑批 → GPU → 结果回到正确用户；租户分级；限流。NFR：1000 RPS（防 10×）、P95<500ms、99.9% 可用、GPU 利用率 70–80%。

**延迟预算拆解**（追问"500ms 里排队 vs 计算各占多少"的答案提前埋好）：
`P95 500ms = 网络/LB ~20ms + admission ~1ms + 排队+凑批 ≤50ms + GPU 100ms + 结果路由 ~5ms ≈ 180ms`，剩 ~300ms 余量留给一次 dispatch 超时重试。**健康系统里计算(100ms)是常数，恶化永远先出现在排队项**。

**GPU 数量**（保守按平均批 32，虽然上限 100）：
```text
单 GPU：1s / 100ms = 10 batches/s × 32 req = 320 RPS
1000 RPS ÷ 320 = 3.125 → 4 块；按 70% 利用率 → 4/0.7 ≈ 6 块
追问 10K RPS：10000/320 ≈ 31.25 → /0.7 ≈ 45 块
  （若流量大到平均批能凑到 ~100：单 GPU 1000 RPS → ~15–20 块——
   高流量下 batch occupancy 自然变高，这就是规模的红利）
```

### 10–18min 接口与数据模型

```text
POST /v1/completions        # 同步：握住连接直到结果或 deadline
  body: {model, input, params, priority?}
  hdr : Idempotency-Key     # 客户端重试去重（防双计费）
  → 200 {request_id, output, usage}
  → 429 {retry_after}（限流/队列满） | 503（过载按优先级丢弃） | 504（deadline 超时）

内部 RequestEnvelope：
  {request_id, tenant, priority, input, enqueue_ts, deadline, reply_to}
  # reply_to = 接入节点 ID，结果路由的关键（深挖 2）
```

同步形态几乎无持久状态：in-memory 有界队列 + 各 handler 节点的 `futures[request_id]` 表。计费/审计走异步 usage log（append-only），不在热路径上写 DB。

### 18–30min 架构图与主流程

```text
Client ── POST /v1/completions（连接保持）
  │
  ▼
LB ──► API/Handler 节点 ×N（auth + per-tenant token bucket
  │      + 注册 futures[request_id]，挂 deadline timer）
  │ enqueue(envelope)                    ▲ result 按 reply_to 路由回原节点
  ▼                                      │
有界优先级队列（paid/free 加权轮询；满 → 429/503）
  │
  ▼
Batcher（双触发：凑满 B=32~100 OR max_wait 20–50ms 到期，先到先发）
  │ dispatch(batch, lease=300ms)
  ▼
GPU Worker Pool（每 worker 串行一批；least-loaded 挑 worker）
  │ outputs 与 inputs 按位置 zip 回 request_id
  ▼
Result Router ──► reply_to 节点 futures resolve ──► HTTP 200
```

**主流程每个箭头讲三件事**：① handler 收请求：先 token bucket（防单租户打爆），再入队——**队列满立刻 429，绝不无界缓冲**：deadline 内做不完的请求，入队只是把 500ms 超时变成 30s 排队后照样超时。② batcher 双触发：高流量凑满为主（等待→0），低流量超时发半满批——GPU 空转才是浪费，半满批照发。③ dispatch 带 lease：300ms（≈3× 批时长）未 ack → 整批 requeue（推理无副作用，重试安全）。④ 结果 zip：`batchstring` 保证输出与输入同序，第 i 个输出对应第 i 个 request_id——顺序即协议，乱序后端才需要显式 ID 回传。

### 30–36min 变体：异步 Batch API 产品形态（队列/结果存取/定价语义）

若面试官把题转向 Anthropic Message Batches 形态，切这套：**submit**（requests 数组，每条带 `custom_id`，≤100K 条/256MB）→ 校验后落对象存储 + jobs 表（durable，先落库再返回 batch_id）→ **调度**：batch 池用闲时容量填 GPU 空隙，池上限设 provider 容量 ~70%，永远给 interactive 留余量（分池语义见 [../../03_gaps/scaling.md](../../03_gaps/scaling.md) LLM 网关节）→ **结果存取**：乱序完成、按 `custom_id` 写对象存储，poll `processing_status` 或 webhook，保留 29 天 → **定价 -50% 的经济学**：用户拿延迟换价格，供给侧削峰填谷把 GPU 利用率抬平。**幂等**：batch 创建带幂等键、`custom_id` 批内唯一；单条 `expired`（24h 没排上）明确标出让用户重提交，不静默吞。细节与叠加 caching 的折上折见 [../../03_gaps/cost_latency.md](../../03_gaps/cost_latency.md) Batch API 节。

### 36–46min 可靠性 ｜ 46–54min 观测与容量应对（见下两节）｜ 54–60min Trade-offs

## 深挖 3 处

### 深挖 1：双触发参数怎么定，adaptive 怎么做

max_wait 从延迟预算倒推：500ms − 100ms(GPU) − ~25ms(网络) − 300ms(重试余量) → 凑批+排队预算 ~50ms，取 max_wait=50ms 上限。批大小 B 不追求 100：**batch occupancy（平均批装载率）是核心效率指标**——occupancy 70%+ 时 GPU 利用率达标，再调大 B 只伤延迟。Adaptive 版：按最近 1s 到达率 λ 估计"等满一批要多久"（B/λ），若 B/λ > max_wait 就直接按 λ×max_wait 缩目标批——低流量自动小批低延迟，高流量自动大批高吞吐，参数自己收敛。一句话总结："我不手调 batch size，我定延迟预算，让 occupancy 指标驱动它。"

### 深挖 2：结果如何路由回正确用户（correlation，多节点化）

单机答案 30 秒说完：handler 注册 `futures[request_id]`，result router resolve 它。真正的考点是**多 API 节点**：

- **方案 A（per-node batching）**：每个 API 节点自带 batcher、直连一个 GPU 子集。无跨节点路由，最简单；但批装载率随节点数被稀释（同样流量切 10 份，每份都凑不满批），GPU 静态划分浪费容量。小规模可用。
- **方案 B（中心队列 + reply_to，我选这个）**：envelope 带 `reply_to=node_id`；result router 完成后按 reply_to 投回原节点（Redis pub/sub per-node channel 或直接 gRPC 回连）。多一跳 ~1ms，换来批装载率与 GPU 池利用率不随节点数退化。
- **节点挂了怎么办**：该节点持有的连接全断，futures 丢失——结果投递失败直接丢弃（客户端会超时重试，Idempotency-Key 去重防双计费）。不要为"结果必达"建持久化：同步 API 的合同是"连接在才有结果"。

### 深挖 3：真 LLM 化——continuous batching / KV cache / 100K RPS

`batchstring` 固定 100ms 是玩具合同。真 LLM：prefill compute-bound、decode memory-bound、每请求输出长度不同 → static batching 让短请求陪跑最长请求（head-of-line）→ **continuous batching（vLLM 式）**：每个 decode step 重组批，完成的请求立即腾位给队首。显存约束：KV per-token bytes $=2 \cdot n_{layers} \cdot n_{kv} \cdot d_{head} \cdot \text{dtype}$，显存 = 权重 + KV×并发 token 数 → **并发上限由显存定，admission 按预估 token 收，不按请求数收**。多 GPU 路由：least-loaded 打底；多轮/共享前缀流量用一致性哈希 sticky，命中 prefix cache 省掉大部分 prefill（[../../03_gaps/cost_latency.md](../../03_gaps/cost_latency.md)）。

**100K RPS 变体**先说这句："我把容量单位从 RPS 换成 tokens/sec——100K RPS × (500 prefill + 200 decode tokens) = 50M prefill tok/s + 20M decode tok/s，两种负载瓶颈不同要分开定容，数量级是上万块 GPU。"随后给结构：cell 化（每 cell 自带队列+batcher+GPU 池，独立故障域），全局层只做路由、配额与溢流；prefill/decode 分离部署各自扩缩。这一步就是"剥掉 AI 皮"的评分点。

## 失败模式与恢复

- **GPU worker 批中崩溃**：lease 300ms 超时 → 整批 requeue（无副作用可重试）；retry budget ≤2 防重试风暴；request_id 去重保计费不双扣。最坏路径 2×(50+300)ms 仍压在 SLO 边缘——第二次重试直接 504，诚实失败。
- **批内单条失败**（非法输入/后端单条报错）：只 fail 该条不废全批；该条隔离成小批重试一次，再失败 → 400 返回用户——poison input 必须隔离，否则一条烂请求反复拖垮整批。
- **一半 GPU 挂掉如何自动限流**（原帖追问）：admission 与实测容量联动——token bucket 的 refill 速率 = 近期完成速率 × headroom，容量掉一半 refill 自动掉一半 → 新请求 429 + Retry-After；队列内按优先级从 free 尾部 shedding，保 paid SLO。**让拒绝发生在门口，不让队列吸收**。
- **新 GPU 启动要 5 分钟**（原帖追问）：warm pool（N+2 待命）+ 按时段/星期预测扩容提前 10min 拉机器；突发窗口内用降级扛：缩 max_tokens、简单请求路由小模型。
- **重复请求要不要缓存**（原帖追问）：exact-match `hash(model+input+params)` 短 TTL，只对 temperature=0 语义安全；semantic cache 有错误共享风险，只在产品层 FAQ 场景做，不进推理层。

## Trade-offs 三条（主动说）

1. **max_wait 大小 = GPU 效率 vs P95**：调大凑批更满省 GPU、伤延迟。我按延迟预算倒推 50ms 上限，之后靠 occupancy 指标驱动 adaptive，不手拍常数。
2. **中心队列 vs per-node batching**：中心队列多一跳、多一个组件，换来批装载率与利用率不随接入层扩容退化。小于 ~5 节点时 per-node 更简单，我明说这个分界。
3. **同步握连接 vs 异步 job/流式**：输出短（~几百 ms）同步最简单；输出长或排队深时同步白占连接与内存——超过约 5–10s 的工作必须转 202+poll 或 SSE 流式（[../../03_gaps/streaming.md](../../03_gaps/streaming.md)）。v1 同步 + 429 背压，出现长输出需求再上流式。

**观测最小集**（46–54min 段落说）：queue_wait P50/P95、batch occupancy、GPU busy%、per-tenant 429 率、retry/timeout 率、E2E P95 按 prompt 长度分桶（口径坑见 [../../03_gaps/cost_latency.md](../../03_gaps/cost_latency.md) TTFT/TPOT 节）；报警挂在 queue_wait 上——它是所有容量问题的前哨。

## 现实参照（只引本地已有链接/事实）

- **Anthropic Message Batches**：-50%、≤100K 条/256MB、poll、结果乱序按 `custom_id`、保留 29 天、`expired` 单条重提交——[../../03_gaps/cost_latency.md](../../03_gaps/cost_latency.md) Batch API 折叠节（含官方 docs 链接与代码形态）。
- **vLLM continuous batching / prefill-decode 分离**：题库 [A5] 参考打法明确点名的改进层（[../A_scenario_design.md](../A_scenario_design.md#a5)）。
- **LLM 网关分池 + 背压 + 租户限流**：interactive/batch 物理分池、batch ≤70% quota、逐级 backpressure——[../../03_gaps/scaling.md](../../03_gaps/scaling.md) LLM 网关折叠节（LiteLLM routing docs）。
- **1p3a 原题解**（容量数学 6 GPUs、双触发、批内 zip 回 request_id）：[../../../online_resource/1p3a-anthropic.md](../../../online_resource/1p3a-anthropic.md)。

> 高分句：Anthropic 的 SD 题都是"AI 皮、分布式系统骨"——这题剥掉皮就是 correlation + 排队论，容量用 tokens/sec 推理，拒绝发生在门口而不是队列里。
