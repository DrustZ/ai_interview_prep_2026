# 06 — System Design Playbooks：四道 Robotics ML 高频题

> 你已经练熟 LLM 侧 system design（eval pipeline、RL data pipeline、serving 等）。本文只把力气花在 **robotics 特有的四件事**上：带宽受限的边缘采集、家庭场景 privacy、真机 eval 贵到改变统计设计、safety 与 ML 解耦。LLM 通用组件（Kafka、object store、model registry、dataset manifest）一律点到为止。

---

## TL;DR — 只有 20 分钟就看这段

1. **叙事主线：数据飞轮**。四道题是同一个闭环的四个切面——采集(A) → 训练部署(B) → 评估(C) → teleop 数据引擎(D)。面试中互相引用，显得体系完整。
2. **万能原则（四题都用）**：safety layer 与 ML 层解耦——本地硬安全（碰撞/力/速度限幅）不 OTA、不依赖网络、不信任 policy。这条原则回答了"怎么敢快速迭代"的所有变体。
3. **A 题 hook**：10k 台全量回传 = **450 TB/天**，"neither feasible nor necessary" → 必须触发式采集（干预、失败、高不确定性、安全事件、novelty、campaign、随机采样七类 trigger），只传 2–5% → 10–20 TB/天。
4. **A 题第二关键词**：privacy 必须 on-device 完成（人脸/PII 模糊后才上传），删除请求要能沿 episode→dataset→model lineage 穿透。
5. **B 题 hook**：机器人金丝雀的分桶单位是 **household 不是 request**，主监控指标是**干预率**（比成功率灵敏、累积快）；shadow mode（新 policy 只推理不执行）补小样本的坑。
6. **B 题回滚**：设备端 A/B 双分区，回滚 = 切分区重启，分钟级；只发完整签名镜像，拒绝 LoRA 热更的版本组合爆炸。
7. **C 题必背数字**：检测 80%→85% 成功率差异要**每组 ~905 次 trial**（α=0.05, power=0.8）；50 次 trial 的 CI 是 ±8pp。真机吞吐 100–200 trials/机/天 → **5pp 级差异物理上不可能靠真机检出** → sim 承担统计功效，真机只做校准 + 灾难性回归粗检 + 安全硬门。
8. **C 题省 trial 三板斧**：配对设计（同种子/同摆位）、sequential testing（TRI 的 STEP）、分层 + 多重比较校正。
9. **D 题必背数字**：glass-to-glass **<100ms** 可闭环抓取、**>150ms** operator 过度修正、**>250ms** 精细操作不可行。共享自治（operator 给子目标，本地 500Hz 闭环）是对延迟的**架构级**解法，也是 1:N 监督的前提。
10. **D 题控制通道语义**：最新状态覆盖 + 过期丢弃，绝不 TCP 式重放旧指令；watchdog 超时 → 冻结 → 自主退避。
11. **估算即设计**：每题前 10 分钟现场算数（带宽/存储/trial 数/延迟预算），用结论驱动决策——这是 robotics ML 题与普通 SD 题最大的区分点。
12. 45 分钟节奏：5 需求 / 5 估算 / 12 架构 / 15 深挖 / 5 tradeoff / 3 收尾，见下节模板。

---

## 0. 45 分钟答题节奏模板

| 时间 | 阶段 | 要点 |
|---|---|---|
| 0–5 min | 需求澄清 | 问 4–6 个问题锁 scope（用途优先级、规模、延迟/安全约束、现有资源）。主动说 "Let me assume X for now — happy to revisit."。**robotics 题必问：What's the physical cost of failure?** |
| 5–10 min | 数量级估算 | 现场算带宽/存储/trial 数/GPU-hours，**用估算结论驱动设计决策**（"450 TB/day is infeasible, so we must go trigger-based"）。 |
| 10–22 min | 高层架构 | 画端到端框图（边缘 → 传输 → 云端 → 训练 → 部署 → 监控闭环），先讲数据流再讲组件，每个箭头标协议/数据量级。robotics 题的通用骨架就是数据飞轮。 |
| 22–37 min | 深挖 1–2 个组件 | 主动说 "I think X and Y are the hardest parts — which would you like to go deeper on?" 把选择权给面试官，同时展示你知道难点在哪。深挖给**具体机制**（状态机、检验公式、缓冲策略），不是更多框图。 |
| 37–42 min | Tradeoff / 失败模式 / 演进 | 每个关键决策给出被否掉的替代方案及理由；2–3 个失败模式及降级路径；一句话讲 10 倍规模后什么先崩。 |
| 42–45 min | 收尾 | 30 秒总结 + 明说残留风险，留提问时间。 |

