# 02 · State、Durable Execution 与 Memory

⏱ 骨架 8 min ｜ 含深潜与资料 45 min ｜ 面试前只看 ⭐⭐⭐ 部分

## 1. 三种状态不要混 ⭐⭐⭐

| 状态 | 内容 | 权威存储 |
|---|---|---|
| Conversation state | 给模型看的消息/summary | 可丢弃，随时重新生成 |
| Execution state | run status、current task、attempt、lease、budget、approval | DB / event log |
| Domain state | 订单、付款、文档、实验等真实业务事实 | 业务系统 |

- Conversation summary 不是 durable state。
- 恢复顺序：从 DB/event log 重建执行状态 → 再重新生成 context。

> 高分句：恢复的是 durable state，不是把旧聊天原样重新塞回模型。

## 2. 状态机 ⭐⭐⭐

`pending → running → waiting_tool / waiting_approval → running → succeeded`

- 任何非终态可进入 `failed` 或 `cancel_requested`；真正停止资源后才是 `cancelled`。
- 每条迁移写明：触发者、前置条件、事务边界、event 和副作用。

> 高分句：cancel_requested 和 cancelled 是两个状态——声明取消不等于资源已经停止。

## 3. 关键 crash window ⭐⭐⭐

最危险情况：**外部工具已经成功，进程在保存结果前崩溃**。解决优先级：

1. 给外部操作稳定 `operation_key`，provider 保证幂等。
2. 恢复先按 key 查询外部 status，再决定 retry。
3. 没有查询/幂等能力时，状态标为 `unknown`，人工 reconcile；不能假装 exactly-once。

<details>
<summary>Transactional outbox 的能力边界</summary>

数据库可用 transactional outbox 协调「保存意图」和「发送任务」两个动作的原子性，但它无法凭空让任意外部系统 exactly-once——外部幂等能力仍然是前提。

</details>

> 高分句：exactly-once 不是承诺出来的，是 operation_key + 恢复时先查 status + unknown 兜底组合出来的。

## 4. Worker lease ⭐⭐⭐

- DB 事务 claim task，写 `worker_id/lease_until/attempt`。
- heartbeat 延长 lease。
- result commit 必须携带 attempt/fencing token；过期 worker 的迟到结果被拒绝。
- retry 前检查 operation status。

分布式多 worker 扩展见 [../03_gaps/scaling.md](../03_gaps/scaling.md)。

> 高分句：lease 防止双跑，fencing token 防止迟到写——两个缺一不可。

## 5. Context vs memory ⭐⭐

- Context：这一次 inference 的工作集。
- Memory：跨 turn/run 可检索的持久信息。
- 两个反模式：把所有 history 当 context；把所有内容都写 memory。

## 6. Memory tiers 与治理 ⭐⭐

| Tier | 内容 | 生命周期 |
|---|---|---|
| Working memory | 当前目标、计划、未决问题、最近 observation | 随 run 结束 |
| Episodic memory | 一次任务的结果、失败、用户修正 | 有 provenance 和 TTL |
| Semantic memory | 稳定事实、术语、偏好或组织规则 | 写入门槛最高 |
| Artifact store | 文档、代码、trace、大结果 | context 只放 pointer/摘要 |

```python
@dataclass(frozen=True)
class MemoryRecord:
    id: str
    subject: str
    kind: str
    value: str
    source_ids: tuple[str, ...]
    scope: str
    confidence: float
    valid_from: datetime
    expires_at: datetime | None
    supersedes: str | None
```

写入 gate（模型的猜测不能直接成为全局事实）：

- [ ] 是否明确/有证据
- [ ] 是否新信息
- [ ] 是否长期有用
- [ ] 是否敏感
- [ ] scope 是否正确
- [ ] 谁能纠错

读取顺序：identity/tenant/ACL → time/TTL → task relevance → token budget。检索后仍要把 source 和不确定性送给模型。

RAG 检索专题见 [../03_gaps/rag.md](../03_gaps/rag.md)。

