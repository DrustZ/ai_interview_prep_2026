# Drill 08 答案: MiniGPT 四个 bug

对应文件: `08_bughunt_minigpt.py` (bug 全在 COLD-WRITE ZONE, 行号以该文件为准)。

面试通用打法 (先背这个流程, 再看具体 bug):

1. 先跑一遍, 记下初始 loss。**初始 loss ≈ ln(vocab_size) 说明模型在输出均匀分布**
   (本题 ln(40) ≈ 3.689), 这是正常起点; 初始就巨大 (几十上百) 说明 init/head 有问题。
2. loss 完全不动 → 优先查"参数有没有在更新": backward/step/zero_grad/lr/参数是否进了 optimizer。
3. loss 降但降不动或异常地快 → 查数据流: shift、mask 泄漏、embedding。
4. 逐模块过一遍 forward, 对每个 tensor 心算 shape; 对 `__init__` 里创建的每个
   submodule 问一句 "forward 里用了吗?"。

---

## Bug 1: positional embedding 创建了但没用 (行 131)

- **位置**: `MiniGPT.forward`, 行 127–139。`self.wpe` 在行 119 创建, 但行 131 只有
  `x = self.wte(idx)`, 没有加 `wpe`。
- **症状**: 单独存在时 loss 会下降但卡在明显偏高的平台 (attention 是置换等变的,
  没有位置信息模型只能学到 "袋装" 统计)。本题里被 bug 3 掩盖 (loss 完全不动)。
- **怎么定位**: 两招。(a) 读 `__init__` 时把每个 submodule 在 forward 里 grep 一遍,
  `wpe` 只出现在 `__init__`; (b) 跑一次 `loss.backward()` 后检查
  `model.wpe.weight.grad is None` —— 没进计算图的参数 grad 是 None。
- **修复**:

  ```python
  pos = torch.arange(T, device=idx.device)
  x = self.wte(idx) + self.wpe(pos)
  ```

- **真题出现形式**: OpenAI 捉虫题里最常见的一类 "创建了但没接线" bug: wpe 没加、
  LayerNorm 建了没调、dropout 只在 `__init__`。400 行代码里靠通读 forward 找。

## Bug 2: causal mask 用乘 0/1 而不是加 -inf (行 90)

- **位置**: `CausalSelfAttention.forward`, 行 90: `att = att * self.mask[:T, :T]`,
  然后行 91 直接 softmax。
- **症状**: 被 mask 的 score 变成 0 而不是 -inf, softmax 后 exp(0)=1, 未来位置
  照样拿到非零权重 → **未来信息泄漏**。单独存在时训练 loss 会异常低 (模型偷看
  下一个 token 来 "预测" 它), 但 eval/生成时崩坏。乘法还把真实的负 score 也砸成 0,
  attention 分布整体失真。
- **怎么定位**: (a) 看到 `* mask` + `softmax` 这个组合直接报警: mask 必须发生在
  softmax 之前的 **加性** 域; (b) 行为测试: 改输入最后一个 token, 看前面位置的
  logits 变不变 (见 `test_buggy_model_leaks_future`), 因果模型必须不变。
- **修复**:

  ```python
  att = att.masked_fill(self.mask[:T, :T] == 0, float("-inf"))
  ```

- **真题出现形式**: 面经里的高频变体: `* mask`、`masked_fill(mask == 1, ...)` 方向
  写反、mask 加在 softmax 之后、`tril`/`triu` 用反。追问通常是 "为什么 -inf 不会
  产生 NaN?" (对角线永远可见, 每行至少一个有限值; 整行全 mask 才会 NaN)。

## Bug 3: 训练循环缺 loss.backward() (行 160–161)

- **位置**: `train`, 行 151–165。行 160 `optimizer.zero_grad()` 之后行 161 直接
  `optimizer.step()`, 中间没有 `loss.backward()`。
