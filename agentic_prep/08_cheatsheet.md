# 08 · 一页纸（面试前 15 分钟 / 7/21 闭卷默写靶子)

⏱ 8 分钟读完 ｜ 全文都是 ⭐⭐⭐

## 开场必问 4 件事

- [ ] 本轮时长？coding 还是 design 还是混合？
- [ ] 允许 AI 吗（哪种）？允许联网/查文档吗？
- [ ] 能粘贴题面给 AI 吗？
- [ ] 是新代码还是 existing codebase？验收标准是什么？

## 面试前 15 分钟节奏

0–2 确认形式与权限 → 2–6 背该公司五句+主练题 → 6–10 闭卷画 agent loop + state + tool policy → 10–13 准备一个失败恢复 + 一个 eval 回答 → 13–15 选好个人故事（见文末三件套）。

## Agent loop 五边界（默写）

1. `build_context` 只放当前任务需要的信息
2. `visible_tools` 已按身份/任务/风险过滤
3. `validate_calls` 不相信模型参数
4. `execute_with_policy` 处理并行/审批/timeout/retry/幂等
5. `deterministic_grader` 不接受模型口头宣告完成

## Claude tool-use 协议 7 步（默写）

发 message+schemas → assistant 返回 `tool_use` blocks → 完整 assistant content 进 history → 执行工具 → 下一条 user message 回**所有**匹配 `tool_use_id` 的 `tool_result` → 异常作为 error result 回传给模型观察 → 外层强制 max steps/deadline/cost。只读且独立才有界并行；写操作默认不并行。

## 状态机一行 + crash window 三步

`pending → running → waiting_tool/waiting_approval → running → succeeded`；非终态可 `failed`/`cancel_requested`（停完资源才是 `cancelled`）。

最坏窗口 = 外部工具成功、结果落库前崩溃：① 外部操作带稳定 `operation_key`（provider 幂等）② 恢复先查外部 status 再决定 retry ③ 查不了就标 `unknown` 人工 reconcile——不能假装 exactly-once。

## Failure taxonomy 七类（每类三词）

1. Specification：目标缺失/冲突 2. Model decision：错工具/参数/事实 3. Tool/runtime：timeout/429/partial 4. Coordination：重复/丢信息/冲突 5. Verification：grader 漏洞/自评 6. Security：注入/越权/泄密 7. Operations：crash/backlog/成本爆炸。
每个失败答四件事：**Detection → Containment → Recovery → Prevention**。

## Eval 四层 + pass 指标

Component（工具选择/参数/检索）→ Trajectory（违规/绕路/重复）→ Outcome（环境终态满足目标）→ System（成本/延迟/稳定/人工负担）。

$\text{pass@}k = 1-(1-p)^k$（有机会做到）；$\text{pass}^k = p^k$（稳定做到）。$p=0.8$ 时连续 4 次只有 $0.8^4 \approx 0.41$——生产 agent 要报一致性，不只报均值。

## Retry matrix 速查

| 情况 | 策略 |
|---|---|
| read + 429/5xx | 有界指数退避 + jitter |
| validation error | 不原样重试；把字段错误回传模型 |
| write + 有 idempotency key | 同 key 重试，先查 status 更稳 |
| write + 无幂等 | timeout 后标 unknown，不自动重复 |
| permission denied | 不重试；解释所需 authority |

## 高分句 Top 15（背）

1. 让模型提出下一步，让状态机决定这一步是否允许、如何执行、怎样证明成功。
2. 工具描述影响选择，但权限不在描述里——executor 再做 authn/authz/validation。
3. 先建可治理的 MemoryRecord，再选检索技术；相似度不是权限，也不是事实性。
4. 按可独立验证的 artifact 分工，而不是让多个 agent 重复思考再投票。
5. 恢复的是 durable state，不是把旧聊天原样塞回模型。
6. 最有价值的改进往往是给 agent 更好的环境和 verifier，而不是让它"再努力一次"。
7. 先问 eval 是否预测 production，而不是先优化 leaderboard。
8. "再问模型一次"不是完整的 recovery strategy。
9. 完成必须由可观察事实判定——模型无法可靠知道外部环境的真实状态。
10. Tool output 是不可信输入，不能修改 system policy。
11. Budget 是可靠性功能：耗尽时返回明确状态和已有 artifact，不伪装完成。
12. Conversation summary 不是 durable state。
13. 多 agent 失败大多来自 specification 和 verification，不是模型不够聪明。
14. Streaming 是 UX 合同：可恢复、可中断、partial result 带可信标注。
15. RAG 先定权限与新鲜度，再谈 chunking 与 rerank。

## 万能结尾 4 句（时间到了就用）

1. "v1 的完成条件是环境状态 X，验证由 Y 完成。"
2. "最大的风险是 Z，所以我把 authority 放在 deterministic policy/approval 层。"
3. "崩溃后从 checkpoint/event 恢复，对外部副作用按 operation key 查询状态。"
4. "上线走 offline held-out → shadow → canary；同时看 outcome、policy、cost、latency。"

## 个人故事三件套（面试前填好、每个 90 秒版本）

| 钩子 | 我的素材（Reflection.ai / 研究经历） | 要落的点 |
|---|---|---|
| 我如何 scope 一个模糊任务 | ___（例：agent infra 里某次砍范围的决策） | 定义 done、砍非目标、验收 |
| 我如何发现 AI 的错误并纠正 | ___（例：post-training/eval 中抓到的一次模型错误） | 证据、最小复现、修 harness 不修 prompt |
| 一次失败→变成 eval/防线 | ___（例：reward hacking 或生产事故转 regression） | 事故→可复现 eval→上线 gate |
