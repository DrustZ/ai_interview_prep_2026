# 22 · 怎么给 code review agent 造训练数据

⏱ 通读 30 分钟 · 配套代码 10 秒跑完 · 建于 2026-07-30

> 姊妹篇：[`21_swe_agent_data.md`](21_swe_agent_data.md)（SWE agent 数据）。
> 那篇的主线是「验证器就是一个可复现的执行环境」；
> **这篇的主线正好相反：code review 没有验证器，所以整条 pipeline 都在「制造可验证性」。**
>
> 配套可跑代码：[`labs/cr_data/`](labs/cr_data/)，20 个测试，
> **采纳信号和 SZZ 都是真的调 git 算出来的。**
>
> 已有的 [`04_case_code_review_llm.md`](04_case_code_review_llm.md) 是**面试答题框架**；
> 这一篇是**实操 pipeline**，不重复。

---

## 0. 三个任务的验证器对比（一眼看清难点）

| | math | SWE agent | **code review** |
|---|---|---|---|
| 一条样本 | (题, 答案) | (issue, repo@commit, 测试) | **(diff, 评论)** |
| 验证器 | 字符串比对 | 跑测试 | **没有** ❌ |
| reward | 对/错 | 测试过/不过 | **「这条评论有用吗」——无 oracle** |
| 误报的代价 | 没得分 | 没得分 | **主动伤害**（消耗 reviewer 信任） |
| 最难的一步 | 找题去重 | 搭执行环境 | **定义「好」** |

> **一句话**：SWE agent 数据的工程量在**搭环境**；
> code review 数据的工程量在**发明一个能自动算、且和「有用」相关的信号**。

---

## 1. 业界的答案：两家独立收敛到了同一个信号 ⭐

| | ByteDance **BitsAI-CR**（FSE'25） | Atlassian **Comment Ranker** |
|---|---|---|
| 信号名 | **Outdated Rate** | **Code Resolution Rate (CRR)** |
| 定义 | 评论标记的代码行**在后续 commit 里被改了** | 作者在收到评论后**改了代码** |
| 达到 | Go 语言 **26.7%**（从 15% 起步） | **40–45%** |
| **人类基线** | **35–46%** | **~45%** |
| 规模 | 12,000+ WAU，21 万周页面浏览 | 每月 43,000+ PR |

**两家独立地选了同一个信号，因为它是唯一能在生产里零成本、全量拿到的。**

它的可爱之处：
- 不需要标注，历史里自己就有
- 直接对应业务价值（作者真的动手改了 = 这条评论产生了作用）
- **有人类基线可比**（人类 reviewer 也只有 35–46%）

它的问题在 §4 —— **它是有偏的**。

---

## 2. Step 1：数据从哪来

### 三类来源

| 来源 | 拿什么 | 规模 | 坑 |
|---|---|---|---|
| **开源 PR 评论** | GitHub review comments | CodeReviewer 数据集：**519 个仓库**（top 10k star 且 PR>2.5k）、9 种语言 | 噪声极大，见下 |
| **公司内部 MR** | 内部代码库的 review 历史 | BitsAI-CR：**12 万条**内部 MR 评论 | 最贵也最对口，风格与规范匹配 |
| **静态分析结果** | linter / SAST 命中 | 无上限 | 确定性强，但覆盖窄、措辞机械 |

> BitsAI-CR 的做法值得抄：**把三类混在一起**，然后用 LLM 做归一化 ——
> 过滤人工评论里的非实质内容、按规则分类、把过于简短的反馈**扩写**成完整描述、
> 把静态分析的结果**改写**成有针对性的建议。
> 最终每种主要语言约 **1.8 万条**样本（长尾语言约 5,000 条）。

### 必做的第一刀：去机器人

CodeReviewer 数据集的做法是两条：**后缀带 `bot`** + **一份已知机器人名单**。
配套代码 `gate.is_bot()` 实现了这两条。别小看它 —— 开源 PR 里机器人评论占比很高，
不滤掉的话模型第一件学会的事就是输出 `Coverage decreased (-0.4%)`。

### 数据长什么样（真实 schema）

