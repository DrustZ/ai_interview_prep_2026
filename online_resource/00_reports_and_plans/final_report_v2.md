# 顶尖AI公司面经全解析：OpenAI · xAI · Anthropic

**数据来源：一亩三分地论坛（2025年4月 – 2026年4月）**

本报告系统整理了OpenAI、xAI、Anthropic三家顶尖AI公司近一年内在一亩三分地论坛上公开的面经信息，涵盖面试流程、高频真题、详细解法、System Design题目、行为面试问题以及评论区中的宝贵补充信息。每条面经均附有原帖链接，方便读者查阅原文。

---

# 第一部分：OpenAI 面经全解析

OpenAI的面试以难度高、代码量大、强调"跑通所有测试用例"而著称。题库相对固定但变种丰富，面试平台通常使用 **CoderPad + Google Meet**。

## 1.1 面试流程概览

OpenAI的标准面试流程通常包含以下环节，从HR联系到最终结果大约需要2-6周时间。Recruiter通常通过LinkedIn主动联系候选人，也接受网上海投和内推。

| 环节 | 时长 | 内容 | 备注 |
|------|------|------|------|
| HR Call | 30 min | 确认背景、期望薪资、介绍面试流程 | 会问 Why OpenAI、对AGI的看法 |
| 技术电面 (Phone Screen) | 60-75 min | 1轮Coding 或 1轮Coding + 1轮SD | 有时两轮同一天，有时分开 |
| Onsite (Virtual/现场) | 4-5轮 | General Coding x 1-2, SD x 1, Deep Dive x 1, BQ x 1 | ML岗会加ML Coding或ML Design |
| Reference Check | — | 要求提供5个reference | 有人reference check后仍被拒 |

**关键信息**：OpenAI的Coding面试强调 **"practical, systems-oriented problem solving rather than algorithmic memorization"**，面试官明确表示 **"passing all the tests is all you need"**。代码必须能实际运行并通过所有测试用例，速度极其重要。

> 来源: https://www.1point3acres.com/bbs/thread-1174077-1-1.html

**面试Prompt示例**：

> "Coding exercises will ask you to implement components of well known systems or primitives." (60 min)

> "This interview focuses on practical, systems-oriented problem solving rather than algorithmic puzzles." (75 min)

## 1.2 高频Coding真题完整列表

根据收集到的数据，以下是OpenAI近一年内出现频率最高的Coding题目，按出现频率降序排列。

### 1.2.1 传染病模拟 (Infection / Plant Infection) — 绝对第一高频

这是OpenAI面试中出现频率最高的题目，几乎每周都有人报告遇到此题。题目通常分为5个递进的小问，60分钟内完成，至少需要做完前3问才算通过。

> 来源: https://www.1point3acres.com/bbs/thread-1171710-1-1.html
> 来源: https://www.1point3acres.com/bbs/thread-1164914-1-1.html

**完整题干**：

> Given a grid of plants. "X" stands for the infected plant, "." stands for the healthy plant. Every day each infected plant would infect at most its 8 neighbors if possible.

**Part 1**：给定矩阵，`X`代表感染植物，`.`代表健康植物。每天感染的植物会感染周围8个邻居。求多少天达到平衡态（no more plants can be infected）。

**解法**：使用BFS（广度优先搜索），维护一个 `newly_infected` 集合记录每天新感染的坐标，当集合为空时退出循环。

**Part 2**：增加 `I` 代表免疫植物，不会被感染。求多少天达到平衡态。

**解法**：在BFS中增加条件判断，只有邻居不是 `I` 才加入队列。

**Part 3**：被感染的植物在 `D` 天后会恢复并免疫。求多少天达到新的平衡态。

**解法**：维护一个HashMap，key为天数，value为该天恢复的坐标集合。也有人认为直接在最后感染天数上加 `D` 即可。

> **注意**：Part 3中"return的时间定义和前两个不一样，会off by one"。

**Part 4**：如果一个植物在生命周期中曾有至少 `K` 个感染邻居，它会在 `D` 天后死亡。求多少天达到新的平衡态。

**解法**：维护每个细胞的感染邻居计数数组 `m[i][j]`，当达到 `K` 时记录死亡时间。使用Level Order BFS，维护 `level_dict {(x,y): level}`，对每个cell计算是否触发K条件，找最大值 `max(level + D)`。注意：如果一个植物要死了，它就不可能Immune了，会影响 `lastImmuneDay` 的计算。

> 来源: https://www.1point3acres.com/bbs/thread-1171710-1-1.html (评论区)

**Part 5**：每天开始时可以选择烧毁一行或一列，设计算法最小化死亡总数。

**解法**：可能是贪心算法，在day 0烧。维护Map，key是row或col，value是该row/col当前处在death临界点上的植物个数，选择最大值的行/列烧毁。

### 1.2.2 GPU Credits — 第二高频

GPU Credits题目模拟GPU计算资源的分配和消耗，有两个版本（I和II）。

> 来源: https://www.1point3acres.com/bbs/thread-1165824-1-1.html
> 来源: https://www.1point3acres.com/bbs/thread-1165749-1-1.html

**题目概述**：实现一个GPU信用额度管理系统，支持添加信用额度（带时间戳和过期时间）、消耗信用额度、查询余额等操作。

