# 02 · 数据、标签与数据短缺

## 一句话原则

> 数据问题先拆成 **coverage、label quality、sample efficiency、distribution shift** 四类；它们需要不同解法，“再收集一些数据”不是方案。

## 1. 从业务流程反推数据来源

按可信度与规模建立 source portfolio：

| 来源 | 规模/成本 | 优点 | 主要偏差 | 合适用途 |
|---|---|---|---|---|
| 真实 outcome / transaction | 大、标签可能延迟 | 最接近业务结果 | policy/exposure、survivorship | online eval、弱监督 |
| 用户行为日志 | 大、便宜 | 持续更新 | position/selection/social bias | ranking、hard-case mining |
| 专家标注 | 小、贵 | 可定义高质量 rubric | annotator drift、覆盖窄 | gold eval、关键训练集 |
| 众包标注 | 中 | 可扩展 | 专业性不足、shortcut | 简单 perception/分类 |
| programmatic/weak labels | 很大 | 快、可复现 | rule-correlated errors | pretraining、candidate set |
| public/partner/licensed corpus | 大 | 冷启动快 | license/domain mismatch | pretraining、representation |
| synthetic / simulator | 可扩展 | 控制 rare factors | generator artifacts、真实性不足 | augmentation、stress test |
| human-in-the-loop corrections | 中 | 聚焦生产错误 | 只覆盖被模型暴露的样本 | active learning、持续改进 |

面试中先画“用户如何产生数据”的流程，再指出模型上线后会改变这个流程。比如 code-review bot 只展示高分 comment，未来的“accepted comment”数据就缺失低分候选的 counterfactual。

## 2. Data contract：一个例子到底是什么

最低字段：

| 类别 | 字段/问题 |
|---|---|
| Identity | `example_id`、`entity_id`（user/repo/writer/doc） |
| Time | event time、feature cutoff、label observation time |
| Input | raw pointer/hash、parser/version、available-at-serving-time context |
| Label | value、definition、source、confidence、adjudication、missing reason |
| Sampling | inclusion rule、sampling probability、negative construction |
| Governance | provenance、license/consent、PII class、retention/deletion |
| Reproducibility | schema、dataset snapshot、transform/code version |

关键检查：

- 训练时使用的 context 在线上 decision time 是否真的可用？
- “没有观察到正例”是负例，还是 unlabeled？
- label 是直接 outcome、专家判断，还是模型/judge 的 proxy？
- 一个 raw event 是否产生多个高度相关样本，从而放大某些实体？

## 3. 标签设计：把 provenance 当成一等公民

至少区分：

```text
gold: 专家按稳定 rubric 标注并处理 disagreement
outcome: 真实结果，但可能延迟且受产品策略影响
behavioral proxy: click/accept/dismiss/merge
weak: rule/static analyzer/heuristic
synthetic: teacher/simulator 生成
learned-judge: 另一个模型打分
```

不要在训练前把它们压成同一个 `label=1`。保存 `label_source` 与 `confidence`，才能：

- 分来源采样或加权；
- 单独报告 gold set 表现；
- 发现 teacher/judge 的系统偏差；
- 当规则或 judge 升级时重建标签；
- 做 ablation，判断增益来自真实信号还是伪标签复制。

### 标注质量控制

1. 先用 50–100 例 pilot 修 rubric，而不是立即大规模发标。
2. 关键样本双标/三标；记录原始 votes，不只保留 adjudicated label。
3. 插入 gold checks，但避免标注员只针对已知模式优化。
4. 分 slice 估计 agreement；总体 κ 高不代表罕见高风险类可靠。
5. 定期 blind re-label，量 annotator/rubric drift。
6. 对专家 disagreement，可保留 label distribution 或“需要人工复核”，不强行制造唯一真值。

## 4. Split 是设计的一部分

Random row split 只在样本独立同分布时成立，现实中经常不成立。

| 风险 | 应用的 split |
|---|---|
| 同一用户/患者/writer 的风格泄漏 | group by entity |
| 同一 repo/fork/文件模板泄漏 | repo/fork family split |
| 未来信息进入过去 | chronological split + feature cutoff |
| 同一设备/扫描仪/站点过拟合 | held-out device/site/geography |
| 网页、代码、文档近重复 | exact + near-dedup before split |
| benchmark 被预训练见过 | provenance audit + post-cutoff/new-source set |

推荐三套集合：

- `IID validation`：快速迭代，发现常规回归。
- `OOD/challenge set`：新实体、罕见场景、对抗输入。
- `prospective holdout`：冻结模型和阈值后，用未来数据验证。

任何手工挑选的 challenge set 都不能替代代表生产分布的 held-out set。

## 5. 数据短缺：先诊断，再按升级阶梯处理

### 先问短缺发生在哪里

- **总量少**：所有类都少；需要 transfer/self-supervision 或更简单模型。
- **正例少**：class imbalance；需要 sampling、cost-sensitive objective、PU learning 思维。
- **关键 slice 少**：coverage gap；定向采集/active learning，而不是全局扩容。
- **gold 少但 raw 多**：weak supervision、self-supervision、pseudo-label。
- **部署域没有标签**：domain adaptation、prospective pilot、HITL。
- **标签有争议**：不是量的问题；先修 task/rubric。

