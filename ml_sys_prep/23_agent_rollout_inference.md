# 23 · 为什么你的 SWE agent rollout 贵了 23 倍

⏱ 通读 25 分钟 · 配套代码 `labs/swe_data/rollout_cost.py`

---

## 从一个真实的账单开始

假设你要给 SWE agent 造训练数据。任务清单已经准备好了：5,000 个可执行任务，
每个采 8 条轨迹做 rejection sampling。你写好了 rollout 脚本，
起了 8 个 vLLM 副本，跑起来。

一天后你去看账单：**1,353 GPU-小时**。按 H100 每小时 2.5 美元算，3,383 美元。

这个数字对不对？取决于你有没有做对一件事。做对了的话，
同样这批数据是 **59 GPU-小时**，147 美元。

**差 23 倍。**

这篇讲的就是这 23 倍从哪来、为什么它极容易被无意中丢掉、以及怎么确认你没丢掉。

---

## 一、先搞清楚：为什么 agent 每一轮都要重发整段历史

很多人对这件事的直觉是错的，所以先从头理一遍。

Transformer 生成一个 token，需要它前面**所有** token 的 key 和 value 向量。
生成过程分两个阶段：

- **Prefill**：把输入的 N 个 token 一次性过一遍模型，算出 N 组 KV，存进 KV cache。
  这一步是**并行**的，但计算量正比于 N（attention 部分还有 N² 项）。
- **Decode**：一个一个吐 token。每吐一个，只需要算这一个新 token 的 KV，
  然后和 cache 里已有的做 attention。所以 decode 是**每 token 常数成本**。

关键在于：**KV cache 是「这次请求」的状态**。请求结束，显存回收，cache 就没了。

现在看 agent loop 长什么样：

```
第 1 轮：  [system + tools + repo上下文]                      → 模型输出 tool_call
           执行工具，拿到结果
第 2 轮：  [system + tools + repo上下文 + 第1轮输出 + 工具结果] → 模型输出 tool_call
           执行工具，拿到结果
第 3 轮：  [system + tools + repo上下文 + 第1轮 + 第2轮 ...]   → ...
```

**每一轮都是一次全新的 API 请求**，因为中间要跳出模型去执行工具。
而模型是无状态的 —— 它不记得上一轮。所以你必须把**整段历史重新发一遍**。

于是：

```
第 t 轮的 prompt 长度 = base + (t−1) × 每轮新增
累计 prefill = Σ_t (base + t × 每轮新增) = O(T²)
```

这个二次项就是那 23 倍的来源。

### 看见它

抽象公式没感觉，跑一下：

```bash
cd labs/swe_data
python rollout_cost.py --trace
```

```
轮次   prompt长度   缓存命中     实际prefill   累计prefill
──────────────────────────────────────────────────────────
  0       9,000           0         9,000         9,000  ← 第一轮本来就要全算
  1      10,100       9,000         1,100        10,100
  2      11,200      10,100         1,100        11,200
  ...
 11      21,100      20,000         1,100        21,100
──────────────────────────────────────────────────────────
      最终 prompt 21,100 tokens，累计 prefill 21,100
```

对比没有缓存的时候：

```
  0       9,000           0         9,000         9,000  ← 缓存失效，整段重算
  1      10,100           0        10,100        19,100  ← 缓存失效，整段重算
  2      11,200           0        11,200        30,300  ← 缓存失效，整段重算
  ...
 11      21,100           0        21,100       181,800
```

**盯住「实际 prefill」那一列的形状**：

- 有缓存：每轮都是常数 **1,100**（只有新增的部分要算）
- 没缓存：每轮 **递增 1,100**（整段重算）

12 轮就差了 8.6 倍。40 轮差 23.5 倍。**轮数越多差得越狠** ——
而 SWE 任务动辄 30–60 轮。

---

## 二、两个容易混淆的概念

上面说 KV cache 是「这次请求」的状态。那第 2 轮怎么可能命中第 1 轮的缓存？

因为有**第二层缓存**。这两个东西名字像，作用完全不同：

