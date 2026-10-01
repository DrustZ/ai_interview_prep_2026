# 05_questions · Agentic 真题库

⏱ 约 5 分钟读完 ｜ 面试前只看目标公司的 ⭐⭐⭐ 行，点链接跳到对应题

汇编来源：9 个挖掘 agent 的产出（1p3a 缓存题库、hack2hire、官方博客、Exponent/PracHub/面经站）+ v1 题库（`../../agentic/data/questions.json`）吸收。共 **A/B/C 44 题 + D 类 20 条**。Applied Compute / Hark / Humans& / Extend 无公开面经（挖掘确证为空），用 🧪 推导题 + 对口 generic 题覆盖。

## 分类法

| 类 | 定义 | 文件 | 数量 |
|---|---|---|---|
| A | 具体应用场景设计题（绑定产品场景的 SD） | [A_scenario_design.md](A_scenario_design.md) | 16 |
| B | 泛化 agent 设计题（loop/memory/multi-agent/eval 平台） | [B_general_design.md](B_general_design.md) | 9 |
| C | live coding / AI-assisted coding 实操 | [C_live_ai_coding.md](C_live_ai_coding.md) | 19 |
| D | 概念快问（一行问 + 两句答） | [D_rapid_fire.md](D_rapid_fire.md) | 20 |

## 置信度规则

- ✅ **多源确认**：≥2 个独立来源家族（1p3a / reddit / glassdoor / blind / 官方博客互为独立；hack2hire 单独不算数）。例外：公司官方博客描述**自家**面试流程，视同 ✅（Sierra、PromptLayer）。
- ⚠️ **单源**：仅一个来源家族，题面可信但可能不完整或已轮换。
- 🤖 **hack2hire 未交叉验证**（该站约 86% 内容疑似 AI 生成）。本库所有 hack2hire 条目均已与独立来源合并升级为 ✅，当前无纯 🤖 条目。
- 🧪 **推导练习非真题**：按公司公开产品/JD 方向自拟，v1 带完整 rubric。
- 挖掘结果与 v1 吸收题重复的已合并为一条并升置信度；v1 吸收题在 details 末尾附 rubric 链接。

## ⭐ 优先级

⭐⭐⭐ = 本周面试公司（Sierra 7/15、Anthropic 7/22、Hark、Humans&、Extend、Applied Compute）的真题，及对口这些公司的 🧪/迁移题（表中标注）；⭐⭐ = generic/其他公司真题；⭐ = 低相关备查。

## 全库总表

