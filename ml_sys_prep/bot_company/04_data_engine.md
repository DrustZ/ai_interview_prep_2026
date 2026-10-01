# 04 · Robot 数据引擎与采集（Data Engine & Data Collection）

> 岗位核心文件。面试官可能是 Cruise 出身：disengagement / triage / counterfactual / regression scenario 这套词要能脱口而出。
> 注：本文关于 The Bot Company 本身没有可引用的公开事实（调研简报未覆盖），所有公司实践均来自 Tesla / Cruise / Waymo / 1X / PI / Figure 的公开资料。

---

## TL;DR — 只有 20 分钟就看这段

1. **一句话世界观**：家用机器人 fleet = AV fleet 的近亲。用户打断 / teleop 接管 / 任务失败 ≈ disengagement；整个数据引擎就是把每次失败变成训练数据 + 永久回归测试的闭环。
2. **飞轮七步**：deploy → 机端 trigger 监控 → 事件式采集上传 → curation（去重/配比/过滤）→ 训练 → eval（回归集 + world-model/replay）→ 再 deploy。北极星是**飞轮周期**（failure 被观测到修复上线的天数）。
3. **Tesla 贡献的词**：shadow mode、trigger campaign（~221 个手工触发器）、机端先筛不回传原始流、离线 auto-label（4D 重建 + 后见之明）、每个 bug 变 eval clip（"Operation Vacation"）。
4. **Cruise 贡献的词**：CLM（自监督标签"等几秒就出现"+ active learning miner 只收显著偏差场景）、event triage funnel（去重聚类 → severity×frequency 排序 → 根因归类 → counterfactual replay 判定 necessary vs unnecessary takeover）、Road-to-Sim（每个路测事件永久变回归场景）。
5. **1X 贡献的词**：产品先于自主性（NEO teleop 进家，$20k/$499月）、operator = trainer（"farm-to-table" 数据）、Redwood 板载推理（隐私+延迟）、world model 解 eval 吞吐瓶颈、"social contract" 明码隐私换数据。
6. **PI 贡献的教义**：pre-train 大而杂（次优数据教恢复），post-train 小而精（教流畅）；π0.5：泛化随**环境数**呈幂律，~100 环境近上限，web 数据救 OOD 物体；π*0.6/RECAP：demos → 专家纠偏（接管即数据）→ 自主 rollout RL，采集成本结构从纯 teleop 转向机器人自产经验。
7. **Scaling law 结论（预算怎么花）**：泛化随环境数/物体数幂律增长，单环境 demo 数过阈值边际趋零 → **钱买多样性，不买同环境条数**。
8. **Teleop 生产线数字**：leader-follower 20–40 demos/h，VR 10–20；全摊 $28–60/操作员小时，成品数据 ~$118–136/h（2025-26 第三方市场口径，未证实——口头说 "on the order of $100+ an hour"），每条成功 demo $1–10；三层 QA（自动打分 → gold-set 校准 → 人工终审）。
9. **Failure-driven 三板斧**：接管即金标数据（DAgger 谱系）；失败 taxonomy → 定向采集 campaign；miner 挖相似场景 + 每个失败固化为回归 eval。
10. **隐私必背案例**：iRobot 如厕照经 Scale AI 外包标注员外泄——**威胁模型必须覆盖整条数据供应链，不只是设备端**；正面模板是 1X（逐次同意、no-go zones、边缘脱敏、自有操作员）。
11. **指标四件套**：采集产能（demos/h/operator、$/demo、QA 良率）、coverage（任务×环境×物体矩阵、独立环境数）、飞轮速度（cycle time、eval 吞吐）、边际贡献（每 +N 小时的成功率增益；部署侧 intervention rate = 家用版 miles per disengagement）。

---

## 1. 数据飞轮全景

### 1.1 ASCII 图