```json
{
  "comment_id": "cm01",
  "commit": "5be7388939b5f29325581e268f55adb2cff062a2",
  "path": "shop/orders.py",
  "line": 18,
  "type": "code_defect",
  "author": "alice",
  "body": "find_order returns None when the id is missing; every caller will hit an AttributeError. Raise KeyError or return a sentinel."
}
```

注意**必须有 `(commit, path, line)` 三元组** —— 没有精确定位，
后面的采纳信号、SZZ、误报判定全都做不了。
只有评论文本的数据集（很多公开数据集就是这样）价值要打对折。

---

## 3. Step 2：制造可验证性（本文的核心）

```bash
cd labs/cr_data && python signals.py
```

### 信号 ①：采纳信号（弱证据，可全量）

```python
# 评论指向的行，在后续 commit 里被改了吗？
touched = changed_old_lines(root, commit, next_commit, path)   # 读 hunk 头
resolved = comment["line"] in touched
```

**一个必须做对的细节**：`git diff` 的 hunk 头是 `@@ -old_start,old_len +new_start,new_len @@`。
评论是挂在**旧版本**上的，所以要读**左边**。读成右边（新文件行号）就全错了，
而且不会报错。配套测试 `test_resolution_uses_old_line_numbers` 守这一条。

跑出来：

```
id     type             line  resolved      真值采纳   真值有用
cm01   code_defect      18    ✅ 251db53        1        1
cm03   code_defect      23    ❌                0        1   ← 说得对但没被采纳
cm07   praise            9    ✅ 251db53        0        0   ← 假阳性
cm14   nit_style         3    ✅ 7c1f627        0        0   ← 假阳性
cm17   security          4    ✅ 7c1f627        0        0   ← 假阳性且**事实错误**
采纳率 = 10/19 = 53%
```

**时间窗是超参不是常数**：BitsAI-CR 用**一周**。太长会把无关重构算成采纳，
太短会漏掉慢反应的作者。**这个要扫。**

### 信号 ②：SZZ（强证据，低召回）

一条 bug-fix commit → `git blame` 它删改的行 → 找到**引入 bug 的 commit**。
产出的是 `(历史版本的代码, 这一行确实有缺陷)` —— **由后来真实发生的修复所证明**。

```
bug-fix commit：5023e36  fix: apply_coupon raises KeyError when code does not match
  shop/orders.py  行 [21, 22] ← 由 5be7388 引入  ✅

可验证正样本：
  shop/orders.py:21  `if code == "SAVE10":`
    缺陷：apply_coupon raises KeyError when code does not match
    证据：fixed in 5023e36
```

**这是 code review 数据里唯一一类真正可验证的正样本** ——
它不依赖任何人的主观判断。

⚠️ **但 SZZ 的边界必须说清楚**（学界反复量化过）：

| 失效情形 | 占比（Linux kernel 上实测） |
|---|---|
| **ghost commit**（fix 只新增不删改 → blame 无从下手） | **17.47%** |
| **跨文件**（bug 成因在别的文件里） | **7.20%** |
| 综合：光靠 blame 解决不了的 | **超过 40%**（28% 要往上翻更多历史，14% 完全 blameless） |

外加：**纯格式化/重构 commit 会被误认成 inducing**。
缓解手段是 `git blame -w`（忽略空白）+ 重构检测。

> **结论：SZZ 是高精度低召回的种子，不是全集。**
> 正确用法是「SZZ 当强证据正样本 + 采纳信号当大规模弱标签」。

---

## 4. Step 3：质量把关 —— 两步，顺序不能反

```bash
python gate.py
```

### 第一步：过滤漏斗

```
raw                     19 条
去机器人                17 条  (−2)
去 nit/夸奖/纯提问      11 条  (−6)
去重复                  11 条  (−0)

过滤后有价值比例：8/11 = 73%（过滤前 8/19 = 42%）
```

**过滤的唯一目的是提高有价值评论的占比。不提高就是白做**
（配套测试 `test_gate_raises_useful_ratio` 断言必须提高 20 个点以上）。

### ⚠️ 词袋去重抓不到改写