贯穿技巧：
- 每 10 分钟对齐一次："Does this direction work for you, or should I pivot to X?"
- 安全层与 ML 层解耦，四题通用，随时可以掏出来。
- 你练过的 LLM pipeline 直觉大部分可迁移（immutable data + manifest、registry 状态机、金丝雀放量）——面试时可以一句带过 "this part is standard data-infra"，把时间花在 robotics delta 上。

---

## Playbook A — 家用机器人 Fleet（1 万台）数据采集 + Telemetry Pipeline

### 可能的题干

> "Design the data collection and telemetry pipeline for a fleet of 10,000 home robots. We want to use fleet data to improve our policies, while also monitoring fleet health. Assume each robot has multiple cameras and runs a learned policy on-device."

### Clarifying questions（开场 5 分钟）

- "What's the priority: training data (episode-level, with action labels) or ops telemetry (metric-level)? They have very different SLAs — training data can be hours late, safety alerts need minutes."
- "What's the privacy model? These robots see faces, kids, screens inside homes. What did users opt into? Does GDPR/CCPA apply?"
- "What uplink can I assume? Home broadband upload is 10–30 Mbps and we can't hog the user's bandwidth — so realistically overnight/idle uploads only."
- "How much edge compute is left over after running the policy — can I run scoring/filtering models on-device?"
- "How many active hours per robot per day? I'll assume 2–4."

### 数量级估算（现场算给面试官看）

| 项 | 估算 | 推出的设计决策 |
|---|---|---|
| 单台原始视频 | 5 cam × 1080p30 H.265 ≈ 5 Mbps/路 → 25 Mbps ≈ 3 MB/s ≈ 11 GB/h；4h 活跃 → **~45 GB/天/台** | 不可能全传 |
| 本体感知 | ~30 关节 × (pos+vel+torque) × 500 Hz × 4B ≈ 200–500 KB/s → 压缩后 <2 GB/天 | 价值密度极高、体积可忽略 → **全量保留** |
| Fleet 全量 | 10k × 45 GB ≈ **450 TB/天** | 本题 hook："neither feasible nor necessary" |
| 触发式采集后 | 上传 2–5% 时间片 → 1–2 GB/天/台 → **10–20 TB/天 fleet → ~5 PB/年** | 热存 30 天 + 冷归档分层 |
| 标注吞吐 | 1 万条 30s clip/天，人工 60–100 条/人/时 → 15–25 人 | 或 auto-label + 人工抽检 10% |

面试时的说法：**"450 terabytes a day is neither feasible nor necessary. The interesting design question is not how to move the data — it's deciding on-device what NOT to upload."**

### 高层架构

```
[机器人] 环形缓冲区 (本地 NVMe 滚动 2-4h 全量录制)
   ├─ 触发引擎 (规则 + 模型, 可 OTA 更新) ──→ 事件切片 [-30s, +30s]
   ├─ on-device 预处理: 人脸/屏幕模糊, PII 过滤, H.265 压缩, novelty 打分
   ├─ telemetry agent: 指标 (1Hz 聚合) + 日志 → MQTT/gRPC 实时上报
   └─ 上传器: 夜间 Wi-Fi, 断点续传, 优先级队列 (安全事件 > 干预 > 常规)
[云端] API Gateway → Kafka →
   ├─ 实时流: 安全告警, fleet 健康 dashboard (时序库)
   └─ 批流: S3 + episode 元数据 (Postgres/数据湖)
        → embedding 索引 (视频帧 + 语言描述 → 向量库)
        → 去重/质量过滤 → 标注队列 (优先级) → dataset manifest
```

云端部分你全都熟（Kafka → S3 → manifest，跟 RL data pipeline 一个骨架），一句带过。**边缘侧才是这题的分数所在。**

