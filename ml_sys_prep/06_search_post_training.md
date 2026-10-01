# 06 · Search / Retrieval Post-training：Exa 类 AI Web Search

⏱ 通读约 35–45 分钟 ｜ 面试前优先背「90 秒开场」「训练目标」「Eval 表」「面试题」

> **三档阅读入口**（别从头读到尾，按你的时间预算选）
> - **Exa 面试前 3 分钟** → §一 90 秒开场 + §十五 面试前一页速记 + [13 · Exa 公司卡](13_company_cards.md)
> - **只有 15 分钟** → §一 + §五 为什么 click ≠ positive + §六 negative sampling + §十四 15 分钟白板模板
> - **完整（Day 2 下午）** → §一/§四/§五/§六/§七/§八/§九 + §十五
>
> 这题的两个题眼：**§五 点击的四种偏差**、**§六 hard negative 的 false-negative 陷阱**（top-k 里混着未标注的相关文档，直接当负例会伤召回）。Exa 自己在博客里讲过「从网页挖 embedding 训练数据的新方法」，§四 就是这个问题的正面回答。

这篇回答的不是「如何接一个向量数据库」，而是：**如何训练、评估并上线一个服务 AI agent 的 web search system**。它同时覆盖两类经常被混在一起的问题：

1. **Search stack 的模型训练**：query understanding、retriever、reranker、snippet/excerpt、quality/freshness。
2. **Search agent 的 post-training**：让 LLM 学会何时搜、搜什么、读哪些页面、何时停止、如何引用。

> 核心原则：先把 relevance、evidence、freshness 和 task success 分成独立可测的目标，再决定哪些组件共享训练信号。点击率不是 relevance，最终答案分数也不能替代 retrieval recall。

---

## 一、90 秒开场（建议背下来）⭐⭐⭐

> 我会先确认产品是给人看的十条蓝链接，还是给 agent 用的 retrieval API，因为后者更关心 evidence completeness、可解析正文、freshness、citation 和每个成功任务的总成本。系统上我会做分层 cascade：query understanding → lexical/dense candidate retrieval → learned reranking → content extraction → search agent / grounded answer。训练数据由四部分组成：人工 graded relevance、经过 propensity correction 的行为日志、document-to-query synthetic pairs，以及真实 agent trajectories。Retriever 用多正例 contrastive learning 和持续 hard-negative mining；reranker 用 pairwise/listwise relevance，并显式加入 authority、freshness、duplication 等特征；agent 先用高质量 demonstrations 做 SFT，再用 preference 或 outcome-verifiable RL 优化 task success，同时对 search calls、延迟、无效引用加成本。评估必须拆成 component、trajectory、answer、system 四层，并用按时间切分的 held-out queries 防止网页和答案泄漏。上线从 shadow 和 interleaving 开始，再做小流量 A/B，guardrail 是 citation correctness、source diversity、tail latency 与成本。

如果 interviewer 只给 30 分钟，把后面所有内容压缩成这五步：

```text
1. 定义用户任务与 freshness/cost SLO
2. 建立 query × candidate × graded label 数据闭环
3. hybrid recall → learned rerank → grounded synthesis
4. SFT demonstrations → preference/RL trajectories
5. temporal offline eval → shadow/interleave → A/B + rollback
```

---

## 二、先问清楚：我们到底在优化什么？⭐⭐⭐

### 2.1 六个需求问题

1. **消费者是谁？** 人类用户、RAG pipeline、coding agent，还是 autonomous research agent？
2. **任务形态？** navigational、factoid、multi-hop、exploratory、entity list、fresh news、people/company search？
3. **成功如何观察？** 找到一个 URL、收齐一组实体、回答正确，还是引用能支持每个 claim？
4. **语料范围？** 整个开放网页、专门 vertical index、客户私有 corpus；是否允许实时 fetch？
5. **SLO？** p50/p95 latency、QPS、每查询成本、index freshness、coverage、region/ACL？
6. **风险？** 错误医疗/金融信息、恶意网页 prompt injection、版权、PII、未成年人、SEO spam？

### 2.2 不同 query intent 需要不同成功定义

| Query 类型 | 例子 | 主要指标 | 常见误判 |
|---|---|---|---|
| Navigational | “Anthropic candidate AI policy” | MRR@1 / success@1 | 语义相近但不是官方网站 |
| Factoid | “1X Series B raised how much?” | answer accuracy + citation entailment | snippet 有答案但已过时 |
| Multi-hop | “找出 A 的创始人中曾任职 B 的人” | complete-chain recall | 只找到一半证据仍生成答案 |
| Exploratory | “agent memory 的主要方法” | subtopic coverage、diversity、utility | 十个近重复结果 |
| Entity/list | “NYC 具身智能公司” | set precision/recall、attribute coverage | 只评 top-1，漏掉长尾 |
| Fresh | “今天刚发布的模型” | freshness lag、temporal accuracy | 高权重旧页面压过新页面 |
| Agent action | “给这些公司补全融资轮次” | end-task completion / cost | 单个结果相关但无法执行任务 |

### 2.3 一个可讲的多目标函数

不要一开始就把所有东西揉成一个不可解释的 reward。先分别测，再在明确约束下做 trade-off：

\[
\max_\pi\; \mathbb{E}[U_{task}]
\quad \text{s.t.}\quad
P(\text{unsupported claim}) < \epsilon,
\; p95 < L,
\; C_{query} < B,
\; \text{freshness lag} < F
\]

线上若需要一个 routing objective，可以写：

\[
U = w_r R_{rel} + w_e R_{evidence} + w_f R_{fresh}
    + w_a R_{authority} - \lambda_c C - \lambda_l L - \lambda_s N_{search}
\]

但每个 term 仍要独立 dashboard；否则一个权重变化会掩盖 citation correctness 下降。

---

## 三、系统边界与白板架构

