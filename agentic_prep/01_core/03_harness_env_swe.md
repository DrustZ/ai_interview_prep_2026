# 03 · Harness、Environment 与 Coding Agent

⏱ 骨架 6 min ｜ 含深潜与资料 35 min ｜ 面试前只看 ⭐ 部分

## 1. Harness 七要素 ⭐

Harness = 模型周围让任务可理解、可执行、可验证的系统。

| 要素 | 内容 |
|---|---|
| Task spec | 目标、范围、acceptance、budget、repo/data revision |
| Environment | 隔离文件系统/浏览器/API sandbox、network policy、fixtures |
| Tools | 检查、修改、运行、测试、观察 |
| Context builder | 入口地图、相关文档、当前状态、最近证据 |
| State store | run/task/event/checkpoint/artifact |
| Verifiers | tests、schema、policy、simulator、judge、human |
| Observability | trace、cost、latency、tool errors、artifacts |

> 高分句：最有价值的改进往往是给 agent 更好的环境和 verifier，而不是让它「再努力一次」。

## 2. 对 coding agent 特别重要的五点 ⭐

1. **Repository legibility**：短入口文件是地图，深度文档按需读取；规则要能被 lint/CI 执行。
2. **反馈回路**：agent 能启动应用、读日志/metrics、操作 UI、跑最小测试。
3. **隔离**：每个 run 独立 worktree/container，凭证最小化。
4. **计划是 artifact**：复杂任务保存 progress、decision、remaining work，不依赖聊天历史。
5. **结构约束**：依赖方向、schema boundary、日志、文件大小等机械检查防 drift。

> 高分句：规则要能被 lint/CI 执行——不能机械验证的约定迟早腐化。

## 3. 现场流程：侦察到回归 ⭐

面试/演示中不要展示「我让 AI 一次写完」。展示：

侦察 → 验收 → 窄任务 → 最小测试 → diff review → 完整回归

每一步产出可验证的 artifact，让面试官看到验证证据而不是运气。

## 4. TaskSpec 与分解原则 ⭐

好 `TaskSpec` 必须让不看主对话的 worker 也能执行：

```python
@dataclass(frozen=True)
class TaskSpec:
    task_id: str
    goal: str
    inputs: tuple[str, ...]
    constraints: tuple[str, ...]
    expected_artifact: str
    acceptance_checks: tuple[str, ...]
    deadline: datetime
    budget: int
```

分解原则：

- 按可独立验证的 artifact 切，不按「让三个 agent 都想一遍」切。
- 并行任务避免共享可变状态；各自在 branch/artifact 中工作。

orchestration / fan-in / verifier / 动态停止见 [./04_multi_agent.md](./04_multi_agent.md)。

> 高分句：好 TaskSpec 的检验标准是——不看主对话的 worker 也能独立执行并被 acceptance_checks 验收。

## 5. 现有系统怎么做 ⭐

