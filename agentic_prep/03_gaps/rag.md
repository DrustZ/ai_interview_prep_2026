# RAG / Retrieval 设计

⏱ 骨架 8 min ｜ 含深潜与资料 40 min ｜ 面试前只看 ⭐⭐⭐ 部分

## 30 秒版本（3 句话）

1. 生产级 RAG 是两阶段检索系统：hybrid recall（BM25 + 向量，RRF 融合）拿 top-50~100，cross-encoder rerank 压到 top-5~10——检索质量瓶颈几乎总在排序层，而不是换 embedding。
2. 企业场景三件事把玩具 demo 和真产品分开：ACL 检索前过滤（不是生成后删）、citation 的 claim→span 映射、增量索引保 freshness。
3. 评测拆成检索（recall@k / NDCG）和生成（faithfulness / answer relevance）两段分别归因；2025 后趋势是 agentic RAG——multi-hop 问题让模型自己决定检索几轮，但简单问题 classic 单轮更快更便宜。

## 核心概念 ⭐⭐⭐

| 概念 | 要点 | 面试一句话 |
|---|---|---|
| Chunking | 固定窗口（512-1024 token + 10-20% overlap）是 baseline；语义切分按 embedding 相似度找断点；结构感知按 Markdown/HTML 标题层级切、标题路径写进 chunk metadata | 「chunk 边界切错是 recall 掉点头号来源；结构感知 > 语义 > 固定」 |
| Hybrid search | BM25 抓精确词（型号/人名/错误码），dense 抓语义，RRF 融合：$\text{RRF}(d)=\sum_i \frac{1}{k+r_i(d)}$，$k\approx 60$ | 「dense 对 out-of-domain 术语必挂，hybrid 是默认不是可选」 |
| 两阶段 rerank | 召回 top-50~100 → cross-encoder 精排 top-5~10；2025-26 主流：Cohere Rerank 3.5（托管）、BGE-reranker-v2-m3（开源）、zerank | 「top-50 里有答案但 top-5 没有 → 加 reranker 比换 embedding 收益大」 |
| Embedding 选型 | 托管：Voyage-3 / OpenAI text-embedding-3 / Cohere Embed-3；开源：Qwen3-Embedding / BGE-M3（dense+sparse 双输出、多语言） | 「先托管跑通，再拿自己语料 50-200 条真实 query 评测决定换不换」 |
| Citation 架构 | 生成时要求 per-claim 标 chunk id → 后处理把 claim 映射回原文 span → 校验 span 真实存在（防幻觉引用） | 「citation 是可验证性架构，不是 UI 装饰」 |
| ACL 前置过滤 | 权限作为 metadata filter 在 ANN 检索时生效（pre-filter）；生成后删 = 泄露已发生，内容进过 context | 「permission-aware retrieval，不是 permission-aware generation」 |
| Freshness / 增量索引 | 文档变更走 CDC/webhook → 只重嵌变更 chunk → upsert + tombstone 或索引双缓冲；ACL 变更走同一条管道 | 「索引要当流式系统运维，全量重建是 batch 时代思维」 |
| Agentic RAG | 模型自主 query rewrite、决定检索轮数、多跳串联；multi-hop 上胜 classic RAG，简单问题上纯烧延迟和 token | 「按问题复杂度路由：简单单轮，multi-hop 才 agentic」 |

## 面试常问 3 题 ⭐⭐⭐

### Q1：设计一个企业知识助手（enterprise ChatGPT / Glean 类）

真题锚点：OpenAI 题库 A 类（[Design a RAG-Based Chatbot System](../../online_resource/1p3a-openai.md)，明确考 multi-tenant + permission + citation + eval）。

<details><summary>参考打法</summary>

- 开场画三条独立管道：Ingestion（connector → 结构感知 chunking → embedding → 索引 + ACL metadata）、Retrieval（query rewrite → hybrid recall → pre-filter → rerank）、Generation（grounded prompt → citation 后校验）；强调三者扩缩容曲线、失败模式、评测方法都不同，必须解耦。
- Ingestion 讲增量：CDC/webhook 触发，只重嵌变更 chunk；ACL 变更同管道，撤权分钟级生效。
- Retrieval 主动给数字：recall 阶段 top-100，rerank 后 top-8 进 context，检索 P95 < 500ms；embedding 与热门 query 加 cache。
- 企业三板斧不等追问：tenant 隔离（namespace/独立索引）、ACL pre-filter、audit log——这是面试官区分"做过玩具"和"做过产品"的信号。
- 收尾谈 eval + 运营闭环：标注集回归测 retrieval recall，LLM judge 测 faithfulness，线上 citation 点击率 + 用户反馈。

