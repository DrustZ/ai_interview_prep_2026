# EXERCISE — 「一批 bot 不 work 了」fleet 数据排查

> **规则：先自己挖，再对答案。**
> 只允许运行 `generate_logs.py` 和查看 `data/episodes.jsonl`。
> 在写出三问的结论之前，**不要**打开 `generate_logs.py` / `triage.py` / `test_triage.py` 的源码（生成器里写着答案）。

## 场景

你是 fleet learning 团队的 on-call。过去两周（2026-07-20 ~ 2026-08-02），客服端报告
"一批机器人任务成功率掉了"。你手上只有 5,000 条 episode 级 telemetry（JSONL），
每行字段：

```
robot_id, fw_version, model_version, task_type, home_id, floor_type, lighting,
battery_pct, cpu_temp, grip_current, policy_latency_ms, success, error_code, ts
```

生成数据：

```
/Users/mingrui/Documents/codes/interview/.venv/bin/python generate_logs.py
```

工具限制：numpy + 标准库（禁 pandas）。建议开一个 `python -i` 或写个 scratch 脚本。

## 三问（按 on-call 汇报的标准交付）

1. **哪个 cohort 回归了？** 精确到「维度组合 + 模型版本」，并给出证据链：
   该 cohort 掉到多少、对照组多少、以及为什么能排除"硬件/环境本来就差"。
2. **哪台机器人硬件坏了？** 给出 robot_id + 两条独立证据（行为指标 + 物理信号），
   并说明它为什么不是问题 1 的受害者。
3. **为什么某个 home_id 的"高失败率"是假信号？** 找到这个 home，解释相关从何而来，
   并演示一个"控制变量后差距消失"的计算。

交付标准：每问一段结论 + 支撑数字（cohort n 与成功率）。口头能在 5 分钟内讲完。

## 提示阶梯（卡住再看，逐级揭开）

<details><summary>L1 — 方法论（不剧透数据）</summary>

- 先算整体成功率，确认"真的掉了"；再按单维度切片（model/fw/task/floor/lighting/home）。
- 单维度看不出的，做两两交叉表（尤其 环境维度 x 环境维度，按 model_version 分开看）。
- "一台 vs 一批"分叉：per-robot 成功率排序 + z-score，找个体离群点。
- 时间维度：把可疑 cohort 的成功率按天画出来，对齐版本切换时间点（同一批机器人自己前后对比，最干净）。
- 相关 != 因果：发现某个 home 很差时，先问"它的 episode 分布和别人一样吗？"

</details>

<details><summary>L2 — 方向性提示（半剧透）</summary>

- 问 1：回归只发生在**两个环境维度同时满足**的交集上，且只在某个 model_version 上。单看任何一维都会被稀释。
- 问 2：看 pick/place 任务的 per-robot 成功率，再看 `grip_current` 随日期的**趋势**（对每台机器人拟合斜率）。
- 问 3：worst home 的 episode 在 `lighting`、`floor_type`、`model_version` 上的分布严重偏斜。把它的 episode 按 (model, floor, lighting) 分层，层内和全 fleet 比。

</details>

<details><summary>L3 — 验证方式（几乎是答案）</summary>

- 跑参考解法对答案：`/Users/mingrui/Documents/codes/interview/.venv/bin/python triage.py`
- 报告分 6 步：整体 → 单维切片 → v2.3/v2.4 分别的 floor x lighting 交叉表 →
  同批机器人 OTA 前后对比 → per-robot z-score + grip 斜率 → worst home 分层校正。
- 你的三问结论应与报告末尾的 `[verify]` 断言一致。

</details>

## 面试怎么讲这套流程（英文骨架）

"Aggregate first, then slice, then cross dimensions, then align with the rollout
timeline, then look for single-robot outliers, and only blame a dimension after
you've controlled for its confounders."
