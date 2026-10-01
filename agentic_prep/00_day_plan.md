# 00 · 作战日历（唯一主线，7/14–7/22）

⏱ 本文件 5 分钟读完 ｜ **每天只看当天那一节**，跟着走 = 自动覆盖本课程全部文件，不需要单独刷任何 section

规则：
- 每天格式固定：**面试前 30 min** → **主任务 ⭐⭐⭐** → **次任务 ⭐** → **砍时规则**
- 时间不够先砍 ⭐，绝不砍面试前 30 min
- 每天睡前 5 分钟做一遍[复盘六问](#复盘六问每天睡前-5-分钟)
- **刷题规则**：26 道 ⭐⭐⭐ 真题有[完整解答](05_questions/README.md#完整解答)（设计题 60 分钟走法 / coding 题可跑实现）——**先自己限时答，再对照解答查缺**，直接看解答记不住

---

## 7/14（今天）· Applied Compute 面试日 + 打地基

| 时段 | 做什么 |
|---|---|
| 面试前 30 min | [06 · Applied Compute 卡](06_company_briefs.md) + [08 · 一页纸](08_cheatsheet.md)扫一遍 |
| 若已面完 | 10 min 复盘六问，把被问倒的点记进 08 页边 |
| 主任务 ⭐⭐⭐（~2h） | [01_core 六篇](01_core/README.md)按 ⭐⭐⭐ 顺序通读：[loop+tools](01_core/01_loop_and_tools.md) → [state+memory](01_core/02_state_and_memory.md) → [reliability](01_core/05_reliability.md) → [eval+security](01_core/06_eval_security.md)，再补 [harness/SWE](01_core/03_harness_env_swe.md)、[multi-agent](01_core/04_multi_agent.md)；然后 [02 · playbook](02_playbook.md) 全文（40 min，重点：时间盒 + AI-coding 现场脚本） |
| 晚 ⭐⭐⭐ 备 Sierra（~90 min） | [06 · Sierra 卡](06_company_briefs.md) + 重读 [02 · playbook](02_playbook.md) 第八节 AI-coding 脚本 + 按 [07 · labs 指南](07_labs_guide.md)做 lab 02（codex repo review，Sierra 形式对口，限时 60 min） |
| 次 ⭐ | [05 · C 类真题](05_questions/C_live_ai_coding.md)浏览 Sierra 条目（C9–C14 电面/debugging 族 + C12/C13 官方形式） |
| 砍时 | lab 02 只做 starter 前半 + 读 solution diff；C 类只看题目不看打法 |

## 7/15 · Sierra 面试日（AI-native：Plan → Build → Review）

| 时段 | 做什么 |
|---|---|
| 面试前 30 min | [06 · Sierra 卡](06_company_briefs.md) + [08 · 一页纸](08_cheatsheet.md)的 AI-coding 四问 + 02 第八节脚本默背 |
| 主任务 ⭐⭐⭐（~2h） | [05 · C 类真题](05_questions/C_live_ai_coding.md)全部过完 + [05 · B 类](05_questions/B_general_design.md)过半（挑 ⭐⭐⭐）；[03 · rag](03_gaps/rag.md) + [03 · mcp](03_gaps/mcp.md) 两篇（各 15 min） |
| 晚 ⭐⭐⭐ 备 Hark（~60 min） | [06 · Hark 卡](06_company_briefs.md) + [03 · streaming](03_gaps/streaming.md)（computer-use agent 必涉及流式/中断） + [05 · A 类](05_questions/A_scenario_design.md)里 computer-use/浏览器条目 |
| 次 ⭐ | B 类剩余条目 |
| 砍时 | mcp.md 只读 30 秒版本和高分句；B 类推后到 7/16 |

## 7/16 · Hark 面试日（computer use 方向）

| 时段 | 做什么 |
|---|---|
| 面试前 30 min | [06 · Hark 卡](06_company_briefs.md) + [08 · 一页纸](08_cheatsheet.md)；口述一遍"click 成功但观察 timeout 怎么办" |
| 主任务 ⭐⭐⭐（~2h） | [03 · cost_latency](03_gaps/cost_latency.md) + [03 · scaling](03_gaps/scaling.md)（各 20 min）；[05 · A 类](05_questions/A_scenario_design.md)全部过完（含 Sora 编排、enterprise RAG 两道高频） |
| 晚 ⭐⭐⭐ 备双面日（~90 min） | [06 · Humans& 卡 + Extend 卡](06_company_briefs.md)；重读 [01_core · multi-agent](01_core/04_multi_agent.md) 和 [01_core · state+memory](01_core/02_state_and_memory.md)；按 [07](07_labs_guide.md) 做 lab 04（multi-agent memory，限时 45 min） |
| 次 ⭐ | 7/15 没读完的 B 类 |
| 砍时 | lab 04 改为只读 solution + RUBRIC；scaling.md 只读 30 秒版本 |

## 7/17 · Humans& + Extend + **Valkai（3:30 PM，live build）**三面日

| 时段 | 做什么 |
|---|---|
| 每场面试前 30 min | 对应[公司卡](06_company_briefs.md) + [08 · 一页纸](08_cheatsheet.md) |
| 场间 ⭐⭐⭐ | 重读 [01_core · harness/SWE](01_core/03_harness_env_swe.md)（Extend 的文档管线 = versioned artifact DAG）+ [03 · rag](03_gaps/rag.md) 高分句（Extend 必问检索/抽取评测） |
| **Valkai 前 30 min ⭐⭐⭐** | `../projects/valkai_agent/02_plan.md` 的 60 分钟时间轴 + walkthrough 讲稿默背；确认 git/uv/python/Claude Code + API key 就绪 |
| 晚 | 切换到 `../projects/takehome_mirendil/`（出本课程范围）；顺手 30 min 通读 [04 · benchmarks](04_benchmarks.md) 主表 |
| 砍时 | benchmarks 推到 7/18 |

> **7/16 晚加练**：用 `../projects/valkai_agent/` 的模拟题做一次 60 分钟全真干跑（Claude Code 驱动，计时），练完对照实现计划复盘。

## 7/18 · Mirendil take-home 日

agentic2 只占 30 min：[04 · benchmarks](04_benchmarks.md)（若 7/17 没读）+ [05 · D 类快问](05_questions/D_rapid_fire.md) 20 条自测（遮住答案）。其余时间全给 take-home。

## 7/19 · Anthropic 冲刺 ①（协议与 loop）

| 时段 | 做什么 |
|---|---|
| 主任务 ⭐⭐⭐（~2h） | 按 [07](07_labs_guide.md) **闭卷重写** lab 01 主循环（stock agent，55 min）；[05 · C 类](05_questions/C_live_ai_coding.md) Anthropic 条目（C1→C2→C4→C5→C6→C7）逐条口述打法；重读 [01_core · loop+tools](01_core/01_loop_and_tools.md)（tool-use 7 步必须能默写） |
| 次 ⭐ | [03 · agentic_rl](03_gaps/agentic_rl.md)（Anthropic 有 GRPO debug 轮记录）+ [03 · self_improvement](03_gaps/self_improvement.md)（Reflexion/技能库/trace→eval→RL 飞轮，Applied Compute 与 Anthropic 对口）+ 翻一眼 `../new/drills/04_grpo_ppo.py` |
| 砍时 | agentic_rl 只读 30 秒版本 + reward hacking 三例 |

## 7/20 · Anthropic 冲刺 ②（durable 家族）

| 时段 | 做什么 |
|---|---|
| 主任务 ⭐⭐⭐（~2h） | 按 [07](07_labs_guide.md) 做 lab 03（durable harness，对应 durable function cache 真题家族，70 min）；[05 · A/B 类](05_questions/README.md)里 Anthropic 条目重过（A5→A6→A7→A8 + B1）；重读 [01_core · reliability](01_core/05_reliability.md) |
| 次 ⭐ | [03 · mcp](03_gaps/mcp.md) 复习（Anthropic 生态）；lab 05（eval harness）没做过就补 |
| 砍时 | lab 03 只推演五个 crash point，不写码 |

## 7/21 · 总复习日

| 时段 | 做什么 |
|---|---|
| 主任务 ⭐⭐⭐（~90 min） | [08 · 一页纸](08_cheatsheet.md)**闭卷默写**（loop 五边界/failure 七类/eval 四层/高分句）；[05 · D 类](05_questions/D_rapid_fire.md) 20 条限时 10 min 自答；用 [02 · playbook](02_playbook.md) 追问模板连续口述：并行工具→重试→预算→注入→恢复→评估 |
| 次 ⭐ | 把 7/14–7/17 每天复盘记下的弱点，回到对应文件重读 |

## 7/22 · Anthropic 面试日

面试前 30 min：[06 · Anthropic 卡](06_company_briefs.md) + [08 · 一页纸](08_cheatsheet.md) + 白纸默写 tool-use 7 步与 loop 伪码框架。

## 7/23+ · 后续公司（OpenAI / xAI / Physion / Miru）

各家面试前一晚：[06 · 附录速记](06_company_briefs.md) 对应 5 行卡 + 该公司相关的 [05](05_questions/README.md) 条目。OpenAI 特别注意：agentic coding beta 轮 = existing codebase + 要求用 AI，直接复用 [02 · playbook](02_playbook.md) 第八节脚本。

---

## 复盘六问（每天睡前 5 分钟）

1. 我今天定义的 `done` 可执行吗？
2. 哪个决定应该是代码，哪个确实需要模型？
3. 最危险的 side effect 在哪里，谁有 authority？
4. 崩溃发生在最坏窗口时，如何恢复而不重复？
5. 我展示了测试/trace，还是只说"应该可以"？
6. 下一次最值得增加的 harness 能力是什么？

## 覆盖核对表（本课程所有文件 ↔ 日程）

| 文件 | 被安排在 |
|---|---|
| [01_core 六篇](01_core/README.md) | 7/14 主任务；7/16、7/17、7/19、7/20 定点重读 |
| [02_playbook.md](02_playbook.md) | 7/14 通读；7/15、7/21、7/23+ 复用 |
| [03_gaps 七篇](03_gaps/README.md) | rag+mcp→7/15；streaming→7/15 晚；cost+scaling→7/16；agentic_rl+self_improvement→7/19 |
| [04_benchmarks.md](04_benchmarks.md) | 7/17 晚（或 7/18） |
| [05_questions 四篇](05_questions/README.md) | C→7/14–15；A→7/15–16；B→7/15–16；D→7/18、7/21 |
| [06_company_briefs.md](06_company_briefs.md) | 每个面试日的前 30 min |
| [07_labs_guide.md](07_labs_guide.md) | lab02→7/14 晚；lab04→7/16 晚；lab01→7/19；lab03/05→7/20 |
| [08_cheatsheet.md](08_cheatsheet.md) | 每个面试日前 30 min；7/21 闭卷默写 |