```
                ┌────────────────────────────────────────────────────────┐
                │                      FLEET (homes)                     │
                └────────────────────────────────────────────────────────┘
                     │  on-robot triggers:                        ▲
                     │  低置信度 / 用户打断 / teleop 接管 /         │ OTA 部署
                     │  任务失败 / shadow-policy 分歧 /             │ 新 policy +
                     │  异常力矩、碰撞、超时                        │ 新 trigger 配置
                     ▼                                            │
   ┌──────────────────────────┐                    ┌──────────────────────────┐
   │ ② 监控 / TRIGGER          │                    │ ⑥ EVAL                   │
   │ 机端算力先筛，事件式最小化 │                    │ 回归集(每个历史失败一条)  │
   │ 上传，隐私脱敏在边缘完成   │                    │ + replay / world-model   │
   └──────────────────────────┘                    │ + 真机 rollout 抽检       │
                     │                              └──────────────────────────┘
                     ▼                                            ▲
   ┌──────────────────────────┐                    ┌──────────────────────────┐
   │ ③ 采集 COLLECT            │                    │ ⑤ 训练 TRAIN             │
   │ fleet 触发片段 +          │                    │ pre-train: 大而杂        │
   │ teleop 定向 campaign +    │───────────────────▶│ post-train: 小而精       │
   │ 接管/纠偏轨迹 + 人类视频   │   ④ CURATE         │ (+ RL on rollouts)       │
   └──────────────────────────┘   去重/去劣/配比/    └──────────────────────────┘
                                  auto-label/QA/
                                  coverage 管理
        ┌──────────────────────────────────────────────────────────┐
        │ TRIAGE FUNNEL（横切②③）: 事件去重聚类 → severity×frequency │
        │ 排序 → 根因归类(perception/planning/…) → counterfactual    │
        │ replay 判定 → 路由 owning team → 数据修 or 代码修           │
        │ → 该事件永久进入回归 eval 集                                │
        └──────────────────────────────────────────────────────────┘
```

### 1.2 每一步的关键设计点

| 步骤 | 关键决策 | 行业范式 |
|---|---|---|
| ① Deploy | OTA 同时下发 policy 和 trigger 配置；新 policy 可先跑 shadow mode（只推理不执行） | Tesla shadow mode |
| ② 监控/触发 | 机端算力先筛，**只上传有信息量的片段**——带宽 + 隐私双约束下的必然架构；家用场景隐私压力比车更大，on-device 筛选更刚性 | Tesla ~221 个手工 trigger |
| ③ 采集 | 四路来源分层：fleet 触发片段（免费、真分布）、teleop campaign（贵、有动作真值）、接管/纠偏（金标失败数据）、egocentric 人类视频（便宜海量、无动作真值） | Optimus 转 vision-only rig；Figure Go-Big |
| ④ 管护 | 去重去劣、混合配比、coverage 矩阵管理、auto-label 占比持续提升 | Re-Mix、SCIZOR、Tesla auto-label |
| ⑤ 训练 | pre-train 杂数据教恢复，post-train 精数据教流畅；成熟期加自主 rollout RL | PI 教义、π*0.6 RECAP |
| ⑥ Eval | 每个历史失败一条回归测试（失败一次，永远测试）；world-model / replay eval 解决真机吞吐瓶颈 | Cruise Road-to-Sim、1X World Model |

**面试时的框架句（英文）**：
> "I think of the data engine as one loop with one north-star metric: cycle time from 'a failure is observed in a home' to 'a fix is deployed and that failure is a permanent regression test.' Every architectural choice — on-device triggers, event-based upload, auto-labeling, world-model eval — exists to shrink that cycle time under privacy and cost constraints."

---

## 2. Tesla / Cruise / 1X / PI 实践对比