**关键细节**：
- 需要clarify按什么顺序consume credit（通常按时间戳顺序）
- 面试官会要求看unit test来理解需求
- Follow-up可能要求将GPU的timestamp从integer改成float
- 版本II的不同点：当前credit不够subtract时，`getBalance` 返回 `None`

> **警告**：有面试者因为"写太快了"被怀疑使用LLM而被挂，建议"假装自己没见过"。来源: https://www.1point3acres.com/bbs/thread-1172810-1-1.html

### 1.2.3 玩具语言解析 (Toy Language / Tokenizer) — 高频

> 来源: https://www.1point3acres.com/bbs/thread-1163593-1-1.html

**题目描述**：实现一个简单的语言解析器。有一个toy language grammar，包含primitives（char, int, float）、generics（T1, T2等代称）和tuples。需要实现Node class表示各种类型，实现 `toString` 方法，以及 `infer_return` 函数来推断泛型的具体类型。

**解法要点**：通常需要实现词法分析（Lexer）和语法分析（Parser），使用栈或递归下降解析。如果发现类型匹配冲突需要报错。

### 1.2.4 Social Network — 高频

> 来源: https://www.1point3acres.com/bbs/thread-1166564-1-1.html
> 来源: https://www.1point3acres.com/bbs/thread-1168926-1-1.html

**题目描述**：实现社交网络的关注系统，通常有4问。

- **A**：建立follower/followee数据结构，支持 `update(A, B, t)` 和 `check(A, B, t)`
- **B**：改成双向查询
- **C**：给用户推荐用户。A→B→C, A→B→D, A→M→C，推荐C和D，优先C（因为C和A的关系有两个媒介）
- **D**：推荐时也要在指定的历史版本（snapshot）上推荐

### 1.2.5 版本依赖解析 (Version Dependency / Python Version) — 高频

**题目描述**：给定软件包及其依赖关系和版本号，实现版本解析系统。通常有4问（第4问是bonus）。

**关键信息**：
- 有三类testing cases：简单、大、有趣
- Part 1涉及binary search（有小变种）
- 代码量很大，完全不用在意优化，一直在不停写
- 提前练过了还是勉强写完

### 1.2.6 其他常见Coding题目

| 题目 | 时长 | 描述 | 来源 |
|------|------|------|------|
| KV Store / Serialize | 60 min | 实现持久化键值存储，处理字符串和字节的序列化/反序列化 | https://www.1point3acres.com/bbs/thread-1174132-1-1.html |
| IP CIDR Iterator | 60 min | 实现迭代器遍历CIDR块中所有IP地址，共5问（需全部完成） | https://www.1point3acres.com/bbs/thread-1165663-1-1.html |
| Memory Allocator | 75 min | 实现内存分配器，要求O(log N)，Python用sortedcontainers的SortedDict | https://www.1point3acres.com/bbs/thread-1162026-1-1.html |
| Resumable Iterator | 60 min | 实现可恢复的迭代器 | https://www.1point3acres.com/bbs/thread-1174077-1-1.html |
| Chat Message / Chatbot | — | channel中有多个bot，需对用户消息做出反应 | https://www.1point3acres.com/bbs/thread-1173168-1-1.html |
| Message Tree | — | 消息树结构实现 | https://www.1point3acres.com/bbs/thread-1164914-1-1.html |
| In Memory DB / Design SQL | — | 实现内存数据库，支持set/get/query by name/age/filter by id | https://www.1point3acres.com/bbs/thread-1165234-1-1.html |
| Encode Decode Strings | 75 min | 字符串编解码 | https://www.1point3acres.com/bbs/thread-1174077-1-1.html |
| Multithreading | 75 min | 多线程相关实现 | https://www.1point3acres.com/bbs/thread-1174077-1-1.html |
| Spreadsheet | — | 电子表格实现 | https://www.1point3acres.com/bbs/thread-1174077-1-1.html |
| 实现cd命令 | — | 文件系统路径解析 | https://www.1point3acres.com/bbs/thread-1174077-1-1.html |
| Battle Monster (怪兽对打) | 60 min | 2 player game，类似LeetCode style | https://www.1point3acres.com/bbs/thread-1166564-1-1.html |
| Shard Balancing / Overlapping Key Range | — | 在有最多重合限制的情况下重新平衡分片 | https://www.1point3acres.com/bbs/thread-1166300-1-1.html |
| Data Labeling Task Scheduler | — | 构造满足多个约束的调度方案 | https://www.1point3acres.com/bbs/thread-1173190-1-1.html |
| Text Buffer | — | Research Engineer岗，设计文本缓冲区数据结构 | https://www.1point3acres.com/bbs/tag/openai-9407-4.html |
| Machine Count and Topology | — | 低频题，implement receiveMessage | https://www.1point3acres.com/bbs/tag/openai-9407-4.html |

### 1.2.7 ML专项Coding题 (Research / Applied 岗)

**Transformer Debugging (变形金刚捉虫)** — ML岗高频

给定一个有Bug的Transformer实现（约400行PyTorch代码），要求找出并修复。通常有4个Bug：

> 来源: https://www.1point3acres.com/bbs/thread-1165833-1-1.html

1. Position Embedding初始化错误
2. Attention Mask未设置为 `-inf`（负无穷）
3. 缺少 `loss.backward()`
4. Projection层相关错误

Follow-up：改成分类器（Classification），把最后一层改了，具体test程序是给好的，跑通就行。

**准备建议**：看Karpathy的YouTube免费课，用GPT产生假Bug练习，手写一遍Transformer主要结构。