```text
                    ┌────────────── offline data / training ──────────────┐
Web crawl / feeds → parse → canonicalize → dedup → quality/safety → shards
       │                                      │                  │
       │                                      ├→ lexical index   ├→ label store
       │                                      └→ vector index    └→ training sets
       └───────────────────────────────────────────────────────────────────┘

Query
  ↓
Intent + rewrite + filters
  ↓
Candidate generation: BM25 / learned sparse / dense / vertical indexes
  ↓                 (high recall, e.g. 1K–10K)
Fusion + dedup + policy filters
  ↓
Light reranker → cross-encoder / late interaction → top N
  ↓
Fresh fetch + content extraction + passage/excerpt selection
  ↓
Search agent: inspect → reformulate → search/open/find → cite → stop
  ↓
Structured results or grounded answer

Every stage → trace, latency, cost, model/index/data versions
Feedback → impression/click/save/citation/task success/human correction
```

**面试高分点**：

- Retrieval candidate generation 要追求 recall；reranker 才负责 precision/order。不能用 answer model 掩盖 recall 缺失。
- Web page 和 passage 是两个 rank unit：先找对 page，不等于抽到了支持答案的 span。
- Index snapshot、parser version、embedding model version 必须进 trace；否则 offline regression 不可重放。
- Search output 是 untrusted input：prompt injection、安全策略和 source provenance 是 serving contract，不是 prompt 文案。

---

## 四、训练数据：从哪里来、如何变成 label ⭐⭐⭐

### 4.1 四层数据源

| 来源 | 能提供什么 | 优点 | 主要风险 |
|---|---|---|---|
| Human relevance judgments | `query, doc/passage, grade, rationale` | 最接近 construct | 贵；annotator disagreement；覆盖有限 |
| Product logs | impression、rank、click、dwell、save、copy、downstream use | 规模大、贴近真实分布、更新快 | exposure/position/trust bias；机器人流量；无点击含义不明 |
| Synthetic pairs | 从文档生成 query；teacher 给 relevance/quality；query perturbation | 覆盖 tail、cold start、稀有 vertical | teacher bias；模板味；答案泄漏；易生成过简单 query |
| Agent trajectories | search/open/find/cite/stop + outcome | 能训练 multi-step policy | reward attribution 难；旧 policy 的 selection bias |
| Public benchmarks | MS MARCO、BEIR、NQ、HotpotQA 等 | 快速 baseline、可比较 | 与生产 query/domain/freshness 不匹配 |

推荐 label schema：

```text
QueryRecord
  query_id, raw_query, locale, timestamp, intent, freshness_need,
  user/task cohort, sensitive_flags, source, split

CandidateJudgment
  query_id, url_id, passage_id, index_snapshot,
  relevance_grade: 0..3,
  answer_bearing: bool,
  evidence_span,
  authority_grade,
  freshness_status,
  harmful_or_injected,
  annotator_ids, rubric_version, adjudication

Trajectory
  task_id, initial_query, action_i, observation_i,
  cited_spans, final_answer, outcome_labels,
  total_searches, fetched_tokens, latency, cost,
  policy/search/index versions
```

### 4.2 人工 relevance rubric：不要只问“相关吗？”

建议四档：

- **3 — Directly useful**：直接满足 query intent，或包含完成任务所需证据。
- **2 — Partially useful**：主题相关且贡献一个子问题，但不足以独立回答。
- **1 — Topically related**：同主题但不能完成任务。
- **0 — Irrelevant / misleading**：不相关、过时导致结论错误、spam 或冲突页面。

另行标注四个正交维度：`evidence`, `authority`, `freshness`, `safety`。原因是：一个页面可以高度 topic-relevant，但不含可引用证据；也可以有答案但已经过期。

标注流程：

1. 写 rubric + anchor examples。
2. 每条至少双标，抽样三标；报告 raw agreement 与 weighted κ，而不是只报最终 consensus。
3. disagreement 进入 adjudication，并按 query type 分析。
4. 每次 rubric/model 改动都 version；不要把不同口径的 label 静默合并。
5. 用 active learning 选 uncertainty 高、模型分歧大、业务影响大的 query，而非只标随机样本。

### 4.3 Synthetic query–document/passage pairs

一个实用生成 pipeline：

```text
high-quality document
  → 抽取 atomic facts / section intents / entity relations
  → 生成 3–5 类 queries：keyword、natural question、underspecified、multi-hop、freshness-sensitive
  → 独立 verifier 检查 query 是否能被该 passage 支持
  → 与其他文档检索，挖出 confusing candidates
  → teacher/human 只复核 uncertain 与高价值样本
```

让 query 多样化，而不是全生成“According to this document ...”：

- 短 keyword：`exa binary quantization`
- 自然问题：`How does Exa reduce vector search memory?`
- 长语义描述：`find a post about a web-scale ANN system using nested embeddings`
- 模糊回忆：`那篇把 embedding 截短仍然可用的搜索文章`
- 时间限定：`after July 2026 latest publication search launch`
- 比较/否定：`methods that avoid cross-encoder cost but retain token interaction`
- multi-hop：需要两个独立页面才能回答的组合问题。

**防止 synthetic data 自嗨**：

- generator 和 judge 最好不是同一 checkpoint；保留 human audit slice。
- 必须加入真实 query distribution，并报告 synthetic-only vs mixed ablation。
- 检查 lexical overlap；否则 query 只是复制 passage，指标虚高。
- 先 split document/entity/time，再生成 query；否则同一页面的 paraphrase 会跨 train/test。

### 4.4 数据切分：web search 最容易泄漏的地方

至少做四个 held-out：

1. **Random query split**：用于快速迭代，但最弱。
2. **URL/domain split**：检查没见过网站的泛化。
3. **Entity/topic split**：避免同一公司/事件的 paraphrase 泄漏。
4. **Temporal split**：在 cutoff 后抓取的新页面和新事件，是 freshness 的主要真测试。

