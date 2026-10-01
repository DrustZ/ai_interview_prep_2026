# ml_sys_prep · ML System Design 冲刺（唯一入口）

⏱ 本文件 3 分钟读完 ｜ 面向 2026-07 的 Exa / OpenAI pretraining / Mirendil / Bridgewater / Decagon 等面试

## 🔴 入口：[`NOW.md`](NOW.md)

只有一屏：**下一场是谁、几点、今天只做什么**。每场面试后立刻更新。
（原来写在这里的「当前最紧」和 `00_study_plan.md` 的两天日历都过期过 ——
静态日历注定过期，所以换成按面试驱动的一屏。）

**评分门槛**：`python mock.py status` —— 40 分 rubric 现在是**机器判的**，
连续两次「≥32/40 且无单项<3 且三个追问都稳」才算 ready。

## 怎么用（只有一条规则）

**打开 [00_study_plan.md](00_study_plan.md)，看当天那一节，照做。** 其余 14 个文件已全部编排进日程，不需要自己另外浏览。

本目录 9600+ 行。**通读是错误用法**——日程已经按 ⭐⭐⭐ 挑好了每篇要读的节。

## 这套材料解决什么

不是「记住某个模型」，而是面对陌生题时能稳定做出一组可解释的工程判断：**任务到底是什么、数据从哪里来、标签是否可信、数据不够怎么办、为什么选这个模型、如何评估、怎样以合理成本上线并持续学习。**

> 默认答题主线：**Problem → Metrics → Data → Model/Objectives → Evaluation → Serving → Feedback loop**

**2026-07-29 新增 §15–19 五个 frontier-lab 题型的 case study**（共 3588 行）。
这五题和传统的推荐/搜索 MLSD 不同，是 OpenAI / Anthropic / Reflection 这类实验室的常考题型，
而且**全部命中你在 Reflection 的真实经历**（RL 数据、合成数据、批量推理基础设施），
写作时已把你的经历直接编进对位素材一节。

针对性说明：你现有的 [`../online_resource/question-bank/theory-and-mlsd.md`](../online_resource/question-bank/theory-and-mlsd.md) 已经覆盖 **架构轴**（serving / RAG / KV cache / 成本架构）。本目录补的是正交的 **数据轴**——也正是你两场面试被问倒的地方（code review 用什么数据+什么 reward；OCR signature 怎么收各种场景数据）。

## 先看 [`INDEX.md`](INDEX.md)

12,000 行里，**16 个核心概念各自散落在 5–18 个文件**。
`INDEX.md` 给每个概念指定唯一的「正本」—— 想学一个概念只读正本，
其他文件出现它只是在自己的语境里用一下。

它同时标出了一个已知问题：**04/05/06/07 四篇 = 全库 32%，
但一手数字密度只有 0.15 条/百行**（21/22/23 是 6.3/4.0/8.7）。
那四篇是早期的散文版，待重写。

## 怎么用这些文件：分两类，别混

| 类别 | 是什么 | 怎么用 |
|---|---|---|
| **必须内化**（能闭卷讲出） | 判断、坑、反直觉结论 | **`python drill.py`** —— 36 道题覆盖 7 个 topic。**不要重读** |
| **查阅**（用到再翻） | 一手数字、公司情报、完整推导、代码 | 需要引用时打开，或面试前扫速记那一节 |

大文件（04–07、14–19、21–22 共约 10000 行）**全部属于「查阅」**。
它们第一次读是为了建立概念；之后每次复习都该是 drill。
**通读第二遍是这套材料里性价比最低的动作。**

## 文件地图