| | **KV cache** | **Prefix cache** |
|---|---|---|
| 作用域 | 单次请求内部 | **跨请求** |
| 存什么 | 这次请求所有 token 的 KV | 之前算过的 KV 块，按内容哈希索引 |
| 生命周期 | 请求结束就回收 | 留在显存里，LRU 淘汰 |
| 谁开的 | 引擎默认就有 | vLLM 要 `--enable-prefix-caching`；SGLang 默认开 |

**Prefix cache 的逻辑**：引擎把 prompt 切成固定大小的块（比如 16 个 token 一块），
对每个块的内容（连同它前面所有块）做哈希。新请求进来时，
从头逐块比对哈希 —— 匹配上的块直接复用已有的 KV，**不用重算**。

所以第 2 轮的请求虽然是新请求，但它的前 9,000 个 token
和第 1 轮**逐字节相同**，哈希也就相同，直接命中。

**注意「逐块从头匹配」这五个字。** 它有两个后果，是这篇后面所有内容的根源：

1. **匹配的是前缀，不是子串。** 你在中间改一个 token，
   从那一块起后面**全部失效**，哪怕后面 90% 的内容没变。
2. **必须逐字节相同。** 多一个空格、字典序不同、时间戳变了 —— 哈希就不一样。

---

## 三、五个会静默打掉缓存的写法

这些都不会报错。你的 pipeline 照常跑完，产出正确的数据，只是账单贵 20 倍。
**而且没有任何日志会告诉你。**

### 杀手 1：system prompt 里的时间戳

```python
# ❌ 看起来完全无害
SYSTEM = f"""You are a software engineering agent.
Current time: {datetime.now().isoformat()}
Working on: {repo_name}
...
"""
```

`datetime.now()` 每次调用都不一样。它在 prompt 的**最前面**，
所以**第一块的哈希每次都不同** → 后面全部失效 → **每一轮都是全量 prefill**。

跑一下数字：这个配置的累计 prefill 是 1.22M，
而完全不开 prefix cache 也是 1.22M —— **一模一样**。

> 你以为你开了缓存。实际上你等于没开。

**修法**：任何变化的东西都往后放。时间戳如果确实需要，
放在对话历史**之后**，作为最后一个 user message 的一部分。

```python
# ✅
SYSTEM = "You are a software engineering agent.\n..."   # 完全静态
messages = [
    {"role": "system", "content": SYSTEM},              # 稳定
    {"role": "user", "content": repo_context},          # 每个 repo 固定
    *history,                                           # 只追加
    {"role": "user", "content": f"[当前时间 {now}] 继续。"},  # 易变的放最后
]
```

### 杀手 2：工具 schema 的序列化顺序不稳定

```python
# ❌ 从 dict 或 set 生成工具列表
tools = [make_schema(name) for name in TOOL_REGISTRY]     # dict 遍历顺序
```

Python 3.7+ 的 dict 保序，所以这个例子**通常**是稳定的 —— 但只要注册过程涉及
`set`、多线程注册、或者按插件加载顺序，就不稳定了。
JSON 序列化时如果没有 `sort_keys=True`，嵌套 schema 里的键序也可能变。

工具定义在 prompt 极前面（system 之后），**它一变，后面全废**。

**修法**：显式排序 + 固定序列化。

```python
# ✅
tools = [make_schema(n) for n in sorted(TOOL_REGISTRY)]
tools_json = json.dumps(tools, sort_keys=True, ensure_ascii=False)
```

并且加一个断言，因为这类问题只有主动检查才会暴露：

```python
_TOOLS_FINGERPRINT = hashlib.md5(tools_json.encode()).hexdigest()
assert _TOOLS_FINGERPRINT == EXPECTED, "工具 schema 变了 —— 全库缓存作废"
```

### 杀手 3：context compaction

这个最讨厌，因为它是**你有意做的**，而且不做不行。

长任务跑到第 25 轮时上下文爆了，于是你把前 20 轮压缩成一段摘要：

```python
# 第 25 轮
if total_tokens > LIMIT:
    history = [summarize(history[:20])] + history[20:]
```

从缓存的角度看：**你重写了前缀**。第 21 个 token 之后的内容全变了，
第 25 轮之后的每一轮都要从压缩点开始重算。

