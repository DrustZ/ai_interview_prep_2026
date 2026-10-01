# 03 · 模型选择、训练目标与 Reward 设计

## 1. 模型选择不是模型名单

先回答六个变量：

1. 输出是 classification、ranking、embedding、sequence、structured action 还是 patch？
2. 输入需要局部模式、全局上下文、跨模态对齐，还是与外部环境交互？
3. 有多少 **独立实体** 的可靠标签，而不只是派生 pair 数？
4. 错误是否能由 deterministic verifier 检查？
5. serving 的 p95、QPS、memory、cost 和 privacy 预算？
6. 数据/ontology 多久变化一次，是否需要 retrieval 或频繁更新？

## 2. 常用架构选择表

| 需要 | 首选 baseline | 升级条件 | 常见风险 |
|---|---|---|---|
| tabular/classification | logistic/tree | 强非线性、多模态 | calibration、shortcut |
| 图像检测/裁剪 | small CNN/detector | 小目标、复杂 layout | resolution 与 latency |
| OCR sequence | detector + recognizer | 多场景端到端需求 | language prior 猜字 |
| 相似度/verification | pretrained encoder + metric learning | 极少参考、跨域 | identity leakage |
| 大规模 retrieval | BM25 + dual encoder | 语义召回不足 | false negatives、freshness |
| 精排 | tree/cross-encoder | 候选少且质量重要 | O(k) 推理成本 |
| 受控生成 | templates/small seq2seq | 长上下文、开放表达 | hallucination、verbosity |
| 复杂代码/推理 | code LLM + tools/verifier | task 可执行或需 repo context | reward gaming、成本 |
| 多步搜索 | deterministic workflow | query planning 需自适应 | trajectory credit assignment |

高分句：

> 我会把“能力模型”和“知识/新鲜度”分开：频繁变化的事实进入 retrieval/index，稳定的行为模式通过 fine-tuning 学习，不用每次知识更新都重训模型。

## 3. Baseline ladder 与实验顺序

```text
B0: current policy / no-ML / random
B1: rules + simple statistics
B2: small supervised model on available features
B3: pretrained representation + linear probe / PEFT
B4: larger task-specific model / cross-encoder / generator
B5: cascade, retrieval, tools, verifier, human escalation
```

每次升级只针对 error taxonomy 中明确的 failure mode，并报告增量质量、p95、cost/success、维护复杂度。大模型和 agent 是可能的 B4/B5，不是 B0。

## 4. 常见训练目标

### 分类与不平衡

Weighted cross entropy：

\[
L=-\sum_c w_c y_c\log p_c
\]

Focal loss 让易例权重下降：

\[
L=-\alpha(1-p_t)^\gamma\log p_t
\]

何时用：正负极不平衡且大量易负例。风险：它不修复 label noise；仍需在 validation 上选业务阈值并做 calibration。

### Retrieval / metric learning

对 query `q`、正例 `d+`、候选集合 `D`：

\[
L_{NCE}=-\log\frac{e^{s(q,d^+)/\tau}}{\sum_{d\in D}e^{s(q,d)/\tau}}
\]

关键不在公式，而在 negative distribution：random negatives 太容易，top-retrieved hard negatives 信息量高，但可能包含未标注的相关文档（false negative）。需要 relevance adjudication、multiple positives 或 soft labels。

### Pairwise / listwise ranking

Pairwise logistic：

\[
L=-\log\sigma(s(q,d^+)-s(q,d^-))
\]

训练候选必须来自接近线上 first-stage retriever 的分布，否则 offline gain 不会迁移到线上。

### 生成 / SFT

\[
L_{SFT}=-\sum_t\log p_\theta(y_t\mid x,y_{<t})
\]

Token likelihood 学的是示范分布，不直接保证 comment 有用、答案有证据或 patch 通过测试。必须追加 outcome verifier / structured rubric / human preference eval。

### Preference optimization

数据是 `(x, y_w, y_l, source, annotator/rubric)`。DPO 类目标可绕过显式 reward-model + online RL 的复杂度，但不能绕过 preference data 的 bias、冲突和 coverage。若偏好来自 learned judge，必须单独标出 AI-feedback provenance，并用人类 gold set 校准。

## 5. Post-training 升级顺序

1. **Prompt / tools / retrieval baseline**：先确认问题真是行为而非缺 context。
2. **SFT**：教格式、任务分解、工具协议和高质量行为。
3. **Filtering / rejection sampling**：用 verifier 或 rubric 从多样本中筛高质量轨迹。
4. **Preference optimization**：学习“两个都可行但哪个更好”，适合 usefulness/style/precision trade-off。
5. **RL/RLVR**：只有当可交互环境与 reward 足够可靠、探索能发现 SFT 数据外的更好策略时再用。

不要回答“先 SFT 再 RLHF”就结束。要说：各阶段更新哪个模型、标签/reward 从哪来、verifier 是否冻结、最终在哪个独立集合验证。

