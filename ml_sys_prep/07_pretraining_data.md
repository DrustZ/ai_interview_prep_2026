# 07 · Pre-training Data Systems：从原始网页到可审计训练 tokens

⏱ 通读约 40–50 分钟 ｜ 面试前优先背「90 秒开场」「funnel」「数据短缺」「ablation」「面试题」

> **三档阅读入口**（本文 1200+ 行，是全目录最长的，务必按预算选节）
> - **OpenAI 面试前 5 分钟** → §一 90 秒开场 + §二十 一页速记（funnel 默写 + 必背 12 句 + 绝不能说 8 条）
> - **只有 20 分钟** → §一 + §六 dedup + §七 filtering + §九 mixture + §二十
> - **完整（Day 2 晨）** → §一/§六/§七/§八/§九/§十/§十三 + **§十八 24 问遮答案自测** + §二十 默写
>
> 这篇的三个题眼：**§七 quality classifier 的正样本从哪来**、**§八 污染不能只做 exact match**、**§十三 数据价值只能由固定算力的训练 ablation 证明**（不是 quality score、不是 training loss）。
>
> 想动手：[`../../cs336/assignment4-data/`](../../cs336/assignment4-data/) 就是这条 funnel 的可跑作业，handout PDF 里有完整实验设置。

这篇把 pre-training data 当成一个 **ML system + data governance system**，而不是“Common Crawl 清洗一下”。面试官真正想听的是：

- 从哪里合法、稳定地获取数据；
- 如何 extraction、去重、过滤、混合、tokenize；
- 如何证明某个数据决策让模型更好；
- 数据不足、低资源语言、专业领域怎么办；
- 如何控制 contamination、PII、copyright、bias；
- 如何让 trillion-token pipeline 可重放、可删除、可监控、成本可承受。

> 核心原则：每个训练 token 都应该能回答四个问题——它从哪里来、经过什么变换、为什么被保留、进入了哪个 model run。数据质量最终要由受控训练实验验证，heuristic 或 LLM quality score 都只是 proxy。

---

## 一、90 秒开场（建议背下来）⭐⭐⭐

> 我会先从目标能力、语言/领域、context length、参数与 compute budget、许可和安全边界反推 token budget 与 source mixture。数据链分为 immutable raw acquisition、结构化 extraction、language/safety/quality filtering、exact/near/semantic dedup、benchmark decontamination、mixture sampling、tokenization/packing 和 versioned sharding。每条 document 都带 source URI、fetch time、license/consent、content hash、父子变换与 filter decisions，保证 lineage、takedown 和可重放。质量不能只靠规则或大模型打分：我会在固定模型、训练 tokens 和 compute 下用小型 proxy runs 做 source/filter/mixture ablation，再在目标能力、per-domain validation loss、memorization、安全与 bias slices 上验证。数据短缺时优先提高有效信息密度、补合法的 first-party/licensed/low-resource data、优化 mixture，再谨慎使用经过 verifier 的 synthetic data 和有限重复；不能把同一低质量网页多跑几 epoch 当作新信息。生产上用 content-addressed manifests、幂等 stage、可恢复 sharding、funnel/分布监控和数据版本锁定，确保一次昂贵训练可以被解释和复现。

15 分钟题的骨架：

```text
Requirements / rights
  → raw immutable acquisition
  → extraction + normalization
  → safety/quality/language filters
  → exact + near dedup + decontamination
  → source mixture + curriculum
  → tokenizer + packing + shards
  → proxy ablations + full-run gates
  → lineage, deletion, monitoring
```

---

## 二、第一步不是 crawl：先定 model/data contract ⭐⭐⭐

### 2.1 开场七问

1. **目标模型是什么？** general LLM、code、multilingual、medical/science、search foundation model，还是 continued pretraining？
2. **目标能力与用户分布？** reasoning、knowledge、code、long context、低资源语言、domain terminology？
3. **模型/compute budget？** 参数量、训练 FLOPs、token budget、重复 epoch 上限、deadline？
4. **训练目标？** causal LM、masked/denoising、FIM for code、multimodal alignment？
5. **数据权利边界？** public domain、licensed、first-party consent、robots/terms、region、retention、opt-out？
6. **安全边界？** PII、secrets、malware、CSAM、NSFW、medical records、private repositories？
7. **成功标准？** held-out loss、target benchmarks、fresh/private eval、safety/bias/memorization、inference economics？

### 2.2 Token budget 的粗估

Dense transformer 训练 FLOPs 常用数量级估计：

\[
C \approx 6ND
\]

- `N`：non-embedding parameters。
- `D`：training tokens。
- `C`：训练 FLOPs。

它只适合 capacity planning，不替代真实 profiler；architecture、sequence length、MoE、activation checkpoint、hardware utilization 都会改变成本。

Chinchilla 的意义不是死背“20 tokens/parameter”，而是：**固定 compute 时，参数量和训练 tokens 必须联合选择**。现代模型还会考虑 inference volume，可能更愿意训练较小模型更多 tokens；最终需自己的 scaling study。

### 2.3 明确 acceptance criteria

示例：训练 7B multilingual search/code model：

```text
Hard constraints
  - approved source/license classes only
  - zero known benchmark exact matches after decontamination stage
  - PII/secrets detector recall ≥ agreed threshold on human test set
  - every shard resolvable to versioned source manifests

Quality objectives
  - target language/domain validation loss
  - code completion + retrieval + multilingual held-out tasks
  - low memorization on canary/extraction tests
  - no material regression on safety/bias slices

System objectives
  - pipeline restartable/idempotent
  - deletion/takedown propagated to future releases
  - deterministic dataset version and token count
```

---

## 三、白板架构：control plane 与 data plane

```text
                            ┌──── Data catalog / policy registry ────┐
Sources / licenses / consent│ source rights, retention, versions     │
           │                └────────────────────────────────────────┘
           ▼
Raw acquisition → immutable object store (WARC/files + metadata)
           │
           ▼
Parser/OCR/code extractor → normalized structured documents
           │
           ├→ language / safety / PII / secret classifiers
           ├→ heuristic + learned quality signals
           ├→ exact / paragraph / MinHash / semantic dedup
           └→ benchmark contamination scanner
           │
           ▼
Curated source pools → mixture sampler / curriculum → tokenizer / packer
           │
           ▼
Versioned train shards + manifest + checksums
           │
           ├→ proxy training / data ablations / eval
           └→ full pretraining loader

Every transform → lineage event, counts/bytes/tokens in/out, reason codes,
                  code/config/model versions, sample audit, deletion index
```

**Control plane** 决定 source policy、pipeline DAG、versions、mixture、deletion；**data plane** 执行 fetch/parse/filter/dedup/tokenize。Policy 不应散落在 worker 的 ad-hoc `if` 中。

---

## 四、Data acquisition：从哪里来，以及如何管理权利 ⭐⭐⭐

### 4.1 Source portfolio

