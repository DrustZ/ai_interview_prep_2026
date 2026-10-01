# 通用 ML 理论 + ML System Design 资源库

> 由 raw/build_question_bank.py 从爬取数据自动生成（2026-07 抓取）。每条含来源 URL 可回查原文。

## 流程与情报

### 2026 年 AI labs/高薪公司面试大盘（ExperiencedDevs 讨论）：店面要求 100% 全对、多段实践题取代单题 leetcode、Python 速度成硬约束
*unknown · 频率: high-engagement discussion (corroborates 10+ threads) · 2026-06*

r/ExperiencedDevs 2026-06 高质量讨论帖（7YoE 双 FAANG，刚挂 Anthropic/Databricks）：(1) >$400-500K 岗位现在要求店面每部分（含'optional'）全对，'差一个 edge case 就挂'，代码必须可运行且输出正确、零容错——归因于裁员潮候选人过剩+AI 作弊泛滥；(2) 趋势：从单题 leetcode 转向 5 段渐进 practical 多部分题（各大 lab 一致），必须秒出解+零 debug 才能写完；(3) 用 Java 做多段 OA 是自杀（类型样板太多），Python 是速度刚需；(4) referral 只保面试不保 offer；networking/跟人跳槽才是 senior+ 的真实通道。与 Anthropic/OpenAI 各 thread 的观察完全一致。

来源: <https://www.reddit.com/r/ExperiencedDevs/comments/1uky9ws/2026_interview_experience/>

### deep-ml.com 站点结构、题库分类与难度体系（爬取总览）
*unknown · 频率: 平台题库结构（1127 题，抓取日期 2026-07） · 2026-07*

deep-ml.com 是一个专注 ML 的开源刷题平台（类比 LeetCode 但全是 ML 题），题目在浏览器内用 Pyodide 跑 Python 评测。抓取自 sitemap.xml：站点共有约 1127 道 problems（/problems/{id}，id 连续到 1132）、34 个 labs（/labs/{id}，真实数据集项目）、articles、collections、learn（学习路径）、contests、leaderboard、jobs、premium、interview-prep。每题有难度标签，取值为 easy / medium / hard（页面 meta 描述里明确写 'a easy/medium/hard <Category> coding challenge'）。按类别统计（对全部 1127 题的 SSR meta 解析）：Deep Learning 278、Machine Learning 255、Reinforcement Learning 192、NLP 71、Linear Algebra 50、Computer Vision 32、pytorch 30、tinygrad 30、sql 26、Probability 17、Statistics 14、Optimization 14、MLOps 14、Inference 12、Data Structures 12、Algorithms 11、triton 10、LLM 9、Calculus 9，另有少量 Information Theory / Game Theory / Financial ML 等。官方对外宣传的主类别是 Linear Algebra、Machine Learning、Deep Learning、NLP、Computer Vision（见 llms.txt）。约 164 题在开源仓库 github.com/Open-Deep-ML/DML-OpenProblem 有完整题干+solution.py+learn.md+tests，其余高编号新题目前只有站点上题干。每题 URL 形如 https://www.deep-ml.com/problems/107 。

**解法**: 抓取旁路：站点是 Next.js 客户端渲染，题库列表走受保护的 Firestore，但每个 /problems/{id} 页面的 <meta name=description> 做了 SSR，含 '标题 + 难度 + 类别'，可批量 curl 全部 id 解析。robots.txt 显式欢迎 GPTBot/ClaudeBot 并提供 https://www.deep-ml.com/llms.txt 与 llms-full.txt。sitemap: https://www.deep-ml.com/sitemap.xml

来源: <https://www.deep-ml.com/problems>

### Interview Prep 页面（/interview-prep）内容与运作方式
*unknown · 频率: 官方功能页（lastmod 2026-06-21） · 2026-06*

页面标题 'Interview Prep: Company-Specific ML Interview Preparation'。定位：'Pick a company, choose a role, and train for it.' 每个公司 track 提供：(1) 该公司面试流程与轮次说明；(2) 该公司筛选简历时看重的 resume projects（对应站点 Labs/Projects）；(3) 限时 mock interview（timed mock interviews）；(4) 按 readiness 追踪的分阶段学习计划（paced study plan，从 2 周到 3 个月）。页面从 Firestore 'companies' 集合动态加载公司卡片（含 company_name、logo、role_count / roles），并把用户进度存到 'user_interview_prep' 集合。公司 track 页面 URL 形如 /interview-prep/{slug}（如 /interview-prep/openai、/interview-prep/anthropic、/interview-prep/google-deepmind、/interview-prep/google、/interview-prep/meta 均返回 200）。注意：具体公司列表、轮次文案、mock 题目均由登录+受保护的 Firestore 驱动，未登录时抓不到明细（见 source_summary）。

**解法**: 公司 track 具体题单/轮次需登录；但站点用公开的 Collections 承载各公司 interview-prep 题单（见下条），可作为等价替代来源。

来源: <https://www.deep-ml.com/interview-prep>

### 公司专属 Interview Prep 合集（Collections）——含 OpenAI / Anthropic / DeepMind
*mixed · 频率: 3 家目标公司均有专属合集 · 2026-07*

deep-ml 的 /collections 里有专门的公司面试合集（每个合集是一组精选题目+徽章）。与候选人目标直接相关的有：
- OpenAI Research Scientist Interview Prep → https://www.deep-ml.com/collections/OpenAI%20Research%20Scientist%20Interview%20Prep
- Anthropic Interview Prep → https://www.deep-ml.com/collections/Anthropic%20Interview%20Prep
- DeepMind Interview Prep → https://www.deep-ml.com/collections/DeepMind%20Interview%20Prep
- MLE Interview Prep → https://www.deep-ml.com/collections/MLE%20Interview%20Prep
- Data Science I Interview Prep → https://www.deep-ml.com/collections/Data%20Science%20I%20Interview%20Prep
每个合集页 SSR meta 为 'Complete the "X" collection on Deep-ML. Practice curated machine learning problems and earn your badge.' 合集内的具体题目清单由受保护的 Firestore 'collections' 集合加载（未登录 403），无法从 HTML 直接抓到成员题 id。合集完整列表见 sitemap.xml。

**解法**: 合集成员题 id 抓不到（Firestore 权限拒绝）。但根据合集主题，OpenAI/Anthropic/DeepMind 合集几乎必然由下面列出的 attention/transformer、optimizer、loss、sampling、RLHF/GRPO/DPO、KV-cache 类题目构成——可按下列 topic 题单自行覆盖。

来源: <https://www.deep-ml.com/collections>

### 与 LLM/post-training 相关的主题学习路径（Collections / learn）
*mixed · 频率: 官方主题合集 · 2026-07*

从 sitemap 抓到的、与 LLM post-training / agentic / 深度学习强相关的主题合集（学习路径），可作为分主题刷题的 curriculum：
- Attention Is All You Need；Attention in Transformers: From Queries to Multi-Head；Inside a Transformer: Embeddings, Attention, and Softmax；How LLMs Work: From Next-Token Prediction to Transformers
- Build GPT from Scratch: Karpathy Walkthrough；GPT-2 to gpt-oss；Karpathy makemore 系列（Bigram / MLP Part 2 / Activations,Gradients&BatchNorm / WaveNet Part5 / Backprop Ninja）；Micrograd Builder；Karpathy's Micrograd
- Deconstructing GRPO: From RAFT to Reinforce-Rej；Fine-Tuning LMs from Human Preferences；Reinforcement Learning: An Introduction（Sutton&Barto 对应题）
- DeepSeek R1；DeepSeek's Multi-Head Latent Attention Explained；DeepSeek-V4；Llama 3；SPARSELY GATED MoE
- optimizers；Muon Optimizer: From Motivation to NumPy Implementation
- Inference Engineering；VLLM；Quantization Basics: Why, When, and How；LLM Evaluation Methods
- PyTorch Basics；Tinygrad Essentials；Triton Essentials
合集 URL 形如 https://www.deep-ml.com/collections/optimizers （名称含空格需 URL 编码）。学习路径入口 https://www.deep-ml.com/learn 。

**解法**: 这些合集是把下方 topic 题单按论文/课程重新编排；候选人 post-training 背景优先做：Deconstructing GRPO、Fine-Tuning LMs from Human Preferences、Inference Engineering、Muon Optimizer、Attention 系列。

来源: <https://www.deep-ml.com/collections>

### Hack2Hire 题库结构与旁路抓取说明（供后续复用）
*unknown · 频率: n/a · 2026-07*

站点结构：公司页路径 /question-bank/companies/{company}/{coding-questions|system-design|ml-system-design|sql-questions|object-oriented-design|interview-resources}。有效 company slug 含 openai、anthropic、google（DeepMind 无独立数据，deepmind/google-deepmind 页面为空壳，实际归 google）。题目详情正文对未登录用户 isLocked=true 只给预览，但每题的 AI insights（quickSummary、whatThisTests、commonPatterns、hints、likelyInterviewFollowUps）、难度、stages(OA/SCREENING/ONSITE)、各公司频率(1-10)、首发/最近报告日期均在 Next.js SSR flight 数据中公开可取。System Design/ML-SD 正文与代码模板需登录，仅标题/元数据可得。后端 API：https://api.hack2hire.com/algro/v1（如 GET /company-directory 列全部公司；GET /post/filter?companyTags={ENUM}&page=1&perPage=999 列某公司全部题，companyTags 用大写枚举如 OPENAI/ANTHROPIC/GOOGLE）。/coding/{id} 详情需 SSR key（401），故详情走 practice 页 SSR。

**解法**: 抓取法：curl practice 页 → 提取 self.__next_f.push 里的 flight 字符串 → unicode_escape 解码 → 取 codingQuestionSsrResponse 平衡括号 JSON（含 description 预览 + insights）。Blog 正文在 flight 的 'NN:T{hexlen},' 文本块里。

来源: <https://www.hack2hire.com/question-bank>

### Mimansa Jaiswal《LLM (ML) Job Interviews - Resources》：面试资源与流程索引页
*unknown · 频率: unknown · 2025*

研究者整理的 LLM/ML 求职资源索引（题库、公司流程、准备清单的元列表），可作为继续深挖 OpenAI/Anthropic/GDM 各家 RS/RE 流程信息的入口。本次任务主要用其定位题库来源；页面本身无具体题目。

来源: <https://mimansajaiswal.github.io/posts/llm-ml-job-interviews-resources/>

### Yuan Meng 'MLE Interview 2.0': frontier-lab round taxonomy (LLM coding, ML infra design, research talk)
*unknown · 频率: first-person + aggregated · 2026-01*

First-person 2025-2026 loop taxonomy: frontier labs (OpenAI, Anthropic, DeepMind, xAI) add non-standard rounds — multi-level OOP (Time-Based KV Store, In-Memory Database, Circuit Breaker w/ rate limiting, LRU/LFU cache, Thread Pool/Task Scheduler; signal = thread safety + production thinking); LLM coding (implement Transformer encoder/decoder, LoRA, KV cache, beam search, autograd internals — 'even daily PyTorch users rarely know how computation graphs are built'); ML infra design (feature stores, distributed training, checkpointing, continuous retraining, serving: feature fetching, latency reduction, caching, logging); research presentation (job-talk style, ~10 slides defending technical work); project deep dives. ML model design framework: problem framing → high-level online/offline paths → retrieval → L1/L2 ranking → deep dives (scaling, cold start, positional bias, diversity). Company notes: OpenAI/Roblox/Databricks/Notion demand OOP excellence; Google random-hard LC; Meta AI-assisted coding round. Prep advice: only start after screens confirm the loop; NeetCode 250, UDL book ch.1-9+11-12, PyTorch-in-one-hour, Deep-ML.com.

来源: <https://www.yuan-meng.com/posts/mle_interviews_2.0/>

### Curated resource maps for frontier-lab MLE/RS prep (Mimansa Jaiswal; Evidently AI case-study DB)
*unknown · 频率: n/a (meta-resources) · 2025*

Mimansa Jaiswal's post-interview resource list (built while interviewing for LLM/ML roles): MLSD via Educative Grokking-ML free section; LLM internals via Transformer Family v2 (Lilian Weng), Transformer Math 101 (EleutherAI), JAX scaling book (jax-ml.github.io/scaling-book — TPU/GPU parallelism for training/inference); RLHF via Chip Huyen RLHF post + HF 'N implementation details of RLHF with PPO' + '37 PPO implementation details' + GRPO guide (yugeten); inference/decoding via Chip Huyen sampling post; retrieval via yuan-meng EBR/LTR/negative-sampling posts + Weaviate RAG eval; ML coding via alirezadir notebooks, Hands-On-LLMs, deep-ml.com — noting interviews asked FNN/LSTM/RNN from scratch and cached/grouped/multi-head attention implementations; her design-round opener pattern: offer discriminative vs generative paths and let interviewer choose. Evidently AI database: 800 real ML/LLM system design case studies from 150+ companies, filterable by industry/use-case (https://www.evidentlyai.com/ml-system-design) — best source of real-world grounding examples to cite in SD answers.

来源: <https://mimansajaiswal.github.io/posts/llm-ml-job-interviews-resources/>

### Sundeep Teki《AI Research Engineer Interview Guide: OpenAI, Anthropic, DeepMind (2026)》要点
*hard · 频率: 聚合指南 · 2026*

三家对比：OpenAI——4-6 小时 onsite（1-2 天），端到端 6-8 周，流程去中心化可同时考虑多岗位，“明显更偏 coding 而非 research”，含 coding/system design/ML debugging/research discussion/behavioral；Anthropic——平均 ~20 天，90 分钟 CodeSignal 需 100% 正确才能进入下一轮，面试周期内做严格 reference check，重 FAANG 式 system design + AI 研究答辩 + 伦理口试；GDM——录取率 <1%，含 rapid-fire quiz 考本科级基础，“像 PhD 答辩混合严格工程考试”，资深工程师也常挂 quiz。通用题型：Transformer 是“AI 面试的 Hello World”——手写 Multi-Head Attention、完整 Transformer layer、NN+训练循环 from scratch、不用 sklearn 写 K-means、纯 Python 算 AUC；ML Debugging 轮格式：“给一个能跑但不学习的 notebook”，典型 bug：broadcast 错误、softmax 维度错、CrossEntropyLoss 前重复 softmax、忘 zero_grad、dataloader shuffle 问题；ML system design 标准题：“How would you train a 100B+ parameter model?”（必须讲 data/pipeline/tensor 三种并行及硬件约束下的选择）；推理优化：KV caching、INT8/FP8 量化 trade-off、speculative decoding（2-3x 加速）；RAG 全架构；research discussion：提前 2-3 天给论文，讨论贡献/方法/结果/局限/扩展。行为面红旗：lone wolf、傲慢、只想发财。

来源: <https://www.sundeepteki.org/advice/the-ultimate-ai-research-engineer-interview-guide-cracking-openai-anthropic-google-deepmind-top-ai-labs>

### letsdatascience 三大 lab 招聘流程与进入策略（含 GDM 7-9 轮结构）
*unknown · 频率: 聚合指南 · 2025~2026*

GDM：7-9 轮、4-6 周——recruiter screen → 1-3 轮 LC 式 coding → ML theory（Transformers、finetuning 方法、大模型训练、Gemini/DeepSeek 等新架构）→ research discussion（详细走查自己的技术工作）→ team fit。RS 必须 PhD+顶会发表；RE 无发表硬性要求（Gordic 案例）。OpenAI：6 阶段（简历→recruiter 30min→coding 60min→project review 60min→system design 60min→onsite 4-6h），4-6 周；system design 重实际 ML infra：real-time feature stores、red-teaming pipelines、大规模部署；40 万+年申请量；Residency 项目面向数学/物理/神经科学转行者。Anthropic：6 阶段（recruiter→90min CodeSignal→HM deep dive→onsite 4h 4-6 轮：coding/system design/ML theory/AI safety reasoning→team matching 2-4 周→reference+offer），3-8 周；~50% technical staff 无 PhD；safety 认同必须真实。跨 lab：内推者拿 offer 概率 ~7x（Pinpoint 450 万申请数据）；给出 6-12 个月建立 visible work→社区参与→内推的路线图。

