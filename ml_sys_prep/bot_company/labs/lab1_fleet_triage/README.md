# lab1_fleet_triage — 「一批 bot 不 work 了」fleet 数据排查实战

## 对应什么考点

The Bot Company 面试点名的 **debug + 数据分析题**（见 `../../05_debug_playbook.md` 的
cohort 决策表、`../../02_interview_rounds_intel.md` 的 practical 情景 B）。典型题面：
"10k 台家用机器人，客服报告一批 bot 成功率掉了，你怎么查？"这个 lab 把那道口头题
变成了可以真手跑的数据：5,000 条 episode telemetry 里埋了三个分层 root cause——

- **(a) OOD cohort 回归**：model v2.4 只在 `carpet x dim` 交集上大跌（OTA 引入的分布外回归）；
- **(b) 单机硬件故障**：一台机器人 `grip_current` 逐日漂移，pick/place 连续失败；
- **(c) 红鲱鱼**：一个 home 集中在晚上（dim）+ 满屋地毯 + 早升级，raw 成功率最差，
  但控制变量后差距消失——练"相关 != 因果"的标准反驳。

练的正是面试官要看的完整链路：**整体 → 切片 → 交叉 → 对齐 OTA 时间线 → 个体
z-score → 控制混淆变量**，以及"一台坏 vs 一批坏"的分叉判断。

## 15–30 分钟熟悉路径（先跑什么再读什么）

解释器固定用 `/Users/mingrui/Documents/codes/interview/.venv/bin/python`
（Python 3.9.6，numpy 2.0.2；本 lab 只用 numpy + 标准库，无 pandas、无网络）。

```bash
cd /Users/mingrui/Documents/codes/interview/my_interview_prep/ml_sys_prep/bot_company/labs/lab1_fleet_triage
PY=/Users/mingrui/Documents/codes/interview/.venv/bin/python

# 1. (1 min) 生成数据
$PY generate_logs.py

# 2. (10-15 min) 打开 EXERCISE.md，按三问自己挖（别看任何 .py 源码，生成器里有答案）
#    建议开 $PY -i，用 json + collections.Counter 徒手切片

# 3. (2 min) 跑参考解法对答案，读六步报告 + 末尾 [verify]
$PY triage.py

# 4. (5-10 min) 读 triage.py：六个分析函数就是可复用的面试口头模板
#    (slice_by / crosstab / before_after_upgrade / robot_success_zscores /
#     grip_current_slopes / raw_and_adjusted_gap)

# 5. (1 min) 全绿确认
$PY test_triage.py
```

测试命令（plain assert，无 pytest，全程 < 60 秒）：

```bash
/Users/mingrui/Documents/codes/interview/.venv/bin/python test_triage.py
```

## 文件说明

| 文件 | 作用 |
|---|---|
| `generate_logs.py` | 确定性 telemetry 模拟器（固定种子，同 seed 字节级一致）；**含答案，先别读** |
| `data/episodes.jsonl` | 5,000 条 episode（200 台机器人 x 25 条，14 天窗口） |
| `EXERCISE.md` | 任务书：三问 + L1/L2/L3 提示阶梯 |
| `triage.py` | 参考解法 = 可复用 cohort 分析工具，结论用 assert 钉死 |
| `test_triage.py` | 测试：确定性、schema、a/b 可检出、红鲱鱼被排除、端到端 |

## 面试中怎么引用这段经验（英文一句话）

> "To pressure-test my fleet-debug workflow I built a synthetic triage drill:
> 5,000 episodes with a planted OOD regression (v2.4 only fails on carpet in
> dim light), one robot with drifting grip current, and a confounded
> 'bad home' red herring — and my cohort-analysis script isolates all three:
> aggregate first, slice, cross dimensions, align with the OTA timeline,
> z-score individual robots, and stratify before blaming a correlated
> dimension."