| Source | 价值 | 风险/偏差 | 需要保留的 metadata |
|---|---|---|---|
| Web crawl / Common Crawl | 规模、长尾、时效 | spam、重复、未知权利、PII、网页模板 | URL、crawl/fetch time、WARC offset、HTTP headers、robots/terms snapshot |
| Wikipedia / public knowledge | 高结构、事实密度、多语言 | 风格单一、覆盖偏差 | revision ID、license、language |
| Public-domain/licensed books | 长文、叙事、知识 | OCR、版本/许可、文化偏差 | edition、rights basis、page/section |
| Scientific papers | technical reasoning、公式 | PDF extraction、版权、引用结构 | DOI、publisher/license、version、sections |
| Documentation/forums/Q&A | procedural knowledge、真实问题 | 许可、用户 PII、低质量回答 | thread/revision、author visibility、license |
| Code repositories | syntax/API/SE patterns | license、secrets、vendored/generated code、malware | repo/commit/path、SPDX、fork lineage |
| First-party/customer data | 产品分布、独特价值 | consent、purpose limitation、tenant leakage | consent/purpose、tenant、retention、access policy |
| Licensed publisher/vendor data | 高质量、稳定 | 成本、scope/term 限制、续约 | contract/version、allowed uses、expiration |
| Synthetic data | 稀有能力、可控 rubric | model collapse、teacher bias、contamination | generator/judge/prompt/version、seed、provenance |
| Human-created curriculum | 高难度、目标明确 | 贵、规模小、annotator bias | rubric、annotator/adjudication、rights |

### 4.2 Crawl 系统需要讲的组件

```text
seed URLs / sitemap / feeds / discovered links
  → URL frontier (priority, host, next_fetch_at)
  → robots/terms/policy check
  → per-host politeness + DNS/HTTP fetch
  → immutable response/WARC + metadata
  → link extraction + canonicalization
  → recrawl scheduler based on change rate/value
```

重要设计：

- URL canonicalization 去 tracking parameters、fragment，处理 redirects/canonical tags；但不能把有语义的 query parameters 全删。
- Per-host rate limit、robots、legal/policy registry、deny/allow list。
- Content hash 判断 change；按 domain/URL 历史变化率安排 recrawl。
- Raw bytes immutable，parser bug 修复时不用重新抓取。
- HTML status、MIME、encoding、fetch time、IP/region、response headers 进入 provenance。
- Tombstone/deletion event 不能只删除 catalog row；要能定位所有 derived docs/shards 和未来 dataset release。

### 4.3 Licensing / consent 不是一个 boolean

推荐 rights record：

```text
RightsRecord
  source_id, asset_id, owner/provider
  legal_basis_or_license_id
  allowed_purposes: [research, commercial_train, redistribution, eval]
  geography, effective_at, expires_at
  attribution_required, share_alike, opt_out_path
  policy_review_version, evidence_pointer
```

一个 URL “公开可访问”不自动等于可用于任何商业训练。具体判断交给 legal/privacy/security；ML system 的责任是保留证据、执行 policy、隔离未知权利数据，并能响应删除/期限变化。

对于 code，每个 repository/file 的 license、fork/vendor lineage、attribution 可能不同。The Stack 的做法值得作为治理案例：保留逐样本 provenance、选择 permissive licenses，并提供 opt-out/removal 流程；不是说它解决了所有法律问题。

---

## 五、Extraction：坏 parser 会比坏模型更早毁掉数据

### 5.1 统一 document schema

```text
DocumentRecord
  doc_id, source_id, source_uri, fetched_at, published_at
  mime_type, language_probs
  title, sections[{heading_path, text, offsets, type}]
  tables/code/math/alt_text
  raw_blob_pointer, content_hash, parent_doc_id
  rights_record_id
  extractor_name/version/config
  quality/safety/pii signals
  dedup_cluster_id, canonical_doc_id
  filter_decisions[{stage, version, signal, threshold, action, reason}]
  lineage_parents, created_at
```

`doc_id` 应基于 immutable source/version；`content_hash` 用于内容相同判断；二者不要混为一谈。

### 5.2 HTML

- Decode encoding，保留 DOM/block structure。
- 去 nav、cookie banners、ads、footer、related links 等 boilerplate。
- 保留 headings、lists、tables、code blocks、alt text 与 link anchors。
- 识别 main content，但不要把短页面/论坛回答一刀切掉。
- 处理 JS-rendered content 要受资源/安全策略约束；不是每页开 headless browser。
- Parser output 抽样做 visual/text comparison，测 text coverage、boilerplate rate、order correctness。

### 5.3 PDF / scans / OCR

```text
native text extraction first
  → layout blocks / reading order
  → OCR only for image regions or scanned pages
  → tables/math/captions specialized extraction
  → confidence + bounding boxes + page provenance
```

OCR 置信度低、双栏顺序错、页眉页脚重复、公式乱码会产生“看似语言、实则噪声”的 token。按 page/block 保存 confidence，低质量 section 可以 filter 或降权，而不是整篇全留/全删。

### 5.4 Code

- 去 vendored/minified/generated/binary/notebook output。
- 解析 repo structure、language、file type；保留 path/import/test relationships。
- secret/credential scanner 在早期运行；malware/security policies 单独处理。
- fork dedup 要保留 canonical upstream 和 license。
- 可做 file-level、repo-level sequence；训练 FIM 时构造 prefix/suffix/middle，同时保证 split 不跨 repo 泄漏。

### 5.5 Normalization 要保守

可以统一 Unicode、换行和明显 encoding error，但要避免：

- lowercase 破坏代码/实体；
- 全删标点破坏句法/公式；
- 空白压缩破坏 Python/表格；
- language-specific normalization 抹除变音符号；
- 在 dedup 前做过强 normalization 导致不同内容碰撞。

保留 raw → normalized offset mapping，便于审计和引用。

---

## 六、Dedup：exact、near、semantic 分层做 ⭐⭐⭐

### 6.1 为什么 dedup

- 降低 memorization 和 extraction risk。
- 避免模板/热门站在 mixture 中被隐式上采样。
- 节省训练 compute，提高 unique information density。
- 防止 train/test 或 train/validation leakage。
- 让 source/domain 统计更真实。

但 **过度 dedup 也会伤害**：合法重复能表达事实重要性/语言规律；全局跨 snapshot 去重可能删除新版本中有价值的常见文本。FineWeb 的 ablation 显示，dedup 范围/策略本身需要通过训练实验选择，不能凭直觉“越干净越好”。

### 6.2 Exact dedup

1. 规范化文本（定义清晰、versioned）。
2. 计算 SHA-256/BLAKE3 等 hash。
3. 同 hash 组成 cluster。
4. 根据 rights、source authority、时间、extraction quality 选 canonical。

Distributed 实现可用 partitioned hash table / sort；Bloom filter 可做快速 membership，但 false positive 不能静默删除唯一文档，除非设计允许并有 audit。

### 6.3 Near dedup：MinHash + LSH

把 document 变成 word/character shingles 集合 `A`、`B`，Jaccard：

\[
J(A,B)=\frac{|A\cap B|}{|A\cup B|}
\]

