# 21 · 怎么给 SWE agent 造训练数据（从 GitHub 到可训练实例）

⏱ 通读 35 分钟 · 配套代码 5 分钟跑完 · 建于 2026-07-30

> **写给谁**：做过 math/STEM 数据 curation，但没做过 SWE 数据的人。
> 全文围绕一个判断展开：**这两件事的 pipeline 骨架是一样的，
> 但「验证器」的形态完全不同 —— 而验证器决定了其余所有设计。**
>
> 配套可跑代码：[`labs/swe_data/`](labs/swe_data/)，纯 Python + pytest，
> 无需网络、无需 Docker、无需 API key，**F2P/P2P 是真的跑测试跑出来的**。

---

## 0. 一句话看清差别

| | math / STEM | **SWE** |
|---|---|---|
| 一条样本 | `(题目, 答案)` | `(issue 文本, repo@commit, 测试集合)` |
| 验证器 | 字符串/符号比对，**微秒级、无状态** | **跑测试套件**，秒到分钟级、**有状态、要装依赖** |
| 造数据的瓶颈 | 题目来源与去重 | **搭执行环境**（占 80% 的工程量） |
| 上下文 | 几百 token | 整个仓库，几万到几百万 token |
| 一次 rollout | 一次前向 | **几十步工具调用** |
| 失败模式 | 答案错 | 答案错 / 补丁打不上 / 环境炸了 / 测试 flaky |

> **最重要的一条**：math 数据里「验证」是廉价的后处理；
> SWE 数据里 **「验证器」本身就是产品**。
> 你造的不是一批题，是**一批可复现的执行环境**。
> 这解释了本文后面几乎每一个设计决策。

---

## 1. 四条数据路线（先选路，再谈细节）

| 路线 | 数据从哪来 | 怎么验证 | 单仓库产出 | 代表工作 |
|---|---|---|---|---|
| **A · 挖 PR** | 真实 PR + 它带的测试 | 执行 F2P/P2P | ~200（12 仓库 2,294 条） | SWE-bench、SWE-Gym、SWE-rebench |
| **B · 合成 bug** | **先搭环境**，再往干净代码里注入 bug | 用仓库**已有**的测试 | **~381**（128 仓库 5 万条） | **SWE-smith** |
| **C · commit 回译** | 任意 commit，**不要求有 PR/测试** | **自动生成**测试 + 回译 issue | ~600（13 仓库 8.1k） | R2E-Gym / SWE-GEN |
| **D · 不执行** | 海量 PR，**完全不搭环境** | 与 gold patch 的**字符串相似度** | 无上限（~1100 万 PR） | **SWE-RL**（Meta） |

**怎么选**：

```
要做 benchmark / 要可信的 reward      → A（贵、慢、但每条都可信）
要 RL 训练量、能接受合成分布偏移      → B（性价比最高，$1,360 造 5 万条）
仓库没测试 / 想覆盖长尾              → C
只有 SFT 预算、或者做冷启动           → D（reward 是 proxy，但能上百万级）
```

**实践里通常是 B 为主 + A 做 held-out**：合成数据训练，真实 PR 数据评测。
理由和 math 一样 —— **训练分布可以是合成的，但评测分布必须是真实的**。

---

## 2. Step 1：选仓库（这一刀性价比最高）

```bash
cd labs/swe_data && python github.py
```

### 三条拿数据的路

| 路 | 怎么拿 | 限制 | 适合 |
|---|---|---|---|
| REST/GraphQL API | `api.github.com` | 认证后 5000 req/h | 几百个仓库 |
| **GH Archive** | BigQuery 或下载每小时 `.json.gz` | 无 | **全量元数据** |
| **本地 clone** | `git clone --filter=blob:none` | 无 | **拿 patch 内容** |