```
阈值 0.35 → 0 条
阈值 0.25 → 0 条
阈值 0.15 → cm19≈cm01
阈值 0.10 → cm18≈cm11、cm19≈cm01
```

真值是 cm18 是 cm11 的改写（都在说 MD5）、cm19 是 cm01 的改写（都在说 None）。
**两条评论说的是同一件事，用的却是完全不同的词** —— 词法方法在这里天然失效。
`语义去重必须用 embedding`，真实规模再加 LSH 分桶。

（真实 PR 里多人重复指出同一问题**非常常见**。不去重的话，
高频问题在训练集里被过度加权，模型学会反复说同一句话。）

### 第二步：校准你的自动信号 ⭐⭐（大多数人跳过这一步）

把「代码后来变了」当成「这条评论有用」的预测，量它有多准：

```
precision 70%   recall 88%   F1 0.78
TP=7  FP=3  FN=1  TN=8
```

**假阳性 3 条**，机制都一样 —— 评论恰好落在**因别的原因被改动**的那一行上：

| id | 类型 | 内容 |
|---|---|---|
| cm07 | praise | "Nice, this is much cleaner 👍" |
| cm14 | nit | "nit: two blank lines here" |
| **cm17** | **security（事实错误）** | **"hashlib is not thread-safe, wrap the call in a lock."** |

⭐ **cm17 是最危险的**：一条**事实错误**的评论被自动信号盖章成「有用」。
直接进训练集就是在教模型**编造听起来专业的错误结论** ——
而这恰好是 code review agent 最容易犯、也最伤信任的错。

**假阴性 1 条**：cm03 说得对，作者当时没改，**三周后它变成了一个真 bug**（SZZ 证实）。
→ **采纳信号会系统性低估「作者当时不认可但其实正确」的评论。**

> **所以采纳信号是有偏的 proxy，不能直接当 label。**
> 正确用法是「**大规模弱标签 + 小规模人工校准**」——
> BitsAI-CR 每天抽样 ≤10%、每周人工标注汇总，就是在做这件事。
> 这和你在 Anthropic take-home 里「拿医生标注校准 grader」是同一个动作。

---

## 5. Step 4：正负样本 ⭐

```bash
python pairs.py
```

### 正样本按证据强度分层，不能等权

```
resolved_comment      10 条  证据=weak     其中实际没用的 3 条
szz_verified_defect    2 条  证据=strong   其中实际没用的 0 条
```

**实践**：强证据权重 1.0，弱证据 0.3–0.5；
或者干脆**只用强证据训 reward model**，弱证据只用来训生成。

### 「负样本」有五种含义，其中一种是陷阱

| 类别 | 训练目标 | 本 lab 产出 |
|---|---|---|
| ① **事实错误** | 别编 | 2 条 |
| ② **对但没价值**（nit/夸奖） | 别啰嗦 | 7 条 |
| ③ **位置指错** | 定位要准 | 3 条（合成：把真评论的行号挪开） |
| ④ **重复别人说过的** | 别重复 | 4 条 |
| ⑤ ~~**没有任何评论的代码行**~~ | — | **9 条 ⚠️ 陷阱组** |

⭐ **把 ⑤ 当负样本是这个领域最经典的错误。**

两个理由：

1. **数量上会淹没正例。** 玩具仓库里就已经 9:12；真实仓库里是**几千比一**。
2. **它们里面有真问题。** 配套测试 `test_an_unreviewed_line_actually_contained_a_real_bug`
   证明了这一点：`shop/orders.py:21` 当时**没有有效评论**，三周后被 fix 掉了 ——
   **它本该是正样本。**

> **「没有评论」只说明没人看，不说明代码没问题。**
> 这是 positive-unlabeled learning，不是二分类。
> （和 [`21`](21_swe_agent_data.md) 里「没有测试改动的 commit 不等于没 bug」是同一类错误。）

③ **位置指错**这一类特别值得注意：它是**最便宜的高价值合成负例** ——
把一条真评论的行号随机挪开就行，零成本，而且直接训练「定位准确性」这个
生成式 reward 很难覆盖的维度。

