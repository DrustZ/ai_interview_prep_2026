# Google DeepMind 面试全攻略（2026-07 版）

> 岗位：RE（你的主轨；RS 实际要求重量级 publication record，RE 更灵活）。GDM 有独立 recruiter 和面试轨，**不走 Google SWE 统一流程**，但 coding 题风与 Google 题库趋同。
> 已投（Shan 内推）。**全程禁 AI 工具**——GDM 明确筛选 unaided reasoning。

## 1. 流程（2026，RE 轨）

```
简历筛（~90% 淘汰）→ Recruiter call 30min（判定 Applied vs Core 方向，含行为面成分）
→ [可能 HM 面] → Skills 轮（gated）：2 轮 coding 先过 → ML fundamentals + ML design 轮
→ 终面：Team Lead + Senior Team Lead + People & Culture → HC → team match（可挂人）
```
全程 6-7 周；官方 PDF 明说用 **STAR** 答行为题（[官方 prep PDF](https://storage.googleapis.com/deepmind-media/DeepMind.com/Assets/Docs/interviewing-at-google-deepmind.pdf)——recruiter 也会发，逐条过推荐阅读）。

**Quiz 演变史**（备考强度定标）：2019 年 2 小时四连考（math/CS/stats/ML 各 30min）→ 对话式快问快答 → **2025 起部分 RE 岗 recruiter 确认取消独立 math/stats quiz，并入 ML/AI 轮**（[Blind 2025-03](https://www.teamblind.com/post/deepmind-re-interviews-z8txzan3)）。含义：数学不单独设轮，但会揉进 ML 轮问直觉与推导。

**RS 轨补充**：paper presentation（讲自己的论文，被 push hard on assumptions）+ research talk + 逐个 teammate 1:1。

## 2. Coding 轮（2 轮，Google 风格，必须现场跑通）

风格：LC medium/hard，出自 Google 内部题库，CoderPad/Jupyter 环境**代码必须运行**。节奏基准：37 分钟 2 题写完+过测试（[Blind 挂经](https://www.teamblind.com/post/got-rejected-by-deepmind-lwftrbpv)——挂点：图复杂度说成 O(N) 而非 O(V+E)、不 clarify）。

| 真题 | 出处 | 解法要点 |
|------|------|---------|
| **Trie 前缀匹配**（LC208） | IGotAnOffer 榜首 | dict children + is_end；三操作 O(L) |
| **Snapshot Array**（LC1146） | 多来源 | 每 index 存 (snap_id,val) 追加列表 + get 二分 |
| **Best Meeting Point**（LC296 hard） | 多来源 | 曼哈顿距离 x/y 可分离 → 各取中位数，O(mn) 免排序 |
| **Add Two Numbers**（LC2） | 多来源 | 进位 + dummy head；follow-up 正序版用栈 |
| **概率 twist 的 LC medium**（2026-05 实测两道全是） | [r/leetcode](https://old.reddit.com/r/leetcode/comments/1tfu311/how_i_passed_deepmind_technical_rounds_with_3/) | 最大概率路径 = 最小化 −Σlog p → Dijkstra（LC1514）；蓄水池采样 LC382、按权采样 LC528、rand7↔rand10 拒绝采样（会证期望调用次数） |
| **刷栅栏最少笔刷**（LC1526 变体）+ DFS 题 | Glassdoor | ans = h[0] + Σ max(0, h[i]−h[i−1])；先给分治再优化 |
| **手写 logistic regression + 1 hard LC** | Blind 2024 | numpy：sigmoid、BCE、梯度 Xᵀ(p−y)/n、数值稳定 |

打底题单：Google 高频 Top30（[1p3a 1116355](https://www.1point3acres.com/bbs/thread-1116355-1-1.html)：Find Leaves、RPN、Snapshot Array、Stock Price Fluctuation、Min Time Difference、Text Justification、Meeting Rooms II、Logger…）+ [hack2hire Google 46 题](https://www.hack2hire.com/question-bank/companies/google/coding-questions)（多为 LC 变体：Unix Find、URL Router(Trie)、Search History(LRU)、MinMax Queue(单调队列)、Grep with Context）。

## 3. ML Fundamentals 轮（俗称 the quiz，现为对话式）

答题标准：**机制级解释，不是名词解释**。签名题示例（verbatim 来自 Glassdoor/IGotAnOffer）：

| 真题 | 标准答案要点 |
|------|-------------|
| **L1 vs L2 为什么 L1 稀疏**（不许只说结论） | L1 次梯度幅度恒为 λ·sign(w)，与 \|w\| 无关，把小权重一路推到 0 且 0 处可驻留；L2 梯度 2λw 按比例收缩，w→0 时更新消失，永不精确为 0 |
| 为什么要凸函数 / 什么是 GD / Newton 法 / 二阶方法 | 凸 → 局部即全局，收敛保证；Newton：x ← x − H⁻¹∇f，二阶 Taylor，局部二次收敛但 O(d³) |
| gradients vs weights 的区别 | 参数 vs 损失对参数的导数；更新关系 |
| Bayes 公式 + 袋中彩球观察后预测下次颜色 | 后验预测（共轭 Dirichlet-categorical / Laplace 平滑） |
| regression / SVM / kernel SVM / Bayesian networks 横向对比 | 判别 vs 生成、margin、kernel trick、概率图 |
| **ELBO 推导** | log p(x) = E_q[log p(x,z)/q(z)] + KL(q‖p(z\|x)) ≥ ELBO；Jensen 和 KL 非负两种推法都要会 |
| KL 性质、协方差、浮点数表示（fp32/bf16 布局）、信息论 | 见 core-ml.md |
| **GRPO rollout 的假设是什么**（2026-01，GDM 相关人员提问风格） | 组内奖励的 mean/std 替代 critic → 假设同 prompt 的 rollouts 可比且非退化（全同奖励→无信号）；std 归一化引入偏差 |
| 遥测信号 ML 应用题（给机器温度/负载数据设计方案） | 按 ML design 框架：目标（异常检测/故障预测）→ 特征 → 标签稀疏/不平衡 → 时序 split 防泄漏 → PR-AUC → 部署监控。**要的是扎实+变通，不是 SOTA** |

复习源：MML book（线代/概率/优化）+ `core-ml.md` 的 20 道必背题。注意：面试官会**顺着你自称懂的领域往深挖**（统计 PhD 被问过泛函分析），你的 post-training 领域必须能推导到底（PPO/GRPO 公式级）。

## 4. ML Design 轮（公认最难轮）

格式：像 SD 但 ML-first——走完整 pipeline（数据收集→预处理→模型→训练→**评估**→部署），面试官**迭代加约束**，每步要从第一性原理 justify。

高频场景（对 RE/Gemini-adjacent 岗）：
- **Distributed training design**：显存数学（Adam 混合精度 ≈ 16 bytes/param）→ DP → ZeRO 1/3 → TP（节点内）→ PP（跨节点）→ activation checkpointing → 互连感知放置 → 故障恢复。内部人推荐读：[EEML tensor parallelism tutorial](https://github.com/eemlcommunity/PracticalSessions2023/tree/main/tensor_parallelism)
- **Evaluation infrastructure design**：直接对口你在 Reflection 的 eval 工具经验，主动讲 trace debugging/eval comparison
- **LLM serving**：KV cache = 2·layers·kv_heads·head_dim·bytes·seq，continuous batching、PagedAttention、speculative decoding、量化
- Applied 轨（recruiter 明说的四大块）：RAG（factuality/grounding）、efficiency（quantization/distillation）、agent frameworks、**evals**
- 练法：拿任一设计（recsys/serving/eval pipeline）自己加约束重解：标注数据少 10 倍？→ 弱监督/合成数据；严格延迟？→ 蒸馏/量化/缓存；分布漂移？→ 监控+再训练

## 5. 终面 / Behavioral

- Team Lead ×2：简历任意深挖 + 开放式 ML 问题 + design choice 辩护；Senior TL 更看团队匹配。
- P&C：why DeepMind、mission alignment、协作。STAR 结构。
- **过了技术仍可能挂在 team match**。准备 3-4 个 STAR 故事：reward hacking 发现与修复、数据配比 ablation、eval 驱动迭代、跨团队协作（infra/数据）。

## 资源

- [官方 prep PDF](https://storage.googleapis.com/deepmind-media/DeepMind.com/Assets/Docs/interviewing-at-google-deepmind.pdf) ⭐ 必读
- [IGotAnOffer RE 完整指南](https://igotanoffer.com/en/advice/google-deepmind-research-engineer-interview) ⭐ 最全聚合
- [Glassdoor RE](https://www.glassdoor.com/Interview/Google-DeepMind-Research-Engineer-Interview-Questions-EI_IE1596815.0,15_KO16,33.htm) / [RS](https://www.glassdoor.com/Interview/Google-DeepMind-Research-Scientist-Interview-Questions-EI_IE1596815.0,15_KO16,34.htm) · [Blind RE 全程](https://www.teamblind.com/post/deepmind-research-engineer-interview-process-wp1gjgyb) · [r/leetcode 2026-05 过经](https://old.reddit.com/r/leetcode/comments/1tfu311/how_i_passed_deepmind_technical_rounds_with_3/) · [techinterview.org 2026](https://www.techinterview.org/post/3233474918/deepmind-interview-process-2026/) · [Aleksa Gordić 上岸长文](https://gordicaleksa.medium.com/how-i-got-a-job-at-deepmind-as-a-research-engineer-without-a-machine-learning-degree-1a45f2a781de) · [deep-ml DeepMind 合集](https://www.deep-ml.com/collections/DeepMind%20Interview%20Prep)
- 你的 reflection 目录直接可用：`../../reflection/theory-mte-quiz-and-stories.md`（就是 GDM quiz 风格）、`theory-ml-question-bank.md`、`design-rl-on-video-game.md`（ML design 轮）、`case-study-rl-bottleneck.md`
