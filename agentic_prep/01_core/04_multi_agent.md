# 04 · Workflow / Single / Multi-agent 与 Orchestration

⏱ 骨架 5 min ｜ 含深潜与资料 35 min ｜ 面试前只看 ⭐⭐⭐ 部分

## 1. 三种形态怎么选 ⭐

| 形态 | 适用条件 | 特征 |
|---|---|---|
| 固定 workflow | 步骤已知、合规严格、变体有限（如 `parse → validate → approve → execute`） | 可预测、便宜、好测；用了 LLM 不等于 agent |
| Single agent | 路径不能预先穷举，但同一个 context 足以完成 | 一个 loop、一个 state owner，debug 最简单；**默认起点** |
| Multi-agent | 下面四条同时成立 | 需要 ownership、handoff、budget、conflict resolution、cancellation、verifier |

Multi-agent 的四个前提（同时成立才用）：

1. 子任务可独立并行，信息增益明显。
2. 每个 worker 需要独立 context，避免主 context 爆炸。
3. 聚合/验证标准明确。
4. 单 agent baseline 已暴露 latency、coverage 或 specialization 瓶颈。

- 多 agent 不是「多开几个模型」：常见失败来自任务描述不完整、agent 对彼此需求建模错误、结果未验证，而不是模型智力不足。
- 为什么不默认多 agent：成本、协调、冲突和 eval 面积增加；只有可并行独立任务才有正收益。

> 高分句：默认 single agent；multi-agent 是用协调成本换并行收益，先让单 agent baseline 暴露瓶颈再升级。

## 2. Orchestration：fan-out 到 fan-in ⭐

- orchestrator 持有唯一全局 plan 和 budget。
- worker 之间用 artifact handoff，TaskSpec 定义见 [./03_harness_env_swe.md](./03_harness_env_swe.md)。
- fan-in 时先结构化合并，再让模型总结。
- verifier 专门检查 coverage、冲突、unsupported claims 和 acceptance。

> 高分句：按可独立验证的 artifact 分工，而不是让多个 agent 重复思考再投票。

## 3. 动态停止 ⭐

取消 worker 的条件（任一满足）：

- [ ] 预期信息增益低
- [ ] 重复已有 source
- [ ] deadline 不够
- [ ] budget 达阈值

取消是正常控制，不是失败。cancel 的状态机语义见 [./02_state_and_memory.md](./02_state_and_memory.md)。

> 高分句：取消是 orchestrator 的正常控制手段——一个不会主动停 worker 的编排器等于没有 budget。

## 4. 现有系统怎么做 ⭐⭐

正反方两篇博客是 2025-06 前后脚发的天然对照组：Anthropic 说 multi-agent 让 research 提升 90%，Cognition 说别建 multi-agent。两边其实不矛盾——**读多写少、天然可分的任务（检索）适合并行；强上下文耦合的任务（写代码）不适合**。面试时把这条边界讲清楚就是高分答案。

