# 13 · 公司速记卡（面试前 5 分钟看这张）

⏱ 每张卡 90 秒读完 ｜ 只看你今天要面的那一家

**置信度标注**：`【一手】` = 官方博客/JD 原文可引用；`【面经】` = 1p3a/论坛实录，带日期；`【推断】` = 我的推理，面试里不要说成事实。

---

## Exa 【进行中 · 第一轮已过 · 第二轮 systems design】

**是什么**：为 AI 而不是为人做的 web search（自称 "the search engine for AIs"）。$250M Series C @ $2.2B（2026-05，a16z 领投），总融资 $361M。产品是给 agent 用的 retrieval API，不是十条蓝链接。

### 🔴 当前进度（2026-07-29）

| 轮次 | 状态 | 内容 |
|---|---|---|
| 第一轮技术（45 min live coding） | ✅ **2026-07-28 已过** | **流式分位数**：给 stream 返回任意 percentile。全排序 → 压缩空间 → 分桶 → 误差容忍 → **log 分桶**。（不是 ML 题，是工程判断题） |
| 第二轮技术（45 min） | 📅 **待约** | recruiter 原话："a more **team specific** question, that is often **systems design**"。面试官 **Joshua Yurtsever**（ML researcher，前 Google） |
| leadership | 之后 | |
| 终轮 | 之后 | **2 天 in-person paid work trial**（fully AI-enabled） |

**面试官方向（LinkedIn 自述）**："Building **production retrieval and post-training systems** for LLM-powered **agentic search**, including **reranking**, **snippet generation**, and **model alignment**"

