# Anthropic 面试全攻略（2026-07 版）

> 岗位：RE/RS/MTS。核心特点：**题库小且编号化（coding Q1-Q21、SD Q1-Q7），recruiter 提前告知题号** → 可完全定向准备，但 bar 极高、容错接近零（有人题全对仍挂）。
> 内部推进中（Xiaoyi 内推）——拿到题号后回来查对应条目。

## 1. 流程（2026）

```
HR Screen（问 safeguard 文档感想）→ [OA：CodeSignal 90min 4-level]
→ 店面 55min（RE/RS 四选一 track，见下）→ VO 5 轮：coding + SD + project deep dive + HM + culture
→ Reference Check（≠offer，check 后仍可能被拒）→ Hiring Committee
```

- 硬性政策：25% onsite（remote 员工每月飞一周）。
- 拒信 timing 规律（hack2hire 统计）：**≤24h = 技术挂，2-3 天 = culture/HM 挂**。
- 官方允许/鼓励在部分轮次用 Claude（看 recruiter 说明），但 GDM/OpenAI 风格的"背题速答"反而触发怀疑。

## 2. 店面四选一 track（2026-05 新政，[thread-1165574](https://www.1point3acres.com/bbs/thread-1165574-1-1.html)）

| 选项 | 内容 | 对你的适配 |
|------|------|-----------|
| ① Coding problem-solving | 传统题（Q1 crawler / Q6 tokenizer 等） | 保底可选 |
| ② **Coding & Design** | 如 **Weighted Data Batcher with Checkpointing**：按权重从 DataRegistry 采样组 batch，要求确定性 save/resume（offset 精确恢复采样流） | ⭐ 首选。就是你在 Reflection 做的事。解法：seeded/counter-based RNG + 可序列化状态（rng state + per-source offset）；加权采样用前缀和二分 vs 别名法；讨论多 worker 分片、数据源增删对确定性的影响 |
| ③ ML Configuration System | 实现/设计 ML 实验配置系统：嵌套 config、默认值+覆盖 deep merge、类型/约束验证、sweep 笛卡尔积展开、reproducibility | ⭐ 备选，也对口 |
| ④ Prompting & Engineering with LLMs | Colab 里用 prompting 搭 pipeline（55min） | 你的 agentic workflows 经验够用 |

## 3. 新增专项轮（2026，对你背景是送分）

### RL Fundamentals 轮：Debug GRPO training loop（[prachub 完整题解](https://prachub.com/interview-questions/debug-a-grpo-training-loop-and-explain-ratios)）
- 给简化 GRPO step 实现，**3 个埋好的 bug**，常见类型：log-prob 未做 autoregressive shift 对齐、KL/loss 的 token masking 错、advantage 归一化除零（组内奖励全相同）、rollout 与 update 的 policy 不一致。每个 bug 要给**检测方法+修复**，不能只点名。
- 核心追问：**严格 on-policy 为什么 importance ratio ≠ 1？** 三大合法原因：① 每 batch 多次 minibatch update 后 πθ 已漂移 ② vLLM 采样与训练器 forward 的 kernel/精度差异 ③ bf16 舍入。判别实验：同一 checkpoint 用训练器重算生成 log-prob 对比；fp32 复算；第一次 optimizer step 前 ratio 应恰为 1。
- Follow-up：clip 如何防崩、组内奖励全同怎么办、engine-to-trainer log-prob 修正、process vs outcome supervision、KL 放 reward 还是 loss。
- **主动澄清**：reward 类型、每 batch optimizer 步数、生成/打分是否同一 forward、采样温度、KL 实现、精度。

### Agent Coding 轮：用 Claude API 搭 agent loop（[1p3a 1178346](https://www.1point3acres.com/interview/thread/1178346)）
- 实测版本：定义 tools 回答股票价格问题。要点：messages API tool-use 协议（tools schema → stop_reason=="tool_use" → 执行 → tool_result 回传 → 循环 + 最大步数保护）、tool 报错回传让模型重试、并行 tool call。**提前手写一遍完整 loop 并跑通**。

## 4. Coding 题库（Q 编号，按频率）

