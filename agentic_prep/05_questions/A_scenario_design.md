# A 类 · 具体应用场景设计题

⏱ 约 10 分钟读完（可见部分） ｜ 面试前只看 ⭐⭐⭐ 部分

按公司分组，组内按置信度排序。答题剧本见 [../02_playbook.md](../02_playbook.md)，通用架构组件见 [../01_core/](../01_core/README.md)。

## Sierra / Extend（7/15–本周）

### [A1] ⭐⭐⭐ Sierra take-home：虚构公司客服 agent（5 选 2 功能）+ onsite 演示<a id="a1"></a>
- 来源: Exponent 面经 2025-05 + gaijineer + norahq ｜ 置信度: ✅ ｜ 公司/轮次: Sierra · take-home 2–4h + onsite 60min 演示 · 2025–2026 持续
- 考察点: 裸写 OpenAI tool-calling loop（不套框架）、scope 取舍、metrics/observability、向面试官讲清架构决策
<details><summary>题面 + 参考打法 + 高频追问</summary>

**题面**：为一家虚构客户公司构建客服 AI agent。已报告场景：户外用品公司、高端音响设备公司。官方提供 OpenAI API key。从约 5 个候选功能（订单查询、退换货、产品推荐类）里**选 2 个实现**，并回答 observability / performance metrics 的追问（生产中看哪些指标、怎么建 dashboard）。Onsite 60 分钟演示 + deep dive："Why this architecture? Why this approach to tool calling?"，可能被要求现场扩展新需求或讨论 scale。同场还有 5–10 分钟自选技术主题讲解（有人选 RAG，追问 chunking/rerank/幻觉抑制）——预备 1–2 个自己最深的主题（可选 agentic RL 或 τ-bench 式评估），预演 8 分钟版本。

**参考打法**：
- 裸写 tool-calling loop（面经原话：build a simple agent without hiding behind a big framework）；结构参考 [../01_core/01_loop_and_tools.md](../01_core/01_loop_and_tools.md)
- 写操作（退款/改单）走 proposal→confirm→execute（幂等键），只读工具自动执行——边界讲法见 [../01_core/05_reliability.md](../01_core/05_reliability.md)
- 主动引 τ-bench pass^k（Sierra 自家论文，airline/retail 场景）谈一致性，见 [../04_benchmarks.md](../04_benchmarks.md)
- metrics 三层：resolution rate / escalation rate / policy 违规率 + token 成本与延迟
- 演示准备 success、missing info、policy denied 三条 scenario

**高频追问**：How would you extend this to handle new requirements or scale? ｜ 生产上怎么监控错误操作？ ｜ 为什么不用 LangChain？

</details>

→ **完整解答：[solutions/A1_customer_agent_takehome.md](solutions/A1_customer_agent_takehome.md)**

### [A2] ⭐⭐⭐ Sierra：为具体客户用例设计 agentic 系统（订阅取消）<a id="a2"></a>
- 来源: norahq guide 汇编（可能转自 Glassdoor） ｜ 置信度: ⚠️ ｜ 公司/轮次: Sierra · take-home 延伸/onsite 讨论 · 2025–2026
- 考察点: 客服 agent 端到端：对话状态、工具/API、策略护栏、升级人工、评估
<details><summary>题面 + 参考打法 + 高频追问</summary>

**题面**："Design an agentic system for a specific customer use case (for example, subscription cancellation)."——Sierra 产品核心场景（退订/挽留）。

**参考打法**：
- 对话与状态：识别意图→验证身份→policy 检查（合同期、退款资格）
- 工具层：查询订阅 API（只读自动）、取消 API（confirmation + 幂等）、优惠 offer API
- 护栏：敏感操作白名单、金额阈值升级人工、防 prompt injection（[../01_core/06_eval_security.md](../01_core/06_eval_security.md)）
- 挽留逻辑做成可配置 policy 而非硬编码 prompt——业务用户可改
- 评估：resolution/escalation/违规率 + pass^k 一致性；离线回放真实对话做回归

**高频追问**：模型升级后如何防 regression？ ｜ 多租户客户的 policy 如何配置化？ ｜ 如何离线回放做回归测试？

</details>

→ **完整解答：[solutions/A2_subscription_cancellation.md](solutions/A2_subscription_cancellation.md)**

