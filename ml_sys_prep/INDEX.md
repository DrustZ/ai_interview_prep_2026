# 概念索引：每个概念只有一个「正本」

> 这个目录 12,000 行。实测有 16 个核心概念**各自散落在 5–18 个文件里** ——
> 所以你想找一件事的时候找不到，而且不知道哪个版本是最新的。
>
> **这份表给每个概念指定唯一的正本。** 其他文件里出现同一个概念时，
> 只是在它自己的语境里用一下，不是在重新讲。**要学一个概念，去它的正本。**

---

## 用法

```
想学某个概念        → 查下表，只读「正本」那一列
想练某个概念        → python drill.py --topic <对应 topic>
想在某个 case 里用   → 那个 case 文件会引用正本，不重复解释
```

---

## 核心概念 → 正本

### 数据与标签

| 概念 | 正本 | 一句话 |
|---|---|---|
| **click ≠ relevance / 隐式反馈偏差** | [`06 §五`](06_search_post_training.md) | 曝光偏差、位置偏差；点击是行为不是标签 |
| **未标注 ≠ 负样本（PU learning）** | [`22 §5`](22_code_review_agent_data.md) | 「没人评论的行」里有真 bug —— 有实测证明 |
| **hard negative 的陷阱** | [`06 §六`](06_search_post_training.md) + 实测在 [`../projects/decagon_finetune/levels/level7_retrieval_first/`](../projects/decagon_finetune/) | top-k 里混着未标注的相关项；**必须有样本数对齐的对照组** |
| **近重复去重（MinHash/LSH）** | [`21 §7`](21_swe_agent_data.md) | 归一化 → shingle → MinHash；**词袋抓不到改写** |
| **污染 / decontamination** | [`07 §污染`](07_pretraining_data.md)；SWE 场景看 [`21 §7`](21_swe_agent_data.md) | 三层：整仓排除 / 精确匹配 / 近重复 + 时间维度 |
| **可验证性从哪来（没有 oracle 时）** | [`22 §3`](22_code_review_agent_data.md) | 采纳信号 + SZZ；两家生产系统独立收敛 |

### 训练

| 概念 | 正本 | 一句话 |
|---|---|---|
| **SFT → DPO → RL 各解决什么** | [`03 §训练路线`](03_model_training_reward.md) | 格式→SFT；相对偏好→DPO；多步且 verifier 可靠→RL |
| **什么时候不该上 RL** | [`21 §8`](21_swe_agent_data.md) | 基线成功率为 0 时 vanilla RL 完全没信号 |
| **pass@k 难度筛选** | [`16 §难度`](16_case_rl_data_pipeline.md) | pass@k ∈ {0,1} 组内优势全 0，白烧算力 |
| **GRPO / Dr. GRPO 的两处修正** | [`../projects/decagon_finetune/levels/level4_grpo/`](../projects/decagon_finetune/) | 去 length norm（长度偏置）、去 std norm（难度偏置） |
| **reward 分层与硬闸门** | [`22 §6`](22_code_review_agent_data.md) | 确定性 → 历史证据 → LLM judge；硬闸门在最前 |
| **reward hacking：检测与防** | [`16`](16_case_rl_data_pipeline.md) 通论；code review 形态看 [`22 §6`](22_code_review_agent_data.md) | 高分轨迹人工抽检 + 分布漂移 + 结构不变量 |
| **合成数据什么时候不该用** | [`17`](17_case_synthetic_data.md) | 质量闸门、多样性、模型坍塌 |

### 评测

| 概念 | 正本 | 一句话 |
|---|---|---|
| **judge 必须用人工标注校准** | [`15`](15_case_eval_pipeline.md) 通论；实操示范在 [`../projects/onsite_prep/projectA_grader_first/`](../projects/onsite_prep/) | AUROC + bootstrap CI；阈值校准集选、验证集报 |
| **baseline 阶梯** | [`01 §baseline`](01_answer_framework.md) | 从最蠢的开始；没有 baseline 的改进不算改进 |
| **对照组纪律** | [`21 §7`](21_swe_agent_data.md) + 实测在 [`../projects/decagon_finetune/`](../projects/decagon_finetune/) | 样本数/预算对齐；配对 bootstrap 报差值 CI |
| **评测器与被评物同源** | [`15`](15_case_eval_pipeline.md) | 用 BM25 造标签又用 BM25 评测 → 收益被抹掉 |
| **切片报告 / slice** | [`08`](08_evaluation_production.md) | 均值达标而长尾退化是最常见的事故 |
| **置信区间 / bootstrap** | [`15`](15_case_eval_pipeline.md) | 配对比较报差值的 CI，不是两个均值各自的 CI |
| **过程 vs 结果奖励、pass^k** | [`19`](19_case_agent_benchmark.md) | agent 评测特有 |