**触发事件清单（要能一口气列出七类）**：
1. **人工干预/接管**——teleop correction 即带标签训练样本，最高价值数据（1X 的 teleop 数据飞轮模式）；
2. **任务失败**（重试、超时、放弃）；
3. **policy 不确定性高**（action 分布熵、ensemble 分歧、VLM confidence 低）；
4. **安全事件**（碰撞、力矩超限、急停、人闯入工作区）；
5. **新颖度**（场景 embedding 与已采集分布距离大）；
6. **云端下发 campaign**（Tesla shadow mode / AWS IoT FleetWise 模式："采集所有『开冰箱门失败』的片段"——条件下发全 fleet，边缘匹配后上传）；
7. **随机均匀采样**（小比例，对冲触发器自身的分布偏差）。

### 深挖组件 1：触发引擎 + 环形缓冲区

- **为什么必须环形缓冲**：失败发生时你需要失败*之前*的上下文。本地滚动保留 2–4h 全量，触发时切 [-30s, +30s] 窗口标记保留。
- **触发器可 OTA**：云端发现某类失败率升高 → 下发新 trigger 规则，不用等固件发版。
- **trigger 风暴防护**：监控每类 trigger 的 fire rate，每类每天限额——否则一个写坏的 trigger 会打爆上传队列和标注队列。
- 类比帮记忆：这就是 robotics 版的 "log sampling with head-based + tail-based rules"，但采样决策必须在边缘做，因为回传本身就是成本大头。

### 深挖组件 2：场景索引与检索

数据工程师要能查 **"all clips where the robot dropped a glass in a kitchen"**。方案三件套：
- 结构化元数据（任务 ID、房间类型、结果、干预标志）→ SQL 过滤；
- V-L embedding（CLIP/VLM 编码关键帧入向量库）→ 语义搜索；
- VLM 自动生成的文字描述 → 全文检索 + 后续 auto-label 的种子。

检索 = 结构化过滤 ∩ 语义搜索。这一层直接决定数据飞轮的转速——"we collected it but can't find it" 等于没采。

### Privacy 设计要点（家庭场景，必讲）

- 模糊/PII 过滤**必须在设备端上传前**完成，云端只见处理后数据；
- 分级 opt-in：仅 telemetry / 匿名化片段 / 完整视频；
- 卧室/卫生间地理围栏禁采；
- 用户可查看/删除自家数据，且 deletion 要能沿 **episode → dataset → model 的 lineage** 穿透到训练集（联动 B 题的 manifest 设计）；
- 加分项：主动提 1X NEO 当前的隐私争议（数据跨境、blanket consent、儿童数据无特别保护），说明你跟得上行业。

### 核心 Tradeoff

**数据覆盖度 vs 带宽/隐私成本**。触发式采集省 95%+ 带宽，但 **your triggers define your data distribution**——你只看得到你已知道要找的失败（selection bias）。缓解：小比例均匀随机采样 + campaign 机制 + 用便宜的全量 telemetry 指标发现盲区再定向采集。第二重：隐私模糊损失了人机交互研究需要的信息 → 按数据用途分级处理，不一刀切。

> **设计哲学**："On a bandwidth-starved fleet, the upload policy IS the data strategy — every trigger you write is a bet on what your model needs to learn next."

---

## Playbook B — Robot Policy Post-Training Pipeline（数据 → 训练 → 部署 → 回滚）

### 可能的题干

> "Design the end-to-end pipeline that takes fleet data, post-trains our robot policy, and safely ships the new policy back to 10,000 robots in homes — including how you'd catch a bad release and roll it back."

### Clarifying questions

- "What's the model? A 2–7B VLA running on-device, or cloud brain + distilled edge model? This decides OTA size and training cost."
- "Target release cadence — weekly or monthly? That decides how much eval must be automated."
- "Full fine-tune, LoRA, or action-head only? Delta size: tens of MB vs. several GB."
- "What's the cost of a bad release — a dropped cup or a hurt person? That sets gate strictness and canary size."
- "Any product/ethics constraint on A/B — is it OK for a paying household to get the worse policy?"

### 数量级估算

| 项 | 估算 |
|---|---|
| 数据增量 | fleet ~1 万条有效 episode/天（30s–2min）→ **~5,000 小时/月**演示+纠正数据（π0/GR00T 级 VLA 预训练在 ~1 万小时量级，post-train 每轮全量+增量） |
| 训练算力 | 3B VLA 在 ~10k 小时数据上微调：8–64 张 H100，1–7 天/轮，**数千到数万 GPU-hours，$10k–100k/run** |
| OTA | 3B fp8 ≈ 3 GB 完整镜像；LoRA/delta 几十–几百 MB；10k 台分波次 CDN 下发 |

