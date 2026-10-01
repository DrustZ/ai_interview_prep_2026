# Streaming 与可中断 UX

⏱ 骨架 6 min ｜ 含深潜与资料 30 min ｜ 面试前只看 ⭐⭐⭐ 部分

## 30 秒版本（3 句话）⭐⭐⭐

1. Agent 产品的 streaming 本质是 **durability 问题而非 transport 问题**：token 先写 durable event log（Redis Streams / ring buffer），HTTP 连接只是 log 上的一个 cursor——断线重连、多设备、水平扩展全靠这一层解耦。
2. **中断是异步协作协议**：`cancel_requested` 只是意向标记，到 in-flight LLM call / running tool 真正停止有一个窗口期 $\Delta t$，期间到达的 delta 要按 turn epoch 丢弃，partial 结果必须落显式终态（`aborted`）。
3. 传输选型只问一件事：是否需要 server 主动向 client 发起 blocking request（如 approval）——不需要就 SSE + POST 控制通道，需要才升级 WebSocket 或双向 JSON-RPC（Codex app-server 模式，见 [mirendil 整理](../../projects/takehome_mirendil/03_option2_cloud_agent_chat.md)）。

## 核心概念

### 传输选型：SSE vs WebSocket ⭐⭐⭐

| 维度 | SSE | WebSocket |
|---|---|---|
| 方向 | server→client 单向 | 全双工 |
| 断线恢复 | 浏览器自动重连 + `Last-Event-ID` 协议内建 | 自己造：心跳、重连、resume token |
| 基础设施 | 纯 HTTP，LB/proxy/HTTP2 友好（需关 buffering） | 需 LB 支持 upgrade，企业代理常掐长连接 |
| 客户端→服务端控制 | 走独立 POST（stop/steer 是普通请求） | 同连接发 cancel/steer 帧 |
| 适用 | 90% 场景：下行 token/事件流（ChatGPT 即 SSE） | 高频双向：语音、协作编辑、server 发起的 blocking approval |

第三选项：**双向 JSON-RPC**（Codex app-server：默认 stdio-JSONL，WS 标注 experimental；approval 是 server 发起的 blocking request，client 回 `accept/decline`；控制有 `turn/steer` 与 `turn/interrupt`）。

> 高分句：先问方向性——只有下行流就 SSE + POST 控制通道；真正需要 server 主动 blocking request 时才上 WS 或双向 JSON-RPC，Codex app-server 就是这个取舍。

### 五个机制 ⭐⭐⭐

| 机制 | 设计要点 |
|---|---|
| 可恢复流 | 生成先写 durable log，event id 单调递增（Redis Stream ID，别用挂钟）；重连带 `Last-Event-ID`/`lastStreamId`，server 从 cursor replay backlog 再接 live（`XREAD` → `XREAD BLOCK`）；至少一次投递 + 客户端按 id 去重 = 恰好一次渲染 |
| token streaming | append-only text delta，直接渲染；持久化与 usage 记在 turn 边界（`onFinish`），不按 chunk 落库 |
| tool-call streaming | 结构化 **partial JSON**：增量 parser 或等参数完整再动作；状态机 `input-streaming → input-available → output-available \| output-error`（AI SDK 5）；各家 SDK 事件序不同，自建 harness 最难的就是归一化这层 |
| 中断语义 | `cancel_requested` ≠ 停止：链路是 flag → abort provider stream → 向 tool 发协作取消（SIGTERM + grace timeout）；cancel 幂等；区分 interrupt（终止）与 steer（注入输入不终止） |
| partial 标注 + 背压 | 被中断消息带终态 `status ∈ {complete, aborted, failed}`，UI 显式"已中断"，进 history 须标注；背压：慢消费者各自拉 log 不反压生成，连接侧队列超限先合帧（coalesce text deltas）再断开 |

<details><summary>可恢复流实现细节（Netclode / LibreChat / Ably 模式）</summary>