**Vectorized Computation (Numpy)** — ML岗

要求不使用for循环，仅使用Numpy的向量化操作实现特定算法（如1NN最近邻分类器）。下一步可能要求将运算过程apply到一个neural network。

**Classifier with Noisy Annotations** — ML岗

给定带有多个标注者（annotators）的数据集，不同标注者给出不同标签。需要找到质量差的标注者，忽略他们后看分类器是否变好。

> 来源: https://www.1point3acres.com/bbs/thread-1168926-1-1.html

## 1.3 System Design 高频题

OpenAI的系统设计题目既有传统后端设计，也有AI应用场景设计。以下按频率排列：

| 题目 | 频率 | 关键考察点 | 来源 |
|------|------|-----------|------|
| Chess.com (在线象棋) | 最高频 | 匹配系统、实时对战、倒计时机制、cache存什么怎么存 | https://www.1point3acres.com/bbs/thread-1164914-1-1.html |
| Payment System | 最高频 | Idempotency、hold与实际扣款分离、batch处理、reconciliation | https://www.1point3acres.com/bbs/thread-1173136-1-1.html |
| Slack | 高频 | DM vs Channel、Redis Pub/Sub、large channel用pull model、multi-device | https://www.1point3acres.com/bbs/thread-1164140-1-1.html |
| CI/CD System | 高频 | 流水线设计、scalability | https://www.1point3acres.com/bbs/thread-1164914-1-1.html |
| Webhook | 高频 | 事件推送系统 | https://www.1point3acres.com/bbs/thread-1162896-1-1.html |
| Remote IDE / Google Colab | 中频 | 500k并发用户、创建/删除/suspend workspace、resume < 5s、failure modes | https://www.1point3acres.com/bbs/thread-1165242-1-1.html |
| Design ChatGPT | 中频 | 前端设计（conversation标题更新、自动滚动）、后端streaming | https://www.1point3acres.com/bbs/thread-1173168-1-1.html |
| YouTube / Video Storage | 中频 | 视频发布存储系统 | https://www.1point3acres.com/bbs/thread-1165234-1-1.html |
| Sora Video Generation | 低频 | scheduling + worker flow、GPU pool波动、failure scenario | https://www.1point3acres.com/bbs/thread-1166689-1-1.html |
| Calendar | 低频 | Apple/Google Calendar | https://www.1point3acres.com/bbs/thread-1162896-1-1.html |
| Short URL | 低频 | 短链接服务 | https://www.1point3acres.com/bbs/thread-1162896-1-1.html |
| Web Crawler | 低频 | 网络爬虫 | https://www.1point3acres.com/bbs/thread-1162896-1-1.html |
| Crossword Puzzle | 低频 | 面试官原创题，设计解谜系统 | https://www.1point3acres.com/bbs/thread-1163593-1-1.html |
| GitHub Actions | 低频 | 支持大量用户的CI系统 | https://www.1point3acres.com/bbs/thread-1165234-1-1.html |

### Slack SD详细面经

> 来源: https://www.1point3acres.com/bbs/thread-1164140-1-1.html

面试者按Hello Interview的思路回答，先讲DM后讲Channel。用Redis Pub/Sub解释消息推送。Large channel用pull model，DM和small channel用push model。面试官问能否都统一成pull model，面试者认为不行（client需要刷新才能收到信息，用户体验不好）。Multi-device讨论中，面试官认为inbox会bloat up。面试者建议收到一次后删除所有session的inbox记录。

**教训**：一开始design应该就把scale这块cover掉（加cache、sharding），不要等到最后才提。

### Payment System SD详细面经

> 来源: https://www.1point3acres.com/bbs/thread-1165749-1-1.html

模拟线下消费刷卡的场景（而非电商场景），分为 hold 和实际扣款两部分功能。Payment service需要把请求给到下游的credit card provider来扣款，实际扣款是半夜统一时刻按batch扣的。重点问了怎么处理reconciliation。

## 1.4 Behavioral / Culture Fit 面试

OpenAI的BQ面试非常重视候选人对AI安全和AGI的理解。

> 来源: https://www.1point3acres.com/bbs/thread-1168926-1-1.html

**常见问题**：
- 为什么要来OpenAI？（必须深思熟虑）
- 为什么离开现在的工作？之前跳槽都是什么原因？
- 对AGI怎么看？
- AI safety对你来说意味着什么？
- 如果你的顶头上司说不安全测试就上线AI，你会怎么做？

## 1.5 重要备考建议（来自面经总结）

1. **速度是第一要务**：OpenAI面试"只讲快不讲efficient"，代码怎么简单怎么来，不要被LeetCode思维局限。
2. **必须跑通测试**：面试官明确要求5问全写出来、跑通、with good test coverage。
3. **不要写太快**：有人因为"Java作为verbose language不可能写那么快"被怀疑用LLM而被挂。
4. **hack2hire网站**：传染病以外的很多题（Chat Message、Toy Language、GPU Credits、KV Store、Message Tree、Design SQL）在hack2hire网站上都有，30美元/月。
5. **面试语言**：Python最常用，也有人用Java、C++、TypeScript。面试官不一定熟悉你的语言。

> 来源: https://www.1point3acres.com/bbs/thread-1164914-1-1.html

---

# 第二部分：xAI 面经全解析

