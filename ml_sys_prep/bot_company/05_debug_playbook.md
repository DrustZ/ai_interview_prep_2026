# 05 — Debug Playbook：「The bot is not working」排查手册

> 面试官考这题不是要答案，是要看：**结构化思维、假设驱动、数据优先、软硬件都碰、先问再查**。
> 这份手册的用法：背熟第 1 节的英文示范回答 → 把第 2 节的六层栈画成能默写的白板图 → 第 4 节的 cohort 决策表是 senior 区分度所在 → 第 6 节的追问话术至少背两条。

---

## TL;DR — 只有 20 分钟就看这段

1. **开口先问 5 个问题**，别急着答："not working" 具体什么现象（不开机/不动/行为错/间歇）？**一台还是多台**？突发还是渐变？**最近改了什么**？有安全风险吗？
2. **一台 vs 一批是最大的分叉**：单台 → 硬件/个体配置优先；一批同时挂 → 软件版本/OTA/配置/环境优先。漏问这个直接掉一档。
3. 白板画 **6 层栈**：L0 电源硬件 → L1 固件驱动 → L2 中间件(ROS 2/时间同步) → L3 经典自主栈 → L4 ML policy → L5 云/网络/OTA/配置。任何一层坏了都可能表现成"机器人变笨"。
4. 核心方法：**逐级看数据流在哪一层开始错**（raw sensor → perception → localization → plan → command → actuator feedback，Foxglove 回放叠加看）。
5. 两个二分工具：硬件用 **swap test**（换件看故障跟人走还是跟件走）；软件用**版本回滚/录制输入喂新旧版本 diff 输出**。
6. 每个假设写成**可证伪预测**再去验证（"若是热降额，则故障只应出现在连续运行 >30min 且电机温度 >80°C 时"）。
7. 区分「模型变笨 / 硬件坏了 / 环境变了」靠 **cohort 切片**（机器 ID × 模型版本 × 站点 × 时间段）+ 时序与 OTA 事件对齐 + **反事实回放**（旧模型跑新数据）。
8. 最干净的一刀：**canary rollout 自带对照组**——"环境 vs 模型"的争论直接消失。
9. 收尾必须闭环："修好"的定义 = 同类故障下次会被**监控自动抓到** + 案例进 failure taxonomy 回灌数据引擎，而不只是这台机器好了。
10. 被问到不熟的硬件细节：**一句诚实 + 一句推理层面的回答 + 一句桥接到自己的强区**（telemetry 设计 / fleet 统计 / data engine），话术见第 6 节。

---

## 1. 完整英文示范回答（3–4 分钟，背诵版）

面试官问："A customer reports their robot is not working. Walk me through how you'd debug it."

下面这段约 480 词，正常语速 3.5 分钟。分了 5 个 beat，方便按段背；`[...]` 是给自己的舞台提示，不用说出来。