| 维度 | Tesla Autopilot | Cruise | 1X | Physical Intelligence |
|---|---|---|---|---|
| **数据来源** | 数百万客户车 = 客户付费的分布式传感网络（成本被购车者补贴） | 自营 robotaxi 车队 + 安全员 | NEO teleop 进家（2025-10 预订，$20k 或 $499/月）：**teleop 期间每次操作/纠偏都是带标签训练数据**，"robot 是数据采集的楔子" | 内部多构型采集：π0 >10,000 h、903M timesteps、7 种构型、68 类任务；混 OXE 开源（~9.1%）|
| **挖掘/触发机制** | ~221 个手工 trigger + shadow mode 分歧挖掘 mispredictions | CLM active learning miner：只收"预测与现实显著偏差"场景，miner 自身 few-shot 训练；三步循环 gathering→mining→update | teleop 接管本身即失败采样点 | π*0.6/RECAP：DAgger 式实时 coaching，接管即数据 |
| **标注** | 离线 auto-label：4D 重建 + 多趟聚合 + 未来帧后见之明；1 万 clip 一周（人工需数月）；人只做 QA | 自监督："等几秒真值自动出现"（实际轨迹即 label） | operator = trainer，采集者自己训模型（"farm-to-table"，闭环极短） | 语言子任务标注（π0.5）；advantage/value 标注（RECAP）|
| **Eval / 回归** | 每个 bug 变 unit-test eval clip；目标 "Operation Vacation" | Road-to-Sim 把每个路测事件程序化重建为永久 sim 场景；Morpheus 参数化生成上千稀有场景；counterfactual 判定接管必要性 | 1X World Model：动作条件视频世界模型，部署前预测候选 policy 结果，解真机 eval 吞吐瓶颈 | 真机指标公开：π*0.6 吞吐 ×2、失败率 ÷2，咖啡机 18h 连续运行 |
| **最可迁移的观点** | 机端先筛 + 事件式上传；trigger campaign 可 OTA 迭代 | triage funnel + counterfactual + "每个事件变回归测试" | 隐私模板（逐次同意/no-go zone/自有操作员）+ 板载推理 + world-model eval | 数据分层教义 + 环境数幂律（~100 环境近上限）+ 采集成本结构随自主性提升而改变 |

**补充参照（一句话级）**：
- **Waymo**：Fleet Response（远程人答问不代驾，每次求助 = 不确定性采样点）；Content Search（自然语言 query the fleet 的日志，学界对应 VLMine）；counterfactual 安全方法论估真实碰撞率；~30k→60k 英里/脱离，年均 +19%。
- **Figure**：Helix 初版只用 ~500 h 高质量 teleop（质量与多样性优先于体量）；公开边际收益曲线：物流 10→60 h ⇒ 6.3→4.3 s/件、扫码 88%→~95%——**业内少见的"数据量 vs policy 指标"曲线，面试直接引用**；Go-Big 与 Brookfield（10 万+ 住宅）采 egocentric 人类视频，声称零机器人演示 zero-shot human-to-robot transfer。
- **Tesla Optimus**：早期 50+ mocap 服操作员 → 2025 年中转 vision-only 5 相机头盔 rig，理由是扩展速度。行业趋势：**teleop（贵、慢、动作真值全）与人类视频（便宜、海量、无动作真值）互补分层**。

---

## 3. Teleop 数据生产线设计（当 system design 答）

面试可能直接问："Design our teleop data collection operation from scratch." 按 requirements → 架构 → 数字 → 追问点答。

### 3.1 Requirements & 假设（先说出口）

- 目标：为家务操作任务产出 post-train 级高质量 demo + 覆盖长尾的定向采集能力。
- 约束：预算有限（每小时全摊成本要盯）、隐私（进家的数据）、scaling law 告诉我们要优先买**环境/物体多样性**。
- 两种采集形态：集中式 site（可控、吞吐高、环境多样性靠搭景）+ in-home teleop（真实分布、隐私和同意成本高）。

### 3.2 生产线架构（六个子系统）

```
[任务定义] → [操作员 ops] → [采集执行] → [ingestion/QA] → [数据入库] → [反馈回路]
```