## 6. Reward 的结构：来源比公式更重要

可以用下式组织讨论：

\[
R = w_tR_{task}+w_qR_{quality}+w_sR_{safety}-\lambda_cC-\lambda_lL
\]

但 production 中应区分：

- **Hard constraints**：泄密、危险 patch、编译失败、无证据 claim、越权工具调用。违反即 reject/zero reward/terminate，不能被“语言很漂亮”抵消。
- **Task outcome**：测试通过、正确定位、检索到支持证据、真实用户任务完成。
- **Quality**：精确、可执行、覆盖、简洁、校准。
- **Cost**：tool calls、tokens、latency、GPU time、人工复核。

### Reward provenance 表

| Reward | 来源 | 优点 | 盲点 | 如何校准 |
|---|---|---|---|---|
| unit/integration tests | deterministic verifier | 便宜、可重复 | tests 不完备、可过拟合 | hidden/adversarial tests |
| static analyzer/type checker | programmatic | 高 precision | 规则 coverage 窄 | 与专家 defect set 对照 |
| user accept/merge | behavior | 贴近 workflow | exposure/team-style bias | exploration + audit |
| expert rubric | human | 处理语义与风险 | 贵、disagreement | double-label/adjudicate |
| learned judge | model | 可扩展 | shared blind spots、position/style bias | human gold、swap order、多 judge |
| downstream business outcome | environment | 最终价值 | 延迟、confounded | causal experiment/holdout |

面试时明确：**哪些 reward 是观测事实，哪些只是 proxy**。

## 7. 防 Reward Hacking

典型攻击：

- 为通过公开 tests 写 hard-coded patch；
- 生成大量低价值 comment 拉高“发现数”；
- 引用很多页面却没有 claim-level support；
- 输出冗长、模仿 judge 偏好的格式；
- 重复 query/tool call，碰巧找到答案但成本失控；
- 在 signature/OCR 中利用背景、scanner 或表单模板 shortcut。

防护组合：

1. hidden、rotating、adversarial verifiers；
2. train reward 与 final acceptance metric 分离；
3. hard constraints + 多维 dashboard，不只优化单一 weighted scalar；
4. judge 用 human gold 校准，交换答案顺序，去掉 identity/style cues；
5. KL/行为约束、长度与成本惩罚、trajectory budget；
6. report pass rate 同时报告 violation、coverage、cost 和 slice；
7. 定期人工读最高 reward 与最大 reward delta 的轨迹。

## 8. 模型选择的三个口述例子

### “为什么不用最大 LLM 做所有 code review？”

> 大量检查是 formatter、type checker、security rule 能高精度完成的；LLM 的价值在跨文件语义、意图和可执行解释。我会用确定性工具先产生或验证候选，小模型做过滤/严重度，大模型只处理高价值或不确定 diff，并以 comment precision、严重 bug recall、p95 与 cost/accepted-comment 共同决定路由。

### “数据很少，为什么不 full fine-tune？”

> 我先按独立实体数与域偏移判断有效样本量。小数据下先 frozen representation/linear probe 或 PEFT，并用 entity-level bootstrap；若错误是表示不足再逐步解冻。full fine-tune 容易过拟合标签噪声，也增加模型版本与回滚成本。

### “什么时候值得 RL？”

> 当任务是多步决策，行为会改变后续 observation，而且有覆盖充分、难以被 gaming 的 outcome verifier 时，RL 才可能超过模仿已有轨迹。若只是单轮格式或偏好，SFT/DPO 更直接；若 verifier 只覆盖一小部分正确性，我会先补 eval/reward，而不是让策略更强地优化一个坏 proxy。

## 9. Ablation 与决策记录

建议实验表：

| 实验 | 只改变 | 假设 | 主指标 | guardrail | cost delta | 决策 |
|---|---|---|---|---|---|---|
| B1→B2 | model | 语义特征补足规则 coverage | recall@fixed FPR | slice FPR | +$ | ship/no |
| +synthetic | data source | 补设备噪声 | new-device score | real-only score | train + | keep/drop |
| +RLVR | objective | exploration 找到更好 trajectory | hidden task success | violation | train ++ | keep/drop |

如果一个实验同时换 data、model、prompt、reward 和 serving，很难回答“为什么变好”，也很难在 regression 时修复。

## 10. 自检清单

- [ ] model family 与输出结构、数据规模、SLO 相匹配。
- [ ] 有便宜 baseline，升级对应具体 failure mode。
- [ ] loss 与 negative/sampling distribution 说清楚。
- [ ] SFT / preference / RL 每阶段的 label 或 reward 来源清楚。
- [ ] hard constraints 不会被软 reward 抵消。
- [ ] learned judge 不是未经校准的“真值”。
- [ ] final eval 与训练 reward 独立，包含 reward-hacking 测试。