> **[Beat 1 — Clarify, ~45s]**
> Great question — let me start with a few clarifying questions before I touch anything, because the answers completely change where I look first.
> First: what does "not working" mean concretely? Is the robot not powering on at all, powering on but not moving, moving but doing the wrong thing, or failing intermittently? Those four are totally different problems.
> Second — and this is the most important question — is it **one robot or many**? If it's a single robot and its fleet-mates on the same software are fine, I lean hardware or per-unit config. If a whole cohort degraded at once, I lean software, OTA, or environment.
> Third: when did it start — sudden or gradual? Sudden points to a discrete event: a deployment, a collision, a power cycle. Gradual points to drift: calibration, wear, a dirty lens, a memory leak.
> Fourth: **what changed recently**? New model checkpoint, new firmware, new config, new site, new payload? "What changed" is the first question of all debugging.
> And finally: is there any safety risk? If so, I e-stop and take the robot offline first — and I **preserve the logs before anyone reboots it**, because a reboot can flush the on-device ring buffer.
>
> **[Beat 2 — Frame the stack, ~45s]**
> Say it's one robot, failing intermittently, started three days ago. My mental model is a six-layer stack: power and hardware at the bottom; then firmware and drivers; then middleware — ROS 2, time sync; then the classic autonomy stack — perception, localization, planning, control; then ML policy inference; and cloud, network, and config on top. A fault at any layer can present as "the robot acts dumb." So instead of guessing, I **trace the data flow level by level**: raw sensor streams, perception outputs, localization pose, planned trajectory, commanded actions, actuator feedback. I replay the recorded bag in a visualizer and find the **first level where the data goes wrong**. Everything below that level is suspect; everything above it is just downstream contamination.
>
> **[Beat 3 — Bisect, ~40s]**
> To localize fast, I use two binary-search tools. On the software side, **version bisection**: roll back just the model, keeping everything else fixed — or better, feed the same recorded inputs to the old and new versions offline and diff the outputs. On the hardware side, **swap tests**: move the suspect sensor to a healthy robot, and see whether the fault follows the part or stays with the robot.
>
> **[Beat 4 — Hypothesis discipline, ~30s]**
> Every hypothesis gets turned into a **falsifiable prediction** before I act on it. For example: if this is thermal derating, failures should only occur after thirty-plus minutes of continuous operation, with motor temps above eighty degrees. So I pull the temperature time series and check — I verify with data, one variable at a time, instead of trusting my gut.
>
> **[Beat 5 — Close the loop, ~40s]**
> And once I find the root cause, fixing this one robot isn't the finish line. I validate the fix with log replay plus a real-run regression, roll it out canary-first, and — most importantly — **add a monitor or alert so this failure class gets caught automatically next time**. My bar for "fixed" is: the fleet catches the next instance before a human notices, and the case goes into our failure taxonomy so it feeds the data engine.

**背诵优先级**：Beat 1 和 Beat 5 一字不差地背（开头定基调、结尾定层次）；Beat 2–4 记结构即可，现场展开。

---

## 2. 分层排查树（六层栈，白板默写版）

白板上从下往上画。每层记住 2–3 个典型故障 + 一句"怎么确认"。**判据**列 = 看到什么就能把嫌疑锁定在这一层。

### L0 电源与硬件（单机故障的第一嫌疑层）

| 部件 | 典型故障 | 检查手段 | 判据（确认信号） |
|---|---|---|---|
| 电池/BMS | 老化内阻上升 → 大电流瞬间 brownout 重启；单体不均衡触发保护断电 | 重启事件与电流尖峰做时序对齐；换已知好电池 | 重启时刻电压曲线瞬间跌破阈值；换电池后消失 |
| 电机/驱动器 | 过热降额（thermal derating）→ 扭矩不足、变慢，**无错误码** | 拉温度曲线；空载 vs 带载对比；读驱动器 fault register | 故障只在长时间运行/高温后出现，温度过 derating 阈值 |
| 编码器 | 磁环滑移/码盘脏 → odometry 漂移、控制抖振 | 手转关节对比读数；轮式 odom vs lidar/视觉定位残差 | 单侧残差系统性增大；手转验证读数不符 |
| 相机 | 进灰/脏污/水汽 → 图像变暗变糊；USB 带宽不够丢帧 | **直接看原始图像流（不是下游输出！）**；对比历史同场景 | 图像亮度/清晰度指标偏离该机自身历史基线 |
| IMU | 温漂、bias 跳变、震动饱和 | 静止读 bias；对比标称噪声谱 | bias 超标称范围；clipping 计数非零 |
| 连接器/线缆 | **微振松动——间歇性故障最常见来源** | wiggle test（边动线边看数据）；换线 | 掉线事件与振动幅值/特定姿态强相关 |
| 散热 | 风扇积灰停转 → SoC/GPU 热节流 → 全系统变慢 | `tegrastats`/`sensors` 看温度与当前频率 | throttling 事件计数 > 0，频率被压 |