> **SWE-rebench V2 的做法值得直接抄**：用 GH Archive 拿元数据
> （issue 正文、PR 讨论、commit SHA、license、语言），
> 然后**分布式 map-reduce 克隆仓库、从本地 git 历史直接取 patch**，
> 完全绕开 API 速率限制。这样处理出 **21,000 个仓库 / 58 万个候选实例**。
>
> **不要用 API 逐个拉 diff** —— 那是这条 pipeline 最经典的自杀方式。

### 筛选阈值（各家实际用的）

| | SWE-smith | SWE-rebench V2 |
|---|---|---|
| 来源池 | PyPI 下载量前 5000 的包 | GH Archive 全量 |
| star | **≥ 1000** | 高资源语言 **≥25**；长尾语言 ≥10 |
| issue | — | closed issue **≥15**；长尾 ≥1 |
| license | — | **必须宽松许可** |
| 排除 | **SWE-bench 的 12 个测试仓库** | 同 |
| 结果 | 128 个仓库 | 21,000 个仓库 |

⭐ **最值得记的一个数**：SWE-rebench V2 量化过，
**这套阈值保留约 20% 的仓库，却覆盖约 80% 的任务** ——
需要搭环境的仓库数直接降到 1/5。

**任务产出是极度长尾的**，所以正确的顺序是：先给 `yield_score` 高的仓库搭环境。
代码里 `score_repo()` 给了一个可用的打分。

### 三个容易漏的过滤

```python
if meta.get("fork"):      reject("是 fork —— 会和上游产生重复实例")
if meta.get("archived"):  reject("已归档 —— 环境多半装不上")
if lic not in PERMISSIVE: reject("非宽松许可 —— 训练数据的法务风险")
```

---

## 3. Step 2：从 PR 挖候选（附完整代码）

```bash
python mine.py
```

### 概念对齐：PR 的本质

> **一个 PR = 一个 base commit + 一个 diff。**
> 所以 pipeline 完全可以跑在本地 git 历史上，不需要 GitHub API。
> 配套代码就是这么做的 —— 造一个带真实 git 历史的玩具仓库，整条链路真跑。

### 关键动作：把 diff 劈成两半

```python
solution_patch = diff 里的 **非测试文件** 部分   # gold answer，训练时不给模型
test_patch     = diff 里的 **测试文件** 部分     # 验证器，评测时才打上
```

**为什么必须劈开**：如果 gold patch 里混进了测试文件，模型在训练时
**能直接看到断言** —— 这是 SWE 数据里最经典的答案泄漏。
（配套测试 `test_solution_patch_never_touches_test_files` 就是守这一条的。）

### ⚠️ 「什么是测试文件」这个小函数，是正确性的隐藏来源

SWE-rebench V2 论文用的是无锚定子串匹配：

```python
NAIVE_TEST_RE = re.compile(r"(?i)(test(?:ing|s)?|e2e)")     # 论文里的
```

它会把 `src/contest.py`、`build/latest/x.py`、`app/protests/views.py`
全部判成测试文件。后果不是「多几条噪声」，而是
**这些文件的改动被归进 test_patch，solution_patch 变空，整个实例被静默丢弃**。

加路径段边界就好了：

```python
TEST_RE = re.compile(r"(^|/)(tests?|testing|e2e)(/|$)|(^|/)test_[^/]*\.py$|_test\.py$", re.I)
```

### 便宜的过滤放在贵的验证之前

执行验证一次要几分钟到几十分钟，而下面这些是微秒级的。
**真实 pipeline 里这一步砍掉 80%+ 的候选**：

```python
if not code_files:            reject("只改了测试或文档")
if not test_files:            reject("没有测试改动 → 无法自动验证")
if len(code_files) > 20:      reject("改动面过大，多半是重构/版本升级")
if patch_lines > 400:         reject("patch 过长")
```

---

## 4. Step 3：搭环境 —— **整条 pipeline 80% 的工程量在这里**

这是 SWE 数据和 math 数据最大的分岔口。math 没有对应物。

### 为什么这么难