### 偏好对：必须在同一个 (文件, 行) 上下文里配对

```json
{
  "context": {"path": "shop/orders.py", "line": 18},
  "chosen": "find_order returns None when the id is missing; every caller will hit an AttributeError...",
  "rejected": "This references the old `read_orders` helper that was removed last week.",
  "chosen_kind": "resolved_comment",
  "rejected_kind": "factually_wrong",
  "same_file": true
}
```

**如果 chosen 来自 auth.py、rejected 来自 orders.py**，模型可能学到
「auth 相关的评论更好」这种和质量无关的捷径 —— **这是最常见的 pair 泄漏**。
配套测试 `test_pairs_are_matched_within_the_same_file` 守这一条。

生成的 24 对里 rejected 的分布：`low_value_nit` 13、`duplicate` 7、
`factually_wrong` 2、`misplaced` 2。**要有意识地配比** ——
如果九成 rejected 都是 nit，模型只会学到「别说 nit」，学不到「别编」。

---

## 6. Step 5：Reward 设计 ⭐⭐

```bash
python reward.py
```

### 和 math / SWE 的根本差异：**不对称**

```
math：reward = 答案对不对    → 对称，找不到只是没得分
SWE ：reward = 测试过不过    → 对称
CR  ：**误报会主动造成伤害**  → 不对称
```

一条错误的 review 评论不是「没得分」，它**消耗 reviewer 的信任**。
ByteDance 的内部数据：**只有 30% 的 review 会被立刻看**；
一旦机器人开始说废话，开发者会整体屏蔽它。

### 三层 reward，硬闸门在最前面

| 层 | 内容 | 特点 |
|---|---|---|
| **r1 确定性** | 行号越界？引用了不存在的符号？命中 linter/SAST 规则？ | 免费、不漂移、**不需要校准** |
| **r2 历史证据** | SZZ 证实（1.0）> 作者改了这一行（0.5）> 无（0） | 来自 §3 |
| **r3 LLM judge** | 最贵、最会漂、**必须用人工标注校准** | 权重最低 |

**顺序很重要**：r1 是**硬闸门**，不是加权项。
「引用了代码里不存在的符号」这种事没有讨论余地，直接判负分：

```
cm11 [security] +0.804   「MD5 for password hashing is broken...」
      r1=1.00  命中静态分析规则（强证据）
      r2=0.50  作者改了这一行（有 30% 假阳性）
cm16 [question] +0.304   「which db driver is this?」
      r1=0.50  —
      r2=0.00  无历史证据
```

### ⭐ 为什么不能最大化 F1（这一节被我自己的数据修正过）

我原本想演示「F1 最优 ≠ 产品最优」。跑出来**在默认参数下两者恰好重合**。
所以正确的问题不是「它们是否分离」，而是**「误报多贵时才分离」**：

| 每条误报的信任衰减 | F1 最优阈值 | **产品（实际采纳）最优阈值** | 差距 |
|---|---|---|---|
| 0.95（误报几乎无害） | 0.675 | **0.075** | −0.600 |
| 0.85 | 0.675 | 0.550 | −0.125 |
| 0.75 | 0.675 | 0.675 | 0.000（巧合） |
| 0.60 | 0.675 | 0.775 | +0.100 |
| 0.45（一条误报让用户少读一半） | 0.675 | **0.825** | +0.150 |

⭐ **F1 最优阈值岿然不动（永远 0.675），产品最优随误报代价单调移动。**
**F1 根本不知道一次误报值多少钱。**

所以真正要问的是：**「一条误报到底让用户少看了多少条后续评论？」**
这个数要从线上量（BitsAI-CR 的 Outdated Rate 就是干这个的）。
量出来之后，**阈值不是调参调出来的，是算出来的**。

这也顺带解释了 BitsAI-CR 为什么把 **ReviewFilter 做成独立一段**，
而不是去调 RuleChecker 的阈值 —— 它的阈值要按产品目标单独定，
不该和 RuleChecker 的召回耦合。

### 两段式的真实收益（BitsAI-CR 18 周线上数据）