### [A3] ⭐⭐⭐ 文档自动化管线：银行材料上传处理 / 医生账单自动报送<a id="a3"></a>
- 来源: igotanoffer《GenAI System Design Interview》+ field guide 转引 ｜ 置信度: ✅ ｜ 公司/轮次: generic（**Extend 对口**，故升 ⭐）· AI SD 轮 · 2025–2026
- 考察点: OCR/结构化抽取、验证+人审队列、异步管线、PII/HIPAA 合规、端到端准确率评估
<details><summary>题面 + 参考打法 + 高频追问</summary>

**题面**：两道真题：(1) "Design a system to process 10K user uploads/month (bank payslips, IDs, references)"；(2) "Design a system that lets doctors automatically send billing info to insurers based on patient notes"。

**参考打法**：
- 摄取：多格式 + OCR/版面解析，content hash 去重，job 异步状态机
- 抽取：LLM schema 约束输出（structured output），每步版本化 artifact
- 验证：规则校验 + domain invariants + 置信度 → 低置信度进人审队列（按 expected loss 排序）
- 隐私：PII redaction 在入库前；审计日志不复制敏感全文
- 评估：field/document/workflow 三层准确率 + 抽样审计；人工修正回流成回归用例

**高频追问**：新 schema 如何重跑旧文档？ ｜ webhook 重复/乱序？ ｜ 恶意 PDF 里的指令如何隔离？（间接注入）

与 [A4] 互为姊妹题——本题偏管线，A4 偏 agent 语义。

</details>

→ **完整解答：[solutions/A3_document_pipeline.md](solutions/A3_document_pipeline.md)**

### [A4] ⭐⭐⭐ 🧪 Extend：保险理赔文档 agent（split/classify/extract/validate + 人审）<a id="a4"></a>
- 来源: 按 Extend 产品方向推导（v1 题库） ｜ 置信度: 🧪 ｜ 公司/轮次: Extend 定向练习 · 60min design
- 考察点: 文档处理 DAG、低置信度人审、webhook 幂等、schema version 演进
<details><summary>题面 + 参考打法 + 高频追问</summary>

**题面**：设计保险理赔文档 agent：一个上传包可能含多份扫描件；先 split/classify，再按 schema extract，跨页校验金额，低置信度送人工。支持重复上传、异步 webhook 和 schema version。

**参考打法**：upload content hash 去重 → parse→split→classify→extract→validate DAG（每步版本化 artifact）→ schema validator + domain invariants（模型 confidence 只是信号之一）→ review queue 按 expected loss 排序，修正绑定 source span → eval 特别测 long arrays 和 missing pages。

**高频追问**：webhook 重复或乱序？ ｜ 新 schema 重跑旧文档？ ｜ 恶意 PDF 指令隔离？

完整 rubric: [../../agentic/data/questions.json](../../agentic/data/questions.json) → `q-extend-document-agent`（相邻题 `q-extend-permission-agent`：权限/注入版）

</details>

→ **完整解答：[solutions/A4_insurance_claims_agent.md](solutions/A4_insurance_claims_agent.md)**

> 高分句：文档 agent 的人审队列不按置信度排序，按 expected loss 排序——错一个金额字段和错一个备注字段的代价差两个数量级。

## Anthropic（7/22）

### [A5] ⭐⭐⭐ Anthropic 最高频 SD：LLM Inference Batch API（含 batchstring 变体与 100K RPS 变体）<a id="a5"></a>
- 来源: 1p3a 题库 Very High（16+ 讨论）+ Exponent 完整题面 + OfferEngineering 2026-07 ｜ 置信度: ✅ ｜ 公司/轮次: Anthropic · 50–55min 店面/onsite SD（含 Google Doc 书面形式）· 2025–2026-07 持续
- 考察点: batching 双触发、continuous batching/KV cache、响应路由、背压限流、GPU 容量与故障恢复
<details><summary>题面 + 参考打法 + 高频追问</summary>

**题面（Exponent 版原文）**："You have a single GPU that can process up to 100 inputs per batch. Users submit requests synchronously and wait for results. Design the system that receives inputs, batches them, processes them on the GPU, and returns responses to the correct users." **batchstring 变体**：给定固定后端 `batchstring(inputs: list[str]) -> list[str]`，每批 1–100 条、固定 ~100ms 延迟（与批大小无关）、每 GPU 一次一批；要求 1000+ RPS、P95<500ms、GPU 利用率 70–80%。**完整需求版**（2026-07）：+ 优先级、流式、重试/幂等、排队/背压/限流/按优先级丢弃、KV-cache 显存、突发流量、worker 崩溃安全重试、可观测性。