### 高层架构

```
episode 存储 (immutable, 带 schema 版本)
 → 数据处理 DAG: 过滤/去重/auto-label/质量分
 → Dataset Manifest (内容寻址快照: episode ID 列表 + 处理代码 hash)
 → 训练 (config + manifest + commit 全入 registry, 可复现)
 → Model Registry: candidate→staging→canary→production→deprecated
 → Eval Gate (三级, 见 Playbook C): sim 套件 → 真机 eval cell → 安全场景 100% 硬门
 → 发布: 签名 → 量化/编译 (TensorRT) → 差分包 → OTA 服务
 → 金丝雀: 1% (内部 dogfood/员工家庭) → 5% → 25% → 100%
     每级最短观察期 + 自动晋级条件
 → 线上监控: 干预率, 分任务成功率, 安全事件率, 延迟/内存 → 异常自动 halt rollout
 → 回滚: 设备端 A/B 双分区 (Android seamless update 模式), 切分区重启, 分钟级
```

前半段（immutable episode + manifest + registry + 可复现训练）你在 LLM pipeline 里全练过，面试时一句 **"the data/training half is standard ML infra — immutable episodes, content-addressed manifests, full lineage in the registry"** 带过，把时间留给部署侧的 robotics delta。

### 深挖组件 1：数据版本化与 lineage（快讲，重点讲 robotics 用途）

数据集 = "manifest = episode ID 列表 + 处理代码版本"的虚拟快照，不复制数据。任何生产模型必须能回答：用了哪些数据、哪个 commit、哪组超参。robotics 特有的两个用途：
- **用户删数请求**沿 lineage 穿透（A 题 privacy 的下游义务）；
- **blast radius 分析**：某批坏标注/坏 teleop 数据污染了哪些模型 → 直接定位需要重训或回滚的版本。

### 深挖组件 2：金丝雀 + A/B 的机器人特殊性（本题分数所在）

与 web A/B 的四个不同，逐条讲：

| Web A/B | Robot fleet | 应对 |
|---|---|---|
| 按 request 分桶 | 按 **household** 分桶（同一家庭内切换 policy 会污染用户行为和环境状态） | randomization unit = household |
| 样本近乎无限 | 1% 金丝雀 = 100 台 × 每天几十个任务，检测 5pp 差异要累积数天（联动 C 题功效表） | 拉长观察期 + 换更灵敏指标 |
| 只能线上比 | 可用 **shadow mode**：新 policy 在设备上并行推理但不执行，比较其 action 与现行 policy/人工纠正的分歧（Tesla 验证 FSD 的核心手段） | 小样本下提前发现行为漂移 |
| 主指标 = 转化率 | 主指标 = **干预率**（比成功率更灵敏、更快累积；成功率作护栏） | 干预率异常 → 自动 halt |

可引用：AgiBot 2026 的 Learning-while-Deploying（fleet RL 的"部署↔共享经验↔改进↔再部署"闭环）是这套东西的学术版参照。

### 核心 Tradeoff

**发布速度 vs 安全置信度**。每级 gate 加严都拖慢迭代（真机 eval 全套数天），但家用场景一次伤害事件可能毁掉产品线。标准答案是**分层**：
- 安全性由本地、不可 OTA 的 safety layer 兜底（碰撞/力/速度限幅独立于 policy 版本、不信任 policy 输出）→ **买来了 policy 层快速迭代的权利**；
- 能力回归靠 sim 大规模 gate + 真机抽查 + 金丝雀慢速放量。

第二重：全模型 OTA（干净、可完整验证）vs LoRA/delta 热更（快、省带宽，但版本组合爆炸）。立场：**设备上只存在完整签名镜像 + A/B 双分区**，宁可多花 CDN 带宽也不要组合爆炸的调试地狱。

> **设计哲学**："A non-OTA safety layer is what buys you the right to ship policies fast — decouple what must never break from what must iterate weekly."

---

## Playbook C — Policy Evaluation 系统（sim + real + human 金字塔 & 统计功效）

这是四题里最"考数字"的一道，也最容易和你练过的 LLM eval pipeline 混淆——**区别只有一个但足够颠覆设计：real eval 太贵，贵到统计功效成为一等公民约束**。LLM eval 里你从不担心跑不够样本；这里每个 trial 是 2–5 分钟的物理动作加人工 reset。