```
RuleChecker 精度   27.9%  →  62.6%
ReviewFilter 精度  35.6%  →  75.0%（峰值）
Go 的 Outdated Rate  15%  →  26.7%
```

### ⭐ 一个反直觉的发现（直接可抄）

BitsAI-CR 比较了 ReviewFilter 的三种输出格式：

| 格式 | 推理耗时 | 精度 |
|---|---|---|
| Direct Conclusion（只出结论） | 1.7s | 63.27% |
| Reasoning-First（先推理后结论） | **31.0s** | 65.80% |
| **Conclusion-First（先结论后理由）** | **1.7s** | **77.09%** ← 选它 |

**先给结论再给理由，比先推理再给结论精度高 11 个点，而且快 18 倍。**

一个可能的解释：先写结论迫使模型基于证据表态；
而先推理会让模型被自己生成的推理链带跑 —— **推理链会为一个不成立的结论找补**。

### reward hacking：三个要按周画趋势的指标

| 形态 | 长什么样 | 怎么监控 |
|---|---|---|
| ① **模糊化** | "this **might** cause an issue" —— 用 might/could 让自己不可证伪 | 对冲词占比 |
| ② **万能话术** | "consider adding a unit test" —— 对任何代码都成立 | 模板句占比 |
| ③ **散弹枪** | 同一行堆五条评论提高命中率 | 每行评论数 |

**配套的硬护栏**：每条评论必须给出**可定位的行号 + 可证伪的断言**。
「考虑加个测试」这种既不可定位也不可证伪的话，**在 r1 层就砍掉**。

---

## 7. 完整 pipeline

```
开源 PR 评论 + 内部 MR 评论 + 静态分析结果
   ↓  去机器人（后缀 + 名单）
   ↓  去 nit / 夸奖 / 纯提问
   ↓  语义去重（embedding + LSH，**不是词袋**）
   ↓  LLM 归一化（扩写过简的、改写机械的）
   ├─→ 采纳信号（全量、弱证据、**30% 假阳性**）
   ├─→ SZZ（低召回、强证据、**>40% 的 case 覆盖不到**）
   └─→ 人工标注（每天 ≤10% 抽样、每周汇总）← **用来校准上面两个**
   ↓  正样本按证据强度分层加权
   ↓  负样本四类（**「未评论行」单独隔离**）
   ↓  偏好对（同文件同上下文配对）
   ↓
SFT / DPO / RM  →  RuleChecker
                        ↓
                   ReviewFilter（Conclusion-First，阈值按误报代价算）
                        ↓
                   线上 → Outdated Rate → 回流
```

**BitsAI-CR 的规则下线判据值得抄**：
> 一条规则如果「**Outdated Rate 约 25%（±5）且精度约 65%（±5）持续 14 天**」就算合格；
> **精度高但 Outdated Rate 持续偏低的规则要下线** ——
> 技术上正确但实践上多余。

这条判据的漂亮之处：**它同时约束了「说得对」和「值得说」**，
而后者是纯技术指标永远看不到的。

---

## 8. 十个坑

| # | 坑 | 后果 |
|---|---|---|
| 1 | 把「没人评论的行」当负样本 | 负例淹没正例，且里面有真 bug |
| 2 | 采纳信号直接当 label | 30% 假阳性，**其中包含事实错误的评论** |
| 3 | 读 hunk 头的右边（新文件行号） | 采纳信号全错，且不报错 |
| 4 | 用词袋去重 | 抓不到改写；同一问题被过度加权 |
| 5 | chosen/rejected 跨文件配对 | 模型靠文件名走捷径 |
| 6 | rejected 全是 nit | 只学会「别说 nit」，学不会「别编」 |
| 7 | 最大化 F1 | F1 不知道误报值多少钱 |
| 8 | 把 SZZ 当全集 | >40% 的 bug 它找不到；ghost commit 占 17% |
| 9 | 不区分证据强度 | 强弱证据等权 = 用噪声稀释信号 |
| 10 | 只有评论文本、没有 (commit, path, line) | 后面所有信号都做不了 |

---