代价（40 轮任务）：

| | 累计 prefill | vs 最优 |
|---|---|---|
| 不 compact | 52k | 1.0× |
| compact 一次（第 25 轮） | 87k | 1.7× |
| compact 三次（10/20/30 轮） | 142k | **2.7×** |

**修法有两个方向**：

**① 尽量晚、尽量少。** 别设一个保守的阈值就频繁压缩。
每次 compact 的成本是「当时的整段 prompt 重算一遍」，
所以越晚 compact 单次越贵，但总次数少反而更划算。上面的数字说明
一次 1.7× 比三次 2.7× 好。

**② 优先截断工具返回，而不是重写历史。** 工具返回（文件内容、测试输出）
是上下文膨胀的主因，而它们**分散在历史各处**。
如果你只截断**最近几轮**的工具返回，改动点在末尾，
前面的缓存全部保留：

```python
# ✅ 只动最近的，前缀不变
for msg in history[-3:]:
    if msg["role"] == "tool" and len(msg["content"]) > 4000:
        msg["content"] = msg["content"][:2000] + "\n...[truncated]"
```

这不能无限延后 compaction，但能把它推迟很多轮。

### 杀手 4：把检索内容插在前面

RAG 式的 agent 常见写法：

```python
# ❌
messages = [
    {"role": "system", "content": SYSTEM},
    {"role": "user", "content": retrieve(query)},   # 每个任务都不同
    {"role": "user", "content": task},
    *history,
]
```

检索结果每个任务都不一样。它一插在前面，**system 之后的所有内容对不同任务就不共享了**。
你损失的是**跨任务**的缓存复用 —— 而那恰恰是批量数据生成里最大的一块（见第六节）。

**修法**：检索内容放在「每个任务固定」的那一层，
而**比它更稳定的东西**（system、tools、仓库级上下文）必须在它前面。

### 杀手 5：对历史做「整理」

```python
# ❌ 这些都会改动早期 token
history = dedupe_messages(history)
history = sorted(history, key=lambda m: m["timestamp"])
history = [normalize(m) for m in history]
```

任何作用于**整段历史**的操作都有可能改动前缀。哪怕这次没改，
你也无法保证下次不改 —— 而缓存的收益完全依赖于「保证不改」。

**一条纪律，比记住上面五条都管用**：

> **agent loop 必须是 append-only 的。前缀只增不改。**

做不到 append-only 的操作（就是 compaction），
就当成一个明确的、有成本的、需要被记账的事件来对待。

---

## 四、prompt 该怎么排：从稳定到易变

上面五条其实是同一条原则的五个推论。把它正过来说：

**按「变化频率」从低到高排列 prompt 的每一段。**

```
┌──────────────────────────────────────┬─────────────────┐
│ system prompt                        │ 永不变          │
│ 工具 schema（排序固定）                │ 永不变          │  ← 断点 ①
├──────────────────────────────────────┼─────────────────┤
│ 仓库结构 / 项目约定 / 代码风格          │ 每个 repo 一份   │  ← 断点 ②
├──────────────────────────────────────┼─────────────────┤
│ 任务描述 / issue 正文 / 检索结果        │ 每个 task 一份   │  ← 断点 ③
├──────────────────────────────────────┼─────────────────┤
│ 对话历史（只追加）                     │ 每轮增长        │
├──────────────────────────────────────┼─────────────────┤
│ 当前时间、剩余步数预算、动态提示         │ 每轮都变        │
└──────────────────────────────────────┴─────────────────┘
```

**为什么这个顺序是唯一正确的**：缓存匹配从头开始逐块比对，
遇到第一个不匹配的块就停。所以任何一段的位置，
决定了「它变化时会作废多少东西」。把最易变的放最前面，
等于每次都从零开始。

三条水平线就是你的 **cache breakpoint** 该打的地方 ——
它们恰好对应三个不同的复用范围：全局、每 repo、每 task。

---

## 五、你怎么知道缓存真的生效了

这是最实用的一节。**别假设，去测。**

### vLLM

启动时开：