| 系统/方法 | 核心机制一句话 | 适用场景 | 链接 |
|---|---|---|---|
| Anthropic Research（orchestrator-worker） | lead agent 按 effort 分级 spawn 并行 subagent，结果 fan-in 后综合 + 独立 citation agent；~15x token | 广度检索、open-ended research | [blog](https://www.anthropic.com/engineering/multi-agent-research-system) |
| Cognition（反方：single-thread + compressor） | 不并行执行；共享完整 trace，超长任务用专门模型压缩历史为关键决策 | 写代码等强上下文耦合任务 | [blog](https://cognition.com/blog/dont-build-multi-agents) |
| Claude Code subagents / Task tool | 子 agent 全新 context window + 自己的 system prompt/tool 子集，父 agent 只收最终文本 | 防主对话膨胀的只读调研 | [docs](https://code.claude.com/docs/en/sub-agents) |
| OpenAI Agents SDK：handoffs | handoff 暴露为 `transfer_to_<agent>` 工具，调用后 active agent 切换、历史（可裁剪）随之转移 | triage/路由型，专家直接答复用户 | [docs](https://openai.github.io/openai-agents-python/handoffs/) |
| OpenAI Agents SDK：agents-as-tools | manager 保持控制，`Agent.as_tool()` 调子 agent，子 agent 不接管对话 | 一个 agent 拥有最终答案、合并多专家输出 | [docs](https://openai.github.io/openai-agents-python/multi_agent/) |
| MAST 失败分类（实证） | 3 类 14 种失败模式 + 各自比例；结论：失败多来自系统设计而非模型智力 | 诊断/评审任何 MAS 设计 | [arXiv](https://arxiv.org/abs/2503.13657) |
| A2A 协议 | Agent Card（`/.well-known/agent.json`）+ JSON-RPC 任务生命周期，跨 vendor agent 互操作标准（Google 发起，现属 Linux Foundation） | 组织间/框架间 agent 调用 | [repo](https://github.com/a2aproject/A2A) |

<details>
<summary>Anthropic multi-agent research system —— 技术机制</summary>

**架构**：orchestrator-worker。lead agent（Opus 4）分析 query、定策略、spawn subagent（Sonnet 4）；subagent 并行检索，各自在独立 context 里工作，把压缩后的发现回传；lead 综合后交给独立的 citation agent 补引用。该组合在内部 research eval 上比单 Opus 4 好 **90.2%**。

**任务分发**：prompt 里明确教 lead 怎么写 task description，四要素缺一不可（缺了就出现重复劳动或漏覆盖）：

1. clear objective（这个 subagent 要回答什么）
2. output format（回传什么结构）
3. tool & source guidance（用哪些工具、优先哪些来源）
4. task boundaries（不要做什么）

——这就是 03 文件里 `TaskSpec` 的 prompt 版本。

**effort scaling 规则**（也写在 prompt 里，防止 over-spawn）：

- 简单事实查询：1 个 agent，3-10 次 tool call
- 直接对比：2-4 个 subagent，各 10-15 次 call
- 复杂研究：10+ subagent，明确分工

**两层并行**：(a) lead 一次 spawn 3-5 个 subagent；(b) 每个 subagent 内部并行调 3+ 个工具。合计把 research 时间砍最多 90%。

**控制流骨架**：

```python
async def research(query):
    plan = await lead.plan(query)              # 决定 effort tier：1 / 2-4 / 10+
    specs = [TaskSpec(goal=..., output_format=...,
                      tool_guidance=..., boundaries=...)
             for s in plan.subtasks]
    results = await asyncio.gather(*[run_subagent(s) for s in specs])
    while not lead.satisfied(results):         # fan-in 后 lead 可追加 spawn（迭代加深）
        extra = lead.follow_up_specs(results)
        results += await asyncio.gather(*[run_subagent(s) for s in extra])
    draft = await lead.synthesize(results)
    return await citation_agent.cite(draft)    # 引用归属单独一个 agent 做
```

**token 经济学**：agent ≈ 4x chat token，multi-agent ≈ **15x** chat token；BrowseComp 上 token 用量单变量就解释 80% 的性能方差——所以只有任务价值足够高才值得。这个数字是面试里"为什么不默认 multi-agent"的最硬证据。

**Eval 方法**：不判中间步骤，判 end-state（是否到达正确终态，允许不同路径）；用 LLM judge 打 rubric 分 + 人工看 trace。

**失败模式（他们自己踩的坑）**：早期版本对简单 query spawn 50 个 subagent；subagent 之间重复搜索；agent 拿到足够结果还继续搜（不会停）；同步 fan-in 意味着 lead 必须等最慢的 subagent。另外生产上必须支持 resume from where it failed，而不是整个 research 重跑。
</details>

<details>
<summary>Cognition「Don't Build Multi-Agents」—— 技术机制（反方）</summary>

**两条原则**（Walden Yan, 2025-06-12）：

1. **Share context**：共享完整 agent trace，不是只共享单条消息。subagent 看不到主对话的完整决策过程，就会误解任务。
2. **Actions carry implicit decisions**：每个 action 都隐含决策，并行 agent 各自做的隐含决策会冲突。

**Flappy Bird 例子**：把"做一个 Flappy Bird clone"拆给两个并行 subagent——一个做了 Super Mario 风格背景，另一个做了视觉风格完全不搭的鸟。两个 agent 都没错，但彼此的隐含决策（美术风格）不可见，fan-in 时无法合并。这正是 MAST 里的 inter-agent misalignment。

**推荐架构**：

- 架构 1：**single-threaded linear agent**——一条线程从头跑到尾，context 完整连续，最可靠。
- 架构 2：长任务加 **dedicated compressor model**——专门（可微调的）模型把历史压缩成关键决策与事件，换取更长 horizon：

```python
history = []
for step in agent_loop:
    if tokens(history) > THRESHOLD:
        history = [compressor.compress(history)]   # 输出：关键决策、事件、待办
    action = model(system_prompt, history, latest_obs)
    history.append((action, execute(action)))
```

**对例外的承认**：文章点名 Claude Code 和 Devin 的做法——subagent 只用于**回答问题**（只读调研），不用于并行**实现**。即读操作可并行，写操作必须单线程。

**失败模式（如果无视这两条原则）**：并行 worker 隐含决策冲突、fan-in 不可合并；compressor 压掉了后面步骤需要的细节（压缩是有损的，压什么本身是个 hard problem，Cognition 为此微调了专门模型）。

**面试用法**：这篇不是说 multi-agent 永远错，而是给出判据——**当子任务间存在隐含决策耦合时，context 完整性 > 并行收益**。
</details>

<details>
<summary>Claude Code subagents / Task tool —— 技术机制</summary>

**语义**：父 agent 调 `Task(description, prompt, subagent_type)`，harness spawn 一个子 agent：

```python
def task_tool(description, prompt, subagent_type):
    cfg = subagent_registry[subagent_type]      # .claude/agents/*.md 定义
    sub = Agent(system=cfg.system_prompt,
                tools=cfg.tool_subset,          # 可以比父 agent 更窄（安全边界）
                context=[])                     # 全新 context，看不到父对话
    final_text = sub.run(prompt)                # 中间 reasoning / tool calls 不回传
    return final_text                           # 父 agent 只拿到这个字符串
```

**关键设计决定**：

- **独立 context window**：子 agent 烧掉几万 token 搜索/读文件，父 context 只增加最终摘要——这是 context 管理手段，不只是并行手段。
- **结果只回最终文本**：没有共享内存、没有消息通道。含义：prompt 必须自包含（子 agent 无法追问），且要在 prompt 里约定输出格式，否则 fan-in 时没法结构化合并。
- **custom subagent 定义**：`.claude/agents/*.md`，YAML frontmatter 写 `name` / `description`（父 agent 靠它决定何时委派）/ `tools` / `model`，正文是 system prompt。
- 与 Cognition 原则一致：并行 Task 用于只读调研（多路搜索、代码考古），**写代码不并行分派**，避免隐含决策冲突。

**失败模式**：prompt 少给了约束 → 子 agent 自由发挥、结果不可用（specification 失败）；父 agent 把需要主对话上下文的任务丢给子 agent → 子 agent 缺关键信息还不能追问；把子 agent 结果当可信事实直接用而不验证。
</details>

<details>
<summary>OpenAI Agents SDK：handoffs vs agents-as-tools —— 技术机制</summary>

SDK 先分两大类：**LLM orchestration**（模型自己决定调谁，灵活）vs **code orchestration**（代码决定流转，速度/成本/行为更可预测）。LLM orchestration 内部再分两种模式：

**模式 1：handoffs（去中心化，转移控制权）**

```python
from agents import Agent, handoff

billing = Agent(name="Billing", instructions="...")
refund  = Agent(name="Refund",  instructions="...")

triage = Agent(
    name="Triage",
    instructions="判断问题类型并转给对应专家",
    handoffs=[billing,
              handoff(refund, input_filter=strip_tool_calls)],
)
```

- 实现上 handoff 就是一个自动生成的工具：`transfer_to_billing`。LLM 调用它 → runner 把 **active agent** 切换成目标 agent，对话历史随之转移，之后由新 agent 直接面对用户。
- `input_filter` 决定下家看到多少历史（如剥掉 tool calls）；handoff 还可带结构化参数（如 `reason`），可运行时动态启用/禁用。
- 适用：客服 triage 这类"专家应该直接接管对话"的场景。

**模式 2：agents-as-tools（中心化，orchestrator 模式）**

- manager agent 用 `specialist.as_tool(tool_name=..., tool_description=...)` 把子 agent 包装成普通工具调用；子 agent 跑完把结果返回 manager，**不接管对话**。
- 适用：一个 agent 拥有最终答案、需要合并多个专家输出。等价于 Anthropic 的 orchestrator-worker，只是粒度更小。

**对比记忆点**：handoff 转移的是 *control + conversation*；as-tool 转移的只是 *一次调用*。

**失败模式**：handoff 链上 `input_filter` 裁太狠 → 下家缺上下文（Cognition 警告的场景）；两个 agent 互相 handoff 形成 ping-pong 循环（要加 max-turns/防环）；handoff 太多时 triage agent 路由准确率下降（工具选择混乱，需要收窄 handoff 列表）。
</details>

<details>
<summary>MAST 失败分类（arXiv 2503.13657）—— 技术机制与实证数字</summary>

**方法**：UC Berkeley 等，分析 7 个 MAS 框架（MetaGPT、ChatDev、AG2、AppWorld 等）150+ 条 trace 归纳出 taxonomy，再扩到 1600+ 条标注数据；6 名专家标注，Cohen's κ=0.88；并配套 LLM-as-a-Judge pipeline 做规模化标注。

**3 类 14 种失败模式（括号内为占比）**：

| 类别 | 失败模式 |
|---|---|
| **FC1 Specification（41.8%）**——任务/角色没定义清楚 | FM-1.1 违反任务规格 (11.0%)；FM-1.2 违反角色规格 (0.5%)；FM-1.3 步骤重复 (17.1%)；FM-1.4 对话历史丢失 (3.3%)；FM-1.5 不知道终止条件 (9.8%) |
| **FC2 Inter-agent misalignment（36.9%）**——agent 间协调失败 | FM-2.1 对话意外重置 (2.3%)；FM-2.2 该问不问 (11.7%)；FM-2.3 任务跑偏 (7.2%)；FM-2.4 信息扣留 (1.7%)；FM-2.5 无视他人输入 (0.2%)；FM-2.6 推理与行动不一致 (14.0%) |
| **FC3 Task verification（21.3%）**——结果没验证 | FM-3.1 过早终止 (7.8%)；FM-3.2 无/不完整验证 (6.8%)；FM-3.3 验证本身错误 (6.7%) |

**关键结论（面试直接引用）**：

- 近 **80%** 的失败（FC1+FC2）发生在验证之前——是系统设计与协调问题，不是"模型不够聪明"。换更强模型解决不了 specification 失败。
- 单个失败模式里最大的三个：步骤重复 17.1%、推理-行动不一致 14.0%、该问不问 11.7%——全部可以用工程手段缓解（幂等检查、行动前 assert、强制 clarification 轮）。
- 论文验证过两类干预：改进 prompt/拓扑（cheap fix）有帮助但不够，说明需要结构性修复（verifier、协议约束），呼应本文第 2 节的 verifier 设计。

**用法**：设计 review 时把 14 条当 checklist 扫一遍；写 postmortem 时用 FM 编号归类失败。
</details>

<details>
<summary>A2A 协议 —— 一段话机制</summary>

Google 发起、现归 Linux Foundation 的 agent 互操作标准。机制：每个 agent 在 `/.well-known/agent.json` 挂 **Agent Card**（JSON：能力/skills、endpoint、认证方式、输入输出 mode），客户端 agent 以此发现并选择远端 agent；通信是 HTTP 上的 JSON-RPC，围绕 **task 生命周期**（submitted → working → input-required → completed/failed/canceled），支持同步请求、SSE 流式和 push notification 三种交互。与 MCP 的分工一句话：**MCP 连 agent↔tool，A2A 连 agent↔agent（双方都是 opaque 的对等体，不暴露内部实现）**。目前更多是标准化尝试而非事实标准，面试提一句定位即可。
</details>

<details>
<summary>自己实现 orchestrator：TaskSpec / fan-out–fan-in / 冲突裁决 / budget —— 工程要点</summary>

（完整可运行版本见 v1 lab04；`TaskSpec` 字段定义见 [./03_harness_env_swe.md](./03_harness_env_swe.md) §4。）

**1. 任务分发数据结构**：`TaskSpec` 必须 frozen（不可变，防 worker 篡改自己的验收标准），核心字段 `goal / inputs / constraints / expected_artifact / acceptance_checks / deadline / budget`。检验标准：不看主对话的 worker 能独立执行并被 `acceptance_checks` 验收。

**2. fan-out 与同步点**：

```python
async def fan_out(specs, max_workers, deadline, budget):
    sem = asyncio.Semaphore(max_workers)              # 有界并发
    async def run(spec):
        async with sem:
            if budget.remaining() < spec.budget or deadline.too_close():
                return WorkerResult.cancelled(spec.task_id)   # 取消是正常控制
            return await worker(spec)                 # worker 只见自己的 spec
    results = await asyncio.gather(*(run(s) for s in specs),
                                   return_exceptions=True)    # 单个异常不拖垮整批
    return [r if isinstance(r, WorkerResult)
            else WorkerResult.failed(spec.task_id, err=r)
            for spec, r in zip(specs, results)]       # typed result，保持输入顺序
```

同步点三选一：**barrier**（等全部，Anthropic research 的 fan-in，简单但受最慢者拖累）、**as_completed 流式 fan-in**（先到先聚合，可提前判断"信息增益够了"并 cancel 其余）、**quorum**（N 取 K 即继续，用于冗余采样）。

**3. 聚合与冲突裁决**：核心原则——**worker 只产 proposal，不直接写共享状态**；由单一 reducer/verifier 提交：

```python
def fan_in(results, state):
    proposals = group_by_key(fact for r in ok(results) for fact in r.facts)
    for key, vals in proposals.items():
        if conflicting(vals):
            state.flag_conflict(key, vals)   # 不写入；交 verifier 裁决或降级人工
        else:
            state.cas_write(key, vals[0],    # compare-and-set：版本过期则写失败
                            expected_version=state.version(key))
```

裁决顺序：先按 provenance/置信度过滤 → 真冲突（同 key 不同值且证据都够）不要静默取多数，标记冲突让 verifier 或人裁决。verifier 检查四件事：coverage（每个 spec 有对应 artifact）、冲突、unsupported claims（结论有无证据）、acceptance_checks。

**4. budget 控制**：三个层级——全局 budget（orchestrator 持有唯一预算，spawn 前扣减）、per-worker budget（写进 TaskSpec，worker 自己 loop 内检查）、deadline 传播（父 deadline 减去预估聚合时间后下发）。没有 budget 的 fan-out 就是 Anthropic 踩过的坑：50 个 subagent 查一个简单问题。

**失败模式对照 MAST**：不 frozen 的 spec → FM-1.1；worker 直写共享状态 → FM-2.4/2.5 的工程温床；没有 verifier → FC3 全家桶。
</details>

## 5. 自学资料

1. [How we built our multi-agent research system](https://www.anthropic.com/engineering/multi-agent-research-system) — 正方必读：orchestrator-worker 全部工程细节、effort scaling prompt、15x token 经济学、end-state eval · 20 min
2. [Don't Build Multi-Agents (Cognition)](https://cognition.com/blog/dont-build-multi-agents) — 反方必读：share context / actions carry implicit decisions 两原则 + compressor 架构；与上一篇对照读 · 10 min
3. [Why Do Multi-Agent LLM Systems Fail? (MAST)](https://arxiv.org/abs/2503.13657) — 14 种失败模式与实证比例；重点读 taxonomy 图和 case study 两节 · 30 min
4. [OpenAI Agents SDK: Orchestrating multiple agents](https://openai.github.io/openai-agents-python/multi_agent/) — LLM vs code orchestration、handoffs vs agents-as-tools 的官方决策指南 · 10 min
5. [OpenAI Agents SDK: Handoffs](https://openai.github.io/openai-agents-python/handoffs/) — handoff=tool call 的实现细节、`input_filter` 裁剪历史 · 10 min
6. [Claude Code: Create custom subagents](https://code.claude.com/docs/en/sub-agents) — 生产系统里"独立 context、只回最终文本"的实际形态与配置格式 · 10 min
7. [MAST repo (GitHub)](https://github.com/multi-agent-systems-failure-taxonomy/MAST) — 1600+ 标注 trace 数据集 + LLM-as-judge pipeline 代码，想看真实失败 trace 长什么样就翻这里 · 15 min
8. [A2A Protocol (a2aproject/A2A)](https://github.com/a2aproject/A2A) — Agent Card 与 task 生命周期规范；扫 `docs/specification.md` 即可 · 10 min
9. 动手：[v1 lab04 · 原生 Orchestrator/Workers/Memory](../../agentic/labs/04_multi_agent_memory/README.md) — 60 min 内不靠框架实现有界并发、typed result、冲突不写入、CAS 共享状态；上面工程要点块的可运行版本 · 60 min
