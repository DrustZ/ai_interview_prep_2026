# lab3_data_engine — Teleop 演示数据摄入/管护 Pipeline

> The Bot Company（家用机器人，fleet learning 路线）备考 Lab。
> 解释器固定 `/usr/bin/python3`（Python 3.9.6），纯标准库，零依赖，全部确定性，测试全程 < 5 秒。

## 这个 lab 对应什么考点

岗位核心是 **data collection / data engine**：机器人学习公司的护城河不是模型，而是
"teleop 演示 → 清洗管护 → 训练集 → 部署反馈 → 下一轮采集" 这个闭环。本 lab 把闭环的
工程形态做成了四阶段 pipeline，每一阶段都是面试高频追问点：

| 阶段 | 函数（pipeline.py） | 面试考点 |
|---|---|---|
| 1. Schema 校验 | `validate_lines` | 坏数据**进 quarantine 并留机器可读原因**，不静默丢弃（可观测性、可 debug） |
| 2. 去重 | `dedup_records` | 精确去重（content hash，排除 demo_id）+ 近似去重（task/operator/场景 + 量化几何特征分桶），keep-first + 完整 audit trail（谁替谁被丢） |
| 3. 质量过滤 | `filter_by_quality` | **可解释**启发式打分：超长停顿 / 高 jerk 抖动 / 重试过多 / 未完成，各扣多少分写在 config 里而不是代码里，阈值可调 |
| 4. 分层配比 | `stratify` | 按 task 目标分布重采样（盈余 task 按质量分取 top-k，欠缺 task 全收）并输出**采集需求单**：缺哪个 task、缺多少、优先补哪种光照/房间 cohort —— 这就是 curation 反哺 collection 的闭环，data collection 岗的点睛之笔 |

再加 `manifest.py` 的两个生产级设计：

- **内容寻址 manifest**：`manifest_id = sha256(sorted demo_ids)`，训练集身份只由内容决定；
  lineage 记录 parent manifest、pipeline config 快照、每个输入文件的 sha256 —— 任何一个
  训练集都能溯源到原始批次和当时的参数。
- **增量运行**：state 里存已处理文件哈希 + 去重索引 + 幸存记录；重跑只处理新批次
  （阶段 1–2 只碰新数据，阶段 3–4 在幸存池上全局重算，便宜且与到达顺序无关）；
  无新数据的重跑是幂等 no-op；增量构建与一次性全量构建产出**完全相同的 manifest id**。
  输入文件被原地修改、或换 config 继续增量，都是硬错误（保护 lineage 不被悄悄作废）。

## 15–30 分钟熟悉路径（先跑什么，再读什么）

```bash
cd my_interview_prep/ml_sys_prep/bot_company/labs/lab3_data_engine

# 1. (2 min) 生成两个批次的合成 teleop 数据（807 + 127 行，含已知缺陷的 ground truth 侧车文件）
/usr/bin/python3 generate_demos.py --batch 1
/usr/bin/python3 generate_demos.py --batch 2 --cross-dup-from data/demos_batch1.jsonl

# 2. (3 min) 增量构建 manifest，看 stage funnel、manifest id、采集需求单；再跑一次看幂等 no-op
/usr/bin/python3 manifest.py
/usr/bin/python3 manifest.py        # "no new inputs; manifest unchanged"

# 3. (2 min) 跑测试（8 个，plain assert）
/usr/bin/python3 test_pipeline.py

# 4. (10 min) 读 pipeline.py：按 Stage 1→4 顺序读四个函数 + PipelineConfig，
#    重点看 content_hash / near_dup_key（生成器 import 它们来保证注入的重复必然碰撞）
#    和 stratify 里采集需求单的构造。

# 5. (8 min) 读 manifest.py 的 run_incremental：state 里存什么、为什么阶段 1-2 增量而 3-4 全局重算、
#    no-op 判定、两个硬错误（输入被改 / config 漂移）。

# 6. (可选) 拧旋钮看 funnel 变化：
/usr/bin/python3 pipeline.py --quality-threshold 0.9 --workdir /tmp/lab3_strict
ls out/            # quarantine.jsonl / dedup_report.json / quality_report.json /
                   # collection_requests.json / train_set.jsonl / manifests/ / state.json
```

关键数字（种子固定，永远复现）：934 行输入 → 18 条 quarantine → 916 有效 →
35 精确重复 + 35 近似重复 → 846 幸存 → 46 低质量剔除 → 800 → 分层选出 375 条，
2 张采集需求单（sort_laundry 缺 34 条、water_plants 缺 11 条，各附最稀缺光照/房间提示）。

## 面试中怎么引用这段经验（英文一句话）

> "I prototyped a fleet-style data engine for teleop demos: a four-stage pipeline — schema
> quarantine with machine-readable reasons, exact-plus-near dedup with a full audit trail,
> explainable quality gates, and stratified resampling that emits collection tickets for
> under-represented task cohorts — feeding content-addressed, lineage-tracked training
> manifests that are reproducible bit-for-bit across incremental and full rebuilds."

追问弹药：为什么 quarantine 而不是丢弃（fleet 端 bug 的第一现场）；near-dup 桶粒度怎么调
（桶太粗误伤多样性、太细漏重复，用 dedup_report 抽查校准）；质量分为什么用可解释启发式
而不是学出来的分类器（冷启动没标注、且 ops 团队要能申诉）；采集需求单如何闭环（直接变成
teleop 排班：哪个 task、什么场景、采多少条）；manifest 内容寻址如何支撑训练可复现与回滚。

## 文件清单

```
generate_demos.py   确定性合成数据生成器：700 clean + 40 差质量 + 25 精确重复 + 30 近似重复
                    + 12 坏 schema 行（batch 1，共 807 行）；batch 2 另含 5 条跨批次重复；
                    每批附 .summary.json ground-truth 侧车，注入的重复用 pipeline 自己的
                    hash/桶函数验证"必然碰撞"
pipeline.py         schema（dataclass）+ 四阶段纯函数 + PipelineConfig + 一次性 CLI
manifest.py         内容寻址 manifest + lineage + 增量 state + 增量 CLI
test_pipeline.py    8 个测试：生成器确定性 / 各阶段计数与 quarantine 原因 / 去重正确性
                    （注入重复全被抓、幸存者双重唯一、audit 指向幸存者）/ 质量过滤恰好剔除
                    注入的差样本 / 分层配比与需求单指向真实欠缺 cohort / manifest 跨 workdir
                    可复现 / 增量幂等 + 增量==全量 + lineage / 两个硬错误守卫
```

运行测试：`/usr/bin/python3 test_pipeline.py`