MinHash signature 近似 Jaccard，LSH 把相似 signature 放入 candidate buckets，再精确验证。

可在不同 granularity 做：

- paragraph/line：去 repeated boilerplate、copyright/footer；
- document：转载、镜像、版本；
- repository：fork/vendor copies；
- crawl snapshot：同页多次抓取。

参数 trade-off：shingle size、signature length、banding、threshold、document minimum length。阈值不是越高越安全；小段落更容易偶然重合，应分 length bucket 校准。

### 6.4 Semantic dedup

Embedding + ANN/clustering 可发现 paraphrase/翻译/模板改写，但：

- web-scale 成本高；
- 语义相似不等于重复，容易删除独立观点和 minority content；
- embedding model 自身有语言/domain bias；
- cluster threshold 很难全局统一。

实践中用它做高风险 slice（benchmark contamination、synthetic data、known syndicated content）或 candidate generation，保留人工 audit，而不是默认全库删除。

### 6.5 Canonical selection

不要随机保留一份。Score 可考虑：

```text
rights certainty
original vs mirror/repost
publication/update timestamp
parser/OCR quality
source authority
completeness
removal/retention constraints
```

仍要保留 cluster membership 和 dropped-to-canonical mapping；删除请求到来时，canonical 变化可以重建。

### 6.6 Dedup eval

- duplicate precision/recall on human-labeled pairs；
- tokens/docs removed by source/language/domain/length；
- minority language/source survival；
- memorization/extraction rate；
- compute-matched proxy LM loss 与 downstream；
- canonical source correctness；
- train/validation overlap。

只报“去掉了 40% tokens”没有价值，因为不知道删的是 spam 还是稀有知识。

---

## 七、Filtering：规则、分类器、模型评分如何组合 ⭐⭐⭐

### 7.1 Filter funnel

```text
malformed / unsupported MIME
  → language + encoding
  → policy/safety/PII/secrets
  → structural heuristics / repetition / boilerplate
  → spam / quality classifiers
  → domain-specific filters
  → dedup / contamination
  → retain signals for mixture weighting
```

不是所有 signal 都要 hard drop。可分：

- `BLOCK`：权利/安全硬约束。
- `DROP`：高置信垃圾/损坏。
- `DOWNWEIGHT`：低质量但可能有长尾价值。
- `REVIEW/QUARANTINE`：不确定、高风险。
- `KEEP + TAG`：保留并用于 mixture/slice。

### 7.2 Heuristic signals

- document/line length；
- alphabetic/number/punctuation/symbol ratio；
- repeated lines/paragraphs/n-grams；
- average word/sentence length；
- stopword/function-word proportion；
- terminal punctuation；
- HTML/JavaScript residue；
- URL/domain patterns；
- lorem ipsum、SEO keyword stuffing；
- code/text ratio、comment ratio；
- OCR confidence/gibberish。

规则便宜、可解释，但跨语言/domain 不可直接复用。每个阈值做 sweep + human sample + proxy train ablation，不要复制另一个 corpus 的 magic number。

### 7.3 Learned quality classifier

一种常见方法：用高质量 reference（百科、教材、精选文章等）为 positives，随机 web 为 negatives，训练 fastText/small transformer/LLM classifier。

风险：

- classifier 学到 source/style，而不是 knowledge utility；
- “像 Wikipedia”会压制口语、论坛、dialect 和新领域；
- random web negatives 太容易，线上 tail calibration 差；
- 用 LLM 评分会继承其语言/政治/文化偏差；
- threshold 把 continuum 伪装成 truth。

改进：

1. 人工 rubric 区分 coherence、information density、originality、instructional value、factual/support quality。
2. 每个 language/domain 单独 sampling 和 calibration。
3. Hard negatives 加入流畅但错误/SEO/AI-slop；positives 加入真实 forums、minority styles。
4. 输出 calibrated score + uncertainty，很多场景 downweight 比 hard drop 更稳。
5. Human blind audit kept/dropped boundary cases。
6. 以固定 compute proxy LM downstream 作为最终验证。

FineWeb-Edu 和 DCLM 的重要启示不是“LLM classifier 永远最好”，而是：**data filtering decisions 需要以训练后能力做受控实验；model-based quality filtering 可以很强，但必须校准和审计其选择偏差。**

### 7.4 Safety、PII 与 secrets

多层检测：

```text
deterministic regex/checksum (emails, phones, keys, cards)
  + NER/contextual PII model
  + secret scanners / entropy / known key formats
  + source-level policy
  + human red-team test set
```

区分：公开机构电话 vs 私人电话；虚构示例 vs 真实 secret；medical/legal context。可采取 redact、drop document、quarantine、source block。记录 span 和 reason，但检测结果本身也是敏感 metadata，要限权。

PII recall 优先时会有 false positives；按风险类别设置阈值，不用一个 global F1 决定所有处理。训练后还要做 canary/membership/extraction tests，因为过滤器通过不代表不会 memorization。

### 7.5 Bias 与 representational harm

“clean”经常隐含标准书面英语/主流文化。要报告：

- 各语言/dialect/source 的保留率；
- 人口群体相关文本的 false-positive filter rate；
- geographic/domain concentration；
- toxicity/hate 的 context：研究/反驳/引用是否被误删；
- 被删样本的分层 human audit。

安全过滤与能力数据可以做 policy-separated pools，不代表所有研究模型都用同一 mixture。

---

## 八、Benchmark contamination：不能只做 exact string match ⭐⭐⭐

### 8.1 污染类型

| 类型 | 例子 | 检测 |
|---|---|---|
| Exact | benchmark JSON/网页原样出现 | canonical hash、exact lookup |
| Substring / n-gram | 题目/答案段落嵌在文章 | rolling n-gram / suffix array |
| Near duplicate | 格式、变量名、选项顺序变化 | MinHash/SimHash/edit distance |
| Semantic/rephrased | 翻译、paraphrase、解释文 | embeddings + verifier + audit |
| Derived-answer | 教程直接讲解 benchmark 答案 | evidence/entity/solution matcher |
| Synthetic leakage | generator 本身见过 benchmark | generator provenance；private fresh eval |
| Split leakage | 同书/同 repo 相邻样本跨 split | group by source/entity/repo/time |

### 8.2 Decontamination pipeline

```text
benchmark registry (private where needed)
  → normalize benchmark inputs/answers
  → exact + long n-gram scan
  → MinHash/semantic candidate scan
  → task-specific verifier
  → quarantine whole source group when appropriate
  → contamination report per benchmark/version
```

为什么有时要删除整个 document/repo，而不是匹配 span？上下文可能仍包含答案或同源 templates；代码 benchmark 应按 repo/group split，数学题可按 source book/problem family。

### 8.3 不能承诺“零污染”

Paraphrase、翻译、未公开数据源和 synthetic teacher 的记忆使完美检测不现实。正确说法：

- 明确检测覆盖和 false-negative limitations；
- 保留 private/fresh/rolling eval；
- 使用 temporal holdout 和 dynamically generated tasks；
- 报告 contaminated/clean slice；
- 不把 benchmark score 当唯一能力证据。