xAI是马斯克旗下的AI公司，面试风格硬核，极其看重工程实现能力和底层系统理解。面试节奏极快，每轮面完基本24小时内就定下一轮，不分节假日或深夜。

## 2.1 面试流程概览

xAI的面试流程因岗位不同差异较大，但整体特点是**速度极快、效率极高**。

| 岗位类型 | 流程 | 特点 |
|----------|------|------|
| MTS/SWE | 15min Screen → 3轮Tech (各45min) → Meet the Team (45min) | 每轮24h内反馈 |
| Exceptional SWE | Recruiter Call → 4hr Take-home OA → Coding → HM面 → Founder Call | 极速流程 |
| ML/Infra Engineer | 15min Screen → 2-3轮Tech → Research Talk | 偏ML方向 |
| SRE/Data Engineer | 15min Screen → Tech面 | 强背景匹配 |

### 15分钟Screen（初筛）

这是xAI面试的标志性环节。一个team的engineer来15分钟聊项目，看是否match team需求。

> 来源: https://www.1point3acres.com/bbs/thread-1163676-1-1.html

**常见问题**：
- 简单自我介绍
- Most Challenging Project（必问）
- What do you wanna work on at xAI?
- 深挖项目细节，具体讲有挑战的点在哪里，如何解决
- 为什么想跳槽，why xAI?

**注意事项**：
- 有人8分钟就被结束面试，第二天收到拒信
- 面试官可能迟到快10分钟且不道歉
- 背景不match直接不会推进正式面试
- 有时会被问基础八股：Process和Thread的区别、Array在memory里怎么存、Smart Pointer是什么

> 来源: https://www.1point3acres.com/bbs/thread-1171571-1-1.html

### 4小时Take-home OA（Exceptional Engineer岗）

在CodeSignal平台上完成，给两周时间但开始做只能做4小时。需要Docker化并上传到GitHub私有目录。

> 来源: https://www.1point3acres.com/bbs/thread-1161166-1-1.html

**7道题目自选一道**：
1. 写一个安卓APP
2. 写Grok Search
3. Full-Stack Sales App Tool
4. 写一个RAG
5. Twitter Insight Platform
6. 另一个Backend App（和第5题很像，是坑）
7. 其他

**关键建议**：必须开Cursor或AI辅助生成boilerplate，纯手敲绝对写不完。Docker化可以等4小时倒计时结束后再搞定。

## 2.2 高频Coding真题

xAI的Coding题目偏向底层系统和并发编程，与OpenAI和Anthropic风格明显不同。

### 2.2.1 分布式矩阵乘法 (Distributed Matrix Multiplication) — ML/Infra岗

考察分布式系统直觉和NumPy基础，给未完成的starter code需要补全两种并行策略。

> 来源: https://www.1point3acres.com/bbs/thread-1171574-1-1.html

**Data Parallel (DP)**：每个rank计算 `a_chunk @ b` 然后发给rank 0。

**Fully Sharded Data Parallel (FSDP)**：模拟PyTorch FSDP里forward hook的实现。在每个rank上针对B做all gather（每个rank把自己的shard send给所有其他rank，然后recv其他所有shard）。

完整的Starter Code包含 `Communicator` 类（用Queue模拟跨设备通信）、部分实现的 `dp_mat_mul` 和空白的 `fsdp_mat_mul`。

### 2.2.2 动态批处理推理引擎 (Dynamic Batching Inference Engine) — MLE岗

给定一个"模拟语言模型"接口，需要实现批量采样/解码流程。核心难点在于**动态批处理**：不同序列会在不同时间结束，导致batch会逐渐出现空槽位。

> 来源: https://www.1point3acres.com/bbs/thread-1158056-1-1.html

需要处理的结束条件：达到max_tokens上限、生成到stop token或stop sequence。

实现思路：初始化阶段尽可能把batch填满 → 迭代解码循环调用模型 → 序列完成与回收 → 动态补位从等待队列中拉取新序列。

### 2.2.3 Group Test GPU节点 — MLE岗

有N个节点，可以调用 `test(S)` 函数测试一个节点集合S。如果S中存在坏节点则返回False，全是好节点返回True。约束：test可并行调用但同一节点不能同时出现在多个并行test中，且 `|S| >= 2`。

> 来源: https://www.1point3acres.com/bbs/thread-1158056-1-1.html

解法思路：先找到一个好节点，然后用它去测试其他节点。

### 2.2.4 并发任务调度器 (Concurrent Job Scheduler) — SWE岗

35-40分钟内要解完还要能跑。考察并发编程能力。

### 2.2.5 其他常见题目

| 题目 | 岗位 | 描述 | 来源 |
|------|------|------|------|
| LRU变形 | SWE | 每个item带数量，算cap时不能把每个都当作一个 | https://www.1point3acres.com/bbs/tag/xai-9906-5.html |
| Versioned DB | SWE | 支持set, get, delete, get_at_version | https://www.1point3acres.com/bbs/tag/xai-9906-5.html |
| Token Limiter | SWE | 令牌限流器 | https://www.1point3acres.com/bbs/thread-1171162-1-1.html |
| LFU | SWE | 最不经常使用缓存 | https://www.1point3acres.com/bbs/tag/xai-9906-5.html |
| Task Scheduler | SWE | 任务调度器 | https://www.1point3acres.com/bbs/tag/xai-9906-5.html |
| In-Memory DB | SWE | 内存数据库 | https://www.1point3acres.com/bbs/thread-1131336-1-1.html |
| Parallelized Sort | Exceptional SWE | 手写并行排序 | https://www.1point3acres.com/bbs/thread-1161166-1-1.html |
| Concurrency题 | Infra | 非LeetCode原题，medium难度 | https://www.1point3acres.com/bbs/tag/xai-9906-5.html |
| DP题 | Infra | 常规动态规划 | https://www.1point3acres.com/bbs/tag/xai-9906-5.html |
| JSON数据处理 | SWE | 处理JSON数据 | https://www.1point3acres.com/bbs/tag/xai-9906-1.html |