- 每个仓库的依赖、构建系统、测试 runner 都不一样
- **同一个仓库的不同历史时点依赖也不一样**（三年前的 commit 装不上今天的依赖）
- 编译型语言打完补丁要**重新编译**，否则跑的是旧的二进制
- 测试输出格式各异，要解析成结构化结果

### 三代做法

**① 人工写 Dockerfile**（SWE-bench）—— 12 个仓库尚可，128 个就不行了。

**② Agent 搭环境**（SWE-smith / SWE-rebench V2 / SetUpAgent）：

> SWE-smith：让 **SWE-agent 在最新 commit 上跑最多 100 步**，
> 指令是「装好这个仓库并跑通测试套件」。然后人工核对安装与测试指令、
> 检查 **>80% 的已有测试能过**，最后固化成一个 Docker 镜像。
> **剩下的人工量：每个仓库约 7 分钟**（从 agent 轨迹里抠出正确的安装步骤）。

> SWE-rebench V2：用 **mini-SWE-agent + Qwen3-Coder-480B** 做交互式 setup agent，
> 闭环调试（读代码 → 试装 → 看报错 → 改脚本）。每种语言预建 base 镜像
> （Java 分 JDK 11/17/21 三个），**每个仓库只推断一次 setup，然后复用到该仓库的所有任务**。

**③ 关键的架构决策：环境按仓库复用，不按实例**

```
❌ 每个 instance 一个镜像   → 存储爆炸（SWE-bench companion env 是 TB 级）
✅ 每个 repo 一个基础镜像   → 实例只存 (base_commit, patches)，运行时 checkout
```

**这也是 SWE-smith 「环境优先」路线的真正优势**：它把最贵的一步（搭环境）
从「每个实例一次」变成「每个仓库一次」。

### 一句可以直接引用的判据

> **能不能自动搭好环境，决定了你的数据规模上限。**
> 挖 PR 的产出率再高，卡在环境上就一条都出不来。
> 所以这条 pipeline 的正确投入顺序是：**先解决环境，再谈数据量**。

---

## 5. Step 4：执行验证（F2P / P2P）—— 核心中的核心

```bash
python mine.py        # 会真的跑 pytest，看得到每一步
```

### 三步验证，缺一不可

```
① 在 parent commit 上跑全套测试   → 必须全过    （证明环境是好的）
② 打上 test_patch 再跑            → 新测试必须 FAIL（证明 bug 真存在）
③ 再打上 solution_patch 跑        → 必须全过    （证明这个 fix 真管用）

F2P = ②失败 且 ③通过  ← 奖励信号
P2P = ②通过 且 ③通过  ← 防回归护栏
```

**这三步是 SWE-bench 的原始定义，后续所有工作都沿用。**
配套代码 `mine.validate()` 一比一实现了它。跑出来长这样：

```
挖到 8 个 commit（不含 initial）
  便宜过滤后剩 5 个进入执行验证
  ✅ 0f2d65e fix: mean() crashes with ZeroDivisionError    F2P=1 P2P=1
  ✅ 4eaae11 fix: median() wrong for even-length input     F2P=1 P2P=2
  ✅ 8e69ade fix: slugify keeps punctuation in the slug    F2P=1 P2P=3
  ✅ f101760 fix: truncate() should append an ellipsis     F2P=1 P2P=4
  ✅ a223d01 fix: clamp silently returns garbage           F2P=1 P2P=5
  ❌ 1331dd3 docs: add install section        只改了测试或文档
  ❌ 8af8f41 test: add idempotence check      只改了测试或文档
  ❌ 63ff97d chore: clarify mean() docstring  没有测试改动 → 无法自动验证

最终 5 个可用实例（产出率 62%）
```

### ⭐ 为什么 P2P 不能省

**只用 F2P 当 reward，模型可以把不相关的代码删光**，只要新测试过就行。
这是 SWE 里最直接的 reward hacking 路径。P2P 是「别把别的弄坏」的约束。