| 文件 | 行数 | 解决的问题 |
|---|---|---|
| [00_study_plan.md](00_study_plan.md) | 主线 | **两天冲刺日历**、4 小时急救版、面试前 30 分钟 |
| [01_answer_framework.md](01_answer_framework.md) | 188 | 45–60 分钟通用答题框架与白板顺序（**唯一建议逐字读完的文件**） |
| [02_data_and_labels.md](02_data_and_labels.md) | 199 | 数据来源、标签合同、泄漏、长尾与数据短缺阶梯 |
| [03_model_training_reward.md](03_model_training_reward.md) | 188 | baseline ladder、模型选择、loss、SFT/preference/RL、reward 设计与防 hacking |
| [04_case_code_review_llm.md](04_case_code_review_llm.md) | 955 | 如何训练并上线 code-review LLM |
| [05_case_ocr_signature.md](05_case_ocr_signature.md) | 784 | OCR、签名检测/识别/验真及场景数据收集 |
| [06_search_post_training.md](06_search_post_training.md) | 906 | Exa 类搜索：retriever / reranker / answerer / search agent 的 post-training |
| [07_pretraining_data.md](07_pretraining_data.md) | 1207 | pre-training 数据获取、过滤、去重、配比、污染与治理 |
| [08_evaluation_production.md](08_evaluation_production.md) | 209 | offline→online eval、阈值、成本、部署、监控与反馈闭环 |
| [09_question_bank.md](09_question_bank.md) | 300+ | 60+ 题库与追问锚点，**§I 是 1p3a 真题实录**（带来源与日期） |
| [10_cheatsheet.md](10_cheatsheet.md) | 105 | 面试前一页速查 |
| [11_mock_interviews.md](11_mock_interviews.md) | 117 | 三套 mock 流程、评分 rubric 和复盘模板 |
| [12_personal_bridge.md](12_personal_bridge.md) | 119 | 把 HCI / wearable / 文本输入 / agentic LLM 经验诚实迁移到 MLSD |
| [13_company_cards.md](13_company_cards.md) | — | 五家公司速记卡（面试前 5 分钟看） |
| [14_case_customer_service_agent.md](14_case_customer_service_agent.md) | 300+ | AI 客服 agent 的**数据轴**：resolution 标签、多租户冷启动、AOP、reward hacking |
| [15_case_eval_pipeline.md](15_case_eval_pipeline.md) | 740 | **ChatGPT 级评测流水线**：judge 偏差与验证、benchmark 污染、分层报告、PPI 采样 |
| [16_case_rl_data_pipeline.md](16_case_rl_data_pipeline.md) | 828 | **RL post-training 数据流水线** ⭐ 最对口你的经历：难度筛选、可验证性、reward hacking 检测 |
| [17_case_synthetic_data.md](17_case_synthetic_data.md) | 684 | **合成数据生成**：质量闸门、多样性、模型坍塌、什么时候不该合成 |
| [18_case_distributed_inference.md](18_case_distributed_inference.md) | 646 | **分布式推理**：在线 serving vs 离线批量的分叉、抢占恢复、成本模型 |
| [19_case_agent_benchmark.md](19_case_agent_benchmark.md) | 690 | **Agent benchmark**：过程 vs 结果、pass^k、环境可复现、污染与漂移 |
| **[20_case_exa_agentic_search.md](20_case_exa_agentic_search.md)** | 500+ | 🔴 **Exa 第二轮（systems design）专用**：Exa 全栈一手事实卡、snippet generation / reranking / model alignment 三套完整设计、延迟与算力算术 |
| **[21_swe_agent_data.md](21_swe_agent_data.md)** | 600+ | 🆕 **SWE agent 训练数据**：从 GitHub 爬 → 选仓库 → 挖 PR → 搭环境 → **F2P/P2P 执行验证** → 合成 bug → 去重去污染 → 造 pair。配 [labs/swe_data/](labs/swe_data/) 可跑代码 |
| **[22_code_review_agent_data.md](22_code_review_agent_data.md)** | 400+ | 🆕 **Code review agent 训练数据**：**没有 oracle** 怎么办 → 从历史制造可验证性（采纳信号 + SZZ）→ 质量把关与**信号校准** → 正负样本（含「未评论行」陷阱）→ **不对称 reward**。配 [labs/cr_data/](labs/cr_data/) 可跑代码 |
| **[23_agent_rollout_inference.md](23_agent_rollout_inference.md)** | 速查卡 | 🆕 **Agent rollout 的推理配置与 KV cache**：prefill 是 O(T²)、什么会静默打掉 prefix cache、prompt 布局、cache-aware 路由、按 repo 分组调度。配 `labs/swe_data/rollout_cost.py` |
| [labs/](labs/) | — | 五个可跑 lab（去重与质量分类 / reward 设计 / 检索负例 / **swe_data** / **cr_data**）+ **[exa_drills/](labs/exa_drills/) Exa 技术轮冷写题包（5 题，含实考的流式分位数）** |