对于 multi-hop task，要把整条 evidence graph 放在同一 split；不能把 hop A 放训练、完整问题放测试。

---

## 五、点击和隐式反馈：为什么不能 `click = positive` ⭐⭐⭐

### 5.1 简化 click model

经典 position-based model 可写成：

\[
P(C=1 \mid q,d,k) = P(E=1 \mid k)\,P(R=1 \mid q,d)
\]

- `E`：用户是否 examination 第 `k` 个结果。
- `R`：结果是否对 query relevant。
- `C`：click。

现实中还要考虑 snippet attractiveness、brand trust、device、query intent、user cohort：

\[
C \leftarrow E(k, device) \times f(R, trust, snippet, user)
\]

所以：未点击可能只是没有被看见；点击也可能是标题诱导，而不是满意。

### 5.2 主要 bias

| Bias | 现象 | 处理 |
|---|---|---|
| Position / exposure | 排名高天然点击多 | 小流量 random swap/interleaving；propensity model；IPS/SNIPS |
| Trust bias | 用户更信 top result/知名域名 | 显式 trust-aware click model；独立 satisfaction signal |
| Selection bias | 旧 ranker 没展示的结果永远没 label | exploration bucket；candidate pool 扩充；counterfactual eval |
| Presentation bias | 好标题/图片骗点击 | 用 long dwell、return、task success；标正文 usefulness |
| Popularity feedback loop | 热门更曝光→更热门 | exploration、source diversity、long-tail audit |
| Query/user confounding | 不同 query 和 cohort 难度不同 | 分层/conditioned propensity；query-level randomization |
| Survivorship | 被删页面没有后续行为 | 记录 fetch failure、deletion 和 crawl snapshot |

### 5.3 IPS / SNIPS 如何解释

若结果在位置 `k` 被观察的 propensity 为 `p_k`，一个简化的 inverse propensity weighted loss：

\[
\hat L_{IPS} = \frac{1}{N}\sum_i \frac{C_i}{\hat p_{k_i}}\,\ell(f(q_i,d_i))
\]

低 propensity 样本权重大、variance 会爆炸，因此通常：

- propensity clipping：`1/max(p, p_min)`；
- SNIPS 自归一化；
- doubly robust estimator：结合 outcome model 与 propensity model；
- 最关键的 propensity 来自受控 randomization，而不是完全相信 observational log 拟合。

**高分回答**：

> 我不会把 no-click 当负例。日志首先是带 exposure policy 的观察数据；我会记录 impression 和 serving propensity，用少量受控 exploration 估计 position/trust bias，再用 IPS/SNIPS 或 doubly robust loss。最终仍保留人工 relevance 和 task-success holdout，因为 propensity correction 不能修复 label construct 本身。

---

## 六、Negative sampling：retriever 成败的关键 ⭐⭐⭐

### 6.1 Negative taxonomy

| 类型 | 如何得到 | 学到什么 | 风险 |
|---|---|---|---|
| Random negative | 全库随机 | 粗 topic distinction | 太容易，梯度很快归零 |
| In-batch negative | batch 其他 positives | 便宜、规模大 | false negative；同 batch 分布偏 |
| BM25 hard negative | lexical top result 但非正例 | 区分词面重叠 | label 不完整会误杀真相关 |
| Dense hard negative | 当前 retriever top result | 修复模型自身错误 | 训练震荡；过拟合当前模型 |
| Reranker-mined | teacher 高分但无证据 | fine semantic distinctions | teacher bias |
| Same-domain/entity | 同公司/同论文不同版本 | 属性、时间、关系精确度 | 需要细粒度 label |
| Stale/near-duplicate | 旧版本、镜像、转载 | freshness/canonicalization | relevance 与 freshness 要分标 |
| Adversarial | SEO spam、标题匹配正文不符 | 抗操纵 | 分布变化快 |

### 6.2 推荐的 mining loop

```text
warm-start retriever
  → 在冻结 index snapshot 上取 top K
  → 去掉已知 positives / near-duplicate positives
  → cross-encoder + human audit 给 uncertain candidates 分级
  → 混合 easy : medium : hard negatives
  → 训练新 checkpoint
  → 在固定 held-out + fresh snapshot 上比较
  → 只在通过 regression gates 后重新 mining
```

不要全用 hardest negatives：早期模型会被 false negatives 和极难例主导。可做 curriculum：先 random/in-batch，随后 BM25/dense，再加入 temporal/adversarial。

### 6.3 False negative 处理

- 每个 query 允许 **multiple positives**，graded relevance 不强制单 gold。
- 对 top-ranked unlabeled candidates 做 pooling annotation；“unjudged”不等于 negative。
- 使用 soft teacher labels 或 margin 与 relevance grade 对应。
- 同一事实的转载/镜像可以在 canonical cluster 内视为正例，但给 source authority 不同分。
- loss 中 mask 已知 near-duplicate 和同 evidence cluster。

---

## 七、训练三个 search components

## 7.1 Retriever：先保证召回

### Bi-encoder / dense retriever

分别编码 query 和 passage：

\[
s(q,d)=\operatorname{sim}(g_q(q),g_d(d))
\]

典型 multi-negative contrastive loss：

\[
L_q=-\log\frac{\sum_{d^+\in P(q)}\exp(s(q,d^+)/\tau)}
{\sum_{d\in P(q)\cup N(q)}\exp(s(q,d)/\tau)}
\]

训练要点：

- Query/document encoder 可共享或不共享；网页标题、正文、metadata 的格式与 query 很不同，需 ablation。
- 多正例 loss 比强迫一个 gold 更符合 web relevance。
- Cross-device negatives 扩大负例池，但要去重、mask false negative。
- Teacher distillation 可把 cross-encoder 的 graded score 压到 bi-encoder。
- 长文档先做 passage-level 表示，再聚合到 page；不要把 100K token 截成头 512 token。
- Multilingual/代码/表格需各自 slice；tokenization fertility 会影响效果和成本。