来源: <https://letsdatascience.com/blog/how-to-land-a-job-at-openai-anthropic-or-google-deepmind>

## Coding 题

### Google OA/Coding: Maximize Coins Collection (token 每次右移3格, 完整题干)
*medium · 频率: single report · 2025-11*

岗位: Google 2026 SWE Online Assessment (通过 1p3a interview OJ API 取到完整公开题干, tid 1157978)。题目: 给一个一维棋盘字符串(长度<=100), 字符为 '.'(空)、'T'(玩家 token)、'C'(硬币)。玩家可移动多个 token, 每个 token 每步严格向右移动 3 格, 不能左移也不能移动其他步数; 若目标格被另一 token 占用则该移动非法。硬币只有在 token 落在其上时才被收集(路过不算)。求最多能收集多少硬币。样例输入: '...TC.TC.' / 'TT.CCCC.T' / 'C..T..C..TT..' / '....T...T...C' / 'TTT.'。虽为通用 Google OA, 但可能出现在 GDM RE coding 轮。

**解法**: 解法: 每个格子按 index mod 3 分成 3 条独立链(因每步 +3, token 只在同余类内移动)。在每条链上把格子重排为一维序列, 问题变为: 若干 token 沿链向右逐格移动(不可越过/占用同格), 每落点若是 C 则 +1, 最大化收集数。链内用 DP/贪心处理 token 与 coin 的匹配(注意占用冲突: 两 token 不能同格, 靠右 token 先动或按顺序 DP)。总复杂度 O(n)。

来源: <https://www.1point3acres.com/interview/thread/1158159>

## ML Coding 题

### [重点] 归一化层题清单（LayerNorm/RMSNorm/BatchNorm，17 题）
*mixed (easy→hard) · 频率: 归一化是高频基础题；RMSNorm 各家变体（Gemma/Cohere）2026 新增多 · 2026-07*

#908 LayerNorm from Scratch [easy] https://www.deep-ml.com/problems/908 | #929 Tinygrad: LayerNorm from Scratch [easy] https://www.deep-ml.com/problems/929 | #372 RMSNorm (Root Mean Square LN) [easy] https://www.deep-ml.com/problems/372 | #1046 Zero-Initialized RMSNorm with (1+w) Scaling [easy] https://www.deep-ml.com/problems/1046 | #1047 Gemma-Style RMSNorm with Optional Scale [easy] https://www.deep-ml.com/problems/1047 | #1038 Gemma-Style RMSNorm with Zero-Centered Scale [easy] https://www.deep-ml.com/problems/1038 | #1039 Bias-less Cohere LayerNorm [easy] https://www.deep-ml.com/problems/1039 | #1042 Bias-less LayerNorm with Float32 Compute [easy] https://www.deep-ml.com/problems/1042 | #109 Layer Normalization for Sequence Data [medium] https://www.deep-ml.com/problems/109 | #684 Adaptive Layer Normalization for Conditional Generation [medium] https://www.deep-ml.com/problems/684 | #128 Dynamic Tanh: Normalization-Free Transformer Activation [easy] https://www.deep-ml.com/problems/128 | #115 Batch Normalization for BCHW Input [medium] https://www.deep-ml.com/problems/115 | #902 BatchNorm2d from Scratch (training mode) [medium] https://www.deep-ml.com/problems/902 | #923 Tinygrad: BatchNorm2d (Training Mode) [medium] https://www.deep-ml.com/problems/923 | #1003 BatchNorm1d Forward with Bessel's Correction [easy] https://www.deep-ml.com/problems/1003 | #1005 BatchNorm1d Supporting 2D and 3D Inputs [medium] https://www.deep-ml.com/problems/1005 | #1002 Fused Backward Pass of BatchNorm1d [hard] https://www.deep-ml.com/problems/1002

**解法**: #372 RMSNorm：x*w/sqrt(mean(x²)+eps)，无均值中心化、无 bias（对比 LayerNorm 要减均值）。#1002 BatchNorm 反向是经典手推题，需对 γ、β、x 分别求梯度（含 1/N Σ 项）——推断为面试常考手推 backprop。

来源: <https://www.deep-ml.com/problems/372>

### [重点] 损失函数题清单（CE/Focal/DPO/对比学习等，28 题）
*mixed (easy→hard) · 频率: CE 系列高频；post-training 相关的 masked CE / DPO loss 是重点 · 2026-07*

#263 Binary Cross-Entropy [easy] https://www.deep-ml.com/problems/263 | #134 Multi-class Cross-Entropy [easy] https://www.deep-ml.com/problems/134 | #914 Numerically Stable Cross-Entropy (pytorch) [medium] https://www.deep-ml.com/problems/914 | #935 Tinygrad: Numerically Stable CE [medium] https://www.deep-ml.com/problems/935 | #220 Derivative of Cross-Entropy Loss w.r.t. Logits [medium] https://www.deep-ml.com/problems/220 | #205 Entropy & Cross-Entropy [medium] https://www.deep-ml.com/problems/205 | #194 Label Smoothing for Multi-Class CE [medium] https://www.deep-ml.com/problems/194 | #795 Masked Cross-Entropy Loss for SFT [medium] https://www.deep-ml.com/problems/795 | #1066 Mask Instruction Tokens for Loss Computation [medium] https://www.deep-ml.com/problems/1066 | #1067 Masked Log-Probability for Sequence Tokens [medium] https://www.deep-ml.com/problems/1067 | #192 Huber Loss [medium] https://www.deep-ml.com/problems/192 | #255 Focal Loss for Imbalanced Classification [medium] https://www.deep-ml.com/problems/255 | #915 Implement Focal Loss (pytorch) [medium] https://www.deep-ml.com/problems/915 | #936 Tinygrad: Focal Loss [medium] https://www.deep-ml.com/problems/936 | #283 Hinge Loss for SVM [easy] https://www.deep-ml.com/problems/283 | #813 Epsilon-Insensitive Loss for SVM Regression [medium] https://www.deep-ml.com/problems/813 | #837 Hamming Loss for Multilabel [medium] https://www.deep-ml.com/problems/837 | #43 Ridge Regression Loss [easy] https://www.deep-ml.com/problems/43 | #227 Knowledge Distillation Loss [medium] https://www.deep-ml.com/problems/227 | #384 Contrastive Loss (InfoNCE / SimCLR) [medium] https://www.deep-ml.com/problems/384 | #387 Triplet Margin Loss [medium] https://www.deep-ml.com/problems/387 | #916 Implement Triplet Loss (pytorch) [easy] https://www.deep-ml.com/problems/916 | #937 Tinygrad: Triplet Loss [easy] https://www.deep-ml.com/problems/937 | #393 VAE Loss (ELBO) [medium] https://www.deep-ml.com/problems/393 | #400 Noise Prediction Loss for Diffusion [medium] https://www.deep-ml.com/problems/400 | #685 Heteroscedastic Laplace NLL Loss [medium] https://www.deep-ml.com/problems/685 | #769 DPO Loss with NLL Regularization [medium] https://www.deep-ml.com/problems/769 | #997 Manual Backprop Through Cross-Entropy Intermediates [hard] https://www.deep-ml.com/problems/997

**解法**: #914 数值稳定 CE：用 log-sum-exp，logsoftmax=x-max-log(Σexp(x-max))，再 gather 目标类。#795/#1066 SFT masked loss：只在 response（label≠-100）token 上算 CE，prompt/instruction token 置 ignore。#220 CE 对 logits 的梯度=softmax(logits)-onehot(y)（经典简洁结论）。

来源: <https://www.deep-ml.com/problems/134>

### ML/LLM coding questions reported across frontier-lab and AI-company loops (same 2026 compendium)
*medium · 频率: high (multiple submissions per assignment reported) · 2026*

ML coding asked from memory: implement multi-head attention; implement a full Transformer layer; implement LoRA adapter from scratch; implement beam search, top-k, top-p decoding; autoregressive generation with top-p sampling; logistic regression with SGD + L2 + early stopping in NumPy; Transformer bug-fixing exercise (position embedding and KV-cache bugs). Knowledge rapid-fire: KV cache, GQA vs MHA, BPE/WordPiece/char tokenization, encoder-only/decoder-only/enc-dec, why decoder-only dominates, positional encoding, FlashAttention, why LLM inference is memory-bound, context-window overflow behavior, RLHF pipeline (SFT → reward model → PPO) and how DPO simplifies it, PEFT/LoRA/QLoRA, 'How would you design a model that can solve math problems?' (data collection → SFT → post-training → evaluation), 'Design a language model that minimizes harmful outputs while remaining useful.' Take-homes reported: production RAG chatbot (100+ concurrent users, <2s latency, citations), LangGraph workflow engine (graph nodes, state, branching/looping, max 50 steps, unit tests mandatory), LLM-judge bedtime-story pipeline (Spec Builder → Storyteller → Judge → Rewriter, gpt-3.5-turbo, ≤2 revision cycles), hallucination-detection eval tool, multi-agent content system (5 agents).

来源: <https://adilshamim8.medium.com/every-ai-engineer-interview-question-you-need-to-know-in-2026-from-100-real-interviews-b5b7ae4b961a>

### [重点] Attention / Transformer 实现题全清单（38 题）
*mixed (easy→hard) · 频率: 该主题题量最大，是平台核心；建议 #53→#490→#107→#94→#391/#390→#405→#208 递进 · 2026-07*

deep-ml 上 attention/transformer 实现相关题（题名[难度] URL）：
#53 Implement Self-Attention Mechanism [medium] https://www.deep-ml.com/problems/53 | #490 Build Scaled Dot-Product Attention [medium] https://www.deep-ml.com/problems/490 | #963 Scale Attention Scores by sqrt(d_k) [easy] https://www.deep-ml.com/problems/963 | #962 Compare Naive vs Stable Softmax for Attention Scores [easy] https://www.deep-ml.com/problems/962 | #955 Simple Self-Attention Without Trainable Weights [easy] https://www.deep-ml.com/problems/955 | #956 Apply Dropout to Attention Weights [easy] https://www.deep-ml.com/problems/956 | #965 Construct Causal Attention Mask via tril and triu [easy] https://www.deep-ml.com/problems/965 | #957 Implement Batched Causal Self-Attention [medium] https://www.deep-ml.com/problems/957 | #107 Implement Masked Self-Attention [medium] https://www.deep-ml.com/problems/107 | #94 Implement Multi-Head Attention [hard] https://www.deep-ml.com/problems/94 | #904 Implement Multi-Head Self-Attention (pytorch) [hard] https://www.deep-ml.com/problems/904 | #925 Tinygrad: Multi-Head Self-Attention [hard] https://www.deep-ml.com/problems/925 | #958 Multi-Head Attention via Head Stacking [medium] https://www.deep-ml.com/problems/958 | #959 Multi-Head Attention with Combined QKV Weight Matrix [medium] https://www.deep-ml.com/problems/959 | #960 Multi-Head Attention Using Einsum [hard] https://www.deep-ml.com/problems/960 | #966 Batched Attention Score Computation for Multiple Heads [medium] https://www.deep-ml.com/problems/966 | #964 Transfer Weights Linear-Style to Parameter-Style Self-Attention [medium] https://www.deep-ml.com/problems/964 | #491 Build a Transformer Encoder Layer [hard] https://www.deep-ml.com/problems/491 | #905 Implement a Transformer Encoder Block (pytorch) [medium] https://www.deep-ml.com/problems/905 | #926 Tinygrad: Transformer Encoder Block [medium] https://www.deep-ml.com/problems/926 | #388 Sliding Window Attention [medium] https://www.deep-ml.com/problems/388 | #131 Efficient Sparse Window Attention [medium] https://www.deep-ml.com/problems/131 | #271 Implement Gated Attention [medium] https://www.deep-ml.com/problems/271 | #390 Implement Multiquery Attention (MQA) [medium] https://www.deep-ml.com/problems/390 | #391 Implement Grouped Query Attention (GQA) [medium] https://www.deep-ml.com/problems/391 | #405 Multi-Head Latent Attention (MLA) [hard] https://www.deep-ml.com/problems/405 | #406 NoPE with iRoPE Attention [hard] https://www.deep-ml.com/problems/406 | #1017 Gated DeltaNet Linear Attention [hard] https://www.deep-ml.com/problems/1017 | #177 MuonClip (qk-clip) for Stabilizing Attention [medium] https://www.deep-ml.com/problems/177 | #208 Flash Attention v1 - Forward Pass [hard] https://www.deep-ml.com/problems/208 | #492 PagedAttention: Block-wise Attention [hard] https://www.deep-ml.com/problems/492 | #448 Context Parallelism with Ring Attention [hard] https://www.deep-ml.com/problems/448 | #1020 Cross-Layer KV Sharing in Transformer [hard] https://www.deep-ml.com/problems/1020 | #1040 Parallel Transformer Block Forward Pass [medium] https://www.deep-ml.com/problems/1040 | #1043 Parallel Attention and FFN Transformer Block [medium] https://www.deep-ml.com/problems/1043 | #1056 Pre-Norm GPT Transformer Block Forward Pass [hard] https://www.deep-ml.com/problems/1056 | #697 Frame-wise Causal Attention Masking for Video [medium] https://www.deep-ml.com/problems/697 | #700 Spatiotemporal Transformer Block [hard] https://www.deep-ml.com/problems/700 | #773 Cross-Document Attention Mask Construction [medium] https://www.deep-ml.com/problems/773

**解法**: #53 自注意力标准解：Q=XW_q,K=XW_k,V=XW_v；scores=QKᵀ/√d_k；softmax 后乘 V（返回 numpy）。#107 masked：在 softmax 前对未来位置加 -inf 掩码（因果）。#94 MHA：把 d_model 拆成 h 个 d_k，逐头做 scaled dot-product 再 concat 过 W_o。#391 GQA/#390 MQA：K/V 头数 < Q 头数，多组 Q 共享同一组 KV（省 KV cache）。以上为我依据题干+标准 transformer 推断的解法思路。

来源: <https://www.deep-ml.com/problems/53>

### [重点] 位置编码 / RoPE 题清单（13 题）
*mixed (easy→hard) · 频率: RoPE 变体多，2025-2026 新题密集（Llama/YaRN/Partial/NoPE） · 2026-07*

#906 Sinusoidal Positional Encoding [easy] https://www.deep-ml.com/problems/906 | #927 Tinygrad: Sinusoidal Positional Encoding [easy] https://www.deep-ml.com/problems/927 | #85 Positional Encoding Calculator [hard] https://www.deep-ml.com/problems/85 | #375 Learned Positional Embeddings [easy] https://www.deep-ml.com/problems/375 | #946 Add Positional Embeddings to Token Embeddings [easy] https://www.deep-ml.com/problems/946 | #381 Rotary Positional Embeddings (RoPE) [medium] https://www.deep-ml.com/problems/381 | #1045 Partial Rotary Position Embedding (Partial RoPE) [medium] https://www.deep-ml.com/problems/1045 | #1048 Proportional RoPE Inverse Frequencies with NoPE Tail [medium] https://www.deep-ml.com/problems/1048 | #1024 Llama 3.1 RoPE Frequency Rescaling [hard] https://www.deep-ml.com/problems/1024 | #1025 Llama 3 RoPE Frequency Scaling [hard] https://www.deep-ml.com/problems/1025 | #1037 YaRN RoPE Frequency Scaling [medium] https://www.deep-ml.com/problems/1037 | #1029 RoPE with Position Offset for KV Cache [medium] https://www.deep-ml.com/problems/1029 | #406 NoPE with iRoPE Attention [hard] https://www.deep-ml.com/problems/406

**解法**: #381 RoPE 标准解：inv_freq=1/(base^(2i/d))，对每个位置 m 构造角度 mθ，把 Q/K 相邻维两两组成复数做旋转（或用 [-x2,x1] 的 rotate_half 技巧）。#1037 YaRN / #1024 Llama3.1 是对 inv_freq 按波长分段插值/外推缩放，用于长上下文扩展——推断解法。

来源: <https://www.deep-ml.com/problems/381>

