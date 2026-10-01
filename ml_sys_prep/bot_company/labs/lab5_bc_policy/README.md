# lab5_bc_policy · BC 训练闭环 + 多模态演示失败复现

⏱ 全流程 CPU < 60 秒 ｜ 依赖：torch + numpy（无 gym / pandas）｜ 解释器：`/Users/mingrui/Documents/codes/interview/.venv/bin/python3`（Python 3.9.6, torch 2.8.0, numpy 2.0.2）

这是把 LLM post-training 背景嫁接到 robot learning 的**最佳单点演示**：
同一份双模态（绕左/绕右各半）演示数据、同一个 MLP trunk，只换输出头——

| Head | 本质 | success | collision | val loss |
|---|---|---|---|---|
| MSE 回归 | 学条件均值 | **0.25** | 0.75 | 0.0011 |
| 离散 bins + cross-entropy | action tokenization 的最小形态 | **1.00** | 0.00 | 0.740 |

（seed=0 实测；`train_bc.py` 的 main 里直接 assert 了这个 gap，跑不出来会报错。两个 val loss 是不同目标函数、不可直接互比——要点在下面第 4 条考点。）

## 对应考点

- **Behavior cloning 完整闭环**：数据收集 → 标准化 → train/val 切分 → 早停 → closed-loop rollout 评估。这是 The Bot Company（fleet learning 路线）最可能让你现场写或口述的东西。
- **多模态演示 → mode averaging 失败**：家用机器人的 teleop 数据天然多模态（不同操作员绕障碍的方向、抓取的姿态都不同），MSE 头学到的是两个模式的均值——一个物理上不存在的动作。
- **为什么 VLA 用 action tokens / diffusion policy 而不是 MSE**（见下节）。
- **offline metric 和 closed-loop 成功率脱钩**：MSE 头的 val MSE 低到 0.0011（RMS 误差 ~0.03，和演示噪声同量级），离线看几乎完美，rollout 却 75% 撞墙——因为它在双模态状态上「精确地」预测了一个错误的均值动作。离线 loss 好 ≠ 机器人能用，这是 robot eval 的核心难点，也是 fleet 里必须做 on-robot eval 的原因。

## 机理：把这个结果讲透

1. 环境是极简 2D 导航+抓取：起点在下方，中间一堵宽墙，目标在上方，**绕左绕右都对**。scripted expert 左右各半，且两种模式在中线附近经过几乎相同的状态、输出方向相反的小侧移动作（`test_env.py` 里有断言验证这个双模态性质）。
2. MSE 最小化的解是 **E[a|s]**：在双模态状态上就是两个模式的平均 ≈ 0 侧移 → 径直爬升 → 撞墙。而且任何平滑回归器都必须在两条 rail 之间插值出一条「平均带」，起点落在带内就完蛋。
3. Cross-entropy 头对每个动作维度输出 **bins 上的完整分布**：双模态就是两个峰，argmax 解码时**承诺其中一个峰**，不会产生「两个峰的均值」这种不在数据里的动作。这就是 action tokenization（RT-1/RT-2 每维 256 bins）解决的第一性问题；diffusion policy / flow matching（如 pi0）是同一个问题的连续解法——建模动作分布本身而不是回归均值。
4. 离散化的代价（追问必考）：分辨率损失；**各维独立 argmax 可能拼出数据里不存在的组合动作**（所以 RT 系列按维自回归解码）；bins 太粗动作抖、太细每个 bin 样本太少。本 lab 用 8 bins 且 expert 速度刻意对齐 bin center（见 `env.py` 的 design note）。

## 面试可说的英文（背这两句）

> "When demonstrations are multimodal — say half the operators pass an obstacle on the left and half on the right — an MSE regression head learns the conditional mean, which is a physically invalid action that drives straight into the obstacle. Discretizing actions into bins with a cross-entropy head keeps the full distribution and lets the policy commit to one mode — that's the minimal version of why VLAs use action tokens and why diffusion policies model the action distribution instead of regressing it."

引用这段经验的一句话：

> "Coming from LLM post-training, I ground myself in robot learning by building a minimal reproducible BC experiment: on bimodal demos, MSE regression gets 25% success while the same network with tokenized actions gets 100% — and notably the MSE head looks near-perfect on offline validation loss, which is exactly why offline metrics don't predict closed-loop success."

## 15–30 分钟熟悉路径

