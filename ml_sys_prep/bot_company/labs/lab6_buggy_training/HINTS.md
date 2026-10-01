# HINTS — 三级提示阶梯

自练规则：先跑 `buggy_train.py`，把你观察到的异常全部写下来，再逐级揭提示。
每个 bug 三级：**L1 症状**（面试官会先给你的信息）→ **L2 定位手段**（你该做的动作）→ **L3 具体位置**（行号区域）。
尽量停在 L2 就把 bug 找出来——真实面试里 L3 是没有的。

先跑一遍，记录这些观察点：

```
/Users/mingrui/Documents/codes/interview/.venv/bin/python3 buggy_train.py
```

- 每个 epoch 的 `by-quarter` 四个数是什么形状？
- `final val MSE (#1)` 和 `(#2)` 一样吗？rollout success `(#1)` 和 `(#2)` 呢？
- train loss 0.076 看起来不错，为什么 rollout success 只有 ~0.05？

---

## Bug A：loss 曲线周期性震荡

**L1 症状**：每个 epoch 内部 `by-quarter` 呈固定形状（末 epoch `[0.0577 0.0817 0.0925 0.0772]`，早期 epoch 相差近 7 倍），
每个 epoch 都重复同一形状；整体收敛也偏慢。数据里有 4 个 task，噪声水平不同。

**L2 定位手段**：打印每个 batch 里样本的 `task_id` 分布——如果一个 batch 几乎全是同一个 task，
说明梯度在 task 间「轮流拉扯」。检查两件事：数据进 DataLoader 之前的顺序，和 DataLoader 的
`shuffle` 参数。

**L3 位置**：`buggy_train.py` L390（`trajectories.sort(key=lambda t: t.task_id)`）+
L399（`DataLoader(..., shuffle=False)`）。两处共同构成这个 bug。

---

## Bug B：loss 低但机器人根本走不到目标

**L1 症状**：train loss 和 val MSE 都在正常下降（拟合没问题），但闭环 rollout 成功率 ~0.05。
「开环指标好、闭环全挂」是机器人学习里最经典的红旗。

**L2 定位手段**：在 rollout 里打印真正发给 `env.step()` 的 action，和专家在同一状态下的 action 对比。
你会发现执行的 action 被压进一条窄带（x 轴 ≈ [0.038, 0.055]，y 轴 ≈ [0.020, 0.036]，两轴永远为正——
机器人永远到不了左边的目标）。专家的饱和动作是 ±0.1。然后逆着后处理链路检查：模型输出的是**归一化**动作，谁先 clip 谁后反归一化？

**L3 位置**：`buggy_train.py` L360，`evaluate_rollout` 内：
`np.clip(pred, -max_action, max_action) * act_std + act_mean` —— 在归一化空间（std≈1）里用物理限幅
0.1 去 clip，饱和动作全被压扁甚至变号。

---

## Bug C：同一个模型、同一批数据，评估两次结果不一样

**L1 症状**：`final val MSE (#1)=0.0852 (#2)=0.0949`，rollout success `(#1)=0.050 (#2)=0.025`。
没有任何东西变了，数字却变了。

**L2 定位手段**：评估是不是纯函数？检查 eval 路径上所有随机性来源：环境 rng（已固定 seed）、
数据顺序（固定）、还剩什么？——网络自己。看 `PolicyNet` 里有什么 module 在 train/eval 模式下行为
不同，再看 eval 代码有没有切模式。顺带检查 autograd：`.detach()` 挡住了报错，但图还是每步都在建。

**L3 位置**：`buggy_train.py` L296–307（`evaluate_mse`）和 L339–371（`evaluate_rollout`）：
两处都没有 `model.eval()` 也没有 `torch.no_grad()`；L359 的 `.detach()` 是掩盖问题的创可贴。

**进阶思考**：全 bug 状态下两次 rollout 有时数值一样——因为 Bug B 的 clip 把 dropout 噪声也压扁了。
修掉 Bug B 之后抖动反而会变明显（0.85 / 0.825 / 0.75……）。bug 之间会互相遮蔽。

---

## Bug D：train loss 好看得可疑

**L1 症状**：轨迹是变长的（4–10 步，均值 7.2），被 pad 成等长张量（T=10）。均值 loss 收敛到 0.076，
但如果只在真实步上算，loss 其实更高；模型还被悄悄拉向「输出全零（=均值动作）」。

**L2 定位手段**：数一数 batch 张量里有多少比例是 padding（`1 - lengths.sum()/(B*T)` ≈ 28%）。
再看 loss 那一行用没用 `lengths`——dataset 明明把 `lengths` 返回了，训练循环接了这个变量吗？

**L3 位置**：`buggy_train.py` L322（`loss = F.mse_loss(pred, act)`，`lengths` 在 L320 被解包但从未使用）；
同样问题在 L302（`evaluate_mse`）。

---

## Bug E：一个不报错、不出图形的 bug（code review 题）

**L1 症状**：没有任何运行时症状——这正是考点。这是一个「部署到机器人上才爆」的 bug。
提示：想一想 train/val 切分和归一化统计量的计算顺序。

**L2 定位手段**：从上往下读 `run_experiment`，画数据流：demos → sort → **stats** → split → dataset。
stats 用了谁？val 集的信息有没有渗进训练？再想部署：机上推理时用的 `NormStats` 应该等于哪份数据的
统计量？如果之后用「新 fleet 数据」重算 stats 而不重训模型，会发生什么？

**L3 位置**：`buggy_train.py` L392（`stats = NormStats.from_trajectories(trajectories)` 在全量数据上算），
而切分在 L394–395 才发生。修复：先切分，用 `train_trajs` 算 stats，并把这份 stats 与 checkpoint 一起落盘。
