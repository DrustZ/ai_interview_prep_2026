# B 类 · 泛化 Agent 设计题

⏱ 约 6 分钟读完（可见部分） ｜ 面试前只看 ⭐⭐⭐ 部分

不绑定单一产品场景的 agent 架构题：loop/memory/multi-agent/eval 平台。组件语言见 [../01_core/](../01_core/README.md)，答题节奏见 [../02_playbook.md](../02_playbook.md)。

### [B1] ⭐⭐⭐ Anthropic：Design an agentic AI system that autonomously adapts to new tasks<a id="b1"></a>
- 来源: Exponent 题库标注 Anthropic（ML 岗，报告数少） ｜ 置信度: ⚠️ ｜ 公司/轮次: Anthropic · ML 岗 SD · 2026-01
- 考察点: agent loop、tool 接口、短/长期 memory、终止条件、沙箱护栏、行为评估
<details><summary>题面 + 参考打法 + 高频追问</summary>

**题面**："Design an agentic AI system that can autonomously adapt to new tasks."——新任务可能需要新工具、新领域规则、多步执行；不重训基础模型。

**参考打法**：
- typed TaskSpec 固化目标/约束/grader/budget——先把"适应成功"定义成可执行的东西
- 适应机制 = tool registry 发现 + few-shot exemplar 检索 + episodic memory，**不默认在线改权重**
- orchestrator 状态机控制 step/retry/approval/termination（max-steps + 成本预算）
- 工具执行前 guardrails：allowlist、dry-run、schema 校验；结构见 [../01_core/01_loop_and_tools.md](../01_core/01_loop_and_tools.md) + [../01_core/05_reliability.md](../01_core/05_reliability.md)
- eval：离线 held-out tasks + LLM-judge 人工校准 + shadow/canary；失败 trace 回流成新 eval

**高频追问**：memory 写错怎么撤销？ ｜ 新工具如何不破坏旧任务？ ｜ 何时需要多 agent、如何证明值得？

完整 rubric: [../../agentic/data/questions.json](../../agentic/data/questions.json) → `q-anthropic-adaptive-agent`

</details>

→ **完整解答：[solutions/B1_adaptive_agent.md](solutions/B1_adaptive_agent.md)**

### [B2] ⭐⭐⭐ 设计 ChatGPT 跨会话 memory 功能（Humans& 对口）<a id="b2"></a>
- 来源: igotanoffer 收录 + field guide 转引 + buildml 追问链 ｜ 置信度: ✅ ｜ 公司/轮次: generic（**Humans& 对口**，故升 ⭐）· AI SD · 2025–2026
- 考察点: 分层记忆、写入/遗忘策略、检索注入与 context 预算、隐私控制
<details><summary>题面 + 参考打法 + 高频追问</summary>

**题面**："Design ChatGPT's cross-conversation memory feature."

**参考打法**：
- 分层：working（当前 context）/ episodic（历史会话摘要）/ long-term semantic（持久用户事实/偏好）——详见 [../01_core/02_state_and_memory.md](../01_core/02_state_and_memory.md)
- 写入策略：显式"记住 X" vs 隐式抽取；去重与冲突合并（新事实 supersede 旧事实而非覆盖）
- 检索注入：embedding 检索 + 相关性阈值 + token 预算，不挤爆 context window
- 遗忘：过期、用户纠正、tombstone 清派生索引
- 隐私：可查看/删除、敏感信息不入库；eval：记忆命中对回答质量的 A/B

**高频追问**（buildml）：How would you design memory retrieval for an agent without overwhelming the context window? ｜ 用户偏好变了旧记忆怎么办？

</details>

→ **完整解答：[solutions/B2_chatgpt_memory.md](solutions/B2_chatgpt_memory.md)**