### 可能的题干

> "Design an evaluation system that decides whether a new policy checkpoint is safe and better enough to ship to the fleet. You have simulators, a handful of real robots for eval, and human reviewers. How do you make this decision rigorous?"

### Clarifying questions

- "Are we evaluating a single-task policy or a generalist VLA? A generalist needs per-task × per-scene stratification — aggregate metrics hide single-task regressions."
- "How well does sim correlate with real today? Has anyone calibrated sim scores vs. real scores?"
- "How many dedicated eval robots and standardized scene cells do I have? Is reset manual or automated? Real-robot throughput is the bottleneck of the whole system."
- "Is the gate 'significantly better' or 'not significantly worse' — superiority vs. non-inferiority? That changes the statistical test."
- "Is safety evaluated separately? I'd argue the safety suite should be a 100% pass hard gate, outside the statistics."

### 数量级估算 — 统计功效（本题核心考点，背下来）

两比例 z 检验，α=0.05 双侧、power=0.8，检测差异所需**每组** trial 数：

| 基线 → 目标 | 每组 n |
|---|---|
| 50% → 55% | **~1,565** |
| 80% → 85% | **~905** |
| 90% → 95% | **~434** |
| 50% → 60% | ~387 |
| 80% → 90% | ~199 |

配套 CI 直觉（90% 成功率附近）：

| trials | 95% CI 宽度 |
|---|---|
| 50 | ±8pp |
| 70 | ±7pp |
| 200 | ±4pp |
| ~1,000 | ±2pp |

（NVIDIA 评估博客的例子：70 rollouts → 15.4pp 宽 CI；1030 rollouts → ±2pp。TRI 明确指出多数学术 benchmark 的 10–50 rollouts 根本不足以支撑"我的 policy 更好"——他们的例子：50 次里 25 成功 vs 29 成功，50% vs 58%，检验不显著。）

真机吞吐算术：一个 eval cell 每 trial 2–5 分钟 + reset → **100–200 trials/机/天** → 检测 80%→85% 需要 ~1,810 total trials ≈ **10 台 eval 机器人跑一整天**。当场推出结论：

**"So a 5-point improvement is physically undetectable on real robots as the primary instrument. The design consequence: sim carries the statistical power, real robots carry calibration and catastrophic-regression checks."**

### 高层架构：评估金字塔（下宽上窄，成本↑保真度↑）

```
L4  fleet 金丝雀/A/B (周级) ── 最终真值, 主指标=干预率 (联动 B 题)
L3  human review (持续) ──── 抽样视频评审, 抓"成功但行为怪异"
L2  真机 eval farm (天级) ── 数百–千 trials, 标准化 cell, 校准 sim + 验收 top candidate
L1  大规模 sim (小时级) ──── 数万 episodes, 域随机化 + 失败场景回放库
L0  离线指标 (分钟级) ────── action MSE/NLL, 只做 sanity check
```

- **L0**：与真实成功率相关性弱，只用于训练监控——等价于你熟的 "loss ≠ eval"，一句带过。
- **L1 sim**：绝对分不可信，但**相对排序 + 回归检测**在校准后可信。sim 是唯一能满足统计功效的层。
- **L3 human**：rubric 化打分抓成功率盲区（粗暴、低效、吓人的动作）；可 VLM-as-judge 预筛再人审——这半套你也熟。
- **L4**：联动 B 题金丝雀。

**降 trial 需求三板斧（深挖弹药）**：
1. **配对设计**：两个 policy 在相同初始条件/场景种子下各跑一次，McNemar/配对检验消除场景难度方差——sim 天然可控种子，真机用摆位模板；
2. **Sequential testing**：TRI+Princeton 的 **STEP** 框架（RSS 2025）边跑边检验、差距大提前停，配 Barnard exact test（小样本二项比较推荐）；后续工作声称再省 ~32% trials；
3. **分层 + 校正**：按任务分层报告，多任务比较用 Bonferroni/FDR，防"20 个任务总有一个假阳性回归"。

### 深挖组件 1：regression gate 的统计设计