对应到你熟悉的 math 场景：F2P 是「答案对不对」，
P2P 是「你没有为了答对而把题目改了」。

### 两个实践细节

**跑全量测试还是只跑相关的？**
> SWE-rebench V2：**始终跑全套**，不做子集选择 ——
> 覆盖更全，而且能发现意料之外的副作用。代价是慢。

**flaky 怎么办？**
> SWE-rebench V2：**每个候选跑 3 次**，只保留三次结构化结果完全一致的实例。
> 这一条很贵但很必要 —— flaky 测试进了训练集，就是持续注入的 reward 噪声。

---

## 6. Step 5：合成路线（SWE-smith）—— 规模从这里来

```bash
python synth.py
```

### 核心洞察：把顺序倒过来

```
SWE-bench：  先找任务（PR）  →  再给每个任务搭环境   ← 卡在环境上
SWE-smith：  先搭环境        →  再在环境里批量造任务  ← 环境成本被摊薄
```

> 论文原话的意思：**执行验证不只能验证解法，
> 它也能筛出「哪些改动是真 bug」** —— 造一堆候选，只留下真的弄挂测试的那些。

### 四种造 bug 的策略

| 策略 | 做法 | 特点 |
|---|---|---|
| **LM Modify** | 给模型一个函数，让它引入错误 | 最像真实 bug |
| **LM Rewrite** | **只给函数签名 + docstring**，让模型重写 | 更多样，也更难 |
| **Procedural** | 改 AST：删条件/删循环/换运算符/…共 13 种 | **免费**，本文代码实现的就是这个 |
| **Combine Bugs** | 把同文件/同模块的多个 bug 合并 | 造出需要改多处的**难题** |
| **Invert PR** | 让模型把一个真 PR 的改动**撤销**回去 | 分布最接近真实 |

⚠️ **注意 Invert PR 的一个细节**：SWE-smith **不 checkout PR 的 base commit** ——
因为老版本的仓库和现在的安装配置可能不兼容。它直接在当前版本上「反向应用」。
这是「环境优先」路线的一个必要妥协。

### 跑出来的样子

```
基线：7 个测试全过
尝试 24 次变异 → 7 个有效 bug（产出率 29%）
  procedural:return_none  3
  procedural:off_by_one   2
  procedural:drop_if      1
  procedural:swap_binop   1
```

产出率 29% 是正常的 —— 大量变异要么改不动、要么没弄挂任何测试、
要么把整个模块炸了（导入失败）。**这三类都要显式丢掉**：

```python
if not res:                 continue   # 语法/导入直接崩
if not broke:               continue   # 没弄挂测试 → 不是 bug
if len(broke) == len(res):  continue   # 全挂了 → 太粗暴，不是有意义的任务
```

### 造 issue 文本

> SWE-smith 的最终配方：把 **`.diff`、一个随机 F2P 测试的源码、
> 以及带 bug 跑测试的输出**一起给 LM，让它写成 GitHub issue 风格，
> **并且包含基于 F2P 测试的复现代码**。
> 成本：**每条 2.54 美分**；整个 5 万条数据集 **$1,360**
> （造 bug $1,000 + 自动装仓库 $160 + 给 1 万个 bug 生成 issue $200）。

**论文的一个结论值得记**：**LM 生成的 issue 文本能有效近似真实的**。
这条很重要 —— 它意味着 issue 链接不是硬需求。

---

## 7. Step 6：curate（这一步你的 math 经验直接迁移）

```bash
python curate.py
```

### 去重：单位是「改动的语义」，不是文本

同一个仓库里「给 N 个函数各加一个 None 检查」的 PR 可能有几十个 ——
patch 文本高度相似，**对模型是同一道题**。

做法：归一化 patch（只保留 +/- 行、去注释去空白）→ shingle → MinHash → LSH 分桶。
和你在 math 上做近重复是同一套，只是**归一化函数不同**。