**这一层的面试论点**：间歇性硬件故障靠 comprehensive logging + 与振动/温度/时间做相关性分析，以及 **swap test**——故障跟着部件走就是硬件，留在机器上就往上层查。

### L1 固件与驱动

| 典型故障 | 检查手段 | 判据 |
|---|---|---|
| 固件与驱动版本不匹配（部分 OTA 后） | 读版本号 vs manifest 比对 | 版本组合不在已测试矩阵中 |
| 设备枚举顺序变化 → `/dev/ttyUSB*` 错位、左右相机互换 | `dmesg`、`lsusb` 对比期望设备清单 | 设备路径与 serial number 映射错乱 |
| 驱动崩溃后 silent 不重启；CAN bus off | journalctl、`candump` 看错误帧 | 总线错误计数飙升 / 设备掉线事件 |

### L2 中间件（ROS 2 / pub-sub / 时间同步）

| 典型故障 | 检查手段 | 判据 |
|---|---|---|
| **QoS 不匹配（reliable vs best-effort）→ 消息静默不投递，无报错** | `ros2 topic info -v` 对比 pub/sub QoS | 拓扑连着但订阅端 hz = 0 |
| 多计算单元时间不同步 → TF extrapolation error、融合出"鬼影" | `tf2_monitor`、`chronyc tracking` | 某计算单元时钟偏移量级达数十~数百 ms |
| executor 饿死 / callback 排队 → 延迟累积 | `ros2 topic hz`、tracing 看 callback 时序 | 端到端延迟随 uptime 增长 |

### L3 经典自主栈（感知/定位/规划/控制）

| 典型故障 | 检查手段 | 判据 |
|---|---|---|
| **外参标定漂移**（振动/热胀/磕碰）→ 相机-lidar 投影错位、抓取偏移 | 可视化叠加投影；标定板复测 vs 出厂外参 diff | 投影错位肉眼可见；复测值超容差 |
| 定位跳变（特征贫乏区/地图过期） | 定位协方差时序；地图版本核对 | 协方差在固定区域规律性膨胀 |
| 规划器振荡/控制发散（新负载） | planner 失败原因码；控制跟踪误差 | commanded vs actual 误差在特定负载下发散 |

**这一层的核心动作**：把同一个 bag 逐级回放，在 RViz/Foxglove 里叠加看——**哪一级开始错，问题就在那一级与下一级之间**。

### L4 ML Policy 推理（ML 岗必被追问的层）

| 典型故障 | 检查手段 | 判据 |
|---|---|---|
| 模型 artifact 错：checkpoint hash 不符；TensorRT/ONNX 量化导出数值不一致 | 核对模型 hash + config；golden input 离线 vs 机上输出 diff | 同输入两端输出差异超数值容差 |
| **预处理不匹配**（归一化常数/resize 插值/通道顺序）——经典 silent failure | 录现场输入，离线复现整条预处理链 | 离线 eval 好、上机差，且 diff 定位到预处理输出 |
| 输入分布漂移（光照/场景/物体偏离训练分布） | 输入 embedding 的 OOD score / 与训练集距离 | OOD 分数上升**先于** success rate 下降 |
| 推理延迟尖峰 → 控制频率掉 → 行为变形 | p50/p99 延迟直方图；GPU 温度/利用率对齐 | p99 双峰，且与热节流/抢占事件对齐 |

**这一层的加分句**："Latency is part of the input distribution too — a policy trained at 30 Hz behaves differently when inference stutters, even if every individual output is correct."

### L5 云端 / 网络 / OTA / 配置

