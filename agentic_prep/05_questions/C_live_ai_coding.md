# C 类 · Live Coding / AI-assisted Coding 实操题

⏱ 约 12 分钟读完（可见部分） ｜ 面试前只看 ⭐⭐⭐ 部分

现场脚本（AI-coding 轮怎么开场、怎么 narration）见 [../02_playbook.md](../02_playbook.md)。练手平台：hellointerview 有专门 "AI-Enabled Coding" mock 赛道（12 题，评分= Prompts / Code review / 最终代码质量三维）。

## Anthropic（7/22）

### [C1] ⭐⭐⭐ Anthropic Agent Coding 轮：手搭 Claude agent loop（tool use 回答股票价格）<a id="c1"></a>
- 来源: 1p3a 三帖交叉 + Telegram 镜像 + Qbank "Agents Coding: LLM Tool Use"（medium 频率，last 2026-06-29） ｜ 置信度: ✅ ｜ 公司/轮次: Anthropic · SWE/RE 技术店面（四选一 track）55min Colab · 2026 Q2 频率上升
- 考察点: tool schema 定义、tool_use/tool_result 协议、while 循环与终止、错误处理与防幻觉
<details><summary>题面 + 参考打法 + 高频追问</summary>

**题面**：实现 Claude agent loop——定义 tools、解析模型 tool call、执行工具回传结果、循环到最终回答。具体版本：给一个股票价格查询工具（`get_stock_price(symbol)`），让 agent 多步调用回答用户问题。环境：Google Colab + Anthropic API，共享屏幕，**可查语言文档和网页、禁 AI 助手**。官方 blurb："写出能编译运行的代码，并根据测试失败迭代"。

**参考打法**：
- 协议肌肉记忆：`stop_reason == "tool_use"` 分支 → 保留完整 assistant content → 追加匹配 `tool_use_id` 的 `tool_result` → 循环；同轮多个 tool_use 必须**一次性**全部回传
- while 循环 + max_steps + token 预算保护；工具异常转 `is_error: true` 回传让模型自修复，不泄异常栈
- 只读工具可并行（有界线程池）；副作用工具禁自动并行
- 防幻觉：system prompt 强制引用 tool 结果、final answer 校验有 tool 调用发生
- 手写模板先背熟：[../01_core/01_loop_and_tools.md](../01_core/01_loop_and_tools.md)

**变体**：同菜单另有 "Prompting/Engineering with LLMs"（Colab，prompt 迭代 + 为输出建简单 evaluation，不含 tool-use）——同一套准备覆盖。

**高频追问**：prompt 设计 ｜ 防幻觉（强制引用 tool 结果） ｜ 并行 tool call 怎么做

完整 rubric: [../../agentic/data/questions.json](../../agentic/data/questions.json) → `q-anthropic-stock-agent`

</details>

→ **完整解答：[solutions/C1_stock_agent_loop.md](solutions/C1_stock_agent_loop.md)**

### [C2] ⭐⭐⭐ Anthropic：Durable Function Call Cache（确定性 key + WAL 崩溃恢复）<a id="c2"></a>
- 来源: hack2hire 完整题面（freq 8/10，2026-07 活跃）+ 1p3a Qbank "Coding Q2 LRU Cache Durability" 独立收录 ｜ 置信度: ✅ ｜ 公司/轮次: Anthropic · onsite coding 60min · 2026-06~07
- 考察点: 规范化序列化与哈希 key、append-only WAL replay、LRU recency 重建、容错反序列化
<details><summary>题面 + 参考打法 + 高频追问</summary>

**题面**：给部分实现的 Python `FunctionCallCache`（LRU 已写好）。**Part 1** `create_cache_key`：确定性可哈希 key——排序 kwargs、递归规范化嵌套 dict、函数名+args+规范化 kwargs 组成不可变容器。**Part 2**（durability）：cache 操作写 append-only WAL；重启 replay 同时重建值和 LRU recency（已有 key 的位置更新要显式 delete-and-reinsert——标准 replay 常漏）；优雅跳过尾部损坏/截断记录，不让启动失败。

