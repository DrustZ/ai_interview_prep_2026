# GDM / OpenAI / Anthropic 冲刺包（2026-07-10 更新，全部本地可离线）

## 包结构

| 位置 | 内容 | 用法 |
|------|------|------|
| [openai.md](openai.md) / [anthropic.md](anthropic.md) / [gdm.md](gdm.md) | 三家攻略：流程 + 题池 + 解法 + 打法（含 Anthropic take-home/culture 专节） | **主阅读材料** |
| **[interactive_1p3acre/](interactive_1p3acre/)** | **交互式题库网页 App**（双击 index.html，离线）：1p3a 布局，左侧 filter + 列表，点进去看题目/答案/帖子/链接，含解锁工具跳转。203 题、48 题含正文 | **首选入口，最方便** |
| **[1p3a-openai.md](1p3a-openai.md) / [1p3a-anthropic.md](1p3a-anthropic.md)** | 一亩三分地会员版完整题库（markdown 版，同 App 数据）：6 篇情报 briefings + 解锁编辑版题解（OAI 26 / ANT 20）+ 未解锁帖 URL + qbank 元数据表 + OJ 题表 | 想直接读 md 时用 |
| [core-ml.md](core-ml.md) | 20 道必背理论题 + 手写题单 + 已有材料→轮次映射 | 理论复习索引 |
| **`drills/`** | **PyTorch 冷写训练包**：8 个模块（attention/熵/损失/GRPO/采样/autograd/KV cache/捉虫），每个自带测试、已验证全绿；协议见 drills/00_README.md | **每日手写训练核心**（针对"概念懂但写不快"） |
| **`question-bank/`** | 爬取全量编译版：openai(99条)/anthropic(108条)/gdm(98条)/理论与MLSD(75条)/hack2hire完整题解(10题25子题含官方讲解+insights+follow-up) | 按公司刷题面，全部带原文 URL |
| **`deepml-problems/`** | deep-ml 官方开源题库 165 题本地版：每题 description + learn.md + solution.py + starter_code.py + tests.json | 离线刷手写题（starter_code 冷写 → 对 solution） |
| `raw/` | 原始 JSON（380 条爬取数据、h2h API 缓存、论坛帖）+ build_question_bank.py（可重新编译） | 查细节 / 再加工 |
| `../../.venv/` | Python 环境（torch 2.8 + numpy），drills 和 deepml 题都用它跑 | `../.venv/bin/python xxx.py` |

**每日核心循环（手写不流利的对症下药）**：上午 1 个 drills 模块冷写（协议见 drills/00_README.md）→ 下午从 deepml-problems 挑 2-3 题用 starter_code 限时写、跑 tests.json 对拍 → 晚上 question-bank 过当天目标公司的一个类别。

三家一表对比：

| | OpenAI | Anthropic | GDM |
|---|---|---|---|
| coding 风格 | 系统实现题，跑通测试，题池可 overfit | 编号题库，recruiter 提前告知题号 | Google 风格 LC med/hard，必须跑通 |
| ML 轮 | AI coding（autograd/entropy/bug hunt） | GRPO debug / agent loop / config system | fundamentals 快问快答 + ML design |
| 最大挂点 | 完成度门槛 + deep dive 沟通 | **culture 轮泛泛而谈** | ML design 轮 + team match |
| AI 工具 | 新试点允许（agentic round） | 部分轮鼓励用 Claude | **全程禁用** |
| 你的相对优势 | ML coding 池 ≈ 你的日常工作 | RL/agent/data batcher 轮全部对口 | eval infra 与 post-training 深挖 |

## 一周计划（7/10 – 7/16，每天 ~12h 按你自己的 time-block 节奏）

穿插日程：TikTok 7/12 · bundle grid 7/13 · Applied Compute 7/14 · Hark 7/16-17 · Extend 7/17 · Meta ping 7/15