### Hybrid retrieval

Web search 不应默认 dense-only。BM25 对精确名称、错误码、数字、rare entity 很强；dense 对长描述和 paraphrase 强。常用 Reciprocal Rank Fusion：

\[
RRF(d)=\sum_m \frac{1}{k+rank_m(d)}
\]

也可以训练 query router 或 fusion ranker。第一版优先 hybrid + learned rerank，因为 robust baseline 比漂亮的单模型架构更重要。BEIR 的结果也提醒：BM25 是强 OOD baseline，而 late interaction/reranking 往往更准但更贵。

### Late interaction

像 ColBERT 一样预计算 document token embeddings，query token 与 document token 做 late interaction。它处于 bi-encoder 与 cross-encoder 之间：保留细粒度匹配、比逐对 cross-encode 便宜，但 index 大、serving 更复杂。

## 7.2 Reranker：在候选集上追求精排

可选训练 objective：

- **Pointwise**：预测 grade/utility；简单，但不直接优化排序。
- **Pairwise**：`d+ > d-`，如 logistic loss
  \[
  L=-\log \sigma(s(q,d^+)-s(q,d^-))
  \]
- **Listwise**：在候选 list 上拟合 graded distribution 或近似 nDCG；更贴近排序，但训练数据和实现更复杂。

实际 score 不应只有 topical relevance：

```text
features/model inputs:
  query ↔ title/body semantic match
  evidence-bearing passage score
  canonical/original source
  domain authority / spam risk
  publication + update time relative to query
  language/locale
  duplicate cluster
  fetch/extraction quality
```

不要让 authority 变成大站垄断：它是一个 calibrated feature/guardrail，并需 long-tail source audit。

## 7.3 Excerpt / evidence selector 与 answer model

对于 agent，返回整页导航栏比低排名更可能浪费 token。训练 excerpt selector：

1. 从人工 evidence span、citation span、answer-bearing passage 得监督。
2. 训练 passage ranker 或 span selector。
3. 给每个 excerpt 保存 URL、page version、char/token offsets。
4. 生成答案后做 claim → span entailment 检查。

Answer model 的 SFT 样本应包含：

```text
question
retrieved evidence with stable source ids
answer with atomic claims
claim → source/span mapping
explicit abstention when evidence incomplete
```

训练时加入四类反例：无答案、相互冲突、过时、恶意 prompt injection。目标不是“总能回答”，而是 evidence 不足时能继续搜或 abstain。

---

## 八、Search Agent Post-training：SFT → Preference → RL ⭐⭐⭐

### 8.1 把 trajectory 定义成可训练 episode

```text
state_t:
  user task, current subquestions, visited URLs,
  evidence table, remaining budget, timestamps

action_t:
  search(query, filters)
  open(url)
  find(pattern)
  extract(span)
  cite(claim, source)
  revise_plan(...)
  stop(answer)

observation_t:
  ranked results / page excerpt / fetch error / policy result
```

每一步必须记录 search engine/index snapshot；否则同一 action 未来返回不同网页，trajectory 不可复现。

### 8.2 Demonstrations 从哪里来

1. **Human expert traces**：人在受限 browser/tool 环境中完成真实任务。
2. **Best-of-N teacher rollouts**：强模型生成多条 trajectory，用独立 outcome/evidence verifier 选优。
3. **Production successes + corrections**：只在明确 consent、redaction、versioning 后使用。
4. **Programmatic task generation**：从结构化知识/网页变更生成可验证问题。
5. **Failure repair pairs**：把缺证据、重复搜索、错误引用轨迹修成 better trajectory。

数据要同时包含：

- search-required 与 search-free questions；否则模型会学会每题都搜。
- single-hop 与 multi-hop。
- 有答案、无答案、冲突证据、时效性强的问题。
- budget 紧与宽松场景。
- tool failure / 429 / dead link / parser failure。

### 8.3 阶段一：SFT / behavior cloning

目标是先学会协议和基本策略：

- query reformulation：从用户问题拆成可检索子问题；
- action schema：正确调用 search/open/cite；
- evidence ledger：不重复访问、记录每个 claim 缺什么；
- stop/abstain：证据完整才停止；
- citation：引用真正支持 claim 的 span。

SFT 的局限：模仿 demonstration 的冗余；对未见工具结果 exposure 不足；不会自动优化 cost。

### 8.4 阶段二：DPO / preference learning

构造相同 task 下的 `(chosen trajectory, rejected trajectory)`：

- 正确完整证据 > 只答对但引用错误；
- 少量有效搜索 > 重复十次相似 query；
- 官方/原始来源 > SEO 聚合转载（在同等证据下）；
- 识别冲突并说明 > 偷选一个来源；
- 合理 abstain > 无证据猜测。

Preference label 可以来自 human，也可以由 rubric grader 产生，但需对 judge 做 human calibration，避免 verbosity/style bias。

DPO 适合稳定、离线 pair 数据；它不会真正探索搜索环境，容易受 behavior policy support 限制。

### 8.5 阶段三：RL / outcome-verifiable training

让 policy 在线与冻结的 search snapshot/environment 交互。一个可解释 reward：

\[
r(\tau)=
w_1 r_{answer}
+w_2 r_{citation\_entail}
+w_3 r_{evidence\_coverage}
+w_4 r_{source\_quality}
-\lambda_1 n_{search}
-\lambda_2 tokens_{fetched}
-\lambda_3 latency
-\lambda_4 r_{unsafe}
\]

设计原则：