## 9. 和 SWE agent 数据的对照（两篇的总结）

| | SWE agent（[21](21_swe_agent_data.md)） | code review（本篇） |
|---|---|---|
| 核心难点 | **搭执行环境** | **定义「好」** |
| reward | 二元、可验证 | **有偏 proxy + 人工校准** |
| 误报代价 | 对称 | **不对称（伤信任）** |
| 主要产出率损耗 | 环境和执行（58 万 → 3.2 万） | 噪声过滤（42% → 73% 有价值） |
| 最经典的错误 | gold patch 混进测试文件 | 把未评论的行当负样本 |
| 可以合成吗 | ✅ 大规模合成（SWE-smith 5 万条） | ⚠️ 只有「位置指错」这类能便宜合成 |
| 你的 math 经验 | 难度筛选、去重、去污染直接迁移 | **judge 校准**直接迁移 |

**一句可以在面试里说的话**：

> 「SWE agent 的数据难在环境，code review 的数据难在**没有 oracle**。
> 业界的答案是**从历史里制造可验证性** —— ByteDance 和 Atlassian
> 独立地收敛到同一个信号：**评论指向的代码后来被改了吗**。
> 但这个信号有偏：我实测它有 30% 假阳性，其中最危险的一条是
> **事实错误的评论因为落在一行恰好被改的代码上而被记成有用** ——
> 直接拿它当 label，就是在教模型编造听起来专业的错误结论。
> 所以正确的用法是大规模弱标签 + 小规模人工校准，
> 和我在 grader 上做的『拿医生标注校准 ROUGE』是同一个动作。」

---

## 10. 配套代码

```bash
cd labs/cr_data
V=/Users/mingrui/Documents/codes/interview/.venv/bin/python
$V toyreview.py && $V signals.py && $V gate.py && $V pairs.py && $V reward.py
$V -m pytest test_cr_data.py -q      # 20 passed
```

---

## 11. 论文与工程报告清单

| 工作 | 一句话 | 链接 |
|---|---|---|
| **BitsAI-CR**（ByteDance, FSE'25） | **最好的生产报告**：219 条规则、两段式、Outdated Rate、数据飞轮、12k WAU | [arXiv 2501.15134](https://arxiv.org/abs/2501.15134) |
| **Atlassian Comment Ranker** | ModernBERT **只用评论文本**做 CRR 分类器，就追平人类 | [engineering blog](https://www.atlassian.com/blog/atlassian-engineering/ml-classifier-improving-quality) |
| **CodeReviewer**（MSR/MSFT） | 领域基准数据集：519 仓库、9 语言、三个任务 | [arXiv 2203.09095](https://arxiv.org/abs/2203.09095) |
| **SZZ 及其后继** | bug-inducing commit 识别；ghost commit 17.47%、跨文件 7.20% | [Neural SZZ (ASE'23)](https://baolingfeng.github.io/papers/ASE2023.pdf) · [AgenticSZZ](https://arxiv.org/html/2602.02934) |
| **DeepCRCEval** | 重新审视 code review 评论生成的评测方式 | [Springer](https://link.springer.com/chapter/10.1007/978-3-031-90900-9_3) |
| code review benchmark 综述 | pre-LLM 与 LLM 时代的评测实践 | [arXiv 2602.13377](https://arxiv.org/abs/2602.13377) |

**读的顺序**：BitsAI-CR（生产全貌）→ Atlassian（最小可行的质量分类器）
→ CodeReviewer（数据集怎么建）→ SZZ（可验证正样本的来源与边界）。

---

## 12. 相关材料

- [`labs/cr_data/`](labs/cr_data/) —— 本文的可跑代码
- [`21_swe_agent_data.md`](21_swe_agent_data.md) —— 姊妹篇：SWE agent 数据
- [`04_case_code_review_llm.md`](04_case_code_review_llm.md) —— code review LLM 的**面试答题框架**
- [`16_case_rl_data_pipeline.md`](16_case_rl_data_pipeline.md) —— RL 数据流水线通论
- [`15_case_eval_pipeline.md`](15_case_eval_pipeline.md) —— judge 校准的通用方法
