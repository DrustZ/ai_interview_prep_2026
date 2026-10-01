# lab4_edge_uploader · 家用机器人边缘上传队列模拟器

⏱ 熟悉 15–30 分钟 ｜ 纯标准库、零依赖 ｜ 全部测试 < 2 秒 ｜ 解释器：`/usr/bin/python3`（Python 3.9.6）

**对应考点**：[bot_company/06](../../06_system_design_playbooks.md) Playbook A「家用机器人 Fleet 数据采集」——(a) 题**带宽受限数据采集**的可运行版本。06 里那句 hook——*"450 TB/day is neither feasible nor necessary"*——推出的结论是「设计重心在边缘侧决定不传什么」；这个 lab 就是把边缘侧那个「上传器」框图变成 ~400 行经得起 code review 的代码：优先级队列 + 每日 WiFi 配额 + 分块断点续传 + 指数退避 + aging 防饿死 + 环形缓冲区丢弃策略。

## 一、先跑什么（5 分钟）

```bash
/usr/bin/python3 simulate.py       # 7 天模拟：正常日 / 断网日 / OTA 风暴日
/usr/bin/python3 test_uploader.py  # 9 条断言 = 9 个设计承诺
```

`simulate.py` 输出一张 7 天表格，读表顺序：

1. **budget% 列**：每天都 ≤ 100%——每日配额是硬约束，代码里不可能超支（chunk 放不进剩余预算就不发）；
2. **day 3 (outage)**：上传量掉到 ~65%，backlog 涨——16 小时断网；第二天从**已完成的 chunk** 继续，summary 里 `resume exactness -> True` 证明没有任何字节被重传；
3. **day 4 (storm)**：OTA 事故导致 failure 从 2/天 激增到 60/天 + 8 次人工接管。看 `done` 列：8 个 intervention 全部当天传完；`drop` 列：32 个 routine 视频被挤出缓冲区——**但 metadata 列 = 94，当天所有事件的元数据照样全部到云**；
4. **summary**：`intervention video lost: 0`——七天下来 14 个接管片段一个不丢、全部完整送达。

## 二、再读什么（15 分钟）

按这个顺序读 `uploader.py` 的三个函数（其它都是脚手架）：

| 函数 | 它回答的面试问题 |
|---|---|
| `effective_priority()` | 优先级怎么定？intervention > failure > novelty(嵌入距离加成) > routine；**aging 让等待者涨分但封顶在 intervention 楼下**——资历救得了 routine，救不过人工接管 |
| `_make_room()` | 缓冲区满了丢谁？丢「本来就最后才会传的」：routine 先走、novelty 其次、failure 最后，**intervention 永不被逐**；极端情况下宁可超容量收下 intervention 并报警（overflow_admit），也不丢 |
| `_upload_pass()` | 一个 tick 里发生什么？**先清 metadata（level 1），再按严格优先级发视频 chunk（level 2）**；chunk 不够预算就停（不许小文件插队——bypass 会重新引入饿死）；发失败按 2/4/8/16 tick 退避 |

然后扫一遍 `test_uploader.py` 的 9 个测试名——每个测试就是一条可以在面试里直接说出口的 invariant。

### Privacy-by-design 在代码里的三个落点（面试必讲）

06 的 privacy 要点「**元数据先行、视频按需拉取**」在这里不是口号，是三处代码结构：

1. `_upload_pass()` 里 level-1 metadata 队列**先于任何视频字节**清空（metadata 只有 2 KB、不含像素，只有任务 ID/结果/novelty 分）；
2. `_top_video_candidate()` 拒绝 metadata 未上传的事件——**级别 2 结构上不可能先于级别 1**；
3. `_evict_video()` 只丢视频、保留 metadata——即使风暴日视频被牺牲，云端仍知道「这个片段存在过」，可以事后下发 campaign 定向拉取。

测试 7 和测试 9(e) 把这个承诺变成断言：风暴日 routine 一个视频字节都没传，但 268/268 事件的 metadata 全部到云。

## 三、动手改参数（可选，10 分钟）

- 把 `UploaderConfig.aging_per_tick` 改成 `0`，重跑 sim：day 5–6 的 routine 完成数归零——这就是饿死（测试 8 的 control 分支就是它）；
- 把 `buffer_capacity_bytes` 减半：风暴日 drop 数翻倍，但 `intervention lost` 仍然是 0；
- 把风暴日 failure 提到 200：观察 overflow_admits 是否触发。

## 四、面试中怎么引用

> "To make the edge-side story concrete, I built a small simulator of the upload problem: a priority queue where teleop interventions preempt everything and are never dropped, a hard daily WiFi quota, chunked resumable uploads with exponential backoff, and an aging term so routine samples can't starve — the takeaway I'd defend is that on a bandwidth-starved fleet the upload policy IS the data strategy, and a metadata-first two-level upload is what keeps privacy and fleet visibility compatible."

### 追问预演

| 追问 | 答 |
|---|---|
| aging 会不会让垃圾数据反超关键数据？ | aging 封顶（cap 55，ceiling 95）永远低于 intervention 的 100；它只保证 routine 在 failure/novelty 的**持续新流量**下不至于无限等待——而 routine 里是均匀随机采样，那是对冲 trigger selection bias 的数据，饿死它等于放弃分布校准 |
| 顶部大文件卡住预算尾巴，为什么不让小文件插队？ | 故意的。bypass 等于给低优先级开后门，饿死会换个形式回来；配额尾巴浪费几十 MB 是可预算的成本，优先级反转不是 |
| 真实系统和这个玩具差在哪？ | 至少五处：chunk 要 per-chunk checksum + 服务端去重；断点状态要 journal 到磁盘防掉电；多机器人共享家庭上行要 fairness；传输走 QUIC/S3 multipart；trigger 风暴防护应该在**入队前**做 per-class fire-rate 限额（本 lab 的丢弃策略是最后一道防线，不是第一道） |
| 为什么 novelty 用嵌入距离？ | `simulate.py` 里 novelty = 场景嵌入到运行中心的距离 `d/(1+d)`——这是 06 触发清单第 5 类「场景 embedding 与已采集分布距离大」的最小代理；真实版是设备端小模型对 fleet 分布的密度估计 |

## 五、诚实性提醒

这是**教学用最小复现**，不是生产系统、更不是项目经历。面试里的正确说法：「为了把 06 题边缘侧的框图变具体，我写了个可复现的模拟器验证这五条 invariant；它不能证明真实 fleet 规模下的表现，下一步是掉电持久化和多设备公平性。」

## 文件

```
uploader.py        核心：EdgeUploader（优先级/配额/续传/退避/aging/丢弃）
simulate.py        7 天模拟（正常/断网/风暴），novelty 用嵌入距离代理
test_uploader.py   9 条 plain-assert 测试，/usr/bin/python3 test_uploader.py
```