- **Outcome reward 为主**：可验证 QA、实体集合或 downstream task completion。
- **Process reward 只奖可观察行为**：引用 span 支持 claim、满足 freshness filter；不要奖漂亮思维过程。
- **检索文本不是 policy 生成 token**：计算 policy loss 时 mask observation/retrieved tokens，避免把环境输出当模型 action。
- Reward model/grader 在该训练阶段冻结；训练的是 policy，不要一边改 grader 一边声称 reward 上升。
- 对 search calls 加 penalty，但必须先满足 correctness constraint；否则模型学会“不搜最便宜”。
- 先在固定 index snapshot 训练以降低 non-stationarity，再评估 live web。

### 8.6 Reward hacking 清单

| Reward | 可能 hack | 防线 |
|---|---|---|
| Answer exact match | 猜答案、不搜 | freshness/OOD/no-answer set；evidence gate |
| Citation count | 堆很多无关引用 | claim-level entailment precision + coverage |
| Search penalty | 永不搜索 | search-required tasks；correctness constraint |
| Source authority | 只用大站、漏长尾 | evidence utility + diversity slice |
| LLM judge score | 冗长、迎合 judge style | deterministic checks + human calibration + judge ensemble/holdout |
| Dwell/click | clickbait 排名上升 | long-term satisfaction、return-to-SERP、task completion |

> 高分句：reward 应该奖励“环境中可验证的结果”，不是模型自己宣称已完成；citation correctness 不能只靠同一个 answer model 自评。

---

## 九、Evaluation：四层、切片、上线实验 ⭐⭐⭐

### 9.1 四层 eval contract

| 层级 | 核心问题 | 主要指标 |
|---|---|---|
| Component — retrieval | gold evidence 有没有被召回？ | Recall@k、MRR、nDCG@k、MAP、set recall |
| Component — extraction/rerank | 正确 passage 是否排前且可读？ | passage nDCG、evidence-span recall、dup rate |
| Trajectory | 搜索策略是否高效可靠？ | success-by-step、query diversity、repeat rate、search/open counts、stop accuracy |
| Answer/outcome | 最终任务是否真正完成？ | EM/F1、task success、claim precision/recall、citation entailment/coverage |
| System | 能否经济稳定地运行？ | p50/p95/p99、$/successful task、QPS、freshness lag、failure rate |
| Safety/policy | 是否越权或被网页操纵？ | injection success、unsafe-source use、PII leakage、ACL violations |

### 9.2 检索公式要能白板写

**Recall@k**：

\[
Recall@k=\frac{|Relevant(q)\cap TopK(q)|}{|Relevant(q)|}
\]

Factoid 只有一个 gold 时常看 `Hit@k`；entity/list search 更应看 set recall。

**MRR**：

\[
MRR=\frac{1}{|Q|}\sum_q \frac{1}{rank_q^{first\ relevant}}
\]

适合 navigational/第一个有用结果，但忽略后续 relevant documents。

**nDCG@k**：

\[
DCG@k=\sum_{i=1}^{k}\frac{2^{rel_i}-1}{\log_2(i+1)},
\qquad nDCG@k=\frac{DCG@k}{IDCG@k}
\]

适合 graded relevance 和多个有用结果。

### 9.3 Agentic search 特有指标

- **Complete-chain recall**：multi-hop 所有必要 evidence 是否都拿到；只拿 1/2 不算完整。
- **Claim coverage**：最终答案有多少 atomic claims 被有效 source span 支持。
- **Citation precision**：引用是否真的 entail 对应 claim。
- **Citation source recall**：gold/必要来源有多少被使用。
- **Search necessity accuracy**：该搜时搜、不该搜时不搜。
- **Stop accuracy**：证据完整才停止；无答案能 abstain。
- **Cost per successful task**：总平均成本会奖励便宜失败，必须除以成功数或画 Pareto frontier。
- **Freshness accuracy**：对有 time cutoff 的答案是否只使用有效版本。
- **Robustness**：query typo、长描述、语言切换、dead links、conflicting sources、SEO/prompt injection。

### 9.4 Offline 数据集设计

推荐最少六桶：

1. Head production queries。
2. Tail/OOD/niche descriptions。
3. Fresh events，严格 temporal cutoff。
4. Multi-hop 和 entity/list tasks。
5. No-answer/conflicting evidence。
6. Adversarial spam/injection/low-quality pages。

每次报告必须按 intent、locale、freshness、domain、query length、head/tail、device/agent client 切片。一个 aggregate nDCG 上升可能掩盖 fresh query 大幅退化。

### 9.5 Online experiment

```text
replay on frozen logs
  → shadow traffic（不影响用户）
  → team-draft interleaving / 小流量 randomization
  → 1–5% canary A/B
  → gradual rollout
  → rollback on correctness/safety/cost/latency guardrail
```

线上主指标优先 downstream：

- agent task completion / human acceptance；
- successful citation use、save/export；
- query reformulation/abandonment/return-to-SERP；
- long click 仅作 proxy；
- 每成功任务 search calls、tokens、latency、cost；
- freshness complaints、unsupported-claim reports。

**Interleaving** 往往比标准 A/B 更快比较两个 ranker，因为同一 query 的结果交错展示并比较偏好；但它不适用于所有 answer/agent UX，仍需最终 A/B 看整体 task outcome。

---

## 十、Freshness、Serving 与成本

### 10.1 Freshness 是一条独立数据链

```text
discovery (crawl/feed/sitemap)
  → fetch scheduling
  → parse + canonicalize
  → incremental lexical/vector indexing
  → cache invalidation
  → query-time temporal ranking
```

要定义：

- `discovery lag`：页面发布到发现。
- `fetch lag`：发现到成功抓取。
- `index lag`：抓取到可检索。
- `answer staleness`：用户查询时用了多久前的内容。

按 domain change rate 动态 recrawl；新闻、职位、金融页面比静态论文更频繁。支持删除/takedown 和 canonical version 替换。query classifier 判断 freshness intent，并把 `as_of` 传入 ranking/answer。