> **我在这里踩了一个值得记的坑**：合成实例最初存的是**整份修改后的源码**，
> 而挖来的实例存的是 **unified diff**。`normalize_patch` 只保留 `+/-` 开头的行，
> 于是合成实例归一化后**全是空串** → MinHash 签名全相同 → 去重把它们**全判成重复**，
> 而且一声不吭。
> **两个数据源 schema 不一致，会让下游过滤静默失效。**
> 修法是加一行护栏：

```python
def assert_is_diff(patch, who=""):
    if not normalize_patch(patch).strip():
        raise ValueError(f"归一化后为空，{who} 传进来的多半不是 unified diff")
```

### 去污染：三层，缺一不可

```
① 整仓排除    SWE-bench 的 12 个测试仓库，**整个仓库**都不能用
              （不只是那 2,294 条实例 —— 同仓库其他 PR 会泄漏代码库结构和风格）
② 精确匹配    instance_id / commit SHA
③ 近重复      patch 与 benchmark patch 的 MinHash 相似度
```

**只做 ①② 不够**：同一个 bug 可能出现在 fork 里、在别的仓库 vendored 的副本里。

**还要加时间维度**：训练数据的 commit 时间必须早于评测集的时间窗口。
（这也是 SWE-bench-Live / SWE-rebench 持续刷新的动机 —— **benchmark 会腐烂**。）

### 难度：别用 patch 行数，用 pass@k

```python
def empirical_difficulty(inst, rollout_results):
    p = sum(rollout_results) / len(rollout_results)
    return {"pass_rate": p, "keep_for_rl": 0 < p < 1, ...}
```

⭐ **这一条和你在 math/STEM 上做的自适应难度筛选是同一件事**：

```
pass@k = 0  →  无梯度信号，GRPO 组内优势全为 0，**这一组 rollout 白跑**
pass@k = 1  →  同样无信号
0 < p < 1   →  有区分度，这才是该留的
```

`static_difficulty`（patch 行数 + 文件数）只能当**初筛和分桶**用，
**不能当结论** —— 行数和难度的相关性没有你以为的高。

---

## 8. Step 7：从「实例」到「训练样本」

到这里你有的是**任务实例**（环境 + 验证器），还不是训练样本。三条路：

### ① SFT：拒绝采样（rejection sampling / filtered BC）

```
用一个强模型（或当前策略）在实例上跑 N 次
  → 用 F2P/P2P 判定成功
  → 只保留成功轨迹
  → 在这些轨迹上做 NLL 微调
```

- **SWE-Gym**：2,438 个实例 → 微调 Qwen2.5-Coder-32B，
  SWE-bench Verified **+13.6%（到 20.6%）**、Lite **+12.3%（到 15.3%）**
- **SWE-smith**：5 万实例 → 用 Claude 3.7 Sonnet 采 **5,016 条专家轨迹**
  → SWE-agent-LM-32B **40.2% Pass@1**（无推理时扩展），开源模型 SOTA
- **轨迹数的 scaling 很干净**：100 → 5,000 条轨迹，
  resolve rate **14.3% → 27.8% → 33.4% → 40.2%**

### ② RL：把实例当环境

reward = F2P 全过 且 P2P 全过（二元）。
**这里可以直接套你 math RL 的全部经验**：组内归一化、难度筛选、
去掉 pass@k ∈ {0,1} 的组、Dr. GRPO 的 length/std normalization 修正。

**SWE 特有的两个麻烦**：
- **一次 rollout 要几十步工具调用**，比 math 慢两个数量级 → 异步 RL 几乎是必须的
- **奖励延迟到最后一步** → credit assignment 更难

### ③ 无执行：SWE-RL 的路子

> Meta 的 SWE-RL：过滤出约 **1,100 万个高质量 PR**，**完全不搭环境**。
> reward = `difflib.SequenceMatcher` 算的**生成 patch 与 gold patch 的相似度**，
> 连续值 0–1。Llama3-SWE-RL-70B 训了 1,600 步，batch 512，16k 上下文。

