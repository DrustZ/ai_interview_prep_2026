# 01 · Agent Loop 与 Tool 契约

⏱ 骨架 8 min ｜ 含深潜与资料 40 min ｜ 面试前只看 ⭐⭐⭐ 部分

## 1. Model plane vs control plane ⭐⭐⭐

- 模型负责：理解模糊目标、提出候选计划、选择工具、总结证据、发现可能遗漏。
- 确定性代码必须负责：
  - 身份、权限、租户隔离和 secret 注入。
  - 状态迁移、step/cost/time budget、timeout 和取消。
  - schema validation、rate limit、retry policy 和 idempotency。
  - action 是否需要审批、批准是否仍有效。
  - 完成条件、grader、发布 gate 和 audit。
- 把 `is_done`、权限或重试副作用交给模型的后果：不可复现、越权、无限循环、重复操作。

> 高分句：让模型提出下一步，让状态机决定这一步是否允许、如何执行以及怎样证明成功。

## 2. Agent loop：最小而完整 ⭐⭐⭐

```python
def run(task, state, *, max_steps, deadline):
    while state.step < max_steps and now() < deadline:
        context = build_context(task, state)
        response = model.complete(context, visible_tools(state))
        append_event(state, "model_response", response)

        if response.final_answer is not None:
            if deterministic_grader(task, state, response.final_answer):
                return succeed(state, response.final_answer)
            append_event(state, "validation_failed", {})
            continue

        calls = validate_calls(response.tool_calls)
        results = execute_with_policy(calls, state)
        append_results(state, results)

    return fail(state, "budget_or_deadline_exhausted")
```

循环的关键不是 `while`，而是五个边界：

- `build_context` 只放当前任务需要的信息。
- `visible_tools` 已按身份、任务和风险过滤。
- `validate_calls` 不相信模型参数。
- `execute_with_policy` 处理并行、审批、timeout、retry 和幂等。
- `deterministic_grader` 不接受模型口头宣告完成。

> 高分句：这个 loop 的价值在五个边界，不在 while——每个边界都是一个不信任模型的确定性检查点。

## 3. Claude tool-use 协议（7 步）⭐⭐⭐

1. 发送 user message 和 tool schemas。
2. assistant 返回一个或多个 `tool_use` block，响应停止原因表明需要工具。
3. 把完整 assistant content 加入 history。
4. 执行每个工具。
5. 下一条 user message 中放所有对应 `tool_result`，每个匹配 `tool_use_id`。
6. 工具异常作为带 error 标记的 result 回传，给模型观察后决定新策略。
7. 外层仍强制 max steps/deadline/cost。

并行规则：同一 turn 的多个结果一起回传；只读且独立的调用可以有界并行，写操作默认不并行。

> 高分句：工具异常是 observation，不是 exception——回传给模型让它改策略，但是否允许重试由外层 policy 决定。

<details>
<summary>深潜：并行 tool call 与流式参数解析的工程实现</summary>

【技术机制 · 并行调用】

- 协议：一条 assistant message 可以含多个 `tool_use` block，`stop_reason="tool_use"`。API 不规定执行顺序——`asyncio.gather` 并发、顺序执行、按 §4 的 `parallel_safe/risk` 分组混合执行都是合法的，执行策略完全是 harness 的决定。
- 结果回传的硬规则：该 turn 所有 `tool_result` 必须放在**紧跟着的同一条 user message** 里，每个用 `tool_use_id` 配对，且 `tool_result` block 必须排在该消息 content 的最前面。
- 最隐蔽的坑：把多个结果拆成多条 user message **不报错**，但等于在 history 里给模型演示「一次只调一个工具」——几轮之后模型就不再并行了。history 即 few-shot，格式错误会被模型学走（官方 docs 明确警告这一点）。
- 关停/强制开关：`tool_choice` 四种取值 `auto` / `any`（必须调某个工具）/ `tool`（必须调指定工具）/ `none`；`auto` 下可设 `disable_parallel_tool_use: true` → 每轮最多一个 tool call。写操作多的 agent 常直接关并行换确定性。

【技术机制 · 流式参数（partial JSON）】