| 典型故障 | 检查手段 | 判据 |
|---|---|---|
| 配置下发错（错的 SKU 拿到错的参数） | diff 机上生效配置 vs 期望（config drift 检测） | cohort 切片只有某 SKU 中招 + diff 出差异项 |
| **半 OTA**：固件成、驱动包败 → 从未测试过的版本组合 | OTA 事件日志 + 全组件版本一致性自检 | 版本组合不在测试矩阵 |
| 证书过期 → 云连接静默失败；网络盲区打断 teleop | 云端 API 错误率；网络 RTT/丢包与位置热力图 | 故障与固定区域/固定时段强相关 |

---

## 3. 「一台 vs 一批」分叉逻辑

这是所有 clarifying questions 里权重最高的一个。问完立刻分叉：

| | **单台异常**（同版本同站点的其它机器正常） | **一批同时异常** |
|---|---|---|
| 先验指向 | 硬件个体差异、该机标定、机械磨损、个体配置 | 软件版本、OTA、配置下发、云端服务、（若同站点）环境 |
| 第一步 | 该机传感器健康指标 vs **自身历史基线**（图像亮度/IMU bias/电机电流曲线/推理延迟） | 画出受影响机器的**共同属性**：同模型版本？同固件？同站点？同 SKU？同时间点开始？ |
| 核心工具 | swap test（换件）、wiggle test、现场检查 | 故障开始时间与 **OTA/配置/flag 变更时间线对齐**；回滚验证 |
| 典型结论 | 镜头脏了、编码器滑移、电池老化、连接器松动 | 模型回归、配置错发、半 OTA、站点环境变更 |
| 面试话术 | "One robot, fleet-mates fine — I go hardware-first: check this unit's sensor health against its own historical baseline, then swap-test the suspect part." | "Multiple robots at once almost never means simultaneous hardware failure — I immediately align the incident start time against the deployment timeline: what shipped to exactly this cohort?" |

两个重要的次级分叉：

- **一批 = 同一站点的全部机器（跨软件版本）** → 不是软件，是**环境**（灯光/地面/布局变了）。去调该站点故障片段的图像人工看。
- **一批 = 同一新版本的机器（跨站点）** → 软件/模型回归。未升级的机器就是天然对照组。

加一句展示 fleet 思维："This is exactly why canary rollouts matter — if every release goes to 10% of robots first, the 'one vs many' question answers itself from the dashboard."

---

## 4. 模型变笨 vs 硬件坏了 vs 环境变了 — 数据区分法

Senior 区分度最高的一节。核心工具：**cohort 切片 + 时序对齐 + 传感器健康基线 + 反事实回放**。

### 4.1 Cohort 切片矩阵

把 success rate（或干预率/任务时长）按这些维度交叉切：

```
机器人 ID × 模型版本 × 固件版本 × 站点 × 时间段（日内/日间）× 任务类型
```

### 4.2 判别决策表（背下来）

| 证据模式 | 指向 | 下一步验证 |
|---|---|---|
| 只有 1 台掉，同版本同站点其它正常 | **硬件/个体** | 该机传感器健康 vs 自身历史基线；swap test |
| 升到新版本的都掉、未升级的正常，拐点与 rollout 对齐 | **模型/部署回归** | log replay 新旧模型 diff；回滚一台验证 |
| 某站点所有机器（跨版本）同时掉，其它站点正常 | **环境变了** | 调故障片段图像人工看；输入 OOD 分数 vs 训练分布 |
| 渐变下滑、无拐点、单机 | **漂移类**（标定/脏污/磨损/内存泄漏） | 与 uptime/日历时间做相关；"重启就好"→ 泄漏/热/时序 |
| 每天固定时段掉 | 日光/温度/网络高峰/排班 | 按 hour-of-day 切片；与环境时序叠加 |

### 4.3 具体例子（面试现场可以直接讲的 walkthrough）

假设 dashboard 显示 fleet 平均 success rate 一周内从 92% 掉到 84%（数字为示意）：