### 2.2.6 System Design题目

| 题目 | 描述 | 来源 |
|------|------|------|
| Distributed KV Store | 分布式键值存储 | https://www.1point3acres.com/bbs/thread-1171162-1-1.html |
| Design Post View (PUT and GET) | 帖子查看系统 | https://www.1point3acres.com/bbs/tag/xai-9906-5.html |

## 2.3 xAI完整面试流程详细案例

### 案例1：MLE岗全套面经

> 来源: https://www.1point3acres.com/bbs/thread-1158056-1-1.html

**15分钟Screen**：聊项目，问了most challenging project，deep dive了一些细节。

**第一轮Tech (45min)**：Dynamic Batching Inference Engine。给了starter code，需要实现batch采样和动态补位逻辑。

**第二轮Tech (45min)**：Group Test GPU节点。需要设计算法找出所有坏节点。

**20分钟Research Talk**：展示研究成果。

**Meet the Team (45min)**：准备45分钟presentation，讲自己最牛的项目、为什么要加入xAI、想做什么。

### 案例2：ML/Infra Engineer面经

> 来源: https://www.1point3acres.com/bbs/thread-1171574-1-1.html

**15分钟Screen**：聊了项目，问了为什么想来xAI。

**第一轮Tech**：分布式矩阵乘法，需要补全DP和FSDP两种实现。

**第二轮Tech**：被问了更深入的分布式系统问题。

**结果**：第二轮后被拒。

### 案例3：Exceptional SWE面经

> 来源: https://www.1point3acres.com/bbs/thread-1161166-1-1.html

**Recruiter Call**：简单聊背景。

**4小时Take-home OA**：选了其中一道题，用Cursor辅助完成。Docker化在时间结束后补充。

**Coding面试**：手写并行排序（Parallelized Sort），需要开两个摄像头。

**HM面**：项目深挖 + Why xAI。

**Founder Call**：据说是和高层聊。

## 2.4 Research Talk / Meet the Team

xAI的Meet the Team环节需要准备一个45分钟的presentation，主要讲自己最牛的项目、为什么要加入xAI、想做什么。这个环节的通过率并不高，有人在此环节被挂。

> 来源: https://www.1point3acres.com/bbs/thread-1163676-1-1.html

对于MLE岗位，还有20分钟的Research Talk，需要展示研究成果。

## 2.5 重要备考建议

1. **15分钟Screen极其关键**：准备好如何在极短时间内展示自己的技术深度和项目经验。
2. **底层知识必备**：Process vs Thread、内存管理、Smart Pointer等基础知识可能被直接问到。
3. **Coding需要开两个摄像头**：面试监控较严。
4. **工作强度大**：面试官坦诚会比较累，80h+工作时间。公司没有食堂，员工都是点外卖。
5. **面试官可能疲惫**：所有面试官看起来都很疲惫，最长tenure好像是6个月。

---

# 第三部分：Anthropic 面经全解析

Anthropic以对"AI Safety"的执着而闻名，面试不仅考察技术能力，还极其看重候选人的价值观和对安全的理解。题库相对较小，建议全部准备。

## 3.1 面试流程概览

Anthropic的面试流程相对标准化，题目编号系统（Q1-Q6）在候选人Portal中可见。

| 环节 | 时长 | 内容 | 备注 |
|------|------|------|------|
| HR Phone Screen | 30 min | Why Anthropic、背景、身份、timeline | 会问是否读了safeguard文档 |
| OA (CodeSignal) | 90 min | Recipe Manager / Task Management / In-Memory DB | 可选是否开启屏幕监控 |
| Phone Screen (Coding) | 60 min | Q1-Q6中的一道 | Portal中可看到题号 |
| Onsite (5轮) | 各60 min | Coding + SD + Culture + HM + Deep Dive | Culture轮通过率很低 |
| Team Match + Reference | — | 2个reference check | Debrief后进行 |

**面试平台**：CodeSignal（OA）+ Google Meet + 在线IDE（面试）。面试官会给接口和模板代码。

**重要提示**：Anthropic有 **hard remote policy**，必须25% onsite。Remote员工每个月都得飞去公司onsite一整周。

> 来源: https://www.1point3acres.com/bbs/thread-1158823-1-1.html

### HR Phone Screen 常见问题

> 来源: https://www.1point3acres.com/bbs/thread-1152296-1-1.html
> 来源: https://www.1point3acres.com/bbs/thread-1156340-1-1.html

- 你为什么想在Anthropic工作？
- 是什么让你开始寻找新的工作机会？
- 如果最终拿到多个offer，你的决策框架/评估标准是什么？
- 你最强的技术能力是什么？
- 你面试时会使用哪种编程语言？
- 是否读了safeguard文档？有什么感想？

**准备建议**：Recruiter在约时间时会发关于safeguard的文档，一定要仔细阅读。Recruiter大概率会问你读了没、有什么感想。