### 8.4 防止 eval 本身反向泄漏

- Eval registry 与 training catalog 权限分离。
- Private benchmark raw text 不进入普通 data exploration notebook/log。
- Contamination service 返回 match IDs/reason，不一定暴露全套 private answers。
- 新数据版本必须重新扫描全部 active evals。
- Eval prompt、grader examples、post-training data 也要扫；污染不只发生在 pretraining。

---

## 九、Data mixture：token 数量不是 mixture 设计 ⭐⭐⭐

### 9.1 基础 sampling

设 domain/source `i` 有 `n_i` tokens，temperature sampling：

\[
p_i = \frac{n_i^\alpha}{\sum_j n_j^\alpha}
\]

- `α=1`：按原始 token 比例，大 web source 主导。
- `α<1`：上采样小 domain/语言。
- `α→0`：趋向 domain 均匀。

还需要 min floor、max cap、rights/quality gate 和重复 epoch 约束。稀有 language 上采样过高会快速重复和 memorization。

### 9.2 Mixture 设计方法

1. **Expert prior**：按目标能力给初始比例。
2. **Small-scale sweep**：多种 mixture 训练固定 proxy model/tokens。
3. **Per-domain validation loss / target tasks**：看 general 与 target trade-off。
4. **DoReMi / Group DRO**：小 proxy 基于不同 domain excess loss 学权重。
5. **Regression/surrogate**：如 RegMix，用小实验预测 mixture 效果。
6. **Full-scale confirmation**：proxy ranking 未必外推，至少验证 top candidates。

### 9.3 为什么单看 training loss 不够

- 高重复/容易文本 loss 很低，却未必增加能力。
- Code/math token 更难，loss 高不代表应删除。
- 不同 tokenizer 导致 domain token count 不可直接比。
- Target downstream 能力与 average web loss 不一致。

至少联合看：per-domain held-out loss、target capability、general retention、safety/bias、memorization、effective unique tokens。

### 9.4 Mixture 与样本权重

两种方式：

- **Resampling**：按 `p_i` 抽 domain/doc；数据 loader 简单，但会重复小池。
- **Loss weighting**：自然抽样但乘权重；可能有高 variance，distributed batching 更复杂。

实际常层级采样：先 domain/source，再 quality bucket，再 document，最后 sequence；同 source 内设 caps，防一个网站占满 batch。

### 9.5 防止 mixture churn

每个 run 锁定：

```text
source pool versions
mixture config + RNG seed
tokenizer version
sampling algorithm
epoch/repetition counters
shard manifests/checksums
```

运行中 source 到期/删除需要明确 policy：停止并重建、在下一版本生效，还是使用预批准 snapshot；不能 worker 悄悄跳过导致 mixture 漂移。

---

## 十、数据短缺怎么办？面试必答 ⭐⭐⭐

先区分四种“短缺”：

1. **总 token 不够**：compute-optimal 需要更多 unique data。
2. **目标 domain 不够**：例如 OCR signature、medical、rare language。
3. **高质量数据不够**：web 很多但有效信息密度低。
4. **label/rights 不够**：能看到但不能用，或没有 quality labels。

### 10.1 优先级顺序

#### A. 提高已有数据的有效信息密度

- 修 extraction；很多“短缺”其实是 PDF/OCR/parser 丢文本。
- 去模板/重复/AI spam，释放 compute 给 unique content。
- 从 document 选择信息密集 spans，而非把整个低质量页面喂入。
- 优化 mixture，防大 web source 淹没稀有 domain。

#### B. 扩展合法 source

- public-domain、open-license、publisher/vendor license。
- first-party data 在明确 consent/purpose/tenant isolation 下使用。
- 专家/社区合作，针对低资源语言和专业知识创建数据。
- 多模态 source：扫描件 OCR、caption/table extraction，但保留 modality/provenance。

#### C. Synthetic data（谨慎）

适合：

- 结构化知识 → 多种表达；
- 稀有 edge cases；
- code transformations/tests；
- curriculum/examples with verifier；
- 跨语言 translation 作为 augmentation。

质量闭环：

```text
seed from real distribution
  → diverse generator(s)
  → deterministic/domain verifier
  → independent model/human quality audit
  → dedup against seed/eval/train
  → mix at controlled ratio
  → real held-out ablation
```

风险：teacher bias、模式坍塌、错误自我强化、低 lexical diversity、benchmark leakage、synthetic artifacts。保留 `generator/checkpoint/prompt/seed/judge` provenance。

#### D. 有限重复 / multi-epoch

重复优质 data 比加垃圾 data 可能更好，但边际收益下降并增加 memorization。按 source/domain 设 max repeats；shuffle/document packing；用 repeated-token count 和 memorization eval。不要称重复为“增加数据”。

#### E. Curriculum / continued pretraining

- Broad general data 建语言/世界知识。
- 随后提升 high-quality/domain/math/code 比例。
- Long-context phase 用结构连续长文，而非任意拼接。
- Domain continued pretraining 用小 LR、general replay 防 catastrophic forgetting。

Curriculum 并非一定优于静态 mixture；必须 ablation。最后阶段数据对模型行为可能权重更大，但不要依赖未经验证的 recency 直觉。

### 10.2 低资源语言

- Language ID 用 calibrated probability；code-switch 不硬删。
- 小语种 tokenizer fertility、Unicode normalization 单独测。
- upsample + max epoch cap；防同几篇文章反复出现。
- 高资源↔低资源 translation augmentation，保留 original/translated provenance。
- 找本地高质量 source/专家评审，不用英语质量 classifier 一刀切。
- Eval 必须 native-speaker/真实任务，不能只看 translated benchmark。

### 10.3 专业领域（medical/legal/science/code）

- 领域 taxonomy 和 source authority。
- 结构化文档、guidelines、版本/生效日期。
- 专家抽样评价 factuality/coverage，不要求专家标每个 token。
- Domain tokenizer/fertility、formula/code/table preservation。
- Rights/privacy 要求通常更严格；患者/客户 data 默认隔离。
- General replay + domain mixture，测 specialization 与 general regression。

### 10.4 高分总结

> 数据短缺不是立刻“让 LLM 生成更多”。我先量 effective unique tokens 和 capability coverage，修 extraction/dedup/mixture，再扩充有明确权利的一手 source；synthetic data 只用于可验证的缺口，并以真实 held-out ablation 决定比例。有限重复是优化手段，不是新信息。

---

## 十一、Tokenizer 与 sequence construction

### 11.1 Tokenizer 选择

常见 subword：BPE、Unigram；现代系统通常有 byte fallback，避免 `<unk>`。需决定：

- vocab size；
- normalization；
- whitespace/newline 处理；
- special tokens；
- language/code sampling；
- byte fallback；
- reserved tokens for post-training/tools/multimodal。

### 11.2 关键 trade-off

