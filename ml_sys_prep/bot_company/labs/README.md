# labs 总索引 — The Bot Company 可跑实战演习（7 个）

> 环境统一：`PY=/Users/mingrui/Documents/codes/interview/.venv/bin/python`（Python 3.9.6；
> numpy 2.0.2；torch 2.8.0 仅 lab5/lab6 用）。全部纯本地、零网络、无 pandas、固定种子
> 确定性；**每个 lab 全套命令 < 60 秒**（lab2/3/4/7 秒级，lab5/6 约 30–45 秒）。
> lab2/3/4 是纯标准库，用 `/usr/bin/python3` 跑也一样（同为 3.9.6）。
> 各 lab 细节（熟悉路径 / 面试话术 / 追问预演）看各自目录下的 README.md。

## 索引

| lab | 对应考点 | 优先级 | 预计熟悉时长 | 一键命令（先 `PY=/Users/mingrui/Documents/codes/interview/.venv/bin/python`） |
|---|---|---|---|---|
| [lab6_buggy_training](lab6_buggy_training/) | **实战 ML debug 轮**：5 个植入 bug 的 BC 训练脚本，从症状到修复（05 的肌肉记忆版） | **P0** | 30–40 min（含盲修计时） | `cd lab6_buggy_training && $PY buggy_train.py && $PY fixed_train.py && $PY test_fixed.py` |
| [lab5_bc_policy](lab5_bc_policy/) | **现场写 BC 训练闭环** + 多模态演示 MSE mode-averaging vs 离散化动作头（03 的核心实验） | **P0** | 30–40 min（含 skeleton 冷写） | `cd lab5_bc_policy && $PY test_env.py && $PY train_bc.py && $PY test_train_bc.py && $PY test_skeleton_ref.py` |
| [lab1_fleet_triage](lab1_fleet_triage/) | **「一批 bot 不 work 了」数据排查**：切片→交叉→OTA 时间线→z-score→控混淆（05 cohort 决策表） | **P1** | 20–30 min | `cd lab1_fleet_triage && $PY generate_logs.py && $PY triage.py && $PY test_triage.py` |
| [lab7_eval_stats](lab7_eval_stats/) | **eval 统计**：Wilson CI / 905 trials / McNemar 配对省 2.4x / peeking α 膨胀（06C + Q36/37 的数字来源） | **P1** | 15–20 min | `cd lab7_eval_stats && $PY evalstats.py && $PY test_evalstats.py` |
| [lab2_ota_canary](lab2_ota_canary/) | **OTA 金丝雀 + 自动回滚**：registry 状态机 + z 检验/Wilson 闸门 + 分 cohort 防 Simpson 掩盖（06B 部署侧） | P2（以读代练） | 15–25 min | `cd lab2_ota_canary && $PY rollout.py && $PY test_ota.py` |
| [lab3_data_engine](lab3_data_engine/) | **teleop 数据摄入/管护 pipeline**：quarantine→去重→质量分→分层配比 + 内容寻址 manifest（04 数据引擎） | P2（以读代练） | 20–30 min | `cd lab3_data_engine && $PY generate_demos.py --batch 1 && $PY generate_demos.py --batch 2 --cross-dup-from data/demos_batch1.jsonl && $PY manifest.py && $PY test_pipeline.py` |
| [lab4_edge_uploader](lab4_edge_uploader/) | **边缘上传队列**：优先级/配额/断点续传/退避/aging/丢弃策略，metadata 先行（06A 带宽受限采集） | P2（以读代练） | 15–25 min | `cd lab4_edge_uploader && $PY simulate.py && $PY test_uploader.py` |

全部测试 plain assert、无 pytest；任何一条命令失败都会非零退出。

## 周日只有 2 小时练代码 → 推荐路径

> 场景：周日 §1 时间表里能挤出的动手时间只有 ~2 小时（例如把 20:15 coding 块扩容，
> 或午休/晚饭后各偷 30 分钟）。目标不是"跑通"（已全部验收跑通），是**手感和叙述**。

1. **lab6 debug 演习（40 min，P0）**——跑 `buggy_train.py`，**不开 HINTS 盲修计时**，
   目标 15 分钟内抓到 4/5 个 bug；对照 SOLUTIONS.md 把每个「症状→假设→验证→修复」用英文
   各说 30 秒。这是最像真实面试轮的一个 lab。
2. **lab5 冷写（40 min，P0）**——跑一遍 `train_bc.py` 看主结果表，然后限时 30 分钟填
   `skeleton.py`，用 `BC_IMPL=skeleton $PY test_skeleton_ref.py` 验证。全绿 = 你能现场
   写出 BC 训练闭环。
3. **lab1 排查（25 min，P1）**——`generate_logs.py` 后按 EXERCISE.md 三问自己挖
   （别看 .py 源码），再跑 `triage.py` 对答案；六个分析函数名就是口头模板。
4. **lab7 过一遍（15 min，P1）**——跑 `evalstats.py`，把 [2] 样本量表抄到数字卡
   （905/1565/434/371 对/±8pp/α→23%），保证周一报数和文档口径一致。

**lab2 / lab3 / lab4 以读代练**：只跑各自的一键命令看输出（合计 < 1 分钟），然后每个花
10 分钟按其 README 的「再读什么」读关键函数——它们对应的是设计题（06 A/B + 04）的
"我真的实现过这段逻辑" 弹药，动手改代码的边际收益低于以上四个。

## 验收状态（2026-08-08）

- 7 个 lab 全部冷启动（删除生成数据后从零）复跑通过：lab1 6/6、lab2 11/11、lab3 8/8、
  lab4 9/9、lab5 三套测试全绿、lab6 全绿（buggy/fixed gap 0.875）、lab7 全绿。
- 确定性验证：关键脚本复跑两次输出逐字一致（lab5/6 仅 wall-time 打印行不同，数值全同）；
  lab1 数据字节级复现、lab3 manifest id 跨冷启动一致。
- 依赖审计：仅标准库 + numpy（+ torch，限 lab5/6），无 pandas、无网络。