## 3.2 OA (Online Assessment) 题目

### 3.2.1 Recipe Manager — 高频OA

90分钟，4个Level，时间非常紧张。

> 来源: https://www.1point3acres.com/bbs/thread-1173693-1-1.html

**Level 1**：实现 `create_recipe`（有user_id, name, timestamp, 食材, steps）和 `rate_recipe`。注意区分大小写，都用lower。

**Level 2**：实现排序 for chef based on ranking。注意corner case。

**Level 3**：实现order edit，track order, meal, add等。

**Level 4**：实现cancel order + track record。

### 3.2.2 Task Management System — 高频OA

4问，整体不难。第三问最后一个part需要熟读requirement，第四问要用bisect。

### 3.2.3 In-Memory DB — OA

题目是in memory db，但有改动版本：没有compare set和compare delete，第四问是implement `backup()` 和 `restore()`。

### 3.2.4 其他OA题型

- **Toy Simulation of an App**：只要求TypeScript或Python，写app logic和refactoring。
- **Performance Engineer OA**：2小时take-home，optimize一个mocked system的core kernel function。之前可以用LLM的版本已被开源：`github.com/anthropics/original_performance_takehome`。

## 3.3 高频Coding真题（Q1-Q6编号系统）

Anthropic的Coding面试题目有固定编号（Q1-Q6），候选人可以在Portal中看到自己被分配的题号。

### Q1: Web Crawler (爬虫) 或 Image Processing (图片处理)

**语言决定题目**：用Python → 可能是Web Crawler或Image Processing；其他语言 → 通常是Web Crawler。

> 来源: https://www.1point3acres.com/bbs/thread-1167684-1-1.html

**Web Crawler**：
- 先实现单线程BFS爬虫（LC 1236）
- Follow-up：实现多线程版本
- Follow-up：如果有多个服务器如何优化（讲思路即可，不需要implement）
- 面试官会给URL fetcher和HTML Parser的接口
- 有人用Redis当central queue storage with 1 host server access the queue and assign slave servers to batch process

> 来源: https://www.1point3acres.com/bbs/thread-1160362-1-1.html

**Image Processing**：

> 来源: https://www.1point3acres.com/bbs/thread-1154439-1-1.html

- 有m个图片，n个pipeline，每个Pipeline有k个操作
- 6种transformation：grayscale, flip horizontally, flip vertically, scale, blur, rotate
- 前三个无参数，后三个有参数
- 需要用Python库（Pillow或scikit-image）处理
- Follow-up：大图片处理，使用ProcessPoolExecutor加速
- 考察搜索文档和快速使用库的能力

**详细步骤**：有4个folder（small images, big images, out, transformations）。先用small images做测试并save output图片到out folder。每一个transformation json file里面会有一个到多个transformation，如果有多个需要sequentially apply到图片上。大图片需要用ProcessPoolExecutor因为图像处理是CPU密集型。

### Q2: LRU Cache 或 File Dedup (文件去重)

**LRU Cache**：

> 来源: https://www.1point3acres.com/bbs/thread-1148690-1-1.html

- 用法和Python `functools.lru_cache` 一模一样
- 需要实现 `generate_key(*args, **kwargs)` 生成hashable key
- Follow-up：crash后如何restore cache → 使用WAL（Write-Ahead Logging）方法
- 可以用OrderedDict或double linked list + dict实现

**File Dedup (文件去重)**：

> 来源: https://www.1point3acres.com/bbs/thread-1144078-1-1.html
> 来源: https://www.1point3acres.com/bbs/thread-1151849-1-1.html

- 在文件系统中查找重复文件
- 使用哈希函数（MD5/SHA256）计算文件指纹
- 讨论CPU密集型 vs I/O密集型
- 大文件如何处理、文件很多如何处理、实时检测如何做
- Follow-up：设计持续监控重复文件的系统（使用数据库维护哈希到文件的映射）
- Follow-up：海量文件使用MapReduce扩展

> **注意**：Recruiter给的提示是 "You should be familiar with handling parallelism/concurrency"，但不一定是Web Crawler，也可能是File Dedup或LRU Cache。来源: https://www.1point3acres.com/bbs/thread-1151625-1-1.html

### Q3: Stack Trace (调用栈解析)

> 来源: https://www.1point3acres.com/bbs/thread-1089271-1-1.html
> 来源: https://www.1point3acres.com/bbs/thread-1112538-1-1.html

**题目描述**：给定一系列调用栈的采样数据（包含时间戳和函数列表），要求将其转换为完整的执行追踪（Trace）。

```
s2 = [
    Sample(0.0, ['a','b','a','c']),  # a -> b -> a -> c
    Sample(1.0, ['a','a','b','c']),
]
# 输出: (s,a)(s,b)(s,a)(s,c)(e,c)(e,a)(e,b)(s,a)(s,b)(s,c)
```

其中 "s" 是 start，"e" 是 end。

**解法**：使用栈数据结构对比相邻采样，判断函数的进入（Start）和退出（End）。本身不难，只是需要处理input之后对于每一个Sample用stack存放并且对比决定输出。

**Follow-up**：只考虑连续出现N次的function。

**过关标准**：题和Follow-up全写完并且能各跑过1-2个test case。

### Q4: Mode/Median

具体题目细节较少，但有面经提到"注意读题"。

### Q5: LeetCode Style Question

