# 01 · ML System Design 通用答题框架

## 90 秒开场

> 我先把产品目标转成一个明确的 prediction/decision contract，并确定主指标、风险和 latency/cost 约束。然后定义样本与标签、数据来源、时间或实体级 split 和最便宜的 baseline；在这些约束下选择模型与训练目标。最后我会分别覆盖 offline/slice evaluation、serving capacity、shadow/canary rollout，以及如何从生产反馈得到无偏的新标签。模型选择会放在数据与目标之后。

这段话告诉 interviewer：你设计的是一个可运营的学习系统，不是一张“数据 → 大模型 → API”的图。

## 45–60 分钟时间盒

| 时间 | 阶段 | 必须回答 | 白板产物 |
|---|---|---|---|
| 0–6 min | Problem framing | 用户、decision、prediction unit、错误代价、SLO | contract + assumptions |
| 6–11 min | Metrics | offline/online 主指标与 guardrails | metric table |
| 11–21 min | Data/labels | 来源、标签定义/延迟、bias、split、隐私 | data contract |
| 21–31 min | Baseline/model | baseline ladder、特征/上下文、objective | v1 + v2 |
| 31–39 min | Training/eval | sampling、hard cases、calibration、slices | experiment matrix |
| 39–49 min | Serving/scale | latency/QPS/cost、cascade、fallback | serving path |
| 49–55 min | Monitoring/loop | drift、delayed labels、HITL、retrain gate | feedback loop |
| 55–60 min | Trade-offs | 最大风险、替代方案、下一实验 | 3 个 trade-off |

## Step 1：先写 Prediction / Decision Contract

不要从“用 transformer”开始。先写：

```text
Given X available at time t,
predict Y over horizon H,
so actor A can take action D,
under latency L, cost C, and risk constraints R.
```

必须澄清：

1. **用户与动作**：输出只是建议，还是自动拒绝/批准/执行？
2. **样本单位**：一张图、一段文本、一个 query-document pair、一次 PR，还是一段 trajectory？
3. **输出结构**：class、score、ranking、sequence、embedding、patch、tool action？
4. **标签窗口**：即时可见，还是 7/30 天后才知道？
5. **错误不对称**：FP 和 FN 哪个更贵？是否允许 abstain？
6. **约束**：QPS、p95/p99、cost/request、隐私、region、可解释性、硬件。

例：签名验真不是“识别图片”。更精确的 contract 是：

```text
Given a document image and 1–5 enrolled reference signatures,
estimate whether the questioned signature is genuine,
so a risk engine can auto-accept low-risk cases, reject only extreme cases,
and send the uncertain band to a trained reviewer within 2 seconds.
```

## Step 2：指标先于模型

至少给四层指标：

| 层 | 例子 | 作用 |
|---|---|---|
| Product outcome | 用户接受率、发现的真实 bug、欺诈损失、任务成功率 | 是否创造价值 |
| Model quality | PR-AUC、Recall@k、NDCG、FAR/FRR、pass@k | 是否学到目标 |
| Guardrail | 严重错误漏检、误拒率、安全/隐私违规、unsupported claim | 不能被平均数掩盖 |
| System | p50/p95、QPS、availability、cost/success、GPU utilization | 是否可上线 |

先确定 operating point，再汇报模型：

- 高风险任务通常固定可接受的 `FPR/FAR`，比较该点的 recall/FRR。
- 极不平衡任务优先 PR curve，不只报 accuracy。
- ranking 同时看 Recall@k（候选召回）与 NDCG/MRR（顺序）。
- 生成任务不能只看 BLEU/ROUGE；加 outcome verifier、grounding、人评和 error taxonomy。

## Step 3：写 Data Contract，而不是说“收集更多数据”

每个训练例子要有：

```text
example_id, entity_id, event_time, feature_cutoff_time
raw_input_pointer, normalized_input, context
label, label_source, label_time, confidence/adjudication
sampling_probability, provenance, consent/license, schema_version
```

然后回答：数据为什么存在、谁被遗漏、标签是事实还是 proxy、上线时能否取得同样特征、train/test 是否共享实体或未来信息。详见 [02_data_and_labels.md](02_data_and_labels.md)。

## Step 4：先给 Baseline Ladder，再选模型

一个成熟答案至少比较：

```text
rules / heuristic
  → linear/tree/small CNN or encoder
  → pretrained encoder / dual encoder
  → cross-encoder or task fine-tuning
  → generative/multimodal foundation model
  → cascade / agent + verifier
```

选择依据不是“SOTA”，而是：输出结构、所需上下文、标签量、错误代价、推理预算、可解释性与更新频率。

高分句：

> 我会先用最便宜的 baseline 建立 error taxonomy 和 data flywheel。只有当错误来自缺少语义或长上下文，而不是标签噪声或 coverage gap 时，才升级模型容量。

