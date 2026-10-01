# Cost / Latency 工程

⏱ 骨架 7 min ｜ 含深潜与资料 35 min ｜ 面试前只看 ⭐⭐⭐ 部分

## 30 秒版本（3 句话）

1. Agent 成本由重复 resend 的 history 主导（N 轮循环 input 累积近似 $O(N^2)$），第一杠杆是 prompt caching：前缀字节级稳定（渲染顺序 `tools→system→messages` 固定，breakpoint 前任何 byte 变化使其后全失效），Anthropic 现行价：读 0.1×、5min 写 1.25×、1h 写 2×，命中即省 ~90% input 成本。
2. 第二杠杆是模型分级 + batch：轻量分诊器把简单请求给小模型、大模型兜底（RouteLLM ICLR'25：14% 流量给强模型即保 95% GPT-4 质量、省 85% 成本）；一切不需要人在等的调用走 Batch API 直接 -50%。
3. 延迟拆成 TTFT（交互体验，目标 <500ms 级）和 TPOT（流式吞吐，人读速 20–50ms/token 即够）分别归因；工程上用逐层 timeout 预算（SLA 自顶向下递减）+ 有界并行（$cost \le K \cdot B \cdot p$）同时给尾延迟和账单封顶。

## 核心概念 ⭐⭐⭐

单次请求成本：$cost = (n_{in} - n_{cached})\,p_{in} + n_{cached}\,p_{cache} + n_{out}\,p_{out}$，其中 $p_{cache} \approx 0.1\,p_{in}$（Anthropic，2026-07 文档核实）。

| 概念 | 要点 | 面试一句话 |
|---|---|---|
| Caching 前缀规则 | 严格前缀匹配，渲染顺序 `tools→system→messages`；breakpoint 之前任何 byte 变化使其后全部失效。设计：system 冻结（时间戳/用户名/模式开关移出）、tool 列表确定性序列化（按名排序）、易变内容放最后 | 「caching 是 prompt 构建层的架构约束，先保证前缀稳定，打标记只是收尾」 |
| Breakpoint / TTL | 每请求 ≤4 个 `cache_control` breakpoint，打在"稳定前缀的最后一个 block"（多轮：最新 turn 尾部，命中随对话增长累积）；TTL 默认 5min，可选 1h；最小可缓存前缀按模型 512–4k token（2026-07 文档：Opus 4.8/Sonnet 5 为 1024，Haiku 4.5 为 4096），低于阈值静默不写 | 「breakpoint 放在稳定/易变的分界上，不是 prompt 末尾」 |
| 命中经济学 | 读 **0.1×**、5min 写 1.25×、1h 写 2×（相对 base input）。5min TTL 第 2 次请求回本（1.35× vs 2×）；1h 需 ≥3 次才划算。验证：`usage.cache_read_input_tokens` > 0 | 「多轮 loop 里 history 按 0.1× 计价，这是 agent 成本第一杠杆」 |
| 模型分级路由 | 分诊在前：<10ms 轻量分类器/规则按难度路由；cascade 在后：小模型先答、置信度不足升级。agent 内部：summarize/分类/子任务用 Haiku 级，主规划 loop 用 Opus/Sonnet 级 | 「路由的本质是把 frontier token 只花在证明需要它的请求上」 |
| TTFT / TPOT | TTFT = 请求→首 token（排队 + prefill）；TPOT = $(T_{e2e} - TTFT)/(n_{out}-1)$（decode 稳态）。降 TTFT：cache 命中跳过大部分 prefill、prompt 减肥；降感知延迟：streaming + 先吐 plan | 「TTFT 是体验指标、TPOT 是吞吐指标，混进一个 P95 无法归因」 |
| Context 精简 = 成本功能 | history 每留 1k token，之后每一轮都重复付费。手段：tool result 截断 / 大输出 offload 到文件只留路径、清老轮 tool_use（context editing）、compaction 摘要 | 「context 管理首先是省钱功能，其次才是防溢出；ROI = 砍掉 token × 剩余轮数 × p_in」 |
| Batch API | 非交互流量（eval、离线打分、批量抽取）走 batch endpoint：全 token **-50%**，多数 <1h 完成、上限 24h，可与 caching 叠加 | 「凡是没有人在等的调用，默认走 batch」 |
| 有界并行成本上界 | fan-out 前先定 K（最大并发 subagent）和每 agent token 预算 B：$cost \le K \cdot B \cdot p$；multi-agent 系统 token 用量可达单 chat ~15×，无界 fan-out = 账单不可预测。配额在 orchestrator 层强制 | 「先给账单设上界，再谈并行加速」 |
| 逐层 timeout 预算 | SLA 自顶向下递减：60s 请求 → orchestrator 50s → 单 tool call 10s → LLM 首 token deadline 数秒；硬约束：内层 timeout × (1+重试次数) < 外层剩余，否则外层先超时、内层重试白烧钱 | 「timeout 是从父层扣减的预算，不是各层拍脑袋的常数」 |