**参考打法**：
- key 等价性：`inspect.signature.bind` + `apply_defaults` 让 positional/keyword/default 同一 key
- WAL record：version + operation + payload + checksum；replay 在第一条坏记录停止（官方提示：try/except 跳过畸形尾部）
- put 和 hit（touch）都追加记录，否则 recency 恢复不完整
- 官方 follow-up 全清单：不可 JSON 序列化参数（自定义类）｜ 序列化字符串 vs 值元组 key ｜ 函数签名/源码变化的失效 ｜ 线程安全 ｜ 多进程并发 ｜ 批量写降 I/O ｜ checkpoint 加速恢复 ｜ log compaction

**高频追问**：pickle 为什么不适合不可信文件？ ｜ 如何演进 key encoding 不静默错误命中？

完整 rubric: [../../agentic/data/questions.json](../../agentic/data/questions.json) → `q-anthropic-durable-cache`

</details>

→ **完整解答：[solutions/C2_durable_cache.md](solutions/C2_durable_cache.md)**

### [C3] ⭐⭐⭐ Anthropic 2026 新增 onsite AI-assisted coding 轮（提供 Claude Code CLI）<a id="c3"></a>
- 来源: 1p3a VO 结构帖（5+ 报告）+ Telegram 镜像多例 ｜ 置信度: ✅ ｜ 公司/轮次: Anthropic · VO coding 轮（部分 loop）· 2026 新增
- 考察点: 驾驭 AI agent 的工作流：任务拆解、给 Claude Code 写 spec、review 生成代码、验证
<details><summary>题面 + 参考打法 + 高频追问</summary>

**形式**：2026 年 Anthropic SWE/RE VO 四轮（coding/SD/project deep dive/culture）中新增的 coding 轮，明确允许并要求"使用 AI 工具编写和审查代码"，现场提供 Claude Code CLI。**对照规则**：店面禁 AI 工具（但可抄网上正当搜到的代码）。VO coding 题为题库题（tokenizer/Bootloader/dedupe 3-part 等），SD 轮为 Prompt Playground / inference API 等。流程硬 gate：技术轮挂了静默取消后续。

**参考打法**：
- 评的不是裸算法，是工作流：先自己读题拆解 → 给 Claude Code 清晰 spec（验收条件、边界）→ review diff → 跑测试验证
- 全程 narration："我让它做 X，因为…；这段我要自己验证，因为…"
- 平时用 Claude Code 做真实项目即最好准备；现场脚本见 [../02_playbook.md](../02_playbook.md)

**高频追问**：为什么接受/拒绝这段 AI 生成的代码？ ｜ 怎么确认它没破坏别处？

</details>

### [C4] ⭐⭐⭐ Anthropic FDE/Applied AI 店面：55 分钟 CodeSignal "build an agent"<a id="c4"></a>
- 来源: 多帖交叉 2026-01~07（含 2026-06 FDE 面经） ｜ 置信度: ✅ ｜ 公司/轮次: Anthropic · FDE/SA-Applied AI/Product Engineer 轨店面 · 2026
- 考察点: 现场从零搭 agent：prompt 优化到特定输出、debug 输出不稳定、边缘案例改进
<details><summary>题面 + 参考打法 + 高频追问</summary>

**形式**：55 分钟 CodeSignal "build an agent"——可能可用 Claude SDK 但**禁 AI 辅助**。实际包含：优化 prompt 达到特定输出、理解模型局限、debug 为什么某些 prompt 输出不稳定、改进 chatbot 边缘案例响应。该轨 OA 是较短的 prompt engineering 测试（非 SWE 4-part ICA）。后续 onsite：dataset analysis（云容量场景：利用率/瓶颈/成本-延迟-可靠性权衡）、project presentation、XFN 协作（含 SQL）、HM（research→生产系统）。

**参考打法**：练"从空白到能跑的 agent"55 分钟节奏：先最小 loop 跑通 → 加 tool → 再调 prompt；输出不稳定的排查顺序 = temperature/采样 → prompt 歧义 → few-shot 锚定 → 结构化输出约束。

**高频追问**：为什么这个 prompt 不稳定？ ｜ 模型做不到 X 时你怎么绕？

</details>

→ **完整解答：[solutions/C4_build_an_agent.md](solutions/C4_build_an_agent.md)**