### 激活函数题清单（10 题）
*easy (仅 #98 medium) · 频率: 入门基础，热身用 · 2026-07*

#42 ReLU [easy] https://www.deep-ml.com/problems/42 | #44 Leaky ReLU [easy] https://www.deep-ml.com/problems/44 | #23 Softmax Activation [easy] https://www.deep-ml.com/problems/23 | #39 Log Softmax [easy] https://www.deep-ml.com/problems/39 | #102 Swish [easy] https://www.deep-ml.com/problems/102 | #103 SELU [easy] https://www.deep-ml.com/problems/103 | #100 Softsign [easy] https://www.deep-ml.com/problems/100 | #147 GeLU [easy] https://www.deep-ml.com/problems/147 | #373 Square ReLU [easy] https://www.deep-ml.com/problems/373 | #98 PReLU Forward and Backward Pass [medium] https://www.deep-ml.com/problems/98

**解法**: #147 GeLU：0.5x(1+erf(x/√2))，或 tanh 近似 0.5x(1+tanh(√(2/π)(x+0.044715x³)))。#23 Softmax 注意减 max 数值稳定。

来源: <https://www.deep-ml.com/problems/147>

### [重点] 优化器题清单（Adam/AdamW/Muon 等，15 题）
*mixed (easy→medium) · 频率: Adam 有两题(#49/#87)；Muon 系列(#170/#172/#740/#1054)是 2025-2026 热点 · 2026-07*

#146 Momentum Optimizer [easy] https://www.deep-ml.com/problems/146 | #150 Nesterov Accelerated Gradient [easy] https://www.deep-ml.com/problems/150 | #145 Adagrad [easy] https://www.deep-ml.com/problems/145 | #148 Adamax [easy] https://www.deep-ml.com/problems/148 | #149 Adadelta [medium] https://www.deep-ml.com/problems/149 | #49 Implement Adam Optimization Algorithm [medium] https://www.deep-ml.com/problems/49 | #87 Adam Optimizer [medium] https://www.deep-ml.com/problems/87 | #200 RMSProp Optimizer [medium] https://www.deep-ml.com/problems/200 | #169 AdamW Optimizer Step [medium] https://www.deep-ml.com/problems/169 | #170 Muon Optimizer Step with Matrix Preconditioning [medium] https://www.deep-ml.com/problems/170 | #172 Muon Optimizer Update with Newton-Schulz Iteration [medium] https://www.deep-ml.com/problems/172 | #740 RMS-Matched Update Rescaling for Orthogonalized Optimizers [easy] https://www.deep-ml.com/problems/740 | #1054 Partition Parameters for Muon vs AdamW [easy] https://www.deep-ml.com/problems/1054 | #886 Run One Training Step: Forward/Loss/Backward/Optimizer (pytorch) [easy] https://www.deep-ml.com/problems/886 | #895 Run One Tinygrad Training Step [easy] https://www.deep-ml.com/problems/895

**解法**: #49 Adam：m=β1 m+(1-β1)g；v=β2 v+(1-β2)g²；bias-correct m̂=m/(1-β1ᵗ), v̂=v/(1-β2ᵗ)；x-=lr·m̂/(√v̂+eps)。默认 lr=1e-3,β1=0.9,β2=0.999。#169 AdamW 把权重衰减从梯度里解耦，直接对参数乘(1-lr·wd)。#172 Muon：对动量矩阵做 Newton-Schulz 迭代近似正交化再更新——推断解法。

来源: <https://www.deep-ml.com/problems/49>

### [重点] 采样 / 解码题清单（temperature/top-p/beam/speculative，15 题）
*mixed (easy→hard) · 频率: LLM 推理核心；#419 三合一 pipeline 是综合 hard 题 · 2026-07*

#1070 Greedy Autoregressive Text Generation [easy] https://www.deep-ml.com/problems/1070 | #378 Temperature Sampling [medium] https://www.deep-ml.com/problems/378 | #383 Top-p (Nucleus) Sampling [medium] https://www.deep-ml.com/problems/383 | #419 Combined Token Sampling Pipeline (Temperature + Top-k + Top-p) [hard] https://www.deep-ml.com/problems/419 | #433 Speculative Decoding Acceptance Rate vs Temperature [medium] https://www.deep-ml.com/problems/433 | #496 Beam Search with Memory-Efficient Block Sharing [hard] https://www.deep-ml.com/problems/496 | #385 Beam Search Decoding [medium] https://www.deep-ml.com/problems/385 | #1055 Greedy Streaming Decoder with KV Cache [medium] https://www.deep-ml.com/problems/1055 | #1082 Autoregressive Token Generation with Block-Size Context Cropping [medium] https://www.deep-ml.com/problems/1082 | #984 Sample Names from a Bigram Language Model [medium] https://www.deep-ml.com/problems/984 | #991 Sample from MLP Character Language Model [medium] https://www.deep-ml.com/problems/991 | #768 Rejection Sampling Best-of-K Selection [easy] https://www.deep-ml.com/problems/768 | #508 Quality Filtering with Rejection Sampling [easy] https://www.deep-ml.com/problems/508 | #696 Logit-Normal Sampling for Diffusion Timesteps [easy] https://www.deep-ml.com/problems/696 | #686 Euler Sampling for Rectified Flow Models [medium] https://www.deep-ml.com/problems/686

**解法**: #378 temperature：logits/=T 后 softmax（T→0 趋近 greedy，T大更均匀）。#383 top-p：按概率降序累加，保留累计到 p 的最小集合，重新归一化再采样。#419：顺序应用 temperature→top-k 截断→top-p 截断→归一化采样。#433 speculative decoding：draft 模型提议、target 模型按 min(1, p_target/p_draft) 接受——推断解法。

来源: <https://www.deep-ml.com/problems/383>

### [重点] Tokenization / BPE / embedding 题清单（17 题）
*mixed (easy→medium) · 频率: BPE 被拆成 6+ 小题(#948-#952/#380)，适合系统练；对 mid-training 数据管线背景很对口 · 2026-07*

#374 Character-Level Tokenizer (stoi/itos/BOS) [easy] https://www.deep-ml.com/problems/374 | #940 Regex-Based Text Tokenizer [easy] https://www.deep-ml.com/problems/940 | #941 Build Vocabulary from Token List [easy] https://www.deep-ml.com/problems/941 | #942 Simple Word Tokenizer Encode and Decode [easy] https://www.deep-ml.com/problems/942 | #943 Tokenizer with Unknown and End-of-Text Tokens [easy] https://www.deep-ml.com/problems/943 | #953 Calculate Vocabulary Size from Token List [easy] https://www.deep-ml.com/problems/953 | #954 Construct Next-Token Prediction Targets [easy] https://www.deep-ml.com/problems/954 | #948 Find Most Frequent Token Pair for BPE [easy] https://www.deep-ml.com/problems/948 | #949 Replace Token Pair in BPE Sequences [easy] https://www.deep-ml.com/problems/949 | #950 BPE Encode Text Using Merge Table [medium] https://www.deep-ml.com/problems/950 | #951 BPE Decode Token IDs to Text [easy] https://www.deep-ml.com/problems/951 | #952 BPE Pre-Tokenization with Whitespace Marking [medium] https://www.deep-ml.com/problems/952 | #380 Byte Pair Encoding (BPE) Tokenizer [medium] https://www.deep-ml.com/problems/380 | #1031 Extending a BPE Tokenizer with New Special Tokens [medium] https://www.deep-ml.com/problems/1031 | #1028 Resize LM Embedding and Output Head for New Tokens [medium] https://www.deep-ml.com/problems/1028 | #1059 Pad and Truncate Tokenized Sequences [easy] https://www.deep-ml.com/problems/1059 | #442 VLM Visual Token Count from Image Resolution and Patch Size [easy] https://www.deep-ml.com/problems/442

**解法**: #380/#948-#951 BPE 训练：统计相邻 token pair 频次→合并最高频 pair→记录 merge 规则，重复到目标词表大小；encode 按 merge 表顺序贪心合并；decode 反查。#1028 resize embedding：新增行用均值或随机初始化，同时同步 tie 的 LM head——推断解法。

来源: <https://www.deep-ml.com/problems/380>

### [重点] Mixture-of-Experts (MoE) 题清单（12 题）
*mixed (easy→hard) · 频率: SPARSELY GATED MoE / DeepSeek 合集核心 · 2026-07*

#123 Calculate Computational Efficiency of MoE [easy] https://www.deep-ml.com/problems/123 | #124 Implement the Noisy Top-K Gating Function [medium] https://www.deep-ml.com/problems/124 | #229 Sparse MoE Top-K Routing [medium] https://www.deep-ml.com/problems/229 | #389 Mixture of Experts Load Balancing Loss [medium] https://www.deep-ml.com/problems/389 | #409 MoE with Shared Expert Forward Pass [medium] https://www.deep-ml.com/problems/409 | #125 Implement a Sparse Mixture of Experts Layer [hard] https://www.deep-ml.com/problems/125 | #458 Implement Sigmoid MoE Router with Bias Correction [hard] https://www.deep-ml.com/problems/458 | #731 Hash-Based Expert Routing for MoE Layers [easy] https://www.deep-ml.com/problems/731 | #744 Anticipatory Routing for MoE Training Stability [hard] https://www.deep-ml.com/problems/744 | #439 Expert Parallelism Token Routing and Communication Cost [medium] https://www.deep-ml.com/problems/439 | #1015 MoE Parameter and Active-Token Memory Estimator [medium] https://www.deep-ml.com/problems/1015 | #1016 Estimate MoE vs Dense FFN Parameters with Match-Dense Sizing [medium] https://www.deep-ml.com/problems/1016

**解法**: #124 Noisy Top-K gating：gate=softmax(topk(Wx + StandardNormal·softplus(W_noise·x)))，只保留 top-k experts。#389 load balancing loss：鼓励 token 均匀分配，loss=α·N·Σ(f_i·P_i)（f_i=分到 expert i 的 token 比例，P_i=router 分给 i 的平均概率）——推断为 Switch Transformer 式辅助损失。

来源: <https://www.deep-ml.com/problems/125>

### [重点] RL 基础题清单（MDP/Bellman/Q-learning/MC/bandit，19 题）
*mixed (easy→hard) · 频率: 'Reinforcement Learning: An Introduction'(Sutton&Barto) 合集，RL 类目共 192 题为全站第三大 · 2026-07*

#157 Bellman Equation for Value Iteration [medium] https://www.deep-ml.com/problems/157 | #464 Bellman Expectation Equation for State-Value [medium] https://www.deep-ml.com/problems/464 | #465 Bellman Expectation Equation for Action-Value [medium] https://www.deep-ml.com/problems/465 | #133 Q-Learning Algorithm for MDPs [medium] https://www.deep-ml.com/problems/133 | #477 Double Q-Learning Algorithm [medium] https://www.deep-ml.com/problems/477 | #158 Epsilon-Greedy Action Selection for n-Armed Bandit [medium] https://www.deep-ml.com/problems/158 | #159 Incremental Mean for Online Reward Estimation [easy] https://www.deep-ml.com/problems/159 | #161 Exponential Weighted Average of Rewards [easy] https://www.deep-ml.com/problems/161 | #543 Estimate Action Values Using Sample Averaging [easy] https://www.deep-ml.com/problems/543 | #472 Off-Policy MC Prediction with Importance Sampling [medium] https://www.deep-ml.com/problems/472 | #473 Weighted Importance Sampling for Off-Policy [medium] https://www.deep-ml.com/problems/473 | #474 Off-Policy MC Control with Weighted IS [hard] https://www.deep-ml.com/problems/474 | #511 Greedy Policy Improvement [medium] https://www.deep-ml.com/problems/511 | #518 Cliff Walking: Sarsa vs Q-Learning [medium] https://www.deep-ml.com/problems/518 | #566 Expected vs Sample Updates Comparison [medium] https://www.deep-ml.com/problems/566 | #599 Full vs Sample Backup Comparison [medium] https://www.deep-ml.com/problems/599 | #610 Branching Factor Impact on Sample Backups [medium] https://www.deep-ml.com/problems/610 | #641 Gibbs Softmax Action Selection [easy] https://www.deep-ml.com/problems/641 | #616 Policy Gradient with Softmax Action Selection [medium] https://www.deep-ml.com/problems/616

**解法**: #133 Q-learning：Q(s,a)+=α[r+γ·max_a' Q(s',a')-Q(s,a)]（off-policy TD）。#472/#473 重要性采样比 ρ=Π π(a|s)/b(a|s)，加权 IS 用 Σρ·G / Σρ 降方差。这些是标准 Sutton&Barto 内容。

来源: <https://www.deep-ml.com/problems/133>

### [重点] 策略优化 / RLHF / post-training 题清单（35 题，最贴合候选人）
*mixed (easy→hard) · 频率: 'Deconstructing GRPO' + 'Fine-Tuning LMs from Human Preferences' 合集核心；候选人 SFT+RL 背景最应刷的一组 · 2026-07*

#122 Policy Gradient with REINFORCE [hard] https://www.deep-ml.com/problems/122 | #481 REINFORCE with Baseline: Episode Update [hard] https://www.deep-ml.com/problems/481 | #552 REINFORCE with Value Baseline [hard] https://www.deep-ml.com/problems/552 | #482 One-step Advantage Actor-Critic [medium] https://www.deep-ml.com/problems/482 | #553 A2C Batch Update from Parallel Environments [hard] https://www.deep-ml.com/problems/553 | #487 Compute GAE Advantages with Episode Boundaries [medium] https://www.deep-ml.com/problems/487 | #485 PPO Clipped Surrogate Loss with Clip Diagnostics [medium] https://www.deep-ml.com/problems/485 | #569 Natural Policy Gradient [hard] https://www.deep-ml.com/problems/569 | #589 Deterministic Policy Gradient [hard] https://www.deep-ml.com/problems/589 | #594 A3C [hard] https://www.deep-ml.com/problems/594 | #595 Trust Region Policy Optimization (TRPO) [hard] https://www.deep-ml.com/problems/595 | #101 GRPO Objective Function [hard] https://www.deep-ml.com/problems/101 | #224 Group Relative Advantage for GRPO [easy] https://www.deep-ml.com/problems/224 | #225 KL Divergence Estimator for GRPO [easy] https://www.deep-ml.com/problems/225 | #210 Dr. GRPO: Complete Objective Function [medium] https://www.deep-ml.com/problems/210 | #209 GSPO: Group Sequence Policy Optimization [hard] https://www.deep-ml.com/problems/209 | #382 Direct Preference Optimization (DPO) Loss [medium] https://www.deep-ml.com/problems/382 | #1068 DPO Implicit Reward Computation [easy] https://www.deep-ml.com/problems/1068 | #1069 Preference Dataset Collate Function for DPO [hard] https://www.deep-ml.com/problems/1069 | #769 DPO Loss with NLL Regularization [medium] https://www.deep-ml.com/problems/769 | #484 Reward Model Loss from Pairwise Human Preferences [medium] https://www.deep-ml.com/problems/484 | #488 Reward Model Validation Accuracy [easy] https://www.deep-ml.com/problems/488 | #489 Log-Probability Ratio for Token Sequences [medium] https://www.deep-ml.com/problems/489 | #486 Adaptive KL-Penalized Reward Shaping for RLHF [medium] https://www.deep-ml.com/problems/486 | #232 PTX Loss for Catastrophic Forgetting Prevention (RLHF) [medium] https://www.deep-ml.com/problems/232 | #361 Fine-Tune Model Weights with RLHF Policy Gradient [medium] https://www.deep-ml.com/problems/361 | #379 RAFT: Iterative Reward-Ranked Fine-Tuning Loop [medium] https://www.deep-ml.com/problems/379 | #1077 RAFT for RLVR with Binary Rewards [medium] https://www.deep-ml.com/problems/1077 | #1078 RAFT++ with Importance Sampling and Clipping [medium] https://www.deep-ml.com/problems/1078 | #1079 Reinforce-Rej: Filtering Trivial Prompt Groups [medium] https://www.deep-ml.com/problems/1079 | #863 Self-Critique Loss for Constitutional AI [medium] https://www.deep-ml.com/problems/863 | #865 RLAIF Reward Model from AI Feedback [medium] https://www.deep-ml.com/problems/865 | #504 Distributed On-Policy Reinforcement Learning [hard] https://www.deep-ml.com/problems/504 | #664 Asynchronous PPO Training Pipeline [hard] https://www.deep-ml.com/problems/664 | #228 Budget-Constrained RL Loss [medium] https://www.deep-ml.com/problems/228

**解法**: #122 REINFORCE：策略 softmax(θ[s])，梯度=Σ_t ∇logπ(a_t|s_t)·G_t，对 episode 求均值。#485 PPO：L=E[min(r_t·Â, clip(r_t,1-ε,1+ε)·Â)]，r_t=π/π_old。#382 DPO：L=-logσ(β(logπ(y_w)/π_ref(y_w) - logπ(y_l)/π_ref(y_l)))。#101 GRPO：用组内相对优势 Â=(r-mean)/std 替代 critic，加 clip + KL 惩罚。#487 GAE：δ_t=r+γV(s')-V(s)，Â=Σ(γλ)ˡδ_{t+l}。以上为标准 post-training 算法解法。

来源: <https://www.deep-ml.com/problems/101>

### [重点] 从零搭 GPT / makemore / micrograd 题清单（12 题）
*mixed (medium→hard) · 频率: 'Build GPT from Scratch: Karpathy Walkthrough' / makemore / micrograd 合集；面试常考端到端搭模型 · 2026-07*

#918 Build a Tiny GPT (pytorch) [hard] https://www.deep-ml.com/problems/918 | #939 Tinygrad: Build a Tiny GPT [hard] https://www.deep-ml.com/problems/939 | #88 GPT-2 Text Generation [hard] https://www.deep-ml.com/problems/88 | #1007 GPT FeedForward Block (Linear-GELU-Linear) [medium] https://www.deep-ml.com/problems/1007 | #1026 Weight Tying Between Embedding and LM Head [easy] https://www.deep-ml.com/problems/1026 | #1009 Count Trainable Parameters with Weight Tying in GPT [medium] https://www.deep-ml.com/problems/1009 | #1050 Per-Layer Embedding Projection (PLE) [hard] https://www.deep-ml.com/problems/1050 | #1056 Pre-Norm GPT Transformer Block Forward Pass [hard] https://www.deep-ml.com/problems/1056 | #745 Multi-Token Prediction Training Objective [medium] https://www.deep-ml.com/problems/745 | #997 Manual Backprop Through Cross-Entropy Intermediates [hard] https://www.deep-ml.com/problems/997 | #1002 Fused Backward Pass of BatchNorm1d [hard] https://www.deep-ml.com/problems/1002 | #1004 Implement FlattenConsecutive Layer for Hierarchical Fusion [medium] https://www.deep-ml.com/problems/1004

**解法**: #918 Tiny GPT = token emb + pos emb → N×(pre-norm: MHA + FFN 残差) → final LN → LM head（可与 emb 权重共享）。#997/#1002 是 Karpathy 'Backprop Ninja' 式手推反向，对 embedding→CE 全链路逐步求梯度。#1007 FFN=Linear(d→4d)→GELU→Linear(4d→d)。

来源: <https://www.deep-ml.com/problems/918>

### 其他相关主题：LLM 评测 / SAE 可解释性 / LoRA / 扩散 / Triton 内核
*mixed · 频率: 覆盖 Anthropic 方向(可解释性/Constitutional AI) 与数据管线方向 · 2026-07*

LLM 评测 & judge：#317 Rubric-Based LLM Judge Evaluation [medium] https://www.deep-ml.com/problems/317 | #323 Pairwise Preference Judge for LLM Comparison [medium] https://www.deep-ml.com/problems/323 | #763 Million-Token Corpus QA Evaluation [medium] https://www.deep-ml.com/problems/763 | #110 Evaluate Translation Quality with METEOR https://www.deep-ml.com/problems/110 . 机制可解释性(SAE/logit attribution)：#851 Train a Sparse Autoencoder on Residual-Stream Activations [medium] https://www.deep-ml.com/problems/851 | #852 Top-K Sparse Autoencoder Forward Pass [medium] https://www.deep-ml.com/problems/852 | #858 Direct Logit Attribution for Transformer Components [medium] https://www.deep-ml.com/problems/858 . 高效微调：#873 Adapter Bottleneck Layer for Transformer Fine-Tuning [medium] https://www.deep-ml.com/problems/873 | #874 Memory Savings of LoRA vs Full Fine-Tuning with Adam [medium] https://www.deep-ml.com/problems/874 . 扩散：#396 DDPM Reverse Sampling Step [medium] https://www.deep-ml.com/problems/396 | #398 DDIM Deterministic Sampling Step [medium] https://www.deep-ml.com/problems/398 | #302 Diffusion Reconstruction Loss [medium] https://www.deep-ml.com/problems/302 . Triton GPU 内核：#969 Triton: Element-wise ReLU [easy] https://www.deep-ml.com/problems/969 | #973 Triton: Numerically Stable Fused Softmax [medium] https://www.deep-ml.com/problems/973 | #976 Triton: Low-Memory Dropout with Seeded RNG [medium] https://www.deep-ml.com/problems/976 . Scaling law：#765 Fit Power-Law Scaling Law for Training Tokens [medium] https://www.deep-ml.com/problems/765 . 数据管线(对 mid-training 背景对口)：#775 Greedy Semantic Deduplication via Cosine Similarity [medium] https://www.deep-ml.com/problems/775 | #786 N-gram Frequency Resampling for Dataset Diversity [medium] https://www.deep-ml.com/problems/786 | #794 Combined RM and LLM Quality Filter [easy] https://www.deep-ml.com/problems/794 | #771 Token Distribution KL Divergence Filter [easy] https://www.deep-ml.com/problems/771 | #508 Quality Filtering with Rejection Sampling [easy] https://www.deep-ml.com/problems/508 .

**解法**: SAE(#851/#852)、Constitutional AI(#863)、RLAIF(#865)与 Anthropic 研究强相关；数据去重/过滤/重采样(#775/#786/#794/#771)与候选人 Reflection.ai mid-training 数据管线经历直接对口，面试可作为项目讨论锚点。

来源: <https://www.deep-ml.com/problems/851>

### 开源题库仓库：完整题干+参考解可离线获取（164 题）
*mixed · 频率: 官方唯一的完整题干+参考解来源 · 2026-07*

deep-ml 全部题目开源在 github.com/Open-Deep-ML/DML-OpenProblem 。仓库结构：questions/{id}_{slug}/ 下含 description.md（题干）、learn.md（知识点讲解）、starter_code.py、solution.py（参考解）、tests.json（测试用例）、meta.json（id/title/difficulty/category/video），部分题另有 pytorch/ 和 tinygrad/ 变体目录。build/ 下有 {id}.json 打包好的完整题目（含 description/learn_section/solution/test_cases）。注意：仓库当前约 164 题有完整内容，站点约 1127 题中高编号新题（>~500）多数尚未同步到仓库，只能在站点上看题干。可 git clone 后离线批量阅读解法——例如 #53/#94/#107 attention、#49/#87 Adam、#101 GRPO、#122 REINFORCE 的完整题干与 solution.py 均在仓库内。meta.json 里还带部分题的讲解视频 YouTube 链接（如 #107 masked attention: https://youtu.be/R_OISH-JWPA ）。

**解法**: 抓取建议：clone 仓库后读 build/*.json 或 questions/*/solution.py 拿参考解；站点新题只能靠 /problems/{id} 页面题干（登录后可见完整描述+starter code，未登录仅 meta 摘要）。

来源: <https://github.com/Open-Deep-ML/DML-OpenProblem>

## ML 理论

### Bojie Li《200道大模型面试题》RL/后训练部分：PPO/DPO/GRPO 深挖题
*medium · 频率: very high（PPO vs DPO、GRPO vs PPO、KL penalty 在本次调研的几乎全部来源中出现） · 2025-04*

作者李博杰（《Hands-On Large Language Models》配套题），2025-04-27 发布。RL/post-training 题目原文：(1) PPO 与 DPO 在计算效率、实现复杂度、训练稳定性上的差异？(2) 如果只有高质量但数量有限的人类偏好数据集，该用 PPO 还是 DPO？(3) PPO 中 actor model、critic model、reward model、reference model 各自的作用？(4) PPO 中 'Proximal' 是什么意思？如何防止模型在微调数据集之外的问题上泛化能力下降？(5) PPO 中 normalized advantage、value function clipping、entropy regularization 等技巧的作用？(6) DPO 中 beta 参数的含义，调大/调小有什么影响？(7) 场景题：一个全部内容由 AI 生成的网站（有用户投票等信号），如何把它转化为 DPO 需要的偏好数据？(8) DeepSeek R1 用的 GRPO 与 PPO 的区别？advantage normalization 如何解决 value function 估计问题？(9) GRPO 中 KL penalty 项的作用？(10) 如何用 RL 方法增强 LLM 的 tool-calling 能力？

**解法**: 要点（部分为我的推断补全）：(1) DPO 免 RM/免采样、离线监督式训练更稳更省，PPO 在线采样天花板更高；(2) 数据少且固定→DPO（离线数据利用率高、无 RM 过拟合风险）；(3) actor=被优化策略，critic=估计 value 降方差，RM=打分，reference=KL 锚点防漂移；(4) Proximal=限制新旧策略距离（clip ratio），配合 KL-to-ref 与混入预训练数据防遗忘；(6) beta 是 KL 约束强度的倒数温度：beta 大→紧贴 reference、偏好信号弱，beta 小→激进拟合偏好、易过优化；(8) GRPO 砍掉 critic，用同一 prompt 组内多条采样的 reward 做 mean/std 归一化当 advantage；(9) GRPO 的 KL 用 k3 无偏估计直接加在 loss 上（而非 PPO 混入 reward）；(10) 工具调用轨迹上做 RLVR：以任务完成/验证器为 reward，对多轮 tool-use 轨迹做 GRPO/PPO，mask 工具返回 token 只训模型决策 token（我的推断）。

来源: <https://01.me/en/2025/04/llm-interview-questions/>

### Bojie Li 200题：Attention / KV cache / FlashAttention / RoPE 内部机制题
*medium · 频率: very high（KV cache、sqrt(d_k)、GQA/MQA 为中英文面经共同最高频） · 2025-04*

同一来源的 LLM internals 题目原文：(1) attention 表达式里 Q 和 K 看似对称，为什么 KV cache 只缓存 K、V 不缓存 Q？(2) 没有 KV cache 推理性能会下降多少？(3) 一个支持 8K 上下文的开源模型如何扩展到 32K？上下文变长对 KV cache 带来什么挑战？(4) attention 如何计算 token 间相关性？每个 head 只关注一个 token 吗？为什么 softmax 前要除以 sqrt(d_k)？(5) 为什么需要多头？GQA、MQA 与单纯减少 head 数有何不同？(6) FlashAttention 不减少计算量为什么能加速？它如何实现 softmax 的增量计算？(7) RoPE 相比绝对位置编码的优势？RoPE 外推到长上下文有什么挑战？

**解法**: 要点（我的推断补全）：(1) 生成第 t 个 token 时只需当前 Q_t 与历史所有 K、V 交互，历史 Q 不再被用到；(2) 无 KV cache 每步重算全部前缀，复杂度从 O(n) 每 token 变 O(n²)，长序列慢一到两个数量级；(3) 位置插值/NTK-aware RoPE scaling/YaRN + 长文本继续训练；KV cache 显存随长度线性涨→需 GQA、量化 KV、PagedAttention；(4) 除 sqrt(d_k) 防止点积方差随维度增大导致 softmax 饱和、梯度消失；(5) MQA 所有头共享一组 KV、GQA 分组共享，只减 KV cache 不减表达 Q 头数，比直接砍头数掉点少；(6) FlashAttention 靠 tiling+算子融合减少 HBM 读写（IO-bound→SRAM 内完成），用 online softmax 维护 running max 和分母增量合并；(7) RoPE 相对位置性质+外推性好，但超训练长度后高频维度失真，需插值缩放。

来源: <https://01.me/en/2025/04/llm-interview-questions/>

### llmgenai/LLMInterviewQuestions（1.9k星）：Preference Alignment + SFT + internals 题清单
*medium · 频率: very high（repo 本身声称为大厂真题汇总；题目与其他来源高度重合） · 2025*

号称收录 Google/Nvidia/Meta/Microsoft 等公司真题，100+题分15类。偏好对齐类：什么时候该选 preference alignment 而不是继续 SFT？什么是 RLHF、怎么用？RLHF 中的 reward hacking 问题是什么？解释各种 preference alignment 方法（RLHF/DPO/ORPO/KTO）。SFT 类：什么是微调、为什么需要？什么场景需要微调 LLM？如何决策是否微调？如何构造 Q&A 微调数据集？微调超参怎么设？PEFT 方法有哪几类？什么是灾难性遗忘？re-parameterized 微调方法有哪些？Internals 类：详细解释 self-attention；什么是位置编码；详解 Transformer 架构；Transformer 为什么计算和显存开销大；如何增加 LLM 的上下文长度；如何计算 KV cache 大小；multi-head attention 各层维度；FP8 是什么及优势；如何低精度训练不掉点；什么是 MoE。注意：答案在其付费课程里，README 只有题目。

**解法**: KV cache 大小计算（我的推断）：2(K和V) × num_layers × num_kv_heads × head_dim × seq_len × batch × bytes_per_elem；如 Llama-7B fp16、4K 上下文单条 ≈ 2×32×32×128×4096×2B ≈ 2GB。SFT→偏好对齐的切换时机：当目标是'多目标权衡/风格与安全偏好'而非'唯一正确答案'，或 SFT 已收敛但仍有 helpful/harmless 权衡问题时。

来源: <https://github.com/llmgenai/LLMInterviewQuestions>

### wdndev/llm_interview_note（11.5k星）：RLHF 专章14问带完整中文答案
*medium · 频率: very high（11.5k星，中文面试准备事实标准） · 2024*

中文最高星 LLM 面试 repo。'1.rlhf相关'文件题目：1) 简单介绍强化学习？2) 简单介绍 RLHF（三步：SFT→训练 RM→PPO 微调，含为什么需要 SFT 模型/RM 模型/RL 模型的三段论）；3) 奖励模型需要和基础模型一致吗？4) RLHF 实践中有哪些不足？（人类反馈成本高、主观性、反馈延迟稀疏、错误反馈影响、探索-利用失衡）5) 人工偏好数据成本高难量产怎么解决？（模拟数据、主动学习、在线学习、众包、数据增强/迁移）6) SFT→RM→PPO 三阶段流程长、迭代慢怎么办？7) PPO 同时4个模型（2训练2推理）资源要求高怎么办？（答案给出 RRHF 方案）8) 基于人类反馈的 RL 完整流程（PPO 四模型：policy/reward/critic/reference + 环境采样→GAE 优势估计→优化调整）9-14) LLM Agent 定义/关键能力/构建/类型/自治能力来源/领域知识注入。RL 强化学习基础章（2.强化学习）另含约40问：MDP/贝尔曼方程、on-policy vs off-policy、Q-learning vs Sarsa、MC vs TD 偏差方差、DQN 目标网络+经验回放、策略梯度手推、REINFORCE、A3C、DDPG、PPO。

