# Exa 技术轮冷写题包（ML Research / ML Evals）

⏱ 本文件 4 分钟读完 ｜ 建于 2026-07-28，**2026-07-29 用第一轮实测结果修正**

## ⚠️ 第一轮实测：预测部分落空，先读这段

**2026-07-28 第一轮实际考的是「流式分位数」** —— 给一个 stream，返回任意 percentile。
推导路线：全排序 → 压缩空间 → 分桶 → 引入误差容忍 → **log 分桶算 index**。（答对了。）

| 我们原来的预测 | 实际 | 修正 |
|---|---|---|
| 检索指标 / 向量检索 / InfoNCE | **近似算法 + 空间/精度权衡** | Exa 的题偏**工程判断力**，不是 ML 配方背诵 |
| 「related to what we do at Exa」= ML 内容 | 是**搜索系统里的基础设施问题** | 索引压缩、剪枝、sketch、延迟预算都在射程内 |

→ 新增 **[Drill E · 流式分位数](drill_e_streaming_quantile.py)**（把那道题做完整：相对误差保证、可合并、滑动窗口）。
→ A–D 仍然值得练，但**优先级降到 Drill E 之后**。

**第二轮（2026-07-29 收到邀约）是 systems design**，不是 coding：
面试官 **Joshua Yurtsever**，方向是 production retrieval + post-training for agentic search
（reranking / snippet generation / model alignment）。
👉 **主备考文件换成 [20_case_exa_agentic_search.md](../../20_case_exa_agentic_search.md)**，本题包这轮只当热身。

## 官方 FAQ 要点（这决定了怎么练）

| 事实 | 对备考的含义 |
|---|---|
| 第一轮 45 min **live coding**，"related to what we do at Exa"，明确不是 LeetCode | 你的 [06](../../06_search_post_training.md) 是**口述 design** 弹药，对这轮不直接得分。要练手速 |
| 题面在 **Colab** 里，用**你自己的环境**共享屏幕 | 现在就要把 Colab 打通，别在面试里浪费时间 |
| ML 团队**必须用 Python** | 不用纠结语言 |
| **禁止任何 AI 工具**（virtual rounds；只有终轮 onsite 才 fully AI-enabled） | 这是你 pipeline 里风险最高的一轮。唯一的准备方式是冷写 |
| ~~第二轮 ML Research/Evals = **PyTorch 题**~~ | ❌ **已被推翻**：recruiter 原话是 "a more team specific question, that is often **systems design**" |
| 开场聊 recent projects + why Exa；结尾有 Q&A | 两头都要提前想好，见文末 |

## 五道题（概率已按第一轮实测重排）

| Drill | 主题 | timebox | 概率 | 对应轮次 |
|---|---|---|---|---|
| **[E · 流式分位数](drill_e_streaming_quantile.py)** | **DDSketch：log 桶、相对误差、可合并、滑动窗口** | 25 min | **★★★★★ 已考** | 第一轮实题 |
| [B · 向量检索](drill_b_vector_search.py) | 批量 top-k、argpartition、**Matryoshka 截断级联** | 20 min | ★★★★☆ | 同类工程题 |
| [A · 检索评测指标](drill_a_retrieval_metrics.py) | recall@k / MRR / **nDCG** / MAP，分级相关性 | 20 min | ★★★★☆ | design 轮口述也用得上 |
| [C · PyTorch InfoNCE](drill_c_infonce_pytorch.py) | 对比学习、温度、对称损失、假负例 mask | 25 min | ★★★☆☆ | work trial / onsite |
| [D · Judge 一致率](drill_d_judge_agreement.py) | kappa、位置偏差、Bradley-Terry、bootstrap CI | 20 min | ★★★☆☆ | Evals 岗对口 |

判断依据：E 是实考题；B/A/C/D 对应 Exa 官方博客反复讲的四件事——自训 embedding（C）、Matryoshka 截到 256 维省 20× 内存（B）、open evals 用 LLM 打 0–1 分级相关性（A、D）、GPT-4.1 judge 与人类 easy 97%/hard 83% 一致率（D）。

## 冷写协议（沿用你 `new/drills/` 那套）

```bash
cd exa_drills
cp drill_a_retrieval_metrics.py scratch.py
# 删掉 COLD-WRITE ZONE 里的所有实现体，保留签名和 docstring
# 计时，从记忆写，不看参考
/Users/mingrui/Documents/codes/interview/.venv/bin/python scratch.py
```

