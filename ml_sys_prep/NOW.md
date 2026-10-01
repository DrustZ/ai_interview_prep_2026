# NOW —— 只看这一屏

> 这个文件替代 `00_study_plan.md` 当入口。
> 两天日历那种东西注定过期（它已经过期两次了）。**这里只写：下一场是谁、几点、今天只做什么。**
> 每场面试结束后**立刻**更新这个文件。

## 🔴 下一场

| | |
|---|---|
| **Bridgewater AIA · 第 1 轮** | **7/31（明天）12:00–13:00 ET** |
| 面试官 | Ananth Ravi Kumar（Columbia 应用数学 / 多维时序 / 写过期权回测框架） |
| 形式 | 前半系统深挖 20–25 min，后半**陌生 repo review（用 AI 工具）** 20–25 min |
| 主文件 | [`../projects/bridgewater_aia/README.md`](../projects/bridgewater_aia/README.md) |

## 今天只做这四件事（别写任何新文档）

```
□ 1. 4 分钟自我介绍 + 20 分钟项目深挖，**录音一次**回放
     → python mock.py score --kind deepdive
□ 2. 陌生 repo review 25 分钟计时 + 5 分钟分级陈述
     → python ../projects/bridgewater_aia/gen_practice_repo.py --seed <随便一个没用过的>
     → python mock.py followups --kind review   （答完再 score）
□ 3. 完整跑一次 60 分钟真实流程（介绍 + 深挖 + review + 反问）
□ 4. 环境：Claude Code / git clone / Zoom 共享屏幕 / 终端字号
```

**门槛**：`python mock.py status` 里 `deepdive` 和 `review` 都是 🟢 才算准备好。
🟢 的定义 = 连续两次「≥32/40 且无单项<3 且三个追问都稳 且没超时」。

## 找不到东西时 → [`INDEX.md`](INDEX.md)

每个概念的「正本」在哪，一张表。别在 12,000 行里翻。

## 三个工具（取代「读材料」）

```bash
V=/Users/mingrui/Documents/codes/interview/.venv/bin/python

$V drill.py --list                    # 36 道闭卷题，7 个 topic
$V drill.py --topic timeseries -n 8   # 抽题，出声答，对锚点自评
$V drill.py --weak                    # 我最弱的 topic 是哪个
$V drill.py --topic X --hard          # 只重练上次没答满分的

$V mock.py followups --kind review    # 随机 3 个追问
$V mock.py score --kind review        # 8 维打分，存历史
$V mock.py status                     # ready 了没（连续两次才算）

$V ../projects/bridgewater_aia/gen_practice_repo.py --seed <新数>   # 每次换靶子
```

**这三个取代通读。** 阅读的作用是第一次建立概念；
之后每一次「复习」都应该是 drill，不是重读 —— 重读会产生「看过但讲不出」。

## 排期与优先级

| 优先级 | 公司 | 状态 | 材料 |
|---|---|---|---|
| **P0** | **Bridgewater 第 1 轮** | **7/31 12:00 ET** | [`bridgewater_aia/`](../projects/bridgewater_aia/) |
| P1 | Applied Compute work trial | 两天 on-site，待定日期 | [`onsite_prep/`](../projects/onsite_prep/) |
| P2 | Exa 第二轮 | **待约** | [`20_case_exa_agentic_search.md`](20_case_exa_agentic_search.md) |
| P3 | Bridgewater 第 2 轮（**非 ML** 系统设计） | 第 1 轮过了才有 | [`bridgewater_aia/06_rounds_2_3.md`](../projects/bridgewater_aia/06_rounds_2_3.md) |
| P4 | OpenAI pretraining 等通识 | 无日期 | [`07_pretraining_data.md`](07_pretraining_data.md) |

## 三条纪律

1. **每天只排 70% 容量。** 原来的两天计划标着「约 7 小时」，实际是 **545 / 502 分钟**（超 20–30%）。塞满 = 看过但讲不出。
2. **新增阅读材料暂停。** 现在瓶颈不是材料不够，是闭卷提取和陌生题迁移。
3. **靶子用完就换种子。** 看过答案的 repo 不再是盲测。

## 面试完之后

立刻做三件事，再谈下一场：
```
□ 更新本文件的「下一场」
□ python mock.py score  记一次真实表现
□ 把被问倒的点写进对应公司的 00_intel.md
```