**参考打法**：
- 请求队列 + 双触发 batch 调度器（凑满 OR 超时 10–50ms）；correlation ID/future 把结果路由回等待的 HTTP handler
- 有界队列 + 429 背压；付费用户多队列加权调度
- 改进层：continuous batching（vLLM 式）、prefill/decode 分离；KV per-token bytes $= 2 \cdot n_{layers} \cdot n_{kv} \cdot d_{head} \cdot \text{dtype}$
- 多 GPU：least-loaded / 一致性哈希（sticky 命中 prefix cache）
- **100K RPS 变体**（"Handle 100,000 req/s for an LLM token-generation service"）：按 tokens/sec 而非 RPS 定容；评分标准=剥掉 AI 皮找核心 infra 问题 + 主动 failure-mode 分析
- 深挖：[../03_gaps/scaling.md](../03_gaps/scaling.md)、[../03_gaps/cost_latency.md](../03_gaps/cost_latency.md)

**高频追问**（原帖清单）：10K RPS 需要几块 GPU？ ｜ 新 GPU 启动 5 分钟怎么办（warm pool + 预测扩容）？ ｜ 一半 GPU 挂掉如何自动限流？ ｜ 500ms 里排队 vs 计算各占多少？ ｜ batch 中单条失败怎么办？ ｜ 重复请求要不要缓存？

</details>

→ **完整解答：[solutions/A5_batch_api.md](solutions/A5_batch_api.md)**

### [A6] ⭐⭐⭐ Anthropic：Prompt Playground 全栈设计<a id="a6"></a>
- 来源: 1p3a 题库 high（完整题解）+ hack2hire 变体（freq 9/10）+ 多个 onsite 报告 ｜ 置信度: ✅ ｜ 公司/轮次: Anthropic · onsite SD（**纯 Google Doc 书面讨论，不画图**）· 2026-04~06
- 考察点: 大文本编辑与存储、版本管理、异步 run+流式、LLM API 成本控制
<details><summary>题面 + 参考打法 + 高频追问</summary>

**题面**：设计类 OpenAI Playground / Anthropic Console 的 prompt 工程平台——写 prompt→迭代→运行→保存最佳版本。**不是 chatbot**：每次 Run 无会话记忆、one-shot；单用户项目（单写者简化版本管理）；prompt 可达 10MB/100K tokens；外部 LLM 慢但界面必须"感觉即时"；每次迭代持久化版本不丢好 prompt。

**参考打法**：
- **核心考点**（原帖标注）：10MB ≈ 250 万 token 远超模型上限——"可存储可编辑"与"可运行"必须分开讲
- 版本：append-only 版本链 + snapshot+diff（1000 次保存追问）；autosave draft vs committed version
- 内容：S3/content-addressed 放大文件，DB 放元数据；服务端 token 计数
- 运行：异步 run job + 流式 partial + 幂等键；run 历史关联 prompt-version+params+输出+成本/延迟
- 成本：估算给到高端模型 $450/天——相同 prompt 结果缓存；读写流量低不需分片，贵的是 LLM 调用
- 每个取舍说 "可以 X 或 Y，我选 X 因为…"；书面轮要练打字表达（[../02_playbook.md](../02_playbook.md)）

**高频追问**：10MB 文件怎么处理？ ｜ 1000 次保存的版本追踪？ ｜ 如何防 LLM API 花费失控？ ｜ 大文档怎么搜索？

</details>

→ **完整解答：[solutions/A6_prompt_playground.md](solutions/A6_prompt_playground.md)**

### [A7] ⭐⭐⭐ Design ChatGPT：多轮对话后端 + SSE token streaming<a id="a7"></a>
- 来源: hack2hire（Anthropic 6/10、OpenAI 9/10）+ hellointerview 官方 guide + 多面经交叉 ｜ 置信度: ✅ ｜ 公司/轮次: Anthropic/OpenAI/generic · onsite SD · 2026 持续
- 考察点: 会话持久化、context 组装 token 预算、GPU 推理调度、SSE 流式与断线恢复
<details><summary>题面 + 参考打法 + 高频追问</summary>

