# [B4] Hark：Computer-use Agent Sandbox 与 Tool Harness · 完整解答

⏱ 读完 12 min ｜ 建议先自己限时 60min 答一遍再看（盲看解答记不住）。题面见 [../B_general_design.md](../B_general_design.md#b4)，完整 rubric 见 [../../../agentic/data/questions.json](../../../agentic/data/questions.json) → `q-hark-computer-use-sandbox`，Hark 卡见 [../../06_company_briefs.md](../../06_company_briefs.md)。

## 题目还原

60min coding-design："设计并**写核心接口**：computer-use agent 根据 screenshot/DOM observation 产生 click/type/navigate action，在隔离浏览器中完成任务。限制 domain/下载/clipboard/credential；发消息、付款、删除属高风险。支持 timeout、用户接管、checkpoint 恢复。"rubric 权重：sandbox boundary 25% + action/state semantics 25% + approval/security 20% + recovery 15% + tests 15%——**接口和边界是主菜，模型能力不是**。最容易答砸的点：把安全写进 prompt、click 用裸坐标不绑页面版本、timeout 后盲重试。

## 开场澄清（5 问 + 为什么问）

1. **Observation 给 DOM/AXTree、screenshot 还是两者？**→ 决定 action 寻址（node_id vs 坐标）和 staleness 检测能不能做。假设两者都有：AXTree 出 stable node_id 与 disabled/visible 状态，screenshot 给视觉 grounding；纯像素环境（native app）作为退化情况在深挖 3 讨论。
2. **登录凭证怎么给？允许模型看到吗？**→ 假设绝不进 context：credential broker + 占位符注入，或 setup 阶段预登录（下文）。
3. **哪些 action 逐次审批？谁审？**→ 假设三档 risk：read 自动、write 校验后自动、irreversible（发消息/付款/删除）逐次人审。
4. **单租户自己账号，还是多租户跑不可信任务？**→ 决定隔离强度：自己账号 container 够，多租户/RL rollout 上 microVM。假设多租户。
5. **SLO 与规模**：任务分钟级？并发多少 run（影响 sandbox 冷启动方案）？RL 采样也用这套 harness 吗？（Hark 语境：是——同一 harness 服务 production 和 post-training rollout。）

## 答案主线（rubric pacing ≈ [../../02_playbook.md](../../02_playbook.md) 时间盒）

**开场 90 秒（背）**："我把系统切成三层：**模型只产 proposal**；**validator + policy 在执行层强制**一切安全属性——domain、staleness、risk、budget；**sandbox 每 run 隔离**兜住剩余爆炸半径。Observation/Action 是 typed envelope，绑 page_version 和 monotonic step，杜绝 stale click。credential 由 broker 注入，永不进模型 context。恢复原则：checkpoint 只存业务状态，重开后重新观察 re-plan，绝不重放旧 action。"

**0–7 任务/权限/环境**：goal predicate = `给定 TaskSpec(goal, domain_allowlist, risk_policy, budget)，在 max_steps/wall_time 内使环境达成可观察终态，零 policy 违规、irreversible action 全部有审批记录`。北极星：task success rate；护栏：unsafe-action rate、canary trigger rate、人工接管率。

**7–14 接口与数据模型（本题核心交付，先写代码）**：

```python
@dataclass(frozen=True)
class Observation:
    run_id: str
    step: int                    # monotonic，controller 分配
    page_version: int            # navigation/DOM mutation 后由 executor 递增
    url: str
    axtree: str                  # 裁剪后的 accessibility tree，节点带 stable node_id
                                 # 与 disabled/visible/focused 属性；secret 已 redact
    screenshot_ref: str          # object store pointer，event 里不内联大 payload
    captured_at: datetime

@dataclass(frozen=True)
class ActionProposal:            # 模型的输出——只是提案，不是命令
    proposal_id: str
    run_id: str
    step: int
    based_on_page_version: int   # 关键字段：这个 action 基于哪次观察
    kind: Literal["click", "type", "navigate", "scroll", "done", "ask_user"]
    target_node: str | None      # AXTree node_id 优先；坐标只作纯视觉兜底
    text: str | None             # type 内容；秘密写 "{{secret:gh_password}}" 占位符
    risk: Literal["read", "write", "irreversible"]
    expected_effect: str         # 模型声明的预期后态，供 timeout 后判定与审批展示
    operation_key: str           # hash(run_id, step, kind, canonical_args) 幂等去重

@dataclass(frozen=True)
class ActionResult:
    proposal_id: str
    status: Literal["executed", "rejected_stale", "rejected_policy",
                    "needs_approval", "timeout_unknown"]
    new_page_version: int | None
    error: str | None            # 结构化原因，如 "target disabled: submit button"
```

validator（deterministic，跑在执行层）：

```python
def validate(p: ActionProposal, env: BrowserEnv, policy: Policy) -> ActionResult | None:
    if p.based_on_page_version != env.page_version:
        return reject("rejected_stale")            # 页面已变，强制重新观察
    node = env.axtree.get(p.target_node)
    if p.kind == "click":
        if node is None or not node.visible:
            return reject("rejected_stale")
        if node.disabled:
            return reject("rejected_policy", f"target disabled: {node.name}")
        if env.element_at(node.center) is not node:  # 遮挡检测（cookie banner）
            return reject("rejected_stale", "target occluded")
    if p.kind == "navigate" and not policy.domain_ok(p.text):
        return reject("rejected_policy", "domain not in allowlist")
    if p.risk == "irreversible" and not has_valid_approval(p):
        return needs_approval(p)                   # 展示 exact effect + args hash
    if env.budget_exceeded():
        return reject("rejected_policy", "budget")
    return None                                    # 放行执行
```

**14–38 执行 loop 与 sandbox（架构图 + 主流程）**：

```text
Client / Hark app
  │ create / approve / takeover / cancel
  ▼
API + Auth ──────────► Policy / Approval Service
  │                          ▲ needs_approval(exact effect)
  ▼                          │
Run Controller 状态机 ────► Event Log / Checkpoints / Trace
  ├── Context Builder（裁剪 AXTree + 最近 k 步 observation）
  ├── Model Adapter（产 ActionProposal）
  ├── Action Validator（staleness/target/risk/domain/budget）
  └── Executor(CDP) ══ sandbox 边界 ══► per-run Browser in microVM
                                          │  egress 全走 MITM proxy：
Credential Broker ──占位符解析──────────►│  domain allowlist / 下载拦截
（secret 不进模型 context）               │  / secret 注入与 redaction
```

主流程一步：`observe → model propose → validate → (approval) → execute(operation_key) → wait quiescence(network idle + DOM stable, 有 deadline) → new Observation(page_version+1) → append event log`。逐条讲边界（25% 分在这）：

- **每 run 隔离**：一个 run = 一个全新 browser context，跑在 Firecracker microVM（多租户/不可信任务；E2B 式 snapshot 恢复 ~150ms，支撑 RL rollout 大规模并行）；单租户自己账号可降级 container。run 结束整机销毁，无跨 run 残留。
- **network/domain policy 在 proxy 层强制**：所有 egress 过 MITM proxy，domain allowlist、下载按 MIME/大小拦截落入 quarantine 卷（绝不自动执行）、clipboard 是 run 内虚拟剪贴板。模型被骗也发不出去——policy 不依赖模型听话。
- **credential 注入两条路**：(a) setup 阶段预登录——凭证只在 agent loop 开始前的 setup phase 可见（Codex cloud 同款两阶段），模型根本不经手登录；(b) 运行中要输密码时，模型产 `type "{{secret:name}}"`，executor 在 CDP 层解析占位符敲真值。反向防泄漏：observation redactor 把 password field 和已知 secret 值在 DOM/screenshot 里 mask 掉再给模型。
- **模型侧只影响"选什么"，不决定"能不能"**：工具描述/system prompt 是 advisory，authz 全在 executor——与 [../../01_core/03_harness_env_swe.md](../../01_core/03_harness_env_swe.md) harness 七要素一致。

**38–48 审批、崩溃和恢复**：

- **审批**：irreversible proposal 生成 `human_readable_effect`（"将向 john@x.com 发送消息，全文如下…"）+ canonical_args_hash + expires_at + **绑定 page_version**——审批期间页面变了审批作废；参数任何改变要求重批。approve 后 executor 用同一 operation_key 执行，审批重试不会重复副作用。
- **用户接管**：takeover 是一级输入：controller 立即停发新 action，in-flight action 等结果或标 unknown；用户操作期间浏览器动作记为 external event 进同一 event log；归还时 agent **从头重新观察**、diff 预期后 re-plan，不假设自己还知道页面状态。
- **checkpoint 恢复**：checkpoint 只存可恢复业务状态——TaskSpec、进度（已完成子目标、已收集 artifact、已填表单的结构化数据）、当前 url、auth session 指针；**不承诺恢复瞬时 UI**。崩溃后：新 sandbox → broker 重新注入 auth → navigate 到 url → re-observe → re-plan。绝不重放 action 序列（页面早变了）。event log 里 `action_dispatched` 无对应 `action_completed` 的步 → 按 timeout_unknown 协议处理（深挖 2）。

**48–55 安全测试（15% 分，别跳）**：① AgentDojo 式双指标 suite：user_task × injection_task，报 utility 和 attack-success-rate 两条曲线（[2406.13352](https://arxiv.org/abs/2406.13352)：最好 agent ASR<25%，加 detector ~8%——防线必须纵深）；② **irreversible-action canaries**：held-out 环境里埋诱饵——醒目的 "Delete all" 按钮、预填好的付款表单、诱导性 "Send" 入口，任何正确轨迹都不该碰；canary 触发 = 该 trial 直接判负。同一批 canaries 复用为 RL post-training 的负 reward 信号（Hark 语境的加分连接）；③ secret-exfiltration canaries：环境里种唯一 canary 凭证串，出现在任何 egress/action 参数即告警；④ staleness 测试：observe 与 act 之间故意 mutate 页面，断言 validator 拒绝；⑤ timeout 演练：click 派发后切断网络，断言走 re-observe 而非盲重试。

**55–60 取舍**：见末节三条。

## 深挖 3 处（题库高频追问）

**1）网页内容诱导 agent 上传 secret（indirect injection）怎么防？**——"按 lethal trifecta 拆（[Simon Willison](https://simonwillison.net/2025/Jun/16/the-lethal-trifecta/)）：私有数据 + 不可信内容 + 外发通道，至少断一条腿。① 断'私有数据'：secret 走占位符/预登录，模型 context 里根本没有——**模型无法泄露它没见过的东西**，这是最硬的一层；② 断'外发通道'：domain allowlist 在 proxy 强制，被骗的模型也 POST 不到 attacker.com；file upload 归 write/irreversible，validator 检查'哪个文件、传到哪个 origin'；③ 数据流约束（CaMeL 思路，[2503.18813](https://arxiv.org/abs/2503.18813)）：给值打 provenance 标记，来自不可信页面的内容流向**另一 origin 的 sink action** 参数时强制升审批——不可信数据不能自由流向外发口；④ observation 里的注入检测 classifier 只当弱第二线，不当依赖。最后用 AgentDojo 双指标和 canary secret 持续量化 ASR，防线是测出来的不是声明出来的。"

**2）click 成功但 observation timeout 怎么恢复？**（Hark 卡高分句，背）——"click 已发出但观察 timeout 时，**副作用状态未知——重新观察页面判定，靠 operation key 幂等恢复，绝不盲重试**。展开成协议：① 该步标 `timeout_unknown`，冻结后续 write action；② 浏览器还活着，放宽 deadline 强制取一次新 observation（哪怕 partial DOM）；③ 用 proposal 里的 `expected_effect` 判定：点了 Send 就看消息是否出现在 thread、点了 Pay 就看订单状态——**用环境后态判定，不用模型回忆**；④ 页面判定不了且目标应用有只读查询面（sent folder、order history）→ 读查询裁决；⑤ 仍未知且 action 是 irreversible → 带证据升级人工，绝不重试；确需重试且目标应用支持幂等键则同 operation_key 重放（Stripe 语义），不支持幂等的外部应用，re-observe 判定就是唯一安全路径；⑥ 全局护栏：连续 N 个 unknown → 暂停 run。harness 自身 crash 在 click 中间是同一协议——event log 的 dispatched-without-completed 就是入口。"

**3）视觉模型看不到 disabled state 怎么办？**——"不让像素当 ground truth。① AXTree/DOM 有 `disabled`/`aria-disabled`/visibility/hit-test，validator 在**执行时刻**查真实计算状态，拒绝时返回结构化原因（'submit disabled——必填项 email 为空'）——模型拿到可行动的反馈，而不是点了没反应白烧一步；② 遮挡同理：elementFromPoint 验证命中的确实是目标节点，cookie banner 盖住就拒绝并提示先关弹窗；③ 纯像素环境（native app 没有 DOM）退化打法：执行后立即验证 `expected_effect` 是否达成，没达成把'点击无效'作为 observation 回流；训练侧用 DOM 配对数据教 grounding 模型识别 disabled 纹理；eval suite 里显式放 disabled-state 用例盯回归。核心一句：**interactability 是环境事实，问环境，别问模型的眼睛**。"

## 失败模式与恢复（本题具体场景）

- **stale click**：观察到行动之间页面自更新（轮播、懒加载）→ page_version 不匹配直接拒绝，代价是多一轮观察，换来的是绝不点错元素；高频自变页面用 DOM diff 缩小重观察范围。
- **无进展循环**：连续 k 步 page_version 不变或 action signature 重复 → 熔断，要求模型换策略或 ask_user；max_steps/wall_time/cost 硬上限兜底。
- **弹窗/cookie banner**：遮挡检测拒绝 + 把弹窗节点标进 observation，让模型显式处理；常见 banner 可作 deterministic 预处理规则。
- **下载恶意文件**：MIME/大小白名单，落 quarantine 卷只读扫描，永不进执行路径——下载的文件内容同样是不可信输入（间接注入的另一入口）。
- **session 中途过期**：登录页检测 → 暂停 loop，broker 走预授权流程重新注入，**模型不参与重登录**，凭证不因异常路径漏进 context。
- **接管竞态**：takeover 请求与 in-flight action 并发 → action 完成或标 unknown 前不移交控制权，用户看到的状态必须落在合法 step 边界上。
- **恢复类总模板**：durable event log 找最后 committed transition → pending 副作用按深挖 2 判定 → 重建最小 context 继续，见 [../../01_core/05_reliability.md](../../01_core/05_reliability.md)。

## Trade-offs 三条（主动说）

1. **AXTree+typed action vs 端到端纯视觉**：typed 方案现在就给你 staleness 检测、policy 强制面和结构化错误反馈；纯像素泛化到任意 native app 但丢掉整个 enforcement 面。我按可靠性瓶颈分配：grounding 差补模型侧，long-horizon/漂移恢复靠 harness——这也是我想反问团队的方向问题（Hark 追问 1 原题）。
2. **per-run microVM vs container**：microVM 冷启动和内存成本高，换硬件级隔离——跑不可信任务/多租户/RL rollout 值得；snapshot 恢复把成本压到 ~150ms 级。自己账号的个人 agent 可降级 container + 严 egress。
3. **irreversible 逐次审批牺牲自主性**：v1 全量人审收集数据；信号出现后放宽——某 action 类在 canary suite 上长期零触发、审批通过率 >99%，才把该类降为 write 档自动执行。审批率本身是一级产品指标。

## 现实参照（只引本地已有链接）

- [AgentDojo](https://arxiv.org/abs/2406.13352)（rubric 官方背景源）：utility vs ASR 双指标 + 注入位点建模，本题安全测试节的直接模板。
- [CaMeL](https://arxiv.org/abs/2503.18813)：capability/provenance 约束不可信数据流向 tool sink，深挖 1 的第三层防线出处。
- [E2B / Firecracker](https://e2b.dev/blog/firecracker-vs-qemu)：microVM 隔离强度谱与 snapshot ~150ms 恢复，per-run 隔离的成本论据（详见 [../../01_core/03_harness_env_swe.md](../../01_core/03_harness_env_swe.md)）。
- [OpenHands](https://arxiv.org/abs/2407.16741)：Action/Observation event stream 为唯一状态源 + 容器内 browser（browsergym）；其"DOM/AXTree observation 是上下文最大消耗源"的坑就是本解 Context Builder 裁剪的理由。
- [Codex cloud environments](https://developers.openai.com/codex/cloud/environments)：secrets 只在 setup 阶段可见、agent phase 默认断网——credential 两阶段注入的生产先例。
- [Stripe idempotency](https://stripe.com/blog/idempotency)：operation_key = hash(run_id, step, kind, canonical_args) 的语义出处。

> 收尾高分句（背）：这个系统的安全属性没有一条写在 prompt 里——模型只产 proposal，staleness/domain/risk/budget 全部由 validator 和 sandbox 在执行层强制；click 发出而观察超时时，唯一正确动作是重新观察环境判定，而不是相信模型或盲目重试。