**卡住 10 分钟才允许看参考**；看懂后整段删掉重写。过关标准：连续两次一遍写对。

一键校验参考实现：
```bash
python3 run_all.py          # 用 .venv 的 python，五个 drill 全跑
```

## 两三天的排法

| 时段 | 做什么 |
|---|---|
| **今天（最要紧）** | ① 打通 Colab（见下）② Drill A 冷写 ③ Drill C 冷写。这两道概率最高 |
| 明天 | Drill B + Drill D 冷写；A、C 各**重写一遍**（第二遍才算拥有） |
| 面试当天早上 | 四个 drill 的参考实现各读一遍 + 出声讲追问预演；**不要再写新题** |

## 环境清单（现在就做，别拖到面试当天）

- [ ] Colab 能登录、能新建 notebook、能跑 `import numpy, torch`
- [ ] 决定用 Colab 还是本地：你本地 `.venv` 是好的（torch 2.8 / numpy 2.0），但**题面在 Colab**，最省事的是直接在 Colab 里写
- [ ] 屏幕共享试一次（哪个显示器、字号调大到面试官能看清）
- [ ] **关掉所有 AI 补全**：Copilot、Cursor、Claude Code、IDE 里的 inline suggestion。面试前当着面关掉是加分项，被抓到是致命的
- [ ] 准备一个干净的 scratch notebook，预先 import 好 numpy/torch（省 30 秒）

## 45 分钟现场节奏

```
0–3    听题 + 复述一遍确认理解 + 问清输入输出格式和规模
3–6    口述打算怎么做（先说最朴素的能跑版本），确认方向再动手
6–30   写。边写边讲。先让最小版本跑通，再优化
30–40  自测 + 优化 + 讲 trade-off（复杂度、内存、web 规模下怎么变）
40–45  Q&A
```

**最重要的一条**：先写能跑的朴素版本，再优化。FAQ 原话是 "we prioritize working code and seeing high level thinking in action"——**working code 排在第一位**。卡在追求最优解上不动手是最差的表现。

FAQ 还说 "you might not be familiar with the question or topic asked about; how do you think through it with the help of your interviewer?"——**这明确邀请你提问**。不懂就问，这是被鼓励的行为，不是扣分项。

## 开场：recent projects + why Exa

你最对口的一条线是 **eval / grader**，不是 agent：

> 我最近做的一块是把「主观质量」变成可自动计算的 grader，再用人工标注校准它——包括论证旧的表面相似度指标其实是在掷硬币，以及构造扰动集去检验 grader 的判别力。这跟 Exa 在 evals 上的做法很像：你们用 LLM 给 (query, result) 打分级相关性，然后拿人类偏好去校准 judge，还专门做了 Exa Olympiad 那种困难 query 集。搜索质量的评测和我做的对话质量评测，难点是同一个：没有免费的 ground truth，只能用可验证信号加人工校准去逼近。

**why Exa** 可以说：搜索是少数几个「评测本身就是核心研究问题」的方向——他们放弃 MS Marco 式封闭评测、自己搭 open evals，说明这家公司认真对待这件事。

## 结尾 Q&A 问什么（他们说会留时间）

挑两三个，别问官网能查到的：
- open evals 里 Exa Olympiad 那批困难 query 是怎么构造和维护的？会随模型变强而更新吗？
- pointwise 打分在跨版本追踪上会不会漂移（judge 模型升级导致历史分数不可比）？怎么处理？
- Matryoshka 的维度是怎么定的？粗筛维度和 shortlist 大小是一起调的吗？
- 从网页挖 embedding 训练数据——最大的噪声来源是什么？
- ML Research 和 ML Evals 两个团队日常怎么协作？

## 相关材料

- 设计题弹药（第二轮若是 design，或 onsite）：[06_search_post_training.md](../../06_search_post_training.md)
- Exa 公司卡（一手事实与接话点）：[13_company_cards.md](../../13_company_cards.md)
- 概念版实验（纯 Python，讲原理用）：[lab03_retrieval_negatives](../lab03_retrieval_negatives/)
- 通用 PyTorch 冷写：[`../../../online_resource/drills/`](../../../online_resource/drills/)