1. **按模型版本切**：v2.3 机器 91%，v2.4 机器 79% → 强烈指向新模型。但慢着——
2. **按站点切**：发现掉分的 v2.4 机器几乎都在 Site B，Site A 的 v2.4 机器只微降 → 混淆了！v2.4 恰好先发给了 Site B。
3. **反事实回放（最干净的一刀）**：把 Site B 失败时段的录制输入喂给旧模型 v2.3 离线跑——
   - 旧模型也失败 → 是**环境/输入**问题（去看图像：也许 Site B 换了地面/灯光）；
   - 旧模型能成功 → 是**模型回归**（v2.4 在 Site B 这类分布上退步了）。
4. **交叉证据**：Site B 的输入 embedding OOD 分数从上周三开始抬升，且抬升**先于** success rate 下降 → 环境指纹坐实。

英文版核心句（背）：

> "The cleanest cut is **counterfactual replay**: feed the failing period's recorded inputs to the old model offline. If the old model also fails, it's the environment or the inputs; if the old model succeeds, it's a model regression. And the cleanest prevention is a **control group**: canary rollouts make the 'environment vs model' debate disappear, because you always have a same-time, same-place comparison cohort."

### 4.4 让区分变容易的三个前置投资（主动提，展示系统思维）

1. **Per-device 健康基线**：每台机维护图像亮度/清晰度、IMU bias、编码器噪声、电机电流-速度曲线、推理延迟 p99 的历史基线，偏离 N σ 报警 → "硬件坏了"在 success rate 掉之前就被抓到。
2. **输入分布监控**：对 policy 输入做 embedding，监控 OOD score / 与训练分布距离 → "环境变了"的早期指纹。
3. **变更事件流**：OTA、配置、flag、地图更新全部进同一条 event timeline，任何指标图都能一键叠加变更竖线 → changepoint 与部署事件重合是最强信号。

---

## 5. Root Cause 案例卡（12 张，每张 3–5 行）

面试时的用法：主叙事讲完框架后，**主动挑 1–2 张卡讲全程**（推荐 #2 地毯 或 #1 标定漂移——同时秀硬件+ML+数据三种肌肉）；其余用于应对 "give me an example of..."。

**#1 相机-lidar 外参标定漂移**
症状：单机渐变，检测框与点云错位，抓取偏移 ~2cm。
路径：可视化叠加投影发现错位 → 标定板复测 → 与出厂外参 diff 超容差。
修复：重标定；长期上在线标定监控（在线失准检测 / 基于运动线索的漂移监控——面试说方法思路即可，别报具体方法名）。

**#2 地毯换了 → 输入分布偏移**
症状：某站点所有机器视觉 policy 成功率骤降，跨软件版本。
路径：cohort 切片锁定单站点 → 回看失败片段图像发现地面纹理全变 → OOD 分数确认输入偏移。
修复：采集新场景数据 fine-tune / domain randomization；流程上加客户环境变更报备 + 输入分布监控告警。

**#3 模型导出/预处理不一致**
症状：新模型离线 eval 更好，上机反而更差。
路径：录同一输入，离线 PyTorch vs 机上 TensorRT 输出 diff → 归一化常数/插值方式不一致（或量化掉点）。
修复：部署链路加"训练-部署数值一致性测试"（golden input 回归），进 CI。

**#4 推理延迟尖峰 → 控制变形**
症状：动作偶发顿挫，模型输出本身正确，成功率轻微下降。
路径：p99 延迟直方图双峰 → 与 GPU 温度对齐发现热节流（或同机进程抢 GPU）。
修复：散热/进程隔离/延迟预算监控；policy 侧加延迟鲁棒性测试。

**#5 内存泄漏 → 延迟累积**
症状：运行数小时后变卡、偶发 watchdog 重启；**"重启就好" = 泄漏类经典指纹**。
路径：故障率与 uptime 正相关 → 监控 RSS 增长 → heap profiler 定位泄漏节点。
修复：修泄漏 + 内存/延迟 p99 告警；临时按班次重启缓解。