```bash
vllm serve <model> \
  --enable-prefix-caching \
  --max-model-len 65536 \
  --gpu-memory-utilization 0.92     # 离线批量可以拉高，给 KV cache 留足空间
```

然后看 metrics：

```bash
curl -s localhost:8000/metrics | grep prefix_cache
# vllm:gpu_prefix_cache_queries_total
# vllm:gpu_prefix_cache_hits_total
```

命中率 = hits / queries。**怎么判断这个数正不正常**：

| 命中率 | 说明 |
|---|---|
| < 20% | **基本等于没开**。去查第三节那五条 |
| 40–60% | 单轨迹内的缓存生效了，但跨请求/跨任务没利用上 |
| **60–85%** | agent 工作负载的正常区间 |
| > 90% | 很好，或者你的任务同质化太高（检查一下数据多样性） |

### 一个五分钟的自测

不用等跑完整个 campaign。发两次**完全相同**的请求，看第二次的 TTFT：

```python
import time, requests

payload = {"model": M, "messages": long_messages, "max_tokens": 1}

for i in range(2):
    t = time.time()
    requests.post(URL, json=payload)
    print(f"第 {i+1} 次 TTFT: {time.time()-t:.3f}s")
```

第二次应该**快一个数量级**。如果两次差不多 —— 缓存没生效，
先别跑 campaign，回去查配置。

然后再做一次**关键测试**：把 system prompt 里加一个 `time.time()`，重跑。
如果加了之后两次一样慢 —— 恭喜，你复现了杀手 1，
现在你知道该去自己的代码里找什么了。

---

## 六、多副本：开了缓存，但还是没用上

这一节讲一个只在生产规模才出现、但一出现就吃掉全部收益的问题。

你有 8 个 vLLM 副本，前面挂一个普通的负载均衡器（round-robin 或最少连接数）。
一条 agent 轨迹的 40 轮请求，会被**均匀打散**到 8 个副本上。

于是第 2 轮很可能落在副本 B，而第 1 轮的缓存在副本 A。**miss。**

命中概率 ≈ 1/8。算出来的账：

| | 累计 prefill | vs 最优 |
|---|---|---|
| 完美缓存 | 52k | 1.0× |
| 开了缓存，8 副本 round-robin | 1.07M | **20.7×** |

**你开了 `--enable-prefix-caching`，但你只拿到了 1/8 的收益。**

实测数据佐证：SGLang 有报告称 RadixAttention 把命中率从
「vLLM 无 sticky 路由的 18%」提到「默认配置 71%」——
差距主要不是引擎，是**路由**。

### 解法：cache-aware routing

路由器为每个副本维护一棵 **radix 树**（前缀树），记录该副本上缓存了哪些前缀。
新请求进来时，用 prompt 的前缀去每棵树里查最长匹配，
**把请求发给匹配最长的那个副本**。

同时要防止一个副本被打爆 —— 所以实际实现是「缓存亲和 + 负载兜底」：
当副本间队列长度差异超过阈值时，退化为最短队列。

现成的实现：

| 方案 | 说明 |
|---|---|
| **SGLang router** | radix 树 + 队列长度，缓存亲和与负载均衡自动切换 |
| **llm-d** | K8s 原生。实测 8 pods / 16 H100 上，相对 round-robin **TTFT 快 57×、吞吐 2×** |
| **Ray Serve** `PrefixCacheAffinityRouter` | Ray 生态 |
| 自己搓 | 离线批量场景下**最简单的方案**：按 `hash(task_id) % n_replicas` 做静态分片。同一个任务的所有轮次固定打到同一个副本，一行代码，不需要 radix 树 |

最后那条对造数据特别实用 —— 离线场景你完全掌控请求分发，
不需要通用路由器的复杂度。

---

## 七、批量生成的完整工作流

把前面所有东西串起来。假设：5,000 个任务、来自 200 个仓库、每任务 8 条轨迹。

### 第 1 步：按仓库分组排序任务清单

这是**最容易被忽略、收益又很大**的一步。