</details>

> 高分句：「我会把它设计成三条独立管道——ingestion、retrieval、generation——因为它们的扩缩容曲线、失败模式和评测方法完全不同。」

### Q2：怎么评测一个 RAG 系统？

<details><summary>参考打法</summary>

- 第一步永远是归因拆分：答案错，是没检到（retrieval 问题）还是检到了没用对（generation 问题）？两段分开测才能定位改哪里。
- 检索侧：recall@k、MRR、NDCG——2025 共识是 NDCG 与端到端质量相关性最强（rank 位置影响模型注意力）；标注集从真实 query 采样 + 人工标 golden chunks。
- 生成侧 RAGAS 三件套：faithfulness（逐 claim 验证能否被 context 支撑，LLM judge）、answer relevance、context precision/recall。
- 离线回归进 CI：改 chunking/embedding/prompt 前后跑同一评测集，防 silent regression；这和 agent eval harness 是同一套纪律。
- 线上信号：citation 点击率、thumbs、escalation 率；agentic RAG 额外看 trace 级指标，如 retrieves-per-correct-answer 控检索轮数成本。

</details>

> 高分句：「评测第一原则是归因隔离：retrieval recall 决定天花板，faithfulness 决定你离天花板多远。」

### Q3：权限与多租户怎么处理？

<details><summary>参考打法</summary>

- 原则先立住：ACL 必须在检索阶段 pre-filter；任何"生成后过滤"等于泄露——未授权内容一旦进 context，就可能被 prompt injection 或改述带出。
- 实现：chunk metadata 存 allowed_principals，查询时用用户的 group 展开集合做 filtered ANN（pgvector/Qdrant 等原生支持）；filter 选择性太高时 ANN recall 会掉，要调 ef_search/nprobe 或走 brute-force fallback。
- ACL 同步是真正难点：源系统（Drive/Confluence/Slack）权限变更 → webhook/定期 diff → 更新 metadata，明确撤权 SLA（分钟级）；group 展开放 ingestion 还是 query time，讲清存储 vs 查询延迟的 trade-off。
- 多租户分层：大客户独立索引/namespace（物理隔离，合规驱动），长尾客户共享索引 + tenant_id 强制 filter（代码层默认注入，不靠调用方自觉）。
- 加分项：semantic cache 的泄露面（命中别人问题的答案）、audit log（谁检索了什么，合规审计用）。

</details>

> 高分句：「权限过滤的位置决定它是安全边界还是装饰——pre-filter 是安全边界，post-filter 是装饰。」

## 常见坑 ⭐⭐

- [ ] 只说 vector search 不提 BM25/hybrid——精确术语查询必挂，面试官必追问
- [ ] 把 citation 说成 UI 功能——要讲 claim→span 映射 + span 存在性校验
- [ ] 权限放生成后处理——一句话暴露没做过企业场景
- [ ] 评测只说 "LLM as judge"——没有 retrieval/generation 分段归因等于没做过 eval
- [ ] 张口就 agentic RAG 多轮检索——不谈延迟/成本、不做复杂度路由，等于没有工程判断

## 现有系统怎么做 ⭐⭐

各环节业界代表性做法一览，细节展开在折叠块里（每块含数据结构、流程、伪码、参数、失败模式）。