**这条路的取舍要说清楚**：
- ✅ 规模无上限，不用碰环境
- ❌ reward 是 **proxy**：功能等价但写法不同的正确补丁会被判低分
- 👉 适合**冷启动 / 大规模 SFT**，不适合当最终的 verifier

---

## 9. 完整 pipeline 与真实产出率

```
GH Archive / API
   ↓  仓库筛选（star / issue / license / 非 fork / 排 benchmark）
21,000 个仓库                                    ← 保留 20% 的仓库覆盖 80% 的任务
   ↓  挖 PR + issue 链接 + 劈 patch
580,000 个候选实例
   ↓  便宜的启发式过滤（无测试 / 过大 / 只改文档）
   ↓  【最贵】环境搭建（agent 闭环，每仓一次）
   ↓  执行验证（三步 + 跑 3 次去 flaky）
   ↓  issue 清晰度过滤（3 个 LLM judge 全票才留）
32,000 个可执行任务 / 3,617 个仓库 / 20 种语言     ← SWE-rebench V2 的最终产出
```

**从 58 万到 3.2 万，产出率约 5.5%。** 这个数字值得记住 ——
**SWE 数据 pipeline 的产出率就是这个量级**，别按 math 的直觉去估算。

### 一个容易忽略的质量闸门

> SWE-rebench V2 用 **3 个独立 LLM judge**（gpt-oss-120b、GLM-4.7、DeepSeek-V3.2）
> 给 issue 的「规格是否足够实现」打分，**三个都说够才留**。
> 这个 rubric 是从 **SWE-bench Verified 的人工标注规范**改写来的，
> 并且**用人工标注校准过**。

这条直接对应你在 Anthropic take-home 里做的事：**judge 要拿人工标注校准**。

---

## 10. 十个我会写进 checklist 的坑

| # | 坑 | 后果 |
|---|---|---|
| 1 | gold patch 里混进测试文件 | **答案泄漏**，模型直接看到断言 |
| 2 | 「是不是测试文件」用无锚定正则 | `contest.py` 被误判 → solution patch 变空 → 实例静默丢弃 |
| 3 | 用 **PR 描述**当 problem_statement | PR 描述常常**已经写了解法** —— 要用 issue 正文；用不了要打标记 |
| 4 | 不跑 3 次去 flaky | 持续向 reward 注入噪声 |
| 5 | 只用 F2P 不用 P2P | 模型学会删代码 |
| 6 | 只排除 benchmark 的实例，不排除**整个仓库** | 代码库结构和风格泄漏 |
| 7 | 两个数据源 schema 不一致 | **下游过滤静默失效**（我这次就踩了） |
| 8 | 用 patch 行数当难度 | 和真实难度相关性弱；要用 pass@k |
| 9 | 每个实例存一个镜像 | 存储 TB 级；应该按仓库复用 |
| 10 | 训练集时间窗口晚于评测集 | 时间穿越污染 |

---

## 11. 和 math/STEM 的对照：什么能迁移，什么不能

### ✅ 直接迁移

- **难度筛选**：pass@k ∈ {0,1} 的题没有梯度 —— 完全一样
- **去重 / 去污染**：MinHash + LSH，只是归一化函数换成 patch 归一化
- **配比与课程**：按难度桶采样
- **judge 要用人工标注校准**
- **对照组纪律**：任何「数据改进」都要有 count-matched 的对照

### ❌ 不能迁移，要重新学

- **环境即数据**。math 的样本是一段文本，SWE 的样本是**一个可复现的容器**。
  你的存储、缓存、调度设计全都不一样。
- **验证是慢的、有状态的**。math 可以在数据生成时就验证完；
  SWE 的验证要排队、要隔离、要防 flaky，**它本身就是一个分布式系统问题**。
- **产出率低一个数量级**。58 万 → 3.2 万。
- **轨迹是多步的**。你造的不是 `(prompt, answer)`，是 `(环境, 工具协议, 终局判据)`。

