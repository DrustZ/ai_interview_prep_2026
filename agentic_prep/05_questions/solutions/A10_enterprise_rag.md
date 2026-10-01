# [A10] 企业级 RAG 聊天机器人（类 Glean）· 完整解答

⏱ 读完 14 min ｜ **也适用于 [A11]**（企业知识库 conversational agent：官方 rubric + cost/latency/accuracy 三约束变体 + 多租户变体 + 10M 规模变体）｜ 建议先自己限时 60min 答一遍再看（盲看解答记不住）。题面原文见 [../A_scenario_design.md](../A_scenario_design.md#a10) 与 [#a11](../A_scenario_design.md#a11)；深潜弹药库全部在 [../../03_gaps/rag.md](../../03_gaps/rag.md)。

## 题目还原

A10（OpenAI 60min ML SD）："设计企业内部搜索问答 RAG 机器人（类 Glean）：检索公司数据 + LLM 生成带引用回答；多用户/多租户、权限控制、答案带来源、低延迟。" A11 是同题的 generic 版，带**官方评分 rubric**：framing（点明概率性本质 + 澄清延迟/敏感度/规模）、retrieval depth、cost awareness、quality/safety、trade-off leadership。**真正在考**：能否超越教程级 RAG——原帖失分点就五条：做成教程级、忽略多轮、不讲评估、不考虑百万文档增长、忽略隐私。对应的得分动作：ACL 前置过滤、多租户隔离分层、retrieval/generation 分段评测、10M 容量账、多轮 query rewrite。

## 开场澄清（6 问 + 为什么问）

1. **数据源与规模**：哪些 connector（Drive/Confluence/Slack/Jira/wiki）？文档量级与日变更率？→ 决定 ingestion 架构与 shard。假设：10M 文档、日变更 ~0.5%。
2. **权限模型**：继承源系统 ACL？group 嵌套多深？撤权 SLA 要求？→ 这是整个设计的安全边界。假设：继承源 ACL，撤权分钟级。
3. **租户形态**：单公司内部工具还是多租户 SaaS？大客户有物理隔离/region/retention 合规要求吗？→ 决定索引隔离分层。
4. **延迟与成本 SLO**：首 token P95？检索预算？→ 假设首 token < 2s、检索 P95 < 500ms；这直接排除若干检索方案（见谱系段）。
5. **查询分布**：事实型 lookup、开放式调研、"这批文档整体在讲什么"各占多少？多轮占比？→ 决定 classic / agentic / GraphRAG 路由。假设：80% 事实型。
6. **错误代价与拒答政策**：幻觉引用错政策文档的代价？no-hit 时拒答可接受吗？→ 决定 grounding 强制程度。假设：宁拒答勿编造。

## 答案主线（按 [../../02_playbook.md](../../02_playbook.md) 时间盒走）

**开场 90 秒**："这是个概率性系统，所以我先定可度量的成功标准，再谈组件。我会把它设计成**三条独立管道——ingestion、retrieval、generation——因为它们的扩缩容曲线、失败模式和评测方法完全不同**。两个原则先立住：① **先定权限与新鲜度，再谈 chunking 与 rerank**——ACL 必须在检索阶段 pre-filter，生成后过滤等于泄露已发生；② 检索质量瓶颈几乎总在排序层，所以默认 hybrid recall + cross-encoder rerank 两阶段。最后讲分段评测和成本抓手。"

**需求与成功（0–7min）**：goal predicate = `每个 query 在延迟 SLO 内返回：要么每个 claim 都有可点开验证的 citation 且用户有权看到所有引用内容，要么明确说"知识库中未找到依据"；跨租户/越权泄露 = 0`。北极星：**有据可答率（answered-with-citation rate）@ 固定 faithfulness 预算**；护栏：越权召回数（必须为 0）、citation 点击验证通过率、P95 延迟、per-query 成本。
**方案定位（去向量化谱系，主动说给 A11 的 trade-off leadership 分）**："2025 后有个真实趋势：Claude Code 删掉向量库改用 grep + 多轮工具搜索，Cursor/Devin 跟进。但那个流派的成立前提是有结构语料 + agent 有时间预算 + 无 ACL。**本题三个变量——10M 文档、<2s 交互延迟、多租户 ACL——全部命中 index-based hybrid 是唯一解的区间**，grep 扫不动 10M 文档的延迟预算。谱系：<200k token 直接进 context → 结构语料 + 时间预算走 agentic/文件式 → 大规模/低延迟/ACL 走 hybrid 索引 → multi-hop 场景把索引当 agent 的一个 tool。"

**容量估算（10M 文档，A11 规模变体必答，口算给面试官看）**：

```text
语料：10M docs × ~2K tok 均值 = 20B tokens；原文 ~80GB
Chunk：400 tok/chunk → ~50M chunks
向量：1024 维 fp16 = 2KB/条 → 100GB；int8 量化 → 50GB；HNSW 图开销 +~30%
  → 单机内存放不下 → 8–16 shard（按 tenant hash 分），每 shard 3–6M 向量内存驻留
BM25：倒排索引与原文同量级 ~80GB，同样按 tenant shard
Embedding 全量构建：20B tok × $0.02–0.13/M = $400–$2.6K 一次性（便宜，别怕重建 embedding）
Contextual retrieval：+$1.02/M doc tokens ≈ $20K 一次性 → 只对高价值语料开（见主流程）
QPS：100K 用户 × ~5 query/天 ≈ 6 QPS 均值，峰值 ~50 QPS
  rerank：50 QPS × 100 候选 = 5K pairs/s → 数张 GPU（BGE fp16 batch）或托管 Cohere
生成：50 QPS × ~5K input tok（8 chunks + system）→ ~2.5B input tok/天 = 成本大头
  → 抓手：稳定前缀 prompt cache、semantic cache、模型分级路由（../../03_gaps/cost_latency.md）
增量：日变更 0.5% → ~25 万 chunk/天 re-embed，流式管道轻松吸收
```

结论一句话："存储和 embedding 都不是瓶颈，**生成侧 token 是成本大头，rerank 是延迟大头**——所以 cost 优化砍生成侧（cache/routing/top-k），latency 优化砍 rerank 候选数。"（正好接 A11 的 cost/latency/accuracy 三约束变体。）

**接口与数据模型（7–14min）**：

```text
POST /threads/{id}/messages     → SSE stream（token + citation event，带单调 event id 可续传）
GET  /threads/{id}/events?after=→ 断线重放（与 trace 共用一条 event log）
POST /messages/{id}/feedback    → thumbs / citation 点击 → eval 回归集
POST /ingest/events             → connector webhook（内容变更 + ACL 变更同一管道）

Chunk:    chunk_id, doc_id, tenant_id, text, heading_path("H1>H2>H3"), source_url,
          span(offset), updated_at, allowed_principals[], embedding_version
Document: doc_id, tenant_id, source, content_hash, version, acl, indexed_at
Message:  msg_id, thread_id, role, text, retrieved_chunk_ids[](审计用), citations[]
Citation: claim_text → (chunk_id, span)   # 可验证性架构，不是 UI 装饰
```

关键点说出来：chunk 的 `allowed_principals` 和 `tenant_id` 是**检索时的 filter 条件**，不是展示时的装饰；`retrieved_chunk_ids` 落库是为了审计（谁检索到了什么）和 eval 归因。

**架构图（14–18min 画）**：

```text
── Ingestion（异步流式，吞吐优先）────────────────────────────
Connectors (Drive/Confluence/Slack)
  │ CDC / webhook：内容变更 + ACL 变更走同一条管道
  ▼
Parse → 结构感知 chunking → [可选 contextual 前缀] → embed
  ▼
Vector index (HNSW, tenant shard) ─┐   两条索引都带 ACL metadata，
BM25 inverted index ───────────────┤   upsert + tombstone / 双缓冲
Doc & ACL store ───────────────────┘
── Query（同步，延迟优先）───────────────────────────────────
User → API + Auth（user → principals 集合展开）
  ├ Query rewrite（多轮改写成 self-contained query，小模型）
  ├ Hybrid recall：BM25 top-100 ∥ ANN top-100（均带 tenant + ACL pre-filter）
  ├ RRF 融合(k=60) → cross-encoder rerank → top-8 进 context
  ▼
Generation：grounded prompt → per-claim citation → span 存在性校验 → SSE
  ▼
Trace / Metrics / Audit log ──► Feedback → 回归 eval 集
```

**主流程走一遍（18–36min）**：
- **Ingestion**：connector 拉取/webhook → parse → **结构感知 chunking**：按 heading 层级切，400–800 tok，标题路径写进 chunk 前缀和 metadata，表格/代码块不从中间切断；overlap 0–15%——Chroma 实证：框架默认参数（800+400 overlap）往往最差，overlap 制造冗余挤占 context 预算。**Contextual retrieval 选择性开**：对财报/合同这类 chunk 脱离全文即有歧义的语料，ingestion 时用小模型给每 chunk 生成 50–100 tok 定位前缀再进双索引（Anthropic 数据：top-20 检索失败率 5.7%→2.9%，-49%；叠加 rerank -67%）；10M 全开要 ~$20K 且文档一变全部 chunk 前缀重生成，所以按语料价值分级。**增量**：CDC 触发只重嵌变更 chunk，upsert + tombstone；**ACL 变更走同一管道，撤权分钟级生效**——"索引要当流式系统运维，全量重建是 batch 时代思维"。
- **Retrieval**：① auth 层把 user 展开成 principals 集合（group 展开放 ingestion 侧预计算还是 query time，是存储 vs 查询延迟的 trade-off，主动讲）；② 多轮时 query rewrite（见深挖 3）；③ **hybrid recall**：BM25 抓精确词（型号/人名/错误码——dense 对 out-of-domain 术语必挂，hybrid 是默认不是可选）+ dense ANN，各 top-100，**ACL filter 同时作用于两条索引，漏一条就是泄露**；④ RRF 融合：$\sum_i 1/(k+r_i)$，k=60，用名次不用分数所以免归一化免调参；⑤ cross-encoder rerank top-100 → top-8 进 context，分数下限 floor 双截断、min-1 保底防空 context 触发幻觉。给数字：recall 阶段 top-100、rerank 后 top-8、检索 P95 < 500ms。
- **Generation**：grounded prompt 要求 per-claim 标 chunk id → **后处理把 claim 映射回原文 span 并校验 span 真实存在**（防幻觉引用）；无支撑的 claim 降级为"知识库中未找到依据"，而不是删 citation 留结论；no-hit（rerank 后无候选过 floor）→ 拒答 + 建议改写，不硬编。SSE 流式输出，未过 span 校验前 citation 标 provisional。
- **多租户三分层**（A11 变体必答）：大客户**独立索引/namespace**（物理隔离，合规驱动）；长尾客户**共享索引 + tenant_id 强制 filter**——filter 在检索层代码默认注入，不靠调用方自觉；中间层 namespace 逻辑隔离。防"租户 A 文档注入影响租户 B"：文档是 untrusted data，生成模型 quarantined（无工具、输出仅是带引用的文本），且跨租户从检索层就物理见不到。

**可靠性/安全（36–46min）**：过失败清单（见下节）；重点主动讲三条——ACL pre-filter 是安全边界不是装饰、semantic cache 的泄露面（cache key 必须含 principals hash）、audit log（谁检索了什么，合规审计用）。

**Eval（46–54min）**：见深挖 1。一句话框架先给出："评测第一原则是归因隔离：**retrieval recall 决定天花板，faithfulness 决定你离天花板多远**。"

**Trade-offs（54–60min）**：见末节三条。

## 深挖 3 处（面试官最可能追问）

**1）如何评估 RAG 质量、检测幻觉？（A10 追问 #1，A11 rubric 的 quality/safety 项）**——"第一步永远是归因拆分：答案错，是没检到（retrieval）还是检到了没用对（generation）？**检索侧**：从真实 query 采样 + 人工标 golden chunks，测 recall@k / MRR / NDCG——NDCG 与端到端质量相关性最强，因为 rank 位置影响模型注意力。**生成侧**用 RAGAS 三件套：faithfulness = LLM judge 把 answer 分解成原子 claims，逐条验证能否仅由 context 推出，支撑数/总数（2 claim 中 1 个被支撑 = 0.5）；answer relevance = 从 answer 反向生成问题、与原问题算 embedding cosine；context recall 需要 ground truth，只能离线。**归因用法**：context recall 低 → 修 chunking/hybrid/rerank；recall 高但 faithfulness 低 → 修 grounding prompt / citation 校验。**幻觉检测线上双保险**：deterministic 的 citation span 存在性校验（每条回答都跑）+ judge 抽查 faithfulness（采样跑，控成本）。judge 的坑主动说：自偏好、位置偏差、claim 分解本身不稳定——分数用于同评测集 A/B 回归可靠，绝对值别当真，定期人工标注校准。离线回归进 CI：改 chunking/embedding/prompt 前后跑同一评测集，防 silent regression。线上信号：citation 点击率、thumbs、escalation 率。"

**2）文档更新/版本怎么处理？两篇文档矛盾优先谁？（A10 追问 #2 + A11 追问 #1）**——"**更新**：CDC/webhook → 只重嵌变更 chunk → upsert 新版 + tombstone 旧版（或索引双缓冲原子切换）；定义 index staleness SLO（如 P95 < 15min）并监控 connector lag；答案附 as-of 时间（'基于 X 月 X 日的文档'）。**版本**：Document 带 version + content_hash，检索默认只出 latest，历史版本留审计。**矛盾**：不静默平均——先按 deterministic 规则裁决：source authority（官方 policy 库 > 个人笔记 > Slack 闲聊，authority 是 ingestion 时打在 metadata 上的分级）+ updated_at（同级取新）；规则裁决不了的，把两个 claim 连同各自来源和日期都呈现给用户，让用户看到 disagreement，这比替用户猜错更安全。**Embedding 换代（A11 追问 #3）避免全量重建**：chunk 带 embedding_version；新旧索引双缓冲——新写入双写，存量按 tenant/热度分批 backfill（全量 20B tok 重嵌只要 $400–$2.6K，真正贵的是 contextual 前缀和验证）；backfill 期间查询按 tenant 路由到已完成的一侧，shadow 对比新旧 recall 指标，达标后按 tenant 灰度切流、tombstone 旧索引。注意新旧 embedding 空间不可比，不能混在同一个 ANN 索引里查。"

**3）多轮对话历史怎么管理？（A10 追问 #3，原帖失分点）**——"三个决定：① **检索 query ≠ 用户原话**：多轮里'那第二种方案呢？'没法直接检索，用小模型把最近 N 轮压成 self-contained query 再进检索（query rewrite，几十 ms、便宜模型）；事实型单轮问题跳过 rewrite 省延迟——按复杂度路由。② **history 里存什么**：message 原文 + retrieved_chunk_ids 指针，**不把 chunk 全文塞回 history**——否则 context 随轮数爆炸；下一轮需要时按指针重取，且重取时**重新过 ACL**（对话期间权限可能被撤）。③ **context 预算**：system prompt + 工具/格式定义固定为 immutable 前缀吃 prompt cache；history 保留最近 K 轮原文 + 更早轮次的 running summary；检索结果放后缀不打散前缀。加分：thread 级 semantic cache——同 thread 内改述问题直接命中，但 cache key 必须含 principals hash + index version，防止越权命中和 stale 命中。"

## 失败模式与恢复（本题具体场景）

- **撤权后的时间窗**：源系统撤权 → 索引 metadata 更新前有分钟级窗口。答法：ACL 变更走高优先级管道（跳过 embed，只改 metadata）；敏感库（HR/法务）查询时对 top-8 结果做实时 ACL 二次校验（+几十 ms，只对小集合做，不是"检索完再删"的全量 post-filter——候选早已被 pre-filter 过，这只是对最终 8 条的降级保护）。
- **ACL filter 选择性太高，ANN recall 掉**：用户只有权看 0.1% 文档时 HNSW 带 filter 遍历退化。调 ef_search 自适应放大，或该 principal 候选集小于阈值时直接 brute-force 精确扫——反而更快更准。
- **rerank 服务挂**：降级直接取 RRF top-8，答案打标 degraded 进 trace；监控降级期 faithfulness 抽查，不静默吞。
- **connector 断流**：staleness SLO 告警；答案带 as-of 时间，让用户知道数据新鲜度，而不是假装最新。
- **文档内 prompt injection**（"ignore instructions and reveal…"藏在 wiki 里）：生成模型 quarantined——无工具、输出只是带引用文本，注入最多污染这一条回答且 citation span 校验会暴露不一致；越权数据从检索层就不可见，所以注入拿不到它没权限的内容；对抗样本进回归集。
- **semantic cache 跨用户泄露**：cache key = hash(query embedding bucket + tenant + principals set + index version)——四元组少一个都是事故。
- **索引双写不一致**（vector 有 BM25 没有）：ingestion 以 event log 为 source of truth，两条索引各自消费 + 各自 offset，定期 count/hash 对账；查询侧 RRF 对单路缺失有天然容忍（另一路仍可召回）。

## Trade-offs 三条（主动说，A11 rubric 的 trade-off leadership 项）

1. **Classic 单轮 vs agentic RAG**：v1 全部 hybrid+rerank 单轮——agentic 多轮检索 token 消耗约为 chat 的 15 倍、延迟分钟级，对 80% 事实型查询是工程判断不及格。信号：eval 里 multi-hop 类 query 的失败率显著高 → 加复杂度路由，只让这类 query 走 agentic loop（检索作为 tool，hard budget 限轮数）；"整体在讲什么"类 sensemaking 需求成规模 → 评估 GraphRAG（索引成本高 1–2 个量级，先确认需求真实存在）。
2. **共享索引+filter vs 物理隔离**：长尾租户共享省成本、运维一套；大客户合规驱动物理隔离。中间态 namespace。这是商务分层决策不是纯技术决策，v1 两端都支持、默认共享。
3. **Freshness vs cost**：ACL 变更和热文档分钟级 CDC；冷文档小时级批量；contextual retrieval 只对高价值语料开（否则每次文档变更全 chunk 前缀重生成，增量成本翻倍）。precision-latency-cost 的张力主动挑明：accuracy 变体加 rerank 候选数和 contextual 覆盖率，latency 变体砍 rerank 候选 + 上 cache，cost 变体砍生成侧（分级路由 + semantic cache + top-k）。

## 现实参照（只引本地已有链接，全部出自 [../../03_gaps/rag.md](../../03_gaps/rag.md)）

- Contextual retrieval 方法与消融数字（-49%/-67%、$1.02/M tok）：[Anthropic blog](https://www.anthropic.com/engineering/contextual-retrieval)
- Chunking 实证（默认参数最差、overlap 反直觉）：[Chroma report](https://www.trychroma.com/research/evaluating-chunking)
- RRF 公式与生产实现：[Elastic docs](https://www.elastic.co/docs/reference/elasticsearch/rest-apis/reciprocal-rank-fusion)；融合替代方案：[Weaviate docs](https://docs.weaviate.io/weaviate/concepts/search/hybrid-search)
- Rerank：[Cohere](https://docs.cohere.com/docs/rerank-overview)（托管）· [BGE/FlagEmbedding](https://github.com/FlagOpen/FlagEmbedding)（开源）
- 评测指标计算：[RAGAS faithfulness](https://docs.ragas.io/en/stable/concepts/metrics/available_metrics/faithfulness/)
- Agentic search 架构与 15x token 成本：[Anthropic multi-agent research](https://www.anthropic.com/engineering/multi-agent-research-system)；global sensemaking：[GraphRAG arXiv](https://arxiv.org/abs/2404.16130)
- 去向量化谱系一手资料：[OpenClaw memory docs](https://docs.openclaw.ai/concepts/memory) · [Milvus memsearch 拆解](https://milvus.io/blog/we-extracted-openclaws-memory-system-and-opensourced-it-memsearch.md)

> 一句话收尾：权限过滤的位置决定它是安全边界还是装饰——pre-filter 是安全边界，post-filter 是装饰；三条管道解耦 + 分段归因评测，是"做过产品"和"做过玩具"的分水岭。
