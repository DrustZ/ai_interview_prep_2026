# 11 · Mock Interview 与评分表

## 怎么练

- 用计时器 45 分钟，前 30 分钟不看答案。
- 每 5–8 分钟让“interviewer”从追问池插一题。
- 结束后只按 evidence 打分：说过/写过才算，不因“心里知道”加分。
- 低于 3 分的维度，回看对应章节并立即重讲 5 分钟。

## Mock 1：Code Review LLM

### 主问题

> 设计并训练一个能审查大型企业 monorepo 中 pull request 的 LLM。它需要发现真实 bug、给出可执行 comment，同时不能让开发者被低价值建议淹没。

### 追问池

1. 历史 PR comment 哪些能当 label，哪些不能？
2. 没有 comment 的代码能当 negative 吗？
3. 如何做 split，既防泄漏又贴近新 repo 冷启动？
4. 你会选 SFT、DPO 还是 RLVR？reward 从哪来？
5. tests 只有 30% coverage，如何防 reward hacking？
6. peak 100 PR/s、p95 30 秒、预算每 PR $0.05，架构怎么改？
7. 线上 acceptance 上升但 bug escape rate 不变，怎么解释？

### 合格答案必须出现

`prediction decomposition`、`repo/time split`、`comment precision/serious-bug recall`、`label provenance`、`static analyzer/test verifier limits`、`incremental context/cascade`、`shadow/A-B + reviewer fatigue`。

## Mock 2：Mobile OCR + Signature Verification

### 主问题

> 为银行设计一个手机拍摄纸质表单的系统：抽取字段，检测签名，并判断签名是否与客户登记样本一致。全球上线，要求两秒内返回。

### 追问池

1. OCR 与 signature verification 为什么不能共用一个“accuracy”？
2. 如何采集 glare、blur、perspective、不同纸张和扫描设备的数据？
3. 每个客户只有 2–3 个 reference，怎么办？
4. 真实 forgery 非常少，synthetic forgery 能解决吗？
5. train/test 为什么要按 writer/site/device 隔离？
6. 如何选择 FAR/FRR operating point 和人工复核区间？
7. 端侧与云端如何分工，怎样把成本降下来？

### 合格答案必须出现

`quality/geometry gate`、`layout/detection→crop→OCR/embedding verification`、`writer-independent metric learning`、`synthetic nuisance only`、`unseen-writer/device prospective set`、`calibration/HITL`、`privacy/consent`。

## Mock 3：Exa 类 Agentic Search

### 主问题

> 训练一个给研究 agent 使用的 web search 系统。它要决定如何改写 query、多轮检索、打开页面并给出带证据的答案。你负责数据、post-training、evaluation 和 production design。

### 追问池

1. Retriever、reranker、answerer、planner 的训练数据分别是什么？
2. click logs 如何去 position/exposure bias？
3. hard negatives 里有真正 relevant page 怎么办？
4. 只有最终答案 reward 会产生什么问题？
5. 如何评 freshness、claim-level grounding 与 source diversity？
6. 何时用 trajectory SFT、preference optimization、RL？
7. 如何控制 query/tool/token 数并保证长尾问题 recall？

### 合格答案必须出现

`layer-specific supervision`、`contrastive + pair/listwise + grounded generation`、`query/time/domain split`、`evidence-aware outcome reward`、`cost/latency penalty`、`offline component + e2e + online`、`freshness/index version`。

## 评分 Rubric（每项 0–4）

| 维度 | 0 | 2 | 4 |
|---|---|---|---|
| Framing | 直接选模型 | 有用户与目标但含糊 | decision/unit/horizon/error/SLO 明确 |
| Metrics | 只说 accuracy | 有 offline/online | 主指标、guardrail、operating point、cost |
| Data | “收集更多” | 列来源 | contract/provenance/bias/split/governance 完整 |
| Scarcity | 只说 synthetic | 有 transfer/augmentation | 先诊断缺口，分阶段并有真实 eval gate |
| Model/objective | 堆模型名 | 模型大致合适 | baseline ladder、objective/sampling 与 failure mode 匹配 |
| Reward | 一个 weighted score | 有 outcome/penalty | hard/soft 分离、provenance、anti-gaming、independent eval |
| Evaluation | 单一 held-out 分数 | 有 slices | IID/OOD/prospective、CI/calibration、e2e/human |
| Production | “API + GPU” | 有 cache/batch | 数量级、cascade、fallback、capacity、cost/success |
| Feedback | “收日志重训” | 有 monitoring | exposure/delay、audit/exploration、retrain gate/rollback |
| Communication | 跳跃/无结论 | 覆盖多数点 | assumption→decision→trade-off→experiment 清楚 |

总分 40：

- `32–40`：能主导 senior-level 讨论；继续练 domain depth 与数量级。
- `24–31`：结构合格，但需要补最弱的两项。
- `<24`：不要继续刷新题；先把通用框架练到可闭卷复述。

## 复盘模板

```text
题目：
我的首个 assumption：
我定义的 action / unit / label：
我漏问的约束：
最大 data bias/leakage：
baseline 与升级理由：
reward provenance：
offline→online gate：
成本数量级：
interviewer 最可能不满意的一点：
下一次固定补的一句话/一个图：
```

## 三分钟压力版

如果 interviewer 只给三分钟，按 7 句：

1. “我把目标定义为 ___，用户据此做 ___。”
2. “主指标是 ___，guardrails 是 ___，因为 FP/FN 中 ___ 更贵。”
3. “训练单位/标签是 ___；最大偏差是 ___；按 ___ split。”
4. “V1 是 ___ baseline；只有出现 ___ 错误才升级到 ___。”
5. “objective/reward 来自 ___；用 ___ 防 gaming。”
6. “线上用 ___ cascade，预算是 p95 ___ / cost ___。”
7. “用 shadow→canary 验证 ___；最大未知通过 ___ 实验解决。”