- Netclode：单条双向流（Connect RPC），所有事件持久化 Redis Streams；客户端带 `lastStreamId` 重连，服务端从该 cursor `XREAD` 补历史再 `XREAD BLOCK` 续实时。take-home 可用 SQLite/内存 ring buffer 复刻。
- LibreChat：chunk 实时写入按 `chat_id:message_id` 键的 Redis stream，后端订阅转发为 SSE；Redis 共享使多实例部署下"A 实例开始的生成可在 B 实例恢复"，rolling deploy 不掉流。
- Ably 总结的坑：Redis 够用的边界是单区域 + 短 TTL；跨设备接管、agent handoff 需要 durable session（持久可寻址、offset-based resumption）。
- buffer 要有 TTL/截断策略（如保留最近 N 事件 + 完成后转冷存储），否则长对话内存爆。

</details>

<details><summary>中断链路时序（Stop 按钮到真正停止）</summary>

- UI 乐观置灰 → `POST /turns/{id}/cancel`（幂等，重复点无副作用）→ orchestrator 置 `cancel_requested`。
- 传播：abort provider HTTP stream（SDK 的 AbortSignal）→ running tool 协作取消（cancellation token / SIGTERM，grace timeout 后 SIGKILL）。
- 窗口期 $\Delta t = t_{\text{stopped}} - t_{\text{requested}}$ 内仍有 delta 到达：给每个 turn 一个 epoch，迟到事件按 epoch 丢弃，否则"停了还在打字"。
- 终态落库：`status=aborted`，partial 内容保留；已发生副作用的 tool（邮件已发）不能假装没发生——记录并在 UI 展示。
- usage：中断的 turn 仍计已消耗 token（计费与限流都要）。

</details>

## 面试常问 3 题

**Q1. 设计 ChatGPT backend：SSE streaming + context assembly**（真题：hack2hire 题库 🤖 未交叉验证，[本地](../../online_resource/question-bank/hack2hire-premium.md)；OpenAI 前端/全栈轮 2026 也反复考 streaming chat UI + SSE 断流恢复）

<details><summary>参考打法</summary>

- 先画三层解耦：inference worker（生成）→ durable event log → SSE gateway（按 cursor 转发）；连接死了生成不死，这是全题的锚。
- context assembly 在 turn 开始一次完成：system prompt + memory + token-budget 截断的 history；流式期间上下文不可变，写回在 turn 边界。
- 断线恢复：event id 单调，重连带 `Last-Event-ID`，replay 后接 live；多副本下任意实例可服务重连。
- fan-out 顺带答掉多设备：同一 chat 的多个 tab = 同一 stream 上多个 cursor。
- 主动提 proxy 坑（见常见坑第 5 条）——OpenAI 前端轮明确把"主动讨论边界情况"当评分项。

</details>

> 高分句：streaming 层的核心决策是 generation–connection decoupling——连接只是 durable log 上的一个 cursor，重连、多设备、水平扩展三个问题被同一个机制化解。

**Q2. 用户点 Stop 之后，系统里到底发生了什么？**

<details><summary>参考打法</summary>

- 先分语义两级：interrupt（终止 turn）vs steer（不停止、向进行中 turn 追加输入）——Codex 协议里是两个独立方法 `turn/interrupt` / `turn/steer`。
- 按时序讲全链路：幂等 cancel API → `cancel_requested` flag → abort provider stream → tool 协作取消 + grace timeout。
- 点出窗口期 $\Delta t$ 和 turn epoch 丢弃迟到 delta——这是区分"背过题"和"踩过坑"的细节。
- partial 终态：`aborted` 状态 + UI 标注 + 进 history 时不冒充完整回复；副作用型 tool 的结果要如实保留。
- 收尾提 usage 记账：中断不免单。

</details>

> 高分句：中断不是 kill 而是异步协作协议——系统必须显式定义 cancel 意向到真正停止之间事件的处置规则，以及 partial 结果的可信标注。

