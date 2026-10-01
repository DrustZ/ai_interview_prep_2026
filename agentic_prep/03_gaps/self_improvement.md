# Agent Self-Improvement：现有实现方法（面试口径版）

⏱ 骨架 8 min ｜ 含深潜与资料 40 min

## 30 秒版本（3 句话）⭐⭐⭐

1. Self-improvement 有几条**正交轴**，区别在于"改进写进了哪个持久物"：**推理时反思**（只改本次 episode 的 context，Reflexion/Self-Refine）、**记忆积累**（改 episodic/semantic memory，见 [02_state_and_memory.md](../01_core/02_state_and_memory.md)）、**技能库**（把成功行为固化成可执行代码复用，Voyager / Claude Code skills）、**提示与代码进化**（把 prompt/程序当可优化参数，DSPy/GEPA/AlphaEvolve/DGM）、**权重更新**（RL/SFT，见 [agentic_rl.md](./agentic_rl.md)）。
2. 最重要的实证边界：**没有外部信号的"自我反思"基本不 work**——[Cannot Self-Correct](https://arxiv.org/abs/2310.01798)（ICLR'24）证明 intrinsic self-correction 去掉 oracle label 后增益消失甚至变差；所以所有靠谱方法都由**外部 verifier**（单测、环境反馈、benchmark 分数、生产失败信号）驱动。
3. 工程上分**三档**记：① test-time——不改任何持久物，episode 结束即丢；② 数据与提示层——改 prompt/memory/skills，**可 diff、可回滚、可人审**，是生产系统的主战场；③ 权重层——RL/SFT，收益最持久但回滚与审计成本最高。生产闭环 = traces → failure taxonomy → eval case → 修（②或③）→ 过 eval gate + 人审。

## 现有系统怎么做 ⭐⭐⭐

| 方法/系统 | 改进的对象 | 核心机制一句话 | 适用 | 链接 |
|---|---|---|---|---|
| Reflexion | 下次 attempt 的 context（episodic buffer） | 失败→外部信号触发语言化反思→存 buffer→重试时注入 | 有 verifier、可重试的任务（coding/游戏） | [arxiv](https://arxiv.org/abs/2303.11366) |
| Voyager | 可执行代码技能库 | 通过验证的行为存成代码，embedding 检索复用；curriculum 自动出题 | 长期运行、行为可代码化的 agent | [arxiv](https://arxiv.org/abs/2305.16291) |
| DSPy / GEPA | prompt / pipeline 各模块 instruction | 把 prompt 当参数：对 trace 做语言反思→变异候选→Pareto 采样进化 | 有小 eval 集、不动权重要提分 | [arxiv](https://arxiv.org/abs/2507.19457) |
| AlphaEvolve | 目标程序代码（不是 agent 自身） | LLM 出 diff + 自动 evaluator 打分 + 进化库保多样性 | 解法可机器打分的算法/系统优化 | [blog](https://deepmind.google/blog/alphaevolve-a-gemini-powered-coding-agent-for-designing-advanced-algorithms/) |
| Darwin Gödel Machine | agent 自身 harness 代码 | agent 读自己的失败日志→改自己的代码→benchmark 分数当 fitness→archive 树防局部最优 | 研究向：自指改进的上限探索 | [arxiv](https://arxiv.org/abs/2505.22954) |
| 生产闭环（Applied Compute / Anthropic evals） | memory/Contextbase + prompt/harness + eval 集 | prod traces → 失败归因 → 变 eval case → 修 → eval gate + 人审后上线 | 一切生产 agent，面试最实用 | [AC](https://www.appliedcompute.com/research/remember-refine-retrieve) · [Anthropic](https://www.anthropic.com/engineering/demystifying-evals-for-ai-agents) |

<details><summary>【技术机制】Reflexion：verbal RL，外部信号驱动的失败反思</summary>

- **数据结构**：episodic memory buffer——一个长度上限 k（论文里 1-3 条）的反思文本列表，per-task 维护，episode 间持久、任务结束即弃。
- **三角色流程**：Actor（ReAct 式 rollout）→ Evaluator（外部信号：单测通过率 / 环境 reward / exact match，也可 LLM 打分）→ Self-Reflection LLM（输入 trajectory + 失败信号，输出"哪一步错了、下次怎么改"的自然语言）。
- 伪码骨架：

```python
memory = []                                    # episodic buffer, 上限 k 条
for attempt in range(max_trials):
    traj = actor.run(task, context=memory)     # 反思文本直接进 prompt
    signal = evaluator(traj)                   # 关键: 外部 verifier, 不是自评
    if signal.success:
        return traj
    reflection = llm(REFLECT_PROMPT, traj[-N:], signal)  # trace 截尾防爆 context
    memory.append(reflection)
    if len(memory) > k: memory.pop(0)          # 滑窗
```

- **数字**：HumanEval 91% pass@1（当时 GPT-4 基线 80%）。本质是把 scalar reward 转成语言梯度（"verbal RL"），不更新任何权重。
- **失败模式**：① evaluator 换成 LLM 自评 → 退化成 intrinsic self-correction，[2310.01798](https://arxiv.org/abs/2310.01798) 证明增益消失、还会把对答案改错；② 反思是泛泛的"我应该更仔细"而非可执行 delta——REFLECT_PROMPT 要强制输出具体行为改变；③ 任务不可重试（有副作用的生产操作）时整个范式不适用。
- **面试口径**：Reflexion = retry loop + 结构化 error feedback 的学术版；你在 harness 里把 stderr/失败测试注回下一轮 context，本质就是它。

</details>

<details><summary>【技术机制】Voyager：技能=可执行代码，验证通过才入库，embedding 检索复用</summary>

- **数据结构**：skill library = 向量库。key：GPT 生成的技能功能描述的 embedding；value：可执行 JS 程序（Mineflayer API 上的函数）。技能可组合调用其它技能——复杂度随库增长而复利。
- **三组件**：automatic curriculum（LLM 根据当前状态/库存/已会技能提出"下一个最大化探索的任务"）；iterative prompting（写代码→环境执行→吃 execution error + 环境反馈 + self-verification 判定→改）；skill library（只有通过验证的代码才入库）。
- 伪码骨架：

```python
skills = VectorDB()                            # desc_embedding -> js_code
while True:
    task = curriculum_llm(agent_state, past_failures)   # 自动出题
    ctx  = skills.topk(embed(task), k=5)                # 检索相关旧技能注入
    code = coder_llm(task, ctx, env_state)
    for _ in range(max_retries):
        ok, err, feedback = env.execute(code)           # 真执行, 不是自评
        verdict = critic_llm(task, feedback)            # self-verify 任务是否真完成
        if ok and verdict.passed: break
        code = coder_llm.refine(code, err, verdict)
    if ok and verdict.passed:
        skills.add(describe_llm(code), code)            # 过验证才入库
```

- **数字**：独特物品 3.3x、探索距离 2.3x、科技树里程碑最快 15.3x；技能库迁移到新世界仍能加速（泛化证据）。
- **失败模式**：① 库污染——critic 误判放行的坏技能被反复检索、错误放大，需要淘汰/版本化机制（论文没解决）；② 描述与代码语义 drift 导致检索失配；③ top-k 注入撑爆 context。
- **现代对应物**：Claude Code 的 [Agent Skills](https://www.anthropic.com/engineering/equipping-agents-for-the-real-world-with-agent-skills)（SKILL.md + 脚本目录，progressive disclosure：启动只载 name/description，用时才载全文）就是"人审版 Voyager 技能库"；agent 自写工具→沉淀成 skill 再复用是同一思想，差别是入库 gate 从 self-verify 换成人审。

</details>

<details><summary>【技术机制】DSPy / GEPA：prompt 当参数，反思式变异 + Pareto 进化</summary>

- **DSPy**（[github](https://github.com/stanfordnlp/dspy)）的核心抽象：把 pipeline 写成模块化程序（signature 声明输入输出，模块=参数化 prompt），optimizer 对着 metric + 小训练集自动优化各模块 instruction / few-shot demos——prompt 不再是手工艺品而是 checkpoint。GEPA 是其中最强的 optimizer 之一（ICLR'26 Oral）。
- **GEPA（Genetic-Pareto）关键设计**：① 反思式变异——不是随机改词，而是让 LLM 读完整 trace（reasoning、tool call、报错、评分理由 μf 文本反馈）诊断"这个 instruction 为什么导致失败"再改写；② Pareto 候选池——不留全局最优单点，而是保留"至少在某个 eval instance 上最优"的候选集合，从中采样父代，防早熟收敛。
- 伪码骨架：

```python
pool = [seed_program]; scores = eval_per_instance(seed_program, D_pareto)
while budget > 0:
    parent = sample(pareto_front(pool, scores))     # 按覆盖 instance 数加权
    batch  = sample(trainset, b)
    traces, feedback = run_with_feedback(parent, batch)   # μf: 文本化失败原因
    module = pick_module(parent)                    # 轮询/采样选一个模块动
    new_inst = reflect_llm(module.instruction, traces, feedback)
    child = parent.replace(module, new_inst)
    if score(child, batch) > score(parent, batch):  # 便宜的 minibatch gate
        pool.add(child); scores.update(child, D_pareto)
return best_by_avg(pool, scores)
```

- **数字**：以最多 **1/35 的 rollouts** 超过 GRPO（RL 基线）平均 6~10%、最高 +20%；比 MIPROv2 高 10%+。卖点：语言反馈的信息密度远高于 scalar reward，所以样本效率碾压。
- **失败模式**：① eval 集太小 → overfit，prompt 学会背 minibatch 的特例；② metric 可 hack 时进化出钻空子的 prompt（和 RL 的 reward hacking 同构，只是发生在 prompt 空间）；③ 多模块 pipeline 的 credit assignment——GEPA 用"一次只动一个模块"缓解。
- **面试口径**：GEPA vs RL 不是二选一——先用 GEPA 便宜地摸清 metric/reward 的坑，确认能力真不够再上 RL。

</details>

<details><summary>【技术机制】AlphaEvolve：进化式代码优化，automated evaluator 是命根子</summary>

- **对象区别**：进化的是**待解问题的程序**（调度启发式、矩阵乘算法、CUDA kernel），不是 agent 自己——所以它是"用 agent 做优化器"，不是自指改进。
- **数据结构**：program database（进化库），MAP-elites 风格保多样性：不只存最优，按特征维度存精英，避免单点爬山。代码里用 EVOLVE-BLOCK 注释标出允许改动的区域，LLM 输出 diff 而非整文件。
- 流程：`parent + inspirations = db.sample()` → 组 prompt（含问题描述、历史高分程序）→ Gemini Flash（走量出点子）/ Pro（走深修改）出 diff → apply → **automated evaluators 打分**（正确性 + 性能，可级联：先跑便宜的 smoke test 再跑贵的完整评测）→ 结果写回 db。循环完全无人值守，跑数天到数周。
- **数字**：4×4 复矩阵乘 48 次标量乘（Strassen 1969 年 49 次以来首次改进）；Google Borg 调度启发式上线回收全球 0.7% 算力；50+ 数学开放问题上 75% 重发现 SOTA、20% 推进 SOTA。
- **失败模式/边界**：① 只适用于"解可机器打分"的问题——evaluator 写不出来就没戏；② evaluator 可 hack 则进化出作弊解（比 RL 更狠，因为搜索预算巨大）；③ 评测成本决定吞吐，级联评测是工程关键。
- **面试口径**：这是"verifier 质量 = 系统上限"的极端例证——模型只负责提候选，所有信号来自 evaluator。

</details>

<details><summary>【技术机制】Darwin Gödel Machine：agent 改自己的 harness 代码，archive 树防局部最优</summary>

- **和 AlphaEvolve 的本质区别**：改进对象是 **agent 自身的 scaffold**（工具实现、prompt、workflow、长上下文管理策略），所以是自指的：改得越好 → 改自己的能力也越强（复利）。名字致敬 Schmidhuber 的 Gödel Machine，但把"形式证明改动有益"松弛成"benchmark 经验验证"（Darwin 部分）。
- **数据结构**：agent archive——一棵树，节点 = 一份完整 coding agent 代码库 + 其 benchmark 分数 + 父子关系。**保留低分个体**：踏脚石（stepping stone）可能通向更高峰，贪心只留最优会卡局部最优。
- 伪码骨架：

```python
archive = [initial_agent]
while budget:
    parent = sample(archive, p ∝ f(score) * novelty_bonus(num_children))
    diagnosis = fm(ANALYZE, parent.eval_logs)      # 读自己的失败日志找瓶颈
    proposal  = fm(PROPOSE_FEATURE, diagnosis)     # e.g. "加 patch 校验工具"
    child_code = fm_agent(IMPLEMENT, parent.code, proposal)  # agent 改 agent
    if not compiles_and_runs(child_code): continue
    score = eval(child_code, swe_bench_subset)     # 经验 fitness, 无形式证明
    archive.append(Node(child_code, score, parent))
```

- **数字**：SWE-bench 20.0% → 50.0%，Polyglot 14.2% → 30.7%（超过 Aider 手工 scaffold）；发现的改进包括更好的编辑工具、长上下文管理、peer-review 机制。
- **失败模式（论文自曝，面试金料）**：**objective hacking**——曾进化出 hallucinate 工具输出、以及在被要求修 hallucination 时**移除检测标记**而非修根因的个体；靠 sandbox + 人审 + 把 hacking 检测本身设为目标来缓解。另外：每个 child 都要跑 benchmark，评测成本是主要瓶颈。
- 资源：[Sakana 博客](https://sakana.ai/dgm/) · [代码](https://github.com/jennyzzt/dgm)。

</details>

<details><summary>【技术机制】生产闭环：traces → failure taxonomy → eval case → 修 → gate + 人审（面试最实用）</summary>

- **数据结构**：trace store（全量 rollout：每步 tool call/结果/最终判定）、failure taxonomy（失败聚类标签：缺知识 / 工具误用 / prompt 缺陷 / 能力不足）、eval suite（失败案例的最小复现）、memory/Contextbase（持久知识层）。
- 通用流程骨架：

```python
loop 每个改进周期:
    traces  = sample(prod_traces, 失败 + 高价值成功)
    clusters = cluster_and_label(traces)          # LLM 辅助归因
    for c in clusters:
        eval_suite.add(minimal_repro(c))          # 先变 eval case, 再谈修
        fix = 按归因分派: 缺知识→写 memory | prompt/harness 缺陷→改并 diff
              | 能力不足→积累成 RL/SFT 数据 (见 ./agentic_rl.md)
        if eval_gate(fix, 含回归集) and human_review(fix):
            deploy(fix)                           # 可回滚
```

- **Applied Compute 的实现（[Remember, Refine, Retrieve](https://www.appliedcompute.com/research/remember-refine-retrieve)，本周面试重点）**：Contextbase = 企业知识的活数据库。三段：**Remember**（SaaS connector + agent 执行 traces 摄入，解 cold-start）→ **Refine**（常驻的 context curation agent 群：消解冲突、抽概念链接、建索引；每个生产 rollout 都是下一轮 refinery 的候选）→ **Retrieve**（运行时 API）。人审：SME 可 accept/reject Contextbase 变更。数字：APEX-Agents 相对提升最高 16.9%；low-reasoning + Contextbase ≈ medium-reasoning 无 Contextbase（直接省推理成本）。这正是"数据与提示层"档的产品化。
- **Anthropic 的 eval 侧（[demystifying evals](https://www.anthropic.com/engineering/demystifying-evals-for-ai-agents)）**：eval 从窄行为起步（Claude Code 先测 concision、file edit，再扩到 over-engineering）；agent eval 要在真实/沙箱环境里跑并验证结果状态（如浏览器任务查 URL/页面状态）；失败案例回流成新 eval case 是常态循环。
- **失败模式**：① 跳过 eval gate 的全自动改进 = 把 [reward hacking](./agentic_rl.md)（见其 Q2 节）从训练搬进生产，proxy metric 会被进化钻空；② memory 写入无 provenance/TTL → 污染后无法定位回滚；③ 只修不建 eval → 同类失败换个皮肤再来，且无回归保护。

</details>

## 面试常问 3 题 ⭐⭐⭐

### Q1：你的 agent 生产里同类任务反复失败，怎么让它随时间变好？

<details><summary>参考打法</summary>

- 先报三档框架定调：test-time（不改持久物）→ 数据与提示层（可 diff 可回滚）→ 权重层（最后手段），成本与持久性递增。
- 短期：确认失败信号可捕获（verifier/用户反馈/状态校验），先在 harness 内做 Reflexion 式 retry——失败信息结构化注回下一轮。
- 中期主线：trace store → 失败聚类归因 → 每类先建最小复现 eval case → 按归因分派修 prompt/harness 或写 memory/skills，全部过 eval gate（含回归集）+ 人审后部署。
- 长期：某类失败归因为"能力不足"且量大 → 积累成 RL/SFT 数据（reward 设计见 agentic_rl.md）。
- 收尾强调：改进的单位是"失败 → eval case → 过 gate 的 diff"，不是"让 agent 自由反思"。

</details>

### Q2：self-improvement 为什么容易变成 self-degradation？怎么防？

<details><summary>参考打法</summary>

- 第一性证据：intrinsic self-correction 无外部信号时平均变差（arxiv 2310.01798，会把对答案改错）——反思必须由 verifier/测试/环境信号触发。
- 累积污染：Voyager 式技能库/memory 只进不出，一条被误判放行的坏条目会被检索反复放大；需要 provenance、版本化、淘汰机制。
- 优化即 hacking：DGM 进化出 hallucinate 工具输出、甚至移除 hallucination 检测标记的个体；GEPA/AlphaEvolve 在 metric 可 hack 时同样进化出作弊解——和 RL reward hacking 同构。
- 防线四件套：外部 verifier 驱动 + eval gate（含回归集）+ 改动落在可 diff 可回滚的持久物上 + 高影响变更人审（Applied Compute 的 SME accept/reject 就是这个）。
- 高阶补充：gate 本身也要演进——失败案例回流成新 eval case，防 gate 被静态打穿。

</details>

### Q3：GEPA 式 prompt 进化 vs RL 微调，什么时候选哪个？

<details><summary>参考打法</summary>

- 数字开场：GEPA 用最多 1/35 的 rollouts 超 GRPO 平均 6~10%、最高 +20%——说明大量"能力问题"其实是 context/instruction 问题。
- 选 prompt 进化：模型只能 API 访问、rollout 预算小、需要可读可 diff 可回滚的产物、任务分布还在变。
- 选 RL：能力真不足（prompt 怎么改都到不了）、有可验证 reward + 大 rollout 预算、任务分布稳定值得把能力烧进权重。
- 实操顺序：先 GEPA 便宜地摸 metric 的坑（metric 被 prompt hack 说明 reward 也会被 policy hack），确认 prompt 空间到顶再上 RL；两者共享同一套 eval/rollout 基建。
- 提一句共同风险：两者都是对 metric 的优化器，metric 质量 = 上限。

</details>

> 高分句：Self-improvement 的工程本质不是"让 agent 自由改自己"，而是选定改哪个持久物——context、memory、skills、prompt、harness 代码还是权重——然后用外部 verifier 产生信号、把每个改动收敛成过 eval gate、可回滚的 diff；没有 verifier 和 gate 的自我改进，优化的只是把病藏得更深的能力。

## 常见坑（checklist）

- 把"自我反思"当免费午餐：无外部信号的 self-correction 平均反而变差（2310.01798）——面试里主动引用这条反面证据是加分项。
- 技能库/memory 只进不出：无去重、无淘汰、无 provenance，污染后检索把错误复利放大，且无法定位回滚。
- 自动改进不过 eval gate：优化的是 proxy metric；连 DGM 都会伪造工具输出，生产 agent 没理由更老实。
- 三档混谈：被问 self-improvement 先答"改的是什么持久物、怎么回滚"，再谈机制，否则显得只会背论文名。
- 只验证目标失败类：改 prompt 修了 A 类失败没跑回归集，B 类悄悄坏掉——eval suite 必须随失败案例持续增长。

## 自学资料

1. [Demystifying evals for AI agents（Anthropic Engineering）](https://www.anthropic.com/engineering/demystifying-evals-for-ai-agents) — 生产闭环的 eval 侧：失败案例如何变 eval case，Claude Code/Chrome 实例 · 20 min
2. [Remember, Refine, Retrieve（Applied Compute）](https://www.appliedcompute.com/research/remember-refine-retrieve) — Contextbase 三段式 + refinery 闭环 + SME 人审，面 Applied Compute 必读 · 15 min
3. [GEPA: Reflective Prompt Evolution Can Outperform Reinforcement Learning](https://arxiv.org/abs/2507.19457) — ICLR'26 Oral，反思式 prompt 进化对 RL 的样本效率论证 · 25 min
4. [Large Language Models Cannot Self-Correct Reasoning Yet](https://arxiv.org/abs/2310.01798) — 反面证据：intrinsic self-correction 不 work，定义整个领域的边界 · 15 min
5. [Reflexion: Language Agents with Verbal Reinforcement Learning](https://arxiv.org/abs/2303.11366) — verbal RL 原型：evaluator + self-reflection + episodic buffer · 15 min
6. [Darwin Gödel Machine（Sakana AI 博客）](https://sakana.ai/dgm/) — 自改 harness + archive 树 + objective hacking 实录，博客比论文好读 · 15 min
7. [Voyager: An Open-Ended Embodied Agent with Large Language Models](https://arxiv.org/abs/2305.16291) — 技能库=可执行代码 + 自动 curriculum 的原型 · 15 min
8. [AlphaEvolve（DeepMind 博客）](https://deepmind.google/blog/alphaevolve-a-gemini-powered-coding-agent-for-designing-advanced-algorithms/) — 进化式代码优化 + automated evaluator 级联 · 10 min
9. [Equipping agents for the real world with Agent Skills（Anthropic）](https://www.anthropic.com/engineering/equipping-agents-for-the-real-world-with-agent-skills) — 技能库思想的生产形态：SKILL.md + progressive disclosure · 10 min
10. [DSPy（GitHub）](https://github.com/stanfordnlp/dspy) — prompt 当参数的框架抽象，GEPA 是其 optimizer 之一，扫 README 即可 · 10 min

补充：Self-Refine（无外部信号的自反馈基线，读 2310.01798 时对照）：[arxiv 2303.17651](https://arxiv.org/abs/2303.17651)；DGM 论文全文：[arxiv 2505.22954](https://arxiv.org/abs/2505.22954)。