Prompt是LeetCode style question。具体题目信息较少。

### Q6: Tokenizer

> 来源: https://www.1point3acres.com/bbs/thread-1111070-1-1.html

**题目描述**：实现一个tokenizer。

1. 找出给定代码中的bug
2. 修改后继续找出bug
3. 根据提供的implementation写正确的tokenizer

使用longest match策略：

```python
vocab = {"app": 1, "apple": 2, "UNK": -1}
tokenize("apple", vocab) -> [2]
tokenize("bbb", vocab) -> [-1, -1, -1]
```

**Optimize 1**：预计算max word length，减少搜索范围。

```python
def tokenize(text: str, vocab: dict) -> list:
    tokens = []
    i = 0
    max_len = max((len(w) for w in vocab if w != "UNK"), default=0)
    while i < len(text):
        matched = False
        for j in range(min(i + max_len, len(text)), i, -1):
            s = text[i:j]
            if s in vocab and s != "UNK":
                tokens.append(vocab[s])
                i = j
                matched = True
                break
        if not matched:
            tokens.append(vocab["UNK"])
            i += 1
    return tokens
```

**Optimize 2**：合并连续的UNK token。

```python
# tokenize("appbbbapp", vocab) -> [1, -1, 1]  (连续的-1合并为一个)
result = []
i = 0
while i < len(tokens):
    result.append(tokens[i])
    if tokens[i] == -1:
        while i + 1 < len(tokens) and tokens[i + 1] == -1:
            i += 1
    i += 1
return result
```

## 3.4 System Design 高频题

Anthropic的SD题目也有编号系统（Q1-Q5），紧密围绕大模型服务展开。

### SD Q1: Inference API / Batch GPU Requests

> 来源: https://www.1point3acres.com/bbs/thread-1161165-1-1.html

**Prompt**: "We will evaluate how you would design scalable, secure, and reliable systems to solve a complex problem."

设计一个LLM推理API，将多个请求组合成Batch发送给GPU处理。考察点包括请求路由、负载均衡、Race Condition处理以及GPU内存瓶颈的理解。

### SD Q2: Prompt Playground

> 来源: https://www.1point3acres.com/bbs/thread-1152783-1-1.html

**Prompt**: "You'll work through the design of a product. Some areas you may cover are UX and user flows, system design, data design, and scaling."

和传统SD很不一样，没有要求画图，就是Google Doc纯聊。重点在UX、workflow、超长Prompt（10MB+）怎么处理。问得很细。

### SD Q3: System Metrics Design

> 来源: https://www.1point3acres.com/bbs/thread-1152058-1-1.html

**Prompt**: "We will evaluate how you would scale, monitor and optimize an existing system in production. The focus will be on aspects of a ML driven system outside the model architecture itself."

### SD Q4: 1-1 Chat System

> 来源: https://www.1point3acres.com/bbs/thread-1173701-1-1.html

**Prompt**: "You'll focus on systems design and don't need specialized ML knowledge or research skills. This will be a system design question to evaluate how you would design scalable and reliable systems to solve a complex problem."

### SD Q5: Data Infrastructure

只有data相关岗位会遇到。

### 其他SD题目

- **Cloud Storage Stream**：给定一个big file，需要从cloud storage stream到1000台机器上，有bandwidth限制。

## 3.5 新题型（2026年新增）

Anthropic近期引入了多种新的面试题型：

| 题型 | 描述 |
|------|------|
| Agents Interview | "This interview will test writing code with LLMs as a building block, and prompting... create an agent" |
| Experiment Design | 实验设计 |
| Design Doc Review | EM岗位，review一个design doc（可能是平时的doc改编） |
| Neural Network Fundamentals | 神经网络基础技术面试 |
| RL Fundamentals | RL基础，debug和改进RL training |
| ML Configuration System | ML配置系统 |
| Prompting and Engineering with LLMs | LLM提示工程 |

**Research Engineer/Scientist 店面四选一**：
1. Coding problem-solving
2. Coding and Design
3. ML Configuration System
4. Prompting and Engineering with LLMs

## 3.6 Anthropic完整面试流程详细案例

### 案例1：5轮Onsite详细面经

> 来源: https://www.1point3acres.com/bbs/thread-1171160-1-1.html

**店面**：Web Crawler（网虫题），一个小时就只问这一个。

**VO第一轮**：File Dedup（稳健驱虫）。没有刁钻的followup，基本是讨论怎么规模化。

**VO第二轮**：Prompt Playground（提示词乐园 - SD）。Google Doc纯聊，没有画图。

**项目深挖**：整体聊得还算谈笑风生。

**HM面**：面试官是白女，面相有点Karen。

**Culture Round**：主要是安全相关的问题。

**结果**：挂了。拒信模板："touch design, cannot provide more feedbacks. Love to see you again after one year."

### 案例2：全套+Coding总结面经

> 来源: https://www.1point3acres.com/bbs/thread-1167684-1-1.html

提供了完整的Coding题目分类和解法代码（anthropic.zip附件），包含：
- Q1 Web Crawler（单线程→多线程）
- Q2 File Dedup（哈希→分布式→MapReduce）
- Q3 Stack Trace（栈对比→连续N次filter）
- Q6 Tokenizer（longest match→优化→合并UNK）
- SD Q1 Inference API
- SD Q2 Prompt Playground
- Culture Fit问题集
- BQ问题集

