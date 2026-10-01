# 01 — The Bot Company 公司情报（Company Brief）

> 事实来源：2026-08-08 调研简报（官网/Ashby API/Wayback/媒体报道）。凡简报未覆盖的一律不写；单一来源或推测的标注 ⚠️ 或（未证实）。技术考点分析是我自己的推断，标注为【考点推断】。

---

## TL;DR — 只有 20 分钟就看这段

1. **一句话**：The Bot Company（bot.co，下称 Botco）在做「a helpful robot for every home」——**非人形、轮式/履带底盘 + 机械臂**的家用机器人，至今 **0 产品、0 收入、0 公开 demo**，估值 **$4B+**（⚠️ 最后一轮 close 未见正式 PR）。
2. **三个数字**：累计融资 **~$552M**（$150M@$550M → $150M@$2B Greenoaks → $250M@$4B+ Eclipse）；团队 **~79–94 人**（目标永远 <100 人、95% 工程师）；在招 **9 个岗位**，全部 SF onsite，$200K–$350K。
3. **创始人**：Kyle Vogt（CEO，Twitch + Cruise 创始人，2023/11 因 Cruise 拖行事故后离职）；Paril Jain（CTO，Tesla FSD **Planning, Imitation Learning & RL** tech lead）；Luke Holoubek（前 Cruise 工程师）。
4. **技术路线（有证据）**：端到端神经网络 + imitation learning，抛弃经典 CV/规划栈；**明确拒绝入户 teleoperation**（隐私 + 不可扩展）；靠 in-home 部署 + fleet learning + OTA 回灌数据——Cruise/Tesla 的 fleet 思路直接移植。
5. **三层技术栈（JD 确证）**：VLA 式 **Multimodal Foundation Models**（text/image/video/kinematics 统一，含 post-training/RL）+ **World Models**（视频生成神经模拟器）+ **Whole-Body Control**（sim-to-real RL）。
6. **你面的 "MLO" 岗**：公开 JD 里**不存在**这个名字（⚠️ 内部叫法/未公开岗）。最对口的公开 JD = **Multimodal Foundation Models**（唯一写明 post-training 的岗）+ **ML Infra - Data Infrastructure**。备考按这两份 JD 的并集准备。
7. **产品哲学**：捆绑「一千件小事」（捡玩具、收包裹、清桌面，容错 90–99%），刻意回避洗碗/洗衣等高风险任务；"Most robots will be specialized, not humanoids"。
8. **数据侧的现实**（对 data collection 方向最重要）：加州合同工集体诉讼（2026-06 获集体地位，估计 "hundreds of employees"）+ Airbnb 秘密测试事件（~6 英尺原型、30+ 人轮班）⚠️ 强烈暗示存在**大规模线下人工数据采集/演示 operator 队伍**——「不做 teleop」指的是不进用户家，不等于不用人类演示数据。
9. **文化关键词**（JD 原文）：extreme sharpness、mental acuity、engineering curiosity、high performance mindset；全员 IC、radical ownership、「工程师离可部署机器人不超过 10 英尺」。
10. **面试策略一句话**：把自己讲成「能 own 整条 data → post-training → eval 链路的人」，用 LLM post-training 经验类比到 VLA，主动谈 data engine 和 fleet learning——这正好打在他们 JD 的 "Own the Training Loop End-to-End" 上。
11. **别主动提**：Cruise 拖行事故细节、Airbnb 诉讼、合同工诉讼——知道即可，问到再得体回应。

---

## 1. 公司速览卡

**一段话**：The Bot Company 由 Kyle Vogt（Twitch/Cruise 创始人）、Paril Jain（Tesla FSD 规划/IL/RL 负责人）、Luke Holoubek（前 Cruise）于 2024 年创立，总部 San Francisco，做面向每个家庭的通用家务机器人。形态是非人形轮式/履带底盘 + 机械臂（Reuters 援引 sources；Airbnb 房东目击 ~6 英尺高履带原型）。公司刻意保持 <100 人的全工程师精英团队，走「端到端神经网络 + fleet learning」路线，在没有任何公开产品的情况下两年半内融资约 $552M、估值 $4B+。

