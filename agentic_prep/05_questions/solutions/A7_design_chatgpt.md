# [A7] Design ChatGPT：多轮对话后端 + SSE streaming · 完整解答

⏱ 读完 15 min ｜ 建议先限时 45 分钟白板答一遍再看（盲看解答记不住）。题面原文见 [../A_scenario_design.md](../A_scenario_design.md#a7)。

## 题目还原

设计 ChatGPT 类服务后端：多轮对话、持久化历史（数天后续聊携带上下文）、context assembly、GPU 集群推理分发、SSE token 流式。指标：TTFT ≤500ms p50 / 2s p95；200M+ DAU；GPU 稀缺。Out of scope（hellointerview 版）：消息编辑、多模态、custom GPTs。**真正在考**：generation–connection 解耦、context 组装的 token 预算、GPU 按 tokens/sec 定容、断线/Stop 的完整语义。本篇是 [../../03_gaps/streaming.md](../../03_gaps/streaming.md) 与 [../../01_core/02_state_and_memory.md](../../01_core/02_state_and_memory.md) 的合体应用。

## 开场澄清（4–6 问 + 为什么问）

1. **推理自建 GPU 还是外部 API？**——题面"GPU 稀缺"暗示自建；决定容量推理必须按 tokens/sec 而非 RPS（Anthropic 组高分句，[../A_scenario_design.md](../A_scenario_design.md) A 组末尾）。
2. **TTFT 口径**：用户发送到首 token 渲染？含 safety 检查？——决定延迟预算怎么切分项。
3. **免费/付费分层存在吗？**——决定调度要不要 priority tier 与公平性设计（四个 deep dive 之一）。
4. **历史保留与删除权**（GDPR delete）in scope？——决定存储分层与 tombstone；本篇假设 in scope 但只点到。
5. **safety/moderation 是否 in scope？**——是的话要给它专门的延迟预算（高频追问，主动圈进来）。
6. **峰值倍数、多 region？**——假设 3× 峰值，先单 region 讲透再谈复制。

## 答案主线（按 [../../02_playbook.md](../../02_playbook.md) 时间盒）

**开场 90 秒**："这题的骨架是三层解耦——durable 的会话存储、turn 开始时一次性组装且流式期间不可变的 context、以及'生成写 durable log、连接只是 log 上一个 cursor'的流式层。我先定 SLO 和量级，给 API 与数据模型，走一条消息的完整生命周期，然后深挖断线/Stop 语义、长会话摘要、GPU 调度与公平，最后 trade-offs。"

### 需求与量级（0–7 min，数字当场算）

- 200M DAU × ~10 msg/天 = 2B msg/天 ≈ **23K msg/s 均值，峰值 ~70K msg/s**。
- 容量按 token：70K msg/s × ~300 output token ≈ **21M output tokens/s**；单 GPU continuous batching 下 ~2K tok/s → **万卡量级**——所以 utilization、batching、prefix cache 每个百分点都是真金白银，这是全题的成本重心。
- 存储：2B msg/天 × ~1KB ≈ **2TB/天**，按 user_id 分片 + 冷热分层（>90 天转对象存储）。
- 目标谓词：`Given a user message in a conversation, stream back a history-grounded response with TTFT ≤500ms p50, durably append both messages, resumable across disconnects and devices.`

### 接口与数据模型（7–14 min）

```text
POST /conversations                                → {conv_id}
POST /conversations/{id}/messages {content, client_msg_id} → 202 {turn_id}
GET  /turns/{id}/events        SSE；Last-Event-ID / ?after= 是同一 cursor
POST /turns/{id}/cancel        幂等
GET  /conversations/{id}/messages?cursor=          历史分页
```

- `conversations(conv_id, user_id, title, summary, summary_upto_seq, model_pref, updated_at)`
- `messages(msg_id, conv_id, seq, role, content, status ∈ {complete, aborted, failed}, model, usage, created_at)`——user_id 分片的 Postgres/KV，seq 单调。
- turn 期间的 token 流放 **Redis Stream** `turn:{id}:events`（durable log，XTRIM + TTL），最终消息落主库。
- 状态三分不混（[../../01_core/02_state_and_memory.md](../../01_core/02_state_and_memory.md) §1）：conversation state（context/summary）可丢可重建；execution state（turn 状态机、event log）在 DB/Redis；domain state 在这题就是 messages 本身。

### 架构图（14–25 min）

```text
Client (Web/App)
  │ POST message / cancel          ▲ SSE (Last-Event-ID)
  ▼                                │
API Gateway (auth / rate limit) ─► SSE Gateway ◄── Redis Streams (turn event log)
  │                                                    ▲ XADD（delta 合帧 + lifecycle 逐条）
  ▼                                                    │
Chat Service ─► Context Assembler ─► Inference Gateway ─► GPU workers（vLLM 式）
  │ 幂等写 user msg   │ summary+recent    │ 按模型分池队列
  ▼                   │ token 预算        │ continuous batching / priority
Message DB (user_id 分片) ◄── turn 完成落 assistant msg + usage
  └── async：摘要 job ／ safety 审计 ／ billing
```

锚（先说再画）：**生成与连接解耦**——inference worker 只写 event log，SSE gateway 只是 log 上的 cursor；连接死了生成不死，断线重连、多设备、水平扩展被同一机制化解（[../../03_gaps/streaming.md](../../03_gaps/streaming.md) 高分句）。

### 主流程：一条消息的生命周期

1. 用户发消息 → gateway 鉴权限流 → chat service 以 client_msg_id **幂等**写 user message → 创建 turn(running)。
2. **Context assembler 一次性组装**：system prompt + user memory + conversation summary（覆盖到 summary_upto_seq）+ 其后的原文轮次 + 新消息，塞进 token 预算（如 128K 留 4K output）；**流式期间 context 不可变**，写回在 turn 边界。前缀按稳定度递减排（system/memory 最前），既拿 provider prompt cache 也利于自建 KV prefix cache。
3. Inference gateway 入队：按 model 分池；conv_id 一致性哈希 **sticky 路由**到 worker，命中上一轮的 KV prefix cache → prefill 大减 → TTFT 达标的关键。
4. worker 逐 token 生成 → **delta 合帧**（每 ~50ms 或 20 token 一条 XADD，防打爆 Redis；lifecycle 事件逐条写不合帧）→ SSE gateway XREAD 转发给所有 cursor。
5. turn 边界：完整 assistant message + usage 落主库（**不按 chunk 落库**），turn → complete；异步触发摘要 job。

### TTFT 预算拆解（追问必到，主动写在白板边上）

500ms p50 ≈ 网关路由 20ms + 读会话/组装 50ms（summary 是预计算的，热路径零 LLM 调用）+ safety 输入检查 0ms（与入队并行，见深挖 3）+ 排队 150ms + prefill 200ms（prefix cache 命中时 <50ms）+ 首个 decode step ~30ms。p95 恶化主要来自**排队和 cache miss**——分项打点归因，不只看总 TTFT。

### Eval / observability / rollout（46–54 min 快速过）

- 系统指标：TTFT/TPOT 分位 per model、队列深度、prefix cache 命中率、abort 率、SSE 重连率、每会话 token 成本。质量指标：thumbs、regenerate 率、safety 违规率。
- 新模型/新 system prompt 上线：held-out 对话回放做离线回归 → shadow → canary（盯 TTFT/拒答率/thumbs）→ rollback；线上 bad case 回流 regression 集（[../../02_playbook.md](../../02_playbook.md) 46–54 段）。

## 深挖 3 处

### 深挖 1：断线续传与 Stop 的完整语义（[../../03_gaps/streaming.md](../../03_gaps/streaming.md) 全套）

**续传**：event id 用 Redis Stream ID（单调递增，绝不用挂钟时间戳）；重连带 `Last-Event-ID` → 服务端先订阅、再 XREAD replay backlog、再接 live；**至少一次投递 + 客户端按 id 去重 = 恰好一次渲染**。刷新页面 = 同一 turn replay + 订阅增量，绝不重开一个 turn；多设备 = 同一 stream 上多个 cursor，免费拿到。
**Stop**：`POST /turns/{id}/cancel`（幂等）→ 置 `cancel_requested` → abort 到 worker 的生成 → 窗口期 Δt 内迟到 delta 按 **turn epoch** 丢弃（否则"停了还在打字"）→ 消息落 `status=aborted`、partial 内容保留并在 UI 标注、进 history 不冒充完整回复 → **usage 照记**（计费与限流都需要，中断不免单）。
**工程坑主动说**：nginx `proxy_buffering off`；heartbeat 15s < LB idle timeout（60s）；EventSource 只支持 GET 且不能带 Authorization header（fetch + 手动解析 SSE）。这三条是"踩过坑"信号。

### 深挖 2：长会话摘要——何时触发、存哪（高频追问原题）

- **触发**：turn 完成后异步检查——summary_upto_seq 之后的原文 token > 阈值（如 8K）才跑摘要 job（小模型），更新 conversation.summary 并推进游标；**热路径永不等摘要**。
- **存哪**：conversations 行上（summary + summary_upto_seq）；**原始消息永不删**——summary 只是 conversation state 的视图，可随时重算（"恢复的是 durable state，不是把旧聊天原样塞回模型"，01_core/02 高分句）；与 OpenHands condenser "原始 events 不删、condense 只是视图"同构（01_core/02 §8）。
- **组装公式**：context = system + memory + summary(≤1K) + 从 summary_upto_seq 之后取原文轮次直到预算满。
- **KV cache 代价**：摘要更新改变前缀 → 该会话 prefix cache 一次性失效——所以阈值化批量做，不每轮做。
- 追问"跨会话个性化？"：参照 ChatGPT memory 双层——saved memories 注入 system prompt + chat history 检索层（01_core/02 §7）；v1 只做 per-conversation summary，跨会话 memory 是 v2。

### 深挖 3：GPU 调度、公平资源分配与 safety 延迟预算

- **调度**：按 model 分 GPU 池；池内 continuous batching（iteration-level：每个 decode step 动态进出序列，不等最慢请求）；进阶提 chunked prefill / prefill-decode 分离防长 prompt 阻塞 decode（同 [A5]，深挖见 [../../03_gaps/scaling.md](../../03_gaps/scaling.md)）。
- **公平**：gateway 层 per-user token 滑动窗口限流 + 同用户并发 turn 上限（防重度用户垄断）；队列内加权公平调度，付费 tier 权重高；**过载时 admission control**：先降免费档（429 + retry-after），保付费 SLO——排队 2s 的 TTFT 已破约，早失败好过晚失败。
- **Safety 延迟预算**（高频追问）：输入侧小分类器（~20–50ms）与入队/prefill **并行**跑，命中则取消生成——TTFT 增量 ≈ 0，代价只是偶尔浪费几十 ms prefill。输出侧流式滑动窗口：SSE 前加 ~20 token 缓冲增量跑轻量 moderation，命中即断流 + 替换拒答 + turn 标 failed(policy)；用户感知首 token 晚 ~200–400ms——把数字说出来：缓冲越大召回越好、感知延迟越差。异步兜底：落库后全量审计复查，事后处置。

<details><summary>更多追问速答：多模型路由与灰度 ｜ 10 倍流量 ｜ GDPR 删除</summary>

- **多模型路由与灰度**：gateway 持逻辑模型名 → 物理 deployment 映射；新模型先 shadow（复制流量不回用户）再按用户桶 canary；会话内**固定模型版本**（mid-conversation 换模型口吻漂移 + cache 全灭）；回滚只改映射表。
- **10× 流量**：先垂直看瓶颈——GPU 池是唯一非弹性资源，答案是 admission control + 分层降级（小模型接管简单请求，路由思路见 [../../03_gaps/cost_latency.md](../../03_gaps/cost_latency.md)），而不是假装能瞬间加卡。
- **GDPR 删除**：messages 写 tombstone → 异步清 summary/检索索引/缓存 → 验证 retrieval 不再返回（删除完整语义见 01_core/02 §6 折叠）。

</details>

## 失败模式与恢复（本题具体场景）

- **GPU worker 生成中途崩溃**：heartbeat/lease 超时 → turn 标 failed，SSE 发终态 error event（lifecycle 不能丢）；客户端给 Retry——user message 已幂等落库，重试只是新 turn 重新生成。
- **Redis 丢失**：event log 是可重建视图，正在流的 turn 客户端断流后降级轮询 turn 状态；最终消息 source of truth 在主库，丢的只是没看完的中间 delta。
- **双发消息**（网络重试/双击）：client_msg_id 唯一约束，第二次返回同 turn_id。
- **写 DB 成功但入队失败**：turn 停在 pending → reconciliation 扫描重新入队（不靠"每条失败路径都处理对"，靠对账兜底）。
- **摘要 job 积压**：组装时发现未摘要原文超预算 → 现场硬截断最老轮次 + 告警，降级不阻塞。
- **SSE 假死**：15s 心跳注释帧；慢消费者各自拉 log 不反压生成，连接侧队列超限先合帧再断开走 resume。

## Trade-offs 三条（主动说）

1. **SSE + POST cancel 而非 WebSocket**：纯下行流，SSE 拿到协议内建重连/Last-Event-ID + proxy 友好（ChatGPT 本身就是 SSE）；真需要 server 主动 blocking request（如 approval）再升级 WS——先问方向性（streaming.md 传输选型）。
2. **Redis Stream 短 TTL event log 而非全量 event sourcing**：流式期间 durable、完成后转冷（最终消息在主库）；单区域 + 短 TTL 内 Redis 够用，多下游 fan-out（billing/analytics 独立消费）出现再上 Kafka（[../../03_gaps/scaling.md](../../03_gaps/scaling.md) 演进原则）。
3. **per-conversation 摘要而非跨会话 memory/RAG 历史检索**：v1 简单可控、无权限面；信号（用户频繁引用旧会话、超长会话占比高）出现再加检索层。

## 现实参照（只引本地已有链接）

- 传输与续传的全部机制、SSE replay 伪码、Redis Streams cursor：[../../03_gaps/streaming.md](../../03_gaps/streaming.md)（内含 [MDN SSE](https://developer.mozilla.org/en-US/docs/Web/API/Server-sent_events/Using_server-sent_events)、[Ably: when Redis is enough](https://ably.com/blog/ai-chat-stream-resumption)、LibreChat/Netclode 模式）。
- Provider 侧流式事件状态机（自建 gateway 要归一化这层）：[Anthropic streaming docs](https://platform.claude.com/docs/en/build-with-claude/streaming)、[OpenAI Responses streaming](https://developers.openai.com/api/docs/guides/streaming-responses)（均见 streaming.md）。
- ChatGPT memory 双层（saved memories + chat history reference）：[OpenAI 官方](https://openai.com/index/memory-and-new-controls-for-chatgpt/)（见 [../../01_core/02_state_and_memory.md](../../01_core/02_state_and_memory.md) §7）。
- Continuous batching / KV cache / 按 tokens/sec 定容：姊妹题 [A5](../A_scenario_design.md#a5) 参考打法 + [../../03_gaps/scaling.md](../../03_gaps/scaling.md)、[../../03_gaps/cost_latency.md](../../03_gaps/cost_latency.md)。
