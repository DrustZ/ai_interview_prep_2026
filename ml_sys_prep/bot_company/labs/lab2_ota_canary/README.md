# lab2_ota_canary — 模型 OTA 金丝雀发布与自动回滚

对应考点：`bot_company/06_system_design_playbooks.md` 的 **Playbook B**（Robot Policy
Post-Training Pipeline：数据 → 训练 → 部署 → 回滚）。那道题的分数集中在部署侧
（registry 状态机、金丝雀放量、统计闸门、自动回滚），这个 lab 就是把 B 题架构图里
`Model Registry → 金丝雀 → 监控 → 回滚` 那一段真的写出来、跑起来。

面试里画完架构图后可以说这句：

> **"I've actually implemented this gate logic — a staged registry state machine plus a
> two-proportion z-test gate with Wilson intervals, and a simulated 10k-robot fleet where a
> cohort-masked regression gets shipped by the aggregate gate but caught by the per-cohort
> gate."**

## 文件

| 文件 | 内容 |
|---|---|
| `registry.py` | 极简 model registry：JSONL 事件日志持久化（append-only，重放重建状态 = 审计日志）；记录 lineage（train manifest id + 父版本）；状态机 `staged → canary_1pct → canary_10pct → fleet`，canary/fleet 可 `→ rolled_back`；非法转移一律 raise `IllegalTransitionError` |
| `gate.py` | 统计放行闸门：两比例 z 检验（显著更差 → ROLLBACK）+ Wilson 下界非劣性判据（→ PROMOTE），其余 HOLD；**样本量不足时强制 HOLD 而不是瞎判**；fleet 级决策 = 各 cohort 里最坏的那个 |
| `rollout.py` | 1 万台 fleet 模拟器 + rollout 控制器：按天累积观测、逐级放量、观察期用尽 fail-closed 回滚；内置三个场景（见下） |
| `test_ota.py` | 11 个测试，plain assert，无 pytest |

三个场景（固定种子，完全确定）：

1. **好模型**（真实 +3pp）：1% → 10% → fleet 逐级晋升；第 1 天 carpet 只有 100 条样本，闸门先 HOLD（演示"样本不足不判"）。
2. **坏模型**（carpet cohort −15pp，整体只 −4pp）：在 **1% canary 第 2 天**被 z 检验拦下自动回滚——blast radius 停在 100 台。
3. **整体持平但分 cohort 回归**（hardwood +2.7pp、carpet −8pp，加权 ≈ 0）：同一份数据，**聚合闸门会 PROMOTE**，分 cohort 闸门 ROLLBACK。这就是闸门必须分 cohort 看的理由（Simpson 式掩盖），对应 B 题"主指标 + 分层护栏指标"的讲法。

## 15–30 分钟熟悉路径

1. **先跑**（约 2 分钟）：
   ```bash
   /usr/bin/python3 rollout.py     # 看三个场景的完整决策转录
   /usr/bin/python3 test_ota.py    # 11/11 PASS
   ```
   重点盯 rollout.py 输出里三处：好模型 day 1 的 `insufficient samples` HOLD；
   坏模型 day 2 的 `z=-3.80 <= -1.96` 自动回滚；场景 3 同一份数据两种闸门结论相反。
2. **再读 `gate.py`**（约 10 分钟，面试最可能被追问的文件）：
   记住决策顺序四步——样本不足 HOLD → z ≤ −1.96 ROLLBACK → (z ≥ +1.96 或 Wilson
   下界 ≥ control − 3pp 非劣) PROMOTE → 否则 HOLD；以及为什么用 Wilson 不用 Wald
   （小样本、rate 贴近 0/1 时 Wald 区间会塌掉，年轻 canary 恰好就在这个 regime）。
3. **然后读 `registry.py`**（约 5 分钟）：event-sourced JSONL（日志即审计轨迹）、
   promote 只走一步、rolled_back 是终态（坏版本不复活，重训重注册）、rollback 强制
   带 reason。
4. **最后扫 `rollout.py`**（约 5 分钟）：控制器的 fail-closed（观察期用尽 = 回滚而
   不是继续挂着）；`demo_cohort_masking` 怎么用 `merge_cohorts` 现场对比两种闸门。

## 面试话术锚点（对着 B 题深挖组件 2 讲）

- 分桶单位是 household 不是 request（本 lab 简化为 robot，口头点出来）；
- 1% canary = 100 台 → 样本天然稀缺 → min-sample HOLD 是一等公民，不是边角处理；
  真实系统还会加 shadow mode 来补小样本的坑；
- 主指标干预率比成功率更灵敏（本 lab 用成功率是为了让 z 检验直观，口头说明替换）；
- 聚合指标掩盖 cohort 回归 → 分层闸门 + fleet 决策取最坏；多 cohort 带来多重比较，
  可提 Bonferroni / 分层 alpha 作为 follow-up；
- 回滚执行端靠设备 A/B 双分区秒级切换，registry 只负责记录真相和挡住非法转移。

## 约束与运行环境

- 解释器固定 `/usr/bin/python3`（Python 3.9.6），纯标准库（math/random/json/dataclasses），
  无 pandas、无网络、无新依赖；固定种子，全套测试 + 主脚本 < 1 秒。