### [B3] ⭐⭐⭐ 🧪 Humans&：多人 + 多 Agent 的 Shared Workspace<a id="b3"></a>
- 来源: 按 Humans& 官方方向（long-horizon/multi-agent/memory/user understanding）推导（v1） ｜ 置信度: 🧪 ｜ 公司/轮次: Humans& 定向练习 · 60min design
- 考察点: 协作数据模型、authority/冲突、编排、memory 边界
<details><summary>题面 + 参考打法 + 高频追问</summary>

**题面**：设计项目 room：多个用户与 research/coding/calendar agents 共享目标和 artifacts，可并行委派、评论、合并、撤销。系统需知道谁有 authority，避免 agent 用过时计划覆盖人类决定。

**参考打法**：room event log 为事实源（derived views 可重建）→ Goal/Task/Artifact/Decision 均带 owner/version/provenance → orchestrator 分派 typed tasks，worker 只写 proposal/artifact branch → merge 需 verifier + authority check（人类 decision > agent suggestion）→ context builder 按角色和任务选事件摘要，禁止跨 room memory。

**高频追问**：两个 agent 同时改一个文档？ ｜ 如何解释某 agent 为何获得任务？ ｜ 如何评估团队而非单 agent 贡献？

完整 rubric: [../../agentic/data/questions.json](../../agentic/data/questions.json) → `q-humans-shared-workspace`（姊妹题 `q-humans-group-memory`：共识/分歧/遗忘）

</details>

→ **完整解答：[solutions/B3_shared_workspace.md](solutions/B3_shared_workspace.md)**

### [B4] ⭐⭐⭐ 🧪 Hark：Computer-use Agent Sandbox 与 Tool Harness<a id="b4"></a>
- 来源: 按 Hark 官方方向（CUA、RL post-training、sandbox）推导（v1） ｜ 置信度: 🧪 ｜ 公司/轮次: Hark 定向练习 · 60min coding-design
- 考察点: sandbox 边界、action/state 语义、审批/安全、恢复
<details><summary>题面 + 参考打法 + 高频追问</summary>

**题面**：设计并写核心接口：computer-use agent 根据 screenshot/DOM observation 产生 click/type/navigate action，在隔离浏览器中完成任务。限制 domain/下载/clipboard/credential；发消息、付款、删除属高风险。支持 timeout、用户接管、checkpoint 恢复。

**参考打法**：Observation/Action 用 typed envelope + page_version + monotonic step → browser/container 每 run 隔离，network/domain/file policy 在**执行层**强制 → 模型只产生 proposal，action validator 检查 target/risk/staleness/budget → 高风险动作展示 exact effect 后审批 + operation key 防重复 → checkpoint 只存可恢复业务状态，重开后重新观察 re-plan。环境/harness 语言见 [../01_core/03_harness_env_swe.md](../01_core/03_harness_env_swe.md)。

**高频追问**：网页内容诱导 agent 上传 secret 怎么防（间接注入）？ ｜ click 成功但 observation timeout？ ｜ 视觉模型看不到 disabled state？

完整 rubric: [../../agentic/data/questions.json](../../agentic/data/questions.json) → `q-hark-computer-use-sandbox`（姊妹题 `q-hark-posttraining-harness`：CUA post-training/eval，对齐 Hark JD 的 GRPO/SWE-bench 关键词）

</details>

→ **完整解答：[solutions/B4_computer_use_sandbox.md](solutions/B4_computer_use_sandbox.md)**

### [B5] ⭐⭐⭐ 🧪 Applied Compute：Enterprise Agent Eval Harness 与 Reward Hacking<a id="b5"></a>
- 来源: 按 Applied Compute 官方方向（custom harness/graders/traces/reward hacking detection）推导（v1） ｜ 置信度: 🧪 ｜ 公司/轮次: Applied Compute 定向练习 · 60min design
- 考察点: eval validity、leakage 隔离、grader 设计、统计与发布
<details><summary>题面 + 参考打法 + 高频追问</summary>

**题面**：为企业 legal agent 设计训练/发布 eval harness。任务来自真实 workflow，agent 可查文档和起草内容。需防 data leakage、grader gaming、环境污染，并比较新 checkpoint 与 production model。

