# [C13] Sierra 试点：同事 draft PR + coding agents 改进 · 完整解答

⏱ 读完 10 min ｜ 彩排素材：v1 自拟场景（ticket priority 跨 API/DB/queue/UI）直接可用
题库原文：[../C_live_ai_coding.md#c13](../C_live_ai_coding.md#c13) ｜ v1 rubric：[../../../agentic/data/questions.json](../../../agentic/data/questions.json) → `q-sierra-cross-cutting-pr`
对照轮：[C9 禁 AI debugging](C9_debugging_round.md)（裸 debug）｜ 同 onsite：[C12 Plan→Build→Review](C12_plan_build_review.md)

## 题目还原：这题真正在考什么

Medium-sized codebase + "同事"的 draft PR（cross-cutting feature，跨 API/DB/queue/UI），任务原文："review and improve it——pulling down the code, inspecting the output, and iterating with coding agents"。
v1 rubric 练习场景：客服 **ticket priority** 功能，draft PR 埋了**回填遗漏、权限绕过、排序回归、脆弱测试**四类问题。评分：25% 仓库导航、25% 风险判断、25% 验证证据、15% AI 协作质量、10% 交付表达——**验证证据链与风险排序合占一半**，比修的数量重要。

## 开场澄清（4 问，来自 rubric）

1. "这个 feature 的**目标行为和 compatibility 要求**是什么？"——没有 spec 无法判断 PR 是 bug 还是设计
2. "允许修改 **migration** 吗？已有 rows 和 rollback 需要处理吗？"——回填（backfill）是 cross-cutting PR 最常见遗漏
3. "哪些**测试/命令是权威验收**？"——先建基线，避免把原有红测当自己弄坏的
4. "目标是**修到可合并**还是 review 报告为主？"——决定时间分配（本题：修到可合并 + 讲清没修的）

## 答案主线（60 分钟，rubric pacing）

| 时间 | 阶段 | 动作 |
|---|---|---|
| 0–7 | 读题+基线 | 澄清 4 问；`git log`/PR 描述；**跑全量测试记录基线**（哪些本来就红） |
| 7–14 | 地图 | agent 生成 codebase map + diff 触点分析（prompt 见下）；自己画跨层数据流 |
| 14–38 | 按风险修 | correctness > security > data migration > operability > style；每个：先补复现测试 → 最小修复 → 回归 |
| 38–48 | 边缘+migration | 回填已有 rows、rollback、并发写入窗口 |
| 48–55 | 回归+diff review | 全量测试 vs 基线；逐 hunk review 自己+agent 的 diff |
| 55–60 | 交付 | demo 行为、修复清单、**没修清单+理由**、residual risks |

### 第一步：两条侦察 prompt（照抄，与 playbook 第八节同构）

> ① 只读探索，不修改文件。给我：(a) 仓库结构与各模块职责；(b) 这个 diff 触碰的所有文件及每处改动意图；(c) diff 改动的函数还有哪些**未被 diff 修改的调用点**；(d) 测试命令。每个结论引用文件与 symbol，列出你不确定的。

> ② 针对 ticket priority 这个 feature，沿 API → DB → queue → UI 追一遍数据流：priority 字段在每层怎么写入、读取、排序。指出各层语义不一致的地方。

Agent 输出必须抽查验证——挑 2 个关键结论亲自打开文件确认，narration："它说 X，我验证了，属实。"这是 25% 仓库导航 + 15% AI 协作分的动作。

### 第二步：cross-cutting PR review 清单（按风险序，对应四个埋点）

1. **一致性/排序回归（correctness）**：priority 在各层语义是否对齐？——API 收 `"high"/"low"` 字符串、DB 存 int、queue 比较时字符串序 `"high" < "low"` 反了？UI 排序和后端排序规则是否一致？**识别法**：让 agent 列出所有对 priority 做比较/排序的位置，逐个核对比较方向和类型
2. **权限绕过（security）**：新加的 API 路径/字段是否绕过了既有 auth middleware？典型埋法：新 endpoint 忘挂权限装饰器、或 mass-assignment 让普通用户能直接设 priority。**识别法**：diff 里每个新入口对照老入口的 auth 链
3. **回填遗漏（data migration）**：migration 只加列没回填——已有 rows 的 priority 是 NULL，排序/过滤逻辑遇 NULL 崩或静默排最后。**识别法**：看 migration 文件有无 backfill/default；问已有数据量与 rollback 要求
4. **遗漏调用点**：改了函数签名/语义但只更新了部分 caller（queue consumer 还在按旧格式解析）。**识别法**：侦察 prompt ①(c) 的输出
5. **脆弱测试（test quality）**：断言写死实现细节（mock 内部调用序）、或断言本身锁了错误行为（测试期望错误的排序）。**识别法**：读测试断言问"它锁的是行为还是实现？行为对吗？"

### 第三步：每个修复的标准动作（验证证据链，25% 分）

```text
复现：先写一个会红的测试暴露 bug（如：已有 row priority=NULL 时列表接口 500）
修复：让 agent 做窄修改（"只改 X 函数的 NULL 处理，不动其他"）或自己改
验证：新测试变绿 + 全量测试对照基线无新红
记录：一行进修复清单（症状 → 根因 → 修法 → 证据）
```

权限绕过必须**自己修**并亲自验证（curl/测试模拟无权限用户）——安全修复不能只信 agent 的"已修复"。

### 交付话术（最后 5 分钟）

> 修了 4 处：排序比较方向（证据：test_priority_order）、endpoint 补 auth（证据：403 测试）、migration 补 backfill + 读路径 NULL 容错（双保险）、脆弱测试改为断言行为。没修 2 处：UI 的 optimistic update 竞态——低频且需要前端重构，建了 issue；queue 的重复消费幂等——超出本 PR scope。残余风险：backfill 在大表上要分批跑，生产前需 migration canary。

## 深挖 2-3 处（rubric follow-up）

**「AI 建议重写整个模块时你怎么判断？」**
"默认拒绝。三步：(1) 问它重写解决什么具体问题——能否用小 diff 达成同效？多数时候可以；(2) 本轮目标是可合并的 PR，大重写让 review 面爆炸、回归风险不可控，与'improve the PR'目标冲突；(3) 如果模块确实烂，我在交付时把重写列为 follow-up issue 并给理由。例外：模块小（<200 行）、有完整测试覆盖、且重写是修复的最短路径——那我会先确认测试锁住行为再让它重写。"

**「哪些问题你选择不修、为什么？」**
框架："不影响本 feature 正确性/安全 + 修复面大于收益 = 不修但记录。"具体三类：风格与命名（留给 lint）、PR 之前就存在的历史问题（单开 issue，混进来会污染 diff）、需要产品决策的行为问题（如 NULL priority 该排最前还是最后——我实现了一个并标注了假设）。**必须展示"不修清单"**——rubric 里交付表达 10% 主要看这个。

**「如何让未来 agents 更容易理解这个域？」**
"三件事：(1) 把这次人肉发现的跨层数据流写成 `docs/priority-dataflow.md`——agent 侦察时最先缺的就是这个；(2) 各层共享的语义（priority 枚举与排序规则）收敛到单一定义处，消除隐式约定；(3) 补一个跨层 e2e 测试作为可执行 spec——对 agent 来说，能跑的 verifier 比文档更硬。呼应 [../../01_core/03_harness_env_swe.md](../../01_core/03_harness_env_swe.md)：最有价值的改进是给 agent 更好的环境和 verifier。"

## 失败模式与恢复（现场）

- **测试基线本来就红**：立即报告并记录，"我以此为基线，只保证不新增红"——别浪费时间修历史红测
- **agent 的 map 有幻觉**（指向不存在的文件/函数）：降级用法——让它只做单文件解释，导航自己用 grep 做；口头说明降级原因（AI 协作分看的是甄别，不是依赖）
- **时间不够修完四类**：按风险序保 correctness + security 两类，migration 讲方案不实施——风险排序正确 > 修复数量
- **修复引入新红测**：先回滚该 diff 再重来，不带着两个未知同时 debug

## Trade-offs 三条（主动说）

1. **先补测试再修 vs 直接修**：多花 5 分钟/bug，换来"修复有证据 + 防复发"——本轮 25% 分在证据链，值得
2. **最小 diff vs 顺手重构**：可合并性优先；重构欲望全部转成 follow-up issue 列表，展示看得见但不失焦
3. **agent 全自动修 vs 人做安全修复**：低风险修复交 agent 提速，权限类自己动手——按风险分配自主权，正是 Sierra 想看的 agent 协作观

## 现实参照

- Sierra 官方博客 "The AI-native interview"（题库 [C13] 与 v1 rubric 的来源）：官方原话 "pulling down the code, inspecting the output, and iterating with coding agents"；本轮与禁 AI 的 [C9](C9_debugging_round.md) 构成"裸 debug vs 带 agent debug"双面验证
- 侦察→计划→窄任务→验证的驾驶模板：[../../02_playbook.md](../../02_playbook.md) 第八节；coding agent harness 的环境/verifier 视角：[../../01_core/03_harness_env_swe.md](../../01_core/03_harness_env_swe.md)