👉 **第二轮主备考文件：[20_case_exa_agentic_search.md](20_case_exa_agentic_search.md)** —— 全栈一手事实卡 + 四道最可能的 design 题的完整答案 + 延迟/算力算术。
👉 recruiter 主动给了读物：[exa.ai/blog/webcode](https://exa.ai/blog/webcode)（coding agent 的搜索评测集）。

### 【一手】可以直接引用的技术事实（来自 [exa.ai/research](https://exa.ai/research)）

- 自己**预训练 + 微调** embedding 模型，不是接现成的。为 **code search 单独微调**过一版。
- 用 **Matryoshka representation learning**：训练时强制前缀也是好 embedding，2048 维截到 **256 维，内存降 20×**。
- Exa 2.0 在 **144×H200 集群上训了一个多月**。
- 自建 **web-scale 向量数据库**（不是买的）。
- 自称有「**从网页挖 embedding 训练数据的新方法**」——高精度网页搜索需要海量训练数据，这是他们的护城河说法。

### 【一手】评测方法论（[evals-at-exa](https://exa.ai/blog/evals-at-exa)，Exa 面试前必读）

他们叫 **open evals**：query set 打**任意** index，不要求固定文档语料和预标注相关性。

| 维度 | 他们的做法 |
|---|---|
| 三种打分 | ① pure result grading：LLM 给 (query, result) 打 0–1 ② RAG grading：用 SimpleQA 测搜索对 QA 的增益 ③ query set 对比 |
| Query 集 | 5,000 条真实去标识 Exa query + 10,000 条 MS Marco + 约 500 条手工构造的 **"Exa Olympiad"** 难题 |
| Judge | GPT-4.1，五个维度（query relevance / result quality / content issues / confidence / overall 0.0–1.0） |
| Judge 校准 | 与人类偏好一致率：**easy 97%，hard/ambiguous 83%** |
| 聚合 | pointwise / pairwise(ELO) / listwise 都试过，**默认 pointwise**，尽管承认 pairwise 理论上更优 |

**他们为什么明确拒绝 MS Marco 式封闭评测**（四个理由，全部可以在面试里复述）：
1. 稀疏标注导致**假负例**；
2. 50 文档量级的语料**预测不了十亿级**表现；
3. query 分布偏向 **2020 年前的 Bing** 搜索；
4. 知识密集型 query 的标注成本**不可行**。

他们也说：自动评测之外仍要人工抽检，手动看常发现自动系统看不到的问题。

### 【一手】2026 年新增的技术事实（第二轮必备，详见 [20](20_case_exa_agentic_search.md) §2）

| 层 | 关键数字 |
|---|---|
| 向量库 | **10 万 cluster** · 4096→**256 维**（Matryoshka 20×）· **二值量化**（16×）· query 保 fp 的**非对称打分** · SIMD 查表（计算 1/4）· **<100ms / >500 QPS**，比云向量库便宜 **10×** |
| BM25 | **1.8TB / 十亿文档 → 砍半**；WAND 动态剪枝；delta+变长编码（4B→1.3B）+ zstd；意外地延迟**还降 10%**（缓存局部性） |
| 数据框架 exa-d | **Lance on S3** + Ray Data；核心原语是「只重写单个 fragment 的单个 column」；backfill 与增量更新**同一条码路** |
| 编排 Canon | 搜索管线 = **DAG，20+ 种 node**；**pull-based** + 级联取消 + memoize；**typestate + totality** 类型安全（明说是为「代码现在多数由 agent 写」设计的） |
| **Highlights** | **<100ms、每请求都跑、不缓存**；**500 字符 ≈ 整页前 8000 字符的准确率（token 少 16×）**；长文档 coding eval 上 **60% vs 6%**；是 /answer、Deep、Websets 的共同底座 |
| **RL / alignment** | Qwen3-4B + LoRA **r32** + **Dr. GRPO**，100 步；Exa vs SERP：达同等水平**少 69% token、少 62% search call**；结果直接含答案 **36.1% vs 32.6%** |
| WebCode | **discriminative 而非 generative**（问「上下文里有没有答案」）；端到端任务**只用 2025-08-01 之后发布的库**抗污染 |

### 对口材料与接话点

- **第二轮（systems design）主文件：[20_case_exa_agentic_search.md](20_case_exa_agentic_search.md)**
- 训练侧弹药 [06_search_post_training.md](06_search_post_training.md)：§四（训练数据从哪来）、§五（click ≠ positive）、§六（hard negative 的坑）、§九（四层 eval）
- **最强接话**：他们拒绝 MS Marco 的第一个理由（稀疏标注造成假负例）和 hard negative mining 的核心陷阱（top-k 里混着未标注的相关文档，直接当负例会伤召回）**是同一个问题的两面**。把这两件事连起来讲，说明你真读过他们的博客且理解检索训练。
- 第二强接话：Matryoshka 是**成本工程**不只是模型技巧——256 维粗筛 + 全维精排是天然的级联，正好接 [08](08_evaluation_production.md) 的 cascade 和 cost/success。
- 可能被问：「怎么给一个新垂类（比如 code search）造 embedding 训练数据」→ 06 §四 的锚文本/链接上下文/title-body/合成 query（doc2query）四类来源。

---

## OpenAI · Pretraining

**要害**：这是四家里**唯一你完全没做过**的方向，知识补全优先级最高。Day 2 上午整块给它。

### 【面经】1p3a 实录真题（数据轴，全部收录在 [09 §H](09_question_bank.md)）

| 题 | 轮次 | 日期 | 为什么对口 |
|---|---|---|---|
| **Mining Novel Data from Large Unlabeled Corpus** | onsite MLSD | 2026-05-26 | 从海量无标注语料挖新信息 + 定位含特定物体的图像。**这题同时是 pretraining data 和感知数据采集的合体** |
| **Classifier Noisy Annotators** | tech screen（9 帖，高频） | 2026-05-26 | 多标注员噪声标签下训分类器 |
| Data Labeling Task Scheduler | phone/onsite coding | 2026-05-31 | 标注调度，两问，第二问要求每个前缀都满足公平约束 |
| Rag Search Ml Design | onsite MLSD | 2026-03-22 | 检索设计 |

### 必背（[07](07_pretraining_data.md) §二十）

- Funnel 十一步默写；`C ≈ 6ND`；Chinchilla ~20 tokens/param；温度采样 `p_i = n_i^α / Σ n_j^α`
- 三个题眼：quality classifier 的**正样本从哪来**、污染**不能只做 exact match**、数据价值**只能由固定算力的训练 ablation 证明**（不是 quality score，不是 training loss）
- 「绝不能说」8 条务必看一遍，那是最容易踩的雷

### 对口材料

[07_pretraining_data.md](07_pretraining_data.md) 全篇 + §十八 24 问自测 ｜ 想动手：[`cs336/assignment4-data`](../../cs336/assignment4-data/) 就是这条 funnel 的可跑作业

---

## Mirendil

**是什么**：ex-Anthropic 的 Behnam Neyshabur、Harsh Mehta 于 2025-12 创立的 frontier lab，$200M seed @ $1B 估值（a16z + Kleiner Perkins 领投，NVIDIA 跟投），约 20 人，使命是「让 AI 自主做 AI 研究」。（此前的详细调研目录已不在仓库中）

**你的状态**：take-home（Chat Trace Viewer）已于 2026-07-19 交付。你申请的两个岗 = **Agent Harness MTS** + **Post-Training RL**。

**【推断】若进 ML design 轮**，最可能考 RL 环境与训练信号，而不是经典 MLSD：
- 怎么给一个新任务域构建 RL 环境（task sourcing → verifier → reward → 防 hacking）
- trajectory 数据从哪来、怎么筛
- reward hacking 的检测与防御

对口：[03](03_model_training_reward.md) §5–§7（post-training 升级顺序、reward provenance、防 hacking）+ [04](04_case_code_review_llm.md) §7–§8（可验证信号的具体造法）+ [`../agentic_prep/agentic2/03_gaps/agentic_rl.md`](../agentic_prep/agentic2/03_gaps/agentic_rl.md)

**你的天然优势**：trace viewer take-home 本身就是 eval/observability 工具，和「怎么知道 agent 在 reward hack」是同一条线，可以自然引用。

---

## Bridgewater

**【面经】流程**：recruiter 电话（行为 + 文化）→ 在线 coding（标准算法题）→ onsite 三轮：**technical / Life Interview / system design**。

**Bridgewater 的两个特殊点**：
1. **Life Interview** 是其他公司没有的——考价值观与自我认知（radical transparency 文化）。不是技术轮，但会挂人。
2. 评估维度是显式命名的：**Structuring、Synthesis、Tolerance for Ambiguity**。他们明说不是找「算法背得最好的人」，而是看你**怎么拆问题**。这对 MLSD 是好消息：[01](01_answer_framework.md) 的框架化答题正中靶心。

**【一手】ML Research Engineer JD 要点**：量化背景（ML / 统计 / **实验设计**）、构建 ML 训练与推理管线、**回归问题**为主（不是分类）、**因果推断**加分、C/C++ 加分。

### 金融时序的数据轴特殊性（本目录其他文件没覆盖，这里补齐）

这是 Bridgewater 与另外三家最大的区别——同一套框架，但每个格子的答案不一样：

| 问题 | 通用 ML 的答法 | 金融时序必须改成 |
|---|---|---|
| Split | entity + time | **只能** chronological，且要 **purge + embargo**：训练集尾部和测试集头部之间挖掉一段，否则重叠持有期造成泄漏 |
| 泄漏 | 未来信息进入特征 | **look-ahead bias** + **point-in-time 数据**：财报会被事后修订，必须用「当时可见的版本」而不是今天数据库里的值 |
| 样本量 | 行数 | 行数是**幻觉**。日频 20 年 ≈ 5000 行但独立事件远少于此；高频采样不增加独立信息，只增加自相关 |
| 分布漂移 | drift 监控 | **regime shift** 是常态不是异常（利率环境、政策、危机）；模型必须按 regime 分层评估 |
| 信噪比 | 通常可学 | 极低。**多重检验**是头号敌人：试一百个信号总有几个"显著"→ 必须 pre-register、留 holdout 期、报 deflated Sharpe |
| 幸存者偏差 | 少见 | 退市公司、清算基金默认不在数据库里 |
| 评估 | AUC / F1 | 回归题看 IC（信息系数）、命中率、**风险调整后收益**；且要看**交易成本后**是否还在 |

**高分句**：在金融数据上，我的默认假设是「任何漂亮的回测都先当作泄漏或过拟合，直到证明不是」——所以我会先做 point-in-time 重建和 purged 时序切分，再谈模型。

对口：[02](02_data_and_labels.md) §4（split）与 §7（行为日志偏差，思路可迁移）+ [08](08_evaluation_production.md) §9（drift）

---

## Decagon（及 Sierra / Intercom Fin / Ada 等 AI 客服赛道）

**是什么**：企业 AI 客服 agent 平台。2023 年由 **Jesse Zhang（CEO）+ Ashwin Sreenivas（CTO）** 创立；2026-01 完成 $250M 融资，估值**翻三倍到 $4.5B**（Coatue + Index 领投，a16z / Accel / Bain Capital Ventures 跟投），累计融资超 $500M。100+ 企业客户，公开可查的包括 Notion、Duolingo、Substack、Rippling、Bilt、Hertz、ClassPass。2025 年扩张到旅游酒店、金融服务、健康、电商四个垂类。Jesse Zhang 公开把 Salesforce 当主要对手。

### 【一手】Agent Operating Procedures（AOP）——他们的差异化，面试大概率会聊

- **要解决的问题**：传统客服机器人用**决策树穷举**所有分支，面对现实中含糊、不完整的客户表述会崩掉；而纯 prompt 又不够可靠。
- **做法**：混合指令集——**业务规则用自然语言**写（CX 团队自己维护，不用排队等工程），**敏感动作的校验用代码**（退款、身份验证走代码级 gate）。业务侧和技术侧并行推进。
- **他们的说法**：迭代周期从「季度」压到「天」。

**最强接话**：AOP 本质上是把 [01 · 答题框架](01_answer_framework.md) 里那条「模型提出、确定性代码授权」的分工做成了产品。可以说：

> 自然语言适合表达「什么情况下该怎么办」，但它不能承担授权。所以政策用自然语言让业务方维护，每个有副作用的动作必须落到代码校验和额度上限——**语言层可以出错，授权层不能**。追问「自然语言规则怎么防冲突和回归」就答：规则版本化 + 每条绑定对话级回归用例，把 prompt 工程变成有 CI 的软件工程。

### 【一手】他们自己就在强调的指标区分

Decagon 的 glossary 明确区分 deflection / containment / resolution，并且直说**containment 高不一定好**。这是这个赛道的头号题眼——**面试里主动拆开这三个词，比报任何数字都有用**。

他们自报客户平均 deflection 约 80%；公开案例从 Rippling「deflection 提升 32%」到 Substack「90% resolution」。第三方汇总普遍认为厂商宣传与实际部署有 30–40 个百分点差距——**主动指出口径差异**（精选案例 vs 跨项目汇总、deflection vs resolution），是加分项。

### 对口材料

- 主文件 **[14 · AI 客服 agent](14_case_customer_service_agent.md)**（数据轴：resolution 的标签怎么造、多租户冷启动、AOP、reward hacking 三例）
- runtime 侧看 [`agentic2`](../agentic_prep/agentic2/README.md)：Sierra 卡、τ-bench/τ²-bench、pass^k、[A1 客服 take-home 完整解答](../agentic_prep/agentic2/05_questions/solutions/A1_customer_agent_takehome.md)、[A2 退订流程](../agentic_prep/agentic2/05_questions/solutions/A2_subscription_cancellation.md)
- 你的 Reflection 经验里 **eval / grader 共建**那条线在这里极其对口：客服最难的就是 resolution 没有免费标签，而你做过「把主观质量变成可自动计算的 grader 并用人工校准」——这正是 §3 那套阶梯。

### 【推断】可能的面试形态

多租户冷启动（新客户零对话数据怎么上线）、resolution 怎么度量、写操作的授权边界、成本从哪里降。写操作（退款/取消）是这个赛道的分水岭——把错误从「说错话」变成「造成财务损失」，答题时务必主动区分只读和可写。

---

## 五家共用的收尾

不管哪家，最后 60 秒都用 [10_cheatsheet.md](10_cheatsheet.md) 的结尾模板：V1 用冻结 holdout + 便宜 baseline 验证信号 → 生产用校准 cascade → shadow→canary 同时 gate 业务指标/关键 slice/p95/cost per success → 「最大未知是 ___，下一步用 ___ 对照实验决定」。

没做过该 vertical 时的诚实句式见 [12_personal_bridge.md](12_personal_bridge.md) §3——**不要把设计方案说成历史结果**。