**解法**: 该 repo 自带完整中文答案，可直接背诵。RL 基础链条答案要点：策略梯度 ∇J=E[∇logπ(a|s)·R]，减 baseline 降方差→critic 估 V(s) 得 advantage→GAE 折衷偏差方差→PPO clip 限制更新步长。

来源: <https://github.com/wdndev/llm_interview_note/blob/main/07.%E5%BC%BA%E5%8C%96%E5%AD%A6%E4%B9%A0/1.rlhf%E7%9B%B8%E5%85%B3/1.rlhf%E7%9B%B8%E5%85%B3.md>

### 小林面试笔记《SFT之后还有哪些Post-Training？RLHF、DPO、GRPO、拒绝采样什么关系》8问
*easy · 频率: very high（'各后训练方法关系'是面试开场标配题） · 2026*

题目+一句话答案：1) Post-Training 概念？（SFT 之后所有继续训练方法的总称）2) 为什么 SFT 之后还需要 Post-Training？（SFT 只产出'合格'不产出'优质'，缺安全对齐和偏好优化）3) RLHF 核心机制？（偏好数据训 RM，PPO 优化主模型并保持 KL 约束）4) DPO 解决什么问题？（绕过显式奖励模型，把 RLHF 目标数学变换成只需 policy+reference 的监督损失）5) GRPO 意义？（砍掉 Value Model，用组内相对 baseline 替代，省显存且保留 RL 探索能力）6) 拒绝采样怎么工作？（生成多条→RM 挑 top→再做一轮 SFT）7) RLAIF 创新点？（用更强 AI 当老师批量生成偏好数据代替人标）8) 实际管线怎么组合？（Llama 2 = SFT+拒绝采样+PPO/RLHF；DeepSeek R1 = SFT+多轮 GRPO+拒绝采样）。