**题面**：设计 ChatGPT 类服务后端——多轮对话、持久化历史（数天后续聊携带上下文）、context assembly、GPU 集群推理分发、SSE token 流式返回。指标：TTFT ≤500ms p50 / 2s p95；200M+ DAU；GPU 稀缺。Out of scope（hellointerview 版）：消息编辑、多模态、custom GPTs。

**参考打法**：
- 主线：API gateway → conversation service（持久存储）→ context assembler（system prompt + 摘要历史 + 最近轮次，token 预算）→ continuous batching 推理调度 → SSE streamer（可恢复 event id）
- 流式快路径与持久化写路径分离；TTFT 预算拆解（排队/prefill/首 token）
- 四个 deep dive：token streaming、GPU 调度、公平资源分配（防重度用户垄断 + 付费优先）、长会话截断/摘要控成本
- SSE vs WebSocket、断线用 Last-Event-ID 续传：[../03_gaps/streaming.md](../03_gaps/streaming.md)

**高频追问**：safety guardrails 管线的延迟预算？ ｜ 多模型路由与灰度？ ｜ 会话摘要何时触发、存哪？

</details>

→ **完整解答：[solutions/A7_design_chatgpt.md](solutions/A7_design_chatgpt.md)**

### [A8] ⭐⭐⭐ Anthropic：500GB 模型权重分发到 100–1000 GPU worker<a id="a8"></a>
- 来源: 1p3a 题库 medium（完整题解，SD 五题 portal 成员） ｜ 置信度: ✅ ｜ 公司/轮次: Anthropic · 店面/onsite SD 55min · 至 2026-06
- 考察点: 带宽数学、链式 pipeline 分发、chunk 化、容错协调
<details><summary>题面 + 参考打法 + 高频追问</summary>

**题面**：把 500GB 模型权重分发到数据中心内 100–1000 台 GPU worker，总时间最短、容忍故障。约束：云端下载 10Gbps；每 worker 全双工 10Gbps。目标：100 台约 8 分钟、1–5% 故障率、支持增量更新与回滚。

**参考打法**：
- **要求当场算数学**：逐台串行 $N \cdot F/B$；树形广播上行带宽被 fan-out 均分 → $\sim \log_2 N \cdot F/B$；链式 pipeline chunk 化（收到即转发）$\approx F/B + (N-1) \cdot c/B \approx F/B$（chunk $c \ll F$）。$F/B = 500\text{GB}/1.25\text{GB/s} = 400s \approx 6.7$ 分钟——正好对上 8 分钟目标
- 中央 coordinator 定链序 + 追踪 chunk 位置；heartbeat 探活，节点挂了绕开重接链路
- chunk 大小权衡：太小协调开销大，太大流水线气泡大；SHA256 校验 chunk 与整文件
- 10K worker：分层（region → rack chain）或 BitTorrent 式 swarm

**高频追问**：为什么 pipeline 优于树形（数学证明）？ ｜ 链中间 worker 挂了？ ｜ 扩到 10,000 台还成立吗？

</details>

→ **完整解答：[solutions/A8_weights_distribution.md](solutions/A8_weights_distribution.md)**

> 高分句：Anthropic 的 SD 题都是"AI 皮、分布式系统骨"——先剥掉 AI 包装说出核心 infra 问题，再用 tokens/sec 而不是 RPS 做容量推理。

## OpenAI / generic（⭐⭐：迁移备用）

### [A9] ⭐⭐ Design Sora / GPU job scheduler（OpenAI 2026 最高频 SD）<a id="a9"></a>
- 来源: 1p3a Very High（19 帖，last asked 2026-06-29）+ hack2hire GPU Scheduling Platform（OpenAI 10/10）｜ 置信度: ✅ ｜ 公司/轮次: OpenAI · 电面+onsite SD 60min · 2026-04~07
- 考察点: durable orchestration on preemptible GPUs：状态机、lease/fencing、checkpoint 恢复、两阶段放置
<details><summary>题面 + 参考打法 + 高频追问</summary>

