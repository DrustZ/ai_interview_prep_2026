# Feedback Agent — 从人类反馈中学习的个人助理（最小可跑演示）

单文件 mock-LLM 助理，展示一个完整的 human-in-the-loop 学习闭环：人类纠正 → 蒸馏成规则（in-context 路径）+ 拟合微型 reward model（post-training 路径）→ 不确定时主动问人（mixed-initiative gate）。全部 stdlib + numpy，确定性，302 行，跑完 <1 秒。

## 一条命令怎么跑

```bash
cd ml_sys_prep/humansand/sample_code
/Users/mingrui/Documents/codes/interview/.venv/bin/python feedback_agent.py   # 演示 + 内置断言
/Users/mingrui/Documents/codes/interview/.venv/bin/python test_feedback_agent.py  # 4 组测试
```

现场跑出来的硬数字（seed=13，永远一样）：

| 指标 | 数值 |
|---|---|
| 反馈前 held-out preference match | **5.0%** |
| 收集 54 次纠正 → 162 个偏好对 | |
| 仅注入蒸馏规则（in-context） | **45.0%** |
| Reward model held-out 成对准确率 | **96.7%** |
| 规则 + RM rerank | **87.5%** |
| Gate 总成本 14 vs 全问 40 / 全不问 25（问了 4/40 次） | **省 44–65%** |

## 2 分钟英文讲法（逐句稿）

> **开场（10 秒）**
> "This is a ~300-line demo I can run right now — it's a minimal system embodying my thesis: human feedback is a training signal, and knowing WHEN to ask is an interaction design problem."

> **设置（20 秒）**
> "A mock personal assistant drafts emails and schedules meetings. Each draft has style features — formality, brevity, emoji use. The user has a hidden preference the agent doesn't know, so out of the box it matches what the user wants only 5% of the time. That's the 'one model, many users' personalization gap."

> **两条学习路径（40 秒）**
> "When the user corrects a draft, I use that signal twice. First, corrections get distilled into human-readable rules — 'avoid emoji', 'prefer brevity' — and injected into later decisions. That's the in-context path: instant, auditable, but coarse — it gets us to 45%. Second, the same corrections become preference pairs for a tiny Bradley-Terry reward model — hand-rolled logistic regression, no sklearn — which reranks candidates. That's the post-training path in miniature: it generalizes to 97% pairwise accuracy on held-out tasks and lifts end-to-end match to 87.5%. The two paths are complementary: the rules actually missed formality, but the reward model caught it."

> **Gate — HCI 的部分（35 秒）**
> "The part I care most about: the agent knows when NOT to act. When the reward model's margin between the top two candidates is low, it asks the human instead. I price the trade-off explicitly — an interruption costs 1, an uncaught error costs 5 — and calibrate the ask threshold on a separate calibration split, never on the test set. On held-out tasks the gate asks only 4 times out of 40 and beats both degenerate policies: cost 14 versus 40 for always-ask and 25 for never-ask. That's the mixed-initiative insight from HCI, quantified."

> **收尾（15 秒）**
> "Everything is deterministic, assertion-pinned, and tested — same discipline I used shipping eval infrastructure at Reflection. Scale the mock LLM to a real one and the reward model to a fine-tune, and this is the architecture I'd build for an assistant that actually learns its user."

## 三个可被追问的设计决策与英文答法

**1. 为什么同一份反馈要走两条路径（rules + reward model）？**
> "They fail differently. Rules are instant and auditable — the user can read 'avoid emoji' and veto it — but they're coarse, direction-only. The reward model generalizes and captures magnitude — it learned that emoji matters 2x more than formality — but it's opaque. In the demo you can see the complementarity: rules alone get 45%, adding the RM gets 87.5%, and the RM caught the formality preference the rules missed. In a production system, rules are also what you can apply at inference time today, while pairs accumulate into training data for the next post-training run. Same signal, two time horizons."

**2. Gate 的阈值怎么定的？为什么不用固定的置信度阈值？**
> "I tried the decision-theoretic threshold first — ask when expected error cost exceeds interruption cost, which gives tau = 1 − cost_ask/cost_error = 0.8. It lost to never-ask, because a freshly fit reward model's sigmoid confidence isn't calibrated. So I calibrate tau on a held-out calibration split of 20 tasks — never the test set. That's a general lesson: any ask-vs-act policy is only as good as its confidence calibration, and calibration is cheap to measure. Also, the costs themselves are the real product decision — interrupting a user in a group chat at 2am is not cost 1 — so I'd want them user- and context-dependent."

**3. Mock 环境会不会太简单，结论能迁移吗？**
> "The mock is deliberately the simplest environment where all three mechanisms are separable and measurable — that's an eval design choice, not a limitation I'm hiding. Linear features and a noise-free human mean I know ground truth, so I can pin every claim with an assertion. What transfers: the correction → pair → reward-model pipeline is exactly RLHF data collection; the gate logic is model-agnostic — it only needs a score margin; and the before/after evaluation discipline is the same one I used at Reflection and in my Anthropic take-home. What doesn't transfer: real preferences are noisy, contextual, and drift — that's why I'd add per-category rules, recency weighting, and periodic re-calibration before trusting it."

## 文件

- `feedback_agent.py` — 全部核心逻辑 + 演示主脚本（234 行）
- `test_feedback_agent.py` — 4 组 plain-assert 测试：反馈改变行为、RM 方向正确、gate 严格优于两个极端、逐字段确定性（68 行）