### 10.2 Cost-efficient serving cascade

```text
query cache / normalized query
  → cheap intent + lexical/dense ANN (top 1K)
  → lightweight reranker (top 100)
  → expensive cross-encoder (top 10–30)
  → fetch/extract only selected pages
  → answer model tier based on difficulty/confidence
```

优化旋钮：

- **ANN**：HNSW/IVF/PQ、binary quantization、Matryoshka/nested embeddings；报告 recall–latency–memory Pareto。
- **Precompute**：document embeddings 离线；增量 index 分 segment，后台 merge。
- **Dynamic top-k**：容易 navigational query 少取，multi-hop/low-confidence 扩展。
- **Early exit**：reranker confidence 足够就不调用大 cross-encoder。
- **Cache**：query/result/excerpt cache 带 index version 与 TTL；fresh query 不盲目复用。
- **Token budget**：返回 dense, query-specific excerpts，而不是整个页面。
- **Model routing**：rewrite/extract 用小模型，复杂 synthesis 才上 frontier model。
- **Parallelism**：独立 subqueries/fetch 并发，但设 per-host limit、deadline 和 global budget。

不要只给“量化、缓存、batching”三个词。面试里要说清它们影响的是哪段 latency、是否损失 recall、如何用 canary 验证。

### 10.3 Capacity 粗估模板

假设峰值 `Q` queries/s，每 query：

- candidate retrieval `K_0`；
- light rerank `K_1`；
- cross-encode `K_2` pairs；
- 平均 `S` 次 agent searches。

那么 cross-encoder pair throughput 约：

\[
TPS_{pair}=Q\cdot S\cdot K_2
\]

如果 `Q=1000`, `S=3`, `K_2=20`，就是 60K pairs/s；这会迫使你做 batching、small reranker、early exit 或降低 `K_2`，而不是简单部署一个最大模型。

---

## 十一、端到端例题：为 Exa 训练 “deep company research”

### 题目

> 设计一个系统，让 agent 回答：“找出 2026 年获得 Series B、在纽约招聘 research scientist 的具身智能公司，并给出融资和职位的一手来源。”如何收集数据、训练和评估？

### 11.1 需求与 gold

- 输出是 entity set，不是单答案。
- 每个 entity 需要两条证据边：`company → financing event`、`company → active role/location`。
- freshness cutoff 是 query time；职位可能关闭。
- 优先公司/投资方公告和官方 careers，而非聚合站。

Gold record：

```text
entity_id
funding: {round, date, amount, source_url, span, valid_at}
role: {title, location, status, source_url, span, valid_at}
```

### 11.2 数据

1. 从官方 funding announcements、VC portfolio、career pages 采 seed evidence graph。
2. 人工编写 head + natural + underspecified queries。
3. 从每个 evidence edge 生成 synthetic single-hop/multi-hop queries。
4. Hard negatives：同名公司、2025 融资、Series A、关闭职位、非 NYC、新闻转载。
5. Temporal split：训练 cutoff 前页面；测试 cutoff 后新融资/新职位。

### 11.3 模型与训练

1. Hybrid retriever 先分别召回 company/funding/career pages。
2. Reranker 学 relevance + official source + valid date。
3. Evidence selector 定位融资/职位 span。
4. Agent SFT 学会拆成 funding search 与 careers search，并 join entity。
5. Preference pairs 奖励完整两条 evidence edge、惩罚旧职位和聚合站。
6. RL outcome 由结构化 gold set 计算 F1，citation entailment 作为 gate；search calls 和 tokens 是二级 penalty。

### 11.4 Eval

- Retriever：每条 evidence edge 的 Recall@20；complete-chain recall。
- Entity output：set precision/recall/F1。
- Citation：claim-level entailment 与 URL validity。
- Freshness：关闭职位是否仍被输出。
- System：p95、$/successful completed entity、search calls。
- Slice：new/obscure companies、同名实体、career ATS provider、职位刚关闭。

### 11.5 面试总结句

> 这不是普通 QA：retrieval gold 是一张随时间变化的 evidence graph。我的 primary metric 是完整证据链和 entity-set F1，而不是单页 nDCG；训练时把 stale page 作为精细 hard negative，上线时让 freshness version 贯穿 crawl、rank、cache 和 citation。

---

## 十二、常见 failure modes 与 debug 顺序

| 症状 | 首先查 | 可能根因 | 修复方向 |
|---|---|---|---|
| 答案错但 citation 看似对 | claim→span | citation 只 topic match，不 entail | atomic claim grader、human audit |
| Relevant page 从未出现 | candidate recall | index coverage、chunking、embedding、filter | 先修 crawl/index/retriever，不调 answer prompt |
| Offline nDCG 升、线上差 | slices/log policy | label leakage、click bias、query drift | temporal holdout、exploration、downstream metric |
| 搜索次数越来越多 | trajectory | SFT 冗余、reward 无 cost/stop | stop labels、budget、Pareto eval |
| 搜索次数为零但答得流畅 | search necessity | cost penalty 过大、benchmark 可背 | fresh/no-answer tasks、evidence gate |
| 只返回大站 | source mix | authority feature domination | diversity/long-tail slice、calibration |
| 新页面搜不到 | freshness funnel | recrawl/index/cache lag | 分段测 lag，event-driven updates |
| Hard-negative 训练退化 | labels | false negatives、过难、teacher bias | pooling annotation、multi-positive、curriculum |
| Latency tail 爆炸 | trace waterfall | dead host、串行 fetch、large rerank K | deadlines、bounded parallelism、early exit |
| 被网页指令劫持 | tool boundary | page text进入高权重 prompt | untrusted data channel、policy、injection eval |

Debug 顺序建议：

```text
coverage/index → candidate recall → reranking → excerpt/evidence
→ agent policy → answer synthesis → online UX/feedback
```

