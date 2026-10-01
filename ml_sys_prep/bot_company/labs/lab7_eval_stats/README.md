# lab7_eval_stats — robot policy 评估统计迷你库

## 对应什么考点

CTO 点名 **evals**。这个 lab 把 `../../06_system_design_playbooks.md` C 题（eval
pipeline）和 `../../07_question_bank.md` Q36/Q37 里的口头论点全部落成可跑、可测的
代码——面试里每一个统计数字你都能说"我实现并验证过这个公式"：

- **wilson_ci** — 小样本真机 eval 的置信区间（50 trials @ 90% ≈ ±8pp 那张 CI 直觉表）；
- **trials_needed** — 两比例 z 检验（pooled 正态近似）的每组样本量：80%→85% 要
  **~905/组**、50%→55% 要 **~1,565/组**——"5pp 差异物理上不可能靠真机检出、sim 承担
  统计功效"的杀手数字来源；
- **paired_compare + paired_trials_needed** — 同一批任务上 A/B 配对（McNemar 精确 +
  连续性校正近似检验）；rho=0.6 时配对设计只要 **371 对任务**（742 次真机 run）对比
  独立分组 906/组（1,812 次 run），**省 ~2.4x**；
- **bootstrap_diff_ci** — 不依赖正态假设的差值 CI；同一份数据，尊重配对结构的
  bootstrap CI（±3.4pp）明显窄于当独立样本处理（±5.4pp）；
- **peeking_inflation_sim** — sequential testing 的坑：每 50 个 trial 偷看一次 z 检验、
  "显著就停"，α 从名义 5% 膨胀到 **~23%**（20 次 look，x4.6）——为什么必须预注册 n
  或用 alpha-spending（Pocock / O'Brien-Fleming）。

## 与备考文档的口径对照（必读，防止面试报数打架）

文档（00/06/07）引用 **905**；本实现 `trials_needed(0.80, 0.05)` 输出
`n_exact = 905.4`、`n_per_arm = ceil = 906`。两者是同一个 pooled 公式：

```
n = [ z_{1-α/2}·√(2·p̄·(1-p̄)) + z_{power}·√(p0·q0 + p1·q1) ]² / δ²,  p̄=(p0+p1)/2
```

文档的 905 是**未取整的公式值四舍五入**（905.4 → 905）；工程上排期要向上取整到
906。同理 90%→95%：文档 434 = round(434.4)，排期 435；50%→55% 的 1,565 两边一致。
（另一常见教材公式用非 pooled 方差，80%→85% 给 ~903——如果面试官算出 903 不要慌，
是方差估计口径不同，量级完全一致。）口头引用统一说 **"~905 per arm"**，并且**必须
带基线**（80%→85%；50%→55% 是 ~1,565）。

## 15–30 分钟熟悉路径（先跑什么再读什么）

解释器固定用 `/Users/mingrui/Documents/codes/interview/.venv/bin/python`
（Python 3.9.6，numpy 2.0.2；只用 numpy + 标准库，无 scipy、无 pandas、无网络）。

```bash
cd /Users/mingrui/Documents/codes/interview/my_interview_prep/ml_sys_prep/bot_company/labs/lab7_eval_stats
PY=/Users/mingrui/Documents/codes/interview/.venv/bin/python

# 1. (2 min) 跑主演示，五段输出对应五个函数；把 [2] 的样本量表抄到数字卡上
$PY evalstats.py

# 2. (2 min) 跑测试，全绿（<5 秒）；注意 test_simulated_paired_eval_end_to_end：
#    用 sizing 公式算出的 n_pairs 去仿真，实测 power ~0.78 ≈ 名义 0.8，
#    这是"公式和仿真互相验证"的完整闭环，面试可以直接讲
$PY test_evalstats.py

# 3. (10 min) 读 evalstats.py，顺序：trials_needed（背公式结构）→
#    paired_trials_needed（psi = 不一致对概率，rho 越高 psi 越小 → 越省）→
#    peeking_inflation_sim（向量化 cumsum + 每 50 个 trial 一次 z 检验）
# 4. (5 min) 改参数玩：把 rho 调到 0.8 看配对省多少；把 peek_every 调到 10
#    看 α 膨胀到多少；把 power 调到 0.9 看 905 变成多少（~1,212）
```

确定性：所有随机函数显式收 `seed`，重复运行输出逐位一致。全部测试 + 主演示 < 5 秒。

## 面试话术（每个函数一句英文）

- **wilson_ci**: "With 50 real-robot trials at 90% success, the Wilson interval is
  about ±8 points — so a 5-point improvement is invisible at that scale; I always
  report success rates with a CI, never a bare number."
- **trials_needed**: "Real-robot eval is expensive, so I size the eval with a power
  calculation first: detecting 80%→85% at α=0.05 and 80% power takes ~905 trials
  per arm — that's a week of robot time, which is why sim carries the statistical
  power and real robots do calibration and safety gating."
- **paired_compare**: "I run A and B on the same task list and use McNemar's test
  on the discordant pairs — pairing cancels shared task-difficulty variance, and
  at a within-task correlation of 0.6 it cuts the robot runs needed by ~2.4x."
- **bootstrap_diff_ci**: "When I don't trust the normal approximation — small n,
  clustered episodes — I bootstrap the difference, resampling tasks jointly so
  the pairing is respected."
- **peeking_inflation_sim**: "The classic eval bug is peeking: checking the test
  every 50 trials and stopping when it's significant inflates the false-positive
  rate from 5% to roughly 23%, so I pre-register the sample size or use
  alpha-spending corrections."

## 文件清单

| 文件 | 内容 |
|---|---|
| `evalstats.py` | 五个统计工具 + `simulate_paired_outcomes` 生成器 + `main()` 五段演示 |
| `test_evalstats.py` | plain-assert 测试，锁死 905/906、1565、434/435、371 对、~2.4x、α→~23% |