### [C5] ⭐⭐⭐ Anthropic：为 tool-calling agent 的 API 实现线程安全 rate limiter<a id="c5"></a>
- 来源: 多来源报告（reyzharkov 面经 + Glassdoor 风格总结） ｜ 置信度: ✅ ｜ 公司/轮次: Anthropic · live coding · 2025
- 考察点: 限流算法 + 并发安全 + 分布式扩展 + 降载
<details><summary>题面 + 参考打法 + 高频追问</summary>

**题面**：实现 rate limiter，follow-up 递进：(1) 线程安全（场景：agent 并发高频调外部 API）；(2) 多机分布式限流；(3) sliding window 实现；(4) load shedding。

**参考打法**：token bucket 单机 + lock/原子操作 → 分布式用 Redis Lua 原子脚本或一致性哈希分片 → sliding window log（精确、内存 O(n)）vs sliding window counter（近似、O(1)）的 tradeoff → 降载按优先级丢弃 + 429 with Retry-After。

**相邻题族**（同来源报告）：实时流数据处理（去重/排名/聚合/故障检测）、sequence packing for LLM training（变长序列打包 max_length，first-fit decreasing 贪心）、tokenization 引擎、duplicate file finder、log processing。Glassdoor 总结 Anthropic coding 风格："software development assignment with a bit of leetcode baked in"。

**高频追问**：突发流量 vs 平均速率怎么同时限？ ｜ 时钟漂移对分布式窗口的影响？

</details>

→ **完整解答：[solutions/C5_rate_limiter.md](solutions/C5_rate_limiter.md)**

### [C6] ⭐⭐⭐ Anthropic RL Fundamentals 轮：debug GRPO training loop（3 个埋点 bug）<a id="c6"></a>
- 来源: 1p3a 三帖（2026-05，3+ 报告）+ prachub 评分维度页 ｜ 置信度: ✅ ｜ 公司/轮次: Anthropic · RE 店面四选一 track · 2026 Q2 新增
- 考察点: GRPO 实现级理解、系统性 debug、区分"设计内偏差"与真 bug 的实验设计
<details><summary>题面 + 参考打法 + 高频追问</summary>

**题面**：给简化 GRPO 训练 step 实现，含 3 个埋好的 bug，每个要求给出**检测方法+具体修复**（不能只点名）。常见 bug 池：log-prob 未对齐 autoregressive shift、loss/KL 的 token masking 错、advantage normalization（组内奖励全相同→除零/无信号）、rollout 与 update 的 policy 混用。

**核心追问**：严格 on-policy 下为什么 importance ratio $\exp(\log\pi_\theta - \log\pi_{old}) \neq 1$？要求设计判别实验区分设计内偏差（推理引擎与训练器 forward 路径不同、bf16/fp32 精度、每 rollout batch 多次 optimizer step）与真 bug。

**参考打法**：
- 应主动澄清：reward 类型、每 batch optimizer 步数、生成与打分是否同一 forward 路径、采样温度/top-p、KL 实现、数值精度
- Follow-ups：clipped surrogate 如何防崩、组内奖励全同怎么办、engine-to-trainer log-prob 修正、process vs outcome supervision、KL 放 reward 还是 loss
- 手写练习：`../../online_resource/drills/04_grpo_ppo.py`；概念梳理 [../03_gaps/agentic_rl.md](../03_gaps/agentic_rl.md)；tool-return masking 见 [D 类 D20](D_rapid_fire.md)

</details>

→ **完整解答：[solutions/C6_grpo_debug.md](solutions/C6_grpo_debug.md)**

### [C7] ⭐⭐⭐ Anthropic Applied AI 轨题族：retrieval scorer / token-budget allocator / customer-brief take-home<a id="c7"></a>
- 来源: getperspective.ai 博客（单源二手；tool-use orchestrator 部分与 1p3a 印证） ｜ 置信度: ⚠️ ｜ 公司/轮次: Anthropic · Applied AI 60min 店面 + 3–4h take-home · 2025H2–2026H1
- 考察点: LLM 周边实用 Python：检索评估指标、context/token 预算、API hygiene、模糊需求自主决策
<details><summary>题面 + 参考打法 + 高频追问</summary>