| 题 | 频率 | 解法要点 | 本地解法 |
|---|------|---------|---------|
| **Q1 Web Crawler** | 10/10 最高频 | 单线程 BFS（LC1236）→ 多线程（ThreadPoolExecutor + 去重锁）→ 多机（Redis central queue） | `../01_company_notes/anthropic/questions_and_solutions.md` |
| **Q1' Image Processing** | 高（Python 候选人） | Pillow 6 种 transform 顺序 apply；大图用 ProcessPoolExecutor（CPU 密集）。**Pillow API 熟练度是真正的门槛** | 同上 |
| **Q2 File Dedup** | 10/10 | 分块哈希（先 size 再首块再全量 SHA256）→ 讨论 CPU vs I/O bound → MapReduce 扩展 → 持续监控（DB 存 hash 映射） | 同上 |
| **Q2' LRU Cache** | 中 | functools.lru_cache 语义 + generate_key(*args,**kwargs)；follow-up crash 恢复 → WAL | 同上 |
| **Q3 Stack Trace / Profiling Events** | 9/10 | 相邻采样栈对比出 start/end 事件；follow-up 连续 N 次 filter | 同上 |
| **Q6 Tokenizer** | 高（2026 持续） | longest match + max_len 剪枝 + 连续 UNK 合并；先 debug 给定实现再重写 | 同上 |
| **Cluster Mode & Median**（分布式） | 10/10 | 分布式众数/中位数：本地聚合直方图 + 合并；中位数用分布式二分计数 | [hack2hire](https://www.hack2hire.com/question-bank/companies/anthropic/coding-questions) |
| **Bootloader Repair**（2026-06 新） | 8/10，活跃 | AoC-2020-Day-8 风格：指令模拟找首个重复执行 → 尝试翻转 jmp/nop 修复 | 同上 |
| **Durable Function Call Cache**（2026-06 新） | 8/10，活跃 | 两 part：cache key 设计（args 规范化哈希）+ WAL crash recovery | 同上 |

## 5. OA 家族（CodeSignal 90min 4-level，本地已有全部解法）

Banking(10/10)、In-Memory DB + backup/restore(9/10)、Cloud Storage(7/10)、Recipe Manager(7/10)、Task Assignment、Worker Mgmt、Note-Taking。
套路：dict-of-dataclass 建模，**先读完 4 级再设计**；L3/L4 常加 TTL/时间戳/备份/排序查询。800/1000 可过线。
→ 本地解法 7 份全在 `../02_coding_practice/anthropic_oa/`，考前重写 2 套即可迁移到任何变种。

## 6. System Design 题库（Q 编号）

| 题 | 频率 | 要点 |
|---|------|------|
| **SD Q1: GPU Inference Serving / LLM Batch API** | 10/10 最高频 | dynamic batching（延迟预算内组 batch）、请求路由、race condition、GPU 显存瓶颈（KV cache 数学要会算）。你可直接引用 vLLM/PagedAttention |
| **SD Q2: Prompt Playground** | 9/10 | **Google Doc 纯书面轮，不画图**——评分的是文字推理深度（requirements/schema/scaling），以及在面试官强势 redirect 下守住结构。10MB+ 超长 prompt 怎么处理 |
| **Distributed AI Model Downloader** | 8/10 | 500GB 模型 → 1000 台机器：P2P/tree 分发、分块校验、带宽限制 |
| **SD Q3 Metrics / SD Q4 1-1 Chat / SD Q5 Data Infra** | 中 | Data Infra 对口你的数据管线背景 |

## 7. Culture 轮（最大挂点，技术全过也能挂）——深度备考

> 交叉验证的挂点画像：1p3a 多帖 + hack2hire 分析 + 2026-06 真实挂经原话："Gave what I thought was a **genuine** answer about AI safety and it **wasn't specific enough**" —— 真诚但不具体 = 挂。

**已验证真题清单**（1p3a 多帖 + interviewing.io）：
1. Why Anthropic?（必须深思熟虑，能区分于"任何 AI 公司都适用"的答案）
2. 对 AI safety 的看法，为什么对你重要？
3. 你有没有做过什么**利他不利己**的事？
4. 大家说 AI 很 risky，那为什么还要做？
5. 和谁观点不一样过？有没有 moral dilemma？当时**感受**如何（追问针对情感而非结果）
6. Tell me a time: failed project，如何依然找到 impact
7. Tell me a time: 跨职能冲突及化解
8. 假设情景伦理题（无标准答案，看推理过程）
9. HR screen 前置题：safeguard 文档读了吗、感想？

**过关公式**（挂经反推）：泛泛而谈必挂 → 每个答案做到四层：
```
具体立场 → 指名一个具体的 Anthropic 主张（RSP 的 ASL 分级 / Core Views 的某个论点）
   → 亲身经历佐证（你的真实故事，含当时的情绪和代价）
   → 批判性思考（指出 Anthropic 自身的张力并给出你的权衡）
   → 为什么这个权衡下你仍然选择来
```

**你的素材库（提前写成 5 个故事，STAR + 情感层）**：
- **利他不利己 / safety 初心**：你 PhD 的 accessibility 研究（为不同能力人群做输入技术）——这是真实的、有 paper 背书的利他向工作，比编造的故事强一个数量级
- **价值与利益冲突**：Meta 推荐系统时期 用户福祉 vs 增长指标 的任何真实张力；或 Reflection 数据质量把关（发现 eval trace 有问题时选择放慢 vs 赶进度）
- **Reward hacking 亲历**：你做 RL post-training 见过的真实 reward hacking 案例 + 你怎么修的——这是 Anthropic 最爱的话题（他们有专门论文）
- **观点冲突**：与 vendor/同事在数据质量标准上的分歧
- **失败项目找 impact**：任选

**批判性思考的安全角度**（挑 1-2 个真信的，别全用）：商业化收入 vs 安全使命的张力；RSP 的 ASL 门槛是否足够保守/可执行；"racing to the top" 论证依赖竞争对手跟进的假设；能力研究与对齐研究的资源分配。表达格式："我认同 X，但认为 Y 存在张力，因为……即便如此我仍然认为 Anthropic 的做法是 Z，理由是……"

**必读**：[Core Views on AI Safety](https://www.anthropic.com/news/core-views-on-ai-safety) · [RSP](https://www.anthropic.com/news/anthropics-responsible-scaling-policy) · recruiter 发的 safeguard 文档。禁忌：背稿感、复述官网、只谈技术不谈价值。

## 8. Take-home + Live Review（⭐ 你当前所在环节，2026-07 实况）

**你的邮件条款解读**：题目在 review 前 72h 发放 → 提交截止 review 前 24h（实际窗口 ~48h，但**要求 timebox 在一个 24 小时段内**）→ 典型投入 ~8h → 提交先经内部审核（**不过线直接取消 review**，说明有硬性质量 bar）→ 55min live review。选时间时给自己留一个完整的空闲日。

**题型情报**（按可信度排序）：
- 研究向 take-home（[interview-help.live 2026 报告](https://www.interview-help.live/interview-experiences/2026anthropic)，付费教练站，谨慎参考）：**exploratory research project**——pandas/numpy/matplotlib，训练+评估模型+数据可视化，live review = **10min presentation（slides 或 code walkthrough）+ 不设限追问**
- 性能向 take-home（官方开源：[anthropics/original_performance_takehome](https://github.com/anthropics/original_performance_takehome)）：模拟加速器上优化树遍历（多核/SIMD/VLIW/手动内存管理）——若你的岗位偏 infra 可能是这型
- 1p3a 历史报告：RS 轨 4 小时作业、Accelerator 团队 4 小时多核模拟器

**AI 工具政策**：官方工程博客[《Designing AI-resistant technical evaluations》](https://www.anthropic.com/engineering/AI-resistant-technical-evaluations)明确写：take-home **允许用 AI**（长题型 AI 难以整体求解、贴近真实工作）；另有轮次直接给 Claude Code CLI。**但以你收到的 assignment 说明为准**——政策没写就邮件问 recruiter，别猜。

**高分打法**（对 8h 研究型）：
1. 前 1h 只做一件事：定义清晰的 research question + 最小 baseline，先跑通端到端再迭代
2. 评估严谨性是评分核心：train/test split 无泄漏、报告不确定性、负结果也报告
3. 可视化讲故事（你有 dataviz 优势）：每张图回答一个问题，图题写结论
4. writeup 里主动写 **known limitations + 下一步**——review 追问时这是你的主场而非弱点
5. 明确记录 timebox 取舍："8 小时内我优先了 X 放弃了 Y，因为 Z"——诚实的取舍叙事本身是评分项
6. 提交后到 review 前：把每个决策的 why 练到能脱口而出（为什么这个指标/这个 split/不用更大模型），预演对抗性追问；review 前确认 Colab/GPU 环境能跑
7. Live review 无 AI、只有你本人——**所有代码和决策必须能亲口辩护**（这也是别找人代工的根本原因，见聊天记录）

## 9. hack2hire 论坛可信度警告

本次抓取其论坛全部 288 帖，**247 帖（86%）含机器生成标记**（HTML 注释 `persona: … | generated_at: …`、用户头像路径为 `/bot-avatars/`）。其"面经/员工评价"帖大概率是 AI 合成的引流内容，**只可采信与 1p3a/Blind/官方交叉验证过的信息**；其题库元数据（题目、频率）可能基于真实报告但无法独立验证。本文档中来自 hack2hire 的条目均已用其他来源交叉核对或标注。

## 资源

- 本地：`../02_coding_practice/anthropic_oa/`（7 份 OA 全解）、`../01_company_notes/anthropic/questions_and_solutions.md`（2026 行题+解）、`../00_reports_and_plans/final_report_v2.md` 第三部分
- [1p3a Anthropic 题库](https://www.1point3acres.com/interview/problems/company/anthropic) · [hack2hire Anthropic](https://www.hack2hire.com/question-bank/companies/anthropic/coding-questions) · [hack2hire 流程汇总](https://www.hack2hire.com/blog/content/6a219a818b879849ebc11ff6) · [interviewing.io Anthropic](https://interviewing.io/anthropic-interview-questions) · [deep-ml Anthropic 合集](https://www.deep-ml.com/collections/Anthropic%20Interview%20Prep)
