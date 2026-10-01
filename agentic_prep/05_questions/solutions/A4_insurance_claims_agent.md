# [A4] Extend：保险理赔文档 agent（split/classify/extract/validate + 人审）· 完整解答

⏱ 读完 14 min ｜ 建议先自己限时 60min 答一遍再看（盲看解答记不住）。题面见 [../A_scenario_design.md](../A_scenario_design.md#a4)，rubric 出处 [../../../agentic/data/questions.json](../../../agentic/data/questions.json) → `q-extend-document-agent`。姊妹题 [A3](A3_document_pipeline.md)（PII/合规与人审经济学深挖在那边）。7/17 面试前配合 [../../06_company_briefs.md](../../06_company_briefs.md) Extend 卡（五句必背）复习。

## 题目还原

设计保险理赔文档 agent：一个上传包可能含多份扫描件（理赔申请表、发票、医疗账单、警方报告混在一个 PDF 里）；先 split/classify，再按 schema extract，**跨页校验金额**，低置信度送人工。要求支持重复上传、异步 webhook 和 schema version。**Rubric 权重**（v1）：25% pipeline/state、20% correctness、20% human review、20% version/idempotency、15% eval——版本与幂等占 1/5，这题一半分数在"无聊的工程"上，别把时间全花在模型。

## 开场澄清（6 问 + 为什么问）

1. **包的形态**：一个上传包最多多少页/多少份文档？有没有 500 页级的大包？→ 决定 split 策略与页级并行。假设：典型 5–50 页、2–8 份文档，长尾 200+。
2. **字段 accuracy 与 latency SLO**：关键字段（claim 金额、policy number、事故日期）目标？异步分钟级可否？假设：关键字段 99%+，P95 < 10min。
3. **下游是什么**：自动赔付决策还是给 adjuster 预填？→ authority 边界。假设：v1 只产结构化 claim + 证据，赔付决策在下游/人（这条要主动说，是 trade-off 3）。
4. **原图与中间结果保留吗**：retention 多久？→ 决定 artifact 能否支撑重放/重跑。假设：保留，受 retention policy 约束。
5. **人工修正如何回流**：reviewer 是我们的还是客户的（Extend 模式：客户 ops 团队用我们的 review UI）？修正可否进 eval/训练？
6. **重复上传语义**：同文件重传返回同结果，还是允许显式重处理（模型已升级）？→ 幂等层设计。

## 答案主线（按 [../../02_playbook.md](../../02_playbook.md) 时间盒 + v1 pacing 走）

**开场 90 秒**："核心是一条 **parse→split→classify→extract→validate→review 的 versioned artifact DAG**：每一步是纯函数，输出内容寻址的 artifact——幂等重试、崩溃恢复、新 schema 只重跑抽取层，全都从这一个决定里免费掉出来。正确性不靠模型自觉：schema validator + domain invariants 是确定性关卡，模型 confidence 只用来路由人审；人审队列按 expected loss 排序，修正绑定 source span 回流成回归 eval。重复上传、webhook、schema 演进各有一层幂等。最后讲 field-level F1 + 人审率。"

**需求与成功（0–7min）**：goal predicate = `每个上传包在 SLA 内变成：一组 classify 过的文档 + 每份按对应 schema_version 的抽取记录（字段带 confidence 和 source span）+ 跨页/跨文档校验结论；全部通过 → COMPLETED，否则带具体 review items 进 NEEDS_REVIEW 并在 review SLA 内闭环`。北极星：STP 率 @ 错误预算；护栏：关键字段错误率、review 积压、per-claim 成本。

**Job / Artifact 模型（7–14min，rubric 25% 的主要得分点）**：

```text
Upload:   upload_id, tenant_id, content_hash, pages, pointer
          （同 tenant 同 content_hash → 返回已有 upload，不重算）
Job:      job_id, upload_id, config_version = (parser_v, model_v, prompt_v, schema_v)
          state: RECEIVED→PARSED→SPLIT→CLASSIFIED→EXTRACTED→VALIDATED
                 →{NEEDS_REVIEW→CORRECTED}→COMPLETED | FAILED
          （config_version 在 job 创建时 pin 死——中途升级模型不影响在跑 job）
Artifact: artifact_id = hash(stage, parent_artifact_ids, config_version)
          stage, payload_pointer, confidence_summary, created_at
Field:    path, value, confidence, source_span(page, bbox), validators[]
ReviewItem: item_id, job_id, kind(field|split|classify), expected_loss, span, status
Correction: item_id, old, new, reviewer_id, reason, at   ← 回流 API
WebhookEvent: event_id, job_id, seq, type, job_snapshot  ← outbox 表
```

API：`POST /uploads`、`POST /jobs`（client 幂等键）、`GET /jobs/{id}`（权威状态+结果）、`POST /jobs/{id}/review-items/{id}/correction`、`GET /jobs/{id}/events?after=`、webhook 注册。

**架构图（14–18min 画）**：

```text
Client ──POST /uploads (content_hash 去重)──► Intake API + Auth
                                                │
                              Job Store（状态机, source of truth）
                                │ 同事务写 WebhookEvent (transactional outbox)
                                │            └─► Relay: at-least-once 投递 + backoff + DLQ
                                ▼
   Queue ──► Stage Workers（无状态、按 stage 消费、写内容寻址 Artifact）
   parse ─► split ─► classify ─► extract ─► validate ─► route
     │        │          │          │           │
     ▼        ▼          ▼          ▼           ▼
   Object Store（artifacts, 原图）      Trace/Metrics（redacted）
                                                │
                          Review Queue（按 expected loss 排序）
                            └─► Reviewer UI（bbox 高亮 source span）
                                  └─► Correction API ─► 回归 eval + 训练候选 + 下游重算
```

**处理 DAG 逐段讲（18–38min，本题核心交付物）**：
- **Parse**：OCR + layout（per-page artifact：text、bbox、表格结构）。**双模式路由**（Extend 卡原词）：light path（干净 text layer：小模型+启发式）vs performance path（扫描/手写：layout model / VLM / frontier）——accuracy/latency/cost 三角是架构主轴。
- **Split**：把一个 PDF 包切成文档段。信号组合：页眉页脚变化、"Page X of Y" 计数器复位、页面 embedding 相邻相似度骤降、首页版式特征，再用小模型对候选边界判定。产出 `DocumentSegment[]`（页范围 + 置信度）。**split 错误是下游一切错误的根**，所以 merge/split 是 reviewer 的一级操作（不只是改字段），修正后下游 stage 按 DAG 自动重算。
- **Classify**：每段打文档类型（claim form / invoice / medical bill / police report / other）+ 置信度；light 模型优先，低置信 escalate 到 frontier；`other` 或低置信 → 人审。分类决定用哪个 extraction schema。
- **Extract**：按 `(doc_type, schema_version)` 用 structured output 抽取。**每个字段必须带 source span，给不出 span 一律 null**——反幻觉是架构约束。长表格（100+ 行项目）按页抽片段：表头签名对齐 + 行连续性合并，`row_count` 和分页小计当合并校验。嵌套表格转 HTML 表示（markdown 表达不了合并单元格——Extend 产品原词，[../../06_company_briefs.md](../../06_company_briefs.md) 追问 1）。
- **Validate（rubric 20% correctness）**三层确定性关卡：
  1. schema validator：类型/必填/枚举/日期格式。
  2. field validators：policy number 存在性（查 policy DB）、金额非负、日期不在未来。
  3. **domain invariants（跨页/跨文档）**：`sum(line_items) == total_claimed`（容差=舍入）；发票合计 == claim form 声称金额；索赔人姓名/保单号跨文档一致；**页完整性**：`"Page X of Y"` 的 Y == 实际页数，缺页必须 flag 而不是让模型脑补缺失字段。
  invariant 失败 → 先做一次带定位提示的 targeted re-extract（self-correcting，Extend JD 原词）；再失败 → NEEDS_REVIEW，review item 附上具体违反的 invariant 和涉及的 span。
- **Route（rubric 20% human review）**：全过且校准置信度达标 → COMPLETED；否则生成**字段/边界粒度**的 review items（不是整包打回），按 `expected_loss = P(错)×cost(字段)` 排序——错金额和错备注代价差两个数量级，所以不按裸置信度排。P(错) 用 held-out 分桶校准，不是直接用 logprob（展开见 [A3](A3_document_pipeline.md) 深挖 1）。修正写回后该字段**锁定**：任何重跑不得静默覆盖人工值。

**低置信/重试/版本（38–48min）**：三层幂等各防一种重复（Extend 卡必背句 2）——`upload content_hash` 防重复上传、`job 幂等键` 防客户端重试建重复 job、`webhook event_id` 防消费端重复处理；stage 级重试靠 artifact 内容寻址天然幂等。schema version 与 webhook 详见深挖 1/2。

**Eval（48–55min，rubric 15%）**：
- **Field-level**：先归一化（金额转最小单位、日期 ISO、姓名 case/空白折叠），然后 per-field P/R/F1：预测值匹配 gold=TP、gold 有而缺/错=FN、gold 空而预测有=FP；按 doc_type × field 分桶报告，关键字段单列。长数组按 key 对齐行再算 cell accuracy + row recall。自由文本字段用 semantic similarity / 校准过的 LLM-as-judge（swap 消位置偏差，人工 gold 校准 κ，[../../01_core/06_eval_security.md](../../01_core/06_eval_security.md)）。
- **Document-level**：split 边界 P/R（over/under-split 分开报）、classify 混淆矩阵、关键字段全对率。
- **Workflow-level**：STP 率、人审率、修正数/claim、端到端时长、per-claim 成本。
- **专项集**（v1 rubric 点名）：long arrays（100+ 行发票）、missing pages（必须 flag 不得脑补）、重复页、跨页表格。
- **回归机制**：人工修正经抽样二次复核后冻结进回归集（只增不改）；任何 model/prompt/schema 变更过 paired 对比 gate，**per-customer slice**（一个客户的怪癖不能污染全局）；生产失败 trace 去敏回填（[../D_rapid_fire.md](../D_rapid_fire.md) D13）。

**Trade-offs（55–60min）**：见末节。

## 深挖 3 处（题库追问栏，每处给完整回答）

**1）webhook 重复或乱序怎么办？**——"先说根因：at-least-once 投递 + 重试 + 并行 delivery worker，重复和乱序是必然的，**不承诺顺序，把事件设计成顺序无关**。生产端：job 状态迁移和 WebhookEvent 在同一个 DB 事务里写（transactional outbox，[../../01_core/05_reliability.md](../../01_core/05_reliability.md)）——不会出现'状态变了但事件丢了'；relay 指数退避 + jitter 重试，N 次失败进 DLQ 告警；payload 带 HMAC 签名。事件结构：`{event_id, job_id, seq, type, job_snapshot}`——带**绝对状态快照**而不是 delta。消费端两道防线：event_id 去重表防重复；per-job 单调 seq，只应用 `seq > last_seen` 的事件，迟到的旧事件直接丢（快照语义下丢旧事件无损）。最稳妥的形态是 **thin notify**：webhook 只是 poke，消费方收到后 `GET /jobs/{id}` 拉权威状态——对重复和乱序天然免疫，我们文档里直接推荐这个模式。"

**2）新 schema 如何重跑旧文档？**——"这就是 artifact DAG 的回报时刻。① schema registry 管版本（semver）：加可选字段是 minor，改字段语义是 major；每条抽取记录都 tag schema_version，consumer 显式 pin 版本。② 重跑 = 建 backfill job：`artifact_id = hash(stage, parents, config_version)`，parse/split/classify 的输入和配置没变 → 缓存命中，**只有 extract→validate 需要重算**，成本只有抽取层 token。③ backfill 走独立低优先级 lane + 预算上限 + 游标 checkpoint（可断点续跑），不挤占线上 SLO。④ 人工修正的字段：语义未变的字段 carry forward（修正绑定的是 `(doc, field_path)` 不是某次模型输出）；语义变了的字段作废该修正、只对这些字段生成新 review item——绝不让新模型静默覆盖人工值。⑤ cutover：新 schema 先在 golden set + 生产抽样上 shadow 跑，出 field-level diff 报告，过 gate 再切默认版本，旧版本给 deprecation 窗口。"

**3）恶意 PDF 中的指令如何隔离？**——"三层，防御在架构不在 prompt：① 抽取模型 **quarantined**：无工具、schema 约束解码，注入最多污染字段值，而字段值要过 validators + invariants + span 校验；② 编排层（决定 DAG 下一步的代码）只消费 schema-valid 的结构化输出，**永远不把文档原文放进任何有工具权限的 context**——CaMeL 式控制/数据流分离；③ 隐藏文本检测：text layer 与渲染像素 OCR 结果 diff，'肉眼不可见但机器可读'的内容直接 flag。回归用 AgentDojo 式 utility-under-attack + ASR 双指标进 eval gate。用 lethal trifecta 自检：碰不可信内容的组件没有外发通道。完整展开见 [A3](A3_document_pipeline.md) 深挖 3；相邻练习题 `q-extend-permission-agent`（[../../../agentic/data/questions.json](../../../agentic/data/questions.json)）是这个追问的整题版。"

## 失败模式与恢复（本题具体场景）

- **worker 在 extract 第 30/50 页时 crash**：页级 artifact 已落的不重算；恢复 = 从 Job state + artifact DAG 找最深合法节点续跑；纯函数 + 内容寻址 → 重试幂等，无重复副作用。
- **split 切错（两份发票被当一份）**：下游全错的根因。reviewer 的 merge/split 操作是一级修正，写回后按 DAG 只重算受影响 segment 的 classify→extract→validate；split 边界置信度低时提前进人审，别等 validate 兜。
- **缺页包**："Page 3 of 7" 而实际只有 5 页 → 页完整性 invariant 直接 NEEDS_REVIEW（请求补件），**禁止**模型用上下文猜缺页字段——span 强制（无 span 即 null）从机制上封死这条路。
- **同一个包在处理中被再次上传**：content_hash 命中 → attach 到进行中的 job 返回同一 job_id；显式 `force_reprocess` 才建新 job（且复用 parse artifacts）。
- **review 积压超 SLA**：按 expected loss 保头部 + 超龄升级告警；短期把自动化阈值**收紧而不是放松**（宁可积压不能放错）；给客户的 job 状态诚实显示 NEEDS_REVIEW 而非伪装完成。
- **模型升级导致在跑 job 行为漂移**：config_version 在 job 创建时 pin 死；升级只影响新 job + 显式 backfill，对比走 shadow/paired eval gate。

## Trade-offs 三条（主动说）

1. **双模式路由（light vs performance）vs 单一 frontier**：全走 frontier 简单但贵 3–10 倍且慢；路由错判会伤质量，所以路由器保守偏 performance，用 eval 数据逐步扩 light 覆盖面。accuracy/latency/cost 三角是运营旋钮不是一次性决策（[../../03_gaps/cost_latency.md](../../03_gaps/cost_latency.md)）。
2. **字段粒度人审 vs 整包人审**：字段粒度 review UI 贵（要 bbox 高亮、split/merge 操作），但人审吞吐差 5–10 倍，而人审是本系统最贵的资源——值得。信号：某 doc_type 的 item 总是成组出现时，合并成包级审。
3. **v1 不做自动赔付决策**：agent 只产结构化 claim + 证据链，adjudication 留给下游——错误赔付的代价和合规责任不属于抽取层。信号：抽取质量稳定 + 客户明确要规则化 adjudication 时，作为独立的、带 policy engine 和 approval 的新系统做（参考 [A2](A2_subscription_cancellation.md) 的 proposal/approval 链路）。

## 现实参照（只引本地已有链接）

- Extend 产品机制（本题就是照它出的）：parse/split/classify/extract/validate/review 术语、`NEEDS_REVIEW` + correction 回流 API、双模式模型路由、table-to-HTML + bbox citation——[Extend Docs](https://docs.extend.ai/)、[Extend Product](https://www.extend.ai/)、[YC JD](https://www.ycombinator.com/companies/extend)，速记见 [../../06_company_briefs.md](../../06_company_briefs.md) Extend 卡。
- 幂等与 outbox 正典：[Stripe idempotency](https://stripe.com/blog/idempotency)、[transactional outbox](https://microservices.io/patterns/data/transactional-outbox.html)（[../../01_core/05_reliability.md](../../01_core/05_reliability.md)）。
- 注入与隔离：[AgentDojo](https://arxiv.org/abs/2406.13352)、[CaMeL](https://arxiv.org/abs/2503.18813)、[lethal trifecta](https://simonwillison.net/2025/Jun/16/the-lethal-trifecta/)（[../../01_core/06_eval_security.md](../../01_core/06_eval_security.md)）。
- Eval 词汇与 judge 校准：[Anthropic evals blog](https://www.anthropic.com/engineering/demystifying-evals-for-ai-agents)、[MT-Bench](https://arxiv.org/abs/2306.05685)（[../../04_benchmarks.md](../../04_benchmarks.md)）。

> 一句话收尾：parse→split→classify→extract→validate→review 是一条 versioned artifact DAG——幂等、恢复、schema 重跑、成本控制，全是同一个设计决定的红利。