| 题号 | 标题 | 公司 | 置信度 | ⭐ | 链接 |
|---|---|---|---|---|---|
| A1 | take-home：虚构公司客服 agent（5 选 2）+ onsite 演示 | Sierra | ✅ | ⭐⭐⭐ | [A1](A_scenario_design.md#a1) |
| A2 | 订阅取消 agentic 系统设计 | Sierra | ⚠️ | ⭐⭐⭐ | [A2](A_scenario_design.md#a2) |
| A3 | 文档自动化管线（银行材料/医生账单） | generic·Extend 对口 | ✅ | ⭐⭐⭐ | [A3](A_scenario_design.md#a3) |
| A4 | 保险理赔文档 agent | Extend | 🧪 | ⭐⭐⭐ | [A4](A_scenario_design.md#a4) |
| A5 | LLM Inference Batch API（含 100K RPS 变体） | Anthropic | ✅ | ⭐⭐⭐ | [A5](A_scenario_design.md#a5) |
| A6 | Prompt Playground 全栈设计 | Anthropic | ✅ | ⭐⭐⭐ | [A6](A_scenario_design.md#a6) |
| A7 | Design ChatGPT（SSE streaming 后端） | Anthropic/OpenAI | ✅ | ⭐⭐⭐ | [A7](A_scenario_design.md#a7) |
| A8 | 500GB 模型分发到 100–1000 worker | Anthropic | ✅ | ⭐⭐⭐ | [A8](A_scenario_design.md#a8) |
| A9 | Design Sora / GPU job scheduler | OpenAI | ✅ | ⭐⭐ | [A9](A_scenario_design.md#a9) |
| A10 | 企业级 RAG 聊天机器人（类 Glean） | OpenAI | ✅ | ⭐⭐ | [A10](A_scenario_design.md#a10) |
| A11 | 企业知识库 agent（官方 rubric；多租户/10M 变体） | generic | ✅ | ⭐⭐ | [A11](A_scenario_design.md#a11) |
| A12 | Design the OpenAI Playground（全栈） | OpenAI | ✅ | ⭐⭐ | [A12](A_scenario_design.md#a12) |
| A13 | Design Copilot / Perplexity | generic | ✅ | ⭐⭐ | [A13](A_scenario_design.md#a13) |
| A14 | PromptLayer 官方题单（白板+coding+take-home） | PromptLayer | ✅ | ⭐⭐ | [A14](A_scenario_design.md#a14) |
| A15 | 客服 agent 10K 工单/天 <2s | generic | ⚠️ | ⭐⭐ | [A15](A_scenario_design.md#a15) |
| A16 | 受限域三题族（银行/法律/医院） | generic | ⚠️ | ⭐⭐ | [A16](A_scenario_design.md#a16) |
| B1 | 能适应新任务的 agentic AI system | Anthropic | ⚠️ | ⭐⭐⭐ | [B1](B_general_design.md#b1) |
| B2 | ChatGPT 跨会话 memory | generic·Humans& 对口 | ✅ | ⭐⭐⭐ | [B2](B_general_design.md#b2) |
| B3 | 多人 + 多 Agent Shared Workspace | Humans& | 🧪 | ⭐⭐⭐ | [B3](B_general_design.md#b3) |
| B4 | Computer-use Agent Sandbox 与 Tool Harness | Hark | 🧪 | ⭐⭐⭐ | [B4](B_general_design.md#b4) |
| B5 | Enterprise Agent Eval Harness 与 Reward Hacking | Applied Compute | 🧪 | ⭐⭐⭐ | [B5](B_general_design.md#b5) |
| B6 | Eval 平台题族（50 workflows / GDM harness / 反馈闭环） | generic·AC 对口 | ⚠️ | ⭐⭐⭐ | [B6](B_general_design.md#b6) |
| B7 | 多 agent 委派系统 + 失败模式 | generic | ✅ | ⭐⭐ | [B7](B_general_design.md#b7) |
| B8 | Agent Tool-use System Design | TikTok | ⚠️ | ⭐⭐ | [B8](B_general_design.md#b8) |
| B9 | GDM Applied AI ML SD 官方考纲 | GDM | ⚠️ | ⭐ | [B9](B_general_design.md#b9) |
| C1 | 手搭 Claude agent loop（股票价格 tool use） | Anthropic | ✅ | ⭐⭐⭐ | [C1](C_live_ai_coding.md#c1) |
| C2 | Durable Function Call Cache（key + WAL） | Anthropic | ✅ | ⭐⭐⭐ | [C2](C_live_ai_coding.md#c2) |
| C3 | onsite AI-assisted coding 轮（Claude Code CLI） | Anthropic | ✅ | ⭐⭐⭐ | [C3](C_live_ai_coding.md#c3) |
| C4 | FDE 55min CodeSignal "build an agent" | Anthropic | ✅ | ⭐⭐⭐ | [C4](C_live_ai_coding.md#c4) |
| C5 | 线程安全 rate limiter（多级 follow-up） | Anthropic | ✅ | ⭐⭐⭐ | [C5](C_live_ai_coding.md#c5) |
| C6 | debug GRPO training loop（3 bug + ratio≠1） | Anthropic | ✅ | ⭐⭐⭐ | [C6](C_live_ai_coding.md#c6) |
| C7 | Applied AI 轨题族（retrieval scorer / token allocator / take-home） | Anthropic | ⚠️ | ⭐⭐⭐ | [C7](C_live_ai_coding.md#c7) |
| C8 | Weighted DataBatcher 确定性 checkpoint | Anthropic | ⚠️ | ⭐⭐⭐ | [C8](C_live_ai_coding.md#c8) |
| C9 | TS/React debugging round（禁 AI） | Sierra | ✅ | ⭐⭐⭐ | [C9](C_live_ai_coding.md#c9) |
| C10 | Markdown 按 header 层级分块 | Sierra | ✅ | ⭐⭐⭐ | [C10](C_live_ai_coding.md#c10) |
| C11 | Debug 日志区间合并 + overlap/gap | Sierra | ✅ | ⭐⭐⭐ | [C11](C_live_ai_coding.md#c11) |
| C12 | 官方 Plan→Build→Review（2h AI build） | Sierra | ✅ | ⭐⭐⭐ | [C12](C_live_ai_coding.md#c12) |
| C13 | 官方试点：draft PR + coding agents 改进 | Sierra | ✅ | ⭐⭐⭐ | [C13](C_live_ai_coding.md#c13) |
| C14 | 电面风格样本（循环引用 / keyboard undo-redo） | Sierra | ✅/⚠️ | ⭐⭐⭐ | [C14](C_live_ai_coding.md#c14) |
| C15 | 通用 AI-allowed live coding（1–2K 行 codebase） | generic·本周通用格式 | ✅ | ⭐⭐⭐ | [C15](C_live_ai_coding.md#c15) |
| C16 | agentic coding beta（现有 codebase + AI） | OpenAI | ⚠️ | ⭐⭐ | [C16](C_live_ai_coding.md#c16) |
| C17 | AI-enabled coding round（三面板） | Meta | ✅ | ⭐⭐ | [C17](C_live_ai_coding.md#c17) |
| C18 | Chatbot OOD 家族（ChatApp / refactor） | OpenAI | ✅ | ⭐⭐ | [C18](C_live_ai_coding.md#c18) |
| C19 | 看视频复刻流式聊天 UI | OpenAI | ✅ | ⭐⭐ | [C19](C_live_ai_coding.md#c19) |
| D1–D19 | agent 基础/eval/安全/memory 快问 | generic | ✅ | – | [D](D_rapid_fire.md) |
| D20 | agentic training 工具返回 mask | 快手（跨公司考点） | ⚠️ | – | [D20](D_rapid_fire.md) |

## 完整解答

26 道题已有完整解答（A11 与 A10 共用一份，共 25 个文件）——先自己限时作答，再对照解答查缺。

- **Sierra**：[A1 客服 agent take-home](solutions/A1_customer_agent_takehome.md) ｜ [A2 订阅取消](solutions/A2_subscription_cancellation.md) ｜ [C9 TS/React debugging](solutions/C9_debugging_round.md) ｜ [C10 Markdown 分块](solutions/C10_markdown_chunking.md) ｜ [C11 日志区间合并](solutions/C11_log_intervals.md) ｜ [C12 Plan→Build→Review](solutions/C12_plan_build_review.md) ｜ [C13 draft PR round](solutions/C13_draft_pr_round.md)
- **Anthropic**：[A5 Batch API](solutions/A5_batch_api.md) ｜ [A6 Prompt Playground](solutions/A6_prompt_playground.md) ｜ [A7 Design ChatGPT](solutions/A7_design_chatgpt.md) ｜ [A8 权重分发](solutions/A8_weights_distribution.md) ｜ [B1 自适应 agent](solutions/B1_adaptive_agent.md) ｜ [C1 股票 agent loop](solutions/C1_stock_agent_loop.md) ｜ [C2 Durable Cache](solutions/C2_durable_cache.md) ｜ [C4 build an agent](solutions/C4_build_an_agent.md) ｜ [C5 rate limiter](solutions/C5_rate_limiter.md) ｜ [C6 GRPO debug](solutions/C6_grpo_debug.md) ｜ [C8 Weighted DataBatcher](solutions/C8_weighted_batcher.md)
- **Extend**：[A3 文档自动化管线](solutions/A3_document_pipeline.md) ｜ [A4 保险理赔文档 agent](solutions/A4_insurance_claims_agent.md)
- **Humans&**：[B2 ChatGPT memory](solutions/B2_chatgpt_memory.md) ｜ [B3 Shared Workspace](solutions/B3_shared_workspace.md)
- **Hark**：[B4 Computer-use Sandbox](solutions/B4_computer_use_sandbox.md)
- **Applied Compute**：[B5 Eval Harness](solutions/B5_eval_harness.md)
- **OpenAI / generic**：[A10 企业级 RAG](solutions/A10_enterprise_rag.md)（A11 共用）

## 使用建议

- **7/15 Sierra 前**：C9→C10→C11→C12→C13→C14 + A1→A2，再扫 D 全部
- **7/22 Anthropic 前**：C1→C2→C4→C5→C6→C7 + A5→A6→A7→A8 + B1
- **Applied Compute / Hark / Humans& / Extend**：对应 🧪 题（B3/B4/B5/A4）+ 对口题（B2/B6/A3），配合 [../06_company_briefs.md](../06_company_briefs.md)
- 每题按 [../02_playbook.md](../02_playbook.md) 的 60 分钟节奏干练：澄清 5–7 min → 设计 10 min → 实现/展开 30 min → 测试复盘 10 min