| 选择 | 好处 | 代价 |
|---|---|---|
| 大 vocab | 常见词更短、sequence 少 | embedding/output 参数和 memory 大；长尾 token 学不充分 |
| 小 vocab | 参数省、组合泛化 | sequence 长、训练/推理 FLOPs 上升 |
| English-heavy training | 英语 fertility 好 | 多语言/代码被拆得很碎 |
| Aggressive normalization | 减少表面变体 | 丢代码、实体、语言差异 |
| Byte fallback | 任意字符可编码 | rare scripts 可能 token 很长 |

**Fertility** 可用每词/每字符 token 数表示；按 language、code、math、emoji、OCR noise 分 slice。Tokenizer 本身改变每个 source 的 token mixture，所以 mixture 统计必须在最终 tokenizer 下重算。

### 11.3 Train tokenizer 的数据

- 从目标 mixture 分层采样，而非直接从最大 web pool 随机抽。
- 限制 domain/site 重复，防 tokenizer 记住 boilerplate。
- 包含所有目标 scripts、code whitespace、math symbols。
- 单独 held-out 测 compression/fertility、round-trip、normalization collision。
- Tokenizer 一旦大规模训练开始应锁 version；更换 tokenizer 不是普通 config update。

### 11.4 Packing

目标是减少 padding，提高 GPU utilization：多个 document 拼成 fixed-length sequences。

需要明确：

- document boundary token；
- attention 是否跨文档（通常 causal LM 可跨但可能学习伪关系；可用 mask/position reset，取决实现）；
- 不切断特殊结构/代码文件，或记录 continuation；
- long document chunk overlap 是否制造重复；
- validation packing 与 training 一致但样本独立。

Long-context curriculum 应保留真实结构连续性（书、repo、thread、paper），而不是仅把随机短文 packing 到 128K。

### 11.5 Code FIM

从一个 code file 采 prefix/middle/suffix，序列可为：

```text
<PRE> prefix <SUF> suffix <MID> middle
```

FIM rate、span length、repo/file boundaries 需 ablation。Tests/definitions/import context 可增强，但避免同 repo 跨 train/eval。

---

## 十二、Curriculum 与训练阶段

一种可讨论而不武断的 phase 设计：

| Phase | 数据 | 目的 | 风险 |
|---|---|---|---|
| Broad pretraining | diverse deduped web/books/code/science | language、knowledge、general patterns | web 噪声、大 source 主导 |
| Quality/domain upweight | educational、reasoning、target domains | 提升目标能力 | general forgetting、classifier bias |
| Long-context | long coherent docs/repos/threads | context extension | 数据少、position artifacts |
| Final anneal | carefully curated high-quality mixture, LR→0 | 稳定/目标能力 | 过拟合小池、recency effect 未验证 |

每个 phase 保存独立 data manifest 和 checkpoint；用 matched continuation ablation 比较“改变数据”与“只是多训练了 tokens”。

Continued pretraining 常见防忘记手段：

- 混入 general replay；
- lower LR / shorter schedule；
- domain/general validation loss 共同 early stop；
- downstream retention gates；
- adapter/branch model 若 full-model trade-off 不可接受。

---

## 十三、如何证明 data 有用：scaling、ablation 与 evaluator independence ⭐⭐⭐

### 13.1 Data experiment ladder

```text
static statistics + human samples
  → tiny LM smoke test
  → proxy LM matched-compute ablations
  → scaling across ≥2 model/token scales
  → selected full-scale confirmation
  → downstream/post-training/production validation
```

### 13.2 一次合格的 ablation

要固定：

- architecture、tokenizer、optimizer/schedule；
- total training tokens 和 approximate FLOPs；
- sampling seed（最好多 seed）；
- eval suite/version；
- base raw pool，除被研究变量外其余 pipeline 相同。

例：比较 dedup A/B：

```text
A: global cross-snapshot MinHash dedup
B: per-snapshot MinHash dedup

Both:
  same 1.3B model, 30B train tokens, tokenizer, LR schedule
  when B has fewer unique tokens, define repeat policy explicitly

Report:
  per-domain val loss
  downstream capability
  memorization/extraction
  source/language retention
  processing cost + final unique tokens
```

### 13.3 不要用大模型 judge 替代训练实验

LLM quality scores 很便宜，可做 triage，但它可能偏好自身写作风格。真正 data value 是：在控制其他变量后，训练出来的模型在独立 target distribution 上更好。

Judge 的正确位置：

- 标注边界/active learning；
- 生成多维 quality signals；
- human-calibrated audit；
- 不是最终 ground truth。

### 13.4 Proxy model 外推风险

小模型喜欢的数据不一定让大模型获益：capacity、memorization、emergent tasks 和 optimizer dynamics 不同。做法：

- 至少两个 proxy scales 和 token budgets；
- 看 mixture/filter ranking 是否稳定；
- top candidates 在更大 scale 复验；
- 报 confidence interval/seed variance；
- 不把 0.2% 单 seed 提升写成确定结论。

### 13.5 指标组合

| 维度 | 指标 |
|---|---|
| LM fit | overall + per-domain validation loss/perplexity |
| Target capability | code/math/multilingual/retrieval/domain fresh eval |
| General retention | broad clean held-out suite |
| Data efficiency | quality at fixed tokens/FLOPs；tokens-to-target |
| Memorization | canary exposure、membership/extraction、rare-sequence recall |
| Safety/privacy | PII/secret extraction、toxicity/bias slices |
| Diversity | source/language/topic/entity distribution、effective unique tokens |
| Operations | bytes/tokens retained、CPU/GPU hours、cost/TB、pipeline failure |

### 13.6 Scaling study

在多个 `N, D` 上拟合经验关系，而不是直接套别家公司曲线：

\[
L(N,D) \approx L_\infty + \frac{A}{N^\alpha}+\frac{B}{D^\beta}
\]

Mixture/quality 变化会改变常数和有效数据量。真正决策通常是：固定总训练+未来 inference 成本，选择 `N, D, mixture` 的 Pareto point。

---

## 十四、Distributed data system：trillion-token pipeline 如何可靠运行

### 14.1 Storage layers

```text
raw/        immutable fetched bytes + source metadata
extracted/  structured text/layout + parser versions
signals/    quality/safety/dedup features (可重算)
curated/    keep/drop/downweight decisions + canonical maps
tokenized/  tokenizer-specific sequences
shards/     immutable train-ready files
manifests/  exact membership, order/sampling config, checksums
```

Raw 与 derived 分离。不要覆盖“清洗后的最终 CSV”；每层 immutable/versioned，manifest 指向具体 objects。

### 14.2 Idempotency 与 restart

每个 stage 的 output key：

```text
hash(input content/version + code commit + config + model version)
```

- Worker retry 写同 key；atomic commit manifest。
- Partial shard 放 temporary namespace，成功校验后 publish。
- Checkpoint 按 partition，而非整个 job 只有一个 done flag。
- Dead-letter queue 保留 parse/fetch failures 和 reason。
- Backfill 用新 version，不静默修改旧 object。

### 14.3 Distributed dedup 的难点

