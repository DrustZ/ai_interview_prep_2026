# 20 · Exa 第二轮技术面：agentic search 的 retrieval / reranking / snippet / alignment

⏱ 通读 35 分钟 ｜ 面试前只看 §2 事实卡 + §9 时间分配 + §13 速记（合计 8 分钟）
📅 建于 2026-07-29，面向 **Exa 第二轮 45 分钟技术面**（team-specific，often systems design）

---

## 0. 这轮是什么 · 和其他文件的边界

### 已知事实（recruiter 原文 + 你第一轮实测）

| 项 | 内容 |
|---|---|
| 轮次 | 第二轮技术面，**45 分钟**，另一位工程师 |
| 官方描述 | "a more team specific question, that is **often systems design**" |
| 面试官 | **Joshua Yurtsever**，Exa ML researcher（前 Google） |
| 他的 LinkedIn 自述 | "Building **production retrieval and post-training systems** for LLM-powered **agentic search**, including **reranking**, **snippet generation**, and **model alignment**" |
| 后续 | leadership 轮 → **2 天 in-person paid work trial**（这轮是通往 work trial 的门） |
| recruiter 主动给的读物 | [exa.ai/blog/webcode](https://exa.ai/blog/webcode) |

**第一轮实际考了什么（2026-07-28，你的实测）**：不是 PyTorch，不是 LeetCode，是一道**流式分位数**题 ——
给一个 stream，返回任意 percentile。你的路径：全排序 → 压缩空间 → 分桶 → 引入误差容忍 → **log 分桶算 index**。
这就是 DDSketch / t-digest 的推导路线，答对了。

> ⚠️ **这修正了 [labs/exa_drills/README](labs/exa_drills/README.md) 的预测**。那份 FAQ 说第一轮是 "live coding related to what we do at Exa"，
> 我们默认成了检索指标 / InfoNCE。实际出的是**近似算法 + 空间/精度权衡**。
> 含义：**Exa 的题偏「工程判断力」而不是「ML 配方背诵」**。第二轮按这个基调准备。

### 和已有材料的分工

| 文件 | 覆盖什么 | 这轮还用得上吗 |
|---|---|---|
| [06_search_post_training.md](06_search_post_training.md) | retriever/reranker/answerer 怎么**训**、click bias、hard negative、四层 eval | ✅ 训练侧弹药库，本文不重复，直接引 |
| [13_company_cards.md](13_company_cards.md) | Exa 公司卡、open evals 方法论 | ✅ 面试前 90 秒扫一遍 |
| [labs/exa_drills/](labs/exa_drills/) | 冷写题包（指标 / 向量 / InfoNCE / judge 一致率 / **流式分位数**） | ⚠️ 这轮是 design，drill 只做热身 |
| [08_evaluation_production.md](08_evaluation_production.md) | cascade、cost/success、上线实验 | ✅ §4 级联部分直接复用 |
| **本文** | **Exa 全栈一手事实 + 四道最可能的 design 题的完整答案 + 延迟预算算术** | — |

**本文只做一件事**：把 Joshua 那三个关键词（reranking / snippet generation / model alignment）
各配一套能讲 15 分钟的完整设计，并且**每个数字都能算给他看**。

---

## 1. 面试官画像：三个关键词把题面收得很窄

他自述的三件事，在 Exa 的产品里各有明确对应物：

| 他说的 | Exa 里的东西 | 一手来源 |
|---|---|---|
| **reranking** | 自研 reranker（"our own re-ranker"），在 Canon 里是 retrieval 之后的一个 node | [ZenML 访谈](https://www.zenml.io/llmops-database/building-a-search-engine-for-ai-agents-infrastructure-product-development-and-production-deployment)、[composing-a-search-engine](https://exa.ai/blog/composing-a-search-engine) |
| **snippet generation** | **Exa Highlights** —— 这是他领域里最独特、外部最少人准备的一块 | [highlights-for-agents](https://exa.ai/blog/highlights-for-agents)、[scaling-our-highlights-server](https://exa.ai/blog/scaling-our-highlights-server) |
| **model alignment** | 用 Dr. GRPO 训 search agent；以及 search 质量如何反过来决定 RL 的样本效率 | [rl-search-outcomes](https://exa.ai/blog/rl-search-outcomes) |
| （隐含）**production** | Canon DAG 编排、Instant 亚 200ms、exa-d 数据框架 | [exa-d](https://exa.ai/blog/exa-d)、[exa-instant](https://exa.ai/blog/exa-instant) |

**我的判断（推断，不要说成事实）**：
最可能的题是 **「设计 Exa 的 highlights / snippet 服务」** 或 **「给 agentic search 设计 reranking 这一层」**，
因为这两个是他本人在做的，他能判断你答得深不深。
第二梯队是「怎么训/评一个 web search 的 reranker」和「端到端设计一个 agentic search endpoint」。

**押注策略**：§3（highlights）和 §4（reranker）**必须能不看稿讲完**；§5、§6 能讲七成即可。

---

## 2. 【一手】Exa 全栈事实卡 ⭐⭐⭐

这一节是本文杠杆最高的部分。**能在设计里随口引用他们自己的数字，等于免掉半小时的信任建立**。
全部来自官方博客，可以直接说"你们博客里写的"。

### 2.1 一张图：从网页到 agent 的完整栈

```
                        ┌─────────────────────────────────────┐
  crawl  ─────────────▶ │ exa-d：Lance on S3 + Ray Data       │  数千亿页 / PB 级
                        │ 列式 DAG，改一列不重写整个 fragment  │  更新频率 小时级→永不
                        └───────────────┬─────────────────────┘
                                        │ 每页派生几十个 artifact
                        ┌───────────────▼─────────────────────┐
   index                │ 向量库：10 万 cluster · 4096→256 维  │  <100ms / >500 QPS
                        │ Matryoshka(20×) + 二值量化(16×)      │  比云厂商便宜 10×
                        │ BM25：倒排 + WAND 剪枝 + 增量压缩    │  1.8TB/十亿文档 → 砍半
                        └───────────────┬─────────────────────┘
                                        │
                        ┌───────────────▼─────────────────────┐
  orchestration         │ Canon：DAG，20+ 种 node，pull-based  │  memoize / 级联取消
                        │ 无依赖节点自动并行；节点级 trace     │  typestate 保证全分支覆盖
                        └───────────────┬─────────────────────┘
                       ┌────────────────┼────────────────┐
                  rerank              highlights       safety
                （自研 reranker）  （<100ms，不缓存）    filter
                       └────────────────┼────────────────┘
                        ┌───────────────▼─────────────────────┐
  products              │ Instant(<200ms) · Deep · Deep Max    │  Exa Agent：五档 effort
                        │ /answer · Websets · Research         │  $0.012 → $1.00
                        └─────────────────────────────────────┘
```

### 2.2 数字卡（背下来）

**存储/数据层 —— [exa-d](https://exa.ai/blog/exa-d)（2026-01）**

| 事实 | 数字 |
|---|---|
| 规模 | 数千亿网页，PB 级原始内容，每页派生**几十个** artifact |
| 存储格式 | **Lance on S3**，按 fragment + 部分 schema 组织 |
| 核心原语 | **只写/删单个 fragment 的单个 column，不重写整个 fragment** |
| 执行 | 列依赖图拓扑排序 → **Ray Data** pipeline；Ray Actor 常驻 embedding 模型避免重复加载 |
| 一致性模型 | 比较「理想状态（所有列都有）」vs「实际状态」，**只算缺失或失效的列** —— backfill 和增量更新走同一条码路 |
| 更新频率 | 新闻小时级 ↔ 论文几乎不变 |

**向量检索 —— [building-web-scale-vector-db](https://exa.ai/blog/building-web-scale-vector-db)（2024-12）**

| 技术 | 具体做法 | 收益 |
|---|---|---|
| 聚类（IVF） | 分成 **10 万个** cluster，只搜 query 所在簇及邻近簇 | 吞吐 **~1000×** |
| Matryoshka | 训练时强制前缀也是好 embedding，**4096 → 256 维** | 内存 **20×** |
| 二值量化 | 每维 16-bit → 1-bit（`>0 ? 1 : -1`） | 内存再 **16×** |
| 非对称打分 | **query 用 fp，doc 用二值**，算点积而不是 Hamming | 保精度 |
| SIMD + LUT | 向量切成长度 4 的子向量，查表存全部 **16 种**可能点积，表放 **CPU 寄存器** | 计算量 **1/4** |
| 过滤 | 可过滤字段建**倒排索引**（value → doc_id 集合） | 支持 keyword+metadata filter |
| 结果 | **十亿级向量 <100ms，>500 QPS，内存小于一台游戏 PC，成本比云向量库低 10×** | |

**BM25 —— [bm25-optimization](https://exa.ai/blog/bm25-optimization)（2025-05）**

| 技术 | 做法 |
|---|---|
| 索引 | 倒排表存 `(doc_id, tf)`，按 doc_id 排序，hashmap 以 token_id 为键 |
| 候选生成 | 先用 **IDF 最高（最稀有）** 的词项的 posting list 生候选，impact-ordered |
| 剪枝 | **WAND** 式 top-k 动态剪枝：数学上不可能进 top-k 的文档直接跳过 |
| 压缩六件套 | ① 按 tf 分组（tf 通常 1–15）② doc_id **delta + 变长编码**（4B → ~1.3B）③ 整条 posting list **zstd** ④ 嵌套结构摊平成单 buffer（100 个 doc_id 只 16B 开销）⑤ 单文档 token 存裸整数 ⑥ 全部 posting list 放一个连续 vector，每 token 只存 `(offset, len)` 8B 而非 Vec 的 24B |
| 结果 | **1.8TB / 十亿文档 → 砍半**；意外地 **平均延迟还降了 10%**（缓存局部性）；十亿文档取数千结果 **<500ms** |

**编排 —— [composing-a-search-engine](https://exa.ai/blog/composing-a-search-engine)（2026-04）**

| 概念 | 内容 |
|---|---|
| 是什么 | **Canon**，把搜索管线表达成 **DAG**，"a graph of **20+ node types** with many branches" |
| 执行模型 | **pull-based**：下游要了上游才跑。父节点超时或客户端断开 → **级联取消所有子节点**，不浪费算力 |
| 菱形依赖 | **memoize**：共享祖先每请求只跑一次 |
| 并行 | 无依赖节点**自动并行**。例子里 web / inverted / news 三个索引赛跑，web 赢了 → **T+80ms 取消其余分支** |
| 缓存 | rerank 拉一次结果并缓存 → **snippet 抽取和安全过滤两个消费者并行**跑在缓存上 |
| 可观测 | DAG 编译成可序列化的图；runtime 在每个调用边界自动记录 timing/输入/输出/决策 → 能回答"某个 query 某天为什么没返回某 URL，是哪个子系统丢的" |
| 类型安全 | **typestate**（状态编码进类型，非法操作变编译错）+ **totality**（每个节点必须处理它能产生的每种结果，缺分支类型检查直接拒） |
| 动机（值得引用） | "most code is now written by agents" → 正确性负担从 **agent 的 context window** 转移到 **schema 和 runtime** |
| 容错 | 节点失败可**从该节点重试**，不用重跑前面的 |

**Highlights —— [highlights-for-agents](https://exa.ai/blog/highlights-for-agents)（2026-04）+ [scaling-our-highlights-server](https://exa.ai/blog/scaling-our-highlights-server)（2024-02）**

| 事实 | 数字 |
|---|---|
| 是什么 | 从网页里抽 query-specific 摘录，"dense, query-specific excerpts let agents ground on the web while reading dramatically fewer tokens" |
| 延迟 | **<100ms**，**每个请求都跑，不缓存** |
| 效果 | **500 字符的 highlights ≈ 整页前 8000 字符的准确率，token 少 16×**；4k 字符 highlights **优于** 32k 字符全文 |
| 极端情形 | 长上下文代码文档 eval 上，500 字符时 **60% vs 6%** |
| 总体 | 某些 eval 上 **token 少 ~94%** |
| 覆盖面 | 公开 API + **Exa 自己的 agentic endpoint（/answer、Deep、Websets）都跑在它上面** —— "the retrieval substrate for agent loops" |
| 早期架构（2024） | 单个 **8×A100** 节点服务全生产；chunk（CPU）+ embed（GPU）+ 选最相关段 |
| Python→Rust | GIL 卡住多进程 IPC 是真瓶颈（不是 GPU 通信）；用 rayon `par_iter()` 换 `iter()`，**吞吐 4×** |
| 踩过的坑 | rayon 并行调 `tch-rs` 导致 **CUDA 调用非线程安全** → tensor 提前释放，80GB A100 也 OOM。解法：**推理和取结果拆成两趟串行**，靠 CUDA 异步执行拿并行 |
| 现在 | "explored a wide range of architectures and training recipes before landing on the current approach"（**架构没公开 —— 这是你可以在面试里主动设计的空白**） |

**Model alignment —— [rl-search-outcomes](https://exa.ai/blog/rl-search-outcomes)（2026-05）**

| 项 | 设置 |
|---|---|
| 模型 | **Qwen3-4B-Instruct-2507**，LoRA **rank 32** |
| 算法 | **Dr. GRPO**，100 步，batch 64，streamed minibatch + 异步训练，跑在 **Tinker** 上 |
| 预算 | 32k context，每 rollout 生成 2048 token |
| 工具 | Exa vs **SERP**（Google 代理）；都返回 5 条实时结果，各截断到 2000 字符 |
| reward | 初版精确子串匹配 → **被 reward hack**（啰嗦回答、列一堆候选答案）→ 换成 SimpleQA 的 **LLM grader**；超上下文 **−0.25** 惩罚 |
| 训练集 | MuSiQue + HotpotQA（multi-hop QA） |
| 评测 | 测试集 pass@k + OOD：2WikiMultihopQA / FRAMES / BrowseComp / SimpleQA |

**结果（这四行是全文最好用的引用）**：

| 发现 | 数字 |
|---|---|
| Exa 训的 4B 在**所有** benchmark 上 pass@1 高于 SERP 训的 | — |
| 到第 100 步的总 token | Exa **1.58B** vs SERP **1.89B**（少 **20%**） |
| 达到 SERP-trained 的水平所需 | 少 **69%** token、少 **62%** search call |
| 搜索结果里直接含答案的比例 | Exa **36.1%** vs SERP **32.6%**（+10.7% 相对） |
| SERP 的方差来源 | **6.74%** 的训练 query 返回不足 5 条，**0.19%** 返回 0 条 |

**机制解释（他们自己给的，也是最值得复述的一句）**：
检索质量高 → **每步 reward 更稠密** → 稀疏性降低 → 样本效率提升。
而且 **skill transfer**：用 Exa 训的 agent，推理时换回别的引擎也更强。

**评测 —— [WebCode](https://exa.ai/blog/webcode)（2026-03）+ [evals-at-exa](https://exa.ai/blog/evals-at-exa)（2025-05）**

| 项 | 内容 |
|---|---|
| WebCode 四类 | ① contents quality（**250 个 URL**）② highlights / 页内搜索 ③ retrieval quality / RAG（**317 组 query-answer**，来自 GNU/W3C/IETF RFC/各语言官方文档）④ 端到端 coding task（**33 个任务、9 种语言**，专挑 **2025-08-01 之后**发布的库 —— 抗污染） |
| 核心方法论 | **discriminative 而非 generative**："不问『从这段上下文生成正确答案』，而问『这段上下文里**有没有**正确答案』" |
| 为什么 | **groundedness 的方差远大于 correctness（~86%）**，更能把搜索供应商的差异分离出来 |
| 数字 | contents completeness Exa **82.8%** vs Parallel 74.2%；code recall **96.7%** vs 94.1% |
| open evals | query set 打**任意** index，不要求固定语料 + 预标注（详见 [13 · 公司卡](13_company_cards.md)） |

**训练基建**：[Exacluster](https://exa.ai/blog/meet-the-exacluster) 18 节点 GPU 集群；Exa 2.0 在 **144×H200 上训了一个多月**；
7–8 人时就买了自己的集群，**始终打满，甚至是瓶颈**；zero-data-retention 承诺靠"模型+索引+基建全自有"支撑。

---

## 3. 主推题 ⭐⭐⭐：设计 Exa Highlights（snippet generation）

> **题面可能长这样**："我们给 agent 返回网页内容。整页太长了，agent 的 context 烧不起。
> 设计一个系统，给定 (query, 一批网页)，返回最相关的片段。要求 p99 < 100ms。"

这是 Joshua 本人的领域，也是**外部候选人准备最少**的一块。下面是完整答案。

### 3.1 先问清楚（2 分钟，不要跳过）

| 问题 | 为什么问 | 我会假设的默认值 |
|---|---|---|
| 消费者是 **agent 还是人**？ | 决定优化目标：人要可读连贯，agent 只要「答案在里面」 | **agent**。这直接把目标改成 groundedness 而非 readability |
| 一次请求 **几个文档、多长**？ | 决定算力预算 | 10 篇 × 平均 8k token |
| 文档来自**已索引**的还是**实时抓取**的 URL？ | 决定能不能预计算 | 两者都有，混合设计 |
| 输出是**固定预算**（500 字符）还是自适应？ | 决定是不是背包问题 | 客户端给字符预算 |
| 允许**改写/生成**还是必须**原文抽取**？ | 生成有幻觉风险且慢 | **抽取式**（保证可引用、可 grounding） |

**开场就把优化目标写出来**（这一句比后面任何架构都重要）：

> 优化的不是「摘要好不好」，是 **在 B 个 token 的预算下，下游 agent 能不能答对**。
> 所以指标是 **answer-in-context recall @ budget**，即 groundedness——你们 WebCode 里正是这么做的：
> 问「这段上下文里有没有答案」而不是「生成的答案对不对」，因为后者被生成模型的能力污染了。

### 3.2 架构 v1 → v3（阶梯式，别一上来就上最复杂的）

```
                     ┌──────────────┐
 (query, docs) ─────▶│ 1. 切块       │  语义感知切分，不是固定窗口
                     │   chunking   │  重叠 20%，保留 heading 路径
                     └──────┬───────┘
                            │ ~40 chunks/doc × 10 doc = 400 chunks
                     ┌──────▼───────┐
                     │ 2. 打分       │  ← 这一层是全部的设计空间
                     └──────┬───────┘
                            │
                     ┌──────▼───────┐
                     │ 3. 选择       │  预算约束下的子集选择（不是简单 top-k）
                     └──────┬───────┘
                            │
                     ┌──────▼───────┐
                     │ 4. 拼装       │  相邻块合并、去重、按文档内顺序、加锚点
                     └──────────────┘
```

**第 2 层的三级阶梯**（面试里把三级都说出来，并说明**什么证据会让你升级**）：

| 级别 | 做法 | 算力 | 什么时候升级 |
|---|---|---|---|
| **v1 · bi-encoder** | chunk embedding 与 query embedding 点积。**已索引文档的 chunk embedding 在索引期就算好**（query 无关），线上只做 1 次 query encode + 400 次点积 | 已索引：**~1ms**；实时抓取：见下算术 | 基线。先量它离天花板多远 |
| **v2 · 小 cross-encoder** | (query, chunk) 联合编码。捕捉 bi-encoder 抓不到的词序/否定/精确匹配 | 见下算术 | 当 v1 的 recall@budget 与 oracle（穷举最优子集）差距 >5 个点 |
| **v3 · 抽取式 span model** | 直接预测 span 边界而不是打分固定 chunk。**切块本身就是有损的** —— 答案跨块或只占块的 10% 时，chunk 级打分会把噪声一起塞进预算 | 约等于 v2 | 当误差分析显示主要损失来自**切块边界**而非排序 |
| ~~v4 · 生成式~~ | LLM 生成摘录 | **超预算，且会幻觉** | ❌ 100ms 内不可能，且破坏可引用性 |

### 3.3 算术：证明 100ms 预算能不能装下 ⭐

**这段是本题的分水岭**。绝大多数候选人会画完架构就停，你要把数算给他看。

前向 FLOPs ≈ `2 × 参数量 × token 数`。

**bi-encoder 打分（实时抓取的文档，无法预计算）**
```
10 篇 × 8k token = 80k token
100M 参数 encoder：2 × 1e8 × 8e4 = 1.6e13 = 16 TFLOP
H100 bf16 有效算力按 300 TFLOP/s（约 30% MFU，序列短、batch 不满）
→ 16 / 300 ≈ 53ms
```
**结论：正好卡在 100ms 预算内 —— 而且这解释了他们为什么用 8×A100 服务，以及为什么"不缓存"是可行的。**
（这也和他们 2024 年那篇 chunk+embed 的架构描述对上了。）

**cross-encoder 全量重排 400 个 chunk**
```
400 chunk × 256 token = 102k token（query 拼进去，量级不变）
100M 参数：2 × 1e8 × 1.02e5 ≈ 2.0e13 = 20 TFLOP → ~68ms
```
**结论：v2 全量跑不进预算**（还要留出网络、切块、拼装的时间）。
→ **必须做级联**：bi-encoder 筛 400 → 40，cross-encoder 只跑 40 个。
```
40 chunk × 256 token = 10k token → 2 TFLOP → ~7ms  ✅
```

**完整 p50 预算表**（我会在白板上写这张）：

| 阶段 | 预算 | 备注 |
|---|---|---|
| 切块（CPU） | 8ms | 这就是他们 Python→Rust 那篇解决的东西；GIL 卡住 IPC，rayon 后吞吐 4× |
| query encode | 3ms | 一次，可与 chunk 前处理并行 |
| bi-encoder 打分 | 53ms | 实时抓取路径；已索引路径 **~1ms**（embedding 预计算） |
| cross-encoder 精排 top-40 | 7ms | |
| 预算内选择 + 拼装 | 2ms | |
| 序列化 / 网络 | 10ms | |
| **合计 p50** | **~83ms** | 留 17ms 给 p99 尾巴 —— 不够，见下 |

**p99 怎么办**（主动说，别等他问）：
- p99 的杀手不是均值，是**长文档**。一篇 200k token 的 API 参考页就能把预算打爆。
- 对策：① 按 token 数**分级路由**，超长文档先用廉价信号（heading 匹配、BM25）粗筛掉 90% 的块，再进 encoder；
  ② **超时降级**：cross-encoder 阶段带 deadline，超了就用 bi-encoder 的序 —— 这正是 Canon 的 pull-based + 级联取消能干净表达的东西；
  ③ 把「返回稍差的 highlight」和「返回整页」都当作合法降级，**但要打点区分**，否则 SLO 达标但质量在偷偷退化。

### 3.4 训练数据从哪来（他一定会追这个）

抽取式 snippet 没有天然标签。四类来源，按成本排序：

| 来源 | 怎么造 | 坑 |
|---|---|---|
| **弱监督 · 答案定位** | 有 (query, 答案) 的数据集（SimpleQA / NQ / 你们的 317 组 WebCode QA），在页面里定位答案字符串所在的 span → 正例 | 答案可能以不同措辞出现；**只做精确匹配会漏掉大半**，要用语义匹配兜底 |
| **蒸馏 · 强模型打标** | 用大模型对 (query, chunk) 打 0–1 相关分，蒸给小模型 | 教师有位置偏差（偏爱开头的块）；要**打乱块顺序**取平均 |
| **下游反事实** | 把 chunk 塞给下游 agent，看**答对率**。这是最贴目标的信号 | 贵；而且被 agent 能力污染 —— 所以你们改用 discriminative（有没有答案）而不是 generative（答得对不对） |
| **锚文本 / 引用** | 别的页面引用这一页时用的那句话，天然是"这一页里最值得引的一段" | 分布偏向热门页 |

**我会主推第 1 + 第 3 的组合**：
用答案定位造大批弱标签训 bi-encoder，用下游反事实造少量高质量标签**只用来评测和校准**，不用来训（量太小、方差太大）。

**负例是关键**（接 [06 §六](06_search_post_training.md)）：
- **同文档内的其他 chunk 是最好的 hard negative** —— 主题相同、只差相关性，正好逼模型学 query-specific 而非 topic-level 相关。
- ⚠️ **陷阱**：同一页里常有多个块都含答案。把它们全当负例会直接教坏模型。
  这和 Exa 拒绝 MS MARCO 的第一条理由（稀疏标注造成**假负例**）是同一个问题。
  解法：多正例 / soft label，或者只把「与正例语义相似度低于阈值」的块当负例。
- 我**实际测过这个的对照实验**，见 §11.2 —— 这是我在这题上最强的个人素材。

### 3.5 Eval：三层，且第一层最容易做错

| 层 | 指标 | 怎么算 |
|---|---|---|
| **① 内在** | **answer-in-context recall @ budget** | 固定 500 / 1k / 4k 字符预算，答案（语义匹配）是否落在返回的片段里。**画成 recall-vs-budget 曲线，不要只报一个点** —— 你们那两个数字（500 字符 ≈ 8000 字符、4k > 32k）本质就是这条曲线上的两点 |
| ② 对照 | 与 **oracle 子集**的差距 | 穷举/贪心选出预算内最优子集作为上界。**报「离上界还差多少」比报绝对值有信息量得多** |
| ③ 下游 | agent 端到端答对率、总 token、search call 次数 | 这是钱；但方差大，需要足够样本量 |

**baseline 阶梯**（必须报，否则数字没有意义）：
`整页前 N 字符` → `随机 N 字符` → `BM25 选块` → `零训练 bi-encoder 选块` → 你的模型。
你们博客里那个 **60% vs 6%** 大概率就是「模型 vs 整页前 N 字符」，这个 baseline 在长文档上极弱，
所以**我会同时报 BM25 baseline**，那才是诚实的对照。

> 💬 **可以直接说的一句**：
> "我注意到你们 highlights 那篇报的是 vs 全文截断。我会额外加一条 BM25 选块的 baseline ——
> 在长 API 文档上截断这个 baseline 弱得不正常，报它会高估收益。"
> （这展示你会读别人的数字，而不是复述。风险可控：这是方法论建议，不是指责。）

---

## 4. 第二题 ⭐⭐⭐：给 agentic search 设计 reranking 这一层

> **题面可能长这样**："搜索返回 1000 个候选，我们要返回 top 10。设计 reranker。
> 延迟预算 100ms，QPS 500。"

### 4.1 第一句话：先问「重排是为谁排的」

**这是 agentic search 和传统搜索最大的区别，一开口就要点出来**：

| | 人用的搜索 | **agent 用的搜索** |
|---|---|---|
| 消费 top-几 | 前 3 条，位置偏差极强 | **全部 5–10 条一起进 context** |
| 排序重要吗 | 极重要（第 1 位 vs 第 3 位差很多） | **相对不重要，集合的覆盖度更重要** |
| 优化目标 | nDCG（位置折扣） | **答案落在集合里的概率**；应该优化 **set-level recall + 多样性**，不是 pointwise 相关性 |
| 失败代价 | 用户多点一下 | **agent 多搜一轮** → 延迟 ×N、成本 ×N（你们 RL 那篇量化过：好检索 = 少 62% search call） |
| 冗余 | 无所谓 | **有害**：5 条说同一件事 = 浪费 4 条的 context |

> 💬 **这段是本题的差异化开场**：
> "传统 reranker 优化 nDCG，因为人只看前三条。但 agent 把 5 条全读进 context——
> 位置折扣基本不适用，而**冗余是实打实的成本**。所以我会把目标从 pointwise 相关性
> 改成 **budget 约束下的 set-level 覆盖**，训练时用 listwise loss，评测时报 recall@k 和 α-nDCG（惩罚冗余），
> 而不只是 nDCG@10。"

### 4.2 级联：算力必须这样花

```
十亿文档
   │  dense ANN（256维二值，10万簇）─┐
   │                                 ├─ RRF 融合 ─▶ ~1000 候选
   │  BM25 + WAND ───────────────────┘             （Canon：两路并行，无依赖自动并行）
   ▼
 ~1000
   │  L1：轻量重排（late interaction / 全维 embedding 重打分）
   ▼
  ~100
   │  L2：cross-encoder（真正的重排）
   ▼
   10
   │  L3（可选）：LLM listwise 重排 —— 只在 Deep / 高 effort 档开
   ▼
 返回
```

**为什么 L1 存在**：dense 那一路用的是**截断+量化**的向量（256 维二值）。
L1 可以用**全维 fp 向量**重算 top-1000 的分数 —— 这是几乎免费的精度回收。
**Matryoshka 天生就是给级联设计的**：粗筛用 256 维，精排用 4096 维，同一个模型，无需第二套索引。

> 💬 这句值得说：**"Matryoshka 在你们那里不只是省内存的技巧，它本身就是一个天然的两级级联。"**

### 4.3 算术：cross-encoder 能重排多少个

```
N 个候选 × 512 token（query + 文档片段）
100M 参数 cross-encoder：FLOPs = 2 × 1e8 × 512N = 1.02e11 × N

预算 30ms，H100 有效 300 TFLOP/s → 9e12 FLOP
N = 9e12 / 1.02e11 ≈ 88
```
**→ 一张 H100 在 30ms 内能重排约 90 个文档（100M 参数、512 token）。**

由此推出的三个结论（都要说）：
1. **候选数 100 不是拍脑袋，是算力反推出来的。** 想重排 1000 个，要么模型缩到 10M，要么砍到 64 token（只用标题+首段），要么加 10 倍卡。
2. **QPS 500 意味着 500 × 30ms = 15 GPU-秒/秒 → 至少 15 张卡满打满算，实际留余量要 25–30 张。** 这是可以直接报给他的容量估算。
3. **模型不能大。** 一个 1B 的 cross-encoder 是 10×，直接出局。所以 web-scale reranker 的真实设计约束是「**在 100M 参数内把质量榨干**」，而不是「用最强的模型」。
   → 这正是**蒸馏**的用武之地：用大模型（甚至 LLM listwise）离线打标，蒸给 100M 的学生。

**降低单位成本的三条路**（按性价比）：

| 手段 | 收益 | 代价 |
|---|---|---|
| **Late interaction（ColBERT 式）** | 文档 token 向量**离线算好**，线上只做 query 编码 + MaxSim | 存储爆炸（每 token 一个向量）→ 必须量化，正好接他们的二值量化经验 |
| **文档侧截断** | 512 → 256 token，算力减半 | 长文档信息丢失 → 但可以先用 §3 的 highlights 挑出最相关的 256 token 再喂 reranker。**highlights 和 reranker 是互相喂的** ⭐ |
| **蒸馏到更小** | 100M → 30M，3× | 质量掉多少要实测；用 [06 §7.2] 的 listwise 蒸馏（RankNet / margin-MSE） |

> ⭐ **highlights ↔ reranker 的耦合是本题最好的洞察**，而且正好横跨他自述的两个关键词：
> reranker 需要"文档里最相关的 512 token"才能判准，而这恰好就是 highlights 干的事；
> 反过来 highlights 只需要对 reranker 留下的候选跑。**两者共享 chunk embedding 缓存，可以合成一个 node。**
> Canon 里正是这个形状：rerank 拉一次结果缓存，snippet 抽取和安全过滤两个消费者并行跑在缓存上。

### 4.4 训练数据与负例（引 06，但补 agentic 特有的部分）

标准部分见 [06 §四/五/六](06_search_post_training.md)。**agentic search 特有的三条**：

1. **没有 click。** agent 不点击。可用的隐式信号是：agent **是否基于这条结果给出了引用**、**是否在这条之后停止搜索**、**最终答案是否正确**。
   → 归因很难（5 条结果共同促成一个答案）。可用 **leave-one-out 反事实**：抽掉这条，答案还对吗？贵但干净。
2. **RL rollout 是免费的标注机。** 你们训 search agent 时会产生海量 (query, results, 最终对错) 三元组。
   这些可以反哺 reranker 的训练 —— **agent 的成功率就是 reranker 的 downstream label**。
   这是一个正反馈：好检索 → RL 更省样本 → 更多 rollout → 更好的 reranker 标签。
3. **query 分布是 agent 生成的，不是人写的。** agent 的 query 更长、更结构化、常带约束（"after 2025-08"、"official docs only"）。
   → 用人类 query 训的 reranker 在这个分布上会掉点。**必须用真实 agent query 训和评**（你们有 5000 条真实去标识 query）。

### 4.5 上线与回归

- **shadow 先跑**：新 reranker 与旧的并行，只记录不返回，比较 top-10 集合的 Jaccard 与各自的 groundedness。
- **切片必看**：query 长度、语言、domain 类别、**新鲜度**（近 7 天的页面）、**长文档**。均值达标而长文档退化是最常见的事故。
- **护栏**：p99 延迟、每查询 GPU-秒、**安全过滤后的结果数为 0 的比例**（这条最容易被忽略且最伤 agent —— 你们自己量过 SERP 有 6.74% 返回不足 5 条，方差就是这么来的）。

---

## 5. 第三题 ⭐⭐：Model alignment —— 训一个 search agent

> **题面可能长这样**："我们想训一个模型，更会用我们的搜索。怎么做？"
> 或反过来："搜索质量怎么影响 RL？"

**这题你有主场优势** —— 你在 Decagon 项目里手写过 Dr. GRPO（含 length/std normalization 的修正）和 DAPO 的 clip-higher，
而**他们博客里用的就是 Dr. GRPO**。见 §11.1。

### 5.1 阶段划分（照他们的方法论说）

```
① SFT：轨迹格式 + 工具协议     ← 建立行为地板，不求最优
② RL（Dr. GRPO）：outcome reward ← 锐化决策边界（何时搜、搜什么、何时停）
③ （可选）on-policy distillation ← 抗遗忘 / 把多个 teacher 蒸成一个 student
```

### 5.2 reward 设计（这是最能出彩的地方）

| 层 | reward | 说明 |
|---|---|---|
| **outcome** | LLM grader 判最终答案对错 | ⚠️ 他们踩过的坑：**精确子串匹配会被 hack** —— 模型学会啰嗦地列一堆候选答案，总有一个命中。改用 grader |
| **cost** | 超上下文 **−0.25**；每次 search call 一个小负项 | 不加成本项，agent 会无限搜。你们量化过：好检索让 search call 少 62%，**这个收益必须进 reward 才能被学到** |
| **process**（我会加，他们没提） | 引用是否真的支撑了 claim | 只给 outcome reward，模型可以**猜对**或**靠记忆答对**而完全没用检索。这是 [06 §E4](09_question_bank.md) 的老问题 |

**verifiable reward 的边界**（主动说这条，显示你不是无脑上 RL）：
> RL 只在 **verifier 可靠**时才该开。multi-hop QA 有唯一答案，verifier 干净，所以你们能训。
> 换成开放式研究任务（Websets 那种「找出所有满足 N 个条件的公司」），verifier 本身就是个难题，
> 这时我会先做 **rejection sampling + SFT**，而不是直接上 RL —— 因为 reward 噪声会被 RL 放大。

### 5.3 「搜索质量 → RL 样本效率」的因果链（背下来）

```
检索质量↑
  → rollout 里「结果中直接含答案」的比例↑（你们：36.1% vs 32.6%）
  → 成功轨迹的密度↑
  → 有效梯度信号↑（GRPO 组内全错时优势全为 0，这一组白跑）  ← 这是机制的关键
  → 到同等性能所需 token↓（你们：−69%）、search call↓（−62%）
```

**⭐ 最值得说的一句（GRPO 特有，博客没写但是对的）**：
> GRPO 是**组内**归一化优势。如果一组 rollout **全部失败**，组内优势全是 0，这一组的算力完全浪费。
> 所以检索质量提升的收益在 GRPO 下是**超线性**的 —— 它不只是把平均 reward 抬高，
> 它是把「全组失败」的组从**零信号**变成**有信号**。这就是为什么少 20% token 就能到第 100 步。

（这段能讲出来，基本就证明你既读了他们的博客又真懂 GRPO。）

### 5.4 skill transfer 与评测污染

- 他们发现用 Exa 训的 agent 换到别的引擎也更强 → 说明学到的是**通用搜索技能**（怎么拆 query、何时停），不是"记住 Exa 的排序"。
  **验证方法**：交叉评测矩阵 —— {Exa训, SERP训} × {Exa测, SERP测}，四格都报。只报对角线会把 overfit 藏起来。
- **污染**：HotpotQA / 2Wiki 早就在预训练里了。所以他们用 **BrowseComp / FRAMES** 做 OOD，
  WebCode 更狠 —— **只用 2025-08-01 之后发布的库**。这是抗污染的正解，值得复述。

---

## 6. 第四题 ⭐⭐：端到端设计一个 agentic search endpoint

> **题面可能长这样**："设计 `/answer`：给一个问题，返回带引用的答案。要求 p50 < 2s。"

**主线**：这题的核心不是"接哪些组件"，是**在延迟预算下决定每一步花多少算力**，以及**并行与提前终止**。

### 6.1 用 Canon 的语言画图（他会认出来）

```
                      query
                        │
        ┌───────────────┼───────────────┐        无依赖 → runtime 自动并行
   query 改写      意图/分类        新鲜度判定
        │               │               │
        └───────┬───────┴───────────────┘
                │  fan-out：一个问题拆成 k 个子查询
    ┌───────────┼───────────┬───────────┐
  dense       sparse      news 索引    code 索引   ← 赛跑；先到的赢，
    └───────────┴─────┬─────┴───────────┘            其余级联取消（他们例子里 T+80ms）
                      │ RRF 融合
                   rerank ──── 结果缓存一次
                      │
              ┌───────┴───────┐            memoize：菱形依赖只算一次
          highlights      safety filter     两个消费者并行
              └───────┬───────┘
                  answer 合成（带引用）
```

### 6.2 延迟预算（p50 = 2s 怎么分）

| 阶段 | 预算 | 备注 |
|---|---|---|
| query 理解 / 改写 | 150ms | 小模型；**能不能省掉？先量它值不值这 150ms** |
| 检索（多路并行） | 200ms | 取最慢的一路，不是加起来。Instant 全链路 <200ms 说明这层能做到 |
| rerank | 60ms | §4.3 算过 |
| 内容取回 | 150ms | 已缓存的页面；未缓存要实时抓 → **这是尾延迟的主要来源** |
| highlights | 100ms | §3.3 算过 |
| 答案合成（LLM） | 800ms | 首 token + 生成 300 token |
| 网络 / 序列化 | 100ms | |
| **合计** | **~1.56s** | 留 440ms 余量 |

**三个必须主动说的工程点**：
1. **流式**：答案边生成边返回，用户/agent 感知延迟远小于 2s。但**引用必须在文本之后校验** —— 流式和 grounding 校验是冲突的，我会先流出答案，再流出校验过的引用块。
2. **提前终止**：如果 rerank 后 top-1 的分数极高且来源权威，跳过 highlights 直接用首段。**用置信度做路由**，这是 [08](08_evaluation_production.md) 的 cascade。
3. **effort 档位**：他们 Exa Agent 就是五档 **$0.012 → $1.00**。设计上应该是**同一个 DAG，不同的 node 开关和 fan-out 宽度**，而不是五套系统。

### 6.3 失败模式与降级

| 失败 | 表现 | 降级 |
|---|---|---|
| 某路索引超时 | 结果变少 | 用已到的路，**打点记录降级** —— 否则 SLO 绿灯而质量在退化 |
| 实时抓取失败 | 无内容 | 回落到索引里的缓存版本 + 标注 staleness |
| 安全过滤清空结果 | 返回 0 条 | **这是最坏的失败**（agent 会重搜，成本翻倍）。要单独告警 |
| 答案无法 grounding | 幻觉风险 | 宁可返回"没找到"+ 原始片段。对 agent 来说，**明确的空结果比错答案便宜** |

---

## 7. 横切：延迟预算的算术（把第一轮那题接上）⭐

第一轮考流式分位数不是巧合 —— **搜索系统的一切都由尾延迟定义**。这一节让两轮连成一条线。

### 7.1 为什么 p99 而不是 p50

**agent 会连着搜 5–30 次**。单次 p99 = 500ms 的系统，30 次串行调用里出现至少一次慢请求的概率：
```
1 − 0.99^30 ≈ 26%
```
→ **四分之一的 agent 任务会撞上尾延迟。** 所以 agentic search 的 SLO 必须盯 p99，甚至 p999。
这也解释了 Canon 为什么把「级联取消」做进 runtime：多路赛跑的目的就是**用冗余换尾延迟**。

> 💬 这句可以主动抛：**"多路索引赛跑本质是 hedged request —— 用算力换 p99。
> 代价是算力乘以路数，所以只对尾部请求 hedge（比如 p50 之后才发第二路）性价比更高。"**

### 7.2 分位数怎么在生产里量（接你第一轮的答案）

| 方案 | 空间 | 误差 | 可合并 | 适用 |
|---|---|---|---|---|
| 全排序 | O(n) | 精确 | ❌ | 离线 |
| 固定宽度桶 | O(range/w) | 绝对误差 w | ✅ | 值域已知且窄 |
| **DDSketch（log 桶）** | O(log(max/min)/ln γ) | **相对误差 γ** | ✅ | **延迟监控的正解** —— 延迟跨几个数量级，你要的是"p99 误差 1%"而不是"误差 1ms" |
| t-digest | O(压缩率) | 尾部更准，中位数较松 | ✅ | 也常用；尾部精度优先时 |

**桶索引就是你答的那个**：`i = ceil( log(x) / log(γ) )`，其中 `γ = (1+α)/(1−α)`，α 是目标相对误差。
**可合并性（mergeable）是分布式系统里的硬需求** —— 每台机器一个 sketch，中心节点合并，
这是 histogram 能跨机聚合而百分位数不能直接平均的原因。

> 💬 如果他问起第一轮："我当时推到了 log 分桶。补一句我当时没说的：
> **选 log 桶的真正理由是延迟分布跨数量级，相对误差才是有意义的保证**；
> 另外 sketch 必须可合并，否则多机环境下根本没法聚合。"

---

## 8. 横切：每一层用什么指标（一页表）

| 层 | 训练目标 | 离线指标 | 上线护栏 |
|---|---|---|---|
| 索引 / crawl | — | 覆盖率、staleness 分布 | 索引滞后 SLO、抓取失败率 |
| Retriever | 对比学习（InfoNCE） | **recall@k**（k 要大：100/1000） | 召回为 0 的 query 比例 |
| Reranker | listwise / margin | nDCG@10 + **α-nDCG**（惩罚冗余）+ set recall@10 | p99 延迟、GPU-秒/查询 |
| **Highlights** | 抽取式打分 | **answer-in-context recall @ budget 曲线** + 离 oracle 子集的差距 | 输出 token 数分布、超时降级率 |
| Answer / Agent | SFT → Dr. GRPO | pass@1、**citation precision/recall** | 幻觉率、search call 数、成本/查询 |
| 端到端 | — | WebCode 四类、SimpleQA、FRAMES、BrowseComp | CSAT 类信号、客户侧成功率 |

**贯穿全表的一条原则**（这是 Exa 的核心方法论，也是你 Decagon 项目验证过的）：
> **评测器必须比被评测的东西强，或者至少不能和它同源。**
> 用 BM25 造的标签去评一个改进 BM25 的系统，收益会被系统性抹掉。
> 你们拒绝 MS MARCO 的四个理由里，第一条（稀疏标注造假负例）就是这个问题的一种形态。
> 我自己有一次量化的失败案例，见 §11.2。

---

## 9. 45 分钟怎么走 ⭐

| 时间 | 做什么 | 注意 |
|---|---|---|
| 0–3 | 自我介绍（[12 §2](12_personal_bridge.md) 的 90 秒版，**换成 retrieval 口径**，见 §11） | 别背简历，只讲能接上今天题目的三条 |
| 3–6 | **澄清问题**（§3.1 那五个的对应版本） | 至少问 3 个。不问就开画 = 减分 |
| 6–9 | **写下优化目标和指标**，明确说"我先定成功的定义" | 这是 Exa 最看重的信号（他们整家公司都在讲 eval） |
| 9–16 | 画架构（v1 → v3 阶梯 + 升级触发条件） | **不要一上来就画最复杂的** |
| 16–24 | **算术**：延迟预算 / 算力 / 容量 | ⭐ 这是与其他候选人拉开差距的地方。白板上写 `2 × params × tokens` |
| 24–32 | 训练数据、负例、失败模式 | 主动说坑，不等他挖 |
| 32–38 | eval 与上线：baseline 阶梯、切片、护栏、降级打点 | |
| 38–43 | 收口：v1 交付什么、什么证据触发 v2 | "我会先上 bi-encoder + 预计算，量出离 oracle 的差距再决定要不要 cross-encoder" |
| 43–45 | 提问（见 §12） | |

### 90 秒开场（retrieval 口径改写版）

> 我最近的工作横跨 agentic LLM 的 post-training 和 retrieval。上一段在 Reflection 做 agent 系统；
> 最近自己搭了一套分级的 retrieval + post-training 实验台，从 eval baseline 一路做到 DPO / Dr. GRPO / on-policy distillation。
> 那套东西里我最大的收获其实是两个负结果：一个是**微调生成式 query rewriter 完全跨不了域，
> 但换检索器 + 微调 embedding 直接把 recall@5 从 0.165 拉到 0.576，一行训练代码都没写**；
> 另一个是我一开始报的 hard negative 收益，加了样本数对齐的对照组之后发现三分之二是假的，我把它划掉了。
> 所以我的习惯是：**先把 eval 和 baseline 立住，再动模型；每个收益都要有对照组**。
> 今天这题我会按这个顺序来。

---

## 10. 追问弹药：20 个可能的追问 + 一句话答

| 追问 | 一句话答 |
|---|---|
| 为什么不直接用 LLM 生成 snippet？ | 100ms 装不下，且生成式破坏可引用性；抽取式保证每个字符都能定位回原文 |
| chunk 大小怎么定？ | 不拍脑袋——扫 128/256/512，画 recall@budget 曲线；块越小定位越准但上下文越碎，**最优值取决于文档类型，API 文档和新闻不该同一个值** |
| 怎么处理答案跨块？ | 重叠切分（20%）+ 相邻块合并；如果误差分析显示这是主要损失来源，升级到 span-level 模型 |
| bi-encoder 和 cross-encoder 差多少？ | 我不背这个数，我会量。经验上 rerank 层 cross-encoder 通常 +3~8 nDCG，但**在 agent 场景该看 set recall 而不是 nDCG** |
| 为什么 Matryoshka 而不是训两个模型？ | 一套权重、一次训练、一个索引就得到多档精度；两个模型还要保证 embedding 空间对齐 |
| 二值量化掉多少精度？ | 靠**非对称打分**（query 保 fp）补回大部分；而且它后面还有全维重排的 L1，粗筛只要求 recall 不要求 precision |
| 100k 个 cluster 怎么定的？ | 经验值 ≈ √N 量级；真正要调的是 **nprobe**（搜几个簇），它是 recall/延迟的直接旋钮 |
| 索引更新怎么不影响在线？ | 双缓冲 + 原子切换；exa-d 的列式设计正好支持只重算受影响的列 |
| 新鲜度怎么进排序？ | 作为特征而不是硬过滤；**query 的时间敏感度要先分类**（"今天的新闻" vs "快排怎么写"） |
| RRF 的 k 怎么选？ | 默认 60；但两路质量差距大时应该加权，或者直接训一个融合层 |
| 冷启动一个新垂类（比如 code search）？ | 见 [06 §四](06_search_post_training.md)：锚文本 / 链接上下文 / title-body / doc2query 合成 query；先零训练量 baseline，再决定投多少标注 |
| 怎么防 reranker 学到位置偏差？ | 训练时打乱候选顺序；评测时报**顺序扰动下的方差** |
| RL 训练 reward hacking 怎么防？ | 他们踩过的那个（精确匹配 → 列候选答案）就是范例；对策是 grader + 成本惩罚 + **人工看一批高 reward 的轨迹** |
| 为什么用 Dr. GRPO 而不是 GRPO？ | 去掉 length normalization（修长度偏置）和 std normalization（修难度偏置）。我自己实现过这两条修正 |
| 只有 outcome reward 够吗？ | 不够，模型可能猜对或靠参数记忆答对。要加 claim-level 的引用校验 |
| 怎么知道 agent 真用了检索？ | 反事实：抽掉检索结果重跑，答对率掉多少。掉得少说明它在靠记忆 |
| offline 提升多少才上线？ | 没有固定百分点。**预注册最小效应量 + 置信区间 + 护栏 + 切片**，然后 shadow/canary 验证能不能 transfer |
| 需要多少 GPU？ | §4.3 那套算法：峰值 QPS × 单请求 GPU-秒 / 利用率 + 余量。不要拿峰值 FLOPS 直接除 |
| 你会先做哪个？ | **先做 eval 和 baseline 阶梯**。没有可信的尺子，后面所有优化都不可验证 |
| 这个设计最可能在哪失败？ | 长文档尾延迟、假负例污染训练、以及**评测器与被评物同源导致收益被抹掉** |

---

## 11. 你的对位素材（这轮的个人弹药）⭐⭐

你刚做完的 [Decagon fine-tuning 项目](../projects/decagon_finetune/README.md) 里，有三块**正好打在 Exa 的靶心上**。
面试里不要主动长篇讲，但被问到时能立刻拿出**带数字的真实实验**。

### 11.1 你实现过 Dr. GRPO —— 而他们博客里用的就是 Dr. GRPO

- 你在 L4 里手写了 GRPO，并**显式加了两个修正**：Dr. GRPO 去掉 length normalization（修长度偏置）与 std normalization（修难度偏置），以及 DAPO 的 clip-higher。
- **接话方式**："我看到你们那篇 RL 用的是 Dr. GRPO。我自己实现过它相对 vanilla GRPO 的两处修正——
  去 length norm 和去 std norm，分别对应长度偏置和难度偏置。"
- 延伸到 §5.3 那个「全组失败 → 组内优势全 0 → 白跑一组」的机制论证，这是你能超出博客的地方。
- 诚实边界：**你的 GRPO 只跑到"证明环境与梯度正确"，没跑到收敛**。这点要主动说，不要含糊。

### 11.2 你做过 hard negative 的**带对照组**消融，并推翻了自己的结论 ⭐⭐⭐

这是你在这轮最强的一张牌，因为它同时命中 Exa 的两个痛点（hard negative、eval 可信度）。

| 配置 | 样本数 | recall@5（跨主题 5 折 CV） |
|---|---|---|
| MNRL in-batch | 306 | 0.600 ± 0.086 |
| `dup`（样本翻倍、**随机**负例）← 对照组 | 612 | 0.672 ± 0.091 |
| `hard`（同主题近邻做负例） | 612 | 0.711 ± 0.103 |

```
in-batch 0.600 ──+0.072──▶ dup 0.672 ──+0.038──▶ hard 0.711
                 样本翻倍              难负例
                （占 65%）          （占 35%，2胜1平2负，符号检验 p=1.0）
```

**怎么讲**（60 秒版）：
> 我一开始报的是 hard negative 带来 +0.109。后来加了一个**样本数对齐的对照组**——
> 把 in-batch 的样本原样复制一份，负例仍然是随机的。结果三分之二的收益来自**样本翻倍**，
> 真正属于难负例的只有 +0.038，而且 5 折里只赢 2 折，几乎全部来自其中一折的 +0.212。
> **我把这条从收益里划掉了。**

**为什么这对 Exa 有价值**：hard negative mining 是他们必然在做的事，
而"没有 count-matched control 就把收益归给难负例"是这个领域最常见的错误。
再加一句：**同主题近邻里混着未标注的相关文档，当负例会伤召回 —— 这和你们拒绝 MS MARCO 的第一条理由是同一个问题的两面。**

### 11.3 你有一次「评测器与被评物同源」的量化翻车

- 你用 BM25 打分造 DPO 偏好对，得出"偏好方向是噪声"的结论；
- 后来发现**用来验证的独立指标本身选错了**：词汇重叠给 46.2%（≈随机），换成语义相似度是 **62.5%（p=0.014）** —— 信号一直在；
- 更深一层：真正的主因不是"打分器弱"，而是**评测器也是 BM25**，所以检索改进被系统性抹掉。

**接 §8 那条原则**。这个故事的价值在于：你不是在复述"要有好 eval"这句正确的废话，
而是**有一次自己踩进去、量出来、公开推翻自己的记录**。

### 11.4 retrieval-first 的负结果 → 正结果

- 微调生成式 query rewriter：**跨域完全失败**（模型只记住训练主题的术语）；
- 直接换检索器（BM25 → dense，零训练）：**recall@5 0.165 → 0.576**；
- 微调 bi-encoder（跨主题 5 折 CV）：**0.276±0.150 → 0.600±0.086，5/5 折全升，标准差还降了**。

**一句话结论**（这句很 Exa）：
> **当瓶颈在检索时，改检索器比微调生成器便宜一个数量级，而且泛化性完全不同。**

**还有一条方法论**：这个数据集主题间难度差 10 倍，单次 holdout 的数字纯由抽到哪几个主题决定
（同一个零训练模型，dev 上 0.576、test 上 0.012）。**所以必须跨主题 CV。**
→ 这直接呼应 Exa 拒绝 MS MARCO 的第二条理由：50 文档量级的语料预测不了十亿级表现。

---

## 12. 反问（准备 4 个，问 2 个）

| 问题 | 为什么这么问 |
|---|---|
| "Highlights 那篇说你们试了很多架构才定下来。是抽取式打分还是 span-level？我很好奇切块边界是不是主要的误差来源。" | 显示你真读了，而且已经在他的问题空间里思考 |
| "RL 那篇的 skill transfer 结论很有意思——你们有没有反过来试过：用 agent 的 rollout 结果去反哺 reranker 的训练标签？" | 这是 §4.4 第 2 条，一个真实的、他们可能在做的想法 |
| "Canon 的 typestate 设计明显是为 agent 写代码准备的。团队现在实际有多少比例的搜索管线代码是 agent 写的？" | 接他们博客的原话，且这是个真实的工程文化问题 |
| "work trial 的两天，你们希望看到候选人交付什么形态的东西？" | 实际有用；也表明你在认真考虑下一步 |

---

## 13. 面试前一页速记（只看这一页）

**三个关键词 → 三套答案**：reranking（§4）· snippet generation（§3）· model alignment（§5）

**必须记住的数字（能引用 = 免掉半小时信任建立）**
- 向量库：**10 万簇 / 4096→256 维（20×）/ 二值量化（16×）/ <100ms / >500 QPS**
- BM25：**1.8TB per 十亿文档 → 砍半**，WAND 剪枝，延迟反而 **−10%**
- Highlights：**<100ms、不缓存**、**500 字符 ≈ 8000 字符（16× token）**、长文档 **60% vs 6%**
- RL：**Qwen3-4B + LoRA r32 + Dr. GRPO**，Exa vs SERP：**少 69% token、少 62% search call**，答案命中 **36.1% vs 32.6%**
- Canon：**20+ node 类型、pull-based、级联取消、memoize、typestate**
- WebCode：**discriminative 而非 generative**；**只用 2025-08-01 之后的库**抗污染

**三条算术（白板上写出来）**
1. `FLOPs ≈ 2 × 参数量 × token 数`
2. 100M cross-encoder，30ms，H100 → **约 90 个候选**。→ 候选数是算出来的，不是拍的
3. QPS 500 × 30ms = **15 GPU-秒/秒 → 25–30 张卡**（含余量）

**四句一定要说的话**
1. "先定成功的定义" —— 开场就写指标和 baseline 阶梯
2. "agent 不看排序，看集合" —— reranker 的目标从 nDCG 改成 set-level 覆盖 + 去冗余
3. "highlights 和 reranker 是互相喂的" —— 共享 chunk 缓存，Canon 里就是这个形状
4. "评测器不能和被评物同源" —— 配 §11.3 那个自己翻车的例子

**三个绝不能说**
- ❌ 把 Decagon 项目说成生产系统（它是自建实验台，GRPO 没跑到收敛）
- ❌ 把 Exa 博客的数字说成自己做过的
- ❌ 只画架构不算数 —— 这轮的差异化全在算术上

**最后一句**：不确定的地方明说是假设，然后给出**什么证据会让你改设计**。
Exa 整家公司的方法论就是 eval-first，这个姿态本身就是分。

---

## 14. 来源

- [WebCode: Search Evals for Coding Agents](https://exa.ai/blog/webcode)（recruiter 主动给的）
- [Exa Highlights](https://exa.ai/blog/highlights-for-agents) · [Scaling our highlights server](https://exa.ai/blog/scaling-our-highlights-server)
- [How Search Quality Shapes RL Outcomes](https://exa.ai/blog/rl-search-outcomes)
- [Composing a Search Engine（Canon）](https://exa.ai/blog/composing-a-search-engine)
- [How we built a web-scale vector database](https://exa.ai/blog/building-web-scale-vector-db)
- [Serving BM25 with 50% memory reduction](https://exa.ai/blog/bm25-optimization)
- [exa-d: Data Framework to Process the Web](https://exa.ai/blog/exa-d)
- [Introducing Deep Max](https://exa.ai/blog/deep-max) · [Exa Instant](https://exa.ai/blog/exa-instant) · [Exa Agent](https://exa.ai/blog/exa-agent)
- [How we do evals at Exa](https://exa.ai/blog/evals-at-exa) · [Meet the Exacluster](https://exa.ai/blog/meet-the-exacluster)
- [Exa 全部研究博客索引](https://exa.ai/research)
- [ZenML LLMOps · Exa 访谈（infra / 团队 / 产品分层）](https://www.zenml.io/llmops-database/building-a-search-engine-for-ai-agents-infrastructure-product-development-and-production-deployment)