| 关键数字 | 值 | 来源可靠度 |
|---|---|---|
| 成立 | 2024（2024-05-13 出 stealth） | ✅ |
| 累计融资 | ~$552M（三轮） | ✅（Sacra 汇总口径） |
| 最新估值 | $4B+（2025-10 Eclipse 领投轮） | ✅报导在募；⚠️ close 无正式 PR |
| 全职员工 | ~79（Builtin）/ ~94（Sacra） | ✅ 两个口径 |
| 合同工 | 估计 "hundreds"（加州集体诉讼口径） | ✅ 诉讼文件转述 |
| 在招岗位 | 9 个，全 SF onsite，$200K–$350K | ✅ Ashby API 实抓 |
| 公开产品/demo | 0 | ✅ |
| 专利（assignee 检索） | 0 条 | ✅ 实查（⚠️ 可能壳公司申请） |
| 投资人（官网列表） | Greenoaks、NFDG、Spark、Eclipse、Kleiner Perkins、YC | ✅ |

---

## 2. 创始人卡片

### Kyle Vogt — Founder & CEO

| 项 | 内容 |
|---|---|
| 背景 | MIT CS/EE 辍学；2004 DARPA Grand Challenge、iRobot 实习；Justin.tv 联创 → **Twitch** 联创（2014 Amazon $970M 收购）；2013 创立 **Cruise**（2016 GM >$1B 收购），历任 President/CTO/CEO；**2023/11 辞职**（Cruise robotaxi 拖行行人事故 → 加州 DMV 吊销牌照 → 内部调查指领导层失职及隐瞒信息） |
| 技术侧重 | 自动驾驶全栈、硬件+软件产品化、消费级规模化 |
| 关键言论 | "We're building bots that do chores so you don't have to."（X, 2024/5）；"Most robots will be specialized, not humanoids"（Uncapped 2025-11）；"Robots will be cooking steaks in less than 5 yrs"；"I'm never going to sell a company again"（Cheeky Pint 2025-07） |

**如果他来面试，可能关心什么**【考点推断】：产品直觉和速度。他是「产品化 + 规模化」型创始人，大概率考察你能不能把 ML 工作对齐到用户价值和 shipping 节奏——比如「这个实验值不值得跑一周」「eval 数字涨了但用户感知没变怎么办」。也会压测 high performance mindset（Cruise/Tesla 式强度）。对他，少谈论文、多谈 ship。

**面试时怎么说（示范）**：
> "What draws me here is that you're treating the home robot as a fleet-learning problem, not a demo problem. My background is post-training and evals for LLM agents — the loop of 'deploy, collect failures, fix the data mixture, redeploy' is exactly the muscle I've built, and it transfers directly to robot policies."

### Paril Jain — Founder & CTO（技术面最可能的终面人）

| 项 | 内容 |
|---|---|
| 背景 | UPenn CS 硕士（2015–17）；F1tenth（自动驾驶赛车教学平台）联创；SRI International 机器人实习；Tesla ~7 年，最后是 **"Planning, Imitation Learning & RL team for Tesla AI" 的 tech lead/manager**（FSD 规划栈）；2024/5 离开 Tesla 创立 Botco。⚠️ 三方页面 "Head of AI" 等头衔口径不一，稳妥表述是 "AI tech lead/manager" |
| 技术侧重 | **Planning、Imitation Learning、RL** —— 与公司 end-to-end + IL 路线直接对应 |

**如果他来面试，可能关心什么**【考点推断】：他是 IL/RL 出身的 CTO，最可能深挖：(a) IL 的失效模式——covariate shift、compounding errors、DAgger 类修法；(b) 什么时候 IL 不够、RL 怎么接上（offline RL、RL fine-tuning on top of BC）；(c) data mixture 和 data quality 对 policy 的影响（Tesla 数据引擎思路）；(d) 你的 post-training 经验能否迁移到 action 模态。他会用追问检验 "deep intuition" 是真是假。

**面试时怎么说（示范）**：
> "I think of robot post-training the same way I think of LLM post-training: base model gives you priors, SFT on demonstrations gives you competence, and RL closes the gap on the long tail — except in robotics your 'preference data' is real-world success and your distribution shift problem is physical. The interesting part is designing the data engine so every fleet failure becomes a training signal."

