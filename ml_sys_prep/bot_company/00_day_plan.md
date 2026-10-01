# 00 — 冲刺计划与临场手册（The Bot Company Onsite, 2026-08-10 周一 13:00–17:00）

> 用法：这是整套资料（01–08）的总控文件。周日按 §1 的时间表执行，周一早上只看 §2。
> 事实纪律：关于 The Bot Company 的事实全部来自 01/02（公开面经为零，轮次配置是推断）。

---

## TL;DR — 只有 20 分钟就看这段

1. **战场判断**：4 小时 2–3 轮、可能提前结束 ⇒ 按**单轮否决制**打（02 推断），没有热身题。官方评分标准就三条（JD 原话）：mental acuity / engineering curiosity / high performance mindset。
2. **明天（周日）只干四件必保的事**：① 60 秒自我介绍 + Reflection S1 故事练到脱口而出（08）；② 05 的 480 词 debug 英文示范回答**出声练 2 遍**；③ 白板**默画一遍** 10k 台家用机器人数据采集 pipeline（04+06A）；④ 07 的 15 道 ★ 每道用英文说出开头两句。
3. **阅读顺序 = 被问概率**：08 → 05 → 04/06 → 03 → 07 → 01。不是从 01 顺着读。
4. **每个时段都要有输出**（说出声 / 画出来 / 写下来），纯阅读不算完成。
5. 时间不够的**砍单**（按序砍）：coding 手感练习 → 01 全文（只留 TL;DR + 10 条事实）→ 03 只读 §0 映射表 + quiz → 06 只保 A/C 两题。**绝不砍**第 2 条里的四件事。
6. **必背数字五个**：450 TB/天（10k 台全量回传，"neither feasible nor necessary"）；只传 2–5%；~905 trials/组才能检出 5pp 成功率差异（80%→85% 基线；引用时必须带基线，50%→55% 要 ~1,565）；50 trials 的 CI ±8pp（90% 成功率附近）；teleop glass-to-glass <100ms。
7. **万能兜底两招**：概念不会 → "Let me reason from the LLM analogy"（03 §0 映射表）；硬件不熟 → 一句诚实 + 一句推理 + 一句桥回 data/eval 强区（05 §6 话术）。
8. **临场总原则**：先 clarify 再答；每个论断落到参数/数字（Skild 哲学："hand-wave and you're done"）；把讨论主动引向 data engine / eval——那是你的主场也是他们 JD 的原话。
9. **地雷**：不主动提 Cruise 拖行事故、Airbnb 诉讼、合同工诉讼；不聊晋升/管理轨道（全员 IC）；不逼问产品形态；Reflection 讲方法不讲机密数字。
10. 周一上午**不学新东西**：只看 8 个 TL;DR + 15 道 ★ + 出声过一遍自我介绍和 debug Beat 1–2；12:15 前吃完轻午餐 + 咖啡因。

---

## §1 · 周日 2026-08-09 一日冲刺时间表

原则：上午练「必背输出」（记忆黄金期），下午过「体系与数字」，晚上收口成一页 cheat sheet。每块先读后练，练的部分不许跳。

