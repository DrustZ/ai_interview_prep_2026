# [B1] Anthropic：能自主适应新任务的 Agentic AI System · 完整解答

⏱ 读完 12 min ｜ 建议先自己限时 60min 答一遍再看（盲看解答记不住）。题面原文见 [../B_general_design.md](../B_general_design.md#b1)，完整 rubric 见 [../../../agentic/data/questions.json](../../../agentic/data/questions.json) → `q-anthropic-adaptive-agent`。

## 题目还原

"Design an agentic AI system that can autonomously adapt to new tasks."——新任务可能需要新工具、新领域规则、多步执行；**不重训基础模型**。这题最容易答虚（"用 memory 让它学习"= 0 分）。真正在考：① 你能不能把 "adapt" 这个模糊词拆成**可实现的持久物变更**（改 context？改 skill/memory？改权重？）；② 适应闭环有没有**外部 verifier 和 eval gate**，还是放任 agent 自由反思（rubric：适应机制 20% + eval 10%，但需求定义和 control plane 各占 25%——地基不能省）；③ 新工具/新 memory 会不会破坏旧任务（回归保护）。

## 开场澄清（6 问 + 为什么问）

1. **新任务由谁定义？成功条件可执行吗？**→ 有没有 grader 决定整个系统能不能闭环。假设：任务带自然语言 goal，我会要求提交方给 acceptance checks（测试/终态断言），给不出的任务降级为 proposal-only。
2. **允许真实副作用吗？**→ 决定 sandbox/approval 强度。假设：读自由，写走 proposal→approval。
3. **"适应"的持久范围**：只在本 episode 内、per-tenant、还是全局共享？→ 决定 skill/memory 的 scope 与审核强度。假设：tenant 内自动、全局需人审。
4. **新工具从哪来**：人往 registry 接入，还是允许 agent 自己写工具？→ 决定 skill 入库 gate 设计。假设：两者都有。
5. **任务分布**：新任务多是旧任务的同域变体，还是完全新领域？→ 变体靠检索就够，新域要 cold-start 路径。
6. **SLO**：延迟/成本预算、人工介入容忍度？假设：分钟级任务、单 run 成本预算 $X、人审 SLA 小时级。

## 答案主线（按 [../../02_playbook.md](../../02_playbook.md) 时间盒走）

**开场 90 秒**（背这段）："adapt 不是让模型现场变聪明，而是**选定改哪个持久物**。我给三档：① test-time——任务分类 + 检索 skill/exemplar 注入 context + 失败反思重试，episode 结束即丢；② 提示与数据层——通过 verifier 的解法沉淀成 skill/memory/prompt diff，可 diff、可回滚、可人审，这是主战场；③ 权重层 RL/SFT——最后手段，只在某类失败量大且归因'能力不足'时启动。运行时是 classifier→检索→尝试→verifier 的闭环，适应面是 trace→失败归因→eval case→过 gate 的 diff。模型只处理模糊判断，权限、终止、入库都由确定性 control plane 管。"

**需求与成功（0–7min）**：goal predicate = `给定 TaskSpec(goal, acceptance_checks, budget)，在 max_steps 与 cost_budget 内使 acceptance_checks 全部通过，且零 policy 违规、零未审批写操作`。系统级北极星：**首次见到的任务家族的 pass rate 随周数上升**（这才是"适应"的可测定义）；护栏：旧任务家族回归 pass rate 不降、skill 库污染率、成本/任务。

**接口与数据模型（7–14min）**：

```text
TaskSpec(immutable): task_id, tenant_id, goal, constraints,
        acceptance_checks[], max_steps, deadline, cost_budget, tool_policy_version
ToolSpec: name, version, input/output JSON schema, risk(read|write|high),
        timeout, owner, eval_status(candidate|passed_regression)
Skill:  skill_id, description(+embedding), body(procedure 或可执行代码),
        provenance(source_run_ids), version, scope(tenant|global),
        status(candidate|committed|deprecated), usage_stats(hit/success)
MemoryRecord: content, kind(episodic_reflection|semantic_fact), source_run,
        confidence, scope, ttl, status(candidate|committed|tombstoned)
EvalTask/TrialResult: task + env snapshot + graders + seed → outcome/scores/cost
```

API：`POST /tasks`（创建 immutable TaskSpec）、`GET /tasks/{id}`、`POST /tasks/{id}/approvals`、`POST /tasks/{id}/cancel`、`GET /tasks/{id}/events?after=`（trace+streaming 共用一条 event log）。

**架构图（14–18min 画）**：

```text
Task source (human / API)
  │ POST /tasks (goal + acceptance_checks + budget)
  ▼
API + Auth ────────────► Policy / Approval
  │
  ▼
Run Controller 状态机 (plan→act→observe→verify; max_steps/cost enforce)
  │                └────► Event Store / Trace / Checkpoints
  ├── Task Classifier (small model: known_family | variant | novel)
  ├── Context Builder ◄── Tool Registry(按任务过滤) + Skill Library(top-k)
  │                       + Episodic Memory(同家族 exemplars/reflections)
  ├── Model Adapter (plan/act 走 frontier, classify/extract 走 small)
  ├── Tool Scheduler ──► Sandboxed Workers (allowlist + schema 校验 + dry-run)
  └── Verifier: 执行 acceptance_checks ──► pass → finalize + distill
                                          fail → Reflector → retry(bounded)
━━━━━━━━━ Adaptation plane（异步，不在请求路径上）━━━━━━━━━
  trace store → failure taxonomy → 最小复现 eval case
  → skill/memory/prompt candidates → eval gate(held-out + 回归集) → 人审 → commit(可回滚)
```

**主流程（18–28min，本题核心交付物）**——一条具体主线，别摊开泛谈：

1. **Task intake**：goal 固化成 immutable TaskSpec；没有可执行 acceptance_checks 的任务，要么让提交方补，要么标记 proposal-only（人当 verifier）。
2. **任务分类**：small model 把任务归到 `known_family / variant / novel`（分类依据：goal embedding 对历史任务家族的相似度 + 规则）。三个分支预算不同：known 走窄 workflow；variant 走检索增强 agent loop；novel 给更保守 budget、更早 escalate。分类结果写 trace——后面 eval 按分支分层看。
3. **检索层（适应的第①档）**：Tool registry 按任务过滤到 ≤10 个相关工具（描述给模型选择用，**权限在 executor 强制**，见 [../../01_core/01_loop_and_tools.md](../../01_core/01_loop_and_tools.md)）；Skill library 按 goal embedding 取 top-k 已 committed 的技能注入（Voyager 打法，见 [../../03_gaps/self_improvement.md](../../03_gaps/self_improvement.md) Voyager 节）；episodic memory 取同家族的成功 exemplar 和失败 reflection。三者共享 context 预算，skill/tool 定义放 immutable 前缀保 prompt cache 命中。
4. **尝试 + verifier**：controller 跑 plan→act→observe；每步 schema 校验、写操作走 proposal/approval；步末由 **Verifier 执行 acceptance_checks**——这是外部信号，不是模型自评。
5. **失败反思写回 memory**：fail → Reflector LLM 读 trajectory 尾部 + verifier 输出，产出"哪步错了、下次具体怎么改"的 reflection（Reflexion 打法，强制可执行 delta，禁止"我该更仔细"），append 进本任务 episodic buffer（上限 k=3 滑窗）→ bounded retry。**关键红线**：没有 verifier 信号就不触发反思——intrinsic self-correction 平均变差（[2310.01798](https://arxiv.org/abs/2310.01798)，主动引用这条是加分项）。
6. **沉淀（第②档）+ eval gate**：成功 run 由 distiller 提炼成 skill candidate（描述 + 步骤/代码 + provenance）；失败 trace 进 failure taxonomy 变最小复现 eval case。candidate **必须过 eval gate**：在 held-out 同家族任务上提分、在旧任务回归集上不降分，tenant scope 自动 commit、global scope 加人审。这就是"Voyager 的 self-verify 入库 gate 换成 eval gate + 人审"——Claude Code Agent Skills 的生产形态。
7. **第③档（说明何时启动）**：某 failure cluster 在 prompt/skill 层怎么改都不动、且量大分布稳 → 积累成 RL/SFT 数据（见 [../../03_gaps/agentic_rl.md](../../03_gaps/agentic_rl.md)）。默认不做，因为回滚与审计成本最高。

**可靠性（36–46min）**：过失败清单（见下节）。**Eval（46–54min）**：见深挖 3。**Trade-offs（54–60min）**：见末节。

## 深挖 3 处（题库高频追问）

**1）memory/skill 写错了怎么撤销？**——"我的写入模型是 candidate/committed 两层 + provenance 全链路。① 任何 run 产出的 reflection/fact/skill 先是 candidate，只在同 tenant 小流量可见；② 每条记录带 `source_run_ids`，发现污染时按 provenance 反查：tombstone 该记录 → 失效所有派生物（embedding 索引、被它组合调用的下游 skill 标 needs-review）→ 引用过它的后续 run 打标重跑抽查；③ 冲突不静默覆盖：新事实 supersede 旧事实留版本链；④ 防线前移——入库时就查重、查与已有记录的矛盾，并维护 false-memory eval：故意注入错误记忆，测系统会不会检索采信。Voyager 论文自己承认没解决库污染（critic 误判放行的坏技能被反复检索、错误复利放大），我的答案就是版本化 + provenance 撤销 + usage_stats 淘汰（命中率高但成功率低的 skill 自动降级）。"

**2）新工具如何不破坏旧任务？**——"三层。① **Registry 隔离**：TaskSpec 带 `tool_policy_version`，旧任务 pin 旧版本工具集，新工具默认不进旧任务的可见集——工具可见性是按任务过滤的，不是全局广播；② **上线 gate**：新工具接入 = 先跑旧任务家族回归 eval（新工具在场但预期不被选用，测它的描述会不会干扰模型选择——工具描述之间的 embedding 相似度过高就要求改写描述）+ 新任务家族的 held-out 提分验证；③ **发布**：shadow（新工具集并行跑、写操作只记录）→ canary 按 tenant 灰度 → 回归 pass rate 掉了自动 rollback 到旧 tool_policy_version。工具本身 versioned、schema 变更 = 新版本号，旧 run replay 不受影响。"

**3）何时需要多 agent、如何证明值得？**——"默认 single agent + workflow 分支，理由是 Anthropic 自己的 Building Effective Agents 结论：先用最简单的够用形态。升级 multi-agent 只在两个信号出现：① 单 context 装不下（多领域检索材料互相挤占预算），需要按子任务隔离 context；② 出现**独立可并行、各自有 verifier 的 artifact**（比如同时改三个互不依赖的模块）。证明方式是把它当 eval 问题：同一 held-out suite 上跑 single vs multi，报 pass rate、cost、latency、一致性——multi-agent 通常成本 3–5 倍，提分不显著就不上。上的话按 [../../01_core/04_multi_agent.md](../../01_core/04_multi_agent.md)：typed task queue、worker 独立 context、artifact handoff、verifier 聚合，不共享消息流。"

## 失败模式与恢复（本题具体场景）

- **verifier 造不出来**（"帮我写个更好的营销文案"）：拒绝进全自动闭环——降级为 proposal-only，人 accept/reject 即 verifier 信号，积累够了再校准 LLM judge 替代部分人力。绝不让 LLM 自评当 grader 闭环（2310.01798）。
- **novel 任务 cold start**：无相关 skill/exemplar → 通用 ReAct + 收紧 budget（更小 max_steps、更早 escalate）+ 全程 trace 重点采样；第一次成功即是第一条 skill candidate。
- **适应循环不终止**：retry 有上限（k 次 reflection），预算临界要求输出 partial artifact + 明确 incomplete，不伪装成功；重复 tool-call signature / 无进展检测提前熔断。
- **skill 库污染**：见深挖 1。补一条摄入面防线：skill 只从 **verifier 通过的 run** 提炼，工具输出中的指令性内容（prompt injection）在 distill 前过 sanitizer，global commit 必人审——否则注入内容会借 skill 库获得持久化和放大。
- **worker crash / timeout**：从 durable RunState + event log 找最后 committed transition，pending 写操作查外部 status 再决定，同 operation key 重试；标准答法见 [../../01_core/05_reliability.md](../../01_core/05_reliability.md)。
- **eval gate 被静态打穿**：gate 也要演进——线上失败持续回流成新 eval case，回归集只增不改；否则 candidate 会进化出过 gate 的皮（与 reward hacking 同构，DGM 连 hallucination 检测标记都会移除）。

## Trade-offs 三条（主动说）

1. **默认②档不上③档（权重）**：牺牲适应的持久度上限，换可 diff、可回滚、可人审——GEPA 用最多 1/35 的 rollouts 超 GRPO 平均 6–10%，说明大量"能力问题"其实是 context/instruction 问题。信号：某 failure cluster 在 prompt/skill 空间到顶且量大分布稳 → RL/SFT，两档共享同一套 eval 基建。
2. **skill 入库过 gate + 人审，牺牲适应速度防污染**：全自动入库（Voyager 原版）适应快但污染无回滚。分级折中：tenant candidate 自动、global commit 人审（Applied Compute 的 SME accept/reject 同款）。信号：人审队列积压且自动 gate 误放行率持续为零 → 放宽自动化范围。
3. **v1 不做 multi-agent、不做自动 curriculum**：先证明"检索 + 沉淀"闭环在真实任务分布上提分。信号：context 预算成为主要失败原因 → multi-agent；skill 库覆盖增长停滞 → 引入 curriculum 式主动探索（Voyager 的另一半）。

## 现实参照（只引本地已有链接）

- [Building Effective Agents](https://www.anthropic.com/engineering/building-effective-agents)（Anthropic，rubric 官方背景源）：workflow 优先、最简单够用形态的立场，本题的"默认 single agent"论据。
- [Voyager](https://arxiv.org/abs/2305.16291)：skill=可执行代码、过验证才入库、embedding 检索复用——本解主线的原型；其未解决的库污染是深挖 1 的靶子。
- [Reflexion](https://arxiv.org/abs/2303.11366) + [Cannot Self-Correct](https://arxiv.org/abs/2310.01798)：失败反思必须由外部 verifier 驱动的正反两面证据。
- [Agent Skills](https://www.anthropic.com/engineering/equipping-agents-for-the-real-world-with-agent-skills)（Anthropic）：SKILL.md + progressive disclosure，"人审版 Voyager 技能库"的生产形态。
- [Remember, Refine, Retrieve](https://www.appliedcompute.com/research/remember-refine-retrieve)（Applied Compute）：Contextbase 摄入→精炼→检索闭环 + SME 人审，②档的产品化实例。
- [Demystifying evals for AI agents](https://www.anthropic.com/engineering/demystifying-evals-for-ai-agents)（Anthropic）：失败案例回流成 eval case 的官方口径。
- [GEPA](https://arxiv.org/abs/2507.19457)：②档 vs ③档取舍的样本效率数字出处。

> 收尾高分句（可背）：这个系统里"适应"的单位不是一次聪明的反思，而是一个**过了 eval gate、可回滚的 diff**——写进 context、skill、memory 还是权重只是档位不同；没有 verifier 和 gate 的自我改进，优化的只是把病藏得更深的能力。