## 面试常问 3 题 ⭐⭐⭐

### Q1：你的 agent 产品月 API 账单 $50k，两周内砍一半，怎么做？

<details><summary>参考打法</summary>

- 先测量再动手：按 `usage` 四字段拆账（`input_tokens` / `cache_read` / `cache_creation` / `output`），按 feature/route 归因；agent 产品通常 input（history resend）占 70%+，确认后再选杠杆。
- 杠杆 1 caching：审计前缀稳定性——`cache_read == 0` 的请求就是 bug；冻结 system、排序 tools、易变量后移；命中后 history 按 0.1× 计，单项常见 -30~50%。
- 杠杆 2 context 精简：tool result 截断 + 大输出 offload 到文件、老轮清理/compaction；每项都能量化（砍掉 token × 平均剩余轮数 × $p_{in}$）。
- 杠杆 3 路由 + batch：分诊小模型接住简单请求（RouteLLM：14% 给强模型保 95% 质量），eval/离线流量全转 batch -50%。
- 讲清顺序与风险：caching/batch 零质量风险先上；路由有质量风险——eval 集回归 + 灰度，盯质量指标不只盯账单。

</details>

> 高分句：「我会先把账单按 input / cache_read / output 拆开归因——agent 产品十有八九是重复 resend 的 history 在烧钱，所以 caching 和 context 精简排在换模型之前。」

### Q2：用户抱怨 agent 响应太慢，怎么系统性降延迟？

<details><summary>参考打法</summary>

- 先拆指标：TTFT（排队+prefill）vs TPOT（decode）vs E2E ≈ 轮数 × (每轮 TTFT + 生成 + 工具时间)；agent 慢通常是"轮数多"，不是"单 token 慢"。
- 降 TTFT：prompt caching 命中直接跳过大部分 prefill（长 system+tools 收益最大）、prompt 减肥；自托管才谈 chunked prefill / prefill-decode 分离。
- 降感知延迟：streaming 必开、先流出 plan/进度、工具执行期推事件——详见 [streaming.md](streaming.md)。
- 结构性减轮数：一轮并行多个 tool call、合并 round trip（programmatic tool calling）、可并行 tool 并发执行、简单请求路由小模型（TTFT 天然更低）。
- 兜底：逐层 timeout 预算 + 降级路径（超时 → 截断作答 / 降级小模型），让 P99 也有确定性上界。

</details>

> 高分句：「agent 的延迟大头是轮数 × 每轮 TTFT，所以我先减轮数、再用 caching 砍 prefill，最后才轮到推理层优化。」

### Q3：prompt caching 命中率很低，怎么诊断？怎么设计缓存友好的 loop？

<details><summary>参考打法</summary>

- 诊断信号：`usage.cache_read_input_tokens` 持续为 0 → 存在静默失效器；diff 相邻两次请求的渲染字节找差异点。
- 常见元凶：system 里 `datetime.now()`/uuid、`json.dumps` 无 `sort_keys`、每用户不同 tool 集、条件拼接 system 段、会话中途换 model。
- 缓存友好 loop：tools/system/model 会话级冻结；history 只 append 不改写；breakpoint 打在最新 turn 尾部；单 turn 超 ~20 blocks 加中间 breakpoint（lookback 窗口限制）。
- 动态需求的替代：模式切换发消息不动 system（mid-conversation system message / user turn 注入）、动态工具用 append 型 tool search 而非换 tool 列表、子任务换模型走 subagent。
- 经济性校验：写 1.25× → 只请求一次的 prompt 别打 breakpoint；bursty 流量间隔 >5min 才考虑 1h TTL（写 2×，≥3 次回本）。

</details>

> 高分句：「命中率低几乎从不是 API 用法问题，而是 prompt 构建代码里藏着不确定性——diff 两次请求的字节，元凶通常是时间戳或无序序列化。」