- gate 设为 **non-inferiority test**：H0 = 新模型比旧模型差超过 margin δ（如 3pp），要求以 95% 置信拒绝。
- 分层落地：sim 上做严格 non-inferiority（n 够大）；真机只做"无灾难性回归"粗检（如 200 trials 检测 ≥10pp 掉落）+ 安全套件 100% 硬门（不进统计）。
- **校准回路**：定期用同批模型的 sim 分 vs 真机分拟合相关性，监控 sim gate 的预测有效性本身——sim 漂移了 gate 就静默失效，这是本系统最阴险的失败模式。

### 深挖组件 2：eval 场景库的策展

gate 质量 = 场景覆盖质量。闭环："fleet 失败数据自动挖掘 hard case → real2sim 重建为 sim 场景 → 进入回归套件"→ **线上失败永不复发**（联动 A 题的失败触发采集）。场景库要版本化：eval 套件本身变了，历史分数不可比 → 套件升级时新旧模型都重跑基线。

### 核心 Tradeoff

**统计严谨 vs 迭代速度/成本**。完全严谨的真机评估物理上不可达。答案不是放弃严谨，而是**把功效花在对的层级**：sim 承担大样本统计，真机承担校准和 spot-check，金丝雀承担最终判决；配对 + sequential 榨取每 trial 的信息量。第二重：单一聚合成功率 vs 分层指标——聚合掩盖回归，分层遭遇多重比较 → 明确主指标 + 护栏指标层级。

> **设计哲学**："When trials cost minutes of physical motion, statistical power is an architectural constraint — spend it where trials are cheap, and spend real robots only on calibrating that proxy."

---

## Playbook D — Teleoperation 系统（低延迟视频/控制 + 调度 + 安全接管）

### 可能的题干

> "Design a teleoperation system for our home robot fleet: operators in a central hub take over robots in customer homes — for recovery, and to generate training data. Cover the video/control links, operator scheduling, and safety."

### Clarifying questions

- "What's teleop for here — (a) fallback takeover, (b) the primary data engine (the 1X model), or (c) full-time remote operation? Scheduling and latency requirements differ."
- "What control granularity — 6-DoF end-effector following with a VR rig needs <150ms; click-a-target shared autonomy tolerates 500ms+. This one answer changes the whole design."
- "Network: home Wi-Fi + residential broadband with limited uplink and high jitter, operators in a central hub — correct?"
- "Privacy/compliance: operators are looking into people's homes. Per-session consent? Session recording and audit?"
- "What's the target operator-to-robot ratio, and peak concurrent takeovers?"

### 数量级估算

**延迟阈值（背下来）**：

| glass-to-glass | 后果 |
|---|---|
| <100ms | 可完成闭环抓取 |
| >150ms | operator 开始过度修正、信任下降 |
| >250ms | 精细操作基本不可行（遥操作研究的常见实测量级；具体文献出处未证实，别报作者名） |

**下行视频延迟预算分解**（面试时逐项写出来，这是硬功夫）：

| 环节 | 延迟 |
|---|---|
| 相机采集/读出 | 5–20ms（便宜 USB 相机 + USB 总线可能吃掉 ~100ms——**选型即架构**） |
| 硬件编码 | 10–30ms（低延迟 preset、零 B 帧） |
| 打包/协议栈 | 1–5ms |
| 网络传输 | 20–60ms |
| jitter buffer | 0–50ms（自适应，激进调小） |
| 解码 + 渲染 | ~10 + 10–20ms |
| **合计** | **可控实现 100–150ms；默认 WebRTC 栈往往 150–250ms** |

上行控制 ≈ 50–100ms（采样 1–5ms + 序列化 <1ms + 网络 20–60ms + 机器人侧插值 10–20ms）。**闭环总延迟 = 下行视频 + 上行控制 ≈ 200ms 上下，这才是体验的真实指标。**

其它数字：operator 侧 2–3 路视频 3–8 Mbps；10k 台 × 2% 并发 = 200 路 ≈ 1–2 Gbps 汇聚，SFU/中继集群轻松承载。人力（Erlang C 思路）：10k 台 × 3 次接管/天 × 3 分钟 = 1,500 机器人-小时/天 → 高峰几十到上百名 operator；目标从 1:1 向 **1:10 监督比**演进。

### 高层架构