**#6 多机时间戳不同步**
症状：TF extrapolation error、传感器融合出"重影"、planner 间歇性拒绝。
路径：`tf2_monitor` 看帧延迟 → `chronyc tracking` 发现某计算单元漂 200ms。
修复：修 NTP/PTP + 加时钟偏移监控告警。

**#7 DDS QoS 不匹配**
症状：升级后某订阅者永远收不到消息，**无任何报错**。
路径：`ros2 topic info -v` 对比 pub/sub QoS → reliable vs best-effort 不兼容。
修复：统一 QoS 配置 + CI 加 topic 连通性检查。"Silent failures need active monitoring."

**#8 连接器微振松动**
症状：传感器随机掉线数百 ms，只在高速/颠簸时发生，实验室复现不了。
路径：掉线事件与 IMU 振动幅值做相关性 → wiggle test 复现 → 锁定连接器。
修复：换带锁扣连接器/加固；长期记录总线错误计数以便早发现。

**#9 电池老化 brownout**
症状：老机器在电机大电流瞬间整机重启，冬天更频繁。
路径：重启时刻与电流尖峰对齐 → 电压曲线瞬间跌破阈值 → 换新电池后消失。
修复：换电池 + BMS 内阻/压降健康监控 + 老化预测性更换。

**#10 电机过热降额**
症状：只在下午/连续作业后"没力气"、变慢，**无错误码**（降额是静默的）。
路径：故障与运行时长/环境温度相关 → 电机温度曲线触发 derating 阈值。
修复：改散热/降占空比；把 derating 事件加入 diagnostics。

**#11 镜头进灰/脏污**
症状：单机数周内 success rate 渐降，无任何软件变更。
路径：图像亮度/对比度/清晰度 vs 自身历史基线偏离 → 肉眼看原始图确认。
修复：清洁 + 定检 SOP + 图像质量自动监控。"永远先看原始图，别只看下游输出。"

**#12 半 OTA / 配置错发**
症状：OTA 后少数机器异常，版本号看似正常（或：某 SKU 全体行为怪异）。
路径：细查发现固件更新成功但驱动包失败 → 从未测试过的版本组合；或 diff 生效配置发现拿到别的机型参数。
修复：OTA 事务化（全成或全回滚）+ 启动时全组件版本一致性自检 + config schema 校验与 drift 监控。

---

## 6. 追问应对：硬件深水区 → 体面地引回强区

LLM 背景的候选人在这题上真正的风险不是"不懂电机"，而是**在不懂的地方装懂**（马上被戳穿）或**直接卡死**（显得只会软件）。正确姿势是一个三步公式：

> **Acknowledge（一句诚实）→ Reason（用第一性原理给推理层面的答案）→ Bridge（引到 telemetry/fleet 统计/data engine，在强区展开）**

诚实那句要**短且不卑微**——一句带过，不要道歉三次。Bridge 要**自然增值**，不是逃跑：你引过去的方向必须对解决当前问题真的有用。

### 场景 A：追问电机/电气细节（"How exactly would you diagnose the motor driver?"）

> "I'll be upfront: my hands-on depth is on the ML and data side, so for component-level electrical diagnosis I'd pair with the hardware team rather than pretend. But here's how I'd reason about it: I'd want commanded-versus-actual torque and velocity, motor current and temperature time series, and the driver's fault registers — because most of what looks like a 'broken motor' is visible in telemetry before you touch a screwdriver: thermal derating shows up as failures correlated with runtime and temperature, a dying driver shows up in the current signature. And that's actually where I'd add the most value: making sure **every robot ships with the telemetry that lets a hardware engineer diagnose this remotely** — per-device current-vs-velocity baselines, derating events in diagnostics, alerts when a unit deviates from its own history. That turns a field visit into a dashboard query."

### 场景 B：追问标定/运动学数学（"Walk me through the extrinsic calibration math."）