同一个仓库的任务共享那 6k 的仓库上下文（目录结构、约定、关键文件摘要）。
如果任务清单是随机顺序，这 6k 每个任务都要重新 prefill 一次；
如果按 repo 排序连着发，**只 prefill 一次**：

```
同一 repo 的 40 个任务：
  随机打散  →  40 × 6k = 240k
  按 repo 排序 →      6k
```

```python
# ✅ 一行的事
tasks.sort(key=lambda t: (t["repo"], t["task_id"]))
```

而且这条和第六节的路由配合起来才完整：**同 repo 的任务要落到同一个副本**。

```python
replica = hash(task["repo"]) % n_replicas     # 按 repo 分片，不是按 task
```

### 第 2 步：配置采样

数据生成是**离线批量**，和在线服务的最优点完全不同：

| | 在线 serving | **离线 rollout 生成** |
|---|---|---|
| 优化目标 | p99 延迟 | **吞吐 / 美元** |
| 并发 | 保守，留头寸应对突发 | **拉满**，让 KV cache 占满显存 |
| `--gpu-memory-utilization` | 0.8 左右 | **0.92+** |
| batch | 小 | 大 + chunked prefill |
| 请求被抢占 | 尽量避免 | **可接受** —— 有 prefix cache，重算便宜 |
| 投机解码 | 常开（降延迟） | **通常关** —— 吞吐场景收益小，还占显存 |

关于 `n`（每任务采几条）：**用引擎的 `n` 参数，别发 n 个独立请求**。

```python
# ✅
payload = {"messages": msgs, "n": 8, "temperature": 1.0}
```

但要知道**这只值 15% 左右**。因为 8 条轨迹在**第一轮就分叉了** ——
之后每条走自己的工具调用路径，什么都不共享。共享的只有那个 9k 的 base。

> 我一开始以为 n-sharing 是大头，算完才发现不是。
> **真正的 23× 来自单条轨迹内跨轮次的缓存**，不是跨样本的。
> 别把优化力气花错地方。

### 第 3 步：跑之前先烧一遍 base

第一个请求要 prefill 9k 的 base，这时候如果 100 个 worker 同时开跑，
它们会**各自**算一遍同样的 base（因为还没人把它写进缓存）。

```python
# ✅ 先单发一个请求把 base 预热进缓存
warm = {"messages": [sys_msg, tools_msg, repo_ctx_msg], "max_tokens": 1}
requests.post(URL, json=warm)
# 然后再放并发
```

小事，但在 200 个仓库 × 8 副本的规模下，省的是 200×8×9k = 14M token。

### 第 4 步：监控这三个数

跑起来之后，只盯三个：

```
1. prefix cache 命中率      → 掉到 40% 以下就停下来查
2. 平均每轮实际 prefill 量   → 应该接近常数（≈ 每轮新增），
                              如果它随轮次增长，说明缓存没命中
3. preemption 次数          → 偶尔可以，持续高说明显存配置太激进
```

第 2 条是最直接的诊断。它本质上就是第一节那张 trace 表 ——
**在生产里画出「实际 prefill vs 轮次」这条曲线，
是常数还是斜线，一眼就知道缓存有没有生效。**

---

## 八、如果你用 API 而不是自己起引擎

用 Claude 或 GPT 造数据时，机制不同但原理一样。

### Anthropic：显式控制

你要自己标记哪些块该被缓存：

```python
messages = [...]
system = [
    {"type": "text", "text": SYSTEM_PROMPT},
    {"type": "text", "text": TOOLS_DESCRIPTION,
     "cache_control": {"type": "ephemeral"}},          # ← 断点 ①
]
# 仓库上下文作为第一条 user message，也打断点
messages[0]["content"][-1]["cache_control"] = {"type": "ephemeral"}   # ← 断点 ②
```

要点：

- **最多 4 个断点**。对应第四节那三条水平线，正好够用（还剩一个机动）
- **写入 1.25× 基础价**（5 分钟 TTL）或 **2.0×**（1 小时 TTL）
- **读取 0.10×** —— 省 90%
- **命中会重置 TTL**。所以高频场景基本只付一次写入费

**TTL 5 分钟这件事对 rollout 有一个直接后果**（2026 年从 60 分钟改成 5 分钟的）：

