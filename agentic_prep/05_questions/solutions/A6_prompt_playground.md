# [A6] Anthropic Prompt Playground 全栈设计 · 完整解答

⏱ 读完 12 min ｜ 建议先开一个空白 Google Doc 限时 45 分钟盲打一遍再看（这轮考的就是书面表达速度）。题面原文见 [../A_scenario_design.md](../A_scenario_design.md#a6)。

## 题目还原

设计类 OpenAI Playground / Anthropic Console 的 prompt 工程平台：写 prompt→迭代→运行→保存最佳版本。约束：**不是 chatbot**（每次 Run one-shot、无会话记忆）；单用户项目（单写者）；prompt 可达 **10MB**；外部 LLM 慢但界面必须"感觉即时"；每次迭代持久化版本不丢好 prompt。**形式**：纯 Google Doc 书面讨论、不画图。**真正在考**：能否点破 10MB 的矛盾（可存储 ≠ 可运行）、版本模型、异步 run + 流式、LLM API 成本意识。

## 书面轮特别打法（先读这段）

- 评分材料就是你打出来的文档：heading + 短 bullet，不写大段散文；面试官边看边插 comment 追问，所以每节都留"钩子"（如 "cost controls → see §8"）。
- 每个取舍固定句式打出来："**Option A / Option B → I pick A because …**"——题库原帖明确说这是得分点。
- 文档前三行先写 assumptions，让面试官第一分钟就能纠偏；数字（10MB→token、$/天）当场算给他看。
- 下面"答案主线"就是可直接誊进 doc 的骨架，节奏对应 [../../02_playbook.md](../../02_playbook.md) 时间盒。

## 开场澄清（打进 doc 的 "Questions & Assumptions" 节）

1. **协作范围**：确认单用户单写者（题面给了）——决定版本模型是**线性链**，不需要分支/merge/CRDT；写明 "v2 若加协作，版本链升级为 DAG"。
2. **Run 语义**：one-shot、无会话记忆、参数 = model/temperature/max_tokens？——那么 run 是纯函数 `(prompt_version, params) → output`，天然可缓存、可复现。
3. **10MB 是上限还是常态？** 内容形态是"长文档素材 + 指令"？——决定编辑器方案与"可运行"的切分策略。
4. **规模**：~1K 活跃用户、~1K runs/天量级？——用来当场算出"贵的是 LLM 调用不是存储"，不做分片。
5. **"感觉即时"的具体 SLO**：打字零卡顿、保存 P95<100ms、run 提交 <200ms 出 pending、首 token 尽快流出？
6. **成本护栏是否 in scope**（per-user budget）？——题库高频追问，主动圈进来。

## 答案主线（= 可誊写的 Google Doc 骨架）

### §1 Requirements（0–7 min）

- Functional：编辑与保存大 prompt（≤10MB）；版本历史可回溯/恢复；对任意版本发起 Run（选 model+params）；流式看输出；run 历史与版本、参数、成本关联。
- Non-functional：保存 P95<100ms；run 提交即时反馈（异步）；版本零丢失（durable）；LLM 成本可控可见；单 region、读写 QPS 极低（人手打字），无分片需求。
- 一行目标谓词：`Given a prompt draft, the user can iterate version-by-version and run any version against a chosen model, with every version and every run durably recorded and cost-bounded.`

### §2 核心洞察先亮牌（书面轮最值钱的一段）

10MB ≈ **250 万 token**（~4 bytes/token），而模型 context 上限 ~100–200K——**"可存储可编辑"与"可运行"是两个系统边界**。存储层照单全收 10MB；运行层在提交时服务端 count tokens，超限返回 422 + 明确选项（运行选区 / head+tail 截取 / 拆分），**绝不静默截断**——截断跑出的"好结果"不可复现，恰好违背这个产品的存在意义。这段写在 doc 第二节，原帖标注这就是核心考点。

### §3 API（7–14 min）

```text
POST /prompts                          创建 prompt
PUT  /prompts/{id}/draft               autosave（发 delta，带 base_version，幂等）
POST /prompts/{id}/versions            commit draft → 新版本（append-only）
GET  /prompts/{id}/versions?cursor=    版本历史分页
POST /runs {prompt_version_id, model, params, idempotency_key} → 202 {run_id}
GET  /runs/{id}/events?after=          SSE：token 流 + 状态（Last-Event-ID 续传）
GET  /prompts/{id}/runs                run 历史（关联版本+参数+成本+延迟）
```

### §4 Data model

- `prompts(prompt_id, owner, name, head_version_id, draft_blob_hash, updated_at)`
- `prompt_versions(version_id, prompt_id, parent_version_id, blob_hash, kind: snapshot|delta, base_snapshot_id, token_count, note, created_at)` —— append-only
- `blobs`：**content-addressed**（sha256 → object store）；DB 只存元数据和 hash
- `runs(run_id, prompt_version_id, model, params_json, status, output_blob_hash, usage{in,out,cached}, cost, latency_ms, error, idempotency_key, created_at)`

不变式：version 一经创建 immutable；相同内容同 hash → 存储天然去重；**run 永远指向 version 而非 draft**（保证可复现）——对 draft 点 Run 时先自动 commit 一个 auto-version。

### §5 架构（书面轮写组件清单 + 数据流文字，白板轮才画图）

```text
Browser editor（piece-table + 虚拟化渲染，本地 buffer）
  │ autosave delta / commit / run          ▲ SSE
  ▼                                        │
API service ── Postgres(元数据/版本链/runs) ── Object store(blobs)
  │ enqueue                                │
  ▼                                        │
Run worker pool ──► LLM API(流式) ──► event log(Redis Stream) ──► SSE gateway
  └── usage/cost 记账 ＋ result cache key=(blob_hash, model, params)
```

### §6 两条主流程（14–25 min）

- **保存路径**：编辑器本地 buffer 打字（零网络依赖，"即时"的真正来源）→ 3s debounce autosave：客户端发 **delta**（相对 base_version 的 diff）而非全量 10MB → 服务端 apply 存 draft blob → 用户点 Save/Run 时 commit 成 version；token_count 异步计算回填。
- **运行路径**：`POST /runs` 带幂等键 → 校验 token_count ≤ model limit → 写 run(pending) 立即 202 → worker 调 LLM 流式 → token 合帧写 event log → SSE 推浏览器（断线 Last-Event-ID 续传，机制同 [../../03_gaps/streaming.md](../../03_gaps/streaming.md)）→ 完成落 output blob + usage/cost。**"感觉即时" = 乐观 UI + 202 快返 + 流式**，而不是让 LLM 变快。

## 深挖（高频追问的完整回答）

### 深挖 1："10MB 文件怎么处理？"

- **传输**：>1MB 走 presigned URL 直传 object store（multipart），API 只收 hash 注册——10MB 不过应用服务器内存。
- **编辑**：naive textarea 放 10MB 必卡死——rope/piece-table 数据结构 + 视口虚拟化渲染；autosave 永远发 delta。
- **运行**：服务端 tokenizer 现算（不信客户端），超限 422 + 三选项（选区运行 / head+tail / 拆分）；"可以静默截断或显式拒绝，我选显式拒绝，因为截断破坏 run 的可复现性。"
- **存储**：content-addressed 去重 + 版本间 delta（见深挖 2），10MB × 1000 版本 ≠ 10GB。

### 深挖 2："1000 次保存的版本追踪？"

- 天真方案每版全量快照：10MB × 1000 = 10GB/prompt，不可接受。
- 方案：**snapshot + delta 混合链**（git packfile 思路）——每 N=20 版落一个全量 snapshot，中间只存 diff；恢复任意版本 = 最近 snapshot + 重放 ≤19 个 delta，毫秒级。
- "可以纯 diff 链或纯快照，我选混合：纯 diff 恢复 O(N)，纯快照存储 O(N×10MB)，混合两头封顶。"
- content hash 兜底去重：没改内容的重复保存 same hash → 不产生新 blob、可不产生新版本。
- 版本链 append-only（parent_version_id 单链），单写者免 merge；**恢复旧版本 = 以它为 parent 开新版本**，不改写历史——和 run 的关联永不悬空。
- autosave draft 与 committed version 分开：draft 高频覆盖可丢，version 显式提交不可变——用户"迭代 50 次只想留 5 个里程碑"两层都照顾。

### 深挖 3："如何防 LLM API 花费失控？"

当场算：1K runs/天 × ~80K token prompt × $5/MTok（Opus 级 input，价目见 [../../03_gaps/cost_latency.md](../../03_gaps/cost_latency.md)）≈ $400/天 + output ≈ **$450/天**——这个系统最贵的是 LLM 调用，不是存储。四层防线：
1. **提交前预估**：token_count × 价格表显示成本，超阈值（如 $1/run）要求确认；
2. **per-user 日预算硬顶**：超了 429 + 面板可见余额，不是月底账单惊吓；
3. **result cache**：key = (blob_hash, model, params)；temperature=0 直接命中返回并标注 cached，>0 默认仍执行但提供"查看上次结果"；
4. **prompt caching**：迭代场景天然前缀稳定——长文档素材在前、指令在后，改指令不动素材时命中按 0.1× 计价（前缀规则见 cost_latency.md）。

### 深挖 4："大文档怎么搜索？"

两层："元数据搜索"（名字/note/model，Postgres 索引）即时可用；全文搜索走**异步索引**——commit 时把 blob 分 chunk 写倒排索引（Postgres FTS 起步），结果返回 version + offset 跳转。不在 10MB 字符串上现场扫描，也不为 v1 上向量检索——"关键词找回我上周那个 prompt"是主场景。

## 失败模式与恢复（本题具体场景）

- **两个 tab 同时 autosave**：delta 带 base_version，不匹配 409 → 客户端 rebase 或提示刷新；单写者所以不做 CRDT。
- **run worker 崩溃**：run 卡 running → lease 超时标 failed(retryable)；重试用同 idempotency_key，防重复计费；已流出的 partial 输出保留并标注不完整。
- **LLM API 超时/429**：指数退避重试；持续失败落 failed + 错误对用户可见；已消耗 token 照记账。
- **token_count 回填失败**：version 照常可用，run 提交时现算兜底。
- **浏览器崩溃**：本地 buffer 定期落 IndexedDB，重开恢复未保存内容——"不丢好 prompt"要覆盖到最后一公里。

## Trade-offs 三条（主动写在 doc 末尾）

1. **线性 append-only 版本链而非 git 式分支**：单写者场景分支是过度设计；信号（协作、A/B 实验需求）出现再升级 DAG。
2. **run 异步 + SSE 而非同步等待**：多一层 event log 复杂度，换来长 run 不占连接、断线可续传、run 历史可审计。
3. **不做分片、不做多 region**：读写流量是人手打字量级，把工程预算全花在成本护栏和版本可靠性上——"贵的是 LLM token，不是数据库"。

## 现实参照（只引本地已有链接）

- Prompt caching 前缀规则与 0.1×/1.25× 计价：[../../03_gaps/cost_latency.md](../../03_gaps/cost_latency.md)（内含 [Anthropic prompt caching docs](https://platform.claude.com/docs/en/build-with-claude/prompt-caching)）。
- SSE 断线续传 / event id / proxy 坑：[../../03_gaps/streaming.md](../../03_gaps/streaming.md)（内含 [MDN SSE](https://developer.mozilla.org/en-US/docs/Web/API/Server-sent_events/Using_server-sent_events)）。
- 状态三分法（可丢弃的 conversation/view vs durable execution state）：[../../01_core/02_state_and_memory.md](../../01_core/02_state_and_memory.md)。
- 姊妹题 [A12] OpenAI Playground（加前端 wireframe + 10x/1000x scale 追问，答法复用本篇）：[../A_scenario_design.md](../A_scenario_design.md#a12)。