**店面三类实作（LLM-adjacent Python）**：(1) retrieval scorer——给 query-document 对和相关性标注，实现打分/排序 + 评估指标（MRR/NDCG，追问平局与缺失标注）；(2) token-budget allocator——多个消息/文档/工具结果竞争有限 context window，按优先级+截断策略分配 token 预算（追问截断对下游影响、缓存友好性）；(3) tool-use orchestrator——与 [C1](#c1) 同型。

**Take-home**：按虚构企业客户 brief，3–4h 用 Claude API 构建能跑的应用。评分＝"shipped behavior, API hygiene"（Messages API/tool use/prompt caching/重试）+ 模糊需求下独立做合理假设。后接 60–90min customer-conversation simulation（discovery 而非 demo——问买家现有评估标准、过去失败的 AI 部署），博文称该轮与 offer 相关性最强；SD 轮 "increasingly focuses on evaluation harnesses, not RAG architecture"。

**打法**：NDCG 手写公式过一遍；token allocator 用贪心+优先级桶；take-home 必带最小 eval 脚本。

</details>

### [C8] ⭐⭐⭐ Anthropic：Weighted DataBatcher with Deterministic Checkpointing<a id="c8"></a>
- 来源: 1p3a 研究岗面经转述（v1 练习版题面） ｜ 置信度: ⚠️ ｜ 公司/轮次: Anthropic · ML 岗 coding-design 55min · 2025–2026
- 考察点: 加权采样、checkpoint/resume 确定性、iterator 状态模型
<details><summary>题面 + 参考打法 + 高频追问</summary>

**题面**：实现 `DataBatcher(registry, weights, seed)`：`next_batch(k)` 按权重选数据源取样；`checkpoint()` 返回可序列化 state；新实例 `resume(state)` 后必须产生与未中断运行**完全相同**的后续样本流。说明动态增删数据源和 multi-worker 语义。

**参考打法**：registry version + 规范化 weights 写进 checkpoint → seeded RNG state 或 counter-based choice 保证随机流可续 → 每 source 存 cursor/epoch，batch commit 后原子推进 → registry 变化默认拒绝恢复（要兼容需显式 migration policy）→ 测试 uninterrupted 与 split-run 序列完全相等。

**高频追问**：checkpoint 正好在 batch 一半？ ｜ 百万数据源的高效 weighted choice（alias table / 树状累积权重）？ ｜ worker 扩缩容 shard 稳定性？

完整 rubric: [../../agentic/data/questions.json](../../agentic/data/questions.json) → `q-anthropic-weighted-batcher`

</details>

→ **完整解答：[solutions/C8_weighted_batcher.md](solutions/C8_weighted_batcher.md)**

> 高分句：Anthropic 全程可查文档、禁 AI——把 tool_use/tool_result 协议写成肌肉记忆，现场时间花在错误处理和终止条件上。

## Sierra（7/15）

### [C9] ⭐⭐⭐ Sierra onsite debugging round：TS/React buggy 代码库找 bug（禁 AI）<a id="c9"></a>
- 来源: Exponent 经历+guide + gaijineer + 1p3a 2026-05 面经 ｜ 置信度: ✅ ｜ 公司/轮次: Sierra · onsite 60min（多人称 "the real gate"）· 2025–2026-05 在考
- 考察点: 读代码 > 写代码；hypothesis-driven 排障；TS/React 硬性熟练度；无 AI 原生 debug
<details><summary>题面 + 参考打法 + 高频追问</summary>

**题面两变体**：(1) TypeScript+React 应用（如客服 bot 聊天界面），4–6 个 bug，明确 no AI tools/resources；(2) 约 4–5 文件的 agent 实现小代码库 + 参考架构图，约 3 个 bug，修完讨论优化。

**警告**（多位候选人）："Do not believe the language-agnostic framing"——只写 Python 的候选人 onsite 第一轮就是 TS/React debugging 直接挂。评估：代码理解、复现→定位→假设→验证、修复不破坏其他功能、UX 影响的产品意识（只让测试通过不够）。

**备考 checklist**：
- React hooks 坑：stale closure、useEffect 依赖数组、setState 异步/批处理、列表 key
- TS：类型窄化、可选链、async/await 与 promise 错误处理（未 await、吞异常）
- API 调用层：竞态（旧请求覆盖新结果）、loading/error 状态、abort

**高频追问**：这个修复会不会影响别的功能？ ｜ 还有时间的话你会优化什么？

</details>

→ **完整解答：[solutions/C9_debugging_round.md](solutions/C9_debugging_round.md)**

### [C10] ⭐⭐⭐ Sierra 电面：Markdown 按 header 层级分块（size limit + 父 header 重复）<a id="c10"></a>
- 来源: PracHub 完整题面 + 1p3a 2026-05-15 同题面经互证 ｜ 置信度: ✅ ｜ 公司/轮次: Sierra · 电面 60min CoderPad（Python/TS）· 2026-04~05
- 考察点: 实用文本处理 + 状态机 + multi-part 递进下的可扩展代码；与 RAG chunking 直接相关
<details><summary>题面 + 参考打法 + 高频追问</summary>

**题面**：`split_markdown(markdown: str, max_size: int) -> list[str]`：切成有序 chunks，每个 ≤ max_size。Header = 1–6 个 `#` + 空格开头；非 header 行属当前层级。**关键规则**：chunk 在 section 中间开始时，须在首个内容行前重复所有 active 父 headers（重复的 header 计入 size limit）；遇 level-L header 清空 level L–6 的 active headers。约束：len ≤ 200,000；保证任意单行+所需父 header 能放进 max_size；保持原顺序，说明空行/换行假设。例：`("", 10) -> []`；`("# Title\nHello\n## Section\nWorld", 100)` → 整篇一个 chunk。

**参考打法**：
- 按 level 维护 active header 栈 + 贪心逐行追加；拼接长度要含换行分隔符——先写 `chunk_len(lines)` helper 避免 off-by-one
- Sierra 电面是 multi-part 递进（每个 follow-up 在已有代码上叠需求）——**结构干净可扩展 > 一次写完**：把"开新 chunk 时注入父 headers"抽成函数
- 先跑空文档/单行超长/连续 header 三个边界

**高频追问**：start 相同的排序？ ｜ code block 里的 `#` 要不要当 header（澄清假设）？

</details>

→ **完整解答：[solutions/C10_markdown_chunking.md](solutions/C10_markdown_chunking.md)**

### [C11] ⭐⭐⭐ Sierra OA：Debug 日志时间区间合并 + overlap/gap 检测<a id="c11"></a>
- 来源: PracHub 完整题面 + 1p3a 2025-11-25 "Debug View Problem" 互证 ｜ 置信度: ✅ ｜ 公司/轮次: Sierra · OA/take-home 附属题 · 2025-11
- 考察点: 区间基本功 + 半开区间边界 + agent debug 日志视图的建模
<details><summary>题面 + 参考打法 + 高频追问</summary>

**题面**：n 个 debug 日志段 `(start, end, text)`，半开区间 `[start, end)`，n ≤ 200,000。**Task 1**：合并重叠区间为 `[min_start, max_end)`，text 按时间顺序空格拼接，按 start 升序返回。例：`[(0,5,"A"),(3,10,"B"),(12,15,"C")] -> [(0,10,"A B"),(12,15,"C")]`。**Task 2**：返回两个 bool——是否存在任意一对区间相交（交集非空）；最早 start 与最晚 end 之间是否存在 gap。同例输出 `(True, True)`。

**边界**：相邻区间 `[1,4)` 和 `[4,6)` **既不算 overlap 也不算 gap**——半开区间语义要开场说清。打法：排序 O(n log n) + 单遍扫描；Task 2 的 overlap 用"排序后相邻对 `prev_end > cur_start`"判定。

**高频追问**：start 相同时 text 拼接定序？ ｜ gap 定义是否含首尾之外？

</details>

→ **完整解答：[solutions/C11_log_intervals.md](solutions/C11_log_intervals.md)**

### [C12] ⭐⭐⭐ Sierra 官方 AI-native onsite：Plan→Build→Review（2h 自选 AI 工具从想法到 demo）<a id="c12"></a>
- 来源: Sierra 官方博客 the-ai-native-interview ｜ 置信度: ✅（官方一手） ｜ 公司/轮次: Sierra · onsite 三段 · 2025–2026 现行
- 考察点: 官方明说：agency（卡住会不会 pivot）、judgment（scope 裁剪）、product sense、系统理解、数据模型与 extensibility、如何用 AI 本身
<details><summary>题面 + 参考打法 + 高频追问</summary>

**形式**：(1) Plan——与面试官共同构思产品；(2) Build——2 小时，"the AI tooling and frameworks of their choice"，官方明确可裁 scope、可跳过 boilerplate（CRUD/auth）聚焦独特部分；(3) Review——现场 demo、产品决策讨论、code review、**解释自己怎么用的 AI**。官方案例：候选人做了让用户保持心流的 AI 游戏，demo 即面试官试玩。

**参考打法**：
- 预先练熟自己的 AI 编码环境（Claude Code/Cursor），彩排 2h 从零到 demo 的节奏（30min 骨架 / 60min 核心 slice / 30min 打磨 demo 路径）
- 准备一个能秀 agent 专长的产品 idea 库（客服 agent、trace viewer、eval 面板）
- Review 时说清"哪些是 AI 写的、我怎么验证的"——对 AI 输出的批判性验证是他们看的信号
- 注意：社区面经报告的仍是 take-home+debugging 旧流程，两种可能并存，**向 recruiter 确认场次格式**

完整 rubric: [../../agentic/data/questions.json](../../agentic/data/questions.json) → `q-sierra-plan-build-review`

</details>

→ **完整解答：[solutions/C12_plan_build_review.md](solutions/C12_plan_build_review.md)**

### [C13] ⭐⭐⭐ Sierra 官方试点：接手中型代码库 + 同事 draft PR，用 coding agents 改进<a id="c13"></a>
- 来源: Sierra 官方博客（piloting） ｜ 置信度: ✅（官方一手） ｜ 公司/轮次: Sierra · onsite debugging 新形态 · 2026
- 考察点: code review 判断力 + 与 coding agent 协作迭代
<details><summary>题面 + 参考打法 + 高频追问</summary>

**题面**：medium-sized codebase + 一位"同事"的 draft PR（引入 cross-cutting feature），任务："review and improve it——pulling down the code, inspecting the output, and iterating with coding agents"。与禁 AI 的 TS/React debugging 轮形成对照——Sierra 正从裸写 debug 转向带 agent debug。

**参考打法**：
- 工作流：让 agent 生成 codebase map → 定位 PR 触点 → 跑测试建基线 → 逐项 review（正确性 > 设计 > 风格）→ 用 agent 做窄修改 → 保留验证证据链
- cross-cutting 变更的典型风险清单：一致性（各层语义对齐）、遗漏调用点、回填/migration、测试覆盖、权限绕过
- 核心信号：给 agent 的指令质量、对产出的甄别、review 意见是否切中要害
- v1 自拟练习场景（ticket priority 功能跨 API/DB/queue/UI）可直接拿来彩排

**高频追问**：AI 建议重写整个模块时你怎么判断？ ｜ 哪些问题你选择不修、为什么？

完整 rubric: [../../agentic/data/questions.json](../../agentic/data/questions.json) → `q-sierra-cross-cutting-pr`

</details>

→ **完整解答：[solutions/C13_draft_pr_round.md](solutions/C13_draft_pr_round.md)**

### [C14] ⭐⭐⭐ Sierra 电面递进风格样本：Excel 循环引用检测 / keyboard undo-redo<a id="c14"></a>
- 来源: Exponent 面经 2025-05（同期同题问所有人）+ norahq guide 汇编 ｜ 置信度: ✅（circular ref）/ ⚠️（keyboard） ｜ 公司/轮次: Sierra · 电面 60min · 2025（可能已轮换，作风格样本）
- 考察点: 从产品描述抽象图/OO 模型；每个 follow-up 在现有代码上叠需求
<details><summary>题面 + 参考打法 + 高频追问</summary>

**题 1**："Excel 式电子表格，单元格可引用其他单元格，如何检测循环引用？"——cell 为节点、引用为有向边，DFS 三色标记或 Kahn 拓扑。递进：返回具体环路径 → 增量更新只查受影响子图 → 从 `"=A1+B2"` 解析依赖 → 大规模性能。面经注："同一道电面题问所有人"（2025 上半年，或已轮换）。

**题 2**："Implement a keyboard object with expansion to support undo/redo."——按键输入 + 文本缓冲起手，递进加 undo/redo（两个操作栈或 command 模式记录逆操作）、光标移动、选区、组合操作原子化。

**打法**：这两题是 Sierra 电面风格样本——不背算法，练"flexible, extensible code + 递进叠需求"；每写一段先说扩展点。

</details>

> 高分句：Sierra 评的是接手陌生代码的判断力——先跑测试建基线，再按正确性>设计>风格逐项 review，每个修复都留验证证据。

## 通用格式 + OpenAI/Meta（迁移备用）

### [C15] ⭐⭐⭐ 通用 AI-allowed live coding：1000–2000 行陌生 codebase 加 feature/修漏洞/重构<a id="c15"></a>
- 来源: interviewing.io + Codility/CoderPad VP 访谈 + techinterview.org（CoderPad 称已 35,000+ 场） ｜ 置信度: ✅ ｜ 公司/轮次: generic（本周多家可能采用此格式，故 ⭐⭐⭐）· 60–90min 屏幕共享 · 2025–2026
- 考察点: 分解先于 prompt、prompt 迭代效率、验证习惯、全程 narration
<details><summary>题面 + 参考打法 + 高频追问</summary>

**形式**：自选 AI 工具（Cursor/Copilot/Claude Code），在 1000–2000 行陌生 codebase 限时完成真实任务。三类典型：implementing a new feature / addressing security vulnerabilities / refactoring a service for maintainability。

**评估标准**："Can you decompose the problem clearly before reaching for AI? Do you know what you want before you prompt?" + prompt 迭代效率 + 验证习惯 + 识别 AI 错误输出。**最致命失败**：pasting and shipping without checking、长时间沉默、把 AI 当不会错的 oracle。动手前先复述问题、问澄清、口头勾勒方案——"这一步没做好，代码还没写面试已经输了"。

**新形态参考**：Tutor Intelligence 公开 challenge（"Claude can 1-shot our interviews"）：60x40 仓库 5 机器人完成 1000 订单最小化 timestep，明确 "AI agent use is encouraged (probably necessary)"——考"人的创造力增量 vs 模型顺手的下一步"。开放优化题 + 全力用 AI 是 2026 agent-native 招聘新形态。

现场脚本与 narration 模板：[../02_playbook.md](../02_playbook.md)。

</details>

### [C16] ⭐⭐ OpenAI onsite 试点 agentic coding round（beta）：现有 codebase + 期望用 AI agents<a id="c16"></a>
- 来源: interviewing.io OpenAI 流程页（2026 更新，单源） ｜ 置信度: ⚠️ ｜ 公司/轮次: OpenAI · onsite beta 轮 · 2026-06
- 考察点: 在陌生 codebase 用 AI agent 解决"复杂到无法从零手写"的问题
<details><summary>题面 + 参考打法 + 高频追问</summary>

**形式**：候选人拿到现有 codebase，解决"复杂到无法从零手写"的问题，期望使用 AI coding agents；并非所有候选人遇到。**关键对照**：除此轮外全程严格禁 AI。其余流程：recruiter 30min → 电面 1h CoderPad → SD screen 1h Excalidraw → onsite 4–6h。SD 轮警告："点名任何具体技术就要准备好深入讲它"。

**参考打法**：用 Claude Code 在陌生 repo 做中型 feature 彩排（定位→改→测试）；v1 练习题面（per-tenant concurrency limit，draft 已改 scheduler 但缺 retry/metrics/migration）可直接用。

**相邻数据点**：OpenAI Support Engineer 有正式 "vibe coding" 轮——debug 间歇性失败的 Python 脚本（根因 race condition）、写自动化；同帖强调 HM 轮 bar 极高，建议深学 OpenAI API 产品细节。

完整 rubric: [../../agentic/data/questions.json](../../agentic/data/questions.json) → `q-openai-coding-harness`

</details>

### [C17] ⭐⭐ Meta AI-enabled coding round：多文件 codebase + 内置 AI 助手<a id="c17"></a>
- 来源: interviewing.io 官方博客 + designgurus ｜ 置信度: ✅ ｜ 公司/轮次: Meta · onsite（替换两轮 coding 之一）· 2025-10 试点，2026 预计推广
- 考察点: 怎么向 AI 提问、理解后再采纳、发现 AI 输出错误
<details><summary>题面 + 参考打法 + 高频追问</summary>

**形式**：60 分钟定制 CoderPad，三面板：文件浏览器/编辑器/AI 聊天窗；**AI 只能在聊天面板回答、不能直接编辑文件**（候选人必须自己搬运和验证）。多文件 codebase 按阶段推进：修 bug → 实现核心功能 → 优化。另一轮仍是无 AI 传统算法。

**参考打法**：因为 AI 不能动文件，粘贴前必须逐行理解——评的就是这个动作；练限时"陌生库定位-修复-扩展"并出声叙述与 AI 的分工。

</details>

### [C18] ⭐⭐ OpenAI Chatbot OOD 家族：可扩展多 bot ChatApp / refactor messy chatbot<a id="c18"></a>
- 来源: hack2hire（OpenAI 8/10）+ PracHub 同族两题 + coditioning 确认 ｜ 置信度: ✅ ｜ 公司/轮次: OpenAI · coding · 2025-11~2026-06
- 考察点: OOD/开闭原则/pub-sub、防 bot 互触发递归；重构不改行为——"从零写"向"读改现有代码"转向
<details><summary>题面 + 参考打法 + 高频追问</summary>

**题 1（ChatApp）**：人类用户 + 自动 bot 共享 channel；用户消息先入 channel 日志，各 bot 可响应并把输出加入同一日志；三种 bot 类型含跨 bot 交互（MeetBot 影响 AwayBot 状态）；新增 bot 类型不改现有逻辑。**题 2（refactor）**：给 messy chatbot 代码，保持行为不变重构（PracHub 2026-06-22）。

**参考打法**：
- 公共 bot 接口 + pub-sub：channel 广播解析后的事件，bot 消费自己需要的；跨 bot 交互通过发布状态变更事件解耦，**别让 bot 直接互调**
- 防无限递归：bot 产生的消息标记 origin，bot 不响应 bot 消息（或深度计数）
- 重构题：先补测试锁行为再动刀，边讲边归纳 code smell；路由用 registry/strategy（handler + can_handle）

**高频追问**：多 bot 对同一消息的执行顺序？ ｜ 数千并发 channel 不同路由规则？ ｜ 历史持久化与 bot 逻辑解耦？

</details>

### [C19] ⭐⭐ OpenAI Fullstack tech screen：看视频复刻 ChatGPT 式流式聊天 UI<a id="c19"></a>
- 来源: 1p3a 三帖交叉（2026-03~05） ｜ 置信度: ✅ ｜ 公司/轮次: OpenAI · 背靠背两轮 tech screen（FE coding + SD）· 2026
- 考察点: 消费 token 流渲染、loading/error/retry；**主动讨论边界是显式评分项**
<details><summary>题面 + 参考打法 + 高频追问</summary>

**题面**：给一个视频——简单输入框+submit 的 ChatGPT 式界面，照着实现；含 streaming text 处理（有提供 utility，不用手写 SSE 解析）。第二轮 SD 聚焦 ChatGPT 功能与异常处理。**挂点提示**（原帖）："要把情况都主动讨论出来，而不是面试官提出 follow-ups 让我们解决"。

**参考打法**：React 消息列表 + 受控输入 + streaming append；主动讨论 loading/error/retry、乱序 chunk、自动滚动（用户上滚时暂停）、防抖、可访问性；SD 轮讲 SSE vs WebSocket、断流恢复、token 计费显示——见 [../03_gaps/streaming.md](../03_gaps/streaming.md)。2026-07 新变体：PracHub "Build a Reliable Streaming Chat UI"（断线清理/backpressure）。

</details>

> 高分句：AI-assisted 轮评的不是代码而是工作流——分解先于 prompt，验证先于接受，全程出声。