| 系统 / 方法 | 核心机制一句话 | 适用场景 | 链接 |
|---|---|---|---|
| Contextual Retrieval（Anthropic） | ingestion 时用 Haiku 给每个 chunk 生成 50-100 tok 上下文前缀，再做 embedding + BM25 双索引 | chunk 脱离全文即有歧义的语料（财报、合同、代码），<200k tok/文档 | [blog](https://www.anthropic.com/engineering/contextual-retrieval) |
| Chunking 实证（Chroma） | 用 token 级 recall/precision/IoU 评测各类 chunker，结论：框架默认参数往往最差 | 定 chunk 大小/overlap/切分器之前 | [report](https://www.trychroma.com/research/evaluating-chunking) |
| Hybrid + RRF（Elastic/Weaviate/Qdrant） | BM25 与 dense 各出一个 ranked list，按 $\sum 1/(k+r_i)$ 融合，k=60，免调参 | 默认检索层，任何含精确词的查询 | [Elastic docs](https://www.elastic.co/docs/reference/elasticsearch/rest-apis/reciprocal-rank-fusion) |
| Cross-encoder rerank（Cohere / BGE） | query+doc 拼接过 full attention 出相关性分，只精排 recall 出的 top-50~150 | recall 里有答案但 top-5 没有；两阶段第二级 | [Cohere](https://docs.cohere.com/docs/rerank-overview) · [BGE](https://github.com/FlagOpen/FlagEmbedding) |
| GraphRAG（Microsoft） | LLM 抽实体建图 → Leiden 社区检测 → 预生成社区摘要，全局问题 map-reduce 摘要作答 | "这批文档整体在讲什么"类 global sensemaking；point lookup 不适用 | [arXiv](https://arxiv.org/abs/2404.16130) |
| Agentic search（Anthropic multi-agent research） | 把检索作为 tool 给 agent，循环：出 query → 评估结果 → 改写/分解 → 再检索；orchestrator 派并行 subagent | multi-hop、开放式调研；简单事实题纯烧钱 | [blog](https://www.anthropic.com/engineering/multi-agent-research-system) |
| 去向量化 / 文件式（Claude Code、OpenClaw） | 不建 embedding 索引：grep/FTS + 结构化 markdown（写入时组织代替读取时搜索），agent 多轮迭代补精度 | 有结构语料（代码库、个人 memory）、agent 有时间预算、要求可审计可版本化 | [OpenClaw memory](https://docs.openclaw.ai/concepts/memory) |
| RAGAS 评测 | LLM judge 把 answer/reference 分解成 atomic claims 逐条对 context 验证，比例即分数 | 无大规模人工标注时的离线回归 | [docs](https://docs.ragas.io/en/stable/concepts/metrics/available_metrics/faithfulness/) |

<details><summary>Contextual Retrieval：技术机制</summary>

**问题**：chunk 切开后丢失指代——"该公司收入增长 3%"这个 chunk 不含公司名和季度，dense/BM25 都检不到。

**处理流程**：ingestion 时对每个 chunk 调一次小模型，输入【整篇文档 + 该 chunk】，生成一段定位性上下文，前缀拼接后再进两个索引（contextual embeddings + contextual BM25）。

```python
CTX_PROMPT = """<document>{full_doc}</document>
Here is the chunk we want to situate within the whole document
<chunk>{chunk}</chunk>
Please give a short succinct context to situate this chunk within
the overall document for the purposes of improving search retrieval
of the chunk. Answer only with the succinct context and nothing else."""

def ingest(doc):
    for c in chunk(doc, max_tokens=800):
        # full_doc 放 prompt 头部 → prompt caching 命中，成本约 $1.02 / M doc tokens
        ctx = haiku(CTX_PROMPT.format(full_doc=doc.text, chunk=c.text))  # 50-100 tok
        text = ctx + "\n" + c.text
        vec_index.upsert(c.id, embed(text), meta=c.meta)
        bm25_index.add(c.id, tokenize(text))   # BM25 也用加前缀后的文本，这是 contextual BM25
```

**关键数字**（Anthropic 内部评测，top-20 检索失败率，baseline 5.7%）：
- contextual embeddings 单独：-35%（→3.7%）
- + contextual BM25：**-49%**（→2.9%）
- + rerank（top-150 → top-20）：**-67%**（→1.9%）
- top-20 进 context 优于 top-5/top-10；embedding 推荐 Voyage/Gemini

**为什么这样设计**：比 HyDE/摘要索引更直接——不改查询侧、不换索引结构，只改被索引的文本本身；prompt caching 让"每个 chunk 都读一遍全文"从不可行变成 $1/M tokens。

**失败模式**：文档超过 context window 要先分段（丢跨段上下文）；文档一变全部 chunk 的 context 都要重生成（增量索引成本翻倍）；对本就 self-contained 的 chunk（FAQ、API doc）收益接近零。

</details>

<details><summary>Chunking：Chroma 实证结论 + chunker 伪码</summary>

**评测方法**：不用文档级 hit rate，用 token 级指标——golden answer 对应原文 span，算检回 token 与 golden token 的 recall / precision / IoU（token 级 Jaccard，惩罚冗余）。472 条合成 query，5 个语料。

**核心发现**：
- OpenAI 默认参数（800 tok + 400 overlap）表现垫底——**框架默认值不可信**
- 去掉 overlap 反而提升 IoU（overlap 制造冗余 token，挤占 context 预算）
- ClusterSemanticChunker（max 200 tok）precision/IoU 最高；LLMSemanticChunker recall 最高（91.9%）
- 但各方法 recall 差距远小于参数选错的损失 → 先调大小，再换算法

```python
SEPS = ["\n## ", "\n### ", "\n\n", "\n", ". ", " "]   # 结构优先，逐级降级

def recursive_split(text, max_tok=400, seps=SEPS):
    if count_tokens(text) <= max_tok:
        return [text]
    for sep in seps:
        parts = text.split(sep)
        if len(parts) > 1:
            pieces = [recursive_split(p, max_tok, seps) for p in parts]
            return merge_greedy(flatten(pieces), max_tok)  # 相邻小片贪心合并到上限
    return hard_split(text, max_tok)   # 兜底：按 token 硬切

# ClusterSemanticChunker（Chroma）：先切 ~50 tok 微片 → 各自 embed →
# 在 max_tok 约束下动态规划合并相邻微片，最大化簇内 pairwise cosine 之和
# LLMSemanticChunker：给 LLM 带编号的微片，让它直接输出断点位置
```

**参数经验值**：200-400 tok 检索效率最优（Chroma 数据）；业界常用 400-800 tok 兼顾生成侧可读性；overlap 0-15%，别无脑 50%；结构感知切分时把标题路径（`H1 > H2 > H3`）写进 chunk 前缀或 metadata。

**失败模式**：表格/代码块被从中间切断（要按块类型保护）；语义切分对结构化文档（Markdown 文档、合同条款）不如直接按标题层级切。

</details>

<details><summary>Hybrid + RRF：融合公式与实现</summary>

**数据结构**：两条并行索引——倒排索引跑 BM25（k1≈1.2, b≈0.75），HNSW 跑 dense ANN（建图参数 M≈16-64，查询参数 ef_search 控 recall/延迟）。

**为什么用 rank 不用 score 融合**：BM25 分数无上界、cosine 在 [-1,1]，分布形状随 query 变化，线性加权前必须归一化（min-max/z-score）且权重对 query 敏感。RRF 只看名次，免调参：

$$\text{RRF}(d) = \sum_{i} \frac{1}{k + r_i(d)}, \quad k = 60$$

```python
from collections import defaultdict

def rrf_fuse(ranked_lists: list[list[str]], k: int = 60, weights=None) -> list[str]:
    weights = weights or [1.0] * len(ranked_lists)
    scores = defaultdict(float)
    for w, ranking in zip(weights, ranked_lists):
        for rank, doc_id in enumerate(ranking, start=1):
            scores[doc_id] += w / (k + rank)
    return sorted(scores, key=scores.get, reverse=True)

candidates = rrf_fuse([
    bm25.search(query, top_k=100),
    ann.search(embed(query), top_k=100),
])[:100]   # → 交给 reranker
```

**k 的含义**：k 越小越奖励头部名次（rank1 vs rank10 差距拉大）；k=60 是原论文经验值，各家默认沿用。文档同时出现在两个列表会得到叠加 boost——这正是 hybrid 想要的行为。

**失败模式**：RRF 对两路 retriever 平权，一路很差会拖累整体（可上 weighted RRF，Elasticsearch 有此提案）；两路 top-k 太小时交集稀疏、融合退化为拼接；Weaviate v1.24 起默认改用 relative score fusion（归一化后加权），对分数分布稳定的场景排序更细。ACL pre-filter 必须同时作用于两条索引，漏一条就是泄露。

</details>

<details><summary>Rerank：cross-encoder vs bi-encoder + 截断策略</summary>

**架构差异**（这是面试必讲点）：
- **bi-encoder**：query 和 doc 各自独立编码成向量，doc 向量离线预计算，query time 只算一次 embedding + ANN 查找 → 可扩展到亿级文档，但 query-doc 交互只剩一个点积。
- **cross-encoder**：`[CLS] query [SEP] doc` 拼接后整体过 transformer，每层 full attention 都在做 query-doc token 级交互，输出一个 relevance logit → 精度显著更高，但每个候选对都要一次 forward，无法预计算，只能当第二阶段。

```python
from FlagEmbedding import FlagReranker
reranker = FlagReranker('BAAI/bge-reranker-v2-m3', use_fp16=True)

def rerank(query, cands, top_n=8, floor=0.3):
    scores = reranker.compute_score(
        [[query, doc_text(d)] for d in cands],  # 每对一次 forward，GPU 上 batch
        normalize=True)                          # sigmoid(logit) → [0,1]
    ranked = sorted(zip(cands, scores), key=lambda x: -x[1])
    kept = [d for d, s in ranked[:top_n] if s >= floor]  # top-n + 分数下限双截断
    return kept or [ranked[0][0]]   # min-1 保底，避免空 context 触发幻觉
```

**参数经验值**：recall top-50~150 进 rerank，出 top-5~10；rerank 延迟随候选数线性增长，P95 预算内 top-100 是常见上限；托管选 Cohere Rerank（API 返回 relevance_score，v4.0 系列，100+ 语言），开源选 BGE-reranker-v2-m3。

**失败模式**：doc 超过模型窗口（多为 512-8k tok）要截断或滑窗取 max 分；分数跨 query 不可比——floor 阈值必须在自己的评测集上校准，不能拍脑袋；listwise LLM reranker（RankGPT 类）精度再高一档但延迟/成本又上一个量级，只适合离线或高价值查询。

</details>

<details><summary>GraphRAG：索引与 global query 流程</summary>

**动机**：classic RAG 只能答"答案存在于某几个 chunk"的问题；"这个数据集的主要主题是什么"没有任何 chunk 直接包含答案，需要全局归纳（query-focused summarization）。

**处理流程**：

```python
# ---- Index time（贵，一次性）----
for chunk in corpus:
    entities, relations = llm_extract(chunk)   # 多轮 "gleaning" 追问提高抽取召回
graph = build_graph(entities, relations)       # 节点=entity，边=relation，权重=共现频次
communities = leiden(graph, hierarchical=True) # 多层级社区（C0 粗 → C3 细）
for c in communities:
    c.summary = llm_summarize(c.nodes, c.edges) # 预生成社区摘要，按度数优先填 token 预算

# ---- Query time：global mode = map-reduce over summaries ----
partials = parallel(
    llm(f"仅基于此社区摘要回答：{q}\n{c.summary}\n并给 0-100 helpfulness 分")
    for c in communities_at_level(L))           # map：每个摘要出 partial answer + 自评分
answer = llm(f"综合以下 partial answers 回答 {q}", top_scoring(partials))  # reduce

# local mode：query 中的 entity 匹配图节点 → 邻域扩展拉相关实体/关系/原文 chunk
```

**结果**（arXiv 2404.16130）：1M token 级语料的 global sensemaking 问题上，comprehensiveness 和 diversity 显著优于 vector RAG baseline；用粗层级社区（C0）可大幅省 token。

**适用边界（面试要主动说）**：indexing 每个 chunk 多次 LLM 调用，成本比 vector RAG 高 1-2 个量级；语料更新要增量重抽取 + 重跑社区检测，freshness 差；point lookup（"X 的电话是多少"）无优势甚至更差。正确姿势是按 query 类型路由：global 问题走 GraphRAG，事实检索走 hybrid+rerank。

</details>

<details><summary>Agentic search：迭代检索 loop 与成本控制</summary>

**与单次 RAG 的区别**：单次 RAG 是 `query → retrieve → generate` 固定管道；agentic search 把 retrieval 作为 tool 暴露给模型，模型自己决定搜什么、搜几轮、什么时候停。

```python
def agentic_retrieve(question, max_turns=5):
    notes = []
    for turn in range(max_turns):                # hard budget，防 agent 无限搜
        step = llm(f"目标：{question}\n已有发现：{notes}\n"
                   f"输出下一条检索 query（先宽后窄），或确认信息足够时输出 DONE")
        if step == "DONE":
            break
        results = hybrid_search(step, top_k=10)
        notes.append(llm("提取与目标相关的事实；评估还缺哪块信息", results))
    return llm_answer(question, notes)           # 带 citation 生成
```

**Anthropic multi-agent research 的做法**：orchestrator-worker——lead agent 把研究问题分解成子任务，spawn 多个并行 subagent 各自跑上面这种 search loop，用 interleaved thinking 评估工具结果质量；比单 agent Opus 4 在内部 research eval 上 +90.2%。

**关键 prompt 工程**（都来自看 trace 发现的失败模式）：
- scale effort to complexity：简单事实题 1 个 agent、3-10 次工具调用；开放调研才开多 agent
- start wide, then narrow：先短宽 query 摸清语料分布，再收窄
- 显式教 agent 停止条件，否则它会在信息足够后继续搜（over-searching）、重复相同 query

**失败模式/成本**：multi-agent 任务 token 消耗约为 chat 的 15 倍——没有 complexity routing 直接上 agentic 是工程判断不及格；延迟从百 ms 变成分钟级，只适合异步/高价值场景；评测要加 trace 级指标（每正确答案的检索轮数）。

</details>

<details><summary>2025–26 分水岭：去向量化（Claude Code 删掉向量库、OpenClaw 文件式 memory）</summary>

**标志性事件**：Claude Code 在 2025-05 移除了向量检索——整条 embedding/分块/本地向量库管线换成 grep/glob + 多轮文件读取（作者 Boris Cherny：效果 "outperformed everything, by a lot"）。随后 Cursor、Windsurf、Cline、Devin、Amp 相继放弃代码库向量索引，转向 tool-driven search。一篇 AAAI 2026 的 Amazon 论文测得 agentic 关键词搜索达到 embedding RAG faithfulness 的 ~94.5%，零向量库。

**OpenClaw 模式**（文件式 memory 的代表）：`MEMORY.md`（长期事实索引）+ `memory/YYYY-MM-DD.md`（每日笔记），磁盘 markdown 是唯一事实源、无隐藏状态，git 可版本化、可手工纠错。细节：它的 `memory_search` 配置了 embedding 时仍做 hybrid（向量+关键词），没配置就退回 FTS——**连 OpenClaw 也不是"无检索"，而是"文件为事实源，检索仅是可选加速器"**。

**本质**：把 read-time search 换成 write-time organization——与其切碎原文埋进向量空间指望相似度捞回，不如写入时就组织成结构化摘要（MEMORY.md 就是索引页），grep/FTS + agent 迭代就够。成立前提：① long context + prompt caching 变便宜；② 模型多轮工具使用质变（会自己改写 query、评估、再搜）；③ 免掉 embedding 索引的运维债（同步、失效、权限镜像）。

**边界（面试必说）**：百万级文档、交互延迟 <2s、多租户 ACL、需要语义改写召回的场景，index-based hybrid 仍是唯一解——grep 扫不动 10M 文档的延迟预算。决策谱系：<200k tok 直接进 context → 有结构语料 + 时间预算 → agentic/文件式 → 大规模/低延迟/ACL → hybrid 索引 → 合成态 agentic RAG（索引只是 agent 的一个 tool）。

**面试一句话**：不答"RAG 已死"也不默认向量库——先问规模/延迟/权限三个变量，再给谱系；提 Claude Code 删向量库作为趋势证据，提 ACL/规模作为索引不可替代的证据。

</details>

<details><summary>RAGAS 指标：每个指标到底怎么算</summary>

**faithfulness**（生成是否被 context 支撑）：

```python
def faithfulness(answer, contexts):
    claims = llm(f"把回答分解成可独立验证的原子陈述：{answer}")      # step1 claim 分解
    verdicts = [llm(f"该陈述能否仅由以下 context 推出？(0/1)\n"
                    f"context={contexts}\nclaim={c}") for c in claims]  # step2 逐条验证
    return sum(verdicts) / len(claims)                                # 支撑数 / 总数
```

例：answer 含 2 个 claim，1 个被 context 支撑 → faithfulness = 0.5。

**answer relevance**（答案是否对题）：LLM 从 answer **反向生成** n 个可能的问题，取各生成问题与原问题 embedding cosine 的均值——答非所问时反向问题会偏离原问题。

**context recall**（该检回的检回了吗）：把 ground-truth reference 答案分解成 claims，逐条判断能否归因于 retrieved context，比例即分。四个指标里**唯一需要 ground truth**，所以是离线回归指标，不能上线上。

**context precision**（检回的都相关吗）：逐 chunk 让 judge 判断是否与回答该问题相关，按 rank 加权（相关 chunk 排得越靠前分越高）——本质是 mean precision@k。

**归因用法**：context recall 低 → 修 retrieval（chunking/hybrid/rerank）；recall 高但 faithfulness 低 → 修 generation（grounding prompt/citation 校验）。

**坑**：judge model 有自偏好和位置偏差，换 judge 分数不可比；claim 分解本身不稳定（同一 answer 两次分解数量不同），指标有噪声——用于回归对比（同一评测集 A/B）可靠，绝对值别当真；定期抽样人工标注校准 judge 一致性。

</details>

## 自学资料

按优先级排序，前 4 条覆盖面试 80% 的追问。

1. [Introducing Contextual Retrieval（Anthropic Engineering）](https://www.anthropic.com/engineering/contextual-retrieval) — 完整方法 + 消融数字（-49%/-67%）+ 附录里有各 embedding/语料组合的实验表，面试引用数字的第一来源 · 15 min
2. [Evaluating Chunking Strategies for Retrieval（Chroma Research）](https://www.trychroma.com/research/evaluating-chunking) — 唯一系统性的 chunking 实证，token 级评测方法本身也值得学 · 20 min
3. [How we built our multi-agent research system（Anthropic Engineering）](https://www.anthropic.com/engineering/multi-agent-research-system) — agentic search 的架构、prompt 工程细节、15x token 成本数字，讲 agentic RAG 边界时的论据库 · 20 min
4. [Ragas: Faithfulness（官方 docs）](https://docs.ragas.io/en/stable/concepts/metrics/available_metrics/faithfulness/) — 指标计算步骤与示例，顺着侧栏把 context precision/recall 两页也过一遍 · 10 min
5. [From Local to Global: A Graph RAG Approach to Query-Focused Summarization（arXiv 2404.16130）](https://arxiv.org/abs/2404.16130) — GraphRAG 原论文，重点读 §2 pipeline 和实验设置，明确它解决的是 sensemaking 而非 lookup · 25 min
6. [Reciprocal rank fusion（Elasticsearch Reference）](https://www.elastic.co/docs/reference/elasticsearch/rest-apis/reciprocal-rank-fusion) — RRF 公式、rank_constant/window_size 参数与 retriever API 用法，生产实现长什么样 · 10 min
7. [FlagOpen/FlagEmbedding（GitHub）](https://github.com/FlagOpen/FlagEmbedding) — BGE-M3（dense+sparse 双输出）与 bge-reranker-v2-m3 的用法和微调脚本，开源检索栈事实标准 · 15 min
8. [Rerank Overview（Cohere docs）](https://docs.cohere.com/docs/rerank-overview) — 托管 rerank API 的输入输出形态与 relevance_score 语义，对比自托管时用 · 5 min
9. [Hybrid search 概念（Weaviate docs）](https://docs.weaviate.io/weaviate/concepts/search/hybrid-search) — RRF vs relative score fusion 两种融合的差异与默认值变迁，回答"除了 RRF 还有什么"的追问 · 10 min
10. [brandonstarxel/chunking_evaluation（GitHub）](https://github.com/brandonstarxel/chunking_evaluation) — Chroma 报告配套代码，ClusterSemanticChunker/LLMChunker 实现可直接读源码 · 10 min
11. [OpenClaw docs: Memory overview](https://docs.openclaw.ai/concepts/memory) — 文件式 memory 的一手规范（MEMORY.md/每日笔记/hybrid memory_search 细节），"写入时组织"流派代表 · 10 min
12. [Milvus: We extracted OpenClaw's memory system (memsearch)](https://milvus.io/blog/we-extracted-openclaws-memory-system-and-opensourced-it-memsearch.md) — 向量库厂商视角拆解文件式 memory 何时够用、何时需要索引，两边论据都齐 · 10 min

## 相关

- 系统设计答题框架：[../02_playbook.md](../02_playbook.md)（题型七 RAG/知识 agent）
- Memory 实现流派（文件式/图谱/pipeline 对比）：[../01_core/02_state_and_memory.md](../01_core/02_state_and_memory.md)
- OpenAI 真题原文与 tips：[1p3a-openai.md](../../online_resource/1p3a-openai.md)