<details>
<summary>删除的完整语义</summary>

删除不是只从向量索引删一条：

1. 写 tombstone。
2. 清 raw、derived indexes、cache。
3. 验证后续 retrieval 不再返回。
4. 若法规要求 audit，只保留最小必要 metadata。

</details>

> 高分句：先建可治理的 MemoryRecord，再选检索技术；相似度不是权限，也不是事实性。

## 7. 现有系统怎么做 · Memory 实现流派 ⭐⭐⭐

面试常问「memory 怎么实现」。答题框架：任何 memory 系统 = **写入路径（谁决定写）× 存储结构 × 读取路径（怎么进 context）× 遗忘/纠错机制**。五个流派在这四个维度上做了不同 tradeoff：

| 系统 | 核心机制一句话 | 适用场景 | 链接 |
|---|---|---|---|
| MemGPT / Letta | OS 分页类比：core memory blocks 常驻 context 且 agent 用工具自编辑，archival/recall 是可检索外存 | 长期陪伴型 agent、persona 一致性 | [arxiv](https://arxiv.org/abs/2310.08560) · [docs](https://docs.letta.com/guides/core-concepts/memory/memory-blocks) |
| ChatGPT memory | 双层：saved memories（显式条目注入 system prompt）+ chat history reference（对历史对话的检索/离线摘要） | 海量 C 端用户的个性化 | [OpenAI](https://openai.com/index/memory-and-new-controls-for-chatgpt/) · [FAQ](https://help.openai.com/en/articles/8590148-memory-faq) |
| Claude Code 文件式 | CLAUDE.md 层级 + auto memory 目录（MEMORY.md 索引 + topic files），纯 markdown、git 可版本化可 review | 代码库/团队知识，人机共编 | [docs](https://code.claude.com/docs/en/memory) |
| Zep / Graphiti | temporal knowledge graph：边带 valid_at/invalid_at 双时间轴，冲突靠时间失效不靠覆盖 | 事实随时间演变、需审计溯源 | [arxiv](https://arxiv.org/abs/2501.13956) · [repo](https://github.com/getzep/graphiti) |
| Mem0 | 两阶段 pipeline：LLM 抽取候选 facts → 检索相似旧 memory → LLM 决策 ADD/UPDATE/DELETE/NOOP | 通用 memory 层、成本敏感 | [arxiv](https://arxiv.org/abs/2504.19413) · [repo](https://github.com/mem0ai/mem0) |

评测一句话：[LongMemEval](https://arxiv.org/abs/2410.10813)（500 题测 5 项能力：抽取、跨 session 推理、时序推理、知识更新、abstention）和 LoCoMo（超长多 session 对话）是这个领域的两个标准 benchmark；Mem0/Zep 的论文数字都在这两个上打。

<details>
<summary>MemGPT / Letta：【技术机制】self-editing memory + 分层换页</summary>

**存储结构**（三层，类比 OS 内存层级）：
- **Core memory**：若干 labeled blocks（`persona`、`human`、自定义），每块 `{label, value, limit}`，limit 是字符上限。渲染进 system prompt，**常驻 context**。
- **Recall memory**：全部历史消息，DB 持久化，全文可搜（被 evict 出 context 的消息永不丢失）。
- **Archival memory**：向量库，存任意事实/文档片段。

**写入路径**：由**模型自己**通过 tool call 决定——`core_memory_append(label, text)`、`core_memory_replace(label, old, new)`、`archival_memory_insert(text)`。工具返回后靠 heartbeat 机制让模型可连续多步操作。这是它最激进的设计：memory management 本身是 agent 的任务。

**读取路径**：core blocks 每次 inference 都在；`conversation_search` / `archival_memory_search` 按需检索。context 满时触发 **queue eviction**：最老的消息被压进一条 recursive summary（也在 context 里），原文进 recall memory。

```python
def assemble_context(agent):
    return [system_prompt,
            render_blocks(agent.core_memory),   # persona/human/... 常驻
            agent.recursive_summary,            # 被 evict 消息的滚动摘要
            *agent.message_queue]               # FIFO 近期消息

def on_context_pressure(agent):                 # 超过警戒水位
    evicted = agent.message_queue.pop_oldest(n)
    agent.recursive_summary = llm_summarize(agent.recursive_summary, evicted)
    recall_store.persist(evicted)               # 原文可搜回，不丢
```

**遗忘/纠错**：`core_memory_replace` 要求 old 串 exact match；archival 没有自动冲突消解。

**失败模式**：① 写入靠模型自觉，模型可能忘写/乱写；② block 超 limit 写入报错，模型要先腾地方；③ exact-match replace 脆；④ archival 被当日志倾倒后检索全是噪声，且新旧矛盾事实并存。

**面试点**：为什么 core 和 archival 分开？——core 是「每次都必须看到的少量高价值状态」（放 context，零检索风险），archival 是「偶尔需要的长尾」（换检索成本省 token）。这就是第 6 节 memory tiers 的一个具体实现。

</details>

<details>
<summary>ChatGPT memory：【技术机制】saved memories + chat history 双层</summary>

**存储结构**：两层，管控粒度完全不同。
- **Saved memories**：一条条自然语言事实（"用户是素食者"），用户可在 Settings 逐条查看/删除。
- **Chat history reference**：对全部历史对话做检索 + 离线批处理摘要（OpenAI 后来称为 "dreaming"：后台任务定期把 chat history 蒸馏成 user insights），用户只能整体开关、不可逐条编辑。

**写入路径**：saved memories 由**模型判断值得记**或用户显式说 "remember X" 时，通过内部工具（早期实现是 `bio` tool）写入一条；chat history 层则是被动全量——所有对话默认可被引用。

**读取路径**：saved memories 直接注入 system prompt（所以每轮都生效、无检索失败风险）；chat history 层是检索式——对当前 query 检索相关历史片段/insights 注入。这个「小而准的注入层 + 大而糙的检索层」组合和 Letta 的 core/archival 是同构的。

**遗忘/纠错**：对话内说 "forget X" 触发删除；Settings 里逐条删 saved memories；Temporary Chat 不读不写 memory。

**失败模式**：① 过度泛化的记忆污染后续所有回答（一次提到 "帮我写儿童故事" 被记成 "用户喜欢儿童向内容"）；② chat-history 层推断对用户不可见，错了难发现难纠正；③ 共享设备/账号下是隐私事故；④ 记忆注入 system prompt 意味着它抢所有对话的 token 预算。

**面试点**：这是「平台替用户管 memory」的极端——写入门槛低、召回率优先；对比 Claude Code 文件式是「用户完全掌控」——precision 优先。第 6 节的写入 gate checklist 正是介于两者之间的工程答案。

</details>

<details>
<summary>Claude Code 文件式：【技术机制】memory as versioned files</summary>

**存储结构**：全部是 markdown 文件，两套系统：
- **CLAUDE.md 层级**（人写）：managed policy → `~/.claude/CLAUDE.md`（user）→ `./CLAUDE.md` 或 `./.claude/CLAUDE.md`（project）→ `CLAUDE.local.md`（个人、gitignore）。支持 `@path` import（最深 4 hops）；`.claude/rules/*.md` 可用 `paths:` frontmatter 做 path-scoped lazy load。
- **Auto memory**（模型写）：`~/.claude/projects/<project>/memory/`，`MEMORY.md` 是索引 + 若干 topic files（`debugging.md` 等）。

**写入路径**：CLAUDE.md 人写（或 `/init` 生成后人 review）；auto memory 由模型在会话中判断「未来会话有用」才写，用户纠正/偏好是主要触发。

**读取路径**：session 启动时 CLAUDE.md **全文注入**（从目录树自 root 向下 concatenate，越近 cwd 越后读）；`MEMORY.md` 只注入**前 200 行或 25KB**，topic files 不预载、模型用 Read 按需取——索引常驻 + 明细懒加载，又是同一个分层模式。子目录的 CLAUDE.md 在模型读到该目录文件时才加载。

**遗忘/纠错**：直接编辑文件、git diff/review/revert、`/memory` 命令浏览。这是「memory as code」流派的核心卖点：可版本化、可 code review、可 grep、可回滚。

**失败模式**：① 文件是 context 不是 enforcement——硬约束必须用 hook，指望 CLAUDE.md 拦坏行为是设计错误；② 超过 ~200 行 adherence 显著下降；③ 多文件规则冲突时模型任选一条；④ compaction 后只有 project-root CLAUDE.md 自动重注入，嵌套的要等再次读文件。

**面试点**：为什么文件系统够用？——memory 的 CRUD、权限（文件权限/gitignore）、版本（git）、审计（git log）全部复用现成基础设施，不需要 memory service。代价是无语义检索、无自动冲突消解——靠人和索引文件补。

</details>

<details>
<summary>Zep / Graphiti：【技术机制】bitemporal knowledge graph</summary>

**存储结构**：知识图谱三层——episode 节点（原始消息，provenance 保留）、entity 节点、fact 边。每条边带**两组时间轴**：
- `created_at / expired_at`：系统时间（什么时候入库/被判失效）——transaction time。
- `valid_at / invalid_at`：事实时间（这件事从何时起成立/不再成立）——valid time。

**写入路径**（每条消息触发 ingest pipeline，多次 LLM 调用）：

```python
def ingest(episode):
    graph.add_episode(episode)                      # 1. 原文永久保留
    entities = llm_extract_entities(episode)
    for e in entities:                              # 2. entity resolution
        candidates = search(e, by=["embedding", "bm25"])
        e.node = llm_dedupe(e, candidates) or graph.new_node(e)
    facts = llm_extract_facts(episode, entities)
    for f in facts:                                 # 3. temporal conflict check
        related = graph.edges_between(f.src, f.dst)
        for old in llm_find_contradictions(f, related):
            old.invalid_at = f.valid_at             # 旧事实标失效，不删除
        graph.add_edge(f, valid_at=llm_extract_time(f, episode))
```

**读取路径**：混合检索（embedding cosine + BM25 + graph n-hop 遍历）→ rerank → 把 facts 连同有效期渲染成 context 字符串（"Alice lived in SF (2020–2023), lives in NYC (2023–)"）。

**遗忘/纠错**：核心设计——**冲突不覆盖，靠 `invalid_at` 时间失效**。旧事实仍在图里，可回答 "用户以前住哪、什么时候搬的"，且全程可审计（每条边可回溯到 episode）。这是第 6 节 `MemoryRecord.supersedes / valid_from` 的完整版。

**失败模式**：① 写入路径每条消息 3-5 次 LLM 调用，延迟和成本高（写是异步的但积压会导致读到旧图）；② entity resolution 错误合并（两个 "John" 并成一个）会不可逆污染图；③ LLM 抽的时间表达式不可靠（"上周" 相对谁？）。

</details>

<details>
<summary>Mem0：【技术机制】extraction → conflict-aware update pipeline</summary>

**处理流程**（两阶段，论文 Fig.1）：

```python
def add(messages):
    # Phase 1: extraction —— context = 全局对话摘要 + 最近 m 条消息
    facts = llm_extract(prompt(summary, recent_msgs, messages))
    # Phase 2: update —— 每个候选 fact 单独决策
    for fact in facts:
        similar = vector_store.search(embed(fact), top_k=10)
        op = llm_decide(fact, similar)   # tool-call 输出四选一
        match op.action:
            case "ADD":    vector_store.insert(fact)
            case "UPDATE": vector_store.update(op.target_id, merged(op))
            case "DELETE": vector_store.delete(op.target_id)   # 新旧矛盾
            case "NOOP":   pass                                # 已知/无价值
```

- 全局对话摘要异步刷新，给 extraction 提供长程 context。
- **Mem0g** 变体把 facts 存成图（entity-relation 三元组），额外支持关系查询，代价是 ingest 更贵。

**读取路径**：query embedding → vector top-k → 注入 prompt。没有 Zep 那样的时间轴渲染。

**遗忘/纠错**：DELETE 由冲突检测触发（"用户搬到 NYC" 使 "住在 SF" 被删）——注意这里是**覆盖式**，旧事实真的没了，和 Zep 的时间失效是两种哲学：Mem0 要「当前世界的最小真集」，Zep 要「带历史的世界模型」。

**关键数字**（LOCOMO，论文 claim）：比 full-context 省 90%+ token、p95 latency 大幅低，质量接近或超过 memory 基线——卖点是「production-ready = 便宜且快」。

**失败模式**：① ADD/UPDATE/DELETE 决策本身是 LLM 判断，误删事实无审计可回滚（对比 Zep）；② facts 被 paraphrase 后 provenance 变弱；③ top-k 检索决定了「相关旧 memory」的视野，冲突若不在 top-k 里就漏检，产生并存矛盾。

**面试点**：把 Mem0 的 update phase 拿来对照第 6 节写入 gate——它把 gate 的「是否新信息/是否矛盾」两条自动化成 LLM 决策，但「是否敏感/scope/谁能纠错」仍然没人管，这就是我会补治理层的原因。

</details>

## 8. 现有系统怎么做 · Long-horizon 跨 context 实现 ⭐⭐⭐

问题本质：任务时长 >> 一个 context window。所有方案都是在回答同一个问题——**context 装不下的状态放哪、恢复时怎么重建**。答案分四类：压缩在 context 里（compaction）、外化到文件（Manus/Anthropic harness）、外化到 event log（Temporal）、压缩后交接（Cognition/OpenHands 的分歧点）。

| 方法 | 核心机制一句话 | 适用场景 | 链接 |
|---|---|---|---|
| Context compaction | 接近 limit 时让模型把 history 摘要化，用 summary 重开 context；API 侧可自动清旧 tool results | 通用兜底，所有长任务 | [博客](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents) · [docs](https://platform.claude.com/docs/en/build-with-claude/context-editing) |
| 文件系统当外存 (Manus) | append-only context 保 KV-cache，大 observation 可还原地截断进文件，todo.md recitation 对抗 lost-in-the-middle | 工具输出巨大、成本敏感的生产 agent | [博客](https://manus.im/blog/Context-Engineering-for-AI-Agents-Lessons-from-Building-Manus) |
| Initializer + progress artifacts | 首 session 建 init.sh / progress 文件 / feature_list.json，后续 session 固定开场序列 + git commit 当 checkpoint | 跨几十个 session 的无人值守长任务 | [博客](https://www.anthropic.com/engineering/effective-harnesses-for-long-running-agents) |
| Durable execution (Temporal) | event sourcing：状态转换 append 进 event history，crash 后 replay 重建，activity 结果不重跑 | 执行状态必须 exactly-once 语义的 workflow | [docs](https://docs.temporal.io/workflow-execution/event) |
| 单线程长 context (Cognition) | 拒绝并行 subagent：context 完整性 > 并行度；超长就用专门模型压缩历史再续 | 强耦合的写任务（coding） | [博客](https://cognition.com/blog/dont-build-multi-agents) |
| Context condenser (OpenHands) | event stream 超阈值后 LLM 把中间段总结成 summary event，首尾保留，原始 events 不删 | 开源 coding agent 的默认方案 | [博客](https://www.openhands.dev/blog/openhands-context-condensensation-for-more-efficient-ai-agents) · [repo](https://github.com/All-Hands-AI/OpenHands) |

<details>
<summary>Context compaction：【技术机制】/compact 与 context editing API</summary>

**Claude Code /compact 的实现**：把 message history 交给模型生成结构化 summary——明确指示**保留** architectural decisions、unresolved bugs、当前 plan、关键文件路径，**丢弃**冗余 tool outputs 和中间对话；然后用 summary 替换旧历史重开 context。`/compact <focus>` 可指定保留重点。project-root CLAUDE.md 在 compact 后从磁盘重读重注入（pinned 事实的来源是文件，不是 summary——这个细节很关键）。

```python
def maybe_compact(msgs, limit):
    if tokens(msgs) < 0.9 * limit: return msgs
    summary = llm(COMPACT_PROMPT, msgs)     # 结构化：decisions/bugs/plan/files
    return [system, reread(CLAUDE_md), summary_msg(summary), *msgs[-K:]]
```

**API 侧 context editing**（beta header `context-management-2025-06-27`）：`clear_tool_uses_20250919` 策略——input tokens 超过 `trigger` 阈值后，server 端自动把**最老的 tool results** 换成 placeholder 文本；可配保留最近 N 个、`exclude_tools` 白名单、是否连 tool inputs 一起清。设计上和 **memory tool**（client-side 文件读写工具）配套：模型先把要紧的东西写进 memory 文件，旧 tool results 被清了也不丢。

**失败模式**：① summary 丢掉「当时看不重要、后来关键」的细节——这是 compaction 的本质风险，只能靠结构化 prompt 缓解；② compaction 使整个 prefix 变化，**KV cache 全灭**（一次性成本尖峰）；③ 连续多次 compact 是有损压缩的迭代，信息熵单调衰减——所以要配文件外存兜底。

**面试点**：compaction 只对 conversation state 合法（第 1 节）——它可丢弃可重建。谁要是把 execution state 也放进被 compact 的 history 里，crash 恢复就没了。

</details>

<details>
<summary>文件系统当外存 (Manus)：【技术机制】KV-cache 友好 + recitation</summary>

Manus 博客的六条经验里最硬核的三条：

**1. Append-only context，KV-cache 至上**。生产 agent 的 input:output token 比约 100:1，KV-cache 命中率是最重要的成本/延迟指标（cached $0.30 vs uncached $3 /MTok，10x）。因此：prefix 绝不放时间戳这类易变内容；历史消息**只追加不修改**（连 JSON 序列化都要保证 key 顺序确定性）；工具集不动态增删（会改 prefix），要限制动作就用 **logit masking / 强制 prefill** 在 decode 侧约束。

**2. 文件系统 = ultimate context**：unlimited、persistent、agent 自己可操作。大 observation（网页、PDF）做**可还原压缩**——context 里只留 URL/路径等引用，全文写文件，需要时再读回。区别于 compaction 的有损摘要：这是无损的换页。

**3. todo.md recitation**：agent 每步重写 todo.md 并 append 到 context 尾部，把全局目标不断拉回模型的近期注意力，对抗 50 步长任务里的 lost-in-the-middle 和目标漂移。零架构成本，纯 prompt 层技巧，但实测有效。

另外两条常被追问：**保留错误**——失败 action 和 stack trace 留在 context 里，模型隐式更新 prior 不再重犯，清洗错误 = 删证据；**避免 few-shot 自模仿**——context 里同型动作太多时模型会机械重复，解法是 serialization 加受控随机化（措辞/顺序微扰）。

**失败模式**：文件外存要求模型自觉管理文件（和 MemGPT 同款风险）；append-only 意味着错误 prompt 设计会永久占 context。

</details>

<details>
<summary>Initializer + progress artifacts：【技术机制】环境有状态、模型无状态</summary>

Anthropic 的 long-running harness 实验（跨几十个 context window 无人值守写应用）：

**Phase 1 — initializer agent**（只跑一次）产出四个 artifact：
- `init.sh`：一键起 dev server 的脚本；
- `claude-progress.txt`：工作日志（agent 自己维护）；
- `feature_list.json`：把需求展开成细粒度可测 features，每项 `{category, description, steps, passes: false}`——**只允许后续 agent 改 passes 字段**，防 scope creep 和提前宣布完工；
- initial git commit。

**Phase 2 — coding agent**，每个新 session 固定开场序列：

```bash
pwd                          # 1. 确认环境
git log --oneline -20        # 2. 从 git + progress 文件重建"我做到哪了"
cat claude-progress.txt
jq '.[] | select(.passes==false)' feature_list.json | head -1   # 3. 下一项
./init.sh                    # 4. 起环境
# 5. 冒烟测试通过后才开始新 feature；结束时 commit + 更新 progress
```

**设计本质**：cross-session state 全部外化为「文件 + git」，模型完全无状态。git commit 即 checkpoint（可 revert、可读 log）；progress 文件即人类交接班笔记。这和 Temporal 是同一个原则的两种实现——状态放环境、放 log，不放模型脑子里。

**失败模式**：agent 不守规矩改 feature_list（要 prompt 层硬约束或工具层拦截）；progress 文件写得含糊导致下个 session 误判状态；冒烟测试缺失时错误状态滚雪球。

</details>

<details>
<summary>Durable execution (Temporal)：【技术机制】event sourcing + deterministic replay</summary>

**机制**：workflow 每个状态转换（started、activity scheduled/completed、timer fired…）append 进 **event history**（append-only、durably persisted）。worker crash 后，新 worker **replay**：从头重新执行 workflow 代码，但每遇到 activity/timer/side-effect，不真的重跑，而是从 history 直接返回记录的结果——代码跑到崩溃点时，内存状态被精确重建，继续执行。

```
run 1: wf_code ── schedule A ──▶ history: [A_scheduled, A_completed(result)]
       wf_code ── schedule B ──▶ crash!
run 2 (replay): wf_code ── schedule A ──▶ history 已有 → 直接返回 result，不重跑
                wf_code ── schedule B ──▶ history 没有 → 真正执行，继续前进
```

**前提：workflow 代码必须 deterministic**——禁止直接用 random/now()/IO/env，全部包成 activity 或 side-effect（后者 replay 时返回记录值）。违反 = replay 走到不同分支 = non-determinism error。history 太长用 Continue-As-New 开新 execution 截断。

**与 agent 的同构映射**（这是面试杀手锏）：LLM call = activity（非确定、昂贵、结果必须记录不能重跑）；agent loop = workflow；恢复 = replay event log 重建 execution state。v1 lab03 的 SQLite event log 版 agent 就是这个模式的缩影。第 3 节的 crash window 在这里的答案是：activity completion 先写 history 再往下走，重放时天然不重复执行。

**失败模式**：① 代码非确定性（最常见 NDE）；② workflow 代码升级后老 history replay 不过（要 versioning/patching）；③ event history 有大小上限，长 agent loop 必须设计 Continue-As-New 点。

</details>

<details>
<summary>单线程 vs multi-agent (Cognition)：【技术机制】context 完整性论证</summary>

**论点**：agent 可靠性 = context 完整性。两条原则：
1. **Share full context and traces**——subagent 只拿到一条子任务描述时，会丢掉「为什么做这个」的隐式约束（原文例子：两个 subagent 各自实现 Flappy Bird 的一半，风格/假设完全冲突，合不起来）。
2. **Actions carry implicit decisions**——并行 agent 各自做的决策彼此不可见，冲突不可避免；把「decisions 也要传递」做到位的成本 ≈ 放弃并行。

**推荐架构**：单线程连续 agent，context 线性增长；超过 window 就用**专门训练/提示的 compressor model** 把历史蒸馏成 key details/decisions/facts 再续——即「压缩后自我交接」而不是「交接给别人」。

**与 Anthropic multi-agent research system 的张力**（面试必被追问）：Anthropic 的 research 系统用 orchestrator + 并行 subagent 有效，因为 research 是**读为主、可切分、结果可合并**（各 subagent 的发现互不冲突）；coding 是**写为主、强耦合**，Cognition 的论证在此成立。正确答案不是站队，而是给出判据：**子任务间的写冲突面积**决定能不能并行。

**失败模式**：单线程方案的天花板是 compressor 的质量——压缩即有损，和 compaction 的熵衰减是同一个问题，只是把赌注全押在一次高质量蒸馏上。

</details>

<details>
<summary>OpenHands context condenser：【技术机制】event stream 上的可插拔视图</summary>

**机制**：OpenHands 把 session 建模为 append-only **event stream**（所有 action/observation 都是 event，本身就是 durable state）。condenser 是 stream 之上的**视图**：conversation 超过 `max_size` 后，`LLMSummarizingCondenser` 保留最早 `keep_first` 条 events（含 user intent）+ 最近一段，把中间的 events 交给 LLM 总结成**一条 summary event** 插回视图。摘要 prompt 显式编码三件事：user goals / progress so far / what remains。

```python
def condensed_view(events, max_size, keep_first):
    if len(events) <= max_size: return events
    head = events[:keep_first]                    # user intent 永不丢
    tail = events[-(max_size - keep_first - 1):]
    middle = events[keep_first:-len(tail)]
    return [*head, SummaryEvent(llm_summarize(middle)), *tail]
```

**关键设计**：原始 events **不删**——condensation 只影响送给模型的 view，完整 stream 仍可回放/审计/重新 condense。这比「直接改写 message history」的 compaction 干净：durable state 和 conversation state 天然分离（正是第 1 节的原则）。condenser 可插拔：recent-events（纯截断）、LLM summarizing、amortized forgetting 等策略可换。

**结果**（官方博客 claim）：SWE-bench 上成本显著降低而 resolve rate 基本不降。

**失败模式**：和一切摘要方案相同——中段细节有损；另外 summary event 插入会破坏该点之后的 KV-cache 前缀（Manus 会不同意这个设计）。

</details>

## 9. 自学资料

按优先级排序，前 4 条是面试前必读：

1. [Effective context engineering for AI agents](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents) — Anthropic 官方框架：compaction / structured note-taking / sub-agent 三板斧，长任务 context 管理的最佳总纲 · 预计 20 min
2. [Context Engineering for AI Agents: Lessons from Building Manus](https://manus.im/blog/Context-Engineering-for-AI-Agents-Lessons-from-Building-Manus) — 生产 agent 的六条实战经验：KV-cache、file system as context、recitation、保留错误，全是面试可直接引用的细节 · 预计 15 min
3. [Don't Build Multi-Agents](https://cognition.com/blog/dont-build-multi-agents) — Cognition 的 context 完整性论证，single-thread vs multi-agent 争论的一极，必须能复述并反驳 · 预计 10 min
4. [Effective harnesses for long-running agents](https://www.anthropic.com/engineering/effective-harnesses-for-long-running-agents) — initializer / feature_list.json / progress 文件 / git checkpoint 的完整配方 · 预计 15 min
5. [MemGPT: Towards LLMs as Operating Systems](https://arxiv.org/abs/2310.08560) — memory 分层 + self-editing 的原始论文，后续所有 memory 系统都在回应它 · 预计 30 min
6. [Zep: A Temporal Knowledge Graph Architecture for Agent Memory](https://arxiv.org/abs/2501.13956) — bitemporal 边 + 时间失效的冲突处理，看 §2 架构即可 · 预计 25 min
7. [Mem0: Building Production-Ready AI Agents with Scalable Long-Term Memory](https://arxiv.org/abs/2504.19413) — extraction→update 两阶段 pipeline 和 LOCOMO 成本数字，读 §3 方法 + §5 结果 · 预计 25 min
8. [Temporal: Workflow Execution Events](https://docs.temporal.io/workflow-execution/event) — event history / replay / determinism 的官方定义，durable execution 面试题的标准出处 · 预计 15 min
9. [Claude Code: How Claude remembers your project](https://code.claude.com/docs/en/memory) — CLAUDE.md 层级 + auto memory 的完整机制，文件式 memory 的参考实现 · 预计 10 min
10. [LongMemEval: Benchmarking Chat Assistants on Long-Term Interactive Memory](https://arxiv.org/abs/2410.10813) — 5 项 memory 能力的评测框架，聊「memory 怎么评」时的引用 · 预计 15 min