**题面**：为 Sora 式视频生成设计后端——提交 prompt+参数，服务接受任务、调度到外部 GPU 池、跟踪进度、返回视频。约束：每 worker 同时一个视频；GPU 池**可抢占**，worker 随时可能被终止。过来人共识："别被名字唬到，本质就是 job scheduler"。NFR：创建 P95<500ms、调度 P95<30s、进度新鲜度<5s、accepted job 零丢失、抢占损失<30s。容量：100K 视频/天、峰值 20 jobs/s、单视频 ~3min → ~3600 并发、~4000 warm worker。姊妹题（hack2hire）：共享训练/批处理 GPU 集群调度平台——优先级队列+抢占、两阶段放置（DB 预留→node agent ack→commit）、desired vs actual reconciliation loop。

**参考打法**：
- 异步 API：先 durable write 再返回 202+job_id（入库前返回成功=红牌 pitfall）
- PostgreSQL source of truth + Redis 队列（可从 DB 重建）+ 对象存储放 checkpoint/成品
- worker **pull** 调度 + heartbeat lease + fencing token；lease monitor 自动 requeue；幂等完成接口防 stale worker
- 队列按 priority_tier + model_version + gpu_type 分区；checkpoint 频率自适应
- Pitfalls：假设供应商发抢占预警（心跳丢失才可靠）、无 fencing、单一 FIFO 混用所有模型

**高频追问**：push vs pull（volatile worker 选 pull）？ ｜ 网络分区 split-brain？ ｜ gang scheduling / per-team 配额（DRF）？ ｜ 供应商容量骤降的 admission control 与 ETA？

</details>

### [A10] ⭐⭐ OpenAI：企业级 RAG 聊天机器人（类 Glean）<a id="a10"></a>
- 来源: 1p3a 完整题解 + Qbank 两条独立行（MLE/RE 轨）｜ 置信度: ✅ ｜ 公司/轮次: OpenAI · 60min onsite ML SD（2026 春取消后恢复）· 至 2026-03
- 考察点: 超越教程级 RAG：权限、多租户、评估/幻觉检测、多轮
<details><summary>题面 + 参考打法 + 高频追问</summary>

**题面**：设计企业内部搜索问答 RAG 机器人（类比 Glean）：检索公司数据 + LLM 生成带引用回答。要求：多用户/多租户、权限控制、数据安全、答案带来源、低延迟。

**参考打法**：
- 架构解耦 ingestion/retrieval/generation；设计 API + 聊天日志 schema
- 检索：semantic vs hybrid（BM25+dense）、cross-encoder rerank、事实型 vs 开放型问题分流
- **权限过滤在检索层做**（用户只能召回有权文档），不是 prompt 层
- 质量：强制 grounding + citation 追踪、no-hit 兜底拒答、量化指标（groundedness/citation correctness）
- 性能：embedding 与热门问题缓存、批处理；RAG 细节见 [../03_gaps/rag.md](../03_gaps/rag.md)
- **失分点**（原帖）：做成教程级、忽略多轮属性、不讲评估、不考虑百万文档增长、忽略隐私

**高频追问**：如何评估 RAG 质量与检测幻觉？ ｜ 文档更新与版本？ ｜ 多轮对话历史管理？

</details>

→ **完整解答：[solutions/A10_enterprise_rag.md](solutions/A10_enterprise_rag.md)**

### [A11] ⭐⭐ 企业知识库 conversational agent（含官方评分 rubric；多租户/10M 规模变体）<a id="a11"></a>
- 来源: PracHub 2026 GenAI SD 指南（recurring prompt + rubric）+ substack/field guide 多源 + agentswarms 变体 ｜ 置信度: ✅ ｜ 公司/轮次: generic GenAI loop · SD 轮 · 2025–2026
- 考察点: RAG 全链路 + 评分维度：framing、检索深度、成本意识、质量/安全、trade-off 主导权
<details><summary>题面 + 参考打法 + 高频追问</summary>

**题面**："Design a conversational AI agent for our enterprise knowledge base."（GenAI 面试循环 recurring prompt）。变体：cost-optimized / latency-optimized / accuracy-optimized 三种约束版本；**多租户变体**："multi-tenant RAG where each tenant's data is isolated"；**规模变体**："scale an AI search assistant for 10M+ articles"。