| 时间 | 块 | 读什么 | 输出（验收标准） |
|---|---|---|---|
| 08:30–09:00 | 定调 | 本文件全文 + 02 的 TL;DR | 纸上默写：三条评分标准、三种轮次情景（A 50% coding+deepdive+founder / B 30% 长 practical / C 20% presentation） |
| 09:00–10:15 | **自我介绍 + 故事**（P0） | 08 全文（§1 逐字稿、S1/S3/S5、弱点预案、Why 三条、反问清单） | ① 自我介绍**计时练 3 遍**（55–70 秒，录音回听 1 遍）；② S1 故事讲 2 遍：一遍 5 分钟版、一遍 30 秒版；③ 弱点预案核心句出声 1 遍 |
| 10:15–10:30 | 休息 | — | — |
| 10:30–12:00 | **Debug playbook**（P0） | 05 全文（§1 背诵稿、§2 六层栈、§4 cohort 决策表、§6 追问话术） | ① 480 词示范回答**出声练 2 遍**（第一遍看稿、第二遍脱稿只看 Beat 提示）；② 白纸默画六层栈 + 「一台 vs 一批」分叉；③ 背 2 条 §6 兜底话术 |
| 12:00–13:00 | 午餐 + 散步 | — | 模拟周一同时段的进食节奏 |
| 13:00–14:30 | **数据引擎 + A 题**（P0） | 04 全文（若落后于计划：只读 TL;DR + §3 + §5 + §7）+ 06 的 §0 节奏模板和 A 题 | ① **白板画一遍完整数据采集 pipeline**（trigger 七类 → 边缘环形缓冲 + on-device 脱敏 → 上传 → curation → 训练 → eval → OTA），边画边用英文讲，压缩到 20 分钟；② 手写数字卡：450 TB/天、2–5%、demos/h、$/h |
| 14:30–14:45 | 休息 | — | — |
| 14:45–16:00 | **B/C/D 题 + eval**（P1） | 06 剩余部分（重点 C 题统计功效） | ① 用英文对墙讲 3 分钟「为什么 5pp 差异真机检不出、sim 承担统计功效」；② 数字卡补齐：905 trials、±8pp、<100ms/150ms/250ms、金丝雀 1%→5%→25%→100% |
| 16:00–17:15 | **速成课 + quiz**（P1） | 03 按 §2→§5→§3→§0→§1 顺序（§4 可跳，04 已覆盖） | ① **过一遍 §6 的 15 道 quiz**，错题标记回读；② Q19 映射表回答出声练 1 遍（"BC is SFT, interventions are the preference data…"） |
| 17:15–17:30 | 休息 | — | — |
| 17:30–18:30 | **题库总装**（P0） | 07 通读 52 题，精读 15 道 ★ | 15 道 ★ 每道**用英文说出前两句 hook**；卡壳的回源文件补；确认 Q48/Q49 两个 opinionated take 能各讲 90 秒 |
| 18:30–19:30 | 晚餐 | — | — |
| 19:30–20:15 | **公司事实 + 反问**（P1） | 01 全文 + 08 反问清单复看 | 手写 10 条公司事实卡（01 §6）+ 选定 3 个反问（首选："Given you've ruled out in-home teleop, what does the intervention signal look like…"）；过一遍地雷清单 |
| 20:15–20:45 | **coding 手感**（P2） | [labs/README.md](labs/README.md)（7 个可跑 lab 总索引） | 首选 **lab6 盲修 debug 演习**（计时，目标 15 分钟抓 4/5 个 bug）；有余力再做 lab5 的 skeleton 冷写。备选（无环境时）：不看参考手写一个 PyTorch 训练循环或 attention forward |
| 20:45–21:15 | 收口 | — | 做**一页纸 cheat sheet**（模板见 §1.1）；收拾周一物品（§2.2）；23:00 前睡 |

> 练代码扩容选项：若白天进度顺利能挤出 ~2 小时动手，按 [labs/README.md](labs/README.md)
> 的「周日只有 2 小时」路径执行：lab6 debug 演习 → lab5 冷写 → lab1 排查 → lab7 过一遍；
> lab2/3/4 以读代练（各 10 分钟读关键函数，当设计题的实现弹药）。

### §1.1 一页纸 cheat sheet 模板（周日晚亲手写，周一轮间只看这张）

- 三条评分标准 + "先 clarify 再答"
- 五个必背数字（450TB / 2–5% / 905 / ±8pp / <100ms）
- 六层栈六个词：power → firmware → middleware → autonomy → policy → cloud
- 自我介绍第一句 + S1 故事的四段式关键词（failure mode → 诊断 → data/eval 改动 → 量化增益）
- 兜底句两条（LLM analogy / 桥回强区）
- 3 个反问 + 地雷清单

### §1.2 优先级：时间不够砍什么

| 级别 | 内容 | 理由 |
|---|---|---|
| **绝不砍** | 自我介绍+S1（08）、debug 出声 2 遍（05）、pipeline 白板（04/06A）、15 道 ★（07） | 这四样覆盖三种轮次情景的开场和主菜 |
| 先砍 | 20:15 coding 块 | 已有基础，边际收益最低 |
| 再砍 | 01 全文 → 只读 TL;DR + §6 十条事实 | 公司事实用量小、密度低 |
| 再砍 | 03 → 只读 §0 映射表 + §6 quiz | 映射表是兜底工具，其余是背景 |
| 最后砍 | 06 → 只保 A/C 两题 | B/D 出现概率低于 A/C |

⚠️ 变数：如果 recruiter 今明两天让准备任何材料（slides），Tesla 式 presentation 情景升为第一（02 §判别信号）——当晚挪 90 分钟做 30 分钟 slides，从 S1 故事直接改。

---

## §2 · 周一 2026-08-10 onsite 当天

### §2.1 上午轻量复习（09:00–11:30，不学新东西）

| 时段 | 做什么 |
|---|---|
| 09:00–10:00 | 8 个文件**只看 TL;DR**（每个 5–7 分钟，按 08→05→04→06→03→07→02→01 顺序） |
| 10:00–10:40 | 07 的 15 道 ★ 当 flashcard：看题→出声说前两句英文→翻答案对照 |
| 10:40–11:10 | 出声过：自我介绍 1 遍（计时）+ debug Beat 1–2 一遍 + 弱点预案核心句 |
| 11:10–11:30 | 看自己的 cheat sheet 一遍，然后**合上所有材料** |

12:15 前吃完轻午餐 + 咖啡因（02 建议；避免 13:00 第一轮撞上消化低谷，16:00 低谷靠 snack）。