- 标准 streaming 下，`tool_use` block 的 `content_block_start` 事件里 `input` 是空对象占位，参数以一串 `input_json_delta` 事件到达，payload 是 `partial_json` 字符串片段，**不按 JSON 边界切**；客户端拼接后在 `content_block_stop` 时 parse。默认服务端会缓冲并校验完整 JSON 后才下发。
- 加 beta header `fine-grained-tool-streaming-2025-05-14` 则去掉服务端缓冲，片段随生成直接下发：首字节延迟大幅下降（适合流式展示长代码/长文档参数），代价是可能收到非法 JSON——尤其 `max_tokens` 把参数拦腰截断时。

```python
buf = {}
async for ev in stream:
    if ev.type == "content_block_start" and ev.content_block.type == "tool_use":
        buf[ev.index] = {"id": ev.content_block.id,
                         "name": ev.content_block.name, "json": ""}
    elif ev.type == "content_block_delta" and ev.delta.type == "input_json_delta":
        buf[ev.index]["json"] += ev.delta.partial_json
        maybe_render(best_effort_parse(buf[ev.index]["json"]))  # 进度 UI 用宽容前缀的 partial-JSON parser
    elif ev.type == "content_block_stop" and ev.index in buf:
        try:
            args = json.loads(buf[ev.index]["json"] or "{}")
        except json.JSONDecodeError:
            args = None  # fine-grained + 截断：当 validation error 回传模型，绝不带半截参数执行
```

【失败模式】

- `tool_use_id` 配对错/漏一个 result → 下一次 API 调用直接 400。
- 截断的 JSON 拿去执行写操作 = 半参数副作用，最危险的一类 bug；guard parse 是必须的。
- 用严格 `json.loads` 做逐片段进度展示会一直抛异常——进度展示要用容忍不完整前缀的 parser，最终执行仍用严格 parse。