**参考打法**：production taxonomy 分层抽样，按客户/时间隔离 held-out → immutable EvalTask 固定 environment snapshot + policy → outcome/policy/process 三类 grader 分开 → 隐藏 canary facts + adversarial tasks + grader ensemble 抓 gaming → paired trials、多 seed、slice CI；shadow→canary 逐步发布。配套 lab：`../../agentic/labs/05_eval_harness`。

**高频追问**：线上指标变好、离线变差？ ｜ LLM judge 与被测模型同源的风险？ ｜ 失败 trace 变训练信号又不污染 test？

完整 rubric: [../../agentic/data/questions.json](../../agentic/data/questions.json) → `q-applied-agent-eval`（姊妹题 `q-applied-improvement-loop`：trace→eval→improvement 闭环）

</details>

→ **完整解答：[solutions/B5_eval_harness.md](solutions/B5_eval_harness.md)**

### [B6] ⭐⭐⭐ Eval 平台设计题族：50 个 agent workflow / 跨 benchmark harness / 反馈闭环<a id="b6"></a>
- 来源: agentswarms（称 Arize/Anthropic/Microsoft 在问）+ techinterview.org GDM RE 轨 + substack 反馈闭环题 ｜ 置信度: ⚠️（三源均非一手，但互相印证） ｜ 公司/轮次: generic Staff+ / GDM RE（**Applied Compute 对口**，故升 ⭐）· 2025–2026
- 考察点: trace 采集、指标分层、judge 校准、golden set 版本化、回归门禁、数据飞轮
<details><summary>题面 + 参考打法 + 高频追问</summary>

**三个题面**：(1) "Build an evaluation platform for a company running 50 different agent workflows"（Staff+）；(2) GDM RE 轨 Evaluation Infrastructure 60min：跨 benchmark 评测 harness，必须处理 test set contamination 和 reproducibility；(3) "Design a feedback loop to improve an AI writing tool over time"。

**参考打法**：
- 统一 trace/span 采集（每次 tool call/prompt/决策可回放）→ 指标分层：通用（成功率/延迟/成本/循环次数）+ per-workflow 业务指标
- LLM-as-judge 规模化 + 校准（人工对齐、漂移监控）；golden set 版本化、从生产 trace 采样回填
- 回归门禁：prompt/模型/工具变更必须过离线 eval 才能发布；在线监控 vs 离线评估分工
- contamination：n-gram/embedding 去污染；reproducibility：固定 seed+温度记录、并行调度与缓存
- 反馈闭环：隐式信号（编辑量/接受/undo）→ embedding 聚类失败模式 → 更新 prompt/reranker/训练集 → 人审管道产出 SFT 数据 → A/B 验证
- 主线笔记：[../01_core/06_eval_security.md](../01_core/06_eval_security.md)

**高频追问**：如何测试非确定性 agent？ ｜ judge 的失败模式？ ｜ 如何区分用户偏好差异 vs 真错误？

</details>

> 高分句：没有 eval harness，任何 prompt 或模型变更都是盲改——eval 是 agent 系统的 CI。

### [B7] ⭐⭐ 设计 agent 互相委派任务的多 agent 系统（+最重要的失败模式）<a id="b7"></a>
- 来源: agentswarms + buildml 双源重合（公司归属未验证） ｜ 置信度: ✅ ｜ 公司/轮次: generic Senior/Staff SD · 2025–2026
- 考察点: 编排拓扑、委派协议、错误级联、何时根本不该用多 agent
<details><summary>题面 + 参考打法 + 高频追问</summary>

**题面**："Design a multi-agent system where agents delegate tasks to each other." Staff 级追问："What's the failure mode that interviewers most want to hear you defend against?"——期望答**协调失败**：死循环互相委派、错误级联放大、上下文交接丢失、成本爆炸。