**Q3. tool-call 怎么流式渲染？慢消费者会把系统拖垮吗？**

<details><summary>参考打法</summary>

- text delta append-only 直接渲染；tool call 是 partial JSON——用增量 parser 只做展示，**执行必须等 `input-available`**，绝不 eval 半截参数。
- 状态机化：`input-streaming → input-available → (approval 门) → executing → output-available | output-error`；approval 插在 available 与 executing 之间（blocking request）。
- 各 SDK（Claude Agent SDK / Codex / OpenAI）tool 事件排序不同，归一化事件模型是自建 harness 公认最难点。
- 背压：生成写 log、各连接自拉，慢消费者永不反压生成；连接侧队列超限 → 合并 text deltas → tool 参数以完整快照替代增量 → 仍超限则断开让其走 resume 路径。
- lifecycle 事件（`item/started`/`item/completed`）与 delta 分通道对待：降级时 delta 可丢可合，lifecycle 一条不能丢。

</details>

> 高分句：背压降级的分界线是——delta 可以合帧或丢弃（可由快照重建），lifecycle 事件必须逐条送达，否则客户端状态机直接错乱。

## 常见坑 checklist

- [ ] stream 生命周期绑死 HTTP 连接：关 tab = 生成中止、刷新 = 丢回复——解耦 + resume 是第一优先级
- [ ] 只做前端 `AbortController`：server 侧 LLM call 与 tool 继续跑，烧钱且状态漂移
- [ ] partial assistant message 无标记进 history（Vercel `useChat` 默认行为），下一轮被当完整回复拼进 context
- [ ] event id 用挂钟时间戳：不单调、重放去重失败——用 log 序号（Redis Stream ID）
- [ ] 反向代理没调：nginx `proxy_buffering off`、LB idle timeout 短于生成时长、无 heartbeat 帧——用户看到"卡死"而非流

## 现有系统怎么做

