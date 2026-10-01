# [A3] 文档自动化管线：银行材料上传 / 医生账单报送 · 完整解答

⏱ 读完 12 min ｜ 建议先自己限时 60min 答一遍再看（盲看解答记不住）。题面原文见 [../A_scenario_design.md](../A_scenario_design.md#a3)。姊妹题 [A4_insurance_claims_agent.md](A4_insurance_claims_agent.md)（偏 agent 语义：DAG/webhook/schema version 深挖在那边）。

## 题目还原

两道真题共用一套骨架：(1) "Design a system to process 10K user uploads/month (bank payslips, IDs, references)"；(2) "Design a system that lets doctors automatically send billing info to insurers based on patient notes"。**真正在考**：① 你能不能第一分钟点破这不是 scale 题（10K/月 ≈ 0.004 QPS）而是**正确性、人审经济学、合规**题；② 异步管线的 durable job 状态与可恢复性；③ 验证不靠模型自觉——schema + domain invariants + 置信度路由人审；④ PII/HIPAA 边界。答题以银行版为主线，医生版当变体（深挖 2）。

## 开场澄清（6 问 + 为什么问）

1. **下游动作与错误代价**：抽取结果喂给贷款审批还是只做预填？错一个金额 vs 错一个备注的代价？→ 决定 expected loss 表和自动化阈值。假设：预填 + 关键字段驱动审批，金额/身份字段错误代价高两个数量级。
2. **输入质量分布**：数码 PDF（有 text layer）vs 扫描件 vs 手机照片？手写？多语言？→ 决定 parse 路由（light vs performance path）。假设：60% 数码、40% 扫描/照片，少量手写。
3. **Latency SLO**：用户等在页面上，还是分钟级异步可接受？假设：异步，P95 < 10min，webhook 通知。
4. **准确率目标与人审预算**：per-field 目标？有没有 reviewer 团队、多大？→ 阈值由人审容量反推。假设：关键字段 99%+，reviewer 0.5–1 人力。
5. **合规**：PII retention、data residency、能否调第三方 LLM API（zero-retention 条款）？医生版是否 HIPAA（BAA、minimum necessary）？→ 决定模型托管与日志红线。
6. **人工修正回流**：修正能否用于 eval/训练？→ 决定 self-correcting loop 能不能建。

## 答案主线（按 [../../02_playbook.md](../../02_playbook.md) 时间盒走）

**开场 90 秒**："先算个数：10K/月 ≈ 330/天，平均 QPS 不到 0.01——这题瓶颈不在吞吐，在**每份文档的正确性和出错的代价**。所以我把预算花在三处：每步版本化 artifact 的异步管线（可恢复、可重放）、schema + domain invariants 的确定性验证（模型 confidence 只是路由信号）、按 expected loss 排序的人审队列 + 修正回流。PII 在入库前 redact。最后讲 field-level F1 + 人审率的评测。"

**需求与成功（0–7min）**：goal predicate = `每个 upload 在 SLA 内产出 schema-valid 的结构化 record：要么全部验证通过自动完成，要么带具体 review item 进入人审并在 review SLA 内闭环；关键字段残留错误率 < 0.5%，PII 泄漏 = 0`。北极星：**STP（straight-through processing）率 @ 固定错误预算**；护栏：关键字段错误率、review 积压时长、per-doc 成本。成本口算：10K 文档 × ~5 页 × VLM 抽取 ≈ 每月几百到两千刀，LLM 成本远小于人审成本——**阈值调的是人审经济学，不是 GPU**。

**接口与数据模型（7–14min）**：

```text
POST /files            → file_id（content_hash 去重：同 hash 同 tenant 直接返回已有 file_id）
POST /jobs             → job_id（body: file_id, processor+schema_version；client 幂等键）
GET  /jobs/{id}        → 状态 + 结果 + 每字段 {value, confidence, source_span}
POST /jobs/{id}/corrections   → 人审修正回流（field_path, old, new, reviewer, reason）
GET  /jobs/{id}/events?after= → trace 增量读取（webhook 只是 poke，真数据从这拉）

Job:      job_id, tenant_id, file_id, state, config_version(model+prompt+schema), created_at
  state ∈ QUEUED→PARSING→EXTRACTING→VALIDATING→{NEEDS_REVIEW→CORRECTED}→COMPLETED | FAILED
Artifact: artifact_id = hash(stage, parent_artifact_ids, config_version)
          stage, payload_pointer(对象存储), schema_version, model_version, created_at
Field:    name, value, confidence, source_span(page, bbox), validators_passed[]
```

Artifact 内容寻址是本设计的支点：重试天然幂等（同输入同配置 = 同 id，缓存命中）、恢复 = 找最深的合法 artifact 续跑、新 schema 重跑只算 extract 层（详见 [A4](A4_insurance_claims_agent.md) 深挖 2）。

**架构图（14–18min 画）**：

```text
User upload (portal/API)
  │ POST /files (content_hash dedup) → POST /jobs
  ▼
Intake API + Auth ──► Job Store (state machine, source of truth)
  │                        │ transactional outbox → webhook relay (at-least-once)
  ▼                        ▼
Queue ──► Pipeline Workers（无状态，按 stage 拉任务）
  │   parse(OCR/layout) → extract(schema 约束) → validate(rules+invariants)
  │        │ 每步写 versioned Artifact ──► Object Store + Trace/Metrics
  │        └ PII redaction：日志/trace 只存 pointer + redacted summary
  ▼
Router：全过且高置信 → COMPLETED → export/webhook
        否则 → Review Queue（按 expected loss 排序）→ Reviewer UI（显示 source span）
                    └ correction API 回流 → 回归 eval + 训练候选
```

**主流程走一遍（18–28min）**：
- **Parse**：先探测 text layer 质量 → **双路由**：light path（数码 PDF：直接取 text layer + 小模型/启发式）vs performance path（扫描/手写：layout model / VLM / frontier）。产出 per-page artifact：text + layout + bbox。质量门：模糊/裁切/空白页在这里打回（"请重新上传"比错误抽取便宜得多）。
- **Extract**：按文档类型 schema 用 structured output（constrained decoding）抽取；**每个字段必须带 source span（page+bbox），给不出 span 的值一律置 null**——这是反幻觉的架构手段，不是 prompt 恳求。长表格按页抽片段再合并（见 [A4](A4_insurance_claims_agent.md) 主流程）。
- **Validate 三层**：① schema validator（类型/必填/枚举）；② field validators（日期格式、身份证/IBAN checksum、正则）；③ **domain invariants**：gross ≥ net、工资单日期序、payslip 雇主名 == 申请表雇主名（跨文档一致性）、行项目求和 == 合计。invariant 失败先做**一次**带定位提示的 targeted re-extract（self-correction），再失败进人审并附上具体违反项。
- **Route**：验证结果 + 校准后置信度 → auto-complete 或 NEEDS_REVIEW。人审修正经 correction API 写回，触发下游重算，且该字段被锁定——后续重跑不得静默覆盖人工值。
- **PII 边界**：原件加密存对象存储（retention policy 定期清除）；trace/日志只存 pointer + hash + redacted summary；reviewer UI 按需拉原图（审计谁看过）；第三方 LLM 走 zero-retention 条款，否则自托管。

**可靠性（36–46min）**：见下方失败模式一节，现场按 crash/重复/质量/积压清单过。

**Eval（46–54min）**：见深挖 1 和 [A4](A4_insurance_claims_agent.md) eval 段（field-level F1 定义在那边展开）。三层：**field**（per-field P/R/F1，关键字段单列）→ **document**（关键字段全对率、STP 率）→ **workflow**（人审率、修正数/doc、端到端时长、per-doc 成本）。人工修正经二次抽检后冻结进回归集（只增不改）；模型/prompt/schema 变更过 paired 对比 gate（[../D_rapid_fire.md](../D_rapid_fire.md) D13）。

**Trade-offs（54–60min）**：见末节。

## 深挖 3 处（面试官最可能追问）

**1）人审阈值怎么定？置信度能信吗？**——"队列不按置信度排序，**按 expected loss = P(错) × cost(字段) 排序**——错一个金额字段和错一个备注字段的代价差两个数量级（题库高分句）。P(错) 不能直接用模型 logprob——LLM 置信度普遍 miscalibrated，我用 held-out 集上按字段类型做 calibration（分桶实测错误率），或者双抽取器（两个模型/两次采样）一致性当信号。cost 是业务给的表：金额/身份字段高、地址中、备注低。阈值不是拍的：扫一遍阈值画出**人审率 vs 残留错误率的 operating curve**，按 'reviewer 容量' 和 '错误预算' 两条约束选工作点。冷启动保守（多送人审），eval 成熟后逐步放；review 积压时按 expected loss 保头部，超龄条目升级告警，绝不静默丢弃。"

**2）医生账单版有什么不同？**——四点差异：① 输入是自由文本 clinical notes 不是表单，抽取任务变成 '诊疗事实 → billing 结构'，每个 code 必须带 note 里的 evidence span，给不出证据不出 code；② **错误方向不对称**：漏报=收入损失，多报=upcoding（欺诈风险）——宁漏勿多，多报侧阈值单独收紧；③ **医生/biller 签核是硬性步骤不是可选优化**：系统只产 draft claim + 证据，提交动作永远在人批准之后（proposal→approve→execute，同 [../../01_core/05_reliability.md](../../01_core/05_reliability.md) 写操作边界）；提交用 idempotency key 防重复报送；④ 合规：HIPAA——BAA 覆盖所有处理方、minimum necessary（给保险公司的只含必要字段）、审计日志记录每次 PHI 访问但不复制全文。**保险公司的 denial/接受回执是免费的 outcome 信号**：denial reason 分桶回流成回归用例和阈值校准数据——这是这个变体独有的 flywheel。

**3）恶意 PDF 里的指令怎么隔离？（间接注入）**——"文档是 untrusted data，防御靠架构分层不靠 prompt：① 抽取模型是 **quarantined**——没有任何工具、输出被 schema 约束死，注入指令最多污染字段值，而字段值要过 validators + invariants + span 校验这三道确定性关卡；② 编排层（决定下一步做什么的代码/agent）**永远不读文档原文**，只读 schema-valid 的抽取结果——这是 CaMeL 式控制流/数据流分离（[../../01_core/06_eval_security.md](../../01_core/06_eval_security.md)）；③ 隐藏文本检测：text layer 与 OCR 渲染像素结果 diff，出现 '肉眼不可见但 text layer 有' 的内容直接 flag 人审；④ 回归：AgentDojo 式双指标（utility under attack + attack success rate）纳入 eval gate。用 Simon Willison 的 lethal trifecta 检查：本设计里处理不可信内容的组件没有私有数据外发通道，三要素不同时成立。"

## 失败模式与恢复（本题具体场景）

- **worker 在 EXTRACTING 中途 crash**：job 状态与 artifact 都是 durable 的——恢复 = 按 artifact DAG 找最深合法节点续跑；stage 是纯函数（同输入同配置同 id），重跑幂等，不会产生重复副作用。
- **重复上传**：content_hash 命中 → 返回已有 file_id/job（省钱且防止同一份工资单算两次收入）；用户确实要重处理（模型已升级）→ 显式 `force_reprocess`，新 job 复用 parse artifact。
- **OCR 垃圾输入**：质量门打回重传；勉强处理的低质量件全部走人审路由，且质量分数进 trace 供归因（是模型差还是件差）。
- **webhook 重复/乱序**：outbox at-least-once + event_id 去重 + "poke 然后 GET 拉权威状态"——完整答案在 [A4](A4_insurance_claims_agent.md) 深挖 1。
- **LLM API 故障/限流**：队列天然削峰（异步 SLO 是分钟级）；backoff + jitter + circuit breaker（[../../01_core/05_reliability.md](../../01_core/05_reliability.md)）；降级路径：performance path 不可用时不静默降到 light path 出低质结果，而是排队等待或改道人审——错误比延迟贵。
- **修正数据被污染（reviewer 错改）**：修正带 reviewer id/理由；抽样二次复核，一致率低的 reviewer 的修正不进回归集；per-customer slice 防一个客户的怪癖污染全局（Extend 卡追问 2，[../../06_company_briefs.md](../../06_company_briefs.md)）。

## Trade-offs 三条（主动说）

1. **异步分钟级 SLO 换正确性预算**：不做实时同步返回，换来质量门、invariants、targeted re-extract 和人审都放得进流程。信号：出现真实时场景（柜台当面办理）再为该场景单做同步 fast path。
2. **自动化率 vs 错误代价**：冷启动把阈值压低（人审率 30–40%），用修正数据把 calibration 和回归集喂厚，再沿 operating curve 移动工作点。这是运营决策不是一次性架构决策。
3. **v1 不做 per-tenant 微调**：先用 frontier + few-shot（把该租户的历史修正当 few-shot 候选）；信号：某文档类型量大且 F1 平台期低于目标，再上蒸馏/微调小模型（同时省成本，[../../03_gaps/cost_latency.md](../../03_gaps/cost_latency.md) 分级路由）。

## 现实参照（只引本地已有链接）

- Extend 产品术语与机制：parse/split/classify/extract/validate/review、`NEEDS_REVIEW` + correction 回流 API、双模式模型路由——见 [../../06_company_briefs.md](../../06_company_briefs.md) Extend 卡与 [Extend Docs](https://docs.extend.ai/)、[官方 JD](https://www.ycombinator.com/companies/extend)。
- 写操作幂等与状态-事件原子化：[Stripe idempotency](https://stripe.com/blog/idempotency)、[transactional outbox](https://microservices.io/patterns/data/transactional-outbox.html)（[../../01_core/05_reliability.md](../../01_core/05_reliability.md)）。
- 注入攻防评测与结构化隔离：[AgentDojo](https://arxiv.org/abs/2406.13352)、[CaMeL](https://arxiv.org/abs/2503.18813)、[lethal trifecta](https://simonwillison.net/2025/Jun/16/the-lethal-trifecta/)（[../../01_core/06_eval_security.md](../../01_core/06_eval_security.md)）。
- Judge 校准（自由文本字段比对时）：[MT-Bench/LLM-as-judge](https://arxiv.org/abs/2306.05685)；eval 词汇栈：[Anthropic evals blog](https://www.anthropic.com/engineering/demystifying-evals-for-ai-agents)。

> 一句话收尾（Extend 卡高分句）：低置信自动转人工、人工修正经 correction API 回流成回归 eval 和训练数据——这才叫 self-correcting system。