### D1 · 7/10（五）— OpenAI coding 池 overfit ①
- 上午：感染题 5 小问一次写穿（计时 60min）+ GPU Credits I/II；对照 `../02_coding_practice/openai/solutions.py`
- 下午：transformer bug hunt（自己用 GPT 造 4 个 bug 练）+ streaming entropy 手写（log-sum-exp 分块）
- 晚上：core-ml.md 必背题 #1-#10 出声背（定义→公式→trade-off）；Anthropic OA 重写 1 套（banking）

### D2 · 7/11（六）— OpenAI coding 池 ② + math reasoning
- 上午：social network+snapshot、toy language、data labeling scheduler（各 45min 计时）
- 下午：autograd/matmul backward 手推手写 + 1-NN→Wx+b + 数值稳定 softmax；stopping time 概率题（RS math reasoning 池）
- 晚上：TikTok OA 准备（你原计划）；必背题 #11-#20

### D3 · 7/12（日）— TikTok 面试日（轻量）
- 面试外：Anthropic OA 家族重写 1 套（in-memory db + backup）；读 Core Views on AI Safety + RSP，写 culture 轮三个故事草稿（价值冲突/利他不利己/moral dilemma）

### D4 · 7/13（一）— Anthropic 专项日（你的 bundle grid 日）
- 上午：Weighted Data Batcher 完整实现（seeded RNG + checkpoint resume）+ Q1 crawler 多线程版
- 下午：**GRPO debug 轮全套**（把 anthropic.md 里 3 类 bug + ratio≠1 的判别实验自己讲一遍并写码验证）+ Claude API agent loop 手写跑通
- 晚上：SD Q1 GPU Inference Serving + Prompt Playground 书面练习（Google Doc 限时 40min 纯文字写设计）

### D5 · 7/14（二）— Applied Compute 面试 + GDM 基础日
- 面试外上午：GDM coding 真题全过（Trie/Snapshot Array/Best Meeting Point/概率 Dijkstra/rand7；每题 ≤18min）
- 下午：GDM quiz 模拟——用 `reflection/theory-mte-quiz-and-stories.md` 快问快答 + L1/L2、ELBO、Bayes 彩球出声推导
- 晚上：官方 prep PDF 通读；Google 高频 Top30 扫一遍思路

### D6 · 7/15（三）— GDM ML design + 分布式日（Meta ping 日）
- 上午：distributed training design 完整练一遍（显存数学→ZeRO→TP/PP→checkpoint）+ EEML tensor parallelism tutorial
- 下午：eval infrastructure design（用你 Reflection 的工具经验组织答案）+ `reflection/design-rl-on-video-game.md` + `case-study-rl-bottleneck.md` 各自讲一遍
- 晚上：deep-ml P0 题单清尾（GQA/MQA、KV cache 估算、PagedAttention）

### D7 · 7/16（四）— SD + BQ 收口（Hark 面试日）
- 上午：OpenAI SD 双题：payment + Sora（GPU job scheduler 框架）各 35min 计时
- 下午：三家 BQ 话术定稿：Why OpenAI / Why Anthropic（具体 value + 亲历例子 + 批判性思考）/ Why GDM；Technical Deep Dive slides 过一遍（明天 Extend 也用得上）
- 晚上：错题回顾；per-company 一页 cheat sheet

### 每日固定
- 必背题滚动复习 20min（出声，五层结构）
- 手写一道 deep-ml P0（不看参考，一次写对为过）
- 面试后 30min 内写 recap（考了什么 → 更新对应公司 md）

## 关键提醒
1. **Anthropic 拿到题号立刻回来查 anthropic.md 对应条目**，把该题所有 follow-up 练到零容错。
2. **OpenAI RS 轨就是 overfit 游戏**：AI coding 池 ≈ {autograd, entropy, bug hunt, noisy annotators, 1-NN}，general 池 ≈ 感染/GPU credits/social network，math ≈ stopping time。bar 4433。
3. **GDM 禁 AI、答题要机制级**：L1 稀疏必须讲梯度机制，图复杂度必须说 O(V+E)。
4. 你的最大差异化武器是一手 post-training/RL/eval 经验——每一轮都主动把答案锚到"我在生产里怎么做的"。