1. **任务定义（task cards）**：每个任务一张卡——scripted variation（物体/位姿/光照/背景系统化随机）、明确成功判据、reset 规范、语言标注/子任务切分要求。每任务先由 best operator 采 20–50 条 **gold demos** 作基准，之后新 demo 自动算与 gold 的相似度分。
2. **操作员 ops**：招募（美国中等城市 $20–35/h，SF/NY $30–50，远程 VR $20–30）→ qualification protocol 认证上岗 → per-operator 质量分持续跟踪 → 45 分钟采集 + 15 分钟休息班制 → **跨任务轮换**防风格过拟合/adaptation bias。家庭场景操作员必须背景调查 + NDA（1X 做法）。可选的文化设计：让 operator 参与训练与评估（1X "operator = trainer"），闭环短、质量高。
3. **采集执行**：硬件选型按任务分层——leader-follower（ALOHA 系，<$2,000，20–40 demos/h）用于桌面任务；VR（10–20 demos/h）用于全身/移动任务；kinesthetic（5–10）仅特殊场景。相机标定例行检查写进班前 checklist。环境 reset 靠人工，是吞吐上限之一——排班时把 resetter 算进去。
4. **Ingestion + 三层 QA**：
   - L1 自动 per-episode 打分：jerk / 停顿 / 空闲段 / 碰撞 / 时长离群 → 直接过滤或标记；
   - L2 gold-set 校准：与 gold demos 的相似度分做漂移检测；
   - L3 人工抽检终审 + rework/重采回路。
5. **数据入库**：统一 episode schema（obs 流 + 动作 + 语言标注 + 元数据：operator id / 环境 id / 物体 id / 任务版本），入 coverage 矩阵（任务×环境×物体），带 lineage 可追溯到训练集版本。
6. **反馈回路**：实时看板盯 demos/h、成功率、活跃操作员数（按站点）——提前暴露硬件故障和操作员困惑；训练侧的数据 ablation 结果反哺任务卡优先级。

### 3.3 关键数字（背下来）

| 项 | 数字 |
|---|---|
| 吞吐 | leader-follower 20–40 成功 demo/h（熟练 30+）、VR 10–20、kinesthetic 5–10 |
| 人力成本 | 全摊 $28–60/操作员小时（工资+督导+场地+硬件摊销） |
| 成品数据价格 | 2024 初 ~$340/h → 2025Q4 ~$136/h → 2026-03 ~$118/h（标准 pick-place 配置；第三方市场报价口径，未证实——面试只说趋势"两年降了约 2/3"，别报到月份）|
| 单条成本 | 每条成功 demo $1–10 |
| 硬件 | leader-follower 系统 <$2,000 |
| Figure 参照 | Helix 初版仅 ~500 h teleop；10→60 h ⇒ 6.3→4.3 s/件、88→95% 扫码 |

### 3.4 预判追问（每条给一句英文答）

- **"How do you trade quality vs quantity?"**
  > "Stratify by training stage. Pre-training tolerates — even benefits from — suboptimal data because it teaches recovery behavior; post-training needs curated, fluent demos. And the data scaling laws result matters here: generalization follows a power law in the number of environments and objects, while per-environment demo count saturates fast. So my marginal dollar buys a new environment or object, not the 300th demo in the same kitchen."
- **"How do you keep operator quality consistent without making the data too homogeneous?"**
  > "Per-operator quality scores calibrated against gold demos catch degradation; task rotation prevents style overfitting. Stylistic consistency improves policy smoothness, but a single style hurts robustness — so I want consistent *quality* with diverse *operators*."
- **"Where does this break at 10x scale?"**
  > "Reset labor becomes the throughput ceiling, QA can't stay human-in-the-loop for every episode so the automated L1 filters and gold-set drift detection have to carry more weight, and coverage management shifts from a spreadsheet to an inventory system with fill targets per long-tail bucket — the same way AV companies manage long-tail scenario inventory."
