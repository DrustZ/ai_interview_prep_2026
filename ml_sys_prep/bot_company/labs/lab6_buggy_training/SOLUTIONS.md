# SOLUTIONS — 五个 bug 的完整档案

每个 bug 按「症状 → 诊断路径 → 修复 → 面试叙述（英文一句话）」组织。
对应关系：HINTS 里的 A–E = 下面的 #3、#2、#5、#4、#1（HINTS 按症状明显程度排序，这里按代码逻辑顺序排）。
所有修复都在 `fixed_train.py` 中以 `FIX #n` 注释标出，可直接 `diff buggy_train.py fixed_train.py`。

---

## Bug #1：归一化统计量在 train/val 切分之前用全量数据计算（HINTS 的 Bug E）

**位置**：`buggy_train.py` L392；修复见 `fixed_train.py` `run_experiment` 内 `FIX #1`。

**症状**：本 lab 里几乎无可观察症状（toy 数据下数值差异极小）——这正是它危险的原因。
真实场景的两种爆法：(a) val 指标系统性偏乐观（val 的分布信息渗进了预处理）；
(b) 部署 mismatch：训练时的 stats 没有和 checkpoint 绑定落盘，机上用新数据重算 stats，
policy 输入分布悄悄平移，行为退化且难以复现。

**诊断路径**：这类 bug 靠 code review 和数据流梳理，不靠 loss 曲线。固定审查动作：
从原始数据到 tensor 的每一步变换，问「这一步用到的参数是从哪个集合估计的？」
凡是 fit 出来的东西（归一化、词表、分位数、PCA）都必须只来自 train split，并作为 artifact 与模型一起版本化。

**修复**：

```python
# buggy: L392（sort 之后、split 之前）
stats = NormStats.from_trajectories(trajectories)

# fixed: 先 split，stats 只来自 train split
val_trajs = trajectories[::cfg.val_every]
train_trajs = [t for i, t in enumerate(trajectories) if i % cfg.val_every != 0]
stats = NormStats.from_trajectories(train_trajs)
```

**面试叙述**：*"Any fitted preprocessing statistic is part of the model: it must be estimated on the training split only and shipped with the checkpoint, otherwise you get silent train-serve skew on the robot."*

---

## Bug #2：反归一化和 clip 顺序颠倒（HINTS 的 Bug B）

**位置**：`buggy_train.py` L360；修复见 `fixed_train.py` `evaluate_rollout` 内 `FIX #2`。

**症状**：train loss / val MSE 正常下降（0.076 / 0.085），rollout 成功率却只有 ~0.05。
「开环好、闭环挂」。

**诊断路径**：
1. 开环拟合没问题 → 问题在「模型输出 → 电机指令」的后处理链路或环交互上。
2. 打印实际执行的 action：全部落在 `act_mean ± 0.1*act_std` 的窄带里
   （x 轴 ≈ 0.046±0.008，y 轴 ≈ 0.028±0.008，两轴永远为正），而专家的饱和动作是 ±0.1；
   负方向动作被均值项拉成正号——机器人只会朝右上方缓慢漂移，左侧目标永远到不了。
3. 逆推公式：`clip(pred, ±0.1)` 作用在**归一化空间**（std≈1，饱和动作 ≈ ±1.1~1.7），
   0.1 的物理限幅把它们全部截断，再乘 std 加 mean，边界动作全错。

**修复**：

```python
# buggy: 先 clip（在归一化空间）再反归一化
action = np.clip(pred, -max_action, max_action) * act_std + act_mean

# fixed: 先反归一化回物理单位，再按执行器限幅 clip
action = np.clip(pred * act_std + act_mean, -max_action, max_action)
```

**量化影响**：修这一个 bug，成功率 0.05 → ~0.80（仍留有 bug #5 的抖动）；全部修完 0.925。

**面试叙述**：*"Low training loss with a near-zero closed-loop success rate points at the action post-processing chain, and here the clip was applied in normalized space so every saturated boundary action got crushed — units and ordering in the de-normalization pipeline are the first thing I check."*

---

## Bug #3：数据按 task 排序 + DataLoader 不 shuffle（HINTS 的 Bug A）

**位置**：`buggy_train.py` L390 + L399；修复见 `fixed_train.py` `run_experiment` 内 `FIX #3`。

**症状**：每个 epoch 内 `by-quarter` 损失呈固定周期形状（末 epoch `[0.058 0.082 0.093 0.077]`，
早期 epoch 差异达 7 倍），因为四个 task 的专家噪声水平不同（0.004→0.013），loss 底就不同；
每个 epoch 的梯度按 task 顺序「轮流拉扯」，收敛慢、末端不稳。

**诊断路径**：
1. loss 有周期结构 → 周期必然来自数据顺序。周期长度 ≈ 每 epoch batch 数 / task 数 → 指向按 task 分块。
2. 打印每个 batch 的 `task_id` 直方图确认：batch 内几乎单一 task。
3. 检查两处：进 loader 前有一行 `sort(key=task_id)`（注释还说得冠冕堂皇），loader `shuffle=False`。