- **症状**: **本题主导症状**。所有参数 `.grad` 是 None, AdamW 对 grad 为 None 的
  参数直接跳过, `step()` 是空操作 → loss 200 步纹丝不动, 恒等于初始值 ≈ ln(40)。
  实测曲线见文末。
- **怎么定位**: loss 一步都不降 (连噪声式的下降都没有) → 第一反应查更新三件套
  `zero_grad → backward → step` 是否齐、顺序是否对。快速验证: 训练几步前后对比
  参数 (`test_buggy_params_never_update`), 或查 `p.grad is None`。
- **修复**:

  ```python
  optimizer.zero_grad()
  loss.backward()
  optimizer.step()
  ```

- **真题出现形式**: 同族变体三选一: 缺 backward (loss 恒定)、缺 zero_grad (梯度
  跨 step 累积, loss 震荡/发散)、顺序错如先 step 后 backward。也见过
  `with torch.no_grad():` 套住了 forward 导致 backward 报错或静默无梯度。

## Bug 4: 权重绑定的 lm_head 忘了转置 (行 135)

- **位置**: `MiniGPT.forward`, 行 135: `logits = x @ self.wte.weight`。
- **正确语义**: weight tying 时 `wte.weight` 形状是 `(V, C)`, 输出头应为
  `logits = x @ wte.weight.T` (即 `F.linear(x, wte.weight)`), 把 hidden state 和
  每个 token 的 embedding 做内积。
- **为什么不报错 (关键)**: 本脚本 `VOCAB_SIZE == N_EMBD == 40`, `(B,T,40) @ (40,40)`
  形状恰好合法 —— **silent bug**。换任何 `V != C` 的配置立刻 shape error。
- **症状**: 最隐蔽的一个。`x @ E` 仍是可学习线性层, loss 也能降一些, 但它用的是
  E 的列而不是行, 与 embedding 端语义不一致, 绑定收益变成互相拖累, 收敛更慢、
  平台更高。主要靠 **读代码** 发现, 而不是看曲线。
- **怎么定位**: (a) 见到 tied head 就默写一遍形状: `E:(V,C)`, `x:(B,T,C)`,
  必须 `x @ E.T`; (b) 警惕一切 "巧合相等" 的维度 —— 面试官埋 silent bug 的标准
  手法就是让两个本不相关的维度相等。
- **修复**:

  ```python
  logits = x @ self.wte.weight.T
  ```

- **真题出现形式**: `Linear(out, in)` 参数顺序写反、tied weight 忘 `.T`、
  `view`/`reshape` 把 `(B,T,C)` 错拆导致 batch 和 time 串位 —— 共同点是 shape
  碰巧兼容所以不崩溃, 只能靠维度语义推理抓出来。

---

## 实测 loss 轨迹 (torch 2.8, CPU, seed=0, 可复现)

`python 08_bughunt_minigpt.py --buggy` (4 个 bug 全在):

```
step    0 | loss 3.7199
step   20 | loss 3.7215
step   40 | loss 3.7172
step   60 | loss 3.7200
step   80 | loss 3.7148
step  100 | loss 3.7244
step  120 | loss 3.7194
step  140 | loss 3.7300
step  160 | loss 3.7206
step  180 | loss 3.7204
step  199 | loss 3.7209
```

→ 恒定在 ln(40) ≈ 3.689 附近 (微小波动只来自随机 batch), 参数从未更新。
末 10 步均值 3.7236, 为初始值的 100.1% (> 80%, 满足 "基本不降")。

`python 08_bughunt_minigpt.py --fixed` (4 个 bug 全修):

```
step    0 | loss 3.7727
step   20 | loss 2.9896
step   40 | loss 2.2671
step   60 | loss 1.7239
step   80 | loss 1.1218
step  100 | loss 0.6895
step  120 | loss 0.4132
step  140 | loss 0.2323
step  160 | loss 0.2362
step  180 | loss 0.1772
step  199 | loss 0.1560
```

→ 末 10 步均值 0.1443, 为初始值的 3.8% (< 60%, 显著下降; 小语料重复 8 遍,
接近被记住)。