### Luke Holoubek — Cofounder

| 项 | 内容 |
|---|---|
| 背景 | 前 Cruise 软件工程师，曾任 **Cruise CTO 的 technical advisor**。公开信息很少，无个人访谈 |
| 技术侧重 | 软件工程（细节未公开） |

**如果他来面试，可能关心什么**【考点推断】：信息太少，按「资深系统软件工程师」准备——工程质量、系统边界、你写的 pipeline 崩了怎么 debug。不要对他假装了解他的背景（没有可引用的公开事实）。

⚠️ 其他成员：The Org 提到 Ray Kwong（Ops/Finance）、Austin Marsh（Legal），可靠性一般。官方口径只有 "team from Tesla, Cruise, OpenAI, Google, Pixar"。

---

## 3. 融资 / 产品时间线

| 时间 | 事件 | 备注 |
|---|---|---|
| 2013–2023 | 前史：Vogt 创立并执掌 Cruise；2023/11 辞职 | ✅ |
| 2024-05-13 | 出 stealth + **Seed $150M @ $550M post**（Spark、Nat Friedman、Daniel Gross、Collison 兄弟等） | ✅ Forbes/Bloomberg。当时还在考虑人形等多种形态，计划用 Discord 式社区定制功能 |
| 2025-02/03 | No Priors 访谈；**$150M @ $2B post，Greenoaks 领投**（Reuters 独家）；Reuters 披露形态：non-humanoid、base + grips | ✅；累计 $300M |
| 2025-07 | Cheeky Pint 访谈：端到端路线、「一千件小事」、拒绝入户 teleop、"never sell again" | ✅ |
| 2025-10-28 | Bloomberg：**"set to raise" $250M @ $4B+，Eclipse 领投** | ✅ 报导在募；⚠️ close 间接确证（官网已列 Eclipse/KP；Sacra 记 ~$552M） |
| 2025-11 | Uncapped 访谈："Most robots will be specialized, not humanoids"；<100 人哲学 | ✅ |
| 2025-11/12 | Ashby board 曾有 14 岗（含泛 ML、ML Platform、ML Compiler、Simulation、iOS、Full-Stack、Head of Supply Chain） | ✅ Wayback |
| 2026-02-25 | 泛 "Machine Learning" 岗下架，**拆分为 World Models / Multimodal FM / Whole-Body Control 三个专门岗** | ✅ Wayback + Ashby |
| 2026-04~06 | **Airbnb 秘密测试事件**：SF 房东起诉，目击 ~6 英尺履带原型（"borg from Star Trek, or a giant Roomba with treads"）、30+ 人轮班；7 月初原告撤诉（⚠️ 或和解） | ✅ 诉讼报道 |
| 2026-06-29 | **合同工集体诉讼获集体地位**：欠加班费/无午休等，估计 "hundreds of employees"；称公开亮相前两年已在用合同工 | ✅ SFist/Yahoo |
| 至 2026-08-08 | 无新融资、无产品发布、无 demo、无新访谈 | ✅ |

**时间线里的信号**【考点推断】：2026-02 的 ML 岗位「专门化拆分」+ Mechanical 岗要求对接 CM 做 volume manufacturing + 曾招 Head of Supply Chain/iOS → 公司从「找路线」进入「按定型架构扩建 + 备产」阶段。面试里可以用这个观察展示你研究过他们（见第 6 节清单）。

---

## 4. 技术路线信号

### 4a. 有证据的（可以在面试中直接引用）