### 案例3：Research Engineer面经

> 来源: https://www.1point3acres.com/bbs/thread-1158568-1-1.html

**第一轮**：准备PPT present目前的work（用了两周前自己的conference talk）。

**第二轮**：Coding - Find Duplicate Files。

**加面**：Image Processing（blur, flip等操作）。

**结果**：两天后说挂了，feedback是coding不够strong。

## 3.7 Culture Fit — 极其重要

Culture轮是Anthropic面试中通过率最低的环节，必须认真准备。

> 来源: https://www.1point3acres.com/bbs/thread-1171160-1-1.html

**核心问题**：
- Why Anthropic?（必须深思熟虑）
- 对AI safety的看法，为什么对你很重要？
- 你有没有做过什么利他不利己的事情？
- 大家会说AI很risky，那为什么还要去做？你怎么看？
- 和谁观点不一样？有没有moral dilemma？
- Tell me a time: failed project，如何依然从里面找到impact
- Tell me a time: conflict during cross-functional collaboration，以及如何resolve

> 来源: https://www.1point3acres.com/bbs/thread-1159248-1-1.html

## 3.8 Behavioral / HM面

**HM面常见问题**：
- Complex project深挖：role是什么、有什么challenge、有什么预料之中的challenge
- 如何影响road map
- 如何mentor别人
- Most impactful project细节

**Project Deep Dive**：需要准备一个20分钟左右的presentation，然后详细聊project。

## 3.9 重要备考建议

1. **题库小，全部准备**：Anthropic的题库相对较小，建议把所有已知题目都准备一遍。
2. **不要只准备Web Crawler**：即使Prompt提到concurrency，也可能考File Dedup或LRU Cache。
3. **Culture轮是关键**：准备好关于AI Safety的深刻见解，举出personal的例子。
4. **被认为见过题会被挂**：有人因为做得太好被认为见过题而被拒。
5. **拒信模板**："Touch design, cannot provide more feedbacks. Love to see you again after one year."
6. **EM岗没有Design**：EM面试是Design Review和组里做的东西非常相似，怀疑就是随便找一个平时的design doc改了改拿出来面试。

> 来源: https://www.1point3acres.com/bbs/thread-1162478-1-1.html

---

# 第四部分：综合备考策略

## 4.1 三家公司对比

| 维度 | OpenAI | xAI | Anthropic |
|------|--------|-----|-----------|
| 面试风格 | 系统编程，跑通测试 | 底层硬核，极速流程 | 题库固定，重视安全 |
| Coding重点 | 传染病、GPU、Toy Language | 分布式系统、并发 | 爬虫、文件去重、LRU |
| SD重点 | Chess、Payment、Slack | KV Store、分布式系统 | Inference API、Prompt Playground |
| BQ重点 | AGI、AI Safety | 项目深挖、Why xAI | AI Safety、Culture Fit |
| 面试平台 | CoderPad + Google Meet | 现场/Google Meet | CodeSignal + Google Meet |
| 反馈速度 | 1-2周 | 24小时内 | 2天-1周 |
| 特殊要求 | 代码必须跑通所有测试 | 可能需要两个摄像头 | 必须25% onsite |

## 4.2 通用备考建议

**Coding准备**：三家公司的Coding面试都强调实际工程能力而非算法竞赛。建议重点练习系统编程题（如实现KV Store、内存分配器、爬虫等），而非传统LeetCode。OpenAI的题在hack2hire网站上有（30美元/月），Anthropic的题在CodeSignal上有。

**System Design准备**：AI公司的SD题目越来越偏向AI应用场景（如Inference API、GPU调度、Video Generation），建议在传统SD基础上补充AI系统架构知识。推荐Hello Interview网站的SD教程。

**Behavioral准备**：三家公司都非常看重候选人对AI安全和伦理的理解，这不是走过场，而是真正的筛选标准。建议深入了解每家公司的AI安全理念，准备真实的个人经历来支撑你的观点。

**时间管理**：OpenAI和Anthropic的Coding面试都有严格的时间限制（60-75分钟），需要在规定时间内完成所有问题并跑通测试。建议平时练习时严格计时。

## 4.3 附件资源说明

本次整理过程中下载了两个重要的附件资源：

1. **openai.zip**（来自 https://www.1point3acres.com/bbs/thread-1173190-1-1.html ）
   - `openai_questions.py`（802行）：收集了40+道OpenAI面经题目和详细描述
   - `openai_solutions.py`（2641行）：包含所有题目的完整Python代码解法

2. **anthropic.zip**（来自 https://www.1point3acres.com/bbs/thread-1167684-1-1.html ）
   - `anthropic_questions_and_solutions.py`（9236行）：包含所有Coding题目（Q1-Q6）的完整解法代码
   - `anthropic_oa_recipt_manager.py`：Recipe Manager OA完整解法
   - `anthropic_oa_task_manager.py`：Task Manager OA完整解法
   - `anthropic_oa_in_mem_db.py`：In-Memory DB OA完整解法
   - `anthropic_oa_bank.py`：Bank OA完整解法
   - `anthropic_oa_cloud_storage.py`：Cloud Storage OA完整解法
   - `anthropic_oa_cloud_storage_version.py`：Cloud Storage Version OA完整解法
   - `anthropic_oa_employee.py`：Employee OA完整解法

这些附件是最宝贵的备考资源，建议仔细研读。所有代码文件均随本报告一同附上。