- **"In-home vs collection site?"**
  > "Sites win on throughput and control; homes win on distribution match — and the deployment distribution is what we're graded on. I'd run sites for volume and use in-home teleop, gated by the consent machinery, primarily for failure-driven campaigns and distribution calibration, tracking KL distance between collected data and real usage."

---

## 4. Curation 与 Active Learning

### 4.1 Curation 流水线（顺序即优先级）

1. **去劣**：剔 no-op/idle 段、失败且无纠偏价值的 episode；SCIZOR 自监督过滤次优片段。
2. **去重**：embedding 聚类去近重复 + SCIZOR 语义去重。
3. **配比（最大杠杆之一）**：Re-Mix 用 DRO 自动学 domain 权重——比 uniform 好 38%、比人工配比好 32%。**"配比即杠杆"** 是可直接说的观点句。
4. **Balancing**：维护任务×环境×物体 coverage 矩阵；每任务保底条数后预算转向多样性；长尾 bucket 设填充目标（Tesla/Cruise 长尾库存管理思路搬到操作任务）。
5. **归因（前沿）**：DataMIL/datamodels 按下游影响选数据——回答"哪 1% 数据最值钱"。

### 4.2 Active Learning：车界三范式直接迁移

| 范式 | 车界原型 | 家用机器人版 |
|---|---|---|
| 不确定性/分歧触发 | Tesla trigger（检测抖动、ensemble 分歧、shadow-policy 与人类行为分歧） | 机端置信度 + shadow policy 与 teleop 操作分歧 → 自动打包上传 |
| 误差挖掘 miner | Cruise CLM：只把"预测 vs 现实显著偏差"送训练集 | policy 预测轨迹 vs 实际执行/纠偏轨迹偏差挖掘 |
| 检索式 query the fleet | Waymo Content Search / VLMine（VLM 挖长尾） | 对 fleet 日志建 embedding 索引，自然语言检索"透明容器抓取失败"类场景 |

**一句英文观点**：
> "Active learning in robotics isn't a research feature, it's the routing layer of the whole engine: it decides which of the fleet's petabytes ever deserve upload, labeling, or a collection campaign."

---

## 5. Failure-Driven Data Collection（高频考点）

### 5.1 方法论三板斧

1. **接管即金标数据**：自主执行中人接管 = 失败标注 + 正确后续，一条数据两种信号（DAgger / HG-DAgger / Sirius 谱系；π*0.6 RECAP 的 coaching 是工业化版本）。
2. **失败 taxonomy → 定向 campaign**：按失败模式建分类（抓取滑落 / 遮挡 / 语言歧义 / 长程规划断裂），逐类下发采集任务——Tesla trigger campaign 的操作任务版。
3. **回放/世界模型前置发现失败**：1X world model 预测候选 policy 结果；Cruise Road-to-Sim 让每个事件永久成为回归场景——**失败一次，永远测试**。

### 5.2 示范回答（英文，背熟）

**Q: "Our bot has a high failure rate on one task category. How do you fix it with data?"**