| 信号 | 证据 |
|---|---|
| 端到端学习，抛弃经典 CV/3D 重建/运动规划栈 | Cheeky Pint："You don't need a robot that's repeatable, you need a robot that's adaptable, powered by neural networks" |
| **拒绝入户 teleoperation**（隐私 + 不可扩展）；end-to-end nets on near-raw sensor/motor signals | No Priors/Sacra 口径 |
| **Fleet learning + OTA**：in-home 部署数据回灌整个车队 | 访谈口径；Cruise/Tesla 思路移植 |
| LLM 做高层自然语言指令理解与行为指挥 | Cheeky Pint；The Rundown |
| **三层栈**：统一多模态基座（text/image/video/**kinematics**，含 pretraining/post-training/RL）+ 视频生成世界模型（neural simulator，multi-billion param）+ sim-to-real 全身控制（IsaacLab/MuJoCo、domain randomization） | ✅ 三份 ML JD 原文 |
| 数据基建目标：PB 级、数千机器，"from acquisition to improving autonomous capabilities" | ✅ Data Infra JD 原文 |
| Edge inference 优化是一等公民 | ✅ Multimodal FM JD："optimize performance for edge inference" |
| 非人形：轮式/履带底盘 + 机械臂；~6 英尺原型 | Reuters sources + Airbnb 目击；3D Vision JD 提 "wheel odometry" |
| 传感器栈含相机、IMU、轮式里程计、LiDAR；SLAM、NeRF/Gaussian Splatting 在招 | ✅ 3D Vision JD |
| 自研执行器 + 力控：FOC/PMSM/BLDC，固件与 ML 协作做 "force-sensitive, compliant control" | ✅ Firmware JD |
| 先做低风险「一千件小事」（容错 90–99%），回避洗碗/洗衣 | Cheeky Pint/Sacra |
| <100 人、95% 工程师、全员 IC、全员 onsite、离机器人 10 英尺内 | 访谈 + JD 模板 |

### 4b. 推测的（面试中要么不说，要么明确说是自己的推断）

| 推测 | 依据与置信度 |
|---|---|
| 上市前存在大规模线下人工数据采集（演示/操作 operator 队伍） | ⚠️ 中高置信：Airbnb 30+ 人轮班 + "hundreds" 合同工 + 「不做入户 teleop」只约束了用户家场景。具体是遥操作演示还是现场标注**未公开** |
| "MLO" 岗 = 内部未公开岗，职责 ≈ Multimodal FM 的 post-training 部分 + data engine | ⚠️ 推测：公开 JD 无此名；泛 ML 旧 JD 原文不可考 |
| 硬件规格：4-DOF 臂、<1kg 载荷、10L 收纳箱、可换末端执行器、sub-$10K、Matter/HomeKit 集成 | ⚠️ 低置信：仅 Sacra 重构，无一手来源，**当作没有** |
| 正在为量产做准备 | ⚠️ 中置信：Mechanical JD（注塑/压铸/MIM、volume manufacturing）+ 曾招 Head of Supply Chain |
| 有消费级 App | ⚠️ 中置信：2025-11 曾招 iOS/Full-Stack |
| 专利以壳公司名义申请或未过 18 个月公开期 | ⚠️ 纯推测：assignee 检索 0 条 |

**竞品格局**（✅ Sacra/The Rundown 汇总）：1X NEO（$20K 或 $499/月，2026 底交付）、Figure、Tesla Optimus、Sunday Robotics（$200M B 轮，Skill Capture Gloves 收了 1000 万条人类轨迹，2026 底 beta）、中国厂商（Galbot $350M、Unitree $13.5K 人形；电机/执行器成本优势 2–3 倍）。差异化记忆点：Botco 赌「非人形 + 专用形态 + 低风险任务捆绑」，vs 人形阵营赌通用形态。

---

## 5. 在招 JD 拆解（重点：你面的 ML/post-training/data 方向）

9 岗全景：3 个 ML 研究岗（World Models / Multimodal FM / Whole-Body Control，均 2026-02-25 上线）+ ML Infra Data / 3D Vision / System Software / Firmware / Mechanical / Something Else。全部 $200K–$350K、SF onsite。

**定位判断**【考点推断】：你面的方向（ML/post-training/data collection）最可能被按 **Multimodal FM 的 post-training 半区 + Data Infra 的 data engine 半区**考察。下面逐条拆。

### 5a. Machine Learning: Multimodal Foundation Models（核心 JD）

JD 定位原文："unified foundation models that natively reason across text, image, video, and kinematics to drive intelligent robotic policies... own the entire stack from data to training and deploying models."

| JD 原文要求 | 可能考什么【考点推断】 | 备考挂钩 |
|---|---|---|
| Build Native Multimodal Policies（vision/language/更多模态**共享统一表征**） | VLA 架构设计：action 怎么进 token 空间（discretized action tokens vs diffusion/flow head）；early vs late fusion；RT-2/OpenVLA/π0 一线的取舍；为什么 "native" 优于 adapter 拼接 | 03_robot_learning_crash_course |
| Improve Cross-Modal Reasoning（"doesn't just 'associate' modalities but actually reasons through them (e.g., grounding visual physics in kinematic constraints)"） | 怎么定义/测量 grounding：设计能区分「关联」和「推理」的 eval；embodied CoT；反例分析（模型看图说对话但动作违反运动学） | 03 + 05_debug_playbook |
| **Own the Training Loop End-to-End**（"design, run, debug, and iterate on large-scale training experiments; diagnosing failure modes, improving data mixtures, tightening evaluation"） | 这是**最高频考区**：讲一次你从数据到 eval 全 own 的训练项目；loss spike/训崩了怎么排查；data mixture 怎么调（上采样什么、按什么信号调权重）；eval 和真实表现脱钩怎么办 | 04_data_engine + 05 |
| Ship and Iterate on Real Systems + **optimize performance for edge inference** | 端侧部署：quantization（W8A8/W4）、distillation、action chunking 摊薄推理频率、控制回路延迟预算、异步推理 | 06_system_design_playbooks |
| Requirements: Python/C++/Rust 强编码 | 现场 coding 不会放水；C++/Rust 至少能读能改 | coding 练习 |
| **Production MLLM Experience**（训练+部署大规模多模态模型 track record） | 深挖简历：数据规模、GPU 规模、你个人的决策点和失败点；追问到细节见底 | 你的项目复盘 |
| **"Pretraining & RL Mastery: Deep intuition for LLM-style pretraining, post-training, and Reinforcement Learning at scale"** | 你的主场：SFT→RLHF/DPO/GRPO 全链路；reward hacking 与 eval 污染；RL for VLA 的特殊性（真机 rollout 贵 → offline RL / RL in world model / advantage-weighted BC）；scaling 直觉（数据 vs 参数 vs 算力） | 03 + 你的 LLM 经验 |
| Infrastructure Fluency（大 GPU 集群实验管理） | FSDP/TP/PP 选型、吞吐诊断（MFU、通信瓶颈）、实验管理纪律（多 run 对照、checkpoint 策略） | 06 |

### 5b. ML Infra - Data Infrastructure（data collection 方向的映射）

JD 定位原文："build the foundation of how our data flows **from acquisition to being used to improve the autonomous capabilities of our robots**."

| JD 原文要求 | 可能考什么【考点推断】 |
|---|---|
| data flows from acquisition → improve autonomy | 系统设计大题：**给家用机器人车队设计 data engine**——机器人端采什么/怎么过滤（带宽约束、on-device 触发器）、上传→ingestion→dedup→auto-label→curation→dataloader 的全链路；隐私处理（他们拒绝 teleop 的理由就是隐私，答题时必须主动覆盖 on-device 过滤/脱敏） |
| "production systems that process **PBs of data on thousands of machines**" | 分布式处理选型（Spark/Ray 类）、视频数据的存储格式与 IO（顺序读、分片、webdataset/parquet 类 tradeoff）、成本意识（PB 级冷热分层） |
| Python/Go/C++；cloud networking；K8s、ML serving 加分 | 工程细节追问：数据管道某环节挂了怎么保证 exactly-once/幂等；吞吐掉了怎么查 |

**data collection 运营侧**【考点推断，结合 ⚠️ 合同工背景】：可能考「怎么设计和 QA 一个几百人的人工演示采集运营」——任务 taxonomy、采集规范与工具、标注/演示质量指标、operator 间一致性、每条轨迹的单位成本 vs 边际模型收益。这正是他们的现实痛点（hundreds of contractors + Airbnb 式驻场测试）。面试中**不要**引用诉讼，只从方法论层面答。

**面试时怎么说（示范，data engine 开场）**：
> "I'd design it as a closed loop: on-robot triggers decide what's worth uploading — interventions, low-confidence actions, task failures — because at fleet scale you can't ship everything home, and for a home robot you also can't, for privacy reasons. Then ingestion, dedup, auto-labeling with a bigger offline model, and a curation layer that feeds the data-mixture decisions for the next post-training run. The metric I'd own is: time from a fleet failure to that failure appearing in a training batch."

### 5c. 另外两个 ML 岗（了解即可，用于展示全局观）

| 岗位 | 一句话职责（JD 原文要点） | 你需要能聊到的深度【考点推断】 |
|---|---|---|
| World Models | "neural simulators that understand the 'grammar' of the physical world"；video generation → controllable world models；multi-billion params | 知道 world model 在栈里的用途（policy 评估/RL rollout 的廉价替代、反事实模拟）；能聊 video gen 与 controllability 的 gap 即可 |
| Whole-Body Control | 仿真训 low-level policies；IsaacLab/MuJoCo；rewards & curricula；domain randomization sim-to-real | 知道高层 VLA 与低层 controller 的接口（action 空间切分、频率差异）；sim-to-real gap 的标准修法 |

### 5d. 全 JD 通用文化题

JD 模板原文三条硬标准："**Exceptional mental acuity**（think quickly, learn instantly, reason across unfamiliar domains）、**Engineering curiosity**（dig into how systems work even outside your specialty）、**High performance mindset**（move fast, handle ambiguity, excel when demanding）"。

【考点推断】对应行为面/压力面：陌生领域快速推理题（估算、跨栈 debug）、「你最近在专业外挖过什么系统」、快节奏高压环境的真实事例。回答基调：IC 心态、大 scope、不等指令。HCI 博士背景要主动框成优势（对「进家门的机器人」而言，人机交互与信任设计是稀缺视角），但主线必须是 hands-on ML 交付。

---

## 6. 面试中可自然引用的公司事实（≤10 条，英文短句）

用法：每条后面括号里是自然带出的场合。全部 ✅ 有据可查。

1. "You split the generalist ML posting into World Models, Multimodal Foundation Models, and Whole-Body Control back in February — that told me a lot about how the stack is organized."（聊岗位定位时）
2. "Paril's background at Tesla was planning, imitation learning and RL — and the end-to-end IL route here reads like a direct continuation of that."（聊技术路线时）
3. "Kyle has been explicit that most robots will be specialized, not humanoids — the wheeled-base form factor follows from that bet."（聊 vs 人形竞品时）
4. "You've publicly rejected in-home teleoperation on privacy and scalability grounds, which makes the data engine the interesting problem."（切入 data 话题时）
5. "The product thesis of bundling a thousand small low-risk chores — tasks that tolerate one-nine reliability — is a very different risk posture from the dishwashing demos."（聊产品/eval 标准时）
6. "The Data Infrastructure posting talks about PBs across thousands of machines — that's fleet learning at consumer scale, the Cruise and Tesla playbook."（聊 infra 时）
7. "You've kept the team deliberately under 100, roughly 95 percent engineers, everyone an IC — and engineers sit within ten feet of a deployable robot."（聊文化/为什么想加入时）
8. "Roughly $550 million raised across three rounds, with Greenoaks and then Eclipse leading, at a reported $4B-plus — all before any public demo."（聊公司阶段/信心时；注意 $4B 轮说 "reported"）
9. "The Multimodal FM role calls out grounding visual physics in kinematic constraints — making the model reason across modalities instead of just associating them."（聊你为什么对这个岗兴奋时）
10. "Kyle said robots will be cooking steaks in less than five years — I'm curious how the low-risk-first task ladder gets there."（收尾提问时，顺势抛出你的问题）

**反面清单（知道但别主动提）**：Cruise 拖行事故与 DMV 吊销细节；Airbnb 诉讼；合同工集体诉讼。若面试官自己提起，用中性事实 + 方法论回应，不评价。

---

## 附：一分钟自查（出门前过一遍）

- 公司口号？→ "A helpful robot for every home."
- 三位创始人 + 各自出身？→ Vogt（Twitch/Cruise）、Jain（Tesla planning/IL/RL）、Holoubek（Cruise）。
- 三轮融资数字？→ 150@550M → 150@2B（Greenoaks）→ 250@4B+（Eclipse，reported）。
- 三个 ML 岗？→ World Models / Multimodal FM / Whole-Body Control。
- 我面的方向对应？→ Multimodal FM 的 post-training + Data Infra 的 data engine（"MLO" 非公开岗名）。
- 他们最想听到的一句话？→ I own the loop from data to training to eval, and I move fast.