### 一句可以在面试里说的话

> 「math 数据里验证器是廉价的后处理；SWE 数据里**验证器本身就是产品**。
> 我做 math curation 时最贵的是找题和去重，
> 做 SWE 数据时最贵的是**让测试能在正确的历史时点上跑起来** ——
> SWE-rebench V2 的漏斗是 58 万候选到 3.2 万可执行，产出率 5.5%，
> 几乎所有损耗都在环境和执行这两步。」

---

## 12. 配套代码

```bash
cd labs/swe_data
V=/Users/mingrui/Documents/codes/interview/.venv/bin/python
$V toyrepo.py     # 造一个带真实 git 历史的玩具仓库（9 个 commit）
$V github.py      # 仓库筛选打分 + issue 链接解析（离线；--live 需 token）
$V mine.py        # 挖候选 + **真跑 pytest** 做三步 F2P/P2P 验证
$V synth.py       # SWE-smith 式 AST 造 bug + 执行验证
$V curate.py      # 去重 / 去污染 / 难度分层
$V -m pytest test_swe_data.py -q     # 26 passed
```

只依赖 pytest，无网络、无 Docker、无 API key。**F2P/P2P 是真跑出来的，不是模拟的。**

---

## 13. 论文与代码清单（按阅读价值排序）

| 工作 | 一句话 | 链接 |
|---|---|---|
| **SWE-bench** | 定义了 F2P/P2P 三步验证。**先读这个** | [swebench.com](https://www.swebench.com/original.html) · [harness 文档](https://www.swebench.com/SWE-bench/reference/harness/) |
| **SWE-smith** | 环境优先 + 四种造 bug 策略。128 仓库 5 万实例，$1,360 | [arXiv 2504.21798](https://arxiv.org/abs/2504.21798) · [swesmith.com](https://swesmith.com) |
| **SWE-rebench V2** | 语言无关的自动化漏斗，20 语言 3.2 万任务。**工程细节最全** | [arXiv 2602.23866](https://arxiv.org/abs/2602.23866) · [HF: nebius/SWE-rebench-V2](https://huggingface.co/datasets/nebius/SWE-rebench-V2) |
| **SWE-Gym** | 第一个训练用环境，2,438 实例 + 拒绝采样 + verifier | [arXiv 2412.21139](https://arxiv.org/abs/2412.21139) · [GitHub](https://github.com/SWE-Gym/SWE-Gym) |
| **R2E-Gym / SWE-GEN** | 从 commit 回译，**不依赖 PR 和人写的测试** | [GitHub](https://github.com/R2E-Gym/R2E-Gym) |
| **SWE-RL** | 1,100 万 PR，**不搭环境**，用 patch 相似度当 reward | [arXiv 2502.18449](https://arxiv.org/abs/2502.18449) |
| **DeepSWE** | 全开源 RL 训练配方 | [together.ai/blog/deepswe](https://www.together.ai/blog/deepswe) |
| SWE-bench Verified | OpenAI 人工核验的 500 题子集 + **标注 rubric** | — |
| SWE-Factory / SWE-Bench++ / DockSmith | 自动化环境构建的不同流派 | — |

**读的顺序建议**：SWE-bench（定义）→ SWE-smith（规模怎么来的）→
SWE-rebench V2（工程细节）→ SWE-RL（另一条路的取舍）。

---

## 14. 相关材料

- [`labs/swe_data/`](labs/swe_data/) —— 本文的可跑代码
- [`04_case_code_review_llm.md`](04_case_code_review_llm.md) —— code review LLM 的数据轴
- [`16_case_rl_data_pipeline.md`](16_case_rl_data_pipeline.md) —— RL 数据流水线通论（难度筛选、可验证性、reward hacking 检测）
- [`19_case_agent_benchmark.md`](19_case_agent_benchmark.md) —— agent benchmark 的过程 vs 结果、pass^k、污染与漂移