## 常见坑 ⭐⭐⭐

- [ ] system prompt 插时间戳/uuid/用户名 → 前缀每请求都变，cache 永不命中；`cache_read == 0` 是第一诊断信号
- [ ] 会话中途增删 tool 或换 model → tools 渲染在前缀最前，整条 cache 报废；动态工具用 append，换模型走 subagent
- [ ] 成本核算只看 `input_tokens`：总 input = input + cache_read + cache_creation，多轮 agent 下 cache_read 占大头，漏算会严重低估流量
- [ ] 全部轮次用旗舰模型：summarize/分类/format 类子任务分诊到小模型基本无质量损失——但先 eval 再全量
- [ ] 各层 timeout 拍同一个数（全 30s）：内层重试必撞外层超时；自顶向下递减、给重试留量，且重试本身也烧钱要计入预算

## 现有系统怎么做

| 系统/方法 | 核心机制一句话 | 适用场景 | 链接 |
|---|---|---|---|
| Anthropic explicit prompt caching | 显式 `cache_control` breakpoint（≤4），严格前缀字节匹配，读 0.1×、写 1.25×/2× | 多轮 agent loop、长 system+tools | [docs](https://platform.claude.com/docs/en/build-with-claude/prompt-caching) |
| OpenAI automatic prompt caching | ≥1024 token 前缀自动缓存（128 token 步进），读 0.5×，无手动 breakpoint | 默认省钱层，零代码改动 | [docs](https://developers.openai.com/api/docs/guides/prompt-caching) |
| RouteLLM（学习型路由） | preference data 训练 win-rate 预测器，$P(\text{strong wins}) > \alpha$ 才给强模型 | 大流量、有历史数据可校准阈值 | [arXiv](https://arxiv.org/abs/2406.18665) |
| 生产简化版路由（规则 + cascade） | 硬规则白名单先分诊，小模型先答、低置信 escalate | 中小规模、无训练数据、快速上线 | 见下方伪码 |
| Batch API（Anthropic / OpenAI） | 异步队列换 **-50%**：提交 JSONL/requests → poll → 取乱序结果，24h SLA | eval 跑批、离线打分、批量抽取 | [Anthropic](https://platform.claude.com/docs/en/build-with-claude/batch-processing) · [OpenAI](https://developers.openai.com/api/docs/guides/batch) |
| TTFT/TPOT 延迟测量（NVIDIA/Databricks 口径） | client 侧流式打点：TTFT = 首 token 到达，TPOT = (E2E−TTFT)/(n_out−1) | 延迟归因、SLA 报表、模型选型 | [NVIDIA](https://developer.nvidia.com/blog/llm-benchmarking-fundamental-concepts/) |
| Context 精简（Anthropic context engineering） | tool result 截断/offload + compaction，context 当有限预算管理 | 长 horizon agent 的成本与质量双保 | [blog](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents) |

<details><summary>Anthropic explicit prompt caching —【技术机制】前缀哈希、breakpoint 语义、成本核算实例</summary>

**数据结构**：server 侧本质是「渲染后 prompt 字节流的前缀哈希 → KV cache（prefill 结果）」的映射，按 (org, model) 隔离。cache key 覆盖从位置 0 到 breakpoint 的全部字节，渲染顺序固定 `tools → system → messages`——所以 tools 的任何变化使一切失效（失效有层级：`tool_choice`/图片/thinking 开关只废 messages 层，system 内容只废 system+messages 层，tools/model 变更全废）。

**处理流程**（每个请求）：
1. 渲染 prompt → 对每个 breakpoint 位置算前缀哈希；
2. 命中：跳过该前缀的 prefill，直接加载 KV cache，按 0.1× 计费（`usage.cache_read_input_tokens`）；
3. 未命中：正常 prefill，并在 breakpoint 处写入 cache，按 1.25×（5min TTL）或 2×（1h）计费（`usage.cache_creation_input_tokens`）；
4. 命中会刷新 TTL（refresh 按读价计）。

**cache 友好的 prompt 布局**（immutable 前缀分层，稳定度递减）：

```text
┌────────────────────────────────────────────┐
│ tools（确定性序列化，按名排序，会话级冻结）      │ ← 永不变
│ system（无时间戳/uuid/用户名/模式开关）         │ ← 永不变
│   ...最后一个 system block ← breakpoint #1    │
│ few-shot / 长文档等会话级共享上下文             │ ← 会话级稳定
│   ...其最后一个 block ← breakpoint #2         │
│ history（只 append 不改写）                   │
│   ...最新 turn 的最后一个 block ← breakpoint #3│ ← 每轮后移
│ 本轮新内容 / 时间戳 / 动态注入                  │ ← 每轮都变，放最后
└────────────────────────────────────────────┘
```

**关键参数**：≤4 breakpoints；TTL 5min（写 1.25×）/1h（写 2×）；读 0.1×；最小可缓存前缀按模型 512–4096 token（低于阈值静默不写、无报错）；breakpoint 向前回看最多 **20 个 content block** 找上次 cache（单 turn >20 blocks 要加中间 breakpoint）。回本公式：5min TTL 两次即回本（1.25+0.1=1.35× < 2×），1h 需 ≥3 次（2+0.2=2.2× < 3×）。

**成本核算实例**（Opus 4.8：input $5/MTok，output $25/MTok）。设 agent 会话：system+tools 8k token，每轮新增 3k（user+tool_result+assistant），共 20 轮，每轮 output 500：

- 20 轮累计发送 input = Σ(8000 + 3000·(n−1)) = **730k token**
- 不命中（每请求全价）：730k × $5/M ≈ **$3.65** input
- 全命中（breakpoint 打在最新 turn 尾部，轮间隔 <5min）：每个 token 写一次 1.25×、之后每轮读 0.1×。唯一 token = 第 20 轮 prompt ≈ 65k → 计费 token 当量 ≈ 65k×1.25 + 665k×0.1 ≈ 148k → **$0.74** input，**省 ~80%**
- 加上 output（10k × $25/M = $0.25）：整段对话 $3.90 → $0.99。轮数越多差距越大（未命中 input 随轮数 $O(N^2)$，命中后近似 $O(N)$）

**失败模式**：① 静默失效器（时间戳/无序 `json.dumps`/条件拼接 system）→ `cache_read == 0`；② 并发 race：cache 在首个响应**开始流式返回后**才可读，N 路并行同前缀请求全付全价——fan-out 前先发 1 个请求、等首 token 再发其余 N−1；③ 只请求一次的 prompt 打 breakpoint = 白付 1.25×；④ compaction/换模型后前缀重置，第一请求冷写。预热技巧：`max_tokens: 0` 请求可只做 prefill 写 cache（不计 output）。

</details>

<details><summary>OpenAI automatic prompt caching —【技术机制】自动最长前缀匹配、prompt_cache_key、与 Anthropic 对照</summary>

**机制**：无需任何 API 改动——server 自动对 ≥1024 token 的 prompt 做「最长已见前缀」匹配，从 1024 起按 128 token 步进。命中部分按 **0.5×** input 价计（读 5 折；GPT-5.6+ 上写入按 1.25× 计，旧模型写入免费）；保留期新模型最低 ~30min（旧模型 5–10min 内存 / 最长 24h extended retention）。命中量在 `usage.prompt_tokens_details.cached_tokens` 里。

**路由问题（工程上真正的坑）**：cache 存在具体推理机器上，OpenAI 按 prompt 前缀哈希做 sticky 路由；高 QPS 下同前缀请求可能被分散到多机、各自冷写。缓解：传 `prompt_cache_key`（如 user id / agent id），把同会话请求固定路由到同一 cache 分片，官方建议每个 key 的请求速率不要超过每分钟 ~15 个请求以维持命中。

**与 Anthropic 的一句话对照**：OpenAI = 自动、粗粒度、5 折、无手动失效控制；Anthropic = 手动 breakpoint、精确控制失效边界、9 折读但写要加价。**共同的架构约束一致：前缀稳定才有一切**——两家的省钱代码写法（冻结 system、排序 tools、易变量后置）完全相同，面试时可以说"caching 策略是 provider 无关的 prompt 布局问题"。

**失败模式**：① 命中率不可控——无法强制写入或 pin 住 cache，突发流量驱逐后静默回落全价；② `cached_tokens` 不看就不知道在烧钱（监控必备）；③ 前缀里混入个性化内容（用户名在 system 开头）→ 跨用户零共享。

</details>

<details><summary>RouteLLM —【技术机制】win-rate 预测器训练、阈值校准、CPT 指标</summary>

**问题形式化**：路由是个二分类问题——给定 query $q$，预测 $P_\theta(\text{strong 赢 weak} \mid q)$，当 $P > \alpha$ 才路由到强模型。$\alpha$ 是唯一运行时旋钮：调高省钱、调低保质量，扫 $\alpha$ 得到 cost-quality 曲线。

**训练数据**：Chatbot Arena 的 ~80k 人类偏好对（哪个模型的回答更好），稀疏且噪声大，所以做数据增强：用 golden-label 数据集（MMLU 等）+ GPT-4 as judge 生成的合成偏好标签扩充。

**四种 router 实现**（GitHub repo 全开源，均训练在 GPT-4 vs Mixtral-8x7B 对上，可迁移到别的模型对）：
1. **Matrix factorization**（推荐）：学 query 与模型的低维嵌入，打分 = 双线性积；
2. **SW ranking**：不训练——按与当前 query 的嵌入相似度加权历史投票，算加权 Elo；
3. **BERT classifier**：偏好数据上微调的 BERT 打分；
4. **Causal LLM classifier**：小 LLM 微调成打分器。

**评估指标**：CPT(x%)——达到强模型 x% 质量所需路由给强模型的流量比例。论文结果：CPT(95%) ≈ 14%，即 14% 流量给 GPT-4 即保住 95% 质量，成本降 ~85%（部分基准 >2× 成本削减）。

```python
# 推理路径（生产形态）
p_win = router.predict(embed(query))       # <10ms, 小模型
model = STRONG if p_win > ALPHA else WEAK  # ALPHA 离线扫曲线定
resp  = call(model, query)
```

**失败模式**：① OOD——流量分布 vs Arena 分布不同，win-rate 预测漂移，$\alpha$ 需在自家 eval 集上重校准；② 阈值随模型版本升级失效（weak 模型变强后曲线整体平移）；③ judge 噪声传染训练标签。**生产落地要点**：路由决策要打 log（query、p_win、chosen、最终质量信号），否则没法回归校准。

</details>

<details><summary>生产简化版路由（规则 + cascade）—【技术机制】决策伪码、escalate 信号、风险控制</summary>

不训练 router 的低成本版本，两个可独立采用的层：**前置分诊**（调用前决定发给谁）和 **cascade**（小模型先答、不行再升级）。

```python
# L0 前置分诊：<1ms 硬规则 → <10ms 轻量分类
def route(req, ctx) -> Model:
    if req.task in {"summarize", "classify", "extract", "format"}:
        return HAIKU                       # 白名单: 结构化子任务小模型足够
    if req.needs_tools or ctx.prior_escalations > 0:
        return OPUS                        # 已升级过的会话不再降级(粘住)
    p_hard = difficulty_clf(embed(req.text))   # 蒸馏分类器/logreg 都行
    return SONNET if p_hard < TAU_EASY else OPUS

# L1 cascade：小模型先答, 置信不足 escalate
def cascade(req):
    r = call(SMALL, req)
    if needs_escalation(r):
        return call(LARGE, req)            # 付两次钱——只对少数流量才划算
    return r

def needs_escalation(r) -> bool:
    return (r.logprob_avg < TAU_CONF        # 生成置信度低
        or r.self_check == "unsure"        # 模型自评(输出末尾附一行 verdict)
        or r.schema_invalid                # 结构化输出解析失败
        or r.tool_error_rate > 0.5)        # 工具调用连续失败
```

**关键参数**：cascade 的经济性条件是 `escalation_rate × (cost_S + cost_L) + (1-rate) × cost_S < cost_L`——escalate 率 <30–40%（且 cost_S ≪ cost_L）时基本稳赚。分诊器延迟必须 ≪ TTFT（<10ms），否则得不偿失。

**与 caching 的交互（易漏）**：cache 按模型隔离，会话中途换模型 = 整条 cache 报废。所以路由决策要在**会话粒度或子任务（subagent）粒度**做，不要在同一会话的轮次间反复横跳；升级过的会话粘在大模型上。

**风险控制**：路由是三杠杆里唯一有质量风险的——上线前 eval 集回归（对照全量大模型基线），灰度放量，监控按 route 分桶的质量指标（thumbs-down 率、重试率、escalate 率）而不只是账单。

</details>

<details><summary>Batch API —【技术机制】提交/poll/取结果流程、限额、与 caching 叠加</summary>

**机制**：把不需要人在等的请求提交进异步队列，provider 用闲时容量处理，换全 token **-50%**。Anthropic：单 batch ≤100k 请求或 256MB，多数 <1h 完成、上限 24h，结果保留 29 天，支持全部 Messages 功能（vision/tools/caching）。OpenAI：JSONL 文件上传，completion window 固定 24h，**独立的 rate limit 池**（不占在线配额——这本身就是价值：跑 eval 不挤兑生产流量）。

```python
# Anthropic 形态（OpenAI 是 files.create + batches.create 的 JSONL 版）
batch = client.messages.batches.create(requests=[
    {"custom_id": f"eval-{i}",
     "params": {"model": "claude-haiku-4-5", "max_tokens": 512,
                "messages": [{"role": "user", "content": p}]}}
    for i, p in enumerate(prompts)])

while client.messages.batches.retrieve(batch.id).processing_status != "ended":
    time.sleep(60)

results = {}
for r in client.messages.batches.results(batch.id):   # 结果乱序返回!
    if r.result.type == "succeeded":
        results[r.custom_id] = r.result.message
    elif r.result.type == "errored":
        ...  # invalid_request → 修了重发; server error → 直接重发
```

**与 caching 叠加**：batch 内所有请求共享同一 system 前缀时打 `cache_control`，折上折（0.5 × 0.1 = 前缀实付 ~5% 全价）——eval 跑批的标准姿势。

**失败模式**：① 结果乱序，必须按 `custom_id` 索引、绝不能按位置对齐；② `expired` 状态的单条要重提交（24h 没排上）；③ 不支持 streaming，也没有进度回调，只能 poll；④ 把交互流量误投 batch = 用户等 1h。**适用判据一句话：凡是没有人在等的调用（eval、离线打分、embedding 预计算、数据清洗），默认走 batch。**

</details>

<details><summary>TTFT / TPOT / E2E —【技术机制】测量伪码、口径坑、感知延迟</summary>

**定义**（NVIDIA/Databricks 口径一致）：TTFT = 请求发出到首 token 到达（含排队 + prefill + 网络）；TPOT = 稳态 decode 每 token 时间；E2E ≈ TTFT + TPOT × (n_out − 1)。吞吐 = 所有并发请求的总 output token/s——吞吐和单请求延迟是 trade-off（batching 提吞吐、抬 TPOT）。

```python
# client 侧流式打点（生产 SDK 中间件形态）
t0 = time.monotonic(); t_first = None; n = 0
async for event in stream:
    if is_content_delta(event):
        if t_first is None:
            t_first = time.monotonic()      # TTFT 断点
        n += count_tokens_in(event)         # 见口径坑①
t_end = time.monotonic()
ttft = t_first - t0
tpot = (t_end - t_first) / max(n - 1, 1)
# 上报: histogram(ttft), histogram(tpot), 按 model/route/prompt长度分桶
```

**口径坑**：① 一个 SSE event ≠ 一个 token（可能打包多个），token 数以响应 `usage.output_tokens` 为准，事件计数只做近似；② TPOT 是均值，掩盖卡顿——要看 ITL（inter-token latency）分布的 P95；③ TTFT 里排队和 prefill 混在一起，归因要拆：cache 命中时 prefill≈0，若 TTFT 仍高就是排队/网络；④ P95 必须按 prompt 长度分桶，否则长 prompt 把整体 P95 拉爆、看不出回归；⑤ thinking 模型"沉默期"计入 TTFT——`display: omitted` 时用户看到长暂停，要用感知口径另算。

**感知延迟 ≠ 测量延迟**：streaming 下用户感知由「首个有意义内容何时出现」决定。工程手段：必开 streaming、先流出 plan/进度行、工具执行期推事件（详见 [streaming.md](streaming.md)）。人的阅读速度 ~200 wpm ≈ 20–50ms/token，TPOT 低于这个阈值后继续优化 decode 对体验无感——钱应该花在 TTFT 和减少轮数上。

</details>

<details><summary>Context 精简 = 成本策略 —【技术机制】截断中间件、compaction 时机、图片降采样</summary>

**为什么是成本功能**：history 里每留 1k token，之后**每一轮**都要重复付费（哪怕 cache 命中也付 0.1×）。ROI = 砍掉 token × 平均剩余轮数 × 有效单价。Anthropic 官方立场（context engineering 博客）：context 是有限预算，追求"最小的高信号 token 集合"。

```python
# ① tool result 截断 + offload 中间件（最高频、最安全的一刀）
MAX_INLINE = 2000  # tokens
def wrap_tool_result(result: str) -> str:
    if count_tokens(result) <= MAX_INLINE:
        return result
    path = save_to_workspace(result)            # 全量落盘, agent 可再 read
    head = truncate_to_tokens(result, 1500)
    return f"{head}\n...[truncated; full output at {path}]"
```

**② 清老轮 tool 内容（context editing）**：Anthropic 有 server 侧 beta（`clear_tool_uses` 策略，清老 tool_result、可连 tool_use 参数一起清）；自己实现则是发请求前把 N 轮以前的 tool_result 替换成占位符。比 compaction 便宜（不用 LLM 调用），先用这个。

**③ compaction 时机**：触发条件用「context 用量阈值」而非固定轮数（Anthropic server 侧 compaction 默认 ~150k token 触发；自实现常取 70–80% 窗口）。机制：老 history → LLM 摘要（保留任务目标、关键决策、未完成项、文件路径），保留最近 K 轮原文。**代价**：摘要本身一次 LLM 调用 + compaction 后 cache 前缀重置（一次冷写）——所以不要太频繁，且摘要用小模型做。

**④ 图片降采样**：图片 token ≈ (宽×高)/750（Anthropic 口径），高分辨率单图可达 ~4.8k token。截图类输入先降到 1080p（计算机操作类任务的性价比点），纯文字截图可更低；不需要视觉保真的管道在 client 侧统一 resize。

**失败模式**：① 截断砍掉了 agent 后面要引用的内容 → 一定配 offload 路径让它能找回；② compaction 摘要丢失约束条件（"不要动 X 文件"）→ 摘要 prompt 里显式要求保留 instruction 类内容；③ 精简与 caching 打架：改写 history（而非 append）会废掉已有 cache——清理/压缩要么在 cache 边界外做，要么接受一次冷写、算清 ROI 再动手。

</details>

## 自学资料

按优先级排序，前 3 条读完即可覆盖面试 80% 的追问：

1. [Anthropic: Prompt caching](https://platform.claude.com/docs/en/build-with-claude/prompt-caching) — 精确规则全集：4 breakpoints、5min/1h TTL、0.1×/1.25×/2× 倍率、按模型最小长度、失效层级表 · 25 min
2. [Anthropic: Effective context engineering for AI agents](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents) — compaction/JIT retrieval/note-taking 的官方论证，"context 是有限预算"的出处 · 25 min
3. [RouteLLM: Learning to Route LLMs with Preference Data](https://arxiv.org/abs/2406.18665) — ICLR'25，路由问题形式化 + 四种 router 训练法 + CPT 指标，路由话题的唯一必读论文 · 40 min
4. [Databricks: LLM Inference Performance Engineering](https://www.databricks.com/blog/llm-inference-performance-engineering-best-practices) — TTFT/TPOT 定义与吞吐-延迟 trade-off，推理层延迟直觉的最佳单篇 · 30 min
5. [OpenAI: Prompt caching guide](https://developers.openai.com/api/docs/guides/prompt-caching) — 自动缓存对照面：≥1024 token、读 0.5×、`prompt_cache_key` 路由 · 15 min
6. [NVIDIA: LLM Inference Benchmarking — Fundamental Concepts](https://developer.nvidia.com/blog/llm-benchmarking-fundamental-concepts/) — 测量口径细节（ITL vs TPOT、归一化坑），写 SLA 报表前读 · 20 min
7. [lm-sys/RouteLLM (GitHub)](https://github.com/lm-sys/RouteLLM) — 四种 router 的开源实现 + 阈值校准脚本，想跑通再看 · 20 min
8. [Anthropic: Batch processing](https://platform.claude.com/docs/en/build-with-claude/batch-processing) — -50%、100k/256MB 限额、poll 模式、与 caching 叠加 · 10 min
9. [OpenAI: Batch API](https://developers.openai.com/api/docs/guides/batch) — JSONL 提交格式、24h window、独立 rate limit 池 · 10 min

相关：[scaling.md](scaling.md)（队列/背压是并发上界的另一半）｜ [streaming.md](streaming.md)（感知延迟）｜ [01_core](../01_core/README.md)（loop/context 基础）｜ v1 系统设计剧本：[SYSTEM_DESIGN_PLAYBOOK](../../agentic/content/SYSTEM_DESIGN_PLAYBOOK.md)