> "I'd run it as a triage-then-campaign loop, borrowing directly from how AV companies handle disengagements.
>
> **First, characterize before collecting.** Pull every failure episode in that category from fleet logs, dedupe and cluster them, and rank clusters by severity times frequency. Then attribute root cause per cluster — is it perception (occlusion, novel objects), policy (grasp slip, wrong subtask), language grounding, or something upstream like calibration or a broken reset assumption? A high failure rate on one task is almost never one problem; it's usually two or three clusters, and some of them aren't data problems at all — if it's a hardware or calibration issue, no amount of demos will fix it.
>
> **Second, verify it's a policy deficiency.** Replay the failures — against the current policy and candidates — through offline eval or a world model, the way Cruise used counterfactual sim to separate necessary from unnecessary takeovers. That also gives me a frozen regression set: every one of these failures becomes a permanent test before I've collected a single new demo.
>
> **Third, targeted collection per cluster.** For each data-fixable cluster I launch a campaign: teleop demos with scripted variation concentrated on the failing conditions — the specific objects, poses, lighting, clutter — plus recovery demonstrations that start from the failure state, because the policy needs to learn to get *out* of trouble, not just avoid it. In parallel, a miner searches fleet logs for near-miss lookalikes so I'm training on the whole failure neighborhood, not just the reported cases. And every future intervention on this task is auto-tagged as gold data — DAgger-style, interventions are the cheapest high-signal data we have.
>
> **Fourth, retrain and gate on the regression set.** Fine-tune with the new data upweighted but mixed carefully so I don't regress other tasks — mixture weights are a real lever, Re-Mix showed 30-plus percent gains from reweighting alone. Ship behind the regression eval plus a shadow or world-model eval, then watch the deployed intervention rate on that category.
>
> **And the exit criterion matters:** I'd track marginal success rate per 100 added demos — Figure published exactly this curve for logistics, 10 to 60 hours took barcode scanning from 88 to 95 percent — and stop collecting when the curve flattens, because at that point the bottleneck has moved somewhere else."

追问 **"What if the failures are too rare to collect enough of?"**：
> "Then I widen the funnel three ways: mine the fleet for semantic lookalikes with embedding search, synthesize variations in sim or via world-model rollouts anchored on the real failures, and design the teleop campaign to oversample the failure's causal factors rather than replaying it literally. Rare events are exactly where the Cruise CLM lesson applies — U-turns were under 100 sightings a day across the whole fleet, and error-driven mining still fixed them."

---

## 6. Privacy 专节（家用机器人必考）

### 6.1 必背反面案例：iRobot × Scale AI

Roomba 开发测试机图像（含如厕照、儿童面孔）经 Scale AI 的委内瑞拉众包标注员外泄到 Facebook/Discord；测试者签的同意书被认为有误导性；iRobot 终止与 Scale 合作。同类先例：Ring 员工滥看用户视频，FTC 罚 580 万美元（2023）。
**教训**：隐私风险在**整条数据供应链**（含标注外包），不只在设备端。

### 6.2 正面模板：1X NEO 的四件套

1. **逐次同意**：teleop 必须车主 App 内逐次批准/预约时间窗并指定任务，操作员无法擅自接管；
2. **边缘脱敏**：操作员视野内实时人像模糊、音频遮蔽；可设房间/时段 **no-go zones**；
3. **人员控制**：自有（非零工）操作员 + 背景调查 + NDA；
4. **坦率的 social contract**：CEO Børnich 公开言明 "If we don't have your data, we can't make the product better… it is a social contract." —— 用数据换更便宜/进步更快的产品，明码标价而非藏在条款里。

### 6.3 工程措施清单（按数据生命周期）

| 环节 | 措施 |
|---|---|
| 机端 | on-device 推理让原始视频不出户（1X Redwood 跑板载 GPU 的动机之一）；事件触发式最小化上传（Tesla 模式） |
| 上传前 | 边缘侧人脸/敏感区域 redaction（AV 惯例：人脸+车牌模糊） |
| 标注 | PII 清洗 + 受控环境（禁下载、屏幕审计）；供应商纳入威胁模型 |
| 存储 | 保留期限 + 删除权（GDPR/CCPA）；每次远程访问留审计日志 |

**未解难题（主动提出显深度）**：访客/家庭其他成员并未签署同意（第三方同意问题）；LiDAR/深度图同样能重建户型隐私；Figure Go-Big 在 Brookfield 物业拍摄也面临拍摄对象同意与场景真实性的追问。

### 6.4 英文观点句（挑 2-3 句用）

> "Privacy isn't a compliance checkbox on a home robot — it's an architectural constraint that decides what the data engine even looks like: on-device triage, event-based minimal upload, and edge redaction before anything leaves the house."

> "The iRobot leak taught the industry that your threat model has to cover the entire data supply chain — the breach happened at an outsourced labeling vendor, not on the device."