不要一看到最终答案错就 fine-tune generator。先找“第一个发生错误的 stage”。

---

## 十三、面试题与答题 walkthrough

### Q1：没有 query–document labels，怎么 cold start？

**回答结构**：

1. BM25 + strong off-the-shelf dense model 建 baseline。
2. 从高质量文档反向生成 diverse queries，做 teacher verification。
3. 用公共 retrieval/QA 数据 warm-start，但单独报告 domain gap。
4. 小规模 human pool 对真实 query 标 graded relevance。
5. 上线 shadow；用受控 exploration 获取 unbiased-ish implicit feedback。
6. Active learning 优先标模型分歧和高业务价值。

不要答“直接用点击数据”：cold start 根本没有足够 exposure，而且 bias 最大。

### Q2：为什么不直接让大 LLM 对所有网页打分？

Web scale 候选量太大、成本和延迟不可接受；LLM 只能在高-recall candidate pool 上做 teacher/reranker。还要考虑 index coverage——LLM 看不到没被召回的页面。用 cascade 把 expensive model 放在 top K，并通过 distillation/early exit 降低 serving cost。

### Q3：如何选 hard negatives？

先按阶段混合 random/in-batch、BM25、dense-mined、same-entity temporal negatives；unjudged candidates 不直接当负例，top pool 人工/teacher 分级；每轮 mining 冻结 snapshot，保留固定 test；监控 false-negative rate 和 negative hardness 分布。

### Q4：点击率上涨是否说明 search 更好？

不一定。可能是 position、标题诱导或新 UI。需要 impression propensity、random swap/interleaving、IPS/SNIPS；同时看 long-term satisfaction、reformulation、return、downstream completion。用人工 relevance holdout 验证构念。

### Q5：Retriever 该用 bi-encoder、ColBERT 还是 cross-encoder？

不是三选一：bi-encoder/learned sparse 做 web-scale candidate recall；late interaction 可在更高成本下增强 fine-grained retrieval；cross-encoder 放 top K 精排。最终按 recall–latency–index memory–cost Pareto 和 query slices 选择。

### Q6：怎么训练 query rewriting？

- 数据：真实 reformulation session、专家拆解、teacher-generated multi-hop subqueries。
- SFT：预测 normalized query/filters/subqueries。
- Pair preference：能提高 evidence recall 且少重复的 rewrite 胜。
- RL：最终 task success + evidence gain，惩罚 duplicate/empty query。
- Eval：rewrite 本身 BLEU 没意义；看 downstream Recall@k、complete-chain recall、cost。

### Q7：怎么让 agent 知道何时停止搜索？

维护显式 evidence ledger：每个 required claim/subgoal 的状态。训练中加入证据完整、缺失、冲突和 no-answer trajectories；stop reward 只在 outcome verifier 确认 acceptance criteria 时给。测 premature-stop rate 与 over-search rate，画 quality/cost frontier。

### Q8：Outcome reward 与 process reward 怎么选？

可验证任务优先 outcome，避免规定唯一思路；process 只约束必要且可观测的行为，如 citation entailment、policy violation、budget。若 outcome 稀疏，可用 potential-based/step evidence gain shaping，但要做 ablation，确保没有把 shortcut 变成目标。

### Q9：如何评价 citation？

先把答案拆成 atomic claims；每个 claim 映射 source span。分别测 citation precision（span 是否支持）、claim coverage（有多少 claim 被支持）、source correctness/freshness。Deterministic span/version 检查 + NLI/LLM judge + human calibration，不用 citation 数量代替正确性。

### Q10：训练 search agent 时为什么 mask retrieved tokens？

检索结果是 environment observation，不是 policy 选择生成的 action。若把 observation token 纳入 policy gradient，会把 credit 错分给不可控网页文本，训练不稳定甚至鼓励选择更容易“预测”的页面，而非更有用的搜索动作。

### Q11：如何处理网页不断变化导致 RL environment 非平稳？

训练/回归先用 versioned frozen index snapshot；每个 observation 记录 content hash。模型通过 gate 后再在 live shadow 测 freshness/generalization。生产 trace 保存 query、URL、snapshot/version，不能只存当前页面链接。

### Q12：如果 offline Recall@k 很好但 answer accuracy 差？

逐层检查：gold page 是否有 gold passage；excerpt 是否包含答案；answer model是否忽略/误读；evidence是否冲突；citation/answer rubric 是否正确。补 passage-level labels和 complete-chain recall，而不是继续扩大 top-k 导致 token/cost 上升。

### Q13：如果 answer accuracy 上升但 Recall@k 下降，是否可以上线？

不能仅凭平均 answer accuracy。可能 generator 用参数记忆或 benchmark leakage 猜对。对 fresh/OOD/no-answer、citation-required slice 检查，要求 evidence coverage guardrail；下游若依赖列表完整性，recall 下降会产生隐藏损害。

### Q14：如何防止 search engine 被 SEO spam 训练污染？

采集层做 canonical/domain/spam/malware signals；标注 adversarial negative；ranker 分离 relevance 与 source quality；上线监控 domain concentration、新域异常、clickbait high-click-low-satisfaction；保留人工 red-team 和快速 block/rollback 通道。

### Q15：怎样证明 synthetic queries 有价值？

做 compute/data-matched ablation：真实-only、synthetic-only、mixed；同一个 base model/hyperparameter，按 real held-out/temporal/OOD slices 比较。检查 lexical overlap、query diversity、teacher-human agreement；只有在真实 held-out task improvement 上才算有效。

### Q16：如何把 production feedback 用进训练而不形成 feedback loop？

完整记录 serving policy/propensity；保留 exploration traffic；对 exposure 做 correction；train/eval 时间切分；监控 source/query distribution；旧 ranker 未展示的候选用 independent crawl/pool 补齐。新模型先 shadow，不直接全量反哺自身日志。

### Q17：Search quality 和 agent quality 谁负责？