**参考打法**：
- 四阶段逐段讲 trade-off：摄取与 chunking（小 chunk 缺上下文/大 chunk 稀释语义）→ embedding（商用 vs BGE 成本）→ retrieve-then-rerank → 生成与流式编排
- **官方 rubric**：framing（点明概率性本质+澄清延迟/敏感度/规模）、retrieval depth、cost awareness（semantic caching、model routing）、quality/safety（evals、citations、guardrails、反馈回路）、trade-off leadership（主动挑明 precision-latency-cost 张力）
- 多租户：per-tenant namespace vs 共享索引+元数据过滤 vs 物理隔离；ACL 在检索层强制；防租户 A 文档注入影响租户 B
- 10M 规模：hybrid + 按主题 shard + 热点缓存 + precision@k 监控；换 embedding 模型的增量重建

**高频追问**：文档互相矛盾优先检索谁？ ｜ 用什么指标度量准确率？ ｜ embedding 换代如何避免全量重建？

</details>

→ **完整解答：[solutions/A10_enterprise_rag.md](solutions/A10_enterprise_rag.md)**（与 [A10] 共用同一份解答）

### [A12] ⭐⭐ OpenAI：Design the OpenAI Playground（全栈：wireframe + API + schema）<a id="a12"></a>
- 来源: Exponent guide（reported screen 题）+ 1p3a Qbank 两条（GPT-3 Playground、Design AI Chatbot System，元数据级）｜ 置信度: ✅ ｜ 公司/轮次: OpenAI · SD screen 60min · 2025-10~2026
- 考察点: LLM 产品全栈：前端 wireframe、API 层、thread/message history schema；10x–1000x scale 压测
<details><summary>题面 + 参考打法 + 高频追问</summary>

**题面**："Design the OpenAI Playground"——前端 wireframes + API layer + thread/message history 的 DB schema，**明确期望全栈**（recruiter 会预告）。同族 Qbank 题：GPT-3 Playground（tech-screen，标签 fullstack/streaming）、Design AI Chatbot System（SSE/WebSocket/api-integration）。

**参考打法**：
- 复用 [A6] Anthropic Prompt Playground 正文（题面几乎同构），OpenAI 版加：前端组件拆解 + REST endpoint 具体化 + 消息队列语义
- 面试官套路：先验证初始设计→"what if we 10x/100x/1000x scale?"——必须点名哪个组件先崩并重设计它
- **主动问清**：model-inference/ML-infra 层要设计还是当黑盒 API
- OpenAI SD 风格：product+infra 混合、中途抛新约束/twist、背模板会翻车

**高频追问**：1000x 后哪个组件先崩？ ｜ thread history 的分页与冷热分层？ ｜ 流式失败的前端体验？

</details>

### [A13] ⭐⭐ Design GitHub Copilot / Design Perplexity（实时 LLM 搜索）<a id="a13"></a>
- 来源: Colin Zhou 2025 面经总结 + field guide 转引 ｜ 置信度: ✅ ｜ 公司/轮次: generic · AI SD 轮 · 2025
- 考察点: 低延迟 LLM 产品：上下文构建、缓存、实时检索+引用、成本
<details><summary>题面 + 参考打法 + 高频追问</summary>

**题面**：(1) "Design an AI co-pilot like GitHub Copilot"；(2) "Design a Perplexity.ai / real-time LLM-powered search engine"。

**参考打法**：
- Copilot：补全延迟预算 ~200ms → 小模型 + FIM（fill-in-the-middle）；context = 当前文件 + 光标邻域 + repo 级检索；请求去抖与前缀缓存；北极星指标=接受率；代码隐私
- Perplexity：实时抓取/索引 + RAG + 逐句引用、查询改写、多源冲突处理；可引 ByteByteGo 拆解（日均 2 亿查询、Vespa 上的 RAG、微调 Sonar）
- 共同点：LLM 当黑盒后拼延迟、成本、检索质量——成本模型见 [../03_gaps/cost_latency.md](../03_gaps/cost_latency.md)

**高频追问**：接受率下降怎么归因（模型 vs context vs 触发时机）？ ｜ 引用与来源冲突怎么呈现？

</details>

