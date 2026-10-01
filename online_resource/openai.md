# OpenAI 面试全攻略（2026-07 版）

> 岗位：Research/RS/RE/MLE 轨（Agent Post-Training / Computer Use / Personal AGI）。
> 数据截至 2026-07：一亩三分地 184 题题库 + hack2hire + Blind/Reddit 交叉验证。

## 1. 流程（2026 年中实测）

```
Recruiter → 店面（coding 60-75min，有时 +SD 60min 双轮）→ VO 4-6 轮
→ Hiring Committee → Team Match（原组满员需重 match，常见 downlevel）→ Reference Check（1 manager + 1 peer，电话）
```

- **RS/Research 轨 2026 大改**（[thread-1173645](https://www.1point3acres.com/bbs/thread-1173645-1-1.html)，最重要单帖）：不再给 prompt，只发 general PDF。四轮：**2 道 AI coding + 1 道 general coding + 1 道 math reasoning**。每题 4 分制，**bar ≈ 4433，4443 稳**（即至少两轮满分）。题池小、高度重叠，原帖原话："如果你不能 overfit，这个题目还是有难度的" → **策略就是 overfit 题池**。
- **MLE/RE 轨**：recruiter 提前给 topic 且很准（[thread-1174800](https://www.1point3acres.com/bbs/thread-1174800-1-1.html) prompt 原文："math and coding + open-ended discussion/brainstorm about research ideas"）→ 提前备 2-3 个 post-training/agentic 开放式研究想法。
- 评分特点：**必须全部写完+跑通测试**；写太快会被疑用 LLM（[thread-1172810](https://www.1point3acres.com/bbs/thread-1172810-1-1.html)）；沟通清晰度是 deep dive 轮的主要挂点。新试点：agentic coding round（给 codebase + 允许用 AI）。

## 2. General Coding 题池（按 2026 频率排序）

| # | 题目 | 频率 | 解法要点 | 本地解法 |
|---|------|------|---------|---------|
| 1 | **感染题** Infection Spread（5 小问） | 33 帖，最高频 | BFS + newly_infected 集合；P2 免疫跳过；P3 恢复用 day→坐标 map（注意 off-by-one）；P4 邻居计数 m[i][j] 达 K 记死亡时间，level BFS 求 max(level+D)；P5 贪心烧行/列 | `../02_coding_practice/openai/solutions.py` |
| 2 | **GPU Credits I/II** | 11 帖（2026-04 上新） | 按 timestamp 顺序消耗 + 过期处理（heap/SortedList）；II：余额不足 getBalance 返回 None；follow-up 时间戳改 float、真实系统实现 | 同上 |
| 3 | **Social Network + Snapshot** | 13 帖 | follow/unfollow + snap()：每关系存 (snap_id, state) 列表 + 二分（同 LC1146 思路）；推荐轮按共同媒介数排序 | 同上 |
| 4 | **Toy Language 类型推断** | 8 帖 | 递归下降 parser + Node class + toString + infer_return 泛型匹配（冲突报错） | 同上 |
| 5 | **Monster Battle**（OOP 多小问，chess follow-up） | 9 帖 | 类设计题，先写清 entity/action 接口再填逻辑 | 同上 |
| 6 | **In-Memory SQL/DB** | 7 帖 | dict + 二级索引；filter by name/age/id | 同上 |
| 7 | **Data Labeling Task Scheduler** | 7 帖 | 构造满足 quota + evenly-distributed 约束的 (task,model,human) 序列；轮转分配即可，无复杂度要求 | `../01_company_notes/openai/questions.md` |
| 8 | **Memory Allocator** | 6 帖 | malloc/free + 空闲块合并；O(log N) 用 SortedDict | [1p3a 1162026](https://www.1point3acres.com/bbs/thread-1162026-1-1.html) |
| 9 | **KV Store 持久化/序列化** | high | 字符串/字节序列化（length-prefix），append-only log | [1p3a 1174132](https://www.1point3acres.com/bbs/thread-1174132-1-1.html) |
| 10 | **Shard Rebalance** | 4 帖 | overlap ≤ limit：动后面的区间以减少数据移动 | [1p3a 1166300](https://www.1point3acres.com/bbs/thread-1166300-1-1.html) |
| 11 | IP/CIDR Iterator（5 问全要）、Version Dependency（二分+大代码量）、Resumable Iterator、cd/pwd 路径解析（4 part：normalize→绝对→~→symlink）、machine topology、spreadsheet、chatbot OOP 重构 | 中低频 | — | solutions.py 有大部分 |

> 题库完整版：[1p3a OpenAI 题库页](https://www.1point3acres.com/interview/problems/company/openai)（184 题，last updated 2026-07）· [hack2hire OpenAI](https://www.hack2hire.com/question-bank/companies/openai/coding-questions)（GPU Credits II 频率 10/10、Toy Language 10/10、Snapshot Social Graph 9/10、KV Store 9/10）

## 3. AI/ML Coding 题池（RS/MLE 轨核心，可 overfit）

| 题目 | 频率 | 解法要点 |
|------|------|---------|
| **Transformer Bug Hunt**（400 行 PyTorch 找 4 bug） | 12 帖 | 经典 4 bug：① pos embedding 初始化错 ② attention mask 没设 -inf ③ 缺 loss.backward() ④ projection 层错误。follow-up 改分类器。问时空复杂度（A@B 的 FLOPs/内存） |
| **Autograd / matmul forward+backward** | 6 帖 | 手推 dL/dA = dL/dC @ Bᵀ, dL/dB = Aᵀ @ dL/dC；写最小 autograd 节点图。RS 轨 "AI coding I 是 autograd" |
| **Streaming Entropy**（流式/分块熵） | 4 帖 | 数值稳定：log-sum-exp；分块合并用 running max + running normalizer（同 online softmax） |
| **Noisy Annotators 分类器** | 9 帖 | 多标注者找低质量标注者（与多数投票/gold 对比一致率），剔除后重训对比 —— 直接对口你的数据工作 |
| **NumPy 1-NN → Wx+b** | 8 帖 | 全向量化（广播算距离矩阵，argmin），follow-up 改写成神经网络形式 |
| **KV cache 实现 / Debug MiniGPT** | PracHub 2026-04 | decode 循环维护 K,V 拼接；手推 matmul backward |
| **Math Reasoning：stopping time / inference time 期望** | 4 帖（RS 专属轮） | 概率递推/期望线性性；排队论直觉。2026-05-31 RS onsite 实测：inference time 概率 + 矩阵乘 + load balancing + 数值稳定 softmax（[thread-1178705](https://www.1point3acres.com/bbs/thread-1178705-1-1.html)） |

## 4. System Design 题池

| 题目 | 频率 | 要点 |
|------|------|------|
| **Payment System** | 20 帖 #1 | hold 与扣款分离、batch 半夜统一扣、idempotency、reconciliation |
| **Design Sora**（视频生成编排） | 19 帖 #2（2026-04 上新） | 本质 GPU job scheduler：外部 GPU pool 波动、worker 随时被 terminate → checkpoint/重试/幂等是核心 |
| **Chess / Chess.com** | 9 帖 | 匹配、实时对战、倒计时、cache 存什么 |
| **Cloud IDE / Colab** | 4-6 帖 | 500k 并发、workspace 生命周期、resume < 5s |
| 长尾：Slack、rate limiter、CI/CD、webhook、crossword、ChatGPT 前后端 | 低频 | 一开始就 cover scale（cache/sharding），别等追问 |
| ML SD（MLE 轨）：RAG 检索、企业 ChatGPT、从未标注语料挖掘新数据 | 低频 | 对口你的数据管线经验 |

### 2026-06/07 实战补充（论坛帖，已剔除机器生成内容、仅留交叉验证条目）

- **店面标配已是 SD+coding 双轮**（60min×2）：多个 6-7 月报告组合为 {Sora 或 KV store SD} + {感染题 / GPU Credits}。
- **Sora SD 的正确打开方式**（Staff 过经原话）："essentially just design a task scheduler"——重点：受限 GPU 资源、**worker preemption 后的重调度**、任务完成通知用户、checkpoint/幂等。DevBox/Cloud IDE 也在店面 SD 池里。
- **题干读起来像小说是故意的**：多人反馈 problem statement 极长但核心逻辑简单——先花 3-5 分钟剥离叙事找核心操作，别边读边写。
- **全对仍可能挂**：高赞帖（GPU Credits + KV store 双双做完，4 天后拒）印证——完成度是必要条件不是充分条件，评分还看代码质量、沟通、速度余量。"close call" 会被 recruiter 标记 6 个月后重面。
- **环境坑**（单一来源，谨慎参考）：编程环境默认按钮是 "Run Test Case" 而非 "Run Main"，有人浪费 7-8 分钟——开场先确认怎么跑代码。
- 拒信节奏：当天到 4 天不等；BQ 出现过 "what if AI causes unemployment" 这类开放题。

## 5. BQ / Deep Dive

- **Technical Deep Dive**（17 帖，gated 轮）：45min slide 讲最强项目，挂点 = 沟通清晰度。用 TableBench RankAgent 或 Reflection mid-training pipeline，练"给非本方向研究员讲清楚"。
- **HM BQ**（17 帖）：Why OpenAI（必须深思）、AGI/安全观、为什么不去 Google/Anthropic、加速项目的 tradeoff、不 ship 的项目。
- Reference check：offer 前，别让它成为惊喜。

## 资源

- 本地：`../02_coding_practice/openai/solutions.py`（2641 行全解）、`../01_company_notes/openai/questions.md`（40+ 原帖面经）、`../00_reports_and_plans/final_report_v2.md` 第一部分
- [1p3a OpenAI 题库](https://www.1point3acres.com/interview/problems/company/openai) · [hack2hire OpenAI](https://www.hack2hire.com/question-bank/companies/openai/coding-questions) · [interviewing.io OpenAI guide](https://interviewing.io/openai-interview-questions) · [deep-ml OpenAI RS 合集](https://www.deep-ml.com/collections/OpenAI%20Research%20Scientist%20Interview%20Prep)