### 升级阶梯

1. **修任务与标签**：合并无法可靠区分的类；预测更可观测的中间目标；允许 abstain。
2. **建立简单 baseline**：判断信号是否存在，形成 error taxonomy。
3. **利用预训练表示**：冻结 encoder/linear probe → parameter-efficient fine-tune → full fine-tune。
4. **自监督/多任务学习**：从大量 unlabeled domain data 学表示。
5. **weak supervision**：组合规则、静态分析器、知识库；保留每个 labeling function 的输出。
6. **专家标注**：优先标覆盖空白和决策边界的样本。
7. **active learning**：uncertainty + diversity + slice coverage + expected value，而非只挑最低 confidence。
8. **semi-supervised/pseudo-label**：高置信 teacher 标签；控制 teacher confirmation bias。
9. **augmentation/synthetic**：只改变已知 nuisance factor 或补可控 rare case；真实 holdout 不得 synthetic。
10. **domain adaptation/HITL**：新域先 shadow，低置信交给人，逐步积累本域 gold。

### 为什么 synthetic 不是万能答案

Synthetic data 适合：

- 可精确控制的几何/噪声/格式因素；
- 可执行 verifier 判定的任务；
- 扩展语言表达但事实内容已有来源；
- 为 challenge set 构造 stress cases。

它不可靠地代表：

- 未知的真实用户行为分布；
- 真实签名的 intra-person variation 与 skilled forgery；
- 安全漏洞、社会偏差等开放长尾；
- teacher 自己不会的能力。

Synthetic 接受门：记录 generator/prompt/seed，去除 train/eval 重复，训练时限制配比，在纯真实 prospective set 上比较，并检查模型是否学到 generator artifact。

## 6. Active learning 的专业答法

只按 entropy 采样会得到一堆噪声/不可判定样本。更合理的 acquisition score：

\[
A(x)=\alpha U(x)+\beta D(x)+\gamma S(x)+\delta V(x)-\lambda C(x)
\]

- `U`：模型不确定性或 ensemble disagreement；
- `D`：与已标数据的多样性/覆盖；
- `S`：关键 slice 稀缺度；
- `V`：标注后可能影响的业务价值/流量；
- `C`：专家标注成本。

还需随机抽样一部分生产流量，才能估计整体指标并发现模型“自信地错”的区域。

## 7. 行为日志中的偏差

对于 click/accept/merge 等日志：

- **exposure bias**：未展示的候选没有标签；
- **position bias**：排前更容易被点；
- **policy bias**：当前模型决定看到什么；
- **survivorship**：只记录完成流程的样本；
- **delayed/ambiguous outcome**：merge 不代表 comment 正确，没采纳也不一定错误。

缓解：随机化小流量、记录展示与 propensity、counterfactual/off-policy evaluation、人工审计未展示候选、按 source 分层训练、未来窗口补 outcome。

若用 inverse propensity weighting：

\[
\hat R(\pi)=\frac{1}{N}\sum_i \frac{\mathbf{1}[a_i=\pi(x_i)]r_i}{p(a_i\mid x_i)}
\]

必须说明小 propensity 会导致高方差，需 clipping / doubly robust estimator，并保留真正随机的校准流量。

## 8. 数据版本与治理

```text
raw immutable layer
  → validated canonical records
  → dedup/PII/license filters
  → labels + provenance
  → split manifest
  → training snapshot + hash
```

训练 run 必须关联 dataset manifest、filter/dedup code、tokenizer/parser、sampling weights。支持按来源删除数据时，要能定位受影响 shard/checkpoint，并定义是未来训练删除还是需要模型 unlearning/retrain。

## 9. 面试示例：“只有 2,000 个签名用户，怎么办？”

> 我先澄清目标是 writer verification，不是 OCR，并按 writer 隔离 train/test。2,000 人并不等于只有 2,000 个 pair：可以从每人的多次 genuine 样本构造正 pair，并用其他 writer 和真实/模拟 forgery 构造分层 hard negatives，但 pair 相关性很强，所以评估置信区间按 writer bootstrap。模型从通用图像或文档自监督表示起步，再做 Siamese/metric learning；synthetic 只用于透视、模糊、压缩、背景等 nuisance augmentation，不能冒充 skilled forgery。新 writer 冷启动与低置信样本进入人工复核，持续采集经 consent 的真实本域数据。最终在 unseen-writer、new-device 和 prospective set 上固定 FAR 比较 FRR。

## 10. 自检清单

- [ ] 样本单位、实体、time cutoff 和标签窗口明确。
- [ ] 所有 label 都保存 source/confidence，而非混成“真值”。
- [ ] split 能阻断 entity/time/near-duplicate 泄漏。
- [ ] 数据短缺方案针对具体缺口，不是无条件 synthetic。
- [ ] gold eval 全为真实、独立、版本冻结的数据。
- [ ] 收集/授权/隐私/删除/lineage 能落到字段与流程。
- [ ] 模型上线后的 exposure bias 和 delayed labels 已处理。