> 同一个仓库的任务如果间隔超过 5 分钟，仓库上下文的缓存就过期了，
> 下一个任务要重新付 1.25× 的写入费。
>
> **所以「按 repo 分组」不只是排序问题，是时间局部性问题** ——
> 同 repo 的任务必须**连着跑完**，不能穿插别的仓库。

### OpenAI：自动

超过 1,024 token 自动缓存，按 128 token 递增匹配。不用你标记，
但也**不能控制** —— 所以第三节那五条杀手对它同样致命，
而且你更难诊断（没有显式的 cache_control 让你确认边界在哪）。

---

## 九、一页纸的自查

跑 campaign 之前，逐条过：

```
□ system prompt 里没有任何变化的内容（时间戳、随机 ID、计数器）
□ 工具 schema 排过序、序列化固定，并且有指纹断言
□ prompt 严格按「稳定 → 易变」排列，易变的在最后
□ agent loop 是 append-only；compaction 是有意识的、被记账的事件
□ 引擎开了 prefix caching（vLLM 要显式开）
□ 多副本有 cache-aware 路由，或者按 repo 做了静态分片
□ 任务清单按 repo 排序，同 repo 连着跑完
□ 跑之前预热了 base
□ 发两次相同请求测过：第二次 TTFT 快一个数量级
□ 监控里有「每轮实际 prefill」这条曲线，确认它是常数不是斜线
```

---

## 十、三句能在面试里说的

> 「agent rollout 的 prefill 是 O(T²) —— 每轮都要重发整段历史。
> 40 轮的 SWE 任务上，prefix cache 开不开差 23 倍。」

> 「但开了缓存不等于用上了缓存。system prompt 里一个时间戳就能让它完全失效；
> 多副本没有 cache-aware 路由的话，命中率掉到 1/N —— 有报告是 18% vs 71%。
> 我会先发两次相同请求测 TTFT，确认缓存真的生效，再放量。」

> 「所以造 SWE 数据本质上是个推理工程问题。三件事比换更快的卡有用：
> prompt 从稳定到易变排序、agent loop 保持 append-only、任务按 repo 分组调度。」

---

## 附：自己跑一遍

```bash
cd labs/swe_data
V=/Users/mingrui/Documents/codes/interview/.venv/bin/python
$V rollout_cost.py --trace     # 逐轮看 O(T²) 长什么样
$V rollout_cost.py             # 六种配置的对比 + campaign 总账
```

代码里有两个断言守着口径：
「每轮失效」必须**恰好等于**「完全不开缓存」，
「从不失效」必须等于「完美缓存」。
（第一版两个都不满足 —— 一个把新增 token 重复计了一次，
导致「每轮失效」比「不开缓存」还贵，那在物理上不可能；
另一个差了一个 PER_TURN，因为最后一轮的输出不会再被 prefill。
**这类口径 bug 只有写不变量断言才会暴露。**）

内化用 drill，不要重读：

```bash
$V ../../drill.py --topic inference
```

## 相关

- [`21_swe_agent_data.md`](21_swe_agent_data.md) —— SWE 数据 pipeline 的数据侧，这篇是它的推理侧
- [`18_case_distributed_inference.md`](18_case_distributed_inference.md) —— 在线 serving vs 离线批量的通论
- Applied Compute 的异步 RL staleness（[`../projects/onsite_prep/00_intel.md`](../projects/onsite_prep/00_intel.md)）——
  rollout 引擎和 trainer 的速度配平，是比这一层更上面的问题

**来源**：[vLLM Automatic Prefix Caching](https://docs.vllm.ai/en/v0.8.4/design/automatic_prefix_caching.html) ·
[llm-d 的 prefix cache 实测](https://llm-d.ai/blog/kvcache-wins-you-can-see) ·
[Ray Serve prefix-aware routing](https://docs.ray.io/en/latest/serve/llm/user-guides/prefix-aware-routing.html) ·
[为什么普通负载均衡会破坏 prefix caching](https://www.truefoundry.com/blog/kv-cache-routing-why-standard-load-balancers-break-prefix-caching-and-how-to-fix-it)