接口 contract 要可归因：search 服务报告 retrieval labels/coverage、ranker/index versions；agent 报 query plan、selected results、outcome。用 oracle retrieval 测 agent upper bound、oracle agent/query 测 search upper bound，避免团队互相归咎。

### Q18：Exa 类系统最重要的 cost metric？

不是单次 API 平均成本，而是 **cost per successful downstream task**，并拆 search、fetch/extract、rerank、LLM tokens。还要看 p95/p99，因为 agent 并行搜索会放大 tail latency。

### Q19：如何测试 fresh search？

建立滚动 temporal benchmark：每天/每周从 cutoff 后新事件生成问题，gold 保留发布/抓取/index 时间。测 discovery/fetch/index 各段 lag、fresh answer accuracy、stale citation rate；cache key 带 snapshot/TTL。

### Q20：v1 最小可行方案是什么？

BM25 + off-the-shelf dense hybrid → RRF → small cross-encoder → structured excerpts；1000–5000 条真实 graded queries + synthetic tail；component/offline temporal eval；agent 用 SFT demonstrations，暂不 RL。上线 shadow 后确认 outcome 信号和日志质量，再做 preference/RL。

---

## 十四、十五分钟白板答题模板

| 分钟 | 讲什么 | 必须落下的产出 |
|---|---|---|
| 0–2 | 用户、query types、SLO、risk | task success + freshness/cost constraint |
| 2–4 | 架构 | hybrid recall → rerank → evidence → agent |
| 4–7 | 数据/labels | human + logs correction + synthetic + trajectories |
| 7–9 | 模型/loss | contrastive retriever、listwise rerank、SFT/DPO/RL |
| 9–11 | hard negatives/bias | false negative、position bias、temporal split |
| 11–13 | eval | component/trajectory/outcome/system + slices |
| 13–15 | serving/rollout/trade-offs | cascade、freshness、shadow→A/B→rollback |

万能结尾：

> v1 我会优先建立可归因的 hybrid retrieval baseline 和可信 temporal eval；当 component recall 与 citation evidence 都过线后，再用 production trajectories 优化 agent。最大的风险是把 biased clicks 或 answer-model 自评误当 truth，所以 exposure policy、grader provenance、index snapshot 和 human audit 都进入数据 contract。

---

## 十五、面试前一页速记

### 必背 10 句

1. Candidate retrieval 优化 recall，reranker 优化 ordering，generator 不能补回没召回的证据。
2. Click 是 `exposure × relevance × presentation/trust` 的结果，不是 relevance label。
3. Unjudged 不是 negative；web search 天生有 multiple positives。
4. Hard-negative mining 必须控制 false negatives，并在冻结 snapshot 上迭代。
5. Dense-only 会丢 rare entity/数字；hybrid 是强 baseline。
6. Agent eval 要测 complete evidence chain，不只测最终答案是否碰巧正确。
7. Search calls penalty 必须受 correctness/evidence constraint 约束，否则模型会学会不搜。
8. Freshness 要拆 discovery、fetch、index、cache、answer 五段 lag。
9. 训练 grader 与 policy 的更新边界必须明确；grader 不应随着 policy 一起漂移。
10. 线上看 cost per successful task，并把 p95/p99 和 citation correctness 设成 guardrail。

### 必背公式

```text
Contrastive: -log exp(s+)/Σ exp(s)
Pairwise:    -log σ(s+ - s-)
IPS:         click_loss / propensity(position)
Recall@k:    relevant in top-k / all relevant
MRR:         mean(1 / first relevant rank)
nDCG:        graded discounted gain / ideal gain
Agent reward: answer + evidence + freshness - calls - tokens - latency - unsafe
```

### 绝不能说

- “点击就是正例，没点击就是负例。”
- “用一个 LLM judge 就能得到 ground truth。”
- “Recall@k 高，所以答案一定正确。”
- “加大 top-k 就能解决 multi-hop。”
- “用 RL 后模型自然会学会何时搜索。”
- “缓存可以提高性能”——却不谈 freshness invalidation。

---

## 十六、延伸阅读（按面试价值排序）

1. [Exa Research](https://exa.ai/research)：Exa 自己训练、嵌入并服务 web-scale search index/model 的研究入口。
2. [Exa Search API](https://exa.ai/docs/reference/search) 与 [Agent API](https://exa.ai/docs/reference/agent-api/overview)：截至 2026-07 的官方产品边界；区分单次 search/content 与异步多步 research agent。
3. [Exa: web-scale vector database](https://exa.ai/blog/building-web-scale-vector-db)：Matryoshka embeddings、binary quantization 与 web-scale serving trade-off。
4. [Exa Highlights](https://exa.ai/blog/highlights-for-agents)：excerpt selection 如何在 agentic search 中同时影响 token cost 与 grounding quality。
5. [WebGPT](https://arxiv.org/abs/2112.09332)：browser demonstrations、behavior cloning、human preference/reward model 与引用。
6. [Search-R1](https://arxiv.org/abs/2503.09516)：reasoning/search interleaved RL、outcome reward 与 retrieved-token masking。
7. [MMSearch-R1](https://arxiv.org/abs/2506.20670)：search-required/search-free mixture、search penalty 与 multimodal multi-turn search。
8. [Unbiased Learning-to-Rank with Biased Feedback](https://www.ijcai.org/proceedings/2018/738)：position bias、counterfactual learning 与 propensity weighting。
9. [BEIR](https://arxiv.org/abs/2104.08663)：heterogeneous zero-shot retrieval benchmark 与 BM25/dense/rerank trade-off。
10. [ColBERT](https://arxiv.org/abs/2004.12832)：late interaction 的效果/成本位置。

阅读策略：先读 abstract、method diagram、data、objective、eval split、failure/ablation；面试不需要背论文数字，但必须能解释它解决的 construct 和代价。