### [A14] ⭐⭐ PromptLayer 官方题单：白板三题 + coding 三题 + take-home 三选一<a id="a14"></a>
- 来源: PromptLayer CEO 官方博客（自家面试题+rubric 全公开） ｜ 置信度: ✅（官方一手） ｜ 公司/轮次: PromptLayer · 白板/live coding/take-home · 2024–2025
- 考察点: 问题分解、多步 agent 流程、每组件 prompt 结构、错误处理；take-home 强制带 eval
<details><summary>题面 + 参考打法 + 高频追问</summary>

**白板三题**：(1) 分析客服工单并自动起草回复、复杂问题升级的 agent；(2) 多 agent 协作产出带引用研究报告；(3) 读代码、理解意图、建议改进的 agent。**公开 rubric 四条**：子任务分解清晰、agent 步骤间逻辑流、错误处理与边界、每组件 prompt 结构设计。

**Live coding 三题**（允许 ChatGPT、禁 Cursor——观察你怎么写 prompt）：batch LLM API 调用、debug embeddings 处理代码、清洗文本准备 fine-tuning。**Take-home 三选一**：CSV 客户数据→个性化 email campaign（含质量 eval 指标）；文档 Q&A + citation tracking（multi-hop）；Python code review agent（含 accuracy eval）。评分三条：能跑、有意义的 eval、能阐述设计理由。

**打法要点**：所有 take-home 都强制 eval——这是 2025 后 agent take-home 共同趋势，答任何 agent 设计题都主动给 eval 段落（[../01_core/06_eval_security.md](../01_core/06_eval_security.md)）。

</details>

### [A15] ⭐⭐ 客服 agent：日处理 10K 工单、响应 <2s<a id="a15"></a>
- 来源: agentswarms 聚合站（称 Stripe/Intercom/Klarna 在问，归属未验证） ｜ 置信度: ⚠️ ｜ 公司/轮次: generic senior SD · 2025–2026
- 考察点: 意图分流、模型分层、延迟/成本预算、HITL 升级、guardrails
<details><summary>题面 + 参考打法 + 高频追问</summary>

**题面**："Design a customer-support agent that handles 10,000 tickets/day with <2s response time."（Sierra 面试的 generic 版，与 [A1]/[A2] 互补）

**参考打法**：
- 前置意图分类分流：FAQ 直答 vs 需查库 vs 直升人工
- <2s → 模型分层（小模型路由 + 大模型兜底）、semantic cache、流式输出掩盖尾延迟
- RAG 知识库 + 工具调用（订单/退款 API，写操作 HITL 审批）
- 工具失败重试降级；per-ticket 成本核算；上线前 eval harness + 回归集
- 素材：Doctolib（有向图上的专门化 agents，日均 17K 消息）、Intercom/Klarna 公开案例

**高频追问**：How would you implement a human-in-the-loop approval step for high-risk agent actions?

</details>

### [A16] ⭐⭐ 受限域三题族：银行零幻觉 chatbot / AI 法律合同 / 医院语音助手<a id="a16"></a>
- 来源: bhavishyapandit9 substack（7 deep-cut AI SD 题） ｜ 置信度: ⚠️ ｜ 公司/轮次: generic · AI SD 轮 · 2025–2026
- 考察点: 生成边界收紧：LLM 只做界面层、模板+槽位受控组装、多约束排优先级
<details><summary>题面 + 参考打法 + 高频追问</summary>

**三题面**：(1) "Build a chatbot for a bank that must not hallucinate"；(2) "AI tool to generate legal contracts from prompts"；(3) "Voice assistant for hospital staff"。

**共同答案模式——把自由生成降级为受控组装**：
- 银行：LLM 只当界面/改写层不当知识源；账户事实路由到结构化 API；回答带来源+审计日志；置信度不够拒答；合规 disclaimer
- 法律：预审核条款模板库 + 可填槽位（当事人/金额/期限）；LLM 只做意图解析与 paraphrase；条款带 metadata（辖区/版本）；输出前强制用户批准 + 版本控制
- 医院：边缘 ASR 降延迟、医学术语微调、HIPAA 加密/匿名化、高风险操作前确认、ASR 失败回退键入——考互相冲突约束（延迟 vs 准确 vs 隐私）的排序

**高频追问**：API 数据不完整的边界？ ｜ 新辖区/新法规的治理流程？ ｜ 发音相近术语消歧？

</details>

> 高分句：企业 RAG 的权限过滤必须发生在检索层——靠 prompt 叮嘱模型"别看无权文档"在架构上不成立。