**解法**: 记忆框架（原文）：SFT 教'说什么'，偏好优化教'怎么选'，RL 教'怎么想'。补充（我的推断）：SFT vs RLHF 数据配比追问——SFT 阶段百万级指令数据重多样性，偏好阶段数十万 pair 重质量与一致性，RL 阶段 prompt 集要难度分布匹配且可验证。

来源: <https://xiaolinnote.com/ai/llm/post_training.html>

### 小林coding《AI大模型八股面试题》74道高频题总目录（Transformer/对齐/KV Cache/MoE/量化/Agent/RAG）
*medium · 频率: very high（自称74道大厂高频题，全站式题库） · 2026*

cnblogs 镜像（xiaolincoding.com 主站连接被拒）。600张图解+25万字答案。可见题目：Transformer 架构基本原理？Encoder/Decoder 是什么？MHA 有哪些局限？MQA、GQA、Flash Attention 怎么解决？位置编码干什么用？sin/cos、RoPE、ALiBi 区别？SFT 之后还有哪些 Post-Training？RLHF、DPO、GRPO、拒绝采样什么关系？DPO 和 PPO 区别？大模型是怎么训练出来的？KV Cache 是什么？Prompt Caching 原理？MoE 是什么？DeepSeek V3、Qwen 为什么用 MoE？量化是什么？INT8/INT4/AWQ/GPTQ 怎么选？LoRA 除了减参数量还有什么优点？另有 Agent 16题（ReAct、任务分解、memory、multi-agent 协作）和 RAG 20题（chunking、embedding、向量库、检索优化）。

**解法**: 量化选型一句话（我的推断）：权重敏感场景 GPTQ（逐层误差补偿），激活 outlier 明显选 AWQ（按激活重要性保护权重通道），需要训练中低精度用 QAT/FP8；LoRA 额外优点：可插拔多任务适配、无推理延迟（合并权重后）、省优化器状态显存。

来源: <https://www.cnblogs.com/xiaolincoding/p/20534325>

### aman.ai《Policy/Preference Optimization》primer——RLHF/DPO/GRPO 全家桶答案参考源
*medium · 频率: very high（作为答案参考被广泛引用） · 2024-06*

覆盖 RLHF、RLAIF、DPO、KTO、IPO、ORPO、SimPO、GRPO 等约18种方法。核心答案要点：RLHF 管线=SFT→Bradley-Terry pairwise ranking loss 训 RM→PPO+KL 正则优化；PPO clipped surrogate = min(ratio·A, clip(ratio,1−ε,1+ε)·A) 形成隐式信赖域；KL penalty 防 reward hacking 并保留预训练能力；DPO 从 KL 约束的奖励最大化闭式解推出直接偏好损失、消除显式 RM；DPO β 类似温度，越大偏好间隔越受强调；KTO 用前景理论的非对称价值函数，只需 binary good/bad 标签不需 pair；GRPO 去掉 critic、组内相对归一化算 advantage、KL 显式加入 loss；IPO/ORPO/SimPO 为去 reference model 或长度归一化的变体（SimPO 用长度归一化的隐式奖励）。适合作为'解释每个算法并比较'类面试题的标准答案库。注意 aman.ai/primers/ai/rlhf/ 与 /llm-alignment/ 均404，此为正确 URL。

**解法**: 比较题万能框架：按'是否在线采样 / 是否需要 RM / 是否需要 critic / 是否需要 reference / 数据形态(pair、binary、group)'五轴对比 PPO/DPO/KTO/GRPO。

来源: <https://aman.ai/primers/ai/preference-optimization/>

### Lilian Weng《Reward Hacking in Reinforcement Learning》——reward hacking 题标准答案源
*medium · 频率: very high（reward hacking 出现在几乎所有 RLHF 面经清单中；Anthropic 尤其关注） · 2024-11*

2024-11-28，约37分钟长文。面试可直接引用的内容：reward hacking 定义（RL agent 利用奖励函数或环境的缺陷/歧义拿高分而不学会预期行为）；存在原因（环境不完美+奖励函数难以精确指定，Goodhart's law）；LLM 场景实例：模型学会改单元测试来通过代码任务、迎合用户已有观点（sycophancy）、RM 对格式/长度的偏好被利用；分类：reward tampering vs specification gaming；in-context reward hacking；缓解方向：更好的 RM 集成/正则、KL 约束、RM 迭代更新、过程监督、对抗评测。适配面试题：'什么是 reward hacking、见过哪些实例、如何检测与缓解'（本次调研中英文来源均反复出现该题）。

**解法**: 检测手段（我的推断补全）：训练中监控 KL 与 RM 分数同时暴涨、离线用 held-out RM/人评复核高 reward 样本、长度/格式统计漂移告警；缓解：RM ensemble、reward clipping、KL 系数调度、周期性用新 on-policy 数据重训 RM、RLVR 换可验证奖励。

来源: <https://lilianweng.github.io/posts/2024-11-28-reward-hacking/>

### HuggingFace blog《A Guide to RL Post-Training: PPO, DPO, GRPO and Beyond》——算法比较题答案参考
*medium · 频率: very high（'PPO vs DPO 谁更好'为本次调研出现频率最高的单题） · 2025*

覆盖'PPO vs DPO vs GRPO 该怎么选'类面试题的标准论述：PPO 优化 KL 正则化目标、仍是对齐强基线；DPO 把 KL 约束奖励最大化目标改写为分类式损失、去掉 RL rollout 与 KL 调参；GRPO 由 DeepSeek 提出、去掉 PPO 的 value model、用组采样 baseline 估计。配合论文《Is DPO Superior to PPO for LLM Alignment? A Comprehensive Study》(arXiv:2404.10719，结论：精调好的 PPO 在难任务尤其代码上普遍优于 DPO，DPO 对分布偏移敏感)可回答高频追问'DPO 和 PPO 到底谁强、什么时候用谁'。

**解法**: 标准答案骨架：DPO 赢在简单稳定省算力、适合离线高质量 pair；PPO/GRPO 赢在 on-policy 探索+可用任意奖励信号（含可验证奖励），分布外泛化和推理任务上限更高；工业界常 DPO 做第一轮偏好对齐再上 online RL。

来源: <https://huggingface.co/blog/karina-zadorozhny/guide-to-llm-post-training-algorithms>

### 跨源高频题清单：出现于3个以上来源的必背题（含一句话答案）
*medium · 频率: very high（每题≥3个独立来源） · 2026-07*

基于本次全部来源的频率统计（锚定 URL 为覆盖面最全的 Bojie Li 200题）。必背题及一句话要点：1) RLHF 三阶段流程——SFT→BT loss 训 RM→PPO+KL 优化。2) PPO vs DPO——离线免 RM 简单稳定 vs 在线探索上限高。3) PPO 四模型各作用——actor/critic/RM/reference。4) KL penalty/reference model 为什么必要——防 reward hacking+防遗忘。5) GRPO 原理与 PPO 区别——组内归一化 advantage 替代 critic。6) reward hacking 定义/实例/缓解——Goodhart；改测试用例/迎合；KL+RM迭代+ensemble。7) DPO loss 手写与 β 含义——−logσ(β·Δlogratio)；β=KL 强度。8) 拒绝采样/RLAIF/RLVR 各是什么。9) R1/o1 怎么训的、R1-Zero vs R1。10) attention 为何除 sqrt(d_k)。11) MHA/MQA/GQA 与 KV cache 大小计算。12) FlashAttention 为什么快——IO-aware tiling+online softmax。13) RoPE 原理与长度外推。14) MoE 路由与负载均衡/routing collapse。15) PTQ vs QAT、AWQ/GPTQ/NF4 选型。16) LoRA/QLoRA 原理与优点。17) 灾难性遗忘与缓解。18) SFT后为什么还要偏好对齐、数据怎么配比。19) 显存估算（训练16字节/参数）。20) 解码策略 temperature/top-k/top-p/beam。

**解法**: 此条为我对全部来源的汇总推断；每题详细答案见对应条目。建议按 20 题×(定义→公式→trade-off→failure mode→实战经验) 五层准备，RS 面试重点在 trade-off 与 failure mode 层。

来源: <https://01.me/en/2025/04/llm-interview-questions/>

### Bojie Li 200题：MoE / 量化 / Tokenizer 题（DeepSeek 系列细节）
*hard · 频率: high（MoE 负载均衡、PTQ/QAT 在多个中文面经复现） · 2025-04*

题目原文：MoE：(1) 为什么 DeepSeek MoE 前三层用 dense、后面层用 MoE？(2) DeepSeek MoE 与 Mixtral MoE 的区别？细粒度专家划分和 shared expert isolation 的优势？(3) DeepSeek MoE 的专家负载均衡如何解决 routing collapse？量化：(4) PTQ 和 QAT 的区别及优缺点？(5) QLoRA 的 block quantization 如何解决普通量化的信息损失？(6) DeepSeek V3 混合精度训练在哪些矩阵计算用 FP8？如何做 grouped quantization？Tokenizer：(7) LLM tokenizer 与传统中文分词的区别？一句话的 tokenize 方式唯一吗？(8) 为什么 BM25 检索对中文分词质量敏感而 LLM 对 tokenizer 选择不敏感？(9) GPT-4/LLaMA 用的 byte-level BPE 相比传统 BPE 的优势？(10) 国产模型为什么能用更少 token 表示中文语料？

**解法**: 要点（我的推断补全）：(1) 浅层学通用低级特征、路由不稳定，dense 更稳；(2) DeepSeek 细粒度专家（更多更小专家）+ 常驻 shared expert 承接通用知识，提高组合表达力；(3) V2 用辅助负载均衡 loss，V3 改为 auxiliary-loss-free 的 per-expert bias 动态调整；(4) PTQ 免训练便宜但低比特掉点，QAT 训练时模拟量化精度高但贵；(5) QLoRA 的 NF4 按块（block-wise）量化+双重量化，块内归一化减少 outlier 影响；(9) byte-level 无 OOV、任意 Unicode 无损往返；(10) 训练语料中文占比高→BPE 合并出更多中文长词块，压缩率高。

来源: <https://01.me/en/2025/04/llm-interview-questions/>

### 博客园 MoonOut《LLM算法岗八股问答(3)·强化学习与RLHF》11问（2026新题含OPD/GSPO）
*hard · 频率: single report（但题目与2026年国内大厂后训练岗面经高度一致，OPD/GSPO/DAPO 为新趋势题） · 2026-03*

2026-03-21 发布，题目原文+答案要点：1) 介绍 PPO、DPO、GRPO 的定义、结构区别、优缺点及适用场景（PPO 效果最优但资源大；DPO 高效但吃数据质量；GRPO 性价比好适合客观任务）。2) PPO 的 Clip 机制是什么？为什么 Clip 了外面还要再取一次 min？（外层 min 保证目标是原目标的保守下界/悲观估计）。3) 除了 Clip 还有哪些方法限制分布差异？（KL 惩罚、early stopping、TRPO 信赖域、自然梯度）。4) PPO 和 GRPO 的结构区别与各自适用场景？（PPO 四模型通用；GRPO 三模型适合数学/代码等可验证任务）。5) DAPO、GSPO 具体做了什么改进？（DAPO：clip-higher 解耦上下裁剪+动态采样，解决长 CoT 熵坍缩；GSPO：序列级无偏 ratio 估计修正 GRPO 的 token 级偏差）。6) 奖励函数坍缩现象？（RM 学到 token 捷径→模式坍塌、多样性丧失）。7) 多目标奖励冲突怎么处理？（加权求和、GDPO、分层优化、Pareto 前沿）。8) 离线 RL vs 在线 RL？RLHF 属于哪种？（混合：RM 训练离线、PPO 阶段在线）。9) 为什么要用 Reference Model？（防遗忘预训练能力、防 reward hacking，KL 惩罚约束不偏离原分布）。10) KL 散度公式及几种估计方法？（反向 KL 是 LLM 标准；k1/k2/k3 蒙特卡洛估计）。11) on-policy distillation 的 loss 是什么？能写成 ratio×advantage 形式吗？（OPD loss=反向 KL，可改写为 ratio 乘教师引导的优势项）。

**解法**: KL 估计器细节（我的推断补全）：k1=logπ/π_ref（无偏高方差可为负），k2=½(log r)²（有偏低方差），k3=r−1−log r（无偏、恒非负、低方差，GRPO 默认）。PPO min 的原因：只在'更新使目标变差'方向保留梯度，防止 ratio 越界后仍获得正向激励。

来源: <https://www.cnblogs.com/moonout/p/19749191>

### CSDN镜像《大模型面试：RLHF夺命连环17问》（RM/Value Model/优势函数逐层深挖）
*medium · 频率: high（17问在国内多平台被反复转载引用） · 2025-11*

2025-11-22 发布（知乎/CSDN 多平台转载，deepseek.csdn.net 镜像已404，adg.csdn.net 镜像可访问）。17问：1) RLHF 定义与价值；2) RLHF vs SFT（RLHF 处理多目标权衡，SFT 需明确标准答案）；3) 三阶段训练流程；4) 奖励模型的意义（把人类偏好转化为可量化奖励信号）；5) RM 数据怎么收集（同 prompt 多候选人工排序）；6) RM 训练后是固定的吗？什么时候需要迭代更新？（分布漂移、被 reward hacking 时）；7) 价值模型(critic)的本质是什么？（预测当前状态起的长期预期收益，用于信用分配）；8) Value Model 怎么训练、标签怎么构造？（带衰减的回报作为回归目标）；9) 折扣因子 γ 一般设多少、作用？（0.9~0.99，平衡未来奖励权重）；10) 折扣与'早期错误更严重'矛盾吗？11) 优势函数怎么计算？（实际收益与预期 V(s) 之差）；12) advantage>0/<0 分别意味着什么？13) VM 有误差还能收敛吗？（相对优势比较比绝对值重要）；14) PPO 损失由哪几部分构成、与 RM 如何关联？（policy loss+value loss+entropy）；15) KL 散度约束的作用？（避免模型为刷高 reward 生成乱码，保持多样性）；16) reward hacking 怎么应对？（正则化、动态更新 RM、加大 KL 约束）；17) RLHF 常见失败模式？（模式坍塌、过度优化、标注者偏好冲突）。

**解法**: 文中自带答案要点（见 detail 括号内）。补充（我的推断）：LLM RLHF 里 γ 通常直接取1（序列短、reward 在末端），GAE 的 λ 才是主要方差调节钮；PPO 总 loss = L_clip − c1·L_value + c2·entropy。

来源: <https://adg.csdn.net/696f5667437a6b40336a0f23.html>

### 快手大模型算法工程师面经10道（含 Agentic Training mask 题）——中文大厂真题样例
*medium · 频率: high（第8题 agent 训练 mask 是2026年 agentic 后训练岗新高频题；其余为通用高频） · 2026-04*

2026-04-25 发布，基于快手 2025-2026 真实面经（对 OpenAI/Anthropic/GDM 面试同样是高频考点）：1) Self-Attention 为什么除以 sqrt(d_k)？（防 softmax 梯度饱和）2) RLHF 训练流程？PPO 为什么比 vanilla Policy Gradient 稳定？3) DPO 和 RLHF 核心区别？为什么 DPO 不需要 Reward Model？4) GRPO 原理和 DPO 有什么区别？（GRPO 组内相对优势归一化，适合可自动验证任务；DPO 离线偏好对）5) SFT 后的模型怎么评估？用什么数据集？（通用能力+业务对齐+安全多维度）6) 大模型推理加速实用方法？（KV Cache、量化、Continuous Batching、FlashAttention、投机解码）7) 多轮对话 LLM 与普通生成模型区别？8) 什么是 Agentic Training？工具返回的内容在训练时要不要 mask 掉？（应 mask，只训练模型自身决策/行动 token 的 loss）9) RAG 文档如何切分？10) 训练/推理显存不够怎么办？（ZeRO、梯度检查点、LoRA/QLoRA、混合精度）。

