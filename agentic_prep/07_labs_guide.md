# 07 · Labs 使用指南（v1 labs 原地不动，本文件只管怎么用）

⏱ 约4分钟读完 ｜ 面试前只看 ⭐⭐⭐ 部分

Labs 本体在 [`../agentic/labs/`](../agentic/labs/)，starter/solution/test 都齐。本指南定：哪个 lab 对哪场面试、什么时候做、限时多少、盲写还是读答案。

## ⭐⭐⭐ 总表：对口面试与做法

| Lab | 绝对路径 | 对口面试 / 建议日期 | 限时 | 做法 | 跑测试 |
|---|---|---|---|---|---|
| [01 raw tool agent](../agentic/labs/01_raw_tool_agent/README.md) | `/Users/mingrui/Documents/codes/interview/my_interview_prep/agentic/labs/01_raw_tool_agent` | Anthropic，**7/19 闭卷重写主循环** | 60–75 min | 盲写 `starter.py` → 对照 `solution.py`；7/19 那次不看任何参考 | `python3 -m unittest -v test_solution.py` |
| [02 codex repo review](../agentic/labs/02_codex_repo_review/README.md) | `/Users/mingrui/Documents/codes/interview/my_interview_prep/agentic/labs/02_codex_repo_review` | Sierra 对口（cross-cutting PR），**7/14 晚** | 60 min | 直接修 `starter/support_agent`，全程用 AI 辅助；结束才看 `solution/` | `TARGET=starter python3 test_solution.py -v`（修完应全绿；参考实现用 `python3 test_solution.py -v`） |
| [03 durable harness](../agentic/labs/03_durable_harness/README.md) | `/Users/mingrui/Documents/codes/interview/my_interview_prep/agentic/labs/03_durable_harness` | durable 家族 + Anthropic，**7/20** | 90–120 min（缩减版 60） | 先读 `solution.py` 吃透 crash window 与状态机，隔天盲写 start/poll/crash-replay 核心路径 | `python3 -m unittest -v test_solution.py` |
| [04 multi agent memory](../agentic/labs/04_multi_agent_memory/README.md) | `/Users/mingrui/Documents/codes/interview/my_interview_prep/agentic/labs/04_multi_agent_memory` | Humans& 对口（group memory / shared workspace），**7/16 晚** | 60 min | 盲写 `starter.py`（保留公开签名）→ 对照 `reference_solution.py` | `python3 test_solution.py -v` |
| [05 eval harness](../agentic/labs/05_eval_harness/README.md) | `/Users/mingrui/Documents/codes/interview/my_interview_prep/agentic/labs/05_eval_harness` | Applied Compute / eval 方向，**有空才做** | 60 min（只读 30） | 时间紧就直接读 `reference_solution.py`，重点 grader 分层与指标口径 | `python3 test_solution.py -v` |

优先级 = 日期序：02（今晚）→ 04 → 01 → 03 → 05。03 依赖 01 的 loop 心智模型，别倒序。

> 高分句：我不背 lab 答案，我练的是限时内把 crash window、idempotency key、authority boundary 讲清楚并有测试证明。

## ⭐⭐⭐ 一题三练（来自 [QUESTION_GUIDE](../agentic/content/QUESTION_GUIDE.md)）

每个 lab 不是做一遍，是三种形态各过一遍：

1. **白板版**：不写代码，20 min 讲 requirements / API / main flow / failure / eval。
2. **coding 版**：只实现最危险的 state transition 或 tool runtime，fake clients 打桩（labs 的 starter 就是这一版）。
3. **review 版**：让 AI 生成一个有缺陷的实现，你限时找 authority、idempotency、recovery、eval 四类漏洞（Lab 02 天然就是 review 版）。

自评硬规则：每个分数必须配一句**证据句**（"因为我展示了 X"），禁止裸打分。
例："可靠性 20/20：覆盖了 tool success 后 crash，用 operation key + status reconcile，且有测试"。
证据句写不出来 = 那项没掌握。分数目标沿用 QUESTION_GUIDE：一刷 60 / 二刷 75 / 面试前 85。

$\text{pass}^k$（k 个 trial 全部通过）衡量可靠性，$\text{pass@1}$ 衡量首发质量——自评也按这个口径：同一 lab 隔天盲写第二次仍达标才算 pass。

> 高分句：白板版练表达，coding 版练最危险的 20% 代码，review 版练的才是 interactive AI interview 本身。

## 统一校验

```bash
cd /Users/mingrui/Documents/codes/interview/my_interview_prep/agentic && python3 scripts/run_all_checks.py
```

每次改动 labs 或做完一轮练习后跑一次，确保 starter/solution/test 没被自己改坏。

<details><summary>各 lab 验收重点（面试官会追问的那一层）</summary>

| Lab | 必须能脱稿讲的点 |
|---|---|
| 01 | 同一 assistant 回合的并行 tool_result 放**同一条** user message；只读工具才并行；`max_steps`/`max_cost_usd` 是 runtime 强制，模型不能解除；Python thread 无法安全强杀 timeout |
| 02 | 修的 6 类 bug：只执行首个 tool call、exception 泄漏、高额退款绕审批、信任模型给的 `customer_id`、重复退款、max-step 边界；authority 来自 `Ticket.customer_id` 不是模型输入 |
| 03 | crash window：intent COMMIT → external.start → crash → UPDATE external_id；唯一解是 provider 侧 idempotency key 重放拿回同一 job；cancel 先写 generation+1 再 best-effort，靠 generation guard 拒 stale result |
| 04 | 为什么 worker 出 proposal、单一 verifier/reducer 提交，优于 worker 直写共享 DB；memory 写入门槛 = provenance + TTL + 置信度 + injection 过滤 |
| 05 | outcome grader 查环境状态而非 agent 自述；`pass^3` vs `pass@1` 的区别；商家备注是不可信数据，injection 指令不得执行 |

</details>

<details><summary>限时 hard stops（所有 lab 通用）</summary>

- 第 7 分钟：锁定 success criteria 与最大 risk，否则停下来重新 clarify。
- 剩 12 分钟：停止扩架构，转 failure handling / eval。
- 最后 4 分钟：总结 trade-offs 与 v2。
- Coding 第 40 分钟后冻结功能；没有测试的 feature 不算完成。

</details>

<details><summary>7/19 Anthropic 闭卷重写的具体规则</summary>

- 新建空目录，不开 Lab 01 任何文件，只允许查语言文档。
- 必须复现：text-only → 单工具 loop + fake model 测试 → 错误/未知工具/timeout → budget → 只读并行 → `resume()`。
- 结束后 diff 对照 `solution.py`，漏掉的行为写进证据句清单；漏 2 项以上则 7/21 再闭卷一次。
- 口述收尾固定五件套：schema validation、幂等键、human approval、trace、sandbox。

</details>
