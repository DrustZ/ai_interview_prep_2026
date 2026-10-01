# Lab 02 · Code Review Reward 设计与 Reward Hacking

⏱ 45 分钟（砍时:只跑 `solution.py` 看输出，10 分钟）｜ 安排在 **Day 1 晚**

对口 [04 §7–§8](../../04_case_code_review_llm.md) 与 [03 §6–§7](../../03_model_training_reward.md)。这是你上周被问倒那题（「设计什么 reward function」）的动手版。

## 为什么值得手写一遍

面试里说「我会加一个 length penalty 防止刷量」是**空话**。手写过之后你能说的是：

> 刷量之所以有效，根因不是缺 length penalty，而是 reward **没有按缺陷去重**——围着同一个可疑区域刷 8 条评论，每条都单独计分。所以我会把 precision 的分子定义成「独立真缺陷数」而不是「命中条数」。

这句话是 senior 和 junior 答案的分界线。

## 怎么做

```bash
python3 solution.py        # 看 reward 被 hack 和被修好的对照
python3 test_solution.py   # 7 条断言，全绿
```

自己写：打开 `starter.py`，按 TODO 实现四层结构（限时 30 min），然后把 `test_solution.py` 的 import 改成 `from starter import` 再跑。

## 实测结论（就是 `solution.py` 的输出）

天真的加权求和（不去重 / 无 precision / 采信自称 severity）：

```
spam        32.00      <- 围着两个 bug 各刷一圈，8 条命中全部计分
inflator    16.00      <- 把 medium 缺陷自称 critical，2 分变 8 分
honest      10.00      <- 只排第三
nitpicker    0.00
```

加固后（hard gate + 按缺陷去重 + precision 地板 + ground-truth severity + 成本）：

```
honest       9.00      unique_true=2 dup=0 fp=1 outcome=7.0 quality=3.5 cost=1.5
inflator     3.50      severity 用真值，medium 就是 2 分
spam        -5.00      GATE: precision_below_floor (2/10=0.20)
nitpicker   -5.00      GATE: precision_below_floor (0/3=0.00)
leaker     -10.00      GATE: leaked_secret（找到真 critical bug 也不能抵消）
```

## 四个可以直接带进面试的点

1. **Hard constraint 必须是乘性 gate，不是加权项。** `leaker` 找到了真正的 critical bug，但把 secret 抄进了评论正文——任何「泄密 −20 分」的加权写法，都可能被足够高的 outcome 分抵消。gate 不会。
2. **按缺陷去重。** 最容易漏的一条，也是刷量的真正入口。
3. **severity 由 ground truth 决定。** 模型自称的严重度是它可以自由写的字段，等于把 reward 的一部分交给了被优化对象。
4. **reward 要拆开报告，不要只给标量。** `RewardBreakdown` 分别报 outcome / quality / cost / precision / duplicate——单一标量看不出是「找得准」还是「说得多」。

## 追问预演

- **「怎么拿到 ground-truth defect？」** 从可验证信号挖：后续 revert/hotfix 改动的行、能复现的失败测试、安全扫描确认项。见 [04 §3](../../04_case_code_review_llm.md)。这也是 [SWE-RL](https://arxiv.org/abs/2502.18449) 的思路。
- **「主观项（可读性、设计）怎么给 reward？」** 用 rubric-as-reward：拆成可逐项打分的 checklist 让 judge 评，并用人类 gold 集校准 judge。见 [Rubrics as Rewards](https://openreview.net/forum?id=c1bTcrDmt4)。
- **「precision 地板设多少？」** 不是常数，是从产品模式反推：auto-comment 模式下一次误报的代价是「开发者以后不再读所有评论」，所以地板高；private assist 模式可以低。见 [04 §1.2](../../04_case_code_review_llm.md)。
- **「模型学会只报最容易验证的 bug 怎么办？」** 这是本 lab 没覆盖的第四种 hack（能力塌缩到易验证子集）。答法：按 severity 和 category 分层报 recall，把「类别覆盖度」也纳入 gate。