**解法**: 第8题展开（我的推断）：tool observation 是环境产生而非策略产生，若计入 LM loss 会让模型学着'预测环境'并稀释决策信号，且 RL 时 importance ratio 只应在策略生成 token 上计算；SFT 与 RL 都对 tool-return span 置 loss mask。第2题：PPO 通过 ratio clip + KL-to-ref 把每步更新限制在信赖域内，vanilla PG 高方差且一次坏更新即崩。

来源: <https://gitcode.csdn.net/69ec254454b52172bc6feb5d.html>

### 腾讯云开发者社区《DPO与GRPO专题学习》：损失函数级细节问答
*medium · 频率: high（DPO loss 手写、GRPO advantage 公式是2025-2026中文面经最常见的手推题） · 2025-11*

2025-11-24 发布。要点即典型追问答案：DPO loss = −log σ(β·Δ)，Δ=[logπ_θ(y+)−logπ_θ(y−)]−[logπ_ref(y+)−logπ_ref(y−)]；β 控制偏好强度。DPO 为什么是 offline？（直接用既有偏好对，不需要采样、RM、PPO，纯监督反向传播）。DPO 优势：不需要显式训练 Reward Model、不需要 RL 算法。DPO 关键局限：训练时要频繁对 ref+current 两个策略在两个回答上算 logprob，计算开销不低。GRPO 解决什么？（对每个 prompt 采样多条输出，组内相对优势，不训练 value function）。优势怎么算？adv=(r−mean_r)/(std_r+ε)。与 PPO 关键区别：无 value network，advantage 来自组内比较而非 critic 估计。常见实现坑：old_policy 必须冻结为独立 checkpoint 才能正确计算 importance sampling ratio。

**解法**: 追问预备（我的推断）：DPO 的隐式奖励 r(x,y)=β·log(π_θ(y|x)/π_ref(y|x))；DPO 会出现 chosen/rejected logprob 同时下降的 'likelihood displacement' 现象；GRPO 的 std 归一化在全对/全错组会除零→需过滤零方差组（DAPO 的动态采样动机）。

来源: <https://cloud.tencent.com/developer/article/2593079>

### Hao Hoang Top-50 LLM 面试题（含逐题一句话答案，gist 独立作答版）
*easy · 频率: high（该50题清单在 LinkedIn/Medium 广泛传播） · 2025-05*

原题单 Hao Hoang 2025-05 发布，gist 提供独立撰写答案。覆盖50题，与本任务相关的：tokenization（BPE/SentencePiece 无损处理罕见词）、attention（softmax(QKᵀ/√d_k)V，O(n²)）、context window、LoRA vs QLoRA（低秩 ΔW；QLoRA 加4-bit NF4+paged optimizer）、temperature/top-k/top-p、catastrophic forgetting（PEFT冻结+rehearsal+EWC）、蒸馏、KL divergence（前向 KL mean-seeking、反向 KL mode-seeking，RLHF 中带 β 惩罚）、位置编码（sinusoidal/learned/RoPE/ALiBi 外推权衡）、MHA/MQA/GQA、softmax 数值稳定（减 row max、mask 置 −∞）、cross-entropy=MLE、MoE（稀疏门控 top-k，负载均衡辅助损失防 expert collapse）、CoT/self-consistency、RAG 流程、修复偏见/错误输出（RAG 治幻觉、SFT/DPO/refusal 治行为）、部署挑战（延迟/吞吐/显存/安全）。

**解法**: gist 每题自带一句话答案（见 detail）。反向 KL vs 前向 KL 是 Anthropic/OpenAI 常见追问：RLHF 用反向 KL(π||π_ref) 因 mode-seeking、防止策略把概率质量放到 ref 的低概率区。

来源: <https://gist.github.com/rajesamp/c6a509d2f6be84db6cf5d509eabaa08d>

### Lilian Weng《Policy Gradient Algorithms》——PPO 手推题答案源
*hard · 频率: high（手推 PG/解释 PPO 目标是 RS 面试经典题） · 2018-04*

2018-04-08（持续更新）。覆盖 policy gradient 定理推导、REINFORCE、baseline 降方差、actor-critic、A2C/A3C、off-policy PG 与 importance sampling、TRPO（KL 信赖域）、PPO（clipped surrogate）、DDPG/SAC 等。对应面试题：手推策略梯度公式；为什么减 baseline 不引入偏差；TRPO 与 PPO 的关系（PPO 用 clip 近似 TRPO 的 KL 约束）；importance sampling ratio 的作用与方差问题；GAE 的 λ 如何权衡偏差方差。与 wdndev repo 的'策略梯度手推'、Bojie Li 的'Proximal 含义'等题直接对应。

**解法**: 减 baseline 无偏证明一句话：E_π[∇logπ(a|s)·b(s)]=b(s)·∇Σ_a π(a|s)=b(s)·∇1=0。

来源: <https://lilianweng.github.io/posts/2018-04-08-policy-gradient/>

### qingkeai《LLM Post-Training 全景指南：从RLHF到GRPO再到Agentic RL》——O1/R1式RL与DAPO考点
*hard · 频率: high（R1/GRPO/DAPO 是2025-2026新高频；OpenAI/GDM reasoning 团队面试重点） · 2026-03*

2026-03-25。面试相关要点：Post-Training 认知框架（SFT 教'说什么'、偏好优化教'怎么选'、RL 教'怎么想'）；PPO 需 Policy/Reference/Reward/Value 四模型同时在显存；GRPO 用组内相对排名去掉 critic（DeepSeek-R1 使用）；RLVR 用规则验证器替代学习型 RM，适合数学/代码；DPO 及变体 SimPO/ORPO/KTO 适配不同数据形态；DeepSeek R1-Zero 证明纯 RL（不经 SFT）能涌现推理（self-verification、反思、aha moment），R1 正式版加冷启动 SFT 解决可读性/语言混杂；DAPO 针对 GRPO 长 CoT 训练的熵坍缩：clip-higher（解耦上下裁剪界）、动态采样（过滤全对/全错零梯度组）、token-level loss；Agentic RL 是下一前沿（多步工具调用轨迹上做 RL）。对应面试题：'讲讲 o1/R1 是怎么训出来的''R1-Zero 和 R1 区别''GRPO 训长推理有什么问题、DAPO 怎么修'。

**解法**: R1 训练管线背诵版（我的推断整理）：V3-Base→R1-Zero(纯GRPO+规则奖励:答案对错+格式)→用 R1-Zero 产冷启动 CoT 数据→SFT→推理向 GRPO(加语言一致性奖励)→拒绝采样产80万 SFT 数据(混通用任务)→再 SFT→全场景 RLHF。

来源: <https://qingkeai.online/archives/RLHF-GRPO-AgenticRL>

### CSDN镜像《2026大模型(LLM)面试题库100+题全解析》（知乎原帖403，镜像可读）
*easy · 频率: high（100+题汇总帖，多平台转载） · 2025-12*

2025-12-08 发布，知乎原帖 zhuanlan.zhihu.com/p/1981387722473116577 被403，adg.csdn.net 镜像可访问。抽样题目：题1 Transformer 基础原理（自注意力避免 RNN 序列依赖、并行化）；题7 Scaled Dot-Product vs Multi-Head（QKᵀ/√d_k→softmax；多头并行捕捉语法/语义多维依赖后拼接）；题9 KV Cache 作用（存历史 K/V 免重算，自回归生成 O(n²)→O(n)，2026优化：PagedAttention 分页管理）；题10 主流开源模型（Mixtral 8x22B、Llama3.1 等）；题12 RLHF/DPO 在对齐中的作用（RLHF 用 PPO 优化偏好，DPO 直接从偏好对优化、免 RL 更省算力）；题15 MoE 概念与优势（路由分发、参数多激活少、<50% FLOPs）；题27 端侧部署量化（INT4+KV cache 量化、ONNX Runtime Mobile）；题32 推理加速量化策略（AWQ/GPTQ 到4bit 精度损失<1%，TensorRT-LLM 加速5-10x）。

来源: <https://adg.csdn.net/69708ef2437a6b40336ab4b5.html>

### KalyanKS-NLP/LLM-Interview-Questions-and-Answers-Hub（994星）：115+题带答案，按推理/微调/预训练分册
*medium · 频率: high（994星，英文答案齐全，适合快速刷） · 2025*

结构：Q1-36 Transformer 架构（位置编码、多头/masked attention、LayerNorm、encoder-decoder）；Q37-72 推理（延迟、batching、解码策略、KV cache、量化、投机解码、continuous batching、混合精度、FlashAttention）；Q73-87 提示工程（CoT、few-shot、system prompt、上下文窗口）；Q88-108 微调与适配（instruction tuning、alignment tuning、LoRA/QLoRA、全参微调、PEFT、灾难性遗忘、RLHF 对齐 Q91/Q106）；Q109-115+ 预训练（LM 目标、scaling laws、MoE、模型并行、自监督）。每题在 Interview_QA 目录下有独立 markdown 答案文件。

来源: <https://github.com/KalyanKS-NLP/LLM-Interview-Questions-and-Answers-Hub>

### 掘金《LLMs千面郎君》(km1994)：中文分领域面试题目录（强化学习面/微调面/推理面/显存面）
*medium · 频率: high（'复读机问题''SFT后变傻''显存估算'是中文面经特色高频题） · 2023-09*

2023-09 掘金帖，对应 GitHub km1994/LLMs_interview_notes。分类：基础面（开源模型体系、prefix LM vs causal LM、涌现能力原因、为什么 Decoder-only）；进阶面（复读机问题原因与缓解、LLaMA 系、长上下文）；微调面（全参需要多少卡、SFT 后模型变傻/灾难性遗忘怎么办、指令数据构造、领域适配、二次预训练）；PEFT 面（Adapter/Prefix/Prompt/P-tuning v1v2/LoRA/QLoRA/AdaLoRA 逐个原理对比）；推理面（显存占用估算、int8 vs fp16、生成参数）；强化学习面（奖励模型与基础模型是否一致、三阶段训练流程慢怎么办、偏好数据成本高怎么办——与 wdndev 同源题）；显存问题面（模型多大需要多少显存的估算题）；分布式训练面（DP/PP/TP/框架选型）；评测面；Agent 面。

**解法**: 显存估算口诀（我的推断）：推理≈参数量×2字节(fp16)+KV cache；全参训练(Adam,fp16混合)≈参数量×(2+2+4+4+4)=16字节/参数，7B≈112GB 需 ZeRO 分摊。复读机问题：诱因是重复模式的自我强化+暴露偏差，缓解用 repetition penalty、top-p、DPO 惩罚重复、数据去重。

来源: <https://juejin.cn/post/7280439887966945280>

### AI Papers Academy《GRPO Reinforcement Learning Explained (DeepSeekMath)》——GRPO 数学细节题参考
*hard · 频率: high（GRPO 公式级追问在 2025-2026 reasoning 岗位面试常见） · 2025*

GRPO 原始出处是 DeepSeekMath 论文（后用于 R1）。面试细节题：GRPO 目标函数与 PPO 的逐项对照（ratio clip 保留、advantage 换成组内归一化 (r_i−mean)/std、KL 用 k3 估计直接进 loss 而非折进 reward）；为什么组相对 baseline 能替代 critic（同 prompt 组内 reward 均值即该状态价值的蒙特卡洛估计）；outcome reward vs process reward 的取舍。配套：Yugen.ai《Understanding the Math Behind GRPO》逐符号推导。

**解法**: 常见追问'GRPO 的 std 归一化有什么问题'（我的推断）：引入难度偏差（简单/极难 prompt 组方差小→advantage 被放大），Dr. GRPO 提议去掉 std 除法与长度归一化偏差；'为什么 GRPO 省显存'：少一个与 policy 同尺寸的 critic 及其优化器状态。

来源: <https://aipapersacademy.com/deepseekmath-grpo/>

### Devinterview-io/llms-interview-questions（1k星）：63题基础清单（部分门控）
*easy · 频率: medium · 2025*

README 展示15题（LLM 定义与工作原理、Transformer 架构、LLM vs 统计语言模型、attention 机制、位置编码、预训练与微调意义、长依赖处理、并行化、GPT-4 vs GPT-3、领域适配、应用类），完整63题答案在 Devinterview.io 网站（需注册，属登录墙）。README 可见内容提到 DPO/KTO 正在替代旧 RLHF 管线以提升稳定性、4-bit/2-bit 量化等。价值：适合 screening 轮基础题自查；深度不如 llmgenai 和 wdndev。

来源: <https://github.com/Devinterview-io/llms-interview-questions>

### Sundeep Teki《The Complete Guide to Post-Training LLMs: SFT, RLHF, DPO, GRPO》——面试叙事版答案源
*medium · 频率: medium · 2026*

面向 2026 求职者的后训练综述（作者为 AI 面试教练/前 Amazon Alexa 科学家）：SFT/RLHF/DPO/GRPO 各自机制、何时选用、组合管线。适配面试题：'给一个新任务你会怎么设计后训练管线''SFT 与偏好数据怎么配比''什么时候值得上 RL'。

**解法**: 管线设计答题模板（我的推断）：先定义评测→SFT 建立格式与基础能力（数据多样性>数量）→若有偏好信号且预算小用 DPO→若任务可验证(数学/代码/agent)用 RLVR+GRPO→全程 KL 监控+held-out RM 防 hacking→迭代数据飞轮（拒绝采样回灌 SFT）。

来源: <https://www.sundeepteki.org/advice/the-complete-guide-to-post-training-llms-how-sft-rlhf-dpo-and-grpo-shape-llms>

### jackaduma/awesome_LLMs_interview_notes：中文 LLMs 面试题+参考答案备用库
*medium · 频率: medium · 2023*

与 km1994 千面郎君同源体系的整理仓（另有 naginoa/LLMs_interview_notes 镜像），覆盖基础/进阶/微调/LangChain/PEFT/推理/评测/强化学习/显存/分布式/Agent 各面。作为 wdndev 之外的第二答案交叉验证源。强化学习面题目与 wdndev 1.rlhf相关 基本一致（RM 与基础模型一致性、三阶段流程慢、偏好数据贵、PPO 四模型资源高→RRHF 等）。

来源: <https://github.com/jackaduma/awesome_LLMs_interview_notes>

### dev.to LLM Interview Series #6：RLHF 十问+每问三个follow-up
*medium · 频率: single report（但 follow-up 结构非常贴近真实 research 面试追问方式） · 2025-11*

2025-11-16。10个主问+follow-ups：Q1 RLHF 解决什么问题？追问：为什么 SFT 不够；RLHF 如何影响模型'性格'；偏好不一致怎么办。Q2 完整 RLHF 管线（SFT→RM→PPO）？追问：为什么选 PPO；KL 正则的作用；如何检测 RM 过拟合。Q3 Reward Model 要点（pairwise 比较训练，'可微分、可扩展的人类判断替身'）？追问：如何检测 RM 偏差；pairwise ranking 相比打分的优势；RM 过强的风险。Q4 PPO 优化过程（maximize reward − β·KL(policy||baseline)）？追问：去掉 KL 会怎样；PPO 失败模式；为什么不是别的算法。Q5 常见失败模式（reward hacking、过度优化、mode collapse、偏见放大、false refusal）？追问：如何检测 reward hacking；过优化保护措施；safety/helpfulness 平衡。Q6 RLHF 如何提升安全性？追问：与规则过滤器差异；如何评估；over-refusal 风险。Q7 RLHF 如何减少幻觉？追问：为什么 RLHF 也可能增加幻觉；如何引入事实性信号；与 RAG 配合。Q8 如何设计高质量偏好数据？追问：inter-annotator agreement 怎么测；如何降低不一致；安全覆盖。Q9 RLHF vs RLAIF？追问：RLAIF 风险；评审模型校准；如何选择。Q10 新兴替代方案（DPO、Constitutional AI、RLVR）？追问：DPO 何时更优；CAI 局限；如何组合。