> "I like 1X's framing of an explicit social contract: per-session consent, no-go zones, employed and vetted operators, and an honest statement that data is the price of a product that improves. Users accept data collection they can see and control; they revolt against collection they discover."

> "The unsolved part is third-party consent — guests and family members never signed anything. That's why I'd default to edge blurring of all faces, not just the owner's opt-outs."

---

## 7. 数据指标体系

| 类别 | 指标 | 基准/备注 |
|---|---|---|
| **采集产能** | demos/hour/operator；$/成功 demo；QA 良率（% episodes 通过）；rework 率；站点 uptime；操作员 ramp 时间 | leader-follower 20–40 demos/h；$1–10/demo |
| **Coverage** | 任务×环境×物体覆盖矩阵及其熵；**独立环境数**；长尾 bucket 填充率；与部署分布的 KL 距离 | scaling laws：环境数是泛化主变量，~100 环境近上限（π0.5）|
| **标注质量** | inter-annotator agreement；gold-set 校准精度；抽检缺陷率；**auto-label 占比** | Tesla/Cruise 北极星之一：人工标注占比持续下降 |
| **飞轮速度** | failure 观测 → 数据入库 → 重训 → 部署的 cycle time；在途 campaign 数；eval 吞吐（真机 rollout/天、world-model/replay eval/天） | 1X 用 world model 就是为解 eval 吞吐 |
| **边际贡献** | 每 +N 小时/+100 demos 的成功率增益曲线；数据 ablation/influence 归因 | Figure：10→60 h ⇒ 88→95% 扫码；π0.5 环境数幂律 |
| **部署侧** | intervention rate（次/任务小时）＝家用版 miles per disengagement；自主成功率；吞吐；MTBF | Waymo 参照：~30k→60k mi/disengagement，年均 +19%；π*0.6 吞吐 ×2 |
| **预算北极星** | **$ per point of success rate**（单位能力提升的数据成本）；飞轮层面的北极星仍是 cycle time（§1） | 决定预算在 teleop / 人类视频 / 自主经验 / sim 之间怎么分 |

---

## 8. 收尾叙事（对 Cruise 出身面试官，英文版，60 秒）

> "I treat a home-robot fleet as a close cousin of an AV fleet. On-device triggers and shadow eval decide what gets uploaded. Every teleop intervention is a disengagement: it enters a triage funnel — dedup and cluster, rank by severity times frequency, attribute root cause, and use counterfactual replay or a world model to decide whether it's really a policy deficiency. Every event becomes a permanent regression test. A miner searches the fleet for lookalikes and spins up targeted collection campaigns. On the training side, mixture weights and dedup — the Re-Mix and SCIZOR playbook — control the distribution, and the budget buys environment and object diversity, not more demos in the same kitchen. On privacy I'd follow the 1X template — per-session consent, no-go zones, edge redaction, employed operators — and include the labeling supply chain in the threat model, because that's where iRobot got burned. And I'd run the whole line on demos per hour, QA yield, the coverage matrix, flywheel cycle time, and marginal success rate per hundred demos."

---

### 速记卡（面试前 5 分钟扫一眼）

- 数字：221 triggers / 10k clips 一周 auto-label / π0 = 10k h·903M steps·7 构型·68 任务 / π0.5 ~100 环境 / Helix 500 h / Figure 10→60h ⇒ 88→95% / 20–40 demos/h / $118–136 per hour / $1–10 per demo / NEO $20k / Waymo 30k→60k mi/disengagement
- 词：shadow mode · trigger campaign · CLM · miner · triage funnel · severity×frequency · counterfactual replay · necessary vs unnecessary takeover · Road-to-Sim · Morpheus · Fleet Response · Content Search · farm-to-table data · social contract · no-go zones · RECAP coaching · Re-Mix · SCIZOR · coverage matrix · intervention rate · $ per point of success rate