### §2.2 出发前 checklist

- [ ] 证件 ID；recruiter 邮件再确认一遍**地址、到达时间、联系人电话**
- [ ] 手机充满 + 充电宝；水瓶；snack（能量棒，给 15:00–16:00 的血糖）
- [ ] 纸质 cheat sheet 一页（轮间隙看，面试中不掏出来）
- [ ] 笔 + 小本（记下每轮面试官名字和聊到的点，反问和 thank-you note 用）
- [ ] 穿着：整洁 casual 即可（95% 工程师、全 IC 文化）
- [ ] 提前 20–30 分钟到楼下，提前 10 分钟进门

### §2.3 轮次间隙怎么调整（13:00–17:00，2–3 轮）

- 每个间隙固定 2 分钟例程：**水 + 4 次深呼吸 + 扫一眼 cheat sheet**，就这三样。
- **不复盘上一轮**。单轮否决制下复盘只产生焦虑不产生分数；上一轮答砸的点如果本轮又出现，就当作第二次机会重新答。
- 间隙 >5 分钟：去洗手间 + 吃两口 snack；16:00 前后必吃。
- 「提前结束」当**中性信号**处理——02 的推断是流程本来就弹性，情绪上不许解读。
- 每轮开场 10 秒记下面试官名字；结尾留 2–3 分钟用准备好的反问。

### §2.4 通用临场原则

1. **先 clarify 再答**——debug 题、设计题、甚至行为题都适用。开场句：*"Let me start with a few clarifying questions, because the answers change where I'd look first."* 这一步本身就是 mental acuity 的信号。
2. **每个论断落到参数和数字**。说 domain randomization 就要能说随机化哪些参数、什么范围；说 trigger 就说七类和 2–5% 上传率。Hand-wave 即挂。
3. **主动把讨论引向 data/eval 强区**。话术：*"I think the hardest part here is the data and eval loop — that's also where I've spent the most time. Want me to go deepest there?"* 把选择权给面试官，同时锚定主场。
4. **白板习惯**：先写标题和坐标/图例再动笔；边说边画不冷场；每个箭头标数据量级或协议；留白给面试官改；画完退一步用 30 秒总结数据流。
5. **不会的题两段式兜底**：先 *"I haven't worked hands-on with X, but let me reason from the LLM analogy…"*；硬件题再加一句桥接：*"…and regardless of the root cause, here's how I'd design the telemetry to catch it fleet-wide."*
6. **答完主动收尾**，不拖泥带水：*"That's my answer — happy to go deeper on any piece."*（自我介绍在 Decagon 讲了 11 分钟被打断的教训：这次严格 60–90 秒。）
7. Founder/culture 轮：聊 high agency、IC ownership、in-person、愿意下场碰硬件和跑 field ops；**不聊**管理轨道；"为什么家用机器人、为什么现在" 用 08 的三条真诚版。

---

## §3 · 文件索引（01–08）

| 文件 | 一句话 | 建议时长 |
|---|---|---|
| [01_company_brief](01_company_brief.md) | 公司全部可引用事实：融资/团队/技术路线/JD/文化关键词 + ≤10 条「面试时能说的事实」清单 | 30 min（砍到 10：只读 TL;DR+§6） |
| [02_interview_rounds_intel](02_interview_rounds_intel.md) | 面经为零的情况下的轮次推断：三情景概率、类比公司风格、单轮否决制结论 | 20 min（TL;DR 为主） |
| [03_robot_learning_crash_course](03_robot_learning_crash_course.md) | LLM→robotics 概念映射表 + VLA/π0/RECAP 速成 + 15 道自测 quiz——你的兜底武器库 | 60 min（砍到 25：§0+§2+§5+quiz） |
| [04_data_engine](04_data_engine.md) | 数据飞轮七步 + Tesla/Cruise/1X/PI 话语体系 + teleop 经济学数字——岗位核心文件 | 50 min |
| [05_debug_playbook](05_debug_playbook.md) | 「bot 不 work 了」的 480 词英文背诵稿 + 六层栈 + cohort 决策表 + 兜底话术 | 50 min（背诵另计） |
| [06_system_design_playbooks](06_system_design_playbooks.md) | 四道设计题（采集/训练部署/eval/teleop）标准解 + 45 分钟节奏模板 + 必背数字 | 60 min（砍到 30：A+C 两题） |
| [07_question_bank](07_question_bank.md) | 52 题总索引，15 道 ★ 带英文 bullet——最后总装和当天 flashcard 用 | 40 min |
| [08_stories_and_asks](08_stories_and_asks.md) | 60 秒自我介绍逐字稿 + S1/S3/S5 故事 + 弱点预案 + 反问清单 + 地雷 | 40 min（练习另计） |

阅读总量 ~5.5 小时（全读）/ ~3 小时（砍单版）；§1 时间表已把练习时间叠进去了。
