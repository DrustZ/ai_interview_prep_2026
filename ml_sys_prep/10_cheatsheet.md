# 10 · 面试前一页速查

## 开场背这一段

> 我先定义用户 decision、prediction unit、错误代价和 SLO，再定主指标与 guardrails。之后写 data/label contract、time/entity split 和最便宜 baseline；根据输出结构、数据规模和 serving 预算选模型/objective。最后覆盖 slice/e2e eval、cost-aware serving、shadow→canary，以及如何从生产获得较无偏的新标签。

## 白板顺序

```text
Problem → Metrics → Data → Baseline/Model → Objective → Eval → Serving → Loop
```

## 八个必问

1. 谁用输出做什么动作？
2. 一个样本和标签是什么，何时可得？
3. FP/FN 哪个更贵，能否 abstain？
4. peak QPS、p95、cost/success、privacy？
5. 最大 selection bias / leakage？
6. 最便宜 baseline 是什么？
7. 为什么这个 model/loss 匹配输出和数据？
8. 上线后如何知道错了并获得新标签？

## 数据短缺阶梯

```text
修 task/rubric
→ baseline + error taxonomy
→ pretrained/self-supervised transfer
→ weak supervision
→ targeted expert labels
→ active learning
→ pseudo-label
→ controlled synthetic augmentation
→ domain pilot + HITL
```

Synthetic 只能补已知 nuisance/可验证 rare case；真实 gold/prospective eval 不 synthetic。

## Split

`time + entity + near-duplicate family`。按题目换成 repo/fork、writer、customer、device/site。Random row split 经常泄漏。

## 模型选择

- classification：rules/tree/small encoder。
- retrieval：BM25 + dual encoder；top-k 再 cross-encoder。
- verification：pretrained embedding + metric learning + calibrated threshold。
- generation：SFT 教行为；outcome/human eval 验 usefulness。
- agent/RL：只有多步决策 + 可靠 verifier + 探索价值时。
- 大模型只处理 ambiguous/high-value traffic；其他走 deterministic/small path。

## Reward

```text
hard constraints first
task outcome + quality - latency/tokens/tool/human cost
```

每个 reward 说来源：deterministic、human、behavior proxy、learned judge。Final eval 必须独立。防 hacking：hidden verifier、adversarial set、多指标、judge calibration、人工看 high-reward trajectory。

## Eval

- classification：PR-AUC、recall@fixed FPR、calibration。
- verification：FAR/FRR，固定业务 FAR 看 FRR。
- retrieval：Recall@k → MRR/NDCG → claim support/e2e task。
- generation/agent：outcome + rubric + policy + success@budget。
- 所有题：IID + critical slices + OOD/challenge + prospective holdout + CI。

## Production 成本

```text
validate/dedupe
→ reduce input/crop/context
→ cache
→ batch/async
→ small-to-large route
→ distill/quantize
→ hardware optimization after profiling
```

报告 `p95, QPS, escalation rate, cost/request, cost/success, human-review rate`。

## 五个专题一句话

- **Code review**：PR/history/tests 造数据；repo+time split；precision 优先；static tools → small filter → LLM → verifier。
- **OCR/signature**：先分 detection/OCR/ID/verification；device/site/writer split；synthetic 只补成像噪声；固定 FAR 看 FRR。
- **Search post-training**：retriever/reranker/answerer/agent 分开训练和评估；最终答对还要证据、freshness 与 cost。
- **Pre-training data**：license/provenance → parse/filter/PII → exact/near dedup → contamination → mixture → proxy runs/lineage。
- **AI 客服 agent**：先拆 deflection/containment/resolution（containment 可以靠拒绝转人工刷出来）；resolution 没有免费标签，用「后端状态变更 + 7 天无重复联系」+ 人工 QA 校准；多租户是共享模型 + 租户配置 + 租户级 eval，不是每租户一个模型；成本看**每次已解决**的成本。

## 高分句

> 我不会先扩大模型；我会先确认错误来自 capacity，而不是 coverage、标签噪声、泄漏或 threshold。

> 行为日志规模大，但模型决定了用户看到什么；因此它是有偏 proxy，不是天然 gold。

> Pair 数量不等于独立样本量；我会按 repo/writer/customer 做 split 和 bootstrap。

> Cost 的分母应是成功且可接受的 outcome，而不只是 request。

> V1 用最简单可审计系统建立 data flywheel，V2 只针对已观测 failure mode 升级。

## 结尾背这一段

> V1 先用冻结的 time/entity holdout 和便宜 baseline 验证信号；生产用校准 cascade，把不确定或高风险样本升级给更强模型/人工。从 shadow 到 canary 同时 gate 业务指标、关键 slice、p95 和 cost/success。最大未知是 ___，下一步用 ___ 对照实验决定是否升级，而不是凭直觉换模型。
