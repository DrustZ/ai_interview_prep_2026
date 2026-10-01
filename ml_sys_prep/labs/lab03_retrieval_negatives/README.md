# Lab 03 · InfoNCE、假负例陷阱、Matryoshka 级联成本

⏱ 40 分钟（砍时:只跑 `solution.py`，10 分钟）｜ 安排在 **Day 2 下午**（Exa 对口）

对口 [06 §五/§六/§九](../../06_search_post_training.md) 与 [13 · Exa 卡](../../13_company_cards.md)。

## 怎么做

```bash
python3 solution.py        # 四部分演示，0.3 秒
python3 test_solution.py   # 10 条断言，全绿
```

## 四个实测结论

### A. 为什么必须换 hard negative（不是"因为大家都这么做"）

```
easy/random   loss=0.0003   |grad|=0.0046
hard          loss=0.4303   |grad|=1.8985      <- 梯度差 400 倍
```

模型早就能把无关文档分开，easy negative 的 loss 和梯度都趋近 0，**再训是在做无用功**。这才是换 negative 的真正理由。

### B. 假负例陷阱（本 lab 的题眼）

语料里有一个 `unlabeled_relevant`：和正例讲同一件事、同样相关，但**标注集里没有它**。

```
dot(positive, unlabeled_relevant) = 0.910
max dot(positive, hard_neg_*)     = 0.716

训练前  unlabeled_relevant 排名 = 2
朴素挖 top-6 hard negatives     = [unlabeled_relevant, hard_neg_4, ...]   <- 污染
训练后  unlabeled_relevant 排名 = 4                                        <- 被推走
```

你以为在做 hard negative mining，实际上在**系统性地把自己的正例训练成负例**。

这正是 Exa 在 [evals-at-exa](https://exa.ai/blog/evals-at-exa) 里放弃 MS Marco 式封闭评测的**第一个理由：稀疏标注导致假负例**。训练侧和评测侧是同一个病。

### C. 去噪：一个 tau 的差别

规则：`dot(candidate, positive) > tau` 就跳过——**与已知正例极其相似的候选，大概率本身就是正例，只是没被标注**。

关键是这条规则**不需要知道谁是假负例**，只看候选与正例的相似度。它之所以可用，是因为假负例与正例的相似度（0.910）显著高于真负例（≤0.716）——测试 `test_denoise_tau_separates_false_negative_from_true_hard_negatives` 就在断言这个前提。

```
去噪后 top-6 = [hard_neg_4, hard_neg_0, ...]   （unlabeled_relevant 被排除）
训练后  unlabeled_relevant 排名 = 2             <- 保住了

对照：污染=4   去噪=2
```

### D. Matryoshka 级联的可算权衡（2012 文档 / 64 维）

```
coarse_dim  shortlist   recall@10   成本
64          10          1.00        100% of full
32          50          1.00         52%
16          50          1.00         27%        <- 1/4 维，召回不掉
 8          50          0.80         15%        <- 开始掉
 8         200          1.00         22%        <- 加大 shortlist 买回来了
 4          50          0.00          9%        <- 截过头，崩溃
 4         200          0.60         16%
```

三个可以直接说的结论：
1. **降维省的是全库扫描成本**，`N × m` 里 N 很大，所以 m 的每一点都很值钱；
2. **精排贵但只碰 top-k**，所以加大 shortlist 是便宜的补救——`m=8, k=200` 用 22% 的成本拿回了满召回；
3. 但截过头（1/16 维）任何 shortlist 都救不回来，信息已经在粗筛阶段丢了。

这就是 Exa 把 2048 维截到 **256 维（1/8）省 20× 内存**的同一个权衡。面试里能把这条曲线画出来，比背"我们用 Matryoshka"强得多。

## 追问预演

- **「in-batch negatives 够不够？」** 训练初期够（便宜、batch 越大越好），后期必须换成从索引里挖的 hard negatives。工程上还要注意跨设备收集 in-batch negatives（GradCache 之类），否则大 batch 放不下。
- **「hard negative 从哪挖？」** BM25 的 top-k 非相关、上一版模型的 top-k 非相关（ANCE 式迭代，每隔若干步刷新索引）。挖完必须去噪，见 C。
- **「除了 tau 还有什么去噪法？」** 用 cross-encoder teacher 给候选打分，分数过高的剔除或改成 soft label；或者保留多正例（multi-positive）而不是强行二分。
- **「temperature 怎么选？」** 太小 → softmax 饱和、梯度消失（本 lab 里 T=0.05 时 loss 就已经趋近 0）；太大 → 区分不出 hard 和 easy。要在 dev set 上扫。
- **「离线 recall 提升了，线上没动，为什么？」** 训练时的候选分布必须接近线上第一阶段召回器的输出分布，否则 offline gain 不迁移。见 [03 §4](../../03_model_training_reward.md)。