**修复**：删掉 sort；`DataLoader(..., shuffle=True, generator=torch.Generator().manual_seed(seed))`
（带种子的 generator，保证可复现——修 bug 不能引入不确定性）。

**面试叙述**：*"A periodic loss curve is almost always a data-ordering artifact; here the demos were grouped by task and the loader never shuffled, so each batch's gradient pointed at one task — shuffle with a seeded generator fixed both the oscillation and the convergence."*

---

## Bug #4：变长序列 padding 没有从 loss 里 mask 掉（HINTS 的 Bug D）

**位置**：`buggy_train.py` L322（`lengths` 在 L320 被解包但没用）；同病 L302。
修复见 `fixed_train.py` 的 `masked_mse`（`FIX #4`）。

**症状**：轨迹长度 4–10 步（均值 7.2），pad 到 10；约 28% 的 loss 项是「预测 0 vs 目标 0」的送分题。
两个后果：(a) 报告的 loss 被稀释，看起来比真实水平好；(b) 梯度持续把模型往「零输出 =
均值动作」上拉，短轨迹 task 的真实步权重被进一步压低。

**诊断路径**：
1. 红旗在代码里：dataset 特意返回了 `lengths`，训练循环解包成 `lengths` 却从未使用——
   接口暗示了必须 mask。
2. 验证：同一模型分别算 masked / unmasked loss，unmasked 明显更小；
   或直接算 `lengths.sum() / (B*T)` 看 padding 占比。

**修复**：

```python
mask = (torch.arange(T)[None, :] < lengths[:, None]).float().unsqueeze(-1)
loss = ((pred - target) ** 2 * mask).sum() / (mask.sum() * action_dim)
```

（测试里有一个极小构造用例：pad 步上放垃圾值，masked loss 必须为 0。）

**面试叙述**：*"Whenever a dataset returns sequence lengths that the loss never consumes, that's an unmasked-padding bug: the reported loss is diluted by free zero-targets and the policy gets biased toward the mean action."*

---

## Bug #5：评估路径没有 `model.eval()` / `torch.no_grad()`（HINTS 的 Bug C）

**位置**：`buggy_train.py` L296–307（`evaluate_mse`）、L339–371（`evaluate_rollout`，
L359 的 `.detach()` 是掩盖报错的创可贴）；修复见 `fixed_train.py` 两个 eval 函数内 `FIX #5`。

**症状**：同一模型、同一数据评估两次：val MSE 0.0852 vs 0.0949，rollout 成功率 0.050 vs 0.025。
dropout 在 eval 时仍激活。另外没有 `no_grad`，每步前向都在建 autograd 图——本 lab 里只是浪费，
真实模型上这就是「eval 时显存莫名上涨/OOM」的标准来源。

**诊断路径**：
1. 「评估不可重复」→ 枚举 eval 路径上的随机源：env rng（有 seed）、数据顺序（固定）→ 只剩网络本身。
2. `PolicyNet` 里有 `nn.Dropout` → 检查 eval 代码是否切了模式 → 没有。
3. `.detach()` 的存在本身就是线索：作者遇到过 "can't call numpy() on Tensor that requires grad"
   报错，用 detach 消音，而没问「为什么 eval 时会有梯度」。

**修复**：eval 函数进门 `model.eval()` + `with torch.no_grad():`，出门恢复原模式
（`was_training` 守卫）。修完后两次评估 bit-identical（测试用 `==` 断言）。

**bug 互相遮蔽的细节（面试加分点）**：全 bug 状态下 dropout 抖动常被 bug #2 的 clip 压扁
（饱和预测被截到同一个值），rollout 两次可能完全一样；先修 #2，抖动才显形（0.85/0.825/0.75）。
说明「修一个 bug 后症状变化」本身就是诊断信号。

**面试叙述**：*"An evaluation that isn't a pure function is a bug: repeated eval on the same checkpoint returned different success rates, which immediately means dropout was still active — model.eval() plus no_grad made eval bit-reproducible and cut the autograd memory overhead."*

---

## 数字总结（seed=0，本机可复现）

| 指标 | buggy | fixed |
| --- | --- | --- |
| final train loss | 0.0758（被 padding 稀释） | 0.0799（masked，真实值） |
| final val MSE 两次 | 0.0852 / 0.0949（抖） | 0.0413 / 0.0413（bit-identical） |
| rollout success 两次 | 0.050 / 0.025 | 0.925 / 0.925 |
| epoch 内 by-quarter | 周期形状（最大 ~7 倍差） | 平坦 |

## 面试里怎么用这套方法论（30 秒版）

1. 先分类症状：开环 vs 闭环、可重复 vs 不可重复、周期性 vs 单调性。
2. 「loss 好、rollout 挂」→ 查后处理/单位/归一化链路；「评估抖」→ 查模式与随机源；
   「loss 周期震荡」→ 查数据顺序；「loss 好得可疑」→ 查 loss 的分母（mask/padding/reduction）。
3. 修复必须保住可复现性（seeded shuffle、eval 纯函数化），并意识到 bug 会互相遮蔽，修一个要全量回归。