> "I know it at the level of: extrinsics are the SE(3) transform between sensor frames, drift shows up as reprojection error, and you re-estimate it from correspondences — but I haven't implemented a calibration pipeline myself, so I won't fake the details. What I *have* thought hard about is the **systems question around calibration**: how do you know, across a fleet, *which* robots have drifted, *before* their success rate drops? That's a monitoring problem — track reprojection-error-style consistency metrics online, baseline them per robot, alert on drift. There's published work on online miscalibration detection with very high accuracy. I'd rather catch drift with a fleet-wide monitor than with a technician's quarterly checkup."

### 场景 C：追问嵌入式/RTOS/CAN bus（"What would you look at on the CAN bus?"）

> "Honestly, embedded is the layer where I'd lean on teammates most — I know it at the level of: check error frame counts, bus-off events, and whether device dropouts correlate with vibration or specific poses, which is how you catch the classic loose-connector intermittent fault. What I can bring to that layer is the **statistical side**: intermittent hardware faults are brutal to catch one robot at a time, but trivial to catch in aggregate — if you log bus error counts fleet-wide, the flaky units jump out of the distribution long before anyone files a ticket. I care a lot about designing logging so that hardware engineers get that signal for free."

### 场景 D：面试官顺着 Bridge 问"那你会怎么设计 telemetry？"（这是你的主场，要能立刻接住并往深打）

准备一个 60 秒的迷你答案：

> "Three tiers. **Tier 1, always-on low-rate health**: temperatures, voltages, clock offsets, topic rates, inference p99, restart counts — cheap enough to stream continuously, baselined per device. **Tier 2, event-triggered flight recorder**: a continuous on-device ring buffer of full sensor and internal state, uploaded only around triggers — anomalies, low-confidence detections, planner interventions, human takeovers — which cuts storage by 90%+ while keeping every interesting moment replayable. **Tier 3, the change-event stream**: every OTA, config push, flag flip, and map update in one timeline, so any metric chart can be overlaid with deployment markers. Then the triage loop: auto-tag and cluster incoming events into a failure taxonomy, fix the biggest cluster first, and feed the failure data back into training and eval sets — that's the data engine."

### 通用桥接句备用（任何硬件深水区都能用）

- "That's exactly the kind of question where I'd want the answer to come from **fleet data rather than intuition** — let me describe what I'd measure."
- "I'd rather be honest that my depth there is limited — but the reason this failure class is hard is that it's **intermittent**, and intermittent problems are fundamentally a **statistics problem**, which is my home turf."
- "One robot's mystery is a fleet's histogram."（这句可以当金句收尾）

### 反面清单（不要做）

| 不要 | 因为 |
|---|---|
| 编造具体硬件参数/操作细节 | 面试官往往就是硬件出身，一戳就穿 |
| 说 "I don't know" 然后停住 | 等于放弃这道题的一半分 |
| 桥接太急（问题没答就跳走） | 显得在逃避；先给推理层面的实质内容再桥 |
| 连续道歉/过度铺垫 | 一句诚实就够，多了显得不自信 |

---

## 7. 收尾 checklist（答题最后 60 秒必须覆盖）

1. Root cause 确认（不是 symptom 消失）。
2. 修复验证：sim/log replay 回归 + 实机验证。
3. 灰度重新发布（canary → fleet）。
4. **加监控/告警：同类故障下次自动被抓**。
5. Postmortem 进 failure taxonomy；失败数据回灌训练/测试集（data engine 闭环）。

四句可直接引用的加分话术：

- "Intermittent, and a reboot fixes it? First suspects: leaks, thermal, timing."
- "QoS mismatches fail silently — connectivity needs *active* monitoring, not just error logs."
- "Latency is part of the model's input distribution."
- "My definition of 'fixed' is that the next occurrence gets caught by a monitor, not by a customer."

三个避坑提醒：不要开口就"I'd check the logs"（太泛）；不要只讲软件不讲硬件；**永远不要漏问 "one robot or many?"**。
