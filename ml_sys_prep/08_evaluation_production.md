# 08 · Evaluation、Production 与成本闭环

## 1. Evaluation 不是最后一节

在收数据前先写 acceptance contract：

```text
Primary: 哪个指标必须提升多少（含置信区间）？
Guardrails: 哪些 slice/安全/业务指标不得退化？
Budget: p95、QPS、cost/success 上限？
Population: 对哪个时间、地区、客户、设备、任务分布成立？
Decision: 通过后 shadow、canary，还是直接替换？
```

## 2. 四层 eval stack

| 层 | 问题 | 示例 |
|---|---|---|
| Data | 数据/标签可信、覆盖 production 吗？ | coverage、dedup、agreement、drift |
| Component | 单个模型/检索器是否工作？ | Recall@k、FAR/FRR、PR-AUC、ECE |
| End-to-end | 整个 pipeline 是否完成用户任务？ | useful review、supported answer、case resolution |
| Online/business | 用户与系统是否真正受益？ | adoption、time saved、loss prevented、cost/success |

强系统可能组件分数一般但 e2e 更好，反之亦然。比如 retriever Recall@20 上升，若引入更多噪声让 answerer grounding 下降，不应上线。

## 3. 常用指标与 operating point

### 分类/检测

- 不平衡数据：PR-AUC、precision/recall、recall at fixed FPR。
- 高风险 verification：FAR（impostor 被接受）与 FRR（genuine 被拒），EER 只用于模型比较；生产阈值由成本决定。
- Calibration：Brier score、ECE、reliability diagram；阈值路由依赖校准后的概率。

若 FP/FN 成本可估计，阈值 `t` 最小化：

\[
\mathbb E[C(t)] = C_{FP}P(FP\mid t)+C_{FN}P(FN\mid t)+C_H P(HITL\mid t)
\]

### Retrieval/ranking

- candidate generation：Recall@k、coverage、latency。
- ranking：MRR、NDCG@k、pairwise accuracy。
- search quality：freshness、source authority/diversity、duplicate rate。
- answer layer：claim-level support、citation precision/recall、answer correctness。

### Generation/agent

- deterministic outcome：test pass、environment state、schema/policy validity。
- human rubric：correctness、usefulness、specificity、non-duplication、conciseness。
- trajectory：success@budget、tool error、steps/tokens、recovery、policy violation。
- stochastic：报告 pass@1、pass^k/consistency，并按 task bootstrap confidence interval。

## 4. Slice first，而非平均分 first

至少覆盖：

- 新实体/冷启动；
- 长尾类与高代价错误；
- 输入质量（blur、noise、长 context、损坏文档）；
- 语言/地区/设备/行业；
- 数据来源与 label provenance；
- 时间新鲜度、post-cutoff；
- 对抗、越权、prompt injection 或 forgery；
- 模型 confidence bins。

为每个关键 slice 设最低样本量与 gate。样本太少时报告区间和人工 review，不伪装成精确百分点。

## 5. Human / LLM judge 的正确用法

### Human eval

- randomized、blind，隐藏 system identity；
- 给具体 rubric 与反例，先 pilot；
- 双标关键样本，保存 disagreement；
- 同时评 pairwise preference 和 absolute acceptability；
- 对生产高频与高风险按目标分布加权。

### LLM-as-judge

可以扩量，不能自动成为 gold：

- 用人类 gold set 量 precision/recall、position/order bias、style/length bias；
- 交换 A/B 顺序，使用结构化 evidence；
- judge 与被评模型尽量不同 family/checkpoint；
- 不确定/分歧进入人审；
- final launch gate 仍含 independent outcome/human checks。

## 6. Offline → Online 发布阶梯

```text
replay/backtest
  → shadow traffic（不影响用户）
  → internal/dogfood
  → 1% canary + strict guardrails
  → randomized A/B or stepped rollout
  → gradual ramp
  → continuous audit + rollback
```

每一阶段预先定义：流量、持续时间、停止条件、owner、rollback artifact/model/index version。不要看到一个好指标就临时改 gate。

## 7. 从 SLO 反推 serving

### Capacity 模板

```text
peak_qps = DAU × requests/user/day × peak_factor / 86400
required_concurrency ≈ peak_qps × average_service_time
replicas ≈ peak_qps / effective_qps_per_replica × headroom
daily_cost ≈ requests/day × cost/request + fixed infra
```

对 LLM 还要按 tokens 计量：