## 与你现有材料的边界

- **架构轴**（serving、RAG、KV cache、成本）→ [`../online_resource/question-bank/theory-and-mlsd.md`](../online_resource/question-bank/theory-and-mlsd.md)
- **agent runtime**（tool protocol、durable execution、多智能体）→ [`../agentic_prep/agentic2/`](../agentic_prep/agentic2/README.md)
- **ML 理论与手写题**（attention、GRPO、采样、KV cache 手写）→ [`../online_resource/core-ml.md`](../online_resource/core-ml.md) 与 [`../online_resource/drills/`](../online_resource/drills/)
- **pretraining data 的实操场** → [`../../cs336/assignment4-data/`](../../cs336/assignment4-data/)（handout PDF 里就是 07 描述的那条 funnel：Common Crawl → 质量分类器 → dedup → 毒性过滤 → leaderboard。Day 2 若时间充裕，跑一遍比读十遍强）
- **post-training 实操场** → [`../../cs336/assignment5-alignment/`](../../cs336/assignment5-alignment/)

若题目是 RAG/search：先在这里回答 retrieval / training / eval，再用 agentic2 补权限、工具调用与状态恢复。

## 诚实性约束（重要）

这里的案例是**面试设计方案**，不是伪装成做过的项目。没有亲自做过时，用「我会先…」「我会用实验验证…」，不要说成已经取得过的结果。可用的迁移句式见 [12_personal_bridge.md](12_personal_bridge.md) §3。

## 每次练习必须交付的 8 行

```text
1. User/action: 谁基于预测做什么决定？
2. Unit/label: 一个样本是什么，标签何时可得？
3. Success: 一个主指标 + 两个 guardrail。
4. Data: 来源、split、最大 bias/leakage。
5. Baseline: 最便宜的可行系统。
6. Model/objective: 为什么匹配输出结构与数据规模？
7. Production: p95/QPS/cost budget 与降级路径。
8. Loop: 如何观测错误、获得新标签、决定是否重训？
```

如果这 8 行说不清，继续堆模型名通常不会让答案变好。

## 外部资源 Top 10（只在错题暴露弱点时打开）

各案例文件末尾另有本主题的延伸阅读；下表是跨主题的。

| # | 资料 | 分钟 | 对口 |
|---|---|---|---|
| 1 | [Hello Interview · ML System Design in a Hurry](https://www.hellointerview.com/learn/ml-system-design/in-a-hurry/delivery) | 60 | 2026 最新交付框架，免费部分够用 |
| 2 | [alirezadir · Machine-Learning-Interviews（9-step MLSD）](https://github.com/alirezadir/Machine-Learning-Interviews) | 40 | 数据采集/标注章节最全 |
| 3 | **本地** [`cs336/assignment4-data`](../../cs336/assignment4-data/) handout | 90 | pretraining data 最快上手路径 |
| 4 | [FineWeb 技术报告](https://huggingface.co/spaces/HuggingFaceFW/blogpost-fineweb-v1) | 60 | 07 那条 funnel 的「标准答案」，含全局 vs 分片去重的反直觉结论 |
| 5 | [DCLM / DataComp-LM](https://arxiv.org/abs/2406.11794) | 40 | model-based filtering 是最大杠杆 |
| 6 | [SWE-RL](https://arxiv.org/abs/2502.18449) | 25 | 从 PR 历史挖可验证信号，直接对口 04 |
| 7 | [Rubrics as Rewards](https://openreview.net/forum?id=c1bTcrDmt4) | 20 | 主观任务怎么做成可 RL 的 reward，对口 04 §7 |
| 8 | [Search-R1](https://arxiv.org/abs/2503.09516) | 20 | 多轮 search+reason RL，retrieved-token masking |
| 9 | [DeepRetrieval](https://arxiv.org/abs/2503.00223) | 20 | 用检索指标直接当 reward 训 query rewriter |
| 10 | [Exa 官方研究博客](https://exa.ai/research) | 40 | Exa 面试前必读，见 [13 · 公司卡](13_company_cards.md) |