**参考打法**：
- 默认立场：多数场景单 agent + 好工具就够；上多 agent 前先证明赢过单 agent 基线
- orchestrator-worker 拓扑：lead 维护 task tree/coverage/budget，worker 独立 context 只回传 compressed artifact
- **编排逻辑放 orchestrator 代码里，不塞进 prompt**（高频失分点）
- 委派协议：typed TaskSpec + task_id 去重 + deadline；critic/verifier agent 只在高价值步骤上（值得成本时）
- 经济性素材：Anthropic multi-agent research 系统 = Opus orchestrator + 并行 Sonnet subagents，token 消耗 ≈ 普通 chat 15 倍
- 详见 [../01_core/04_multi_agent.md](../01_core/04_multi_agent.md)

**高频追问**：When should you actually use a multi-agent system? ｜ critic agent 何时值得？ ｜ 交接时 context 丢失怎么测？

</details>

### [B8] ⭐⭐ Agent Tool-use System Design（企业级工具运行时）<a id="b8"></a>
- 来源: 1p3a ByteDance 题库公开摘要（v1 重建题面） ｜ 置信度: ⚠️ ｜ 公司/轮次: TikTok/ByteDance · SD 60min · 2025–2026
- 考察点: tool registry/discovery、执行运行时、租户权限、审批、trace、eval
<details><summary>题面 + 参考打法 + 高频追问</summary>

**题面**：设计企业级 agent tool-use system：数千工具由不同团队注册，模型按任务选择调用；支持 schema/version、发现与裁剪、并行只读调用、长时异步工具、租户权限、rate limit、错误回传、trace；高风险写操作必须审批。

**参考打法**：registry 存 ToolSpec/version/owner/risk/auth/SLO（不把全部 schema 塞 context）→ retriever 按 task+tenant+policy 过滤后只暴露少量工具 → executor 做 schema validation、credential injection、timeout、quota、result cap → 只并行 independent read-only calls，write 走 proposal/approval/operation key → TraceEvent 串联选择/调用/结果/cost，held-out task 测 selection/args/outcome/policy。

**高频追问**：工具 schema 升级如何不中断进行中 run？ ｜ 工具返回的 prompt injection？ ｜ 模型反复选错工具——是描述、retrieval 还是 model 的问题？

完整 rubric: [../../agentic/data/questions.json](../../agentic/data/questions.json) → `q-tiktok-agent-tool-system`

</details>

### [B9] ⭐ GDM Applied AI Engineer：ML System Design 轮官方考纲<a id="b9"></a>
- 来源: Blind（候选人转述 recruiter 官方大纲，verbatim） ｜ 置信度: ⚠️（单源但为官方大纲转述） ｜ 公司/轮次: GDM · Applied AI ML SD 轮 · 2025-09
- 考察点: 五大块：架构与 scale、RAG（factuality/grounding）、效率（量化/蒸馏）、agent 框架编排、eval 对齐
<details><summary>题面 + 参考打法 + 高频追问</summary>

**官方大纲（verbatim）**：(1) System Architecture: "high-level model choice, designing for scale"；(2) Retrieval (RAG): "factuality, grounding, implementation"；(3) Efficiency: "quantization, distillation, optimization"；(4) Agent Frameworks: "LangChain, LangGraph, etc."；(5) Evaluation: "aligning evals with problem formulation"。

**答题模板**：问题形式化 → 模型选型（API LLM vs 微调 vs 蒸馏）→ RAG 管线（chunking/embedding/hybrid/rerank/带引用生成）→ **eval 一等公民**（离线 eval 对齐任务、LLM-judge 人工校准、回归套件）→ 效率杠杆 → agent 编排与故障处理。另有 ML Debugging 轮，社区共识："bugs are stupid, not hard"——shape/broadcast 错、softmax 维度错、忘 zero_grad。

**高频追问**：vector DB 与 prompt orchestration 深度 ｜ 理论 ML vs 分布式系统比重

</details>

> 高分句：多数场景单 agent + 好工具就够；上 multi-agent 之前我要先证明它赢过单 agent 基线，并接受约 15 倍的 token 成本。
