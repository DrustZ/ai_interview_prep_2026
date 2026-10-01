# PyTorch 冷写训练包

> 针对"概念懂但写不快"的定向训练。8 个模块全部对应三家真实考题，每个文件自带测试，参考实现已验证可跑。
> 运行环境：`/Users/mingrui/Documents/codes/interview/.venv/bin/python`（torch 2.8 + numpy，已装好）

## 冷写协议（每模块 4 步）

1. **复制**：`cp 01_attention.py scratch.py`，删掉 `COLD-WRITE ZONE` 里的所有实现体（保留函数签名和 docstring）
2. **计时冷写**：按 docstring 里的 timebox，从记忆写出实现 → `../.venv/bin/python scratch.py` → 红了就修，**不看参考**
3. **卡住 10 分钟才允许看参考**——看懂后整段删掉，重新从空白写
4. **通过后 diff 参考实现**，把写法差距记到自己的"惯用法清单"（比如：`masked_fill_` vs 乘 mask、`gather` 的 dim 语义、`keepdim=True` 什么时候必须加）

**过关标准：同一模块连续两次一遍写对（测试全绿、不查任何资料），才算拥有。** 出过错的模块隔天必须重写一次。

## 模块 → 考题映射与排期

| 模块 | 对应真题 | 建议日 |
|------|---------|--------|
| 01_attention | GDM ML coding 标配、OpenAI transformer 题 | D1 |
| 02_stable_softmax_entropy | OpenAI RS streaming entropy 原题族 | D1 |
| 06_backward_autograd | OpenAI RS "AI coding I = autograd"、matmul 手推 | D2 |
| 03_losses | GDM loss 手写、agent 训练 mask 陷阱 | D3 |
| 04_grpo_ppo | **Anthropic RL Fundamentals 轮**（含 3-bug debug 练习） | D4 |
| 05_sampling | GDM top-k/top-p 点名考点 | D5 |
| 07_kv_cache_decode | OpenAI MLE KV cache 原题 | D6 |
| 08_bughunt_minigpt | OpenAI 变形金刚捉虫（4 bug，先自己找再看 answers） | D7 |

## 出声练习

面试是边写边讲。冷写第二遍起，**边写边解释每一步**（"这里要减 max 因为……"）。GDM 尤其看重这个。