## Step 5：训练目标必须对应行为

| 任务 | 常见 objective | 面试中要补的一句 |
|---|---|---|
| 分类 | weighted CE、focal loss | threshold 由业务代价决定，不由 0.5 决定 |
| retrieval | contrastive / InfoNCE | in-batch negatives 可能有 false negatives；要做 hard-negative mining |
| ranking | pairwise logistic、listwise softmax | 训练采样要接近 serving candidate distribution |
| 生成 | token CE / SFT | likelihood 不等于 usefulness；需 outcome/human eval |
| preference | RM + RLHF、DPO/IPO 类 | preference 来源和 annotator disagreement 必须保存 |
| verifiable task | rejection sampling、RLVR | verifier coverage 是 reward 的上限，防止 gaming |

不要把所有目标揉成一个不可解释分数。先定义 hard constraints，再定义软目标和 cost。详见 [03_model_training_reward.md](03_model_training_reward.md)。

## Step 6：Evaluation 要回答“能否预测生产表现”

1. **Split**：time/entity/repository/writer/customer/device/geography；说明为何能阻断泄漏。
2. **Slices**：长尾、冷启动、低质量输入、语言/设备/行业、极端长度、对抗样本。
3. **Baselines/ablations**：rules、小模型、去掉 retrieval、去掉 synthetic、不同 context。
4. **Uncertainty**：confidence interval、多 seed、校准、coverage-risk curve。
5. **Human eval**：blind、randomized、明确 rubric、重复标注与 disagreement。
6. **Prospective holdout**：保留未来时间窗或新实体，避免“精心修到 test set”。

## Step 7：Serving 从预算倒推

先列预算：

```text
peak QPS, p95 latency, input size/tokens, output size/tokens,
availability, cost/request, cost/success, peak memory, region/privacy.
```

再选择：batch/async、cache、quantization、distillation、small-to-large routing、early exit、candidate generation + rerank、image crop/downsample、token/context pruning、fallback 和 abstention。

最常用结构：

```text
Request
  → deterministic validation / quality gate
  → cheap high-recall or high-confidence model
  → uncertain/high-value traffic routed to expensive model
  → verifier / policy / calibration
  → action, abstain, or human review
```

## Step 8：Feedback Loop 不等于“把用户点击拿来重训”

生产事件至少记录：model/data/prompt/index version、输入 slice、score/calibration、decision、human override、delayed outcome、latency/cost。注意：模型改变了用户看到的内容，所以点击、acceptance 等标签存在 exposure/selection bias。

可用做法：保留小比例 exploration、记录 propensity、随机抽样人工审计、用 inverse propensity weighting 做分析、维护不受在线策略污染的 prospective set。

## 白板总图

```text
Sources ─→ immutable raw/lineage ─→ validate/dedup/label ─→ versioned dataset
                                                     │
                                                     ▼
                                           train + experiment registry
                                                     │
                           offline eval + slices + calibration + safety gates
                                                     │
                                                     ▼
Request ─→ feature/context builder ─→ cascade/model ─→ verifier/policy ─→ action/HITL
   │                                     │                    │
   └──────────── trace + latency + cost + prediction ─────────┘
                                                     │
                         delayed outcome + audit + drift ─→ retrain decision
```

## 必须主动说的三个 trade-off

1. **Coverage vs precision**：多提建议/多召回会提高 coverage，也会增加噪声与 reviewer fatigue。
2. **Quality vs latency/cost**：大模型不是默认路径；高价值或不确定样本才升级。
3. **Fast feedback vs unbiased truth**：行为日志快但有 bias；专家 gold 慢且贵，需组合使用。

## 常见失分模式

- 一上来就说 GPT-4/ViT/LLM，没有定义 action 与标签。
- “数据不够就生成 synthetic data”，但没说 synthetic 能覆盖什么、不能代表什么。
- random split 让同一用户、repo、writer 或模板出现在 train/test。
- 用用户点击/merge 当 gold label，不讨论曝光偏差、团队规范和延迟。
- 只报模型平均分，不报关键 slice、阈值、校准与置信区间。
- 只说量化/缓存，不给 QPS、p95、cost/request 或路由条件。
- 直接用 RL，但 reward 不可验证、judge 未校准、没有防 reward hacking。
- 结束时没有 launch gate、rollback、人工兜底和获取新标签的方法。

## 60 秒结尾模板

> V1 会用可审计的数据合同、时间/实体隔离的 holdout 和一个便宜 baseline 验证是否真的有信号；生产上用校准后的 cascade，把不确定或高风险样本交给更强模型/人工。上线从 shadow 到 canary，以业务主指标、关键安全 slice、p95 和 cost/success 共同 gate。最大的未知是 ___，所以我下一步会做 ___ 对照实验，而不是直接扩大模型。