- Exact hash 可 partition/sort。
- MinHash/LSH 需要大 shuffle；按 language/length/domain blocking 降 candidate，但会漏跨 block duplicate。
- Connected components 合并 transitive clusters；防 giant boilerplate cluster。
- Canonical selection 需 deterministic tie-breaker。
- Cluster map versioned；后续 deletion 可以找所有 derived records。

### 14.4 Sharding 与 loader

- Shard size 平衡 object-store requests、shuffle granularity、failure recovery。
- 每 shard checksum、doc/token counts、source mix、min/max IDs。
- Loader prefetch、local cache、async I/O；监控 data starvation/GPU idle。
- Deterministic global order 通常代价高；至少 dataset membership、sampling algorithm 和 seeds 可重现统计等价 stream。
- 多 worker 防重复/漏读：global sample IDs + distributed sampler state checkpoint。

### 14.5 Backpressure 与 resource tiers

不同 stage：

- Crawl/network-bound。
- Parse/OCR CPU/GPU mixed。
- MinHash shuffle/memory-heavy。
- LLM quality classifier GPU inference-heavy。
- Tokenization CPU-heavy。

用 queue depth + autoscaling + per-stage quotas；昂贵 learned filter 放在便宜 rule filter 后，避免对必删垃圾跑 GPU。

---

## 十五、Lineage、监控与删除 ⭐⭐⭐

### 15.1 Data lineage 最小字段

```text
dataset_version
source_asset_id + rights_version
raw object pointer + content hash
all transform code/config/model versions
all keep/drop/redact/downweight reason codes
dedup cluster + canonical
tokenizer version
train shard/sample offsets
model run IDs consuming this version
```

Data lineage 不是只为了 debug，也是 rights update、PII incident、benchmark contamination 和 model card 的基础。

### 15.2 Funnel dashboard

每 stage 按 source/language/domain 报：

- docs/bytes/chars/tokens in/out；
- pass/drop/quarantine/redact reason；
- extraction empty/error/OCR confidence；
- exact/near duplicate rate 和 cluster size；
- PII/secret/safety hit rate；
- quality score distribution/threshold；
- tokenizer fertility、sequence length、packing utilization；
- estimated unique tokens、repeat count；
- processing throughput、cost/TB、retry/failure/backlog。

### 15.3 Drift detection

- crawl source/domain mix 变化；
- 新 AI-generated spam/style；
- language ID/quality score shift；
- parser change 导致平均长度突变；
- PII detector hit rate 突变；
- duplicate giant cluster；
- tokenizer fertility/unknown byte spike。

任何大幅变化先抽样 raw/extracted/kept/dropped examples，再决定阈值；不要自动“把分布调回去”，可能现实 web 真变了。

### 15.4 Human audit

每个 release 至少抽：

- uniform kept；
- uniform dropped；
- filter threshold 两侧；
- each language/domain/source；
- high duplicate clusters；
- PII/safety uncertain；
- new/changed domains；
- synthetic data。

记录 annotator rubric、agreement、adjudication。只看 kept data 会漏掉 filter false positives。

### 15.5 Takedown / deletion

```text
verified request / rights expiry / incident
  → resolve source assets + dedup/derived lineage
  → block future acquisition
  → tombstone raw/derived according to policy
  → rebuild affected curated/tokenized manifests
  → mark affected model runs/releases
  → document what can/cannot be removed from already trained weights
```

不要承诺从既有 model weights 中“精准删除”某条训练样本，除非有已验证 unlearning process；数据删除、未来不再训练、模型下架/重训是不同动作。

---

## 十六、Cost model：钱花在哪里、如何降

### 16.1 Funnel 成本公式

设 raw `B_0` bytes，每 stage 保留率 `r_i`，则 stage `j` 输入：

\[
B_j = B_0\prod_{i<j}r_i
\]

所以便宜、高 recall 的 policy/format/language/obvious spam filters 应尽早；昂贵 OCR/LLM classifier/semantic dedup 放后面。但 rights/safety gate 的顺序由 policy 决定，不能为了省钱先非法处理。

### 16.2 主要成本中心

| Stage | 成本 | 优化 |
|---|---|---|
| Crawl/store | bandwidth、object storage、requests | change-aware recrawl、compression、content hash |
| Parse/OCR | CPU/GPU、long-tail files | MIME routing、native text first、page confidence |
| Quality models | inference GPU | cheap prefilter、batching、small distilled classifier、uncertainty routing |
| Dedup | shuffle、RAM、index | blocking、signature compression、incremental clusters |
| Tokenization | CPU、I/O | batched vectorized tokenizer、pretokenized immutable shards |
| Training loader | object-store egress/GPU idle | locality/cache/prefetch、shard sizing |
| Reprocessing | repeated full DAG | immutable layers、content-addressed cache、stage-level versioning |

### 16.3 不能为了 cost 牺牲的东西

- rights/consent enforcement；
- provenance；
- deletion ability；
- held-out eval independence；
- PII/secrets safety gates；
- raw sample audits。

Cost optimization 应画 quality/safety/throughput Pareto，而不是只报 TB/hour。

---

## 十七、端到端例题：构建 search + code foundation model 的 2T-token corpus

### 题目

> 你有固定预算，想训练一个 7B 模型，擅长 web research、technical papers 和 code。设计 2T-token pretraining data system。

### 17.1 需求假设（先声明，可调整）

- 主要英文，但覆盖主要编程语言和部分多语言 technical content。
- 商用；source 必须通过 rights policy。
- 后续还会做 search-agent post-training，所以 pretraining 不需要伪装成指令数据。
- 训练能力：technical language、code理解、long documents、source/citation structure。
- 2T 是训练 token exposure，不等于 2T unique tokens；必须报告 repeats。

### 17.2 Source pools（比例只是实验起点，不是答案）

```text
high-quality filtered web       40%
licensed/public books/docs      15%
scientific/technical papers     15%
permissively licensed code      20%
forums/Q&A/issues               5%
multilingual technical text     5%
```

为什么不直接说这是最终比例？要用 proxy mixture sweep/DoReMi-like study，在 search/code/technical target eval 和 general retention 上选择。比例在最终 tokenizer 下按 tokens 计算。

### 17.3 Pipeline

1. Source rights registry；raw immutable crawl/vendor snapshots。
2. HTML/PDF/code specialized extraction，保留 headings、citations、repo graph。
3. Language/PII/secrets/safety + structural heuristics。
4. Learned quality 分维度打分，按 domain 校准；多为 weighting，不全 hard drop。
5. Exact → paragraph boilerplate → MinHash document/repo/cross-source dedup。
6. 扫 code/math/search eval registry，按 repo/document group quarantine。
7. Tokenizer 在 stratified source sample 上训练，测 language/code/math fertility。
8. Mixture sampler 有 floors/caps/repeat limit；long-context phase 采 coherent papers/repos/docs。
9. Pretokenized versioned shards + full lineage。

### 17.4 Experiments

第一轮小模型：

