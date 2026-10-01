# Lab 6 — Buggy Training：训练循环 Debug 演习

## 对应什么考点

The Bot Company（及 Cruise/Tesla 系面试官）的实战 ML debug 轮：**给你一段「表面正经」
但不收敛/表现异常的训练代码，现场诊断并修复**。这轮考的不是算法，是：

1. 从症状到假设的分诊能力（loss 曲线形状、开环/闭环指标背离、评估不可重复各指向什么）；
2. PyTorch 肌肉记忆（`model.eval()`/`no_grad`、DataLoader shuffle、mask 掉 padding、归一化链路）——
   这正是你自评的最大风险点，本 lab 就是练这个；
3. 机器人语境的加分意识：train-serve skew（归一化 stats 要跟 checkpoint 一起落盘到机上）、
   动作后处理链路（归一化空间 vs 物理单位）、fleet 数据按 task/session 分块带来的顺序偏差。

场景：BC（行为克隆）训练一个 2-D reach 任务的小 MLP policy，4 个「家庭任务」的脚本专家演示，
变长轨迹 + padding，闭环 rollout 评估成功率。五个植入 bug 全部来自真实事故模式：

| # | Bug | 可观察症状 |
| --- | --- | --- |
| 1 | 归一化 stats 用全量数据算（split 前） | 无——靠 code review 抓（这正是考点） |
| 2 | 反归一化和 clip 顺序颠倒 | loss 低但 rollout 成功率 ~0.05 |
| 3 | 数据按 task 排序 + loader 不 shuffle | epoch 内 loss 周期性震荡（by-quarter 打印） |
| 4 | 变长 padding 没从 loss 里 mask | train loss 被稀释得好看，模型被拉向均值动作 |
| 5 | eval 没有 `model.eval()`/`no_grad` | 同一模型评估两次结果不同（val MSE 和成功率都抖） |

## 文件

- `buggy_train.py` — 埋了 5 个 bug 的 BC 训练脚本（无任何 bug 标记，当面试题用）
- `HINTS.md` — 三级提示阶梯（症状 → 定位手段 → 行号），自练时逐级揭开
- `SOLUTIONS.md` — 每个 bug 的症状/诊断路径/修复/英文面试叙述 + 数字总结
- `fixed_train.py` — 修复版，每处修复有 `FIX #n` 注释，可与 buggy 版直接 diff
- `test_fixed.py` — 断言修复版收敛、评估 bit 级可复现、成功率比 buggy 版高 ≥0.4（实际 0.875）

## 15–30 分钟熟悉路径

解释器固定用：`/Users/mingrui/Documents/codes/interview/.venv/bin/python3`（Python 3.9.6，torch 2.8 CPU）。

1. **跑 buggy（3 分钟）**：
   ```
   /Users/mingrui/Documents/codes/interview/.venv/bin/python3 buggy_train.py
   ```
   只看输出，写下至少 3 个异常：by-quarter 的周期形状、val MSE #1≠#2、
   success #1≠#2 且都 ~0.05、train loss 0.076 与成功率 0.05 的矛盾。
2. **盲修（10–15 分钟，核心环节）**：不开 HINTS，自己在 `buggy_train.py` 里找。计时。
   卡住了再按 HINTS 的 L1→L2→L3 逐级揭。目标：L2 内抓到 4 个（stats 泄漏那个允许靠 diff 发现）。
3. **对答案（5 分钟）**：`diff buggy_train.py fixed_train.py`，逐个对照 SOLUTIONS.md，
   重点背每个 bug 的「诊断路径」而不是修复本身——面试考的是路径。
4. **验证（2 分钟）**：
   ```
   /Users/mingrui/Documents/codes/interview/.venv/bin/python3 fixed_train.py
   /Users/mingrui/Documents/codes/interview/.venv/bin/python3 test_fixed.py
   ```
   预期：fixed 成功率 0.925 且两次评估 bit-identical；测试全绿约 10–25 秒。
5. **复述（3 分钟）**：不看材料，口头把五个「症状→假设→验证→修复」各讲 30 秒英文。

## 面试中怎么引用这段经验

> *"I keep a personal drill of the five training-loop bugs I've actually hit — leaked normalization stats, clip-before-denormalize, unshuffled task-sorted data, unmasked padding loss, and eval without model.eval() — and for each one I can go from the observable symptom to the diagnosis in a couple of minutes, because the symptom signatures (periodic loss, non-reproducible eval, good loss but failed rollouts) are distinct."*

追问时的展开点见 `SOLUTIONS.md` 末尾的「30 秒方法论」。

## 测试命令

```
/Users/mingrui/Documents/codes/interview/.venv/bin/python3 test_fixed.py
```

plain assert，无 pytest 依赖；CPU、全 seed，整套约 10–25 秒（视机器负载），三次连跑输出 bit 级一致。