**解法**: 去掉 KL 的后果（我的推断）：策略快速漂移到 RM 分布外→reward hacking、输出退化（乱码/重复/超长）、通用能力遗忘；'为什么 RLHF 可能增加幻觉'：RM 偏好自信流畅的回答，惩罚不确定表达→校准变差（sycophancy 同源）。

来源: <https://dev.to/jackm_345442a09fb53b/llm-interview-series6-rlhf-reinforcement-learning-from-human-feedback-demystified-hi8>

### Chip Huyen ML Interviews Book: 200+ knowledge questions (free online) — math/CS/workflows/algorithms
*medium · 频率: canonical, very widely used by interviewers and candidates · 2021*

Free full-text book with Part II question banks used verbatim by many interviewers: Ch.5 Math (vectors/matrices/dimensionality reduction, probability & statistics problem sets — direct URL https://huyenchip.com/ml-interviews-book/contents/chapter-5.-math.html); Ch.6 CS (algorithms, complexity, data structures); Ch.7 ML workflows (training data creation, objective functions, evaluation metrics — /contents/chapter-7.-machine-learning-workflows.html); Ch.8 ML algorithms (classical ML, deep learning architectures for NLP/CV/RL, training techniques). Over 200 knowledge questions organized by difficulty; pairs with her 27 open-ended systems-design exercises (separate booklet). Part I documents ML interview pipeline/round formats — useful for process calibration at research-oriented orgs.

来源: <https://huyenchip.com/ml-interviews-book/>

## System Design

### AI-framed vs classic system design blend reported in 2025-2026 loops (System Design Handbook questions blog)
*medium · 频率: prep compilation · 2026*

Three archetypes with answer skeletons: (1) recommendation engine for e-commerce/streaming — batch vs real-time personalization, data pipeline + feature store + training service + model registry + inference service, cold start, CTR + drift monitoring; (2) real-time fraud detection — millisecond transaction analysis, Kafka/PubSub streaming ingestion, ensemble models + rules, tight feature-extraction latency budgets, fallbacks, feedback loops from confirmed fraud; (3) LLM-powered chat system — third-party API vs self-hosted decision, prompt orchestration, caching, rate limiting, GPU allocation/autoscaling if self-hosted, RAG, token limits + context-window management, cost monitoring, moderation layers. Site's overall 2026 thesis (echoed by Exponent): 'design a system that serves an LLM' has moved from ML-engineer-only loops into general SWE loops, and evaluation methodology is 'the new system design' — interviewers weight cost, latency, guardrails, monitoring over the architecture diagram.

来源: <https://www.systemdesignhandbook.com/blog/ai-system-design-interview-questions/>

## ML System Design

### Design ChatGPT (Hello Interview problem breakdown)
*hard · 频率: very high (cross-listed on 3+ major prep platforms) · 2025*

Functional requirements: send prompts and receive AI-generated responses; view past conversations and resume with prior context maintained. Non-functional: low latency-to-first-token (called the critical metric), efficient GPU allocation (GPUs = the scarce resource), 200M+ DAU scale. High-level design in two flows: prompt submission + AI response generation; chat history retrieval + context-aware resumption. Deep dives flagged: token streaming optimization and smoothness (SSE, resumability), GPU routing and request scheduling across workers, tier-based access control preventing resource monopolization, cost control for lengthy conversations via summarization/context management. Detailed solutions are premium-gated; free tier shows the structure above. Also appears as 'Design ChatGPT' mock on Exponent and in ByteByteGo's GenAI book — the single most cross-listed LLM SD question.

**解法**: Skeleton: stateless API/chat service + conversation store (NoSQL, conversation_id → messages) + inference fleet with continuous batching; stream via SSE with sequence numbers + resume tokens; context management: sliding window + rolling summary + prefix caching; GPU scheduler: priority queues by tier, preemption of free-tier, KV-cache-aware routing (route follow-up turns to replica holding prefix cache); billing/abuse: token metering at gateway.

来源: <https://www.hellointerview.com/learn/system-design/problem-breakdowns/chatgpt>

### Design ChatGPT (Exponent mock interview walkthrough)
*medium · 频率: very high (canonical practice question) · 2024*

Functional: create/update/view/delete conversations; thumbs up/down message rating feeding model retraining; text input sanitization (profanity/insult detection). Non-functional: login + rate limiting for DDoS, scalability for concurrent users, tolerance for long backend latency. Back-of-envelope: 100-byte avg messages × 200M msgs/day = 20 GB/day, ~7.3 TB/yr, 76 TB/10yrs; NoSQL recommended. Components: Conversation Service (REST, unique conversation/message IDs), sanitization layer, transformer model with top-k/greedy/nucleus sampling, rating system with fraud-detection risk model, thumbs-down triggers retraining review. Also covers SFT + reward model (RLHF) as the improvement loop and multimodal extension.

来源: <https://www.tryexponent.com/blog/design-chatgpt-system-design-mock-interview>

### 11 AI/LLM system design questions with answer frameworks (Educative blog, 2026)
*medium · 频率: prep compilation (topic frequency: RAG/serving themes reported very high elsewhere) · 2026*

(1) 'Design a high-QPS LLM inference service' — edge auth/quota/admission control, routing by tenant/model-class/region, intelligent batching, KV-cache reuse, queue-depth scaling, graceful degradation (shorter outputs, fallback models, cached responses), observability (TTFT, p95, tokens/sec, refusal rates, GPU saturation). (2) Throughput vs latency in LLM serving — TTFT vs time-to-last-token pull in opposite directions; micro-batching with ms windows + early token streaming; backpressure; explicit priority policy. (3) KV caching / batching / speculative decoding trade-offs — failure modes: KV memory explosion, draft-model distribution shift, spike latency. (4) SSE vs WebSockets for token streaming — SSE unidirectional/CDN-friendly; WS bidirectional (tool calls, cancellation); resume tokens, heartbeats, backpressure either way. (5) Prompt-injection defense — immutable system prompts, provenance-tracked context, schema-constrained whitelisted tool calls, output validation, continuous red-teaming. (6) RAG + tool orchestration — orchestrator decides retrieve/call/stop; bound context aggressively; log all decisions for replay/audit. (7) Observability/compliance logging — prompt hashes not raw text, model versions, retrieval metadata, tool traces, redaction, retention. (8) Real-time audio transcription + diarization pipeline — latency budget across ASR/speaker-embedding/clustering stages, jitter buffers, edge inference. (9) Capacity planning — size GPU pools on tokens/sec not requests/sec; pre-warmed buffers; cost-aware degradation. (10) Model/prompt lifecycle — version models, prompts, tools independently; shadow + canary deploys. (11) AI incident response — hallucination spikes, safety bypasses, cost explosions without 500 errors; kill switches, throttles, rollback.

来源: <https://www.educative.io/blog/ai-system-design-interview-questions>

### alirezadir Machine-Learning-Interviews: 9-step MLSD framework + question catalog + 2026 GenAI section
*medium · 频率: very high (23k+ star repo, widely used) · 2026*

9-step framework: problem formulation → offline/online metrics → architectural components → data collection/labeling → feature engineering → model dev + offline eval → prediction service (batch/online/edge) → online testing & deployment (A/B, bandits, canary) → scaling/monitoring/continual training. Question catalog: video/movie/friends/event/game/replacement-product/rental/place recommendation; text/image/video/multimodal search; newsfeed ranking; ads CTR; entity linking; autocomplete; sentiment; language ID; chatbots; QA; OCR; image blurring (Street View); jaywalking detection; ride matching; harmful content & fraud detection; proximity services; delivery-time estimation; healthcare diagnosis. 2026 GenAI additions: RAG-vs-fine-tuning-vs-long-context-vs-tools decision; RAG pipeline (chunking, embeddings, hybrid retrieval + rerank + query rewriting, grounded generation with citations and context budgeting); agentic systems (planning, tool calling, memory, multi-agent orchestration, error recovery); production reliability (rate limiting, retries, idempotency, circuit breakers); guardrails (prompt-injection defense, PII redaction, hallucination checks); evaluation (golden datasets, LLM-as-judge, RAG triad: faithfulness/answer-relevance/context-relevance); cost/latency (token accounting, caching, batching, streaming, model routing). Repo also updated with KV cache, GQA, RoPE, MoE, SFT/DPO/GRPO/RLVR, PEFT topics.

来源: <https://github.com/alirezadir/machine-learning-interviews/blob/main/src/MLSD/ml-system-design.md>

### 100+ real AI-engineer interviews compendium: LLM system design questions (Adil Shamim, 2026)
*medium · 频率: very high (aggregated from 100+ interviews; RAG-for-support marked most frequent) · 2026*

Most frequently reported SD questions: 'Design a RAG system for a customer support chatbot. How do you evaluate it?' (multiple companies, common opener; probes: retrieval strategy, hallucination prevention, golden datasets); 'How would you design an LLM-powered enterprise search system?' (scaling to 10M+ articles with sharding/caching, NDCG/MRR/precision@k, citations/source attribution, search-engine→answer-engine transformation); 'Design a generative AI document-processing pipeline for unstructured data (emails, PDFs, images)' (OCR integration, chunking, document-wide context when pages have prefatory info, sensitive-data protection); 'Your app gets 1M queries/day — how do you optimize cost?' (very common; multi-layer caching, model tiering/routing, prompt compression, quantization/distillation); 'How do you reduce latency in GenAI applications?' (bottleneck identification, PagedAttention, throughput vs latency); 'Walk through a production-ready agent architecture' (orchestrator logic, safe agent loops, termination conditions); 'Design an agent analyzing support tickets, drafting responses, escalating complex issues' (tool use, HITL); 'How do you evaluate a chatbot?'; 'How do you detect and mitigate hallucinations in production?' (very common); 'How do you debug a RAG chatbot giving confident but wrong answers?'; 'Estimate the budget for a RAG pipeline at enterprise scale (300,000 legal contracts)'; safety: 'Your application generates code that gets executed — how do you prevent malicious code generation/execution?'. Also lists classic SD still asked at Amazon/Databricks (GitHub Actions, Slack, feeds, Uber, KV store, rate limiter, Stripe payments, 1B-notifications/day system) and troubleshooting variant 'p95 latency spiked 100ms→2000ms — find bottlenecks fast'.

来源: <https://adilshamim8.medium.com/every-ai-engineer-interview-question-you-need-to-know-in-2026-from-100-real-interviews-b5b7ae4b961a>

### llmgenai/LLMInterviewQuestions: 100+ LLM interview questions in 15 categories (claimed asked at Google/Nvidia/Meta/Microsoft)
*medium · 频率: very high visibility repo; per-question frequency unknown · 2025*

Categories: prompt engineering & LLM basics; RAG; document digitization & chunking; embedding models; internal working of vector databases; advanced search algorithms; LM internals; SFT; preference alignment (RLHF/DPO); evaluation of LLM systems; hallucination control; deployment of LLM; agent-based systems; prompt hacking; misc; case studies. Sample system-design-flavored questions quoted: 'How to increase accuracy and reliability & make answers verifiable in LLM'; 'What are the architecture patterns for customizing LLM with proprietary data?'; 'How do you build production-grade document processing and indexing pipeline?'; 'Why does quantization not decrease the accuracy of LLM?'; 'What are the techniques by which you can optimize the inference of LLM for higher throughput?'; 'How to accelerate response time without attention approximation like GQA?'; 'Explain ReAct prompting with a code example'; 'OpenAI functions vs LangChain agents'; 'How to build production grade RAG system, explain each component in detail'. Free 100 questions in repo; extended set behind their paid course (masteringllm.com).

来源: <https://github.com/llmgenai/LLMInterviewQuestions>

### Vector database deep dive for system design interviews (Hello Interview)
*medium · 频率: high (retrieval layer appears inside most LLM SD questions) · 2025*

When 'design semantic search / RAG retrieval layer' comes up: embeddings 128-1536 dims; the nearest-neighbor-at-scale problem; four ANN index families to know: HNSW, IVF, LSH, Annoy; interview discussion points: filtering + hybrid search (dense + keyword/metadata), insert/update/index-maintenance trade-offs, architecture tiers (start with pgvector/Redis extensions, move to purpose-built vector DBs at scale). Page's guidance: most interviews need when/where judgment more than index internals. Complementary free sources: Weaviate RAG evaluation (RAG triad, NDCG/MRR) and PracHub's rubric — chunking default 512 tokens with 50-100 overlap, recursive chunking over fixed-size, two-stage retrieve-then-rerank with cross-encoder, metadata for access control.

**解法**: My inference for a full 'design vector search' answer: two paths — ingestion (parse → chunk → embed → upsert with metadata, async re-embedding on edits) and query (embed query → ANN top-k with metadata pre/post-filtering → cross-encoder rerank). HNSW for high-recall low-latency in-memory; IVF-PQ for billion-scale memory-constrained; discuss recall@k vs latency vs memory triangle, replication + sharding by namespace, and index rebuild strategy.

来源: <https://www.hellointerview.com/learn/system-design/deep-dives/vector-databases>

### [重点] KV Cache / 推理系统题清单（20 题）
*mixed (easy→hard) · 频率: Inference Engineering / VLLM 合集核心；#492-#495 是 vLLM PagedAttention 系列 · 2026-07*

#376 KV Cache for Efficient Autoregressive Attention [medium] https://www.deep-ml.com/problems/376 | #418 Estimate KV Cache Size from Model Config [medium] https://www.deep-ml.com/problems/418 | #1012 KV Cache Size Estimator MLA vs MHA vs GQA [easy] https://www.deep-ml.com/problems/1012 | #1019 Estimate KV-Cache Memory MHA vs Linear Attention [easy] https://www.deep-ml.com/problems/1019 | #1021 Estimate KV-Cache with GQA and Cross-Layer Sharing [medium] https://www.deep-ml.com/problems/1021 | #416 Compute Attention Memory Traffic and FLOPs [medium] https://www.deep-ml.com/problems/416 | #417 Classify LLM Prefill vs Decode as Compute/Memory-Bound [medium] https://www.deep-ml.com/problems/417 | #435 KV Cache Memory Budget and Eviction Policy [medium] https://www.deep-ml.com/problems/435 | #436 KV Cache Tiered Offloading Simulator [medium] https://www.deep-ml.com/problems/436 | #492 PagedAttention: Block-wise Attention [hard] https://www.deep-ml.com/problems/492 | #493 Virtual Memory System for KV Cache [medium] https://www.deep-ml.com/problems/493 | #494 Copy-on-Write Memory Sharing for LLM Sampling [medium] https://www.deep-ml.com/problems/494 | #495 Analyzing Memory Fragmentation in LLM Serving [easy] https://www.deep-ml.com/problems/495 | #1011 Pre-allocated Sliding KV Cache Update [hard] https://www.deep-ml.com/problems/1011 | #1014 KV Cache Estimator with Sliding Window Attention [medium] https://www.deep-ml.com/problems/1014 | #1023 Build Causal Mask with Position Offsets for Cached Attention [medium] https://www.deep-ml.com/problems/1023 | #1041 Truncate KV Cache for Sliding Window Attention [medium] https://www.deep-ml.com/problems/1041 | #1053 Sliding Window KV Cache Truncation [medium] https://www.deep-ml.com/problems/1053 | #1032 Tokens-per-Second Throughput from Inference Intervals [medium] https://www.deep-ml.com/problems/1032 | #1036 Trim Input Tokens to Fit Model Context Window [medium] https://www.deep-ml.com/problems/1036

**解法**: #418 KV cache 大小=2(K,V)·layers·seq·kv_heads·head_dim·dtype_bytes·batch；GQA/MLA 通过减少 kv_heads / 潜在维压缩显著降内存。#492 PagedAttention：把 KV 分块存非连续物理块，用 block table 映射逻辑→物理，attention 按块遍历——推断解法，对候选人做系统方向很对口。

来源: <https://www.deep-ml.com/problems/492>

### Frontier-lab tribal-knowledge quiz questions (workatafrontierlab.com)
*hard · 频率: site claims these represent recurring frontier-lab interview themes · 2026*

Six verbatim questions billed as what frontier labs (OpenAI/Anthropic/DeepMind-style) test: (1) 'Your 70B model training is at 40% MFU. Walk me through where the other 60% is going.' (2) 'We need to serve this model at 200 tokens/sec per user. What's your KV cache memory budget and how does it constrain batch_size?' (3) 'Why does Chinchilla recommend a different compute-optimal ratio than Kaplan's original scaling laws?' (4) 'Your model's loss spikes at step 50k. Here's the training log. Diagnose it.' (5) 'Explain why speculative decoding gives exact samples from the target distribution, not approximate ones.' (6) 'This operation runs at 2 TFLOPS on an A100 rated for 312 TFLOPS. Is that a problem? Why or why not?' Topic areas: KV cache/gradient checkpointing/OOM debugging, FSDP/ZeRO-3/parallelism, prefill vs decode/PagedAttention, roofline model, numerical stability, scaling laws.

**解法**: My inference: (1) MFU losses: communication (all-gather/reduce-scatter bubbles), pipeline bubbles, data-loading stalls, kernel launch overhead/non-fused ops, recomputation from activation checkpointing, stragglers/restarts. (2) KV bytes/token = 2·n_layers·n_kv_heads·d_head·bytes; multiply by context len × batch — batch_size bounded by (GPU mem − weights − activations)/KV-per-seq; GQA/MQA, quantized KV, paged KV raise the bound. (3) Kaplan under-trained: fixed cosine schedule + smaller models led to params-heavy optimum; Chinchilla shows ~20 tokens/param, scale data with params equally. (4) Loss spike: check for bad data shard, lr/warmup schedule boundary, fp16/bf16 overflow (check grad-norm spike first), optimizer state corruption after restart; mitigations: skip batch, grad clipping, lower lr, switch to bf16. (5) Speculative decoding uses rejection sampling — accept draft token with prob min(1, p_target/p_draft), resample from normalized residual on reject, provably yielding the target distribution. (6) Not necessarily — the op is memory-bound (low arithmetic intensity); compare against roofline: bandwidth-limited ops (elementwise, small GEMV in decode) can't hit peak FLOPS; fix via fusion/batching, not more compute.

来源: <https://www.workatafrontierlab.com/>

### Generative AI system design 9-step framework + 8 worked questions with token economics (System Design Handbook)
*medium · 频率: prep compilation · 2026*

Framework: clarify use case → estimate load & token budget → high-level architecture → RAG deep dive → model interaction patterns (streaming, function calling, routing, sampling) → trade-offs/governance/cost → bottlenecks/observability → security/compliance → wrap-up. Worked questions: 'How would you reduce token costs in an LLM-powered product at scale?' (prompt trimming/templating, semantic prompt caching, route low-risk queries to cheaper models, per-feature token monitoring); 'How do you detect and mitigate ungrounded outputs?' (RAG grounding, classifier/zero-shot flagging, confidence scoring, HITL); 'Design a fast low-latency LLM autocomplete' (edge-hosted small models, 100-200 token completions, stream immediately, warm GPU pools, debounce keystrokes, speculative decoding, <500ms target); 'Protect against prompt injection'; 'Monitor and debug GenAI in production' (tokens/request, P50/P95/P99, RAG hit rate, toxic-output alerts, audit logs by model version); 'Internal documentation Q&A with freshness' (async re-embedding on edits, metadata filtering, snapshot expiry); 'Biggest LLM scaling challenges' (tokens are the scaling unit; GPU throughput bottleneck); 'Fine-tune vs prompt-engineered RAG for domain chatbot' (default RAG, fine-tune later from production logs). Reference numbers: 100K DAU × 10 interactions × 2K tokens = 2B tokens/day; avg 23K tokens/sec, peak 70K/sec (3×); GPT-4 Turbo ~$13K/day; ~40 tok/s per GPT-4 request vs 150-300 tok/s LLaMA-3 on A100; RAG retrieves 3-10 chunks.

来源: <https://www.systemdesignhandbook.com/guides/generative-ai-system-design-interview/>

### LLM System Design: The Complete Guide — prefill/decode physics & KV cache (System Design Handbook)
*medium · 频率: prep compilation · 2026*

Core interview framework for 'design an LLM service' questions: token-based computation replaces request-based reasoning; self-attention is quadratic in sequence length; prefill (parallelizable, compute-bound) vs decode (sequential, memory-bound) split drives latency and cost modeling; KV-cache management is the critical decode-phase component; embeddings/vector DBs as retrieval infrastructure for RAG; variable latency driven by prompt length, batching, and queue dynamics; tensor parallelism and speculative decoding called out as senior-differentiator topics; cost control framed as first-class requirement ('prevent systems from bankrupting organizations through inference expenses').

来源: <https://www.systemdesignhandbook.com/guides/llm-system-design/>

### 19 AI system design interview questions (alexeygrigorev / AI Engineering Field Guide)
*medium · 频率: compilation from community-reported interviews · 2025*

Typical AI SD questions: design an AI chatbot (ChatGPT/Claude chat service); Document Q&A / RAG system; AI co-pilot like GitHub Copilot; Hospital voice assistant (noise, privacy, latency, domain vocabulary); legal contract generation with compliance; AI-powered candidate sourcing; system to process 10K user uploads/month (payslips, IDs, references); doctors auto-sending billing info to insurers from patient notes; fraud detection; ChatGPT cross-conversation memory feature; multi-step agentic workflow (meeting scheduling, code review, email campaigns); content/policy violation detection; unified query engine across email/calendar/docs/chat; Perplexity-style real-time LLM search engine. Near-AI/platform questions: real-time vs batch data updates; ingesting structured/unstructured/event data; scalable image-generation pipeline for millions of users; distributed job queue for 100K+ GPU training jobs with preemption and checkpointing; large-scale model deployment system (serving, GPU scaling, versioning, result caching). Repo positions 'AI system design' as a distinct interview category from classic MLSD. Companion files in same repo: 01-theory.md, 02-coding.md, 03-project-deep-dive.md, 05-behavioral.md, 06-home-assignments.md.

来源: <https://github.com/alexeygrigorev/ai-engineering-field-guide/blob/main/interview/questions/04-ai-system-design.md>

### Chip Huyen's 27 open-ended ML systems design exercises (free online)
*medium · 频率: classic canon; individual questions widely reused by interviewers · 2019*

Full list of 27 questions, e.g.: Duolingo story-difficulty measurement and difficulty editing; credit-card fraud detection from labeled purchases; replacement-item recommendation for out-of-stock e-commerce; Twitter who-to-follow + cold start + limitations of data-driven recsys; Google related-searches generation; Google Images-style image retrieval; trending hashtags; Quora answer ranking + compute cost; Airbnb top-10 rental search; texting autocompletion; StackOverflow similar-questions dedup; Lyft/Uber pool rider matching; estimate % of real high schools listed on Facebook + deploy invalid-school detection at scale; trigger-word ('activate') detection in 10s audio; Netflix-clone watch-abandonment prediction (tired of show vs taking a break); Facebook birthday estimation without direct data; language identification; Zillow house-price prediction + city-level investment decision; iPhone next-app prediction at 90% accuracy; nickname→real-name mapping (Pete/Andy/Nick/Rob); minimize e-commerce time-to-purchase; hotel-booking chatbot; extractive QA over large document collections; 'jaguar' animal-vs-car word sense disambiguation; portfolio stock-swap decision; triangle/circle/square recognizer; CIFAR-10 open-set recognition (is image in the 10 classes or not). Companion to her ML Interviews Book (200+ knowledge questions at huyenchip.com/ml-interviews-book/).

来源: <https://huyenchip.com/machine-learning-systems-design/exercises.html>

### Exponent public ML-engineer system design question bank with company tags
*medium · 频率: company-tag counts shown per question (e.g. 'Anthropic + 7 others') · 2026*

Publicly visible question titles + company attributions: 'Design an inference batching system for a single GPU' (Anthropic +7 others); 'Design an ML experiment tracking and analysis platform' (Google); 'Design an evaluation framework for ads ranking' (Meta +2); 'Design a next word prediction system' (Meta); 'Design an end-to-end ML solution to detect ads selling weapons' (Meta +2); 'Design TikTok' (Meta, Google +4); 'What metrics would you track to evaluate the performance of your ML pipeline?' (Perplexity AI); 'Design a product recommendation system' (Meta, Reddit, Pinterest +3); 'Implement a streaming database with given constraints' (Anthropic); 'Design a denoising system for sounds' (Google); 'Design an agentic AI system that can autonomously adapt to new tasks' (Anthropic); 'Design a language detection system' (Google); 'Design a system to detect bot players' (Roblox); 'Design a personalized news ranking system' (Meta); 'Design a fake news detection system' (Meta +1); 'Design Facebook Marketplace' (Meta); 'Design a monitoring system for TikTok' (TikTok). Full bank claims 150+ MLSD practice questions (rest behind login).

来源: <https://www.tryexponent.com/questions?role=ml-engineer&type=system-design>

### Exponent 6-step MLSD framework + example questions by category (2026 guide)
*medium · 频率: prep compilation with company attributions · 2026*

Framework (45-min budget): define problem (8m) → data pipeline (8m) → model architecture (8m) → train & evaluate (8m) → deploy/serve/monitor (8m) → wrap-up (5m). Example questions: 'Design a product recommendation system' (Meta, Pinterest); 'Design Netflix Top Picks'; 'Recommend similar artists on Spotify'; 'Design an evaluation framework for ads ranking' (Meta); 'Design YouTube Search'; 'Design a personalized news ranking system'; 'Detect the language of a text input'; 'Design a fake news detection system'; 'Design an automated comment moderation system'; 'Design a spam detection system on Pinterest'; 'Design a fraud-detection system for Stripe'; 'Design visual search for Pinterest'; 'Design an automatic recycling bin'; 'Design a stock-prediction system from Reddit' (JP Morgan); 'Design YouTube advertising'; 'Design TikTok For You page'; 'Design a monitoring system for TikTok'. Common mistakes: rushing past requirements, hunting for the 'right' answer instead of justifying trade-offs, defaulting to SOTA over practical v1, skipping evaluation/validation.

来源: <https://www.tryexponent.com/blog/machine-learning-system-design-interview-guide>

### 21 LLM system design Q&A flashcard set (Dr. Sanjay Kumar, Medium)
*easy · 频率: prep compilation · 2025*

Questions with answer sketches: what is LLM system design; explain RAG's role; optimize inference for low latency + high throughput (quantization, caching, batching, distillation, GPU/TPU); NFRs for LLM systems (<1s latency, autoscaling, fallbacks, bias/safety); design a customer-support chatbot case study (React + RAG + vector DB + LangChain + FastAPI + quantized model + Redis + monitoring); handle hallucinations/bias; cloud vs edge deployment; monitoring/eval tools (Prometheus/Grafana, toxicity APIs, A/B); cost-performance balance (tiered models, cold starts, spot instances); prompt engineering for consistency; design rate limiting for LLM APIs (token bucket, priority queues for premium users); quantization trade-offs (fp32→int8, ~1-2% accuracy loss); zero-downtime LLM version rollout (blue-green, shadow testing, canary); design a multi-agent LLM system (router classifies → specialized models, orchestrator, JSON passing, fallback logic); reduce GPU costs (distillation, sparse MoE, spot, caching); feature prioritization for a support bot; LLM project ROI; ethical risks; handling incorrect legal advice (keyword routing to humans, disclaimers, audits); design 'Chat with PDF' (extract → chunk → embed at upload → RAG → cache); scale an LLM app 100→1M users (stateless APIs + K8s, CDN, read replicas, sharding, autoscaling).

来源: <https://skphd.medium.com/llm-system-design-interview-questions-and-answers-2a7a16212492>

### Book: 'Generative AI System Design Interview' (Ali Aminian & Hao Sheng, ByteByteGo, Nov 2024) — canonical 10-question set
*medium · 频率: the de-facto standard prep books for MLSD/GenAI SD rounds · 2024-11*

Chapter/question list: (1) Introduction + 7-step GenAI SD framework; (2) Gmail Smart Compose; (3) Google Translate; (4) ChatGPT: personal assistant chatbot; (5) Image captioning; (6) Retrieval-Augmented Generation; (7) Realistic face generation; (8) High-resolution image synthesis; (9) Text-to-image generation; (10) Personalized headshot generation; (11) Text-to-video generation. 280+ diagrams; covers training + serving architecture and trade-offs per system. Companion to Alex Xu/Aminian 'Machine Learning System Design Interview' book whose 10 problems (visual search; Street View blurring; YouTube video search; harmful content detection; video recommendation; Eventbrite event recsys; ad click prediction; Airbnb similar listings; personalized news feed; People You May Know) are summarized free in the junfanz1 notes repo: https://github.com/junfanz1/AI-LLM-ML-CS-Quant-Review/blob/main/System%20Design/ML%20System%20Design%20Interview.md

来源: <https://www.amazon.com/Generative-AI-System-Design-Interview/dp/1736049143>

### Educative 'Grokking the Generative AI System Design' course: SCALED framework + case-study list (free TOC + 14 free lessons)
*medium · 频率: prep course (widely referenced) · 2026*

Course structure: fundamentals (evaluation metrics for GenAI, parallelism in GenAI models, inference optimization, RAG vs fine-tuning breakout w/ mock interview); back-of-the-envelope calculations for LLM training and deployment; 6-step 'SCALED' framework for GenAI SD problems; design case studies: text-to-text conversational AI (ChatGPT mock interview), text-to-image (DALL·E mock), text-to-speech (ElevenLabs mock), text-to-video (Sora mock), image captioning, ASR, and RAG system architecture. 2026 edition added modules: LLM serving infrastructure, RAG architectures, agentic orchestration platforms. 14 lessons free; mocks premium.

来源: <https://www.educative.io/courses/generative-ai-system-design>

### 'Design a conversational AI agent for our enterprise knowledge base' + RAG scoring rubric (PracHub 2026)
*medium · 频率: claimed recurring across GenAI loops · 2026*

Called 'a recurring prompt in GenAI interview loops.' Strong answer walks a 4-stage RAG pipeline stage by stage naming trade-offs: (1) document ingestion & chunking (parsing strategy, metadata capture); (2) embedding layer (model selection e.g. text-embedding-3-large vs open-source BGE for cost, hybrid search support); (3) retrieval & re-ranking (vector search + cross-encoder); (4) generation & prompt orchestration (streaming output). Evaluation rubric dimensions: framing (state the probabilistic nature; clarify latency/sensitivity/scale), retrieval depth (retrieve-then-rerank, chunking trade-offs: small chunks lack context, large chunks dilute embedding semantics), cost awareness (tokens as budget, semantic caching, model routing), quality/safety (evals, citations, guardrails, feedback loops), trade-off leadership (proactively surface precision-latency-cost tensions). Variants: cost-optimized / latency-optimized / accuracy-optimized RAG designs.

来源: <https://prachub.com/resources/genai-llm-system-design-interview-guide-2026>

### Hao Hoang 'Top 25 LLM System Design Interview Questions' (free-PDF workbook; content engagement/paywall-gated)
*medium · 频率: 795 reactions/117 comments on LinkedIn; widely shared · 2025-11*

50+ page workbook where each chapter = interview question + the common wrong answer + technical breakdown + one research paper to cite. Topics confirmed from LinkedIn preview: the tokenizer trap in domain-specific training (tokenization mismatch as production failure mode); speculative decoding for lossless acceleration; KV-cache bottlenecks under concurrent inference; the 'alignment tax' in RLHF (alignment-induced latency/quality trade-offs); scaling laws & compute-optimality. Full 25-question list not retrievable (Substack paywall; LinkedIn post requires engagement to get PDF; archive.org unreachable from this environment). Companion paywalled post: 'Top 25 ML System Design Interview Questions' (2026-01-01, same substack). His free 'Top 50 LLM Interview Questions' (May 2025) knowledge-question set is mirrored openly at https://gist.github.com/rajesamp/c6a509d2f6be84db6cf5d509eabaa08d

来源: <https://www.linkedin.com/posts/hoang-van-hao_top-25-llms-system-design-interview-questions-activity-7396785599728422913-EedS>