- web filter thresholds 3 档；
- code 10/20/30%；
- paper/doc 10/20%；
- dedup per-snapshot vs global；
- synthetic technical explanation 0/5/10%。

用 fractional factorial / surrogate 降低组合爆炸；top mixtures 在第二个 scale/seed 验证。

### 17.5 Eval

- Per-domain held-out loss：fresh web、papers、docs、code、multilingual。
- Clean private tasks：technical QA、paper comprehension、code completion/repair、rare entity retrieval language modeling。
- General benchmark + temporal/private variants。
- Memorization/extraction、license attribution/code copying audit、PII/secret canaries。
- Data pipeline：unique tokens、repeat exposure、source entropy、cost/TB、GPU loader utilization。

### 17.6 高分结尾

> 2T 是曝光预算，不是质量目标。我会把 raw rights、dedup cluster、filter signal、tokenizer 和 train sequence 串成可追踪 lineage；比例只是 prior，由 matched-compute proxy runs 和独立 fresh eval 选择。对 code 和 scientific data，我宁愿保留结构与 provenance 并限制许可范围，也不把它们 flatten 成无法审计的纯文本池。

---

## 十八、面试题与答题 walkthrough

### Q1：你从哪里获取 pretraining data？

不要只列 source。按 portfolio 回答：web 提供规模/长尾；licensed/public-domain books/docs 和 papers 提供结构化长文；permissive code 提供程序知识；first-party/专家数据补目标分布；synthetic 补可验证缺口。每类都有 rights record、provenance、quality/safety pipeline 和 mixture cap。

### Q2：如何定义“高质量数据”？

不是一个 universal score。拆成 coherence、information density、originality、factual/support quality、target utility、rights/safety。Heuristic/learned score 是 proxy；最终通过固定 compute 的训练 ablation，在独立 target/general/safety eval 上验证。

### Q3：Quality classifier 如何构造 labels？

Human rubric + 多样 positive/negative sources；hard negatives 包括流畅 spam/AI-slop，positives 不限百科风格；按语言/domain 分层，双标/仲裁；classifier calibration + threshold boundary audit；输出 score/uncertainty，很多场景 downweight。最后用 proxy LM ablation 验证。

### Q4：为什么 dedup 能提高模型？

提高 unique information per FLOP、减少热门模板隐式上采样和 memorization/泄漏。但过度 dedup 可删掉有意义重复/长尾；exact、near、semantic 分层，保留 canonical/provenance，并用 compute-matched ablation 选择 scope/threshold。

### Q5：MinHash 怎么工作？

文档转 n-gram/shingle set，Jaccard 表示重叠；多个随机 hash 的最小值组成 signature，其相等概率近似 Jaccard；LSH banding 找候选，随后精确检查。说清它是 candidate approximation，不是 semantic equivalence。

### Q6：如何避免 train/test contamination？

Eval registry → exact/long n-gram → MinHash/semantic candidates → task-specific verification；按 document/repo/entity/time group 删除；每个新 dataset version 重扫；保留 private rolling temporal eval；报告检测覆盖，不能宣称完全无污染。

### Q7：如何处理 PII？

Source policy + deterministic patterns/checksums + contextual NER/model + secret scanners + human red-team；按风险 redact/drop/quarantine；记录 lineage 方便删除；训练后做 extraction/membership/canary eval。具体 legal basis 与 retention 由 counsel/privacy policy 定义。

### Q8：数据 mixture 怎么定？

Expert prior 建初始范围；temperature/floor/cap 控制；固定 architecture/tokens/compute 做 proxy mixture sweep，观察 per-domain loss、目标能力、general retention、安全与 memorization；可用 DoReMi/RegMix 类方法；跨两个 scale 验证 proxy ranking；最后锁 manifest。

### Q9：为什么不能把每个 domain 均匀采样？

Domain 规模、质量、目标价值和重复风险不同。极小 domain 均匀采样会反复曝光、memorization；巨大 web domain 原比例又会淹没其他能力。用目标驱动权重、repeat caps 与 ablation。

### Q10：数据不足怎么办？

先判断 unique tokens、domain coverage、rights 还是质量短缺；修 extraction/dedup/mixture；扩合法 first-party/licensed/低资源 source；synthetic 只补可验证 gap；有限重复设 cap 并测 memorization；continued pretraining 加 general replay。不要直接说“GPT-4 生成”。

### Q11：Synthetic pretraining data 的风险是什么？

Teacher bias/error、低多样性、model collapse、风格 artifact、benchmark leakage、权利/provenance 不清。用真实 seed、多 generators、deterministic/independent verification、dedup、controlled ratio、真实 held-out ablation，并记录 generator lineage。

### Q12：Tokenizer 多大？

没有固定答案。大 vocab 缩短 sequence 但增 embedding/output 参数、rare token 学不够；小 vocab 序列更长。按最终 source mixture train candidates，测各语言/code/math fertility、compression、downstream 与 end-to-end train/inference cost，再选 Pareto point。

### Q13：为什么 tokenizer 会改变 mixture？

Mixture 常按 tokens 计；同样字符在不同语言/domain 的 fertility 不同。English-optimized tokenizer 会让小语种占更多 tokens/compute。因此 source proportions 必须在最终 tokenizer 下重算，并按字符/文档和 token exposure 双重审计。

### Q14：如何构建 long-context pretraining data？

优先 coherent long units：书章节、论文、repo、thread、manual；保留结构和顺序；过滤重复 headers/OCR；合理 chunk/continuation；packing 与 attention boundary 明确；按 length/position 做 eval。随机短文拼 128K 只提高 utilization，不等于训练 long-range dependency。

### Q15：Proxy model 的结果能否直接外推？

不能保证。至少多个 model/token scales、seed，看 data strategy 排名稳定；top candidates full-scale confirmation。报告 uncertainty，不把单个小模型 0.x% 当真理。

### Q16：如何监控 pipeline？

Funnel 按 source/language/domain 看 bytes/docs/tokens、filter reasons、duplicate cluster、PII、quality score、fertility、packing、throughput/cost。对 kept/dropped/threshold/new source 分层 human sample；distribution shift 触发调查而不是自动调阈值。

### Q17：如何支持删除请求？

Source asset 和 rights registry → raw/derived lineage → dedup cluster → curated/tokenized manifests → model run usage。Block future crawl，tombstone/rebuild future dataset，记录受影响模型。明确已训练 weights 的删除不能等同于删文件，需 policy 决定重训/下架/unlearning。

### Q18：如何比较两个 filters？

先比较 retention/failure slices 与 human precision/recall，再用同 raw pool、同模型/tokenizer/tokens/FLOPs/schedule 的 proxy runs；报告 per-domain loss、target/general eval、memorization/bias、processing cost。若 retained token 数不同，明说 repeat/fill policy。

### Q19：训练 loss 降了是否说明新数据更好？

不一定。新数据可能更容易/重复，loss 低但能力没增。要看 clean per-domain held-out、target downstream、unique information、memorization、安全，以及 fixed-compute quality。

### Q20：为什么保存 raw data？