```
[机器人] 相机 → HW 编码 (H.264/265 低延迟) →
   媒体通道: WebRTC/SRT/自研 QUIC-RTP, 自适应码率, FEC 优先于重传
   控制通道: 不可靠+带时间戳的"最新状态"语义 (过期指令丢弃)
             + 可靠通道 (模式切换/急停)
   本地安全层 (不经网络): 避碰, 力/速度限幅, 关节限位, 指令合法性校验
   watchdog: 心跳 200ms; 超时 500ms → 冻结; 超时 3s → 自主退避到安全姿态
[网络] STUN/TURN + 区域中继 POP (降尾延迟), QoS 标记, LTE/5G 备份链路
[运营中心] operator 工作站 (VR 或屏幕 + space mouse/外骨骼)
   调度器: 接管队列 (安全事件抢占 > 任务卡住 > 数据采集任务),
           技能路由, 会话录制 (审计 + 全部转训练数据 → 喂回 A/B 题)
[控制模式梯度] 直接遥操作 ←→ 共享自治 (operator 给子目标, 本地闭环) ←→ 监督确认
```

### 深挖组件 1：控制通道语义与延迟对抗

- **最新状态覆盖语义**：每包带序号 + 时间戳，机器人只执行最新且未过期的指令，绝不排队重放旧指令——**TCP 式可靠重传对实时控制是毒药**（重放 500ms 前的速度指令 = 事故）。急停/模式切换走单独的可靠通道。
- 抖动时机器人侧做指令插值/外推平滑。
- **共享自治是对延迟的架构级解法**：operator 发末端目标位姿或 "grab that cup" 级子目标，本地控制器 500Hz 闭环执行——把 200ms 网络延迟从控制回路里整个拿出去。这也是 1:1 → 1:N 监督的前提。面试金句：**"You can't beat the speed of light, so move the control loop onto the robot and let the human supervise at the level of intent."**

### 深挖组件 2：安全接管状态机

五态：`autonomous → takeover-requested → teleop-active → degraded → safe-stop`
- **degraded 触发条件**：单向延迟 >250ms 或丢包 >5% → 禁止精细操作、限速；
- **安全不依赖网络**：所有限幅/避碰在机器人本地执行，且**对 teleop 指令同样生效**——operator 也不能命令机器人打人（联动 B 题的 non-OTA safety layer，同一个组件）；
- **接管交接**：operator 接管瞬间看到的必须是 <200ms 新鲜的状态——基于陈旧画面操作比不接管更危险 → 接管前强制 2–3s 观察期；
- watchdog 心跳 200ms，超时 500ms 冻结、3s 自主退避。

Privacy：operator 看进用户家里是当前行业最大舆论风险点（1X 的争议）——逐次授权、会话录制审计、operator 屏蔽名单。

### 核心 Tradeoff

- **延迟 vs 可靠性/质量**：FEC vs 重传（实时控制选 FEC——恒定开销换零重传延迟）；jitter buffer 调小降延迟但花屏增加 operator 认知负担。
- **WebRTC vs 自研**：WebRTC 起步最快，但拥塞控制和 jitter buffer 不可深调 → 规模化团队普遍走向 QUIC/RTP 自研栈（业内常见判断，可当自己的观点说："WebRTC gets you to demo fastest, and breaks first when demo becomes deployment"）。
- **更高一层**：直接遥操作（数据质量高、动作自然，但受延迟限制且 1:1 占人力）vs 共享自治（抗延迟、1:N，但采到的数据不再是纯人类演示——喂给 BC 训练时要区分数据来源）。

> **设计哲学**："Latency you cannot eliminate, you must design around — keep the fast loop local, the human at the intent level, and safety independent of the network entirely."

---

## 附：一分钟串起四题（收尾/behavioral 联动用）

> "These four systems are really one flywheel viewed from four angles: the fleet collects triggered, privacy-scrubbed data (A); teleop turns every human correction into a labeled training sample (D); post-training turns data into candidate policies with full lineage (B); and a power-aware eval pyramid decides what ships, with a non-OTA safety layer underneath it all so we can iterate fast without betting the company on any single release (C+B)."

四题共用的三条原则，任何一题卡壳时都能退回来：
1. **估算驱动设计**——先算数，让"不可行"替你做决策；
2. **safety 与 ML 解耦**——本地硬安全不 OTA、不依赖网络、不信任 policy；
3. **触发/分层思维**——带宽、标注、真机 trial、operator 人力全是稀缺资源，一律"便宜的全量 + 昂贵的定向"两层结构。
