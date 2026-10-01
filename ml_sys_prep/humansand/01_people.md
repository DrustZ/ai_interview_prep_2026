# humans& 团队人物志（onsite 2026-08-10）

## TL;DR
- humans&（humansand.ai）：human-centric frontier AI lab，2025-09 成立，SF/Redwood City，~20 人（TechCrunch 2026-01，样本已旧），$480M seed @ $4.48B（SV Angel + Georges Harik 领投，NVIDIA/Bezos/GV 等）。
- 主线：multi-agent + long-horizon RL、memory、user understanding；产品是「AI 版协作/IM 层」，明确走 product-model co-evolution——和你 HCI PhD + post-training 的组合精准对口。
- 公开具名 9 人：6 研究 / 2 系统 / 1 商业向；浓重 HCI/认知科学味（Peng=human feedback、Ross=AI tutoring、Mireshghallah=privacy/memory、Goodman=pragmatics）。
- ⭐Reflection 校友：官网 founding team 背景列表与 TechCrunch 均明确含 "Reflection"，但**无任何公开具名**——建议今晚问 recruiter 或登录 LinkedIn 查 company people，别在现场猜名字。
- 最强连接点：Niloofar Mireshghallah（UW postdoc 2023-25，Yejin Choi/Yulia Tsvetkov 组，大概率与你同期在 UW CSE）+ 未具名 Reflection 校友。
- 技术栈证实（官方 Product Engineer JD）：Backend Convex (TypeScript)；Frontend Next.js、React Native (Expo)、Tailwind；MTS $350K + equity。

## ① 团队画像（样本 = 9 具名，全员 ~20，注意偏差：公开露面者偏研究侧）
- 构成：xAI、Anthropic、Google DeepMind、OpenAI、Meta、Reflection、AI2、Stanford、MIT（官网原文）。研究 vs 工程 ≈ 6:2（+1 商业），实际工程比例应更高（两个 MTS JD 都在招人）。
- 气质：frontier RL（NVFP4 异步 RL 博客、开源给 TransformerEngine/cuDNN/FlashInfer/SGLang）× 认知科学/HCI（导师链 Jacob Andreas、Noah Goodman）× 快节奏（多人「聊完周四、周一离职」入职）。
- 招聘口径："exceptional work at the frontier of modern AI"（研究）+ "thinking about how humans and computers interact"（产品）——后者几乎是为你的履历写的。

## ② 逐人卡片（按 1-1 概率排序）
### ⭐（未具名）Reflection.ai 校友 —— 1-1 概率最高的隐藏牌
- 官网 + TechCrunch 双证实团队含 Reflection 背景成员；公开搜索（LinkedIn 摘要/X/博客/GitHub org）均未找到名字（GitHub org HumansAnd 无公开成员）。
- 可能聊：Reflection 的 agentic RL / 大规模训练经历、为何转向 human-centric。
- Talking point: "I was MTS at Reflection — I'd love to compare notes on what carries over from autonomous-agent RL to training models that collaborate with humans."

### 1. Andi Peng — Co-founder（研究，Anthropic 系）
- MIT CSAIL PhD（Jacob Andreas & Julie Shah）→ Anthropic RL/post-training（Claude 3.5-4.5、behavioral RL）；MSR AI Resident、White House OSTP/DIU 政策经历。（来源：TechCrunch/Forbes/andipeng.com）
- 可能聊：human feedback、reward learning、post-training 如何塑造模型行为、product-model co-evolution（她在 TechCrunch 讲这条战略）。
- Talking point: "Your pragmatic-feature-preferences line is exactly the gap I hit doing post-training evals — human intent is underspecified, and I approached it from the HCI side."

### 2. Niloofar Mireshghallah — Founding MTS（研究，2025-11 入职）⭐UW 连接
- UCSD PhD（Berg-Kirkpatrick）→ **UW postdoc（Yejin Choi & Yulia Tsvetkov，2023-25）**→ Meta FAIR Alignment（2025.5-11）→ humans&；2026 秋入职 CMU 助理教授。方向：privacy/contextual integrity、LLM memory（CIMemories, ICLR'26）、unlearning。写了 "Why I Joined humans&" 博客（聊完周四、周一从 Meta 离职）。（来源：个人主页+博客）
- 可能聊：agent memory 的隐私边界、什么信息该在群组中流动（contextual integrity ↔ 他们的多人协作产品）。
- Talking point: "We overlapped at UW — and your contextual-integrity framing is the right lens for group-chat memory: who should the model remember what for, and in front of whom."

### 3. Alexis Ross — Founding researcher（研究，2025-11 入职）
- MIT CSAIL PhD（Jacob Andreas）；Harvard CS+Philosophy '20；AI2 两年 + MSR 实习。方向：adaptive AI tutors、学生 misconception 建模、counterfactual eval。写了 "Why I joined humans&" 博客。（来源：个人主页+博客）
- 可能聊：teaching/education 作为 human-AI collaboration 场景、如何建模用户认知状态。
- Talking point: "Modeling a student's misconceptions is a user-modeling problem — my HCI work on adaptive input systems hit the same challenge of inferring hidden user state from sparse signals."