Parser/filter bugs 可重跑；审计原始来源；rights/删除解析；新 extractor 不必重新 crawl。但 raw 可能最敏感，需严格 access、encryption、retention 和 purpose policy；并不是无限期保留。

### Q21：如何处理新一轮 web crawl？

作为 versioned snapshot ingest；URL/content hash 与历史比对；new/changed/deleted 分流；增量 quality/dedup cluster；重新 contamination/rights checks；比较 source/quality drift；发布新 manifests，不覆盖旧 dataset。

### Q22：如何防止 AI-generated web 污染下一代模型？

无法完美检测。组合 source/time provenance、known generator/watermark、stylometry/classifier、duplicate/template clusters、domain reputation；降低 uncertain synthetic pool 权重；保留人类/可信一手 source；用 diversity/novelty/closed-loop degradation eval。不要把 detector 当 truth。

### Q23：如果某 source 提升目标 benchmark 但增加 memorization，怎么办？

这是多目标 trade-off，不能只看 score。先检查 contamination/重复；减少 repeat/near duplicates、降权或只保留独特部分；看 private/fresh task 是否仍提升；设 memorization/privacy hard gate。若提升依赖泄漏，不能算能力收益。

### Q24：v1 最小可行 data pipeline？

Approved sources → immutable raw → robust extract → language/format/safety/PII → exact + MinHash dedup → simple quality score/weight → benchmark n-gram scan → stratified mixture → tokenizer/shards/manifests。先用 300M–1B proxy model 做 3–5 个 high-value ablations，再扩系统，不先建 semantic dedup/复杂 optimizer。

---

## 十九、十五分钟白板答题模板

| 分钟 | 讲什么 | 必须落下的产出 |
|---|---|---|
| 0–2 | 目标能力、N/D/compute、rights/safety | data contract |
| 2–4 | source portfolio | source × value × risk |
| 4–7 | pipeline | raw→extract→filter→dedup→tokenize→shards |
| 7–9 | shortage/mixture | floors/caps/repeats/synthetic verifier |
| 9–11 | tokenizer/packing/curriculum | final-token mixture + coherent long context |
| 11–13 | ablation/eval | fixed compute + proxy scales + private/fresh eval |
| 13–15 | lineage/cost/failures | manifests、deletion、monitoring、trade-offs |

万能结尾：

> v1 的目标不是最大 token count，而是在固定 compute 下最大化经过权利和安全约束的有效信息。每个 filter 和 mixture decision 都先以 proxy 衡量，再由独立 real held-out tasks 证实；每个 train shard 都能追溯到 source、rights、transform、tokenizer 和 run。最大的风险是 quality proxy、benchmark leakage 与 source bias，所以我保留 temporal/private eval、dropped-data audit 和可执行 deletion lineage。

---

## 二十、面试前一页速记

### Funnel 默写

```text
rights + sources
→ immutable raw
→ parse/OCR/structure
→ language/safety/PII/secrets
→ heuristics + learned quality signals
→ exact/near/semantic dedup
→ benchmark decontamination
→ mixture/curriculum
→ tokenizer/packing/shards
→ proxy ablation/full train
→ lineage/monitor/delete
```

### 必背 12 句

1. 公开可访问不是一个足够的数据许可字段；rights 必须逐 source/version 可执行。
2. Raw immutable 让 parser/filter 可重跑，但 retention/access 仍受 privacy policy 约束。
3. Quality score 是 proxy；数据价值由 fixed-compute 训练后的独立 eval 决定。
4. Dedup 提高 unique information density，但过度 dedup 会伤害长尾与多样性。
5. Uncertain data 可 downweight/quarantine，不必所有 signal 都 hard filter。
6. Mixture 在最终 tokenizer 下按 token 重算；fertility 会改变语言/domain compute。
7. Synthetic data 只补可验证缺口，并保留 generator/judge provenance。
8. 重复训练优质文本可能有效，但重复不是新数据，且增加 memorization。
9. Benchmark exact decontamination 不足以发现 paraphrase/derived-answer leakage。
10. Proxy model 只用于筛选；至少跨 scale/seed 检查 ranking 稳定。
11. 每个 shard 都需要 manifest、checksum、source mix、tokenizer 和 lineage。
12. 删除原数据、未来不再训练、从已训练权重移除，是三件不同的事。

### 必背公式

```text
Training compute: C ≈ 6 N D
Jaccard:         |A ∩ B| / |A ∪ B|
Temp sampling:   p_i = n_i^α / Σ n_j^α
Scaling sketch:  L ≈ L∞ + A/N^a + B/D^b
Stage bytes:     B_j = B_0 Π_{i<j} r_i
```

### 绝不能说

- “Common Crawl 是公开的，所以可以直接用于任何商业训练。”
- “Wikipedia-like classifier 分数就是数据质量。”
- “去重越多越好。”
- “benchmark 没 exact match，所以不存在 contamination。”
- “缺数据就让当前模型生成更多。”
- “训练 loss 更低证明数据更好。”
- “把多份文档拼到 128K 就学会 long context。”
- “删掉训练文件就从模型里删除了该数据。”

---

## 二十一、延伸阅读（按面试价值排序）

1. [FineWeb paper](https://arxiv.org/abs/2406.17557) 与 [FineWeb processing write-up](https://huggingfacefw-blogpost-fineweb-v1.static.hf.space/index.html)：96 个 Common Crawl snapshots、filter/dedup ablation、FineWeb-Edu。
2. [DataComp-LM](https://proceedings.neurips.cc/paper_files/paper/2024/hash/19e4ea30dded58259665db375885e412-Abstract-Datasets_and_Benchmarks_Track.html)：固定训练/eval 框架比较 filter、mixture 与 data design。
3. [Dolma](https://aclanthology.org/2024.acl-long.840/) 与 [Dolma toolkit](https://allenai.github.io/dolma/)：open corpus、可复现 curation pipeline 与数据文档。
4. [The Llama 3 Herd of Models](https://arxiv.org/abs/2407.21783)：大规模 pretraining data filtering、mixture、tokenizer、scaling 的系统案例。
5. [DoReMi](https://arxiv.org/abs/2305.10429)：用 proxy model + group DRO 优化 domain mixture。
6. [Training Compute-Optimal Large Language Models](https://arxiv.org/abs/2203.15556)：参数、tokens 与固定 compute 的联合规划。
7. [The Stack](https://arxiv.org/abs/2211.15533) 与 [BigCode data governance](https://www.bigcode-project.org/docs/about/the-stack/)：permissive code、provenance、near dedup、opt-out/removal。
8. [ROOTS](https://arxiv.org/abs/2303.03915)：多语言 composite corpus 与 governance/documentation。
9. [RedPajama-V2](https://github.com/togethercomputer/RedPajama-Data)：raw artifacts、quality signals 与 dedup 分离的开放实现。

阅读方法：对每篇只回答六个问题——raw pool 是什么、rights/provenance 如何记录、filter/dedup 具体做了什么、用什么 proxy 选方案、下游怎么评、作者承认什么 limitation。不要只背最终 token 数。
