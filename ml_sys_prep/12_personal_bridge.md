# 12 · 从你的 HCI / Agentic LLM 背景切入 ML System Design

这页基于你的[公开主页](https://drustz.com/)所列背景：HCI、智能文本输入与可访问性、AR/wearable 输入交互，以及近期 agentic LLM 开发。目的不是伪造 code review、OCR 或 search 项目经历，而是把已有能力转换成 interviewer 能识别的 ML system design 信号。

## 1. 你不是从零开始

| 已有背景 | 在 ML system design 中对应的优势 | 面试里怎么说 |
|---|---|---|
| HCI experimental design | construct validity、用户任务、实验与行为指标 | “我会先问模型指标是否预测真实用户 decision，而不是先优化 proxy。” |
| 智能文本输入/纠错/预测 | ranking、latency、personalization、online feedback | “接受/忽略候选是有 exposure bias 的行为标签，不是天然 truth。” |
| Accessibility research | critical slices、error asymmetry、inclusive data collection | “总体均值会掩盖 subgroup burden，我会单独 gate 关键用户 slice。” |
| AR / wearable interaction | device/domain shift、on-device latency、power、multimodal noise | “采集矩阵必须覆盖设备、姿态、光照、输入质量与真实使用环境。” |
| Agentic LLM work | trajectory、tool/verifier、SFT/RL、e2e eval | “我会把 retriever、policy、verifier 与 final outcome 分开评估和版本化。” |

你真正要补的是三段“中间层”：

1. 从用户研究走到 **data contract / sampling / label provenance**；
2. 从模型训练走到 **baseline ladder / objective / calibration**；
3. 从 prototype 走到 **capacity / cost / rollout / delayed feedback**。

## 2. 适合你的 90 秒自我定位

> 我的背景横跨 HCI 和 agentic LLM。HCI 训练让我先定义真实用户任务、可观察行为和错误成本，也让我对行为日志的偏差、subgroup slices 和人评 construct validity 比较敏感；智能文本输入与 wearable 工作让我长期考虑 latency、device shift 和 human-in-the-loop。最近做 LLM/agent 后，我把这些问题扩展到 trajectory、tool use、verifier、post-training 和端到端 eval。对我而言 ML system design 不是先选模型，而是把用户 decision、数据生成机制、训练信号、serving 约束和 feedback loop 接起来。对于我没有亲自做过的 vertical，我会明确假设，用 baseline 和实验逐步验证，而不会把设计方案说成历史结果。

## 3. 回答陌生领域题时的“可信迁移”句式

### 可以说

- “我没有亲自上线过签名验证，但它与我做过的真实设备输入问题共享 domain shift 和 human-error-cost 结构；我会先把不同任务拆开，再验证这些假设。”
- “我没负责过 web-scale pretraining corpus，所以这里我会区分业界已知方法与我的设计选择；我的第一步是建立可审计的数据实验，而不是声称某个比例一定最好。”
- “我做过 agentic system，因此 trajectory 与 verifier 的边界比较熟悉；search-specific relevance/click bias 部分，我会用 held-out relevance data 和 online experiment 验证。”
- “我会给 v1 和触发 v2 的 evidence，而不是假设最复杂模型一定需要。”

### 不要说

- “我们以前就是这么做的”，如果实际没有该项目。
- 把 HCI user study 直接等同于 production A/B 或大规模因果结论。
- 把训练过通用/agent model 等同于拥有 OCR、fraud、search relevance 的 domain label expertise。
- 用“我研究过用户，所以 user feedback 是 gold”——恰恰应主动指出 feedback bias。

## 4. 把已有项目故事映射到答题框架

准备 3 个真实故事，每个只需一页：

### Story A：Reflection / Agentic LLM

用来回答：post-training、trajectory data、verifier、eval、data curation、失败分析。

```text
Problem / users:
Training unit / trajectory:
Label or reward provenance:
Which model updated / which verifier stayed frozen:
Offline + end-to-end metrics:
A failure where proxy and real goal diverged:
Serving/cost constraint:
Your exact ownership vs collaborators:
```

### Story B：智能文本输入 / auto-correction

用来回答：ranking、behavior logs、personalization、latency、online metrics、accessibility slices。

```text
Candidate generation and ranking unit:
Accepted/ignored behavior and its bias:
Latency interaction with user experience:
Per-user vs global modeling trade-off:
How you evaluated different abilities/users:
```

### Story C：AR / Wearable Interaction

用来回答：multimodal data collection、device/domain shift、edge constraints、human factors。

```text
Device/environment matrix:
Sensor/input quality failures:
How participants/tasks were sampled:
Offline signal vs real interaction outcome:
Power/latency/comfort trade-off:
```

把每个故事都标出：`I owned`、`I collaborated on`、`team outcome`。这能防止把团队结果说成个人 ownership，也让追问时更稳。

## 5. 四道题怎样自然接回你的强项

### Code Review LLM

先按 [04_case_code_review_llm.md](04_case_code_review_llm.md) 回答。到 online eval 时连接 HCI：comment 不仅要技术正确，还消耗 reviewer attention；需要 precision、dismiss reason、review time、trust/fatigue，而不只看生成文本相似度。

### OCR / Signature

先按 [05_case_ocr_signature.md](05_case_ocr_signature.md) 消歧。连接 wearable/interaction：真实设备输入分布、用户 recapture 指令、低质量输入的可行动反馈、edge latency 与不同能力用户的 failure burden。

### Exa / Search Post-training

先按 [06_search_post_training.md](06_search_post_training.md) 分层。连接 text input：query rewrite/candidate ranking 与输入预测类似，用户点击/接受都受 exposure 和 rank 影响；连接 agent：trajectory success 必须同时有 evidence 与 cost。

### Pre-training Data

按 [07_pretraining_data.md](07_pretraining_data.md) 讲 pipeline。连接 HCI 的 construct validity：quality classifier/benchmark 都是 proxy；真正的数据价值要用固定 compute 的训练 ablation 和独立下游任务验证。

## 6. 一周内可完成的四个“证据练习”

不需要把它们包装成 production project；它们用于让知识从口述变成可检查 artifact。

1. **Data contract drill（1 小时）**：从一个公开 PR 抽出 review-time snapshot、candidate finding、label source、split key，写成 JSON schema。
2. **Retrieval eval drill（2 小时）**：做 30 个 query 的人工 graded set，跑 BM25 与 embedding baseline，报告 Recall@k/MRR、hard-negative errors 和 latency。
3. **OCR slice drill（1–2 小时）**：在许可公开样本上只做 blur/perspective/quality gate；按 transform slice 报 calibration/abstention，不声称完成签名验真。
4. **Data-mixture thought experiment（1 小时）**：为 1B proxy model 写 source mixture、token budget、三个 fixed-compute ablation 和 acceptance gates。

做完后，每个 artifact 都能用这句话诚实描述：

> 为补足该领域知识，我实现了一个小规模、可复现的 validation exercise；它验证的是 ___，不能证明 ___，下一步若上线还需要 ___。

## 7. 你的差异化结尾

> 我会把 ML system 当成一个 socio-technical loop：模型改变用户看到和执行的内容，因此也改变下一轮训练数据。我的 HCI 背景让我特别关注这个反馈机制、人的 attention 与 subgroup burden；我的 agentic LLM 经验让我能把它落实成 trajectory、verifier、eval 和 serving contract。对陌生 vertical，我的策略是明确假设、从可审计 baseline 开始、用真实 prospective outcome 决定是否升级。