### 4. Ziang Li — MTS（RL infra/量化）
- ex-NVIDIA DevTech、Google Gemini、CUHK-Shenzhen（GitHub zianglih，未证实细节）；官方博客《The 4-bitter Lesson》（2026-07）一作：NVFP4 异步 RL recipe，与 RadixArk(SGLang)/NVIDIA 合作开源；GPU MODE Lecture 110 主讲。（来源：官网博客/GitHub/YouTube）
- 可能聊：async RL 的 off-policy staleness × 量化误差权衡、rollout/trainer 解耦、per-token scaling。
- Talking point: "Your dequantized-backward trick is neat — I've fought the same policy-mismatch instability from the algorithm side in post-training; curious where you draw the line between recipe and algorithm fixes."

### 5. Eric Zelikman — Co-founder & CEO（终轮大概率见）
- Stanford PhD（Goodman 门下）→ xAI（Grok reasoning）；STaR/Quiet-STaR/Parsel 作者，Forbes 称其写了「第一篇教 LM 用自然语言推理」的论文。（来源：Forbes/TechCrunch）
- 可能聊：愿景层——为什么 collaboration 是下一个 frontier、如何评估「好的协作者」。
- Talking point: "STaR taught models to reason by bootstrapping their own rationales — I want to ask how you bootstrap *collaboration* signal, since my eval work says it's much harder to verify than correctness."

### 6. Yuchen He — Co-founder（研究）
- TechCrunch 称 ex-xAI（Grok），TechBuzz/Reuters 称 ex-OpenAI——来源冲突（未证实，可能两段经历都有）；方向：long-horizon & multi-agent RL。
- Talking point: "I'd love to hear how you define reward for multiplayer, dozens-of-steps rollouts — my agent-eval experience says credit assignment across humans is the hard part."

### 7. Ray Ramadorai — founding team（infra/系统）
- 曾负责 Microsoft 大型数据中心系统设计（Forbes）；大概率管 compute/集群。可能聊 training infra、H100/Rubin 集群、$480M 大头买算力（Crunchbase News）。
- Talking point: "Most of the seed going to compute means training efficiency is existential — the NVFP4 blog reads like that's already the culture."

### 8. Noah Goodman — Co-founder（Stanford 教授，兼职概率高）
- Stanford CS+Psych 教授；probabilistic programming、Rational Speech Acts（语用学）；曾参与 Gemini post-training（Forbes）。若遇到：聊 pragmatics ↔ 多人对话中的意图推断，和你 HCI 的 user intent 研究天然接轨。

### 9. Georges Harik — Co-founder（商业/投资侧）
- Google 第 7 号员工，AdWords/AdSense 早期系统；SV Angel 一起领投了本轮。1-1 概率低；若遇到聊 scaling 产品到 billions of users。

## ③ 1-1 通用弹药（从团队构成推断）
1. **Product-model co-evolution 是你的主场**：他们公开说设计与模型能力要共同演化（TechCrunch）——你是少数同时做过 HCI 研究和 LLM post-training/eval 的人，直接把 talk 和 1-1 都锚在这句话上。
2. **「协作评估」空白**：全队都在说 long-horizon/multi-agent RL + memory + user understanding，但没人公开讲清楚怎么 eval「好协作者」——你的 agent eval 经验可以每场 1-1 都递进这个问题。
3. **开源与学术姿态**：官网承诺回馈开源/学术（NVFP4 博客已兑现）＋两位成员保留学界身份（Mireshghallah→CMU、Goodman@Stanford）——可聊发表/开源文化，契合你 PhD 背景。
4. 彩蛋：官网首页是 Axelrod cultural dissemination 交互模拟（社会动力学品味）；X 账号 @humansand。

## ④ 事实纪律 / 来源
- 官网 humansand.ai（mission、founding team 背景列表含 Reflection、投资人名单、博客）；Ashby JD（tech stack、$350K）；均为 2026-08-09 直接抓取。
- 新闻：TechCrunch 2026-01-20 & 01-25（融资、~20 人、来自 OpenAI/Meta/Reflection/AI2/MIT、产品方向）、Forbes 2025-10-31（Zelikman/Goodman/Harik/Peng/Ramadorai 背景）、Crunchbase News、Reuters。
- 个人页：mireshghallah.github.io（+博客）、alexisjihyeross.github.io（+博客）、andipeng.com、GitHub zianglih。
- 未证实项已标注：Yuchen He 的 xAI vs OpenAI（来源冲突）；Ziang Li 履历（仅 GitHub bio）；HQ 为 Redwood City（PrivCo）但 JD 写 San Francisco。
- 找不到即如实说：Reflection 校友具体名字、其余 ~11 名员工、org chart——公开渠道均无。