来源：[Parallel tool use](https://platform.claude.com/docs/en/agents-and-tools/tool-use/parallel-tool-use) ｜ [Fine-grained tool streaming](https://docs.claude.com/en/docs/agents-and-tools/tool-use/fine-grained-tool-streaming)

</details>

## 4. Tool design：为非确定性调用者设计契约 ⭐⭐

```python
@dataclass(frozen=True)
class ToolSpec:
    name: str
    description: str
    input_schema: dict
    version: str
    risk: str                  # read / reversible_write / irreversible
    parallel_safe: bool
    timeout_seconds: float
    max_result_bytes: int
    required_scopes: tuple[str, ...]
```

好工具 checklist：

- [ ] 名称和描述说明「何时用、何时不用、返回什么」。
- [ ] schema 小且约束强；枚举、required、范围、格式明确。
- [ ] 粒度围绕完整意图，而不是把底层 API 每个 endpoint 原样暴露。
- [ ] 返回最小但足够的上下文，并给稳定 ID；不要倾倒巨量 JSON。
- [ ] error 结构化：`code/message/retryable/retry_after`。
- [ ] secret 由 executor 注入，不进入 prompt、trace 或 model output。
- [ ] tool output 是不可信数据，不能修改 system policy。

<details>
<summary>Retry matrix（按错误类型的默认策略）</summary>

| 情况 | 默认策略 |
|---|---|
| read + transient 429/5xx | bounded exponential backoff + jitter |
| validation error | 不原样重试；把具体字段错误回传模型 |
| deterministic not-found | 通常不重试，除非模型能改变查询 |
| write 且 provider 支持 idempotency key | 同 key 可安全重试；先查 status 更稳 |
| write 且不支持幂等 | timeout 后进入 unknown，不自动重复 |
| permission denied | 不重试；解释需要的 authority |

write 超时后的 unknown 状态处理见 [./02_state_and_memory.md](./02_state_and_memory.md) crash window 一节。

</details>

> 高分句：工具描述影响选择，但权限不在描述里；executor 再做 authentication、authorization 与 validation。

## 5. 现有系统怎么做 ⭐⭐⭐

历史基线一句话：ReAct（[arxiv 2210.03629](https://arxiv.org/abs/2210.03629)）确立 thought→action→observation 交替循环。2025-26 生产系统的分歧已经不在「要不要循环」，而在三个轴：**action 用什么表示**（JSON tool call / bash 文本 / 可执行代码）、**执行环境**（独立 subprocess / 长驻 harness / 沙箱解释器）、**控制点插在哪**（hooks / guardrails / 审批中断 / 自写 policy）。

| 系统 / 方法 | 核心机制一句话 | 适用场景 | 链接 |
|---|---|---|---|
| mini-swe-agent | 只有 bash、不用 tool-calling API：模型每步输出一个 bash 块，`subprocess.run` 独立执行，线性 append 历史，agent 类 ~100 行，SWE-bench Verified >74% | 基准、研究、可重放实验；验证「模型强则 scaffold 可以薄」 | [GitHub](https://github.com/SWE-agent/mini-swe-agent) |
| SWE-agent（ACI） | 为 LM 定制 agent-computer interface：窗口化文件查看、带 lint 守卫的 edit、限量 search | 为特定域优化工具界面时的设计参照 | [arxiv 2405.15793](https://arxiv.org/abs/2405.15793) |
| Claude Agent SDK | 把 Claude Code 的 harness 当库用：内置 tools + compaction，控制点是 hooks / permission 回调 / subagents；streaming input 模式下是长驻进程 | 要生产级 harness（审批、压缩、子代理）但不想自己写 loop | [docs](https://platform.claude.com/docs/en/agent-sdk/streaming-vs-single-mode) |
| OpenAI Agents SDK | Runner 循环 + handoffs（换 active agent 的特殊 tool call）+ 并行 guardrails + 可序列化的审批中断 | 多 agent 分诊/工作流，需要内建 HITL | [docs](https://openai.github.io/openai-agents-python/) |
| smolagents（CodeAct） | action = 可执行 Python 代码，AST 解释器或沙箱执行，变量跨步持久；论文报最高 +20% 成功率 vs JSON call | 工具组合密集、数据处理型任务 | [arxiv 2402.01030](https://arxiv.org/abs/2402.01030) |
| 手写 loop（lab01 = §2） | 五边界循环，完全控制 context、policy、grader | 特殊 policy/合规/成本需求，核心业务 loop | 本文 §2 |

<details>
<summary>mini-swe-agent：bash 即 ACI（与 SWE-agent ACI 思想对照）</summary>

【技术机制】

- 数据结构：唯一状态是 `messages: list[dict]`，纯线性 append，没有工具注册表、没有 JSON schema。工具契约靠 system prompt 的自然语言约定：「每次回复恰好一个 ```bash 代码块」。它甚至不走 API 的 tool-calling 接口——就是普通 text completion。
- 处理流程：query 模型 → 正则抽取 bash 代码块 → `subprocess.run` 执行拿 stdout/returncode → 截断后作为 user message append → 循环。抽到 0 个或多个代码块 → append 一条格式错误消息让模型重试（错误即 observation，同 §3）。
- 每个 action 是**独立 subprocess，无状态 shell**。代价：`cd`、`export`、激活 venv 不跨步生效，模型每条命令要自带完整上下文；收益：环境可整体替换（local/docker/ssh 只换 environment 类，agent 不动），且线性历史 + 无隐藏状态 = 可以完美重放调试。
- 终止：模型在 bash 里 echo 一个约定的完成 marker，harness 在 stdout 检测到即收尾——「宣告完成」也走同一条 action 通道，不需要专门的 finish tool。

```python
class DefaultAgent:                       # 结构示意，忠于原设计
    def run(self, task):
        self.messages = [system(TPL), user(task)]
        for _ in range(self.step_limit):
            out = self.model.query(self.messages)     # 纯文本，不传 tools 参数
            self.messages.append(assistant(out))
            blocks = re.findall(r"```bash\n(.*?)```", out, re.S)
            if len(blocks) != 1:
                self.messages.append(user(FORMAT_ERROR)); continue
            r = subprocess.run(blocks[0], shell=True,
                               capture_output=True, timeout=self.timeout)
            obs = truncate(r.stdout + r.stderr, self.max_obs_chars)
            if FINISH_MARKER in obs:
                return extract_final(obs)
            self.messages.append(user(f"returncode={r.returncode}\n{obs}"))
```

- 关键参数：per-command timeout、observation 截断长度、step limit、cost limit——正是 §2 的边界，只是砍到最薄。
- 失败模式：线性历史无 compaction，`grep` 大 repo 一次输出就能淹掉 context；无并行；stateless shell 对没见过这套约定的模型是坑；工具粒度不可控（bash 什么都能干，§4 的 risk 分级无从谈起，只适合沙箱内跑）。
- 与 SWE-agent ACI（arxiv 2405.15793）对照：ACI 论文方向相反——论证「LM 是新一类用户，界面要为它定制」：窗口化 file viewer（一次只看 ~100 行）、`edit` 命令内嵌 lint 检查（编辑引入语法错误直接拒绝并回报）、search 限制返回条数。两个结论合起来是面试高分答案：**模型弱 → 用 ACI 补界面；模型强 → bash 本身就是最通用的 ACI**。mini-swe-agent 就是同一团队在强模型时代把自家 ACI 论文「反过来做」的实验，且 >74% 的分数证明了这一点。

</details>

<details>
<summary>Claude Agent SDK：harness 作为库，hooks 作为 control plane 插点</summary>

【技术机制】

- 定位：不是「帮你调 API 的薄封装」，而是把 Claude Code 的完整 harness（内置 file/bash/web tools、自动 context compaction、session 持久化）暴露为 SDK。内层 loop 不是你写的，你拿到的是插点。
- 两种输入模式：
  - single message：`query(prompt="...")`，一次任务、消费完 message 流即结束。简单但受限。
  - streaming input：传 async iterable / 用 `ClaudeSDKClient` 保持长驻进程——可以中途插话、打断、排队多条消息；官方明确这是推荐模式，hooks、图片输入等能力只在此模式完整。
- 三类控制点（对应本文 §1 的 control plane）：
  1. **hooks**：在 loop 生命周期点执行你的确定性代码。事件包括 `PreToolUse`（收到 tool_name + tool_input，返回 allow/deny/ask，可改参）、`PostToolUse`（可改写结果）、`Stop`（可拒绝停止、强制继续）、`SessionStart/End`、`UserPromptSubmit`。§2 的 `validate_calls` / `execute_with_policy` 在这里落位。
  2. **permission 回调**：`canUseTool(tool_name, input)` → 允许/拒绝/修改，配合 permission_mode 做人审。
  3. **subagents**：注册 `AgentDefinition(description, prompt, tools)`，主 agent 通过 Agent tool 委派；子 agent 在独立 context window 工作、只回传结论——官方版 context isolation。

```python
from claude_agent_sdk import query, ClaudeAgentOptions, HookMatcher  # 结构示意

async def deny_prod_writes(input_data, tool_use_id, ctx):
    if touches_prod(input_data["tool_input"]):
        return {"hookSpecificOutput": {
            "hookEventName": "PreToolUse",
            "permissionDecision": "deny",
            "permissionDecisionReason": "prod writes require approval"}}
    return {}

options = ClaudeAgentOptions(
    allowed_tools=["Read", "Grep", "Bash"],
    hooks={"PreToolUse": [HookMatcher(matcher="Bash", hooks=[deny_prod_writes])]},
)
async for msg in query(prompt="fix the failing test", options=options):
    handle(msg)
```

- 失败模式/取舍：harness 黑盒程度高——inner system prompt 与 context 组装不可完全控；进程模型偏重（背后是 Claude Code 运行时）；API 随版本演进快。需要完全自定义 context 策略时（本仓库 §2 的场景）它不合适，hooks 是唯一逃生门。
- 代码参考：[anthropics/claude-agent-sdk-python](https://github.com/anthropics/claude-agent-sdk-python)。

</details>

<details>
<summary>OpenAI Agents SDK：handoffs、并行 guardrails、可序列化的审批中断</summary>

【技术机制】

- 三原语：Agent（instructions + tools）、Handoff（委派）、Guardrail（输入/输出校验），外加 Sessions（跨 run 记忆）。Runner 驱动 loop：

```python
async def run(agent, input, max_turns):                 # Runner 语义伪码
    schedule(run_input_guardrails(agent, input))        # 与首次模型调用并行；tripwire → 抛异常
    current, turn = agent, 0
    while (turn := turn + 1) <= max_turns:
        resp = await model.call(current.instructions, history,
                                tools=current.tools + handoff_tools(current))
        if resp.is_final_output():          # 无 tool call 且（纯文本或匹配 output_type）
            await run_output_guardrails(current, resp)
            return RunResult(resp)
        if resp.handoff_call:               # 名为 transfer_to_<agent> 的特殊 tool
            current = resolve_handoff(resp.handoff_call)   # 换 instructions+tools，history 保留
            continue
        results = await asyncio.gather(*(invoke(c) for c in resp.tool_calls))
        history += [resp, *results]
    raise MaxTurnsExceeded
```

- **handoff 的本质**：每个可交接 agent 被编译成一个名为 `transfer_to_<name>` 的 tool；模型调用它 = runner 把 current agent 换掉（新 system prompt + 新工具集），对话历史默认全量带过去（可用 input_filter 裁剪）。这是「换脑不换记忆」——和 subagent（独立 context、只回传结果）是**相反的多 agent 拓扑**，面试常考二者取舍。
- **guardrails**：输入 guardrail 与第一次模型调用并行跑（不加延迟），tripwire 触发即抛 `InputGuardrailTripwireTriggered`，fail-fast 省掉后续昂贵调用。
- **HITL 中断**：tool 声明需要审批（JS SDK 为 `needsApproval`）→ run 不抛异常，返回带 `interruptions` 的结果；RunState 可序列化落库；人批准后 `state.approve(interruption)` 再 `Runner.run(agent, state)` 恢复——审批可以跨进程、跨天完成。这是 §2「审批由确定性代码把关」的框架级实现。
- 失败模式：handoff 链可能成环（A→B→A），要外层 max_turns 兜底；history 全量交接导致 token 膨胀，需 input_filter；guardrail 默认只挂在入口 agent 上，handoff 之后的 agent 不会自动继承。

</details>

<details>
<summary>smolagents / CodeAct：代码即 action，AST 解释器即 executor</summary>

【技术机制】

- 论点（CodeAct，arxiv 2402.01030）：用可执行 Python 作为统一 action 空间，替代 JSON/文本 tool call；在 API-Bank、M3ToolEval 上对 17 个 LLM 评测，最高 +20% 成功率。原因有三：组合性（for 循环里批量调 tool、中间变量直接复用——JSON 里无法表达「把 action A 的输出存下来给 action C」）、训练分布（模型见过海量 Python，没见过你家的 JSON DSL）、一步多 action 省 round-trip。
- smolagents 的实现（HF）：`CodeAgent` 每步输出 Thought + ```py 代码块，解析后交给 executor：
  - `LocalPythonExecutor` **不是 `exec()`**：是自写的 AST 解释器，逐节点求值——import 白名单（`additional_authorized_imports`）、builtins 白名单、操作计数上限防死循环。
  - tools 作为 Python callable 注入解释器命名空间；变量存在跨步持久的 state 里（step 3 能直接用 step 1 算出的 dataframe）——这就是 object management 问题的解。
  - `final_answer(x)` 是特殊 tool，调用即终止循环。
  - 生产推荐远程沙箱 executor（E2B / Docker），拿进程级隔离。

```python
while step < max_steps:                       # CodeAgent 语义伪码
    out = model(messages)                     # "Thought: ...\n```py\n...\n```"
    code = extract_py_block(out)
    try:
        result, logs, is_final = executor(code, state)  # AST walk；tools 与既有变量都在 state
    except InterpreterError as e:
        messages.append(user(f"Error: {e}")); continue  # 错误即 observation
    messages.append(user(f"Observation: {logs}"))
    if is_final:
        return result
```

- 失败模式：安全是第一位——本地 AST 白名单挡不住所有 exfil 路径（prompt injection 后用已授权的网络库外传），必须沙箱；弱模型语法错误率高、堆栈长要截断；**审批粒度是真实短板**：一个代码块内含多个副作用，无法像 JSON call 那样对单个写操作做 `needsApproval`，高风险写场景反而适合退回 JSON tool call。
- 概念综述：[smolagents docs · intro to agents](https://huggingface.co/docs/smolagents/conceptual_guides/intro_agents)。

</details>

<details>
<summary>手写 loop（lab01）：什么时候写、要自己补齐什么</summary>

【技术机制/定位】

- 什么时候手写：context 组装策略特殊（自定义 compaction、检索注入）、合规要求每个 decision point 可审计、成本敏感不接受 harness 的 token 开销、要嵌进已有工作流引擎/队列系统。
- 框架替你做了、手写就要自己补齐的清单：
  - session 持久化与 crash 恢复（event log 重放，见 02 篇）；
  - context compaction 触发与摘要策略；
  - 并行 tool 执行 + `tool_use_id` 配对回传（§3 深潜块）；
  - HITL 中断/恢复的状态序列化（对标 Agents SDK 的 RunState）；
  - tracing/telemetry、tool schema 版本管理、error→observation 格式约定。
- 定位一句话：先用 §2 骨架跑通，再对着上面四个系统按需「偷设计」——mini 的可重放线性历史、Claude SDK 的 hook 位点、Agents SDK 的可序列化中断、CodeAct 的 action 表示，每一项都可以单独抄，不必整套引框架。

</details>

> 高分句：这五个系统是同一个 loop 的五份答卷，差异只在 action 表示、执行环境和控制点位置——说清你的任务在这三个轴上的需求，选型就自动完成了。

## 6. 自学资料

1. [Building Effective AI Agents](https://www.anthropic.com/engineering/building-effective-agents) — workflow 五模式（chaining/routing/parallelization/orchestrator-workers/evaluator-optimizer）vs agent 的选型框架；回答「什么时候不该用 agent」的标准出处 · 20 min
2. [Writing effective tools for AI agents—using AI agents](https://www.anthropic.com/engineering/writing-tools-for-agents) — §4 checklist 的官方展开：token 效率（分页/截断/默认值）、error 消息的 prompt 工程、用 agent 评测工具 · 20 min
3. [mini-swe-agent（GitHub）](https://github.com/SWE-agent/mini-swe-agent) — 通读 ~100 行 agent 源码建立「最小 harness」心智基线；README 三条设计声明（bash-only / 线性历史 / subprocess.run）可直接引用 · 30 min
4. [Parallel tool use — Claude Docs](https://platform.claude.com/docs/en/agents-and-tools/tool-use/parallel-tool-use) — 结果消息格式如何反过来训练模型的并行行为；`disable_parallel_tool_use` · 10 min
5. [Executable Code Actions Elicit Better LLM Agents（CodeAct）](https://arxiv.org/abs/2402.01030) — code-as-action 的论证与 up-to-20% 数据，读方法与实验设置即可 · 30 min
6. [OpenAI Agents SDK docs](https://openai.github.io/openai-agents-python/) — 重点读 Running agents（loop 语义）、Handoffs、Guardrails 三页，对照 Claude SDK 找结构差异 · 30 min
7. [Streaming Input mode — Claude Agent SDK](https://platform.claude.com/docs/en/agent-sdk/streaming-vs-single-mode) — 两种输入模式的能力差异，为什么长驻 agent 必须用 streaming input · 10 min
8. [Fine-grained tool streaming — Claude Docs](https://docs.claude.com/en/docs/agents-and-tools/tool-use/fine-grained-tool-streaming) — 无缓冲流式参数的取舍与 invalid JSON 防御 · 10 min
9. [SWE-agent: Agent-Computer Interfaces Enable Automated Software Engineering](https://arxiv.org/abs/2405.15793) — ACI 设计原则（lint 守卫 edit、窗口化 viewer、限量 search），「界面影响 agent 性能」的量化证据 · 30 min
10. [Introducing advanced tool use on the Claude Developer Platform](https://www.anthropic.com/engineering/advanced-tool-use) — 工具规模化的下一步：tool search、programmatic tool calling；回答「几百个 tool 怎么办」 · 15 min