```bash
PY=/Users/mingrui/Documents/codes/interview/.venv/bin/python3
cd /Users/mingrui/Documents/codes/interview/my_interview_prep/ml_sys_prep/bot_company/labs/lab5_bc_policy
```

1. **先跑** `$PY env.py`（约 1 秒）：看 ASCII 图里左右两条演示轨迹绕墙——双模态长什么样。
2. **再跑** `$PY train_bc.py`（约 10 秒）：看主结果表 + "CLAIM VERIFIED"。
3. 读 `env.py` 顶部 docstring 和 `ExpertConfig` 的 design note（5 分钟）：几何为什么这样设计。
4. 自底向上读 `train_bc.py`（10 分钟）：`Normalizer` → `ActionDiscretizer` → `MLPPolicy` → 两个 loss → `train_one_epoch`/`train_policy`（早停）→ `make_policy_fn`/`rollout_policy`。**这份代码就是你的冷写范本**。
5. 跑三个测试（见下）；回家作业：限时 30 分钟填 `skeleton.py`，用 grader 验证。

## 冷写训练

```bash
$PY test_skeleton_ref.py                  # 先确认 grader 对参考实现全绿
# 然后不看 train_bc.py，把 skeleton.py 的 TODO 全部填完：
BC_IMPL=skeleton $PY test_skeleton_ref.py # 全绿 = 你能冷写 BC 训练闭环
```

冷写清单（就是 skeleton 里的符号）：`Normalizer`、`ActionDiscretizer.encode/decode`、`split_train_val`、`MLPPolicy`（两种头）、`mse_loss`、`discrete_ce_loss`、`train_one_epoch`、`eval_loss`、`make_policy_fn`（argmax 解码）、`rollout_policy`。

## 文件与命令

```
env.py                2D 导航+抓取环境 + scripted expert + 演示收集（numpy）
train_bc.py           教科书式 BC 训练闭环 + 核心对比实验（main 里 assert）
skeleton.py           冷写骨架（签名 + shape 注释 + TODO）
test_env.py           环境determinism / expert 100% 成功 / 双模态断言 / 错误处理
test_train_bc.py      单元测试 + 端到端跑一遍核心实验并 assert gap
test_skeleton_ref.py  冷写 grader（默认验证参考实现，BC_IMPL=skeleton 验证你的）
```

```bash
$PY test_env.py           # ~1 s
$PY test_train_bc.py      # ~13 s（含一次完整实验）
$PY test_skeleton_ref.py  # ~2 s
$PY train_bc.py           # ~10 s 主实验
$PY env.py                # ~1 s ASCII demo
```

## 追问预演

- **为什么不用 mixture density network？** 可以，那是这个问题的九十年代解法，但数值不稳（log-sum-exp、mode collapse）；bins+CE 更简单稳健，diffusion/flow matching 是表达力更强的现代连续解法。
- **argmax 还是采样？** 这里 argmax（部署确定性好）；采样也能破对称但会抖。真系统里温度/top-k 是可调的。
- **这个 lab 和 DAgger 是什么关系？** BC 有两个独立失效轴：多模态（本 lab）和 covariate shift/compounding error（DAgger 解决的）。这里刻意用短 horizon + 演示覆盖把后者控制住，隔离出多模态这一个变量。
- **调这个实验时踩过什么坑？（好故事）** 第一版用圆形小障碍，MSE 反而 93% 成功——网络在两个模式间插值出的「不稳定平衡」把 agent 甩到一侧，顺着单模式数据绕过去了。要让 mode averaging 真正致命，需要：宽障碍（逃逸距离长）、演示侧移速度温和（平均场逃逸速度有上界）、起点落在模糊带内。**「多模态会害死 BC」是有几何前提的，这个前提本身就是 senior 信号。**
- **8 bins 怎么选的？** expert 的爬升/侧移速度刻意放在 bin center 上，量化零滞后；bins 翻倍会让每 bin 样本减半。RT-2 用 256 bins 是因为它的动作范围和精度需求大得多。

## 诚实性提醒

这是**教学用最小复现**，不是真机经验。面试里的正确说法：

> 为了补 robot learning 这块，我写了一个小规模可复现实验，验证的是「多模态演示下 MSE 回归头 mode-average 而离散化动作头不会」；它不能证明真实 fleet 规模、视觉输入、7-DoF 下的表现，下一步我会在真实 benchmark（如 LeRobot 的 PushT）上验证同一对比。