```text
prefill tokens/s, decode tokens/s, TTFT, TPOT,
input/output length distribution, KV-cache bytes/sequence,
batch utilization, cache hit rate.
```

对图像：分辨率、crop 数、batch size、decode/preprocess CPU、GPU memory 与传输经常比“模型 FLOPs”更早成为瓶颈。

### 成本优先级

1. 避免无价值调用：validation、dedupe、debounce、exact/rule path。
2. 减少输入：相关 crop、incremental diff、selective retrieval、context pruning。
3. 重用：feature/embedding/prefix/result cache，明确 version/TTL/invalidation。
4. 合并：micro-batching、async queue、continuous batching。
5. 路由：small-to-large cascade、confidence/value-aware escalation。
6. 压模型：distillation、quantization、pruning/early exit，在真实 slices 上重验。
7. 优化硬件/并行：profiling 后再做 kernel、parallelism 与 autoscaling。

核心指标是 **cost per successful, acceptable outcome**，不是只看 cost/request；便宜但大量失败/人审的模型可能更贵。

## 8. Cascade 与 abstention

例：

```text
quality/rule gate
  → small model score p
      p < t_low: reject/no-op
      p > t_high and low-risk: accept
      otherwise: large model / more context / human
```

阈值不只看 accuracy，要在真实流量上优化总成本：model cost、human cost、FP/FN loss、latency。监控每层流量和 conditional quality，防止大模型 escalation rate 悄悄升高吞掉预算。

## 9. Monitoring：检测什么变化

| 类型 | 指标 | 动作 |
|---|---|---|
| Input drift | schema/null、embedding/feature distribution、device/language mix | data alert、fallback |
| Prediction drift | score/entropy、class/routing rate、abstention | calibration audit |
| Concept/performance | delayed gold、human override、slice errors | retrain/threshold change |
| System | p95/p99、queue、OOM、timeout、cache hit、GPU util | autoscale/degrade |
| Cost | tokens/crops/tool calls、cost/request/success、HITL rate | route/budget gate |
| Safety/security | PII leak、policy violation、attack/forgery success | kill switch/incident |

Drift 告警不等于自动重训。先判断 schema bug、traffic mix、label delay、seasonality 还是 concept drift；再通过固定 evaluation gate 决定 threshold update、data refresh 或 retraining。

## 10. Delayed labels 与 feedback flywheel

事件表至少能 join：

```text
request_id, entity_id, event_time,
data/model/prompt/index versions,
prediction + calibrated confidence,
route/action/exposure,
human decision/correction,
outcome + outcome_time,
latency/tokens/cost/error.
```

定期产出：

- random audit set（估总体质量）；
- disagreement/uncertain set（高信息量标注）；
- high-cost/high-impact failures；
- new slice/post-cutoff prospective set；
- accepted 与 rejected/unexposed 候选的对照。

## 11. Production failure modes

- train-serving skew：parser/tokenizer/context/feature cutoff 不同；
- stale cache/index 与版本不匹配；
- retry storm、batch head-of-line blocking、GPU OOM；
- fallback 安静地产生低质量结果；
- calibration 随流量变化失效，cascade 成本爆炸；
- 人工队列超载，SLA 和 label quality 同时下降；
- model/judge 同时升级，无法定位 regression；
- privacy deletion 只删 raw data，派生 feature/index 仍残留。

## 12. 面试中的成本回答模板

> 我会先给 workload 的数量级：peak QPS、输入/输出分布、p95 与 cost/success。V1 用 deterministic gate + small model 覆盖常见流量，仅把不确定或高价值样本升级；缓存有明确 version/TTL，批处理只在 latency budget 内。shadow 阶段测真实 service-time 与 escalation 分布，再据此容量规划。量化/蒸馏属于后续 profiling-driven 优化，并且必须重新跑关键 slice、校准和 guardrails。

## 13. Launch checklist

- [ ] frozen representative + prospective eval sets，且 provenance 可审计。
- [ ] primary、guardrail、SLO、cost gates 预注册。
- [ ] confidence/threshold 校准到目标流量。
- [ ] shadow/canary、kill switch、fallback、rollback 已演练。
- [ ] model/data/prompt/index/feature 版本写入 trace。
- [ ] human escalation 有容量、SLA 和 rubric。
- [ ] delayed outcomes 可 join，random audit 能估无偏表现。
- [ ] drift 只触发调查；重训仍需完整 acceptance gate。