### 系统与成本

| 概念 | 正本 | 一句话 |
|---|---|---|
| **cascade / 级联** | [`08`](08_evaluation_production.md) 通论；检索侧看 [`20 §4.2`](20_case_exa_agentic_search.md) | 便宜的先筛，贵的只跑 shortlist |
| **prefix cache / KV cache** | [`23`](23_agent_rollout_inference.md) | agent rollout 的 prefill 是 O(T²)，差 23 倍 |
| **在线 serving vs 离线批量** | [`18`](18_case_distributed_inference.md) 通论；rollout 场景看 [`23 §7`](23_agent_rollout_inference.md) | 目标从 p99 延迟变成吞吐/美元 |
| **算力估算 `FLOPs ≈ 2·params·tokens`** | [`20 §4.3`](20_case_exa_agentic_search.md) | 候选数是算出来的不是拍的 |

---

## 文件分层：先知道每个文件是干什么的

| 层 | 文件 | 怎么用 |
|---|---|---|
| **入口** | [`NOW.md`](NOW.md) | 下一场是谁、今天做什么。**每天只看这个** |
| **工具** | `drill.py` `mock.py` | 内化靠这两个，不靠重读 |
| **索引** | 本文件、[`09_question_bank.md`](09_question_bank.md)、[`13_company_cards.md`](13_company_cards.md) | 查 |
| **通用框架** | `01` `02` `03` `08` `10` `11` `12` | 第一次读，之后 drill |
| **旧版 case（散文，待重写）** | ⚠️ `05` `06` `07`（`04` 已重写 ✅） | 见下方「已知问题」 |
| **新版 case（有实测数字 + 可跑代码）** | `14`–`23` | 每篇配 lab 或 project |
| **公司专用** | [`20`](20_case_exa_agentic_search.md) Exa；`../projects/` 下各家 | 面试前看 |

---

## ⚠️ 已知问题：04/05/06/07 需要重写

实测：这四篇 **3,882 行 = 全库 32%**，但**一手数字密度约 0.15 条/百行**
（作为对比：21/22/23 分别是 6.3 / 4.0 / 8.7）。

它们是早期写的，特点是：

- 大段散文和关键词表，**没有可跑代码、没有实测数字**
- 讲「应该怎么想」，但没有「跑一遍看看是不是这样」
- 04 和 [`22`](22_code_review_agent_data.md) 是同一个 topic 的两个版本

**当前的正确用法**：

| 文件 | 还有什么独有价值 | 重叠的部分去哪读 |
|---|---|---|
| [`04`](04_case_code_review_llm.md) ✅ | **已重写**（974→569 行）。系统与产品侧：架构、reward 的具体形状、reward hacking 表、成本、灰度 | 数据侧的实测数字 → [`22`](22_code_review_agent_data.md) |
| [`05`](05_case_ocr_signature.md) | OCR/签名的场景数据采集矩阵（独一份） | — |
| [`06`](06_search_post_training.md) | click bias、hard negative、四层 eval 的完整讨论 | Exa 相关的一手事实 → [`20`](20_case_exa_agentic_search.md) |
| [`07`](07_pretraining_data.md) | pretraining data funnel 十一步（独一份） | — |

**⚠️ 我先前的诊断要更正**：我用「一手数字/论文引用密度」当代理指标，
得出「这四篇内容水」的结论 —— **那个指标测错了东西**。
实际读进去发现它们内容很扎实（gated reward、severity 膨胀惩罚、
10 行 reward hacking 表、bug 注入的验证链），**比我从零写的好**。
问题是**呈现太压缩**（一堆 keyword，读完还是不知道），不是内容水。
所以重写的正确做法是**保住内容、换掉呈现**，不是推倒重来。

04 已按这个方式重写完（974→569 行，9 项关键内容逐条核对保留）。
**剩余优先级**：06（和 20 重叠）> 05 > 07。
但**在有面试日程的时候，重写它们的优先级低于练 drill**。

---

## 这份索引怎么维护

新增一个概念时问自己：**它的正本在哪？**

- 已有正本 → 在新文件里**引用**，不重新解释
- 没有正本 → 在最合适的文件里写正本，然后**在这张表里登记**

不登记的结果就是现在这样：一个概念散落 18 个文件，谁也不知道哪个是最新的。