| 系统/方法 | 核心机制一句话 | 适用场景 | 链接 |
|---|---|---|---|
| SWE-agent (ACI) | 为 LM 重新设计 file viewer/editor/search 命令集，editor 内置 lint 守卫，接口设计本身带来 3.8%→12.5% 的提升 | 研究/理解「接口即能力」；自建 harness 时的工具设计参照 | [arxiv 2405.15793](https://arxiv.org/abs/2405.15793) |
| OpenHands | Event stream（Action/Observation 事件流）为唯一状态源 + 每 session 一个 docker sandbox，容器内跑 action execution server | 通用 agent 平台；需要 bash+jupyter+browser 混合环境 | [arxiv 2407.16741](https://arxiv.org/abs/2407.16741) · [repo](https://github.com/OpenHands/OpenHands) |
| OpenAI Codex (cloud) | universal 容器镜像 + setup script（有网）/ agent phase（默认无网、代理白名单）两阶段 + AGENTS.md 作地图 | 云端异步任务、批量并行 PR；安全默认值最保守 | [环境 docs](https://developers.openai.com/codex/cloud/environments) · [codex-universal](https://github.com/openai/codex-universal) |
| Claude Code | CLAUDE.md 分层记忆 + hooks（确定性强制）+ 权限 allowlist/OS 级 sandbox + git worktree 并行 | 本地/交互式开发；人机混合、规则需机械强制 | [best practices](https://code.claude.com/docs/en/best-practices) |
| E2B（托管沙箱层） | 每 sandbox 一个 Firecracker microVM（独立 guest kernel），snapshot ~150ms 恢复，SDK 管理生命周期 | 跑不可信/模型生成代码；多租户 agent 产品的执行层 | [docs](https://e2b.dev/docs) · [blog](https://e2b.dev/blog/firecracker-vs-qemu) |
| SWE-bench harness | 三层 docker 镜像（base→env→instance）+ git apply patch + FAIL_TO_PASS/PASS_TO_PASS 双向判定 | 评测/回归基线；自建 eval 流水线的模板 | [repo](https://github.com/swe-bench/SWE-bench) |

> 高分句：这五家收敛到同一结论——隔离边界、反馈回路、镜像准备是 harness 的三根柱子，差异只在把安全边界画在 process、container 还是 microVM。

<details>
<summary><b>SWE-agent：Agent-Computer Interface（ACI）的技术机制</b></summary>

【设计动机】LM agent 是一类新的「终端用户」：给它 vim + 裸 shell（为人类设计的接口）表现很差——`cat` 大文件淹没上下文、交互式程序挂死、编辑靠 sed 易碎。ACI 的核心论点：**接口设计本身是能力来源**，同一模型换接口，SWE-bench 从 RAG 基线 3.8% 到 12.5%。

【数据结构与命令集】所有工具以 shell function 注入一个持久 bash session，系统提示里给命令文档：

- **File viewer**：`open <path> [line]` / `goto <line>` / `scroll_up|down`——每次只显示一个 **100 行窗口**（ablation 结论：30 行窗口太碎、整文件太吵，100 行最优），顶部显示总行数与当前位置。
- **Editor**：`edit <start>:<end> <<EOF ... EOF`——按行号区间替换，**内置 lint 守卫**。
- **Search**：`search_dir` / `search_file` / `find_file`——结果超过 ~50 条时只返回摘要（文件名+命中数），防止淹没上下文。

【edit 守卫流程（关键创新）】

```text
edit 120:135 <<EOF
    ...new code...
EOF
# 内部：
1. 备份文件，替换 [120,135] 行区间
2. 跑 flake8（只查 syntax 级错误，E999/undefined-name 类）
3. lint 失败 → 回滚到备份，返回错误信息 + 出错处上下文窗口，
   提示「你的编辑没有生效，请修正后重试」
4. lint 通过 → 落盘，返回编辑后 ±N 行窗口供模型自查
```

ablation：去掉 lint 守卫，成功率显著下降——大量失败模式是一次坏编辑（缩进错/括号不闭合）之后连锁崩坏。

【上下文管理】只保留最近 5 条 observation 全文，更早的折叠成一行占位。这是最早的「observation 淘汰」实现之一。

【隔离与反馈回路】每个 task 在 docker 容器里跑（repo checkout 到指定 commit）；反馈= lint 结果 + 命令 stdout/stderr + 测试输出，全部作为 observation 回流。

【坑】① 行号编辑对「模型数错行」敏感——后续系统（Aider、Claude Code）多改用 search/replace 字符串匹配；② 100 行窗口导致反复 scroll 浪费轮次；③ 交互式命令（如 `python` REPL）仍会挂死，需 timeout 兜底。

</details>

<details>
<summary><b>OpenHands：event stream 架构 + docker runtime + AgentSkills</b></summary>

【核心抽象】状态 = 按时间排序的 **event stream**，事件只有两类：`Action`（agent 想做什么）与 `Observation`（环境返回什么）。agent 本身无状态，每步从 stream 重建 State。好处：可回放、可持久化恢复、多 agent delegation 只是往同一条流里写事件。

【控制循环（简化）】

```python
# agent_controller 主循环
while not done and steps < max_iterations and cost < budget:
    state  = State(history=event_stream.get_events())
    action = agent.step(state)              # LLM 决策 → Action 对象
    event_stream.add(action)
    obs = await runtime.run_action(action)  # HTTP → 容器内 action server
    event_stream.add(obs)                   # Observation 回流为下一步上下文
```

【Runtime 机制】每个 session 启动一个 docker 容器，容器内跑一个 **action execution server**（REST API）。宿主侧 runtime 把 Action 序列化后 POST 进去执行：

- `CmdRunAction` → 持久 bash session（保 cwd/env 连续性，带 timeout）
- `IPythonRunCellAction` → 常驻 Jupyter kernel
- `FileRead/FileEditAction` → 文件操作（edit 复用 SWE-agent/Aider 式带 lint 的编辑）
- `BrowseInteractiveAction` → 容器内 headless chromium（browsergym 封装）

沙箱可配 memory/CPU limit、timeout、restricted network、read-only volumes。runtime 抽象成接口后可换实现：local docker / 远端 K8s / 第三方沙箱。

【AgentSkills】一个预装进 Jupyter kernel 的 Python 工具库（`edit_file`、`parse_pdf` 等）——把「工具」实现为可 import 的函数而不是 JSON tool schema。配合 **CodeAct** 范式：agent 的 action 就是一段可执行代码，一步能组合多个操作，比逐个 JSON tool call 省轮次。

【坑】① event stream 无限增长 → 需要 condenser（截断/摘要旧事件），否则长任务爆上下文；② 容器冷启动慢 → 靠预构建 runtime 镜像 + 复用缓解；③ CodeAct 代码报错时错误栈很长，回流前要裁剪；④ browser 事件的 observation（DOM/AXTree）极大，是上下文最大消耗源。

</details>

<details>
<summary><b>OpenAI Codex cloud：两阶段生命周期 + 无网 agent phase + AGENTS.md</b></summary>

【任务生命周期】

```text
1. 从 codex-universal 基础镜像起容器，checkout repo
2. 跑 setup script（此阶段有完整 internet；secrets 只在此阶段可见，
   进入 agent phase 前删除）
3. 应用网络策略：agent phase 默认断网，可配 domain 白名单，
   所有流量强制走 HTTP/HTTPS proxy
4. agent 循环：编辑代码 + 跑命令/测试验证
5. 产出 diff/PR；容器缓存最多 12h，resume 时跑 maintenance script
   （setup script / secrets / env vars 变更会使缓存失效）
```

【镜像与环境准备】`codex-universal` 预装主流语言工具链，通过 `CODEX_ENV_PYTHON_VERSION` 等环境变量 pin 版本（支持 Python/Node/Rust/Go/Swift/Ruby/PHP），参考 Dockerfile 开源可本地拉取调试。常见包管理器（npm/pip/poetry…）自动 setup，复杂项目写自定义 bash setup script 装 typechecker/依赖。

【为什么 agent phase 断网】把 prompt injection 与数据外泄的爆炸半径压到最小：模型能改代码、跑测试，但不能把 secrets 发出去、不能拉恶意依赖。代价是 agent 不能临时装包——所有依赖必须在 setup 阶段就绪，这是最常见的配置坑（本地能跑、云上 agent 装不了包）。

【AGENTS.md 与 harness engineering】官方经验（harness-engineering 文章）：
- AGENTS.md 是**地图不是说明书**——「one big AGENTS.md」失败，因为巨型指令文件挤占任务本身的上下文；短入口 + 指针指向按需读的深度文档。
- **taste 用机械约束执行**：风格/架构规则写成 lint 规则、CI 检查、目录结构约定，而不是自然语言恳求。repo 的初始脚手架（CI 配置、格式化规则、包管理）本身就可由 agent 生成后固化。
- repository legibility 是一等工程目标：为 agent 优化的仓库 = 短文件、显式依赖方向、可机械验证的约定。

【坑】① setup script 与 CI 环境漂移 → 测试结果不可信；② 断网下测试若依赖外部服务会假失败，需 fixtures/mock；③ 12h 缓存 + 老 commit resume → maintenance script 忘写就是脏环境。

</details>

<details>
<summary><b>Claude Code：CLAUDE.md 分层 + hooks + 权限/sandbox + worktree</b></summary>

【CLAUDE.md（advisory 层）】每次会话开始加载的分层记忆：`~/.claude/CLAUDE.md`（全局）→ 项目根（入 git 共享）→ `CLAUDE.local.md`（个人）→ 子目录（按需拉取）→ `@path` import 其他文件。官方纪律：每行自问「删掉会不会导致犯错」，不能就删——过长的 CLAUDE.md 会让真正的规则被淹没。只放广泛适用的内容，领域知识放 skills 按需加载。

【Hooks（deterministic 层）】CLAUDE.md 是请求、hooks 是保证。生命周期事件（`PreToolUse` / `PostToolUse` / `SessionStart` / `Stop`）触发 shell 命令，hook 进程从 stdin 读工具调用的 JSON，用退出码控制放行/阻止：

```json
// .claude/settings.json
{ "hooks": { "PostToolUse": [ {
    "matcher": "Edit|Write",
    "hooks": [ { "type": "command",
                 "command": "eslint --fix \"$CLAUDE_FILE_PATHS\"" } ]
} ] } }
```

典型用法：每次写文件后自动 format、编辑后跑快速测试、阻止写 migrations 目录、`Stop` hook 把「测试必须绿」变成回合结束的硬门禁（连续 8 次 block 后强制放行防死循环）。

【权限与 sandbox】三档递进：`/permissions` allowlist 具体命令（如 `npm run lint`）→ auto mode（独立 classifier 模型审查命令，只拦 scope escalation/未知 infra）→ `/sandbox` OS 级隔离（macOS 用 Seatbelt、Linux 用 namespace 类机制，限制文件系统与网络 egress）。设计假设是 **bounded failure**：即使 prompt injection 得手，sandbox 仍挡住关键文件修改与未授权外联。

【并行与反馈回路】每个并行 session 一个 **git worktree**（独立 checkout，编辑不冲突）；核心最佳实践是「给 Claude 一个它能自己跑的 check」——测试/build 退出码/lint/截图对比，让循环自闭合而不是人当 verifier。headless 模式 `claude -p` + `--allowedTools` 支持脚本化 fan-out（批量迁移每文件一个调用）。

【坑】① 把「必须发生的事」写进 CLAUDE.md 而不是 hook——advisory 规则必然偶发失守；② 上下文塞满后规则遵从率下降，需 `/clear` 与 subagent 隔离探索；③ checkpoint 只跟踪 Claude 编辑工具的改动，bash 改的文件不在回滚范围。

</details>

<details>
<summary><b>沙箱技术层：Firecracker / gVisor / Seatbelt / E2B 的隔离强度谱</b></summary>

【隔离强度谱】从弱到强：

| 层 | 机制 | 边界 | 代表 |
|---|---|---|---|
| process sandbox | syscall/文件/网络策略过滤 | 同 kernel 同 userland | macOS Seatbelt（Claude Code /sandbox）|
| container | namespace + cgroup + seccomp | 共享 host kernel（kernel 0-day 即逃逸） | docker（OpenHands/SWE-bench）|
| user-space kernel | 拦截 syscall 转发给 Go 实现的内核 | 应用与 host kernel 之间多一层 | gVisor（GKE sandbox）|
| microVM | KVM 硬件虚拟化，独立 guest kernel | 硬件级 | Firecracker（E2B、AWS Lambda）|

选型逻辑：跑**自己 repo 的测试** → container 够用且最省事；跑**不可信/模型生成的任意代码、多租户** → microVM。

【Firecracker 关键数字】面向 serverless 设计的极简 VMM：裁掉 BIOS/PCI/大部分设备模型 → 攻击面小；boot ≤125ms、每 VM 内存开销 <5MiB → 可高密度部署，接近容器的成本拿到 VM 的隔离。

【E2B 实现机制】

```python
from e2b_code_interpreter import Sandbox

sbx = Sandbox(template="my-env", timeout=300)   # timeout 到期自动回收
sbx.commands.run("pip install -r requirements.txt")
res = sbx.run_code("import pandas as pd; ...")   # stdout/stderr/rich 输出结构化返回
sbx.files.write("/home/user/patch.diff", diff)   # 文件系统 API 双向传输
```

- **模板系统**：用户写 Dockerfile 定义环境 → E2B 构建成 microVM rootfs + 内存快照；创建 sandbox = 从 snapshot 恢复（整机状态含运行中进程，~150ms），而不是冷启动。
- 生命周期：sandbox 有硬 timeout，超时自动销毁——这同时是资源回收和「agent 跑飞」的兜底。
- 对 agent harness 的意义：把「环境准备」从每 run 的 docker build 变成快照恢复，百 ms 级拿到全新隔离环境，才能支撑大规模并行 rollout（eval、RL 采样）。

【坑】① snapshot 里的依赖会过期，模板要有重建流水线；② microVM 内默认无 GPU、无 docker-in-docker，需求特殊要绕；③ 网络 egress 若不设白名单，「强隔离」只保护宿主、不防数据外泄。

</details>

<details>
<summary><b>SWE-bench 官方 harness：三层镜像 + 双向测试判定</b></summary>

【三层 docker 镜像（核心设计）】为了「可复现 + 可复用」把镜像拆三层：

```text
base image      OS + 语言运行时（ubuntu + python/conda）    → 全局一份
env image       某 repo@某版本区间的历史依赖环境             → 按 repo×version 复用
instance image  checkout 到该 task 的 base_commit 并安装 repo → 每 task 一个
```

难点在 env 层：要在今天装出 2019 年的 django/sympy 依赖闭包，每个 repo×version 一份手工维护的安装 spec（conda env + pip 固定版本）。这层是 SWE-bench 最大的工程成本，也是它可信的原因。

【评测流程】

```text
python -m swebench.harness.run_evaluation \
  --dataset_name princeton-nlp/SWE-bench_Verified \
  --predictions_path preds.jsonl --max_workers 8 --run_id my_run
# 每个 instance：
1. 起 instance 容器
2. git apply model_patch（失败则降级 patch 命令带 fuzz 重试）
3. 应用官方 test patch（加入新测试），跑指定测试命令
4. 解析测试日志 → 每个测试 PASS/FAIL
5. 判定 resolved = FAIL_TO_PASS 全部转绿（修好了）
              && PASS_TO_PASS 全部仍绿（没改坏别的）
```

双向判定是关键：只看 F2P 会奖励「把测试改到通过」式作弊，P2P 是回归保险。

【资源与运维】推荐 x86_64、120GB 磁盘、16GB RAM、8 核；`max_workers` 并行起容器；云上有 sb-cli/Modal 方案。

【坑】① flaky test 造成同一 patch 两次评测结果不同——报告分数要说明重跑策略；② arm64/Mac 上部分镜像构建失败，官方以 x86_64 为准；③ patch 只要 apply 成功就算进入评测，diff 格式错误直接 0 分——生成端要先本地 `git apply --check`；④ 磁盘会被镜像吃满，需 `--cache_level` 控制保留哪层。

</details>

## 6. 自学资料

按优先级排序：

1. [SWE-agent: Agent-Computer Interfaces Enable Automated Software Engineering](https://arxiv.org/abs/2405.15793) — ACI 论文；重点读接口 ablation（lint 守卫、窗口大小、搜索摘要各值多少分），是「接口即能力」的最强证据 · 40 min
2. [Harness engineering: leveraging Codex in an agent-first world](https://openai.com/index/harness-engineering/) — OpenAI 官方：AGENTS.md 是地图不是说明书、用 lint/CI 机械化执行 taste、repository legibility 工程化 · 25 min
3. [Claude Code: Best practices](https://code.claude.com/docs/en/best-practices) — 官方 docs：verify-first 循环、CLAUDE.md 取舍表、hooks vs advisory、worktree 并行、headless fan-out · 30 min
4. [OpenHands: An Open Platform for AI Software Developers as Generalist Agents](https://arxiv.org/abs/2407.16741) — event stream 架构与 runtime 设计（ICLR 2025）；读 §2 架构 + AgentSkills 部分即可 · 30 min
5. [Codex cloud environments 文档](https://developers.openai.com/codex/cloud/environments) — 两阶段生命周期、setup/maintenance script、secrets 只在 setup 可见、无网默认值的官方定义 · 10 min
6. [SWE-bench 官方 repo](https://github.com/swe-bench/SWE-bench) — 看 `swebench/harness/` 的三层镜像构建与 run_evaluation 入口，自建 eval 的直接模板 · 20 min
7. [Firecracker vs QEMU（E2B 官方博客）](https://e2b.dev/blog/firecracker-vs-qemu) — 为什么 agent 沙箱选 microVM：boot 时间、内存开销、攻击面对比 · 15 min
8. [openai/codex-universal](https://github.com/openai/codex-universal) — universal 镜像的参考 Dockerfile 与 CODEX_ENV_* 版本 pin 机制，可本地拉起复现 · 5 min
9. [E2B docs](https://e2b.dev/docs) — 托管沙箱 SDK：模板→snapshot→sandbox 生命周期，看 quickstart 与 sandbox lifecycle 两页 · 10 min
