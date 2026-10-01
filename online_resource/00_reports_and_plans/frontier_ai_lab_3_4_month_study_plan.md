# 3–4 个月高强度 Frontier AI Lab 面试学习规划

> 目标公司：OpenAI / Anthropic / DeepMind / xAI / 其他 frontier AI lab 或 AI infra startup  
> 目标岗位：MLE / Research Engineer / AI Infra Engineer / Software Engineer with LLM Systems focus  
> 你的当前状态：ML/CV 基础强，有论文和工程经历；LeetCode 手感需要恢复；LLM training、post-training、inference、parallelism、serving infra、AI safety 和 practical systems coding 需要系统补齐。  
> 核心策略：**先知识体系，再实现能力，再面试专项。**

---

## 目录

- [0. 总体判断](#0-总体判断)
- [1. 目标能力画像](#1-目标能力画像)
- [2. 学习原则](#2-学习原则)
- [3. 16 周总览](#3-16-周总览)
- [4. Phase 1：知识体系重建，Week 1–6](#4-phase-1知识体系重建week-16)
- [5. Phase 2：知识转实现，Week 7–10](#5-phase-2知识转实现week-710)
- [6. Phase 3：系统设计与项目表达，Week 11–12](#6-phase-3系统设计与项目表达week-1112)
- [7. Phase 4：公司专项与 Mock，Week 13–16](#7-phase-4公司专项与-mockweek-1316)
- [8. 每日执行模板](#8-每日执行模板)
- [9. 高频题库映射](#9-高频题库映射)
- [10. 必须掌握的知识地图](#10-必须掌握的知识地图)
- [11. Mock Interview 评分表](#11-mock-interview-评分表)
- [12. 项目 Deep Dive 准备](#12-项目-deep-dive-准备)
- [13. Behavioral / Culture / Safety 准备](#13-behavioral--culture--safety-准备)
- [14. 资源清单](#14-资源清单)
- [15. 最终交付物 Checklist](#15-最终交付物-checklist)

---

# 0. 总体判断

你现在最重要的不是马上开始刷 300 道 LeetCode，而是先补一层 **LLM + AI infra 的完整知识骨架**。

你已经有很强的 ML/CV 背景，这意味着你不是从零开始。但你要冲 OpenAI、Anthropic、DeepMind、xAI 这类公司，面试官不会只问“attention 是什么”。他们会进一步问：

- attention 的 shape 怎么走？
- training 和 inference 的 dataflow 有什么区别？
- KV cache 具体存什么？为什么 decode 阶段瓶颈不一样？
- dynamic batching 怎么处理不同 request 的生命周期？
- tensor parallel 的 column / row split，forward 和 backward 各需要什么通信？
- FSDP 为什么省显存？all-gather 和 reduce-scatter 在哪里发生？
- SFT、RLHF、DPO、PPO 的训练数据、loss、failure mode 是什么？
- 一个 LLM inference API 怎么设计成 scalable、secure、reliable？
- 如果你的模型有 safety risk，如何设计 eval、gate、rollback？

你的资料中高频题也印证了这一点：很多题不是传统算法，而是 **系统组件实现**：Dynamic Batch Inference Engine、Column/Row Tensor Parallel、FSDP、KV Cache、Radix Cache、LRU/LFU、Tokenizer/Trie、Versioned DB、Durable Cache、Task Scheduler、Distributed KV Store、RAG、Inference API 等。

所以这份计划按下面顺序设计：

```text
知识学习  →  小实现验证  →  高频题闭卷重写  →  系统设计  →  公司专项 mock
```

---

# 1. 目标能力画像

准备结束时，你应该达到 5 层能力。

## Level 1：概念准确

看到一个词，你能在 30 秒内说清楚：

- 它是什么
- 解决什么问题
- 输入输出是什么
- 常见 tradeoff 是什么

例子：

- KV cache：缓存每一层历史 token 的 K/V，避免 decode 时重复计算所有 prefix 的 K/V。
- FSDP：把参数、梯度、optimizer state shard 到不同 rank 上，forward 时 all-gather 需要用的参数，backward 后 reduce-scatter 梯度。
- DPO：直接用 preference pair 优化 policy 相对 reference model 的偏好，不需要显式训练 reward model 后再 PPO。

## Level 2：机制理解

你要能画图解释：

- Transformer block 数据流
- prefill / decode 数据流
- KV cache append / read 流程
- dynamic batching 状态机
- column TP / row TP 通信
- FSDP 参数 gather 与梯度 scatter
- RLHF pipeline
- RAG ingestion / retrieval / generation pipeline

## Level 3：代码实现

你要能在 35–75 分钟内写出简化版：

- LRU / LFU
- Trie tokenizer
- Normalize path
- Flatten / Unflatten
- Dynamic batch scheduler
- Radix cache
- Versioned DB / nested transaction
- Durable KV cache
- Multithread sort
- Task scheduler
- File dedup / web crawler
- Stack trace parser

## Level 4：系统设计

你要能设计：

- LLM Inference API
- Dynamic batching service
- GPU job scheduler
- RAG system
- Distributed KV store
- Prompt playground
- Evaluation platform
- Training data pipeline
- Model rollout / safety gate system

## Level 5：面试表达

你要能做到：

- 先 clarify，不急着写代码
- 先给简单可跑方案，再优化
- 边写边解释状态、invariant、edge cases
- 写完能跑 test
- follow-up 能自然扩展到 distributed、failure recovery、scaling、safety
- 项目 deep dive 可以讲 20–30 分钟，且能和 frontier AI lab 的需求对齐

---

# 2. 学习原则

## 原则一：每个知识点必须过四关

每学一个知识点，都要回答：

1. **What**：它是什么？
2. **Why**：为什么需要它？
3. **How**：它内部怎么工作？
4. **Code/System**：如果让我实现一个 toy version 或设计一个 service，我怎么做？

不要满足于“我听懂了”。只有能闭卷写出来、讲出来，才算掌握。

## 原则二：先建立 mental model，再刷题

你现在一上来刷 Dynamic Batching、FSDP、Radix Cache，容易变成背题。更好的顺序是：

```text
Transformer → Training → Tokenizer/Data → SFT/RLHF → Inference/KV → Parallelism → Serving System → Coding/System Design
```

## 原则三：每周必须有输出物

每周都要产出一个可复用 artifact：

- 一页图解
- 一个 toy implementation
- 一个 question bank solution
- 一个 system design answer
- 一个 mock 复盘文档

没有输出物，就说明你只是在“看资料”。

## 原则四：面试训练必须计时

OpenAI / Anthropic / xAI 的 coding 不是“最终会写出来就行”，而是时间内跑通。训练时必须逐渐从 90 分钟压到 60 分钟，再压到 45 分钟。

## 原则五：不要只追求算法最优

这些公司很多题考 practical implementation。优先级：

```text
正确性 > 可跑测试 > 清晰状态设计 > edge cases > complexity optimization
```

不要为了炫一个复杂最优解，把简单版本写挂。

---

# 3. 16 周总览

| 阶段 | 周数 | 主题 | 目标 |
|---|---:|---|---|
| Phase 1 | Week 1–6 | LLM 知识体系 | 建立 Transformer、training、SFT/RL、inference、parallelism 的完整 mental model |
| Phase 2 | Week 7–10 | 高频 coding + implementation | 把知识转成可写的系统组件代码 |
| Phase 3 | Week 11–12 | System design + project deep dive | 能设计 LLM 系统，能讲深自己的项目 |
| Phase 4 | Week 13–16 | 公司专项 + mock | OpenAI / Anthropic / xAI / DeepMind targeted preparation |

如果你只有 3 个月：

- Week 1–5：知识学习
- Week 6–9：coding + implementation
- Week 10：system design
- Week 11–12：company mock

如果你有完整 4 个月：按下面 16 周执行。

---

# 4. Phase 1：知识体系重建，Week 1–6

## Week 1：Deep Learning / PyTorch / Transformer 前置基础

### 本周目标

把 LLM 需要的 DL/PyTorch 基础重新压实。你不是重新学 ML，而是把和 LLM 面试最相关的部分补到“能解释 + 能写 toy code”的程度。

### 必学概念

- Tensor shape / broadcasting
- Matrix multiplication
- Autograd
- Forward / backward
- Cross entropy
- Optimizer state
- Mixed precision：fp32 / fp16 / bf16
- Parameter / gradient / activation memory
- Train loop / eval loop
- 梯度累积
- checkpointing 的直觉

### 你必须能回答的问题

1. 一个简单 MLP 的 forward 会保存哪些中间 activation？
2. 为什么 training 比 inference 更耗显存？
3. optimizer state 为什么可能比 parameter 本身还占内存？
4. fp16 和 bf16 的差别是什么？为什么大模型训练偏爱 bf16？
5. batch size、sequence length、hidden size 分别影响什么？
6. gradient accumulation 解决什么问题？它和真正增大 batch size 是否完全等价？

### 小实现

- [ ] 手写一个 MLP training loop
- [ ] 手写 cross entropy，不直接调用 PyTorch loss
- [ ] 打印每层 tensor shape
- [ ] 估算 parameter / activation / optimizer memory
- [ ] 加入 gradient accumulation

### 本周输出物

`week1_dl_pytorch_notes.md`

内容包括：

- 一张 train loop 数据流图
- parameter / gradient / activation / optimizer state 的区别
- 5 个常见 PyTorch bug
- 一个最小 MLP training loop

### 判断是否过关

闭卷解释：

```text
input → forward → loss → backward → optimizer.step → zero_grad
```

并且能解释每一步在显存里主要存了什么。

---

## Week 2：Transformer / Attention

### 本周目标

真正掌握 Transformer block，不只是知道 QKV。

### 必学概念

- Token embedding
- Positional embedding
- RoPE
- Q / K / V
- Self-attention
- Multi-head attention
- Causal mask
- Scaling by sqrt(d_k)
- MLP / FFN
- Residual connection
- LayerNorm / RMSNorm
- Pre-norm vs post-norm
- Decoder-only model
- Logits / sampling

### 你必须能回答的问题

1. 为什么 attention 是 `softmax(QK^T / sqrt(d_k))V`？
2. Q、K、V 的 shape 是什么？
3. 多头 attention 为什么不是简单重复算多次？
4. causal mask 为什么要加 `-inf`？
5. 训练时为什么可以并行处理整个 sequence？
6. decode 时为什么不能完全并行生成所有未来 token？
7. RoPE 和 absolute positional embedding 的直觉区别是什么？
8. pre-norm 为什么在深层 transformer 中更稳定？

### 小实现

- [ ] single-head attention
- [ ] multi-head attention
- [ ] causal mask
- [ ] 一个 GPT block
- [ ] transformer bug hunt：mask、position embedding、loss shift、softmax dim

### 推荐练习顺序

1. 先只实现 single-head attention。
2. 再把 head 拆成 `[B, H, T, D]`。
3. 再加 causal mask。
4. 再加 residual + norm + MLP。
5. 最后写一个 tiny decoder-only model。

### 本周输出物

`week2_transformer_from_scratch.md`

必须包含：

- Transformer block 图
- QKV shape 推导
- Causal mask 示例
- 训练 vs 推理数据流对比
- 5 个 transformer coding bug

### 判断是否过关

面试官问：

> “Given B=2, T=128, hidden=768, heads=12, what are Q/K/V shapes?”

你能不犹豫回答，并能继续解释 attention score shape。

---

## Week 3：Tokenizer / Dataset Prep / Pretraining

### 本周目标

理解“模型吃什么”，从 raw text 到 pretraining batch 的完整流程。

### 必学概念

- Token / token id / vocab
- BPE
- WordPiece
- SentencePiece
- special tokens
- chat template
- document boundary
- sequence packing
- loss masking
- data dedup
- quality filtering
- data mixture
- contamination
- next-token prediction
- pretraining eval

### 你必须能回答的问题

1. 为什么 tokenizer 会影响模型对中文、代码、数学的能力？
2. BPE 的核心思想是什么？
3. raw web data 怎么变成 training batch？
4. 为什么要 document packing？
5. 为什么要 dedup？
6. benchmark contamination 是什么？
7. pretraining 和 SFT 的数据格式有什么区别？
8. chat template 如果错了会发生什么？

### 小实现

- [ ] toy BPE tokenizer
- [ ] longest-match tokenizer
- [ ] chat template formatter
- [ ] dataset packing function
- [ ] loss mask builder
- [ ] contamination check toy example

### 本周输出物

`week3_data_tokenizer_pretraining.md`

必须包含：

- raw data → tokenized dataset → packed sequence → batch 的流程图
- tokenizer 常见坑
- pretraining data quality checklist
- 一个 toy packing 实现

### 判断是否过关

能从头讲：

```text
Common Crawl / code / books / papers → cleaning → dedup → filtering → mixture → tokenizer → packing → next-token loss
```

---

## Week 4：SFT / RLHF / DPO / Alignment

### 本周目标

理解 base model 如何变成 assistant。你不需要成为 RL 专家，但要能把 post-training pipeline 讲清楚。

### 必学概念

- Instruction tuning
- SFT
- Human preference data
- Reward model
- RLHF
- PPO
- DPO
- Rejection sampling
- KL penalty
- Helpful / harmless / honest
- Reward hacking
- Refusal behavior
- Safety eval
- Constitutional AI / RLAIF 的高层直觉

### 你必须能回答的问题

1. Base model、SFT model、RLHF model 的区别是什么？
2. SFT 为什么不能完全解决 alignment？
3. Preference pair 长什么样？
4. Reward model 怎么训练？
5. PPO 在 RLHF 里大概做什么？
6. DPO 为什么可以绕过显式 reward model？
7. KL penalty 为什么重要？
8. 什么是 reward hacking？
9. Safety eval 如何变成上线 gate？

### 小实现

- [ ] preference pair data format
- [ ] reward model ranking loss
- [ ] DPO loss toy implementation
- [ ] refusal eval set design
- [ ] SFT loss mask for assistant response only

### 本周输出物

`week4_post_training_alignment.md`

必须包含：

- SFT / RM / PPO / DPO 对比表
- RLHF pipeline 图
- reward hacking 例子
- safety eval checklist

### 判断是否过关

你能用 3 分钟给非 RL 背景工程师讲清楚 RLHF，再用 10 分钟给面试官讲清楚数据、loss 和 failure mode。

---

## Week 5：Inference / Decoding / KV Cache

### 本周目标

进入 AI lab 高频核心：模型怎么服务用户。

### 必学概念

- Prefill
- Decode
- Autoregressive generation
- KV cache
- KV cache shape
- Greedy decoding
- Temperature
- Top-k / top-p
- Repetition penalty
- Stop token / stop sequence
- Streaming
- Latency vs throughput
- Memory bandwidth bottleneck
- Context length vs memory

### 你必须能回答的问题

1. Prefill 和 decode 的计算模式有什么不同？
2. KV cache 存 K/V，为什么不存 Q？
3. KV cache 的 shape 大概是什么？
4. context length 变长，显存为什么增长？
5. decode 为什么经常 memory-bound？
6. top-k 和 top-p 有什么区别？
7. repetition penalty 通常怎么改 logits？
8. streaming response 是怎么实现的？

### 小实现

- [ ] toy autoregressive decode loop
- [ ] greedy / top-k / top-p sampling
- [ ] repetition penalty
- [ ] stop sequence matcher
- [ ] KV cache append/read mock
- [ ] request state machine

### 本周输出物

`week5_inference_kv_cache.md`

必须包含：

- prefill vs decode 对比
- KV cache shape 图
- sampling 方法对比
- 一个 toy decode loop

### 判断是否过关

能回答：

> “为什么 batching 对 decode throughput 很重要？为什么不是所有 request 都适合简单 static batching？”

---

## Week 6：Parallelism / Distributed Training / Serving Infra

### 本周目标

掌握大模型训练和推理里最常见的并行方式，尤其是 TP 和 FSDP。

### 必学概念

- Data Parallel
- Tensor Parallel
- Column Parallel Linear
- Row Parallel Linear
- Pipeline Parallel
- Sequence Parallel
- FSDP
- ZeRO-1 / ZeRO-2 / ZeRO-3
- All-reduce
- All-gather
- Reduce-scatter
- Activation checkpointing
- Communication/computation overlap
- GPU memory breakdown

### 你必须能回答的问题

1. Data parallel 切的是什么？为什么需要 all-reduce gradients？
2. Column parallel linear 的 forward 输出如何拼？backward 需要什么通信？
3. Row parallel linear 的 forward 为什么需要 all-reduce？
4. FSDP 和普通 data parallel 的区别是什么？
5. ZeRO-1/2/3 分别 shard 什么？
6. activation checkpointing 用计算换什么？
7. TP、PP、FSDP 在 training 和 inference 中用途有何不同？
8. 通信瓶颈出现在哪里？

### 小实现

- [ ] toy data parallel matmul
- [ ] toy column parallel linear
- [ ] toy row parallel linear
- [ ] FSDP all-gather / reduce-scatter mock
- [ ] 参数量和显存估算表

### 本周输出物

`week6_parallelism_fsdp_tp.md`

必须包含：

- DP / TP / PP / FSDP 对比
- Column TP / Row TP 图解
- FSDP forward/backward 通信图
- memory accounting example

### 判断是否过关

别人问 column TP / row TP backward，你不能只说 “all-reduce / all-gather”，你要能说清楚为什么。

---

# 5. Phase 2：知识转实现，Week 7–10

## Week 7：基础系统组件 Coding

### 本周目标

恢复 coding 手感，把最常见的 practical systems coding 题变成稳定送分题。

### 高频题

- Normalize Path
- Flatten / Unflatten
- LRU size variant
- LFU
- Trie / T9
- Tokenizer longest match
- Stack Trace parser
- File Dedup basic version

### 每题训练模板

每道题严格按这个流程：

```text
1. Clarify requirements
2. Define input/output
3. Choose data structure
4. State invariant
5. Implement simple version
6. Write tests
7. Discuss follow-up
```

### 本周时间安排

| Day | 任务 |
|---|---|
| Day 1 | Normalize Path + symlink follow-up |
| Day 2 | Flatten / Unflatten + iterator version |
| Day 3 | LRU size variant |
| Day 4 | LFU |
| Day 5 | Trie / Tokenizer |
| Day 6 | Stack Trace / File Dedup |
| Day 7 | 2 轮 60 分钟 mock + 复盘 |

### 本周输出物

`week7_system_coding_solutions/`

每题一个文件，包含：

- solution
- tests
- complexity
- follow-up notes

### 判断是否过关

至少 5 道题能在 45 分钟内写完并通过自测。

---

## Week 8：LLM Serving Coding

### 本周目标

把 Week 5 的 inference 知识变成代码实现。

### 高频题

- Dynamic Batch Inference Engine
- Continuous Batching Scheduler
- Request Queue / Active Batch
- Token Budget Manager
- Rate Limiter
- Prefix Cache / Radix Cache
- Repetition Penalty
- Stop Sequence Handling

### Dynamic Batching 的核心状态

你要会设计这些对象：

```python
Request:
    id
    prompt_tokens
    generated_tokens
    max_new_tokens
    stop_tokens
    status
    kv_cache_handle

Scheduler:
    waiting_queue
    active_batch
    completed
    max_batch_size
    step()
```

### 关键 edge cases

- request 一开始就超过 max length
- stop token 出现在 batch 中某个 request
- stop sequence 跨 token 边界
- 某个 request 结束后 batch 空槽如何补位
- timeout / cancellation
- priority request
- max batch tokens vs max batch size
- prefill request 和 decode request 是否分队列

### 本周时间安排

| Day | 任务 |
|---|---|
| Day 1 | 写最小 decode loop |
| Day 2 | 加 request state + stop token |
| Day 3 | 加 dynamic batching slot reuse |
| Day 4 | 加 stop sequence / timeout |
| Day 5 | 写 rate limiter / token budget manager |
| Day 6 | 写 radix cache insert / longest prefix |
| Day 7 | 75 分钟 Dynamic Batch mock |

### 本周输出物

`week8_llm_serving_engine/`

必须包含：

- dynamic_batch_engine.py
- tests.py
- README.md：设计说明和 follow-ups

### 判断是否过关

能完整讲：

```text
waiting requests → prefill → active decode batch → token generation → finished cleanup → slot refill → streaming output
```

---

## Week 9：Storage / DB / Durability / Transactions

### 本周目标

掌握 OpenAI/xAI/Anthropic 高频的 KV/DB/durable system 题。

### 高频题

- In-memory DB
- Nested transaction
- Versioned DB
- Durable KV cache
- WAL
- Snapshot
- Backup / Restore
- Distributed KV Store simplified

### 必学机制

- write-through
- write-back
- WAL
- snapshot
- compaction
- stale data cleanup
- idempotency
- consistency vs availability
- read path / write path

### 本周时间安排

| Day | 任务 |
|---|---|
| Day 1 | In-memory DB：set/get/delete/filter |
| Day 2 | Nested transaction：begin/commit/rollback |
| Day 3 | Versioned DB：get_at_version |
| Day 4 | Durable KV：WAL + restore |
| Day 5 | Snapshot + compaction |
| Day 6 | Distributed KV design mini answer |
| Day 7 | 2 轮 coding mock |

### 本周输出物

`week9_db_durability/`

必须包含：

- versioned_db.py
- durable_cache.py
- wal_notes.md
- distributed_kv_design.md

### 判断是否过关

能解释：

> “如果 cache crash 了，如何恢复？如果 WAL 很大怎么办？如果 value 很大、key 很少怎么办？”

---

## Week 10：Concurrency / Parallelism Coding

### 本周目标

把分布式和并发题变成可以写的代码。

### 高频题

- Multithread sorting
- Concurrent job scheduler
- Worker heap scheduling
- Producer-consumer queue
- Thread pool
- Web crawler single-thread → multi-thread
- File dedup parallel version
- Distributed matrix multiplication mock
- DP / FSDP toy implementation

### 本周时间安排

| Day | 任务 |
|---|---|
| Day 1 | Multithread merge sort |
| Day 2 | Thread pool + task scheduler |
| Day 3 | Heap worker scheduling |
| Day 4 | Web crawler multi-thread |
| Day 5 | File dedup parallel hashing |
| Day 6 | DP / FSDP toy matmul |
| Day 7 | xAI-style 45 分钟 mock |

### 本周输出物

`week10_concurrency_parallelism/`

必须包含：

- parallel_sort.py
- task_scheduler.py
- crawler_multithread.py
- distributed_matmul.py

### 判断是否过关

你能在 45 分钟内写出多线程排序的核心逻辑，并能解释：

- 如何 split
- 如何 merge
- thread 数怎么选
- GIL 对 Python CPU-bound 代码有什么影响
- 什么时候用 multiprocessing

---

# 6. Phase 3：系统设计与项目表达，Week 11–12

## Week 11：AI System Design

### 本周目标

把 LLM/AI infra 知识组织成 system design 答案。

### 必练题

1. LLM Inference API
2. Dynamic batching service
3. RAG system
4. Prompt playground
5. GPU job scheduler
6. Training data pipeline
7. Model evaluation platform
8. Distributed KV Store
9. Realtime chat / Slack-like system
10. Payment / idempotency system

### AI System Design 答题框架

```text
1. Requirements
   - functional
   - non-functional
   - scale
   - latency / throughput / cost / safety

2. API
   - request / response
   - streaming or non-streaming
   - idempotency key

3. Data model
   - request state
   - user/session/conversation
   - cache key
   - metrics/events

4. High-level architecture
   - gateway
   - scheduler
   - workers
   - storage
   - observability

5. Core flow
   - read path
   - write path
   - failure path

6. Scaling bottlenecks
   - GPU memory
   - queueing delay
   - hot keys
   - network bandwidth
   - storage IO

7. Reliability
   - retry
   - timeout
   - cancellation
   - checkpoint
   - rollback

8. Security / safety
   - auth
   - rate limit
   - abuse prevention
   - content safety
   - audit logs

9. Metrics
   - latency
   - throughput
   - GPU utilization
   - cache hit rate
   - error rate
   - quality / safety eval
```

### 本周输出物

`week11_ai_system_design/`

写 5 篇完整答案：

- `llm_inference_api.md`
- `dynamic_batching_service.md`
- `rag_system.md`
- `gpu_scheduler.md`
- `model_eval_platform.md`

### 判断是否过关

每道题能讲 35–45 分钟，并且不只是传统后端，而是能讲到 GPU / batching / cache / safety / metrics。

---

## Week 12：Project Deep Dive + Resume Story

### 本周目标

把你的 CV/video generation/inference acceleration/LLM work 包装成 frontier AI lab 喜欢的故事。

### 你应该准备 4 个项目故事

## Story 1：Video Generation / DiT Inference Acceleration

核心定位：

> 我不仅懂 generative model，也懂如何把模型优化到真实 serving 场景可用。

要讲清楚：

- 背景：video generation inference 成本高
- 技术挑战：attention / memory / latency / quality tradeoff
- 你做了什么：sparse attention / quantization / distillation / evaluation
- 难点：质量评估、layer sensitivity、drift metric、schedule search
- 结果：speedup / GPU savings / quality metrics
- 反思：哪些 metric 和 perception 不一致，如何改进

## Story 2：LLM Post-training / Evaluation / Safety

核心定位：

> 我理解模型上线不是只看 loss，还要看 quality、safety、regression、human preference。

要讲清楚：

- 数据来源
- SFT/RL/eval pipeline
- reward / preference / safety signal
- failure case
- launch gate
- monitoring

## Story 3：Large-scale Data Pipeline

核心定位：

> 我能处理 frontier model 训练/评估需要的数据质量、规模和工程问题。

要讲清楚：

- 数据格式
- filtering
- dedup
- quality check
- distributed processing
- monitoring
- downstream impact

## Story 4：Research Background / CV Paper

核心定位：

> 我有研究 taste，能从问题定义、方法设计、实验验证到 limitation 讲清楚。

要讲清楚：

- 研究问题
- 为什么重要
- 方法核心
- 实验设计
- ablation
- limitation
- 如何迁移到 foundation model / multimodal / robust AI

### Project Deep Dive 答题模板

```text
1. One-line summary
2. Why this problem matters
3. Constraints
4. Baseline
5. My contribution
6. Technical deep dive
7. Metrics
8. Failure cases
9. Tradeoffs
10. What I would do next
```

### 本周输出物

`week12_project_deep_dive/`

包括：

- 4 个 project story
- 1 个 20 分钟 presentation outline
- 1 个 “Tell me about yourself”
- 1 个 “Why frontier AI lab”
- 1 个 “Most challenging project”

---

# 7. Phase 4：公司专项与 Mock，Week 13–16

## Week 13：OpenAI 专项

### OpenAI 风格判断

OpenAI coding 更偏：

- practical systems-oriented problem solving
- 代码量大
- 多 part 递进
- 必须跑通 tests
- 不一定追求算法竞赛最优
- ML 岗可能加 transformer debugging / ML coding / ML design

### 必练 Coding

- Infection simulation
- GPU Credits
- Toy Language / Parser
- Social Network
- Version Dependency
- KV Store / Serialize
- IP CIDR Iterator
- Memory Allocator
- Resumable Iterator
- Transformer Debugging
- Vectorized NumPy computation

### 必练 SD

- Chess.com
- Payment System
- Slack
- CI/CD
- Webhook
- Remote IDE / Colab
- Design ChatGPT
- Sora/video generation scheduling

### 每天安排

| Day | 任务 |
|---|---|
| Day 1 | Infection simulation 75min + 复盘 |
| Day 2 | GPU Credits 60min + tests |
| Day 3 | Toy Language / Parser |
| Day 4 | Transformer Debugging |
| Day 5 | Payment or Slack SD |
| Day 6 | Full mock：coding + SD |
| Day 7 | OpenAI behavioral + project deep dive |

### OpenAI Behavioral 必答题

- Why OpenAI?
- 你怎么看 AGI？
- AI safety 对你意味着什么？
- 如果上级要求不做安全测试就上线，你怎么办？
- 你过去最能体现 ownership 的项目是什么？

---

## Week 14：Anthropic 专项

### Anthropic 风格判断

Anthropic 更偏：

- practical coding
- concurrency / file system / cache
- inference API / prompt playground
- culture / AI safety 权重极高
- 题库相对集中，值得全部准备

### 必练 Coding

- Web Crawler：single-thread → multi-thread → distributed discussion
- File Dedup
- LRU Cache + WAL restore
- Stack Trace
- Tokenizer
- Image Processing pipeline
- In-memory DB OA
- Recipe Manager OA
- Task Management OA

### 必练 SD

- Inference API / batch GPU requests
- Prompt Playground
- System Metrics Design
- 1-1 Chat System
- Data Infrastructure

### 每天安排

| Day | 任务 |
|---|---|
| Day 1 | Web Crawler |
| Day 2 | File Dedup |
| Day 3 | LRU + WAL |
| Day 4 | Stack Trace + Tokenizer |
| Day 5 | Inference API SD |
| Day 6 | Culture round mock |
| Day 7 | Full Anthropic mock |

### Anthropic Culture 必答题

- Why Anthropic?
- 你为什么关心 AI safety？
- 为什么 AI 很 risky 还要继续做？
- 讲一次你做过利他但不利己的事情。
- 讲一次 moral dilemma。
- 讲一次你和别人观点不同但最后解决了的问题。
- 讲一次 failed project，如何仍然产生 impact。

---

## Week 15：xAI 专项

### xAI 风格判断

xAI 更偏：

- 硬核系统实现
- 底层并发 / 分布式 / GPU infra
- 节奏快
- 15 分钟 screen 极其重要
- 项目 deep dive 必须非常锋利

### 必练 Coding / Infra

- Dynamic Batch Inference Engine
- Distributed Matrix Multiplication
- DP / FSDP mock
- Column / Row Tensor Parallel
- Normalize Path + symlink
- Parquet metadata + worker assignment
- KV Cache
- Radix Cache
- LRU size variant / LFU
- Versioned DB / nested transaction
- Durable Cache
- Distributed KV Store
- Rate Limiter
- Task Scheduler
- Multithread sorting
- Twitter Space active duration / top-k users

### 每天安排

| Day | 任务 |
|---|---|
| Day 1 | Dynamic batching 45min |
| Day 2 | Column/Row TP + FSDP oral drill |
| Day 3 | Radix Cache + KV Cache |
| Day 4 | Task Scheduler + Heap Worker |
| Day 5 | Versioned DB + Durable Cache |
| Day 6 | 15min screen + project deep dive mock |
| Day 7 | Full xAI mock |

### xAI 15 分钟 Screen 模板

你需要在 3 分钟内讲清楚：

```text
I am an ML/AI systems engineer with experience in generative AI, video generation, model evaluation, and inference optimization. My strongest recent work is around accelerating large video generation models while preserving output quality, where I worked on attention sparsity / quantization / evaluation / serving tradeoffs. I want to work on frontier model systems where model quality, infra efficiency, and deployment constraints meet.
```

中文理解版：

> 我不是只会训练模型，也不是只会后端。我最强的是在 model quality、inference efficiency、systems constraints 之间做工程决策。

### xAI 必答问题

- Most challenging project?
- Why xAI?
- 你最想在 xAI 做什么？
- 你如何看待高强度工作？
- 讲一个你解决底层系统瓶颈的例子。
- 如果你只有一周时间优化 inference cost，你怎么做？

---

## Week 16：DeepMind + 综合 Final Mock

### DeepMind 风格判断

DeepMind 更可能综合考察：

- ML fundamentals
- research engineering
- distributed training
- experiment design
- coding correctness
- scientific reasoning
- project depth

### 必练主题

- Transformer fundamentals
- Training loop
- Distributed training
- Evaluation design
- Research paper discussion
- Experiment design
- Project deep dive
- ML debugging

### 每天安排

| Day | 任务 |
|---|---|
| Day 1 | ML fundamentals oral exam |
| Day 2 | Transformer / training coding mock |
| Day 3 | Distributed training / FSDP mock |
| Day 4 | Experiment design / eval design |
| Day 5 | Project deep dive mock |
| Day 6 | Full interview loop mock |
| Day 7 | Final review + weak point patch |

### 最终目标

到 Week 16 结束时：

- 你应该能稳定完成 60–75 分钟 practical coding。
- 你应该能讲清楚 LLM training / post-training / inference / parallelism。
- 你应该有 5–8 个可复用 system design answers。
- 你应该有 4 个强 project deep dive story。
- 你应该有每家公司定制版 why company / safety answer。

---

# 8. 每日执行模板

## 标准 3 小时版

```text
30 min：复习昨天 notes / Anki
60 min：学习一个知识点
60 min：小实现或 coding
30 min：整理错题 / 口述总结
```

## 高强度 4 小时版

```text
45 min：概念学习
45 min：画图 + 口述
90 min：coding / implementation
30 min：test + edge cases
30 min：复盘文档
```

## 周末 6 小时版

```text
90 min：timed coding mock
60 min：复盘 + rewrite
90 min：system design mock
60 min：项目 deep dive / behavioral
60 min：补弱项
```

## 每天必须回答的 5 个问题

1. 今天学的东西解决什么问题？
2. 它的核心数据结构或状态是什么？
3. 输入输出是什么？
4. 有哪些 edge cases？
5. 面试官会怎么 follow-up？

---

# 9. 高频题库映射

## A. LLM / Inference Infra 高频

| 题目 | 对应知识 | 优先级 |
|---|---|---|
| Dynamic Batch Inference Engine | prefill/decode, scheduler, request lifecycle | P0 |
| KV Cache | attention inference, memory layout | P0 |
| Radix / Prefix Cache | trie, prefix sharing, cache eviction | P0 |
| Tensor Parallel | distributed matmul, communication | P0 |
| FSDP | distributed training memory | P0 |
| Repetition Penalty | decoding logits processing | P1 |
| Tokenizer | BPE / longest match / trie | P0 |
| Inference API SD | serving architecture | P0 |

## B. Practical Systems Coding 高频

| 题目 | 核心模式 | 优先级 |
|---|---|---|
| LRU | hashmap + doubly linked list | P0 |
| LFU | key map + freq map | P0 |
| Normalize Path | stack state machine | P0 |
| Flatten / Unflatten | traversal + template reconstruction | P0 |
| Versioned DB | history / snapshot / transaction | P0 |
| Durable Cache | WAL / snapshot / restore | P0 |
| Task Scheduler | heap / queue / worker state | P0 |
| Multithread Sorting | divide-merge + concurrency | P1 |
| Web Crawler | BFS + concurrency | P0 for Anthropic |
| File Dedup | hashing + IO/concurrency | P0 for Anthropic |
| Stack Trace | stack diff | P1 |

## C. System Design 高频

| 题目 | 重点 |
|---|---|
| LLM Inference API | batching, GPU routing, streaming, rate limit |
| RAG | ingestion, embedding, retrieval, reranking, grounding |
| Distributed KV Store | partitioning, replication, consistency |
| Prompt Playground | UX, prompt versioning, eval, long prompt handling |
| GPU Scheduler | queueing, fairness, cost, utilization |
| Payment | idempotency, hold/capture, reconciliation |
| Slack / Chat | push/pull, fanout, multi-device |
| Remote IDE / Colab | workspace lifecycle, cold start, storage |

---

# 10. 必须掌握的知识地图

## 10.1 Transformer Knowledge Map

```text
Token IDs
  ↓
Embedding + Position / RoPE
  ↓
Transformer Block × N
  ├── Norm
  ├── QKV Projection
  ├── Attention Scores
  ├── Causal Mask
  ├── Softmax
  ├── Weighted Sum V
  ├── Output Projection
  ├── Residual
  ├── MLP
  └── Residual
  ↓
Logits
  ↓
Loss or Sampling
```

必须会讲：

- training 时 logits 对所有 position 并行计算
- inference decode 时每次只生成下一个 token
- KV cache 缓存历史 K/V
- attention complexity 与 sequence length 有关

## 10.2 Training Knowledge Map

```text
Raw data
  ↓
Cleaning / filtering / dedup
  ↓
Tokenizer training / tokenization
  ↓
Packing / shuffling / batching
  ↓
Pretraining next-token prediction
  ↓
SFT instruction tuning
  ↓
Preference data
  ↓
Reward model / DPO / PPO
  ↓
Safety eval / regression eval
  ↓
Deployment
```

必须会讲：

- data quality 为什么比单纯 data size 重要
- contamination 为什么危险
- SFT loss mask 如何做
- preference pair 如何训练 reward model 或 DPO
- eval 如何防止模型退化

## 10.3 Inference Knowledge Map

```text
User request
  ↓
Tokenization
  ↓
Queue / scheduler
  ↓
Prefill
  ↓
KV cache creation
  ↓
Decode loop
  ├── select active batch
  ├── model forward one token
  ├── logits processing
  ├── sampling
  ├── KV cache update
  ├── stop condition
  └── stream token
  ↓
Final response
```

必须会讲：

- prefill 更像大矩阵计算
- decode 更容易受 memory bandwidth 和 batch utilization 限制
- continuous batching 提升 GPU utilization
- prefix cache 降低重复 prompt 的 prefill cost

## 10.4 Parallelism Knowledge Map

```text
Large model too big / too slow
  ↓
Data Parallel: replicate model, split data
  ↓
Tensor Parallel: split matrix inside layer
  ├── Column Parallel
  └── Row Parallel
  ↓
Pipeline Parallel: split layers
  ↓
FSDP / ZeRO: shard params/grads/optimizer states
  ↓
Hybrid 3D Parallelism
```

必须会讲：

- DP 需要 gradient all-reduce
- TP 需要 layer 内通信
- PP 有 pipeline bubble
- FSDP 用通信换显存
- ZeRO 分阶段 shard optimizer / grad / param

---

# 11. Mock Interview 评分表

## Coding Mock 评分

| 维度 | 0 分 | 1 分 | 2 分 | 3 分 |
|---|---|---|---|---|
| Clarification | 直接写 | 问很少 | 问清主要输入输出 | 主动澄清 edge cases |
| Data structure | 混乱 | 大致可用 | 合理 | 能解释 invariant |
| Implementation | 写不完 | 能写主体 | 能跑通 | 清晰、模块化、可扩展 |
| Testing | 无测试 | 简单测试 | 覆盖常见 case | 覆盖 edge + follow-up |
| Communication | 沉默 | 偶尔解释 | 边写边讲 | 清晰引导面试官 |
| Follow-up | 卡住 | 能讨论 | 能改代码 | 能扩展到 production |

目标：每轮总分 14/18 以上。

## System Design Mock 评分

| 维度 | 目标 |
|---|---|
| Requirements | 先明确功能和非功能需求 |
| Scale | 能给出合理量级假设 |
| API | 清楚 request/response |
| Architecture | 组件边界清晰 |
| Bottleneck | 能指出核心瓶颈 |
| Reliability | 有 retry/timeout/failure handling |
| Metrics | 有业务、系统、模型质量指标 |
| Tradeoff | 能比较至少两种方案 |

## Project Deep Dive 评分

| 维度 | 目标 |
|---|---|
| Problem importance | 说明为什么值得做 |
| Technical depth | 能深入到机制和细节 |
| Ownership | 说清楚你具体负责什么 |
| Metrics | 有量化结果或清晰评估 |
| Failure cases | 能讲踩坑和反思 |
| Relevance | 能连接到目标公司需求 |

---

# 12. 项目 Deep Dive 准备

## 12.1 你的主线定位

建议你把自己定位成：

> ML engineer with strong generative AI, model optimization, and AI systems experience, moving toward frontier model training and inference infrastructure.

中文理解：

> 我不是单纯 CV researcher，也不是传统后端。我更适合做 frontier model systems：理解模型，理解数据，理解推理成本，理解质量评估，也能把东西工程化。

## 12.2 你的优势

- 有 ML/CV research 背景
- 有 generative AI/video generation 经验
- 有模型评估和 inference acceleration 经验
- 有工业界大规模系统经验
- 有 Meta/TikTok 这类环境的产品化经验

## 12.3 你要补齐的短板

- LLM training/post-training 系统知识
- LLM serving infra 细节
- distributed training communication
- practical coding speed
- AI safety / alignment 表达

## 12.4 推荐一句话自我介绍

```text
I am a machine learning engineer focused on generative AI systems. My recent work sits at the intersection of model quality, inference efficiency, and production constraints, especially around video generation and model optimization. I am now looking to work more directly on frontier model training, post-training, and serving systems.
```

---

# 13. Behavioral / Culture / Safety 准备

## 13.1 通用问题

- Tell me about yourself.
- Why are you looking?
- Why this company?
- What is your most challenging project?
- Tell me about a conflict.
- Tell me about a failure.
- Tell me about a time you changed your mind.
- Tell me about a time you disagreed with leadership.
- How do you handle ambiguous projects?

## 13.2 AI Safety 问题

- What does AI safety mean to you?
- Why build powerful AI if it is risky?
- How would you handle pressure to ship an unsafe model?
- How should companies evaluate frontier models before launch?
- What failure modes worry you most?
- How do you balance helpfulness and harmlessness?
- What is your view on open-source frontier models?

## 13.3 回答原则

不要说空话：

```text
AI safety is important because powerful models can amplify both beneficial and harmful human intent.
```

这种太泛。更好的回答要具体：

```text
For me, AI safety means building technical and organizational mechanisms that prevent model capabilities from being deployed beyond our ability to evaluate and monitor them. Concretely, that includes pre-launch evals, red-teaming, staged rollout, monitoring, incident response, and the willingness to block launch when evidence is insufficient.
```

中文理解：

> safety 不是态度，而是流程、指标、gate、rollback、责任链。

---

# 14. 资源清单

## 14.1 Transformer / LLM Basics

- The Illustrated Transformer
- Andrej Karpathy: GPT from scratch / nanoGPT
- Stanford CS336: Language Modeling from Scratch
- Hugging Face NLP Course
- Jay Alammar transformer visualization

## 14.2 Training / Post-training

- InstructGPT paper
- DPO paper
- RLHF Book / open RLHF notes
- Hugging Face TRL examples
- Anthropic Constitutional AI / RLAIF related materials

## 14.3 Inference / Serving

- vLLM paper and docs
- PagedAttention
- TensorRT-LLM docs
- FasterTransformer / Triton examples
- Hugging Face Text Generation Inference
- llama.cpp architecture notes

## 14.4 Parallelism

- Megatron-LM paper/code
- DeepSpeed ZeRO paper/docs
- PyTorch FSDP docs/tutorials
- GPipe / pipeline parallel materials
- NVIDIA collective communication / NCCL concepts

## 14.5 System Design

- Hello Interview system design
- Designing Data-Intensive Applications
- ByteByteGo system design notes
- Real-world LLM inference architecture blog posts

## 14.6 Coding Practice

优先级：

1. 你资料里的 question bank
2. OpenAI / Anthropic / xAI 面经高频题
3. LeetCode design 类题
4. LeetCode medium 基础题
5. concurrency / file system / cache 题

---

# 15. 最终交付物 Checklist

## 15.1 知识笔记

- [ ] Transformer from scratch notes
- [ ] Pretraining data pipeline notes
- [ ] SFT / RLHF / DPO notes
- [ ] Inference / KV cache notes
- [ ] Dynamic batching notes
- [ ] Parallelism / FSDP / TP notes
- [ ] AI safety / eval notes

## 15.2 Coding 实现

- [ ] LRU
- [ ] LFU
- [ ] Normalize Path
- [ ] Flatten / Unflatten
- [ ] Trie / Tokenizer
- [ ] Dynamic Batch Engine
- [ ] Radix Cache
- [ ] Versioned DB
- [ ] Durable Cache
- [ ] Task Scheduler
- [ ] Multithread Sort
- [ ] Web Crawler
- [ ] File Dedup
- [ ] Distributed Matmul / FSDP mock

## 15.3 System Design 文档

- [ ] LLM Inference API
- [ ] RAG system
- [ ] Dynamic batching service
- [ ] Distributed KV store
- [ ] GPU scheduler
- [ ] Model eval platform
- [ ] Prompt playground
- [ ] Training data pipeline

## 15.4 面试表达

- [ ] Tell me about yourself
- [ ] Why OpenAI
- [ ] Why Anthropic
- [ ] Why xAI
- [ ] Why DeepMind
- [ ] Most challenging project
- [ ] Conflict story
- [ ] Failure story
- [ ] AI safety answer
- [ ] Project deep dive deck outline

## 15.5 最终通过标准

你准备好了的标志不是“我看完了所有资料”，而是：

- [ ] 任意 P0 coding 题，60 分钟内可写完 + 自测
- [ ] Dynamic batching / KV cache / TP / FSDP 能画图讲清楚
- [ ] SFT / RLHF / DPO 能讲数据、loss、failure mode
- [ ] LLM Inference API 能讲 45 分钟
- [ ] 项目 deep dive 能讲 20–30 分钟
- [ ] 每家公司 why company 都具体、不空泛
- [ ] AI safety 回答有工程细节，而不是价值观口号

---

# Appendix A：前 14 天详细执行计划

## Day 1：LLM 全流程大图

目标：从 user prompt 到 model response。

输出：

```text
User prompt → tokenizer → input ids → embedding → transformer blocks → logits → sampling → token → KV update → repeat → response
```

## Day 2：Tensor / Autograd / Loss

输出：

- MLP train loop
- cross entropy 手写
- backward 过程 notes

## Day 3：Single-head Attention

输出：

- Q/K/V shape
- attention score shape
- causal mask

## Day 4：Multi-head Attention

输出：

- `[B, T, C] → [B, H, T, D]`
- head merge
- projection

## Day 5：Transformer Block

输出：

- GPT block
- residual + norm + MLP

## Day 6：Training vs Inference

输出：

- teacher forcing
- label shift
- decode loop

## Day 7：Week 1 Review

输出：

- 1 页总结
- 5 个 bug
- 1 个 toy model

## Day 8：Tokenizer 概念

输出：

- longest-match tokenizer
- BPE notes

## Day 9：Dataset Packing

输出：

- packing function
- loss mask builder

## Day 10：Pretraining Pipeline

输出：

- raw data → batch 流程图

## Day 11：SFT

输出：

- chat template
- assistant-only loss mask

## Day 12：Preference Data / Reward Model

输出：

- pairwise ranking loss

## Day 13：DPO

输出：

- toy DPO loss
- DPO vs PPO 对比

## Day 14：Post-training Review

输出：

- SFT/RLHF/DPO 总结表
- 10 个面试问答

---

# Appendix B：每周复盘模板

```markdown
# Week X Review

## 1. 本周完成了什么

- 

## 2. 最重要的 5 个知识点

1. 
2. 
3. 
4. 
5. 

## 3. 本周写了哪些代码

- 

## 4. 哪些题还不能闭卷写

- 

## 5. 哪些概念还讲不清楚

- 

## 6. 下周优先补什么

- 

## 7. Mock 分数

Coding:
System Design:
Project Deep Dive:
Behavioral:
```

---

# Appendix C：面试中遇到不会的题怎么办

## Coding

不要沉默。用这个流程：

```text
Let me first restate the problem.
I think the core state we need to maintain is ...
A simple solution would be ...
I will implement the simple correct version first, then optimize if needed.
```

中文理解：

> 先把问题变成状态机或数据结构，再写简单正确版。

## System Design

如果不知道具体技术，先退回原则：

```text
I would separate the system into request routing, scheduling, execution, storage, and observability. The main bottleneck is likely GPU memory/utilization, so I would first design around batching and backpressure.
```

## ML / LLM 概念

如果忘了公式，讲直觉和数据流：

```text
I may not remember the exact formula, but the key idea is that we compare the preferred and rejected response under the policy relative to a reference model, and optimize the policy to increase the margin while staying close to the reference.
```

---

# Appendix D：最重要的 30 个口述题

1. 讲一下 Transformer block。
2. Q/K/V shape 怎么走？
3. causal mask 怎么实现？
4. 训练和推理的数据流有什么区别？
5. tokenizer 为什么重要？
6. pretraining data pipeline 怎么做？
7. SFT 和 pretraining 有什么区别？
8. RLHF pipeline 是什么？
9. DPO 和 PPO 有什么区别？
10. 什么是 reward hacking？
11. KV cache 存什么？
12. prefill 和 decode 有什么区别？
13. continuous batching 怎么 work？
14. prefix cache / radix cache 为什么有用？
15. LLM inference API 怎么设计？
16. DP / TP / PP / FSDP 区别？
17. column parallel 和 row parallel 怎么通信？
18. FSDP 为什么省显存？
19. ZeRO-1/2/3 区别？
20. 如何设计 GPU scheduler？
21. 如何设计 RAG？
22. 如何设计 model eval platform？
23. 如何做 safety eval？
24. 如何处理模型上线 rollback？
25. LRU / LFU 区别？
26. versioned DB 怎么实现？
27. durable cache crash 后怎么恢复？
28. multithread sort 怎么写？
29. file dedup 大规模怎么做？
30. 讲一个你最难的项目。

---

# Appendix E：一句话总结

你的准备路线应该是：

```text
先把 LLM 的训练、对齐、推理、并行、serving mental model 建起来；
再用高频 practical coding 把这些知识压成实现能力；
最后用 system design、project deep dive 和 AI safety 表达，把你的 CV/GenAI 背景包装成 frontier AI lab 想要的人。
```