| 系统/方法 | 核心机制一句话 | 适用场景 | 链接 |
|---|---|---|---|
| SSE / EventSource 协议本体 | `id:`/`retry:` 帧 + 浏览器自动重连时回报 `Last-Event-ID`，replay 语义协议内建 | 一切下行流的传输底座 | [MDN](https://developer.mozilla.org/en-US/docs/Web/API/Server-sent_events/Using_server-sent_events) |
| Anthropic Messages streaming | 嵌套状态机：`message_start` → 按 `index` 的 `content_block_start/delta/stop` → `message_delta/stop`；tool args 走 `input_json_delta` 累积 | provider 侧事件模型的参照实现 | [docs](https://platform.claude.com/docs/en/build-with-claude/streaming) |
| OpenAI Responses streaming | 扁平 semantic events（`response.output_text.delta` 等），每事件带全局 `sequence_number` 游标；background mode = 官方 durable 流 | 对照事件建模差异；服务端可恢复流的官方版 | [docs](https://developers.openai.com/api/docs/guides/streaming-responses) |
| Vercel resumable-stream（AI SDK resume） | Redis pubsub + producer 侧 buffer：重连带 `resumeAt` 字符偏移，先补发 buffer 再接 live | Next.js/serverless 快速补上"刷新不丢流" | [GitHub](https://github.com/vercel/resumable-stream) |
| 自建 durable event log（LibreChat/Netclode 模式） | 事件全量 `XADD` 进 Redis Stream，连接只是 log 上的 cursor：`XREAD` 补历史 → `XREAD BLOCK` 续实时 | 多设备/多实例/审计要求的产品级方案 | [Ably 分析](https://ably.com/blog/ai-chat-stream-resumption) |
| partial-json 增量解析 | 对前缀 JSON 补全未闭合括号/按 `Allow` 掩码处理截断字面量，解析出"目前为止"的对象 | 流式 tool args 的展示层渲染 | [GitHub](https://github.com/promplate/partial-json-parser-js) |

<details><summary>SSE 协议 + 服务端 replay 伪码（event buffer + Last-Event-ID）</summary>

【技术机制】wire format 是行协议：`event:`（事件名）、`data:`（payload，多行拼接）、`id:`（设置客户端 `lastEventId`）、`retry:`（重连等待 ms），空行分隔事件。连接断开后浏览器自动重连并带 `Last-Event-ID` 请求头——replay 是服务端的责任，协议只负责把 cursor 送回来。

```python
buffers: dict[run_id, list[tuple[int, str, dict]]]   # 生产用 Redis Stream，内存版示意

async def sse_endpoint(req, run_id):
    # Last-Event-ID 与 ?after= 是同一 cursor 的两种拼法
    cursor = int(req.headers.get("Last-Event-ID") or req.query.get("after", -1))
    resp = start_response(headers={
        "Content-Type": "text/event-stream",
        "Cache-Control": "no-cache",
        "X-Accel-Buffering": "no",          # 关 nginx buffering，否则整段攒着不发
    })
    resp.write("retry: 3000\n\n")
    sub = subscribe(run_id)                  # 1) 先订阅，避免 replay 与 live 之间丢事件
    for seq, etype, payload in buffers[run_id]:   # 2) replay backlog
        if seq > cursor:
            resp.write(f"id: {seq}\nevent: {etype}\ndata: {json.dumps(payload)}\n\n")
            cursor = seq
    async for seq, etype, payload in sub:    # 3) 接 live，按 seq 去重（订阅早于 replay）
        if seq <= cursor: continue
        resp.write(f"id: {seq}\nevent: {etype}\ndata: {json.dumps(payload)}\n\n")
    # 4) 心跳：每 15s 写 ": ping\n\n"（注释行，不触发 onmessage），防 LB idle timeout
```

- 关键参数：heartbeat 周期必须 < LB idle timeout（常见 60s → 用 15s）；`retry` 只是建议值，浏览器默认 ~3s。
- 设计理由：先订阅再补历史 + 按 seq 去重 = 至少一次投递、恰好一次渲染；id 必须用 log 序号（单调），挂钟时间戳不单调会导致去重失败。
- 坑：EventSource 只支持 GET 且不能带自定义 header（要带 Authorization 得用 fetch + ReadableStream 手动解析 SSE，即 fetch-event-source 模式）；HTTP/1.1 每域 6 条连接上限（HTTP/2 才解）；buffer 无 TTL/截断策略会内存爆。

</details>

<details><summary>Anthropic streaming 事件状态机 + 中断语义</summary>

【技术机制】嵌套三层：message → content block（按 `index` 寻址，支持并行多 block）→ delta。完整序列：

```
message_start                          # 空 message 壳（id/model/usage 初值）
  content_block_start (index=0, type)  # text | tool_use | thinking
  content_block_delta (index=0)*       # delta 子类型见下
  content_block_stop  (index=0)
  ...（index=1, 2 重复）
message_delta                          # 顶层增量：stop_reason + 最终 usage
message_stop
```

delta 子类型：`text_delta`（append 文本）、`input_json_delta`（tool args 的**字符串片段** `partial_json`，需累积）、`thinking_delta`、`signature_delta`。另有 `ping`（可随时出现，保活）和 `error` 事件（如 mid-stream `overloaded_error`——要重试而不是当作正常结束）。

```ts
const blocks: Block[] = []
for await (const ev of stream) {
  switch (ev.type) {
    case "content_block_start": blocks[ev.index] = init(ev.content_block); break
    case "content_block_delta": {
      const b = blocks[ev.index]
      if (ev.delta.type === "text_delta") b.text += ev.delta.text
      if (ev.delta.type === "input_json_delta") b.partialJson += ev.delta.partial_json
      break
    }
    case "content_block_stop":
      if (blocks[ev.index].type === "tool_use")
        blocks[ev.index].input = JSON.parse(blocks[ev.index].partialJson) // 此刻才合法、才可执行
      break
    case "message_delta": stopReason = ev.delta.stop_reason; usage = ev.usage; break
  }
}
```

- 设计理由：`index` 寻址让并行 blocks（text + 多个 tool_use + thinking 交错）能在同一条流里复用同一套 start/delta/stop 生命周期；SDK 的 accumulator（Python `stream.get_final_message()`、Go `message.Accumulate(event)`）就是上面这段的官方实现。
- 中断语义：client 侧 AbortSignal / `stream.close()` → 断 HTTP 连接 → 服务端停止生成。**没有撤回**：已生成 token 照常计费，所以 turn 状态机里 partial 必须显式落 `aborted` 并记 usage。
- 坑：对 `input_json_delta` 逐 chunk `JSON.parse`（必炸，见 partial-json 块）；忽略 `ping` 把长间隔误判为断流；漏处理 `message_delta` 里的 `stop_reason=max_tokens`（截断被当完整回复进 history）。

</details>

<details><summary>OpenAI Responses streaming：扁平事件 + background 可恢复流</summary>

【技术机制】与 Anthropic 的嵌套模型相反，OpenAI Responses API 用**扁平 semantic events**——路径编码在事件名里，定位靠字段：

```
response.created → response.in_progress
  response.output_item.added (output_index)
    response.content_part.added (content_index)
      response.output_text.delta {item_id, output_index, content_index, delta, sequence_number}*
      response.output_text.done
  response.output_item.done
response.completed | response.failed | error
```

- 工具参数走 `response.function_call_arguments.delta`（同样是字符串片段，`...done` 事件才是完整 JSON）；另有 `response.refusal.delta`、`response.reasoning_text.delta`——只订 `output_text.delta` 会漏内容。
- **每个事件带全局递增 `sequence_number`**：这是官方内建的重连游标。background mode（请求带 `background: true`）把生成变成服务端任务：断连不杀生成，可 `GET /v1/responses/{id}` 轮询、带 `starting_after=<sequence_number>` 重挂 stream，`POST /v1/responses/{id}/cancel` 显式取消——等于官方托管版"durable log + cursor"，与自建方案是同构的。
- 归一化（自建 harness 最难点）：内部统一事件 `{run_id, seq, kind: text_delta | tool_args_delta | lifecycle, block_ref}`——Anthropic 的 `(event.type, index, delta.type)` 与 OpenAI 的 `(type 字符串, output_index/content_index)` 各写一个 mapper 收敛到这一层，UI 与持久化只认内部模型。
- 坑：把旧 chat.completions 的 chunk 模型（`choices[].delta`，无 lifecycle 事件）和 Responses 语义事件混在一个 handler 里；忽略 `response.failed` / `error` 事件只等 `completed`。

</details>

<details><summary>Vercel resumable-stream：Redis pubsub + buffer 的 resume 实现</summary>

【技术机制】一个 `streamId` 对应一个活跃 producer。fast path（无人重连）只花一个 `INCR` + `SUBSCRIBE`，几乎零开销；producer 把每个 chunk 追加进自己的 buffer 并 publish 到 Redis channel。重连时 consumer 调 `resumeExistingStream(streamId, resumeAt)`，producer 收到信号后把 buffer 里的内容补发（跳过前 `resumeAt` 个字符）再接 live。

```ts
const ctx = createResumableStreamContext({ waitUntil })   // serverless 里靠 waitUntil 保活 producer

// POST /api/chat —— 生成侧
const stream = await ctx.resumableStream(`chat-${chatId}`, () => llmSseStream())

// GET /api/chat/[id]/stream —— 重连侧（useChat({ resume: true }) 挂载时自动打）
const resumed = await ctx.resumeExistingStream(`chat-${chatId}`, resumeAt)
if (!resumed) return new Response(null, { status: 204 })  // 无活跃流；已完成流返回 422
```

- 设计理由：为 serverless（无 sticky LB、函数随时被回收）优化——不做全量持久化，只在"producer 还活着"的窗口内提供 resume，把常态成本压到最低。
- 与自建 durable log 的本质区别：**cursor 是字符偏移不是事件 id**；buffer 挂在 producer 上而非独立存储——producer 死了流就没了；已完成的流 resume 返回 422（要靠落库的最终消息兜底）。所以它解决"刷新/闪断不丢流"，不解决多设备、跨实例、审计。
- 坑：abort 与 resume 的交互（[vercel/ai#6502](https://github.com/vercel/ai/issues/6502)：客户端 stop 后 resumable stream 不停，服务端继续烧钱）；partial 消息默认无标记进 history；换 Redis 客户端要用 `resumable-stream/ioredis` 或 `/generic` 入口。

</details>

<details><summary>自建 durable event log：Redis Streams + after= cursor（对应 02_playbook）</summary>

【技术机制】每个 run 一个 stream key（`run:{id}:events`）。写侧 orchestrator 把**全部**事件 `XADD`（lifecycle 逐条写；text delta 先合帧——如每 50ms 或 20 token 一条——再写，否则每 token 一条 XADD 打爆 Redis）。`XADD` 自动 ID 是 `<ms>-<seq>`，单调且免费解决"别用挂钟"问题。读侧：

```python
async def stream_events(run_id, cursor="0-0"):
    key = f"run:{run_id}:events"
    # 1) catch-up：非阻塞读 backlog 直到追平
    while batch := await redis.xread({key: cursor}, count=500):
        for id_, ev in batch[0][1]:
            yield sse_frame(id_, ev); cursor = id_
    # 2) live：阻塞等新事件；超时窗口顺便当心跳
    while await run_active(run_id):
        batch = await redis.xread({key: cursor}, block=15_000)
        if not batch:
            yield ": ping\n\n"; continue
        for id_, ev in batch[0][1]:
            yield sse_frame(id_, ev); cursor = id_
```

- `GET /runs/{id}/events?after={cursor}` 与 SSE 的 `Last-Event-ID` 是同一 cursor 的两种拼法——一套 log 同时服务流式 UI、轮询客户端和 webhook 补偿。
- 投递语义：catch-up 与 live 的边界可能重复 → 至少一次投递 + 客户端按 id 去重 = 恰好一次渲染。
- 保留策略：`XTRIM MAXLEN ~10000` 截断 + run 完成后把最终 message 落主库、事件转冷存 + key TTL——三层兜底防内存爆。
- 多实例：状态在 Redis 不在进程内，任意 API 副本可服务重连，rolling deploy 不掉流（LibreChat 即此模式）。Ably 给出的边界：单区域 + 短 TTL 内 Redis 够用；跨区域接管、长离线、agent handoff 才需要 durable session 产品（offset-based resumption 的托管版）。
- 坑：用 Redis pub/sub 代替 Stream（无 backlog，断线即丢）；lifecycle 事件与 delta 不分级，降级时把 `item/completed` 一起丢掉导致客户端状态机错乱。

</details>

<details><summary>partial JSON 解析 + 流式渲染管线（delta→缓冲→markdown 安全渲染）</summary>

【技术机制·parser】`partial-json`（[JS](https://github.com/promplate/partial-json-parser-js) / [Python](https://github.com/promplate/partial-json-parser)）的思路：解析到输入结尾时不报错，而是补全未闭合的容器（`}` `]`），截断的字面量按 `Allow` 位掩码决定保留还是丢弃——`parse('{"a": "hel', Allow.STR)` → `{a: "hel"}`；不允许 `STR` 时 → `{}`（防止把半截 URL 当完整 URL 用）。注意每个 chunk 重解析整个 buffer 是 O(n²)——参数大或频率高时用维护活对象的增量 parser（`feed()` 只扫新字节）或降频到渲染帧。

铁律：**partial 结果只做展示**（灰显参数预览）；执行必须等 `content_block_stop` / `...arguments.done` 之后的完整 JSON——绝不 eval 补全产物。

【技术机制·渲染管线】

```ts
let buf = "", dirty = false
onTextDelta(d => { buf += d; dirty = true })       // 1) delta 只进缓冲，不直接触发渲染
setInterval(() => {                                 // 2) 30–60ms 一拍合并渲染（或 rAF）
  if (!dirty) return; dirty = false
  const md = closeDangling(buf)                     // 3) 临时闭合未完的 ``` 和 * ，防整页闪成代码块
  el.innerHTML = sanitize(renderMarkdown(md))       // 4) DOMPurify——流内容是不可信输入
}, 33)
```

- 设计理由：按帧合并把渲染成本从 O(tokens) 降到 O(帧率)；markdown 按 block 级 memoize（未变段落不重 parse）解决长回复卡顿。
- 坑：每 delta 全量重 parse markdown → 几千 token 后 UI 卡死；sanitize 只在最终消息做、流式路径裸 `innerHTML` → 半截 `<img onerror=` 也会执行，流式 XSS；未闭合 code fence 不做假闭合 → 后续正文全被吞进代码块再"弹回来"，视觉闪烁。生产案例见 [Aha! 的截断 JSON 处理实践](https://www.aha.io/engineering/articles/streaming-ai-responses-incomplete-json)。

</details>

## 自学资料

1. [Streaming Messages — Anthropic docs](https://platform.claude.com/docs/en/build-with-claude/streaming) — 事件状态机与全部 delta 类型的权威定义，面试引用以此为准 · 15 min
2. [Using server-sent events — MDN](https://developer.mozilla.org/en-US/docs/Web/API/Server-sent_events/Using_server-sent_events) — `id`/`retry`/`Last-Event-ID` 协议语义与 EventSource 行为，SSE 一切讨论的底座 · 10 min
3. [vercel/resumable-stream — GitHub](https://github.com/vercel/resumable-stream) — Redis pubsub+buffer 可恢复流的最小可读实现，README + src 半小时能读完核心 · 15 min
4. [Chatbot Resume Streams — AI SDK docs](https://ai-sdk.dev/docs/ai-sdk-ui/chatbot-resume-streams) — `useChat({resume})` → `GET /api/chat/[id]/stream` 的端到端接线，看别人怎么把 resume 塞进产品 · 10 min
5. [Streaming API responses — OpenAI docs](https://developers.openai.com/api/docs/guides/streaming-responses) — semantic events + `sequence_number` + background 模式，与 Anthropic 对照读 · 10 min
6. [AI chat stream resumption: when Redis is enough — Ably blog](https://ably.com/blog/ai-chat-stream-resumption) — Redis 方案的能力边界分析，回答"什么时候该上 durable session" · 12 min
7. [promplate/partial-json-parser-js — GitHub](https://github.com/promplate/partial-json-parser-js) — `Allow` 掩码设计与补全实现，理解流式 tool args 展示的正确姿势 · 8 min
8. [Streaming AI responses and the incomplete JSON problem — Aha! Engineering](https://www.aha.io/engineering/articles/streaming-ai-responses-incomplete-json) — 生产系统处理截断 JSON 的实战复盘 · 8 min

<details><summary>Sources（2024–2026 公开实践）</summary>

- [Ably: Resume tokens and last-event IDs for LLM streaming](https://ably.com/blog/resume-tokens-last-event-id-llm-streaming-reconnection) ・ [AI chat stream resumption: when Redis is enough](https://ably.com/blog/ai-chat-stream-resumption)
- [AI SDK UI: Chatbot Resume Streams](https://ai-sdk.dev/docs/ai-sdk-ui/chatbot-resume-streams) ・ [LibreChat: Resumable Streams](https://www.librechat.ai/docs/features/resumable_streams)
- [websocket.org: AI Token Streaming — From SSE to Durable Sessions](https://websocket.org/guides/use-cases/ai-streaming/)
- 本地：[Codex app-server / Netclode / AI SDK 坑位整理](../../projects/takehome_mirendil/03_option2_cloud_agent_chat.md)

</details>
