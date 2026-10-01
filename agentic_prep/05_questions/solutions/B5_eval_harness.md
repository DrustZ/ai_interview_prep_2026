# [B5] Applied Compute：Enterprise Agent Eval Harness 与 Reward Hacking · 完整解答

⏱ 读完 12 min ｜ 建议先自己限时 60min 答一遍再看（盲看解答记不住）。题面原文见 [../B_general_design.md](../B_general_design.md#b5)，完整 rubric 见 [../../../agentic/data/questions.json](../../../agentic/data/questions.json) → `q-applied-agent-eval`；动手版配套 lab：[../../../agentic/labs/05_eval_harness/README.md](../../../agentic/labs/05_eval_harness/README.md)。

## 题目还原

为企业 legal agent（可查文档、可起草内容）设计训练/发布 eval harness：任务来自真实 workflow，需防 data leakage、grader gaming、环境污染，并比较新 checkpoint 与 production model。rubric 权重：eval validity 25% + leakage 20% + grader 20% + 统计/rollout 20% + reward hacking 15%——**这题不考 agent 本身，考你能不能把 eval 当成一个会被 policy 攻击的生产系统来设计**。最容易答虚的两个地方：① 只说"搞个 benchmark 跑分"，不谈 eval 是否预测 production；② 把 reward hacking 当奇闻讲，给不出攻击面枚举和具体防线。

## 开场澄清（5 问 + 为什么问）

1. **这个 harness 服务训练（RL reward / checkpoint 选择）还是只做发布 gate？**→ 训练用意味着 policy 会主动优化打分面，防 hack 强度完全不同。假设：两者都要，共用一套环境与 grader 基建，held-out 只用于发布。
2. **允许用真实客户数据吗？合规边界？**→ 决定去标识 pipeline 和"合成 near-real 语料"的比例。假设：允许，但须去标识 + 客户同意范围内 + 按客户隔离。
3. **哪些 outcome 是确定性的？**→ 条款抽取/citation 可 deterministic；草稿质量必须 judge。这决定 grader 栈比例。
4. **发布 gate 对 regression 的阈值？**→ 假设：总体 non-inferior（单侧 CI），任一高风险 slice 回归超 2pt 即 block。
5. **比较对象只有 candidate vs production 一对吗？多久发一次？**→ 决定 runner 吞吐、缓存与预算设计。假设：每周多个 checkpoint，报告小时级出。

## 答案主线（按 [../../02_playbook.md](../../02_playbook.md) 时间盒 + rubric pacing 走）

**开场 90 秒**（背这段）："我按五层交付：① task registry——从 production taxonomy 分层抽样，按客户+时间双维隔离 held-out，EvalTask immutable、只增不改；② environment——文档库 snapshot + 每 trial 全新 reset，零真实副作用；③ trial runner——paired trials、多 seed、transcript 与 outcome 分开采集；④ grader 栈——outcome/policy/process 三类 deterministic 优先，模糊质量才交给用人工 gold set 校准过的 judge；⑤ 统计与发布——pass@1/pass^k、slice 级 paired CI、shadow→canary→rollback。两条防线贯穿全部五层：leakage（训练管线在物理权限上读不到 held-out）和 reward hacking（grader 对 agent 不可见 + ensemble + '自动分涨而人工抽查不涨'的散度告警）。先问 eval 是否预测 production，再谈跑分。"

**需求与发布风险（0–7min）**：legal agent 的任务 taxonomy 从 production trace 聚出来：合同审阅/redline、条款抽取、NDA 起草、research memo。风险排序（决定 slice 与 gate 权重）：**引用不存在的条款**（幻觉 citation，法务场景致命）＞ 跨客户/privileged 文档泄露 ＞ 无依据法律结论 ＞ 质量平庸。goal predicate 写一行：`给定冻结的 registry 版本 R_v 与 (M_cand, M_prod)，输出带 CI 的 paired 分 slice 报告；harness 的北极星是预测力——离线过 gate 的 checkpoint 上线后 online 指标不回归`。

**接口与数据模型（7–14min）**：

```text
EvalTask(immutable, versioned): task_id, family(taxonomy), slice_tags{customer_segment, risk, horizon},
    inputs(去标识 workflow 输入), env_snapshot_ref(文档库+索引 snapshot hash), policy_version,
    grader_ids[](spec 不随环境下发), canary_fact_ids[], seeds[], lineage(source_trace|synthetic), holdout: bool
TrialResult: task_id+version, model_version, trial_idx, seed, outcome(环境终态 diff),
    transcript_ref(全 tool trace/token/cost), scores{grader_id: value}, latency, tool_error_count,
    policy_violations[], error_category
Grader: grader_id, kind(outcome|policy|process|judge), version, assertions|rubric, calibration_ref(judge 才有)
EvalReport: registry_version, model_pair, per-slice {pass@1, pass^k, paired delta + CI},
    cost/p95 latency/policy violation rate, judge κ 快照, failure examples(链到 transcript)
```

API：`POST /eval-runs {registry_version, candidate, baseline, k}` → `GET /eval-runs/{id}/report`；`POST /tasks`（只增不改，改 = 新版本 + deprecate 旧版）；`GET /trials/{id}/transcript`。transcript 与 outcome **分开采集**——才能分别评 trajectory 和 outcome（Anthropic 口径）。

**架构图（14–18min 画）**：

```text
Production traces ──► Curation（去标识 + taxonomy 分层抽样 + lineage 单向分配）
      │                          │
      ▼                          ▼
 train pool                Held-out Task Registry（immutable/versioned/append-only）
（训练/调 prompt 可见）           │      ✕ 物理隔离：训练管线无读权限
      ▲                          ▼
      │                  Trial Runner / Scheduler ──► per-trial 全新 sandbox env
      │                    │  paired: cand vs prod 同 task 同 seed；k trials
      │                    ▼
      │                  Trace Store（transcript ∥ outcome 分开落盘）
      │                    ▼
      │                  Grader 栈（环境外执行）: outcome → policy → process → 校准 judge
      │                    ▼
      │                  Report: pass@1/pass^k、slice paired CI、failure taxonomy
      │                    ▼
      └── 失败 trace（先去污染再回流训练）◄── Release gate → shadow → canary → rollback
```

**环境与评估 pipeline（18–38min，rubric 主体）**：

1. **Task registry**：按 production taxonomy 分层抽样保 mix 代表性；held-out 按**客户 × 时间**双维隔离——同一客户的相似合同、同一时间窗的关联案件都是 near-dup 泄漏源，只按行随机 split 必挂。每条事故型 task 加 2–3 个邻近变体（换当事方/金额/条款序），防"只修单例"也防 memorization。
2. **Environment reset**：环境 = `f(snapshot, seed)`。文档库 + 检索索引一起 snapshot（hash 固定进 EvalTask），每 trial 起全新容器/DB，禁网络出口；transient tool error 由 seed 确定性注入（lab 05 打法）。**红线：绝不复用上一 trial 的 workspace**——上轮草稿残留被下轮读到 = 假提升，这就是题面说的"环境污染"最常见形态。
3. **Trial runner**：任务 × 模型 × seed 矩阵并行跑；**paired**——同 task 同 seed 下 candidate 与 prod 各一次，噪声（检索顺序、注入的 error）两边一致，方差立减；k=4–8 trials 支撑 pass^k；结果按 `(task_version, model_version, seed)` 幂等缓存；message/token/cost limit 防跑飞。
4. **Grader 栈**（优先级从上往下，能用上面的不用下面的）：
   - **outcome（deterministic，环境终态）**：条款抽取与 gold 集合比对；**citation 逐条 span 匹配回 snapshot 文档**，引用不存在即 fail；草稿必含/必不含条款断言。不信 agent 自述"已完成"——完成由可观察事实判定（lab 05 第 3 条）。
   - **policy（读 trace）**：越权文档访问、禁止工具、privileged 内容出现在产出、注入指令被执行——任一即整题 fail，不做加权平均。
   - **process**：步数预算、重复 call signature、绕路率——只作诊断信号，不进 gate 分。
   - **judge（最后才上）**：草稿质量 rubric（结构/术语/风险提示），pairwise + 交换顺序消 position bias，swap 不一致判 tie；用 SME（律师）gold set 校准，Cohen κ ≥ human-human κ − margin 才上岗；阈值附近样本交人工。judge 与被测模型**异族**（深挖 2）。
5. **grader 执行位置**：grading 全部在环境**外**跑——agent 可见的文件系统里没有任何测试/评分文件；grader spec 不随任务下发。这是防 gaming 的第一性设计，不是补丁。

**Leakage 与 reward hacking（38–48min）**：leakage 三道闸：① **权限**：held-out bucket 对训练/prompt 调优管线物理不可读，eval run 产生的 trace 打 `eval` 标签、训练摄入端硬过滤；② **指纹**：训练数据入库前对 held-out 做 n-gram + embedding near-dup 扫描，命中即剔除；③ **canary**：held-out 文档里埋唯一 GUID 事实——模型没做检索就说出 canary = 训练集被污染，事后兜底告警。reward hacking 攻击面枚举 + 防线：

| 攻击 | 具体形态（legal 场景） | 防线 |
|---|---|---|
| 碰 grader | 找评分文件/改测试 | grader 在环境外 + 环境里放诱饵 `grader_config.yaml`（honeypot），碰了即 flag |
| 骗 judge | 草稿嵌"本条款已经合伙人复核"、自信语气、超长列表 | grounding check（claim 必须映射到 citation span）+ judge ensemble + 已知 repetitive-list 攻击能骗 GPT-4 8.7%（MT-bench），对抗样本定期打 judge |
| 谎报完成 | "已在第 4.2 条加入赔偿上限"但环境里没有 | outcome grader 只看环境终态 diff |
| 走捷径 | 不检索靠记忆答（训练见过相似合同） | canary fact 必须被引用才算对：没检索就答对 = 污染；检索了引用错 = 能力问题——一个机制同时测两件事 |
| 过度谨慎 | 学会"不确定就 escalate"刷安全分 | 拒答/错答/对答三态分开计分，无功也计低分（[../../03_gaps/agentic_rl.md](../../03_gaps/agentic_rl.md) Q2 例 3） |

监控口径（背）：**自动分上涨而人工抽查分不涨，这个散度就是被 hack 的第一告警**；配 top-score trial 人工抽样 + score 分布突变检测。若 harness 兼作 RL reward：compliance 用 hard gate（reward=0）不给软惩罚交易空间；CoT/行为 monitor 信号**只做告警与数据过滤，绝不进 reward**——OpenAI 实证把 monitor 并进 reward 会教出 obfuscated hacking。

**统计与发布（48–55min）**：报告以 **paired per-task delta** 为主：每 task 算 `score(cand) − score(prod)`，bootstrap 出 CI；pass^k 用 τ-bench 的组合数无偏估计 `mean(C(c,k)/C(n,k))`（capability 看 pass@k，production readiness 看 pass^k——p=0.8 时 p⁴≈0.41，均值掩盖不稳定）。slice 至少按 family/customer_segment/risk/horizon 切，规定最低样本量，不够就标"insufficient"而不是报个大 CI 假装有结论。Gate：总体 non-inferior + 高风险 slice（citation 正确率、泄露率）零回归。过 gate 后 shadow（candidate 消费 production 输入、不产出）→ canary 按客户灰度 → 指标回归自动 rollback；线上失败去污染后回流成新 held-out regression case——事故→eval 的六步见 [../../01_core/06_eval_security.md](../../01_core/06_eval_security.md) §5。

## 深挖 3 处（题库高频追问）

**1）线上指标变好、离线变差怎么办？**——"先当作 eval validity 事故而不是直接信任一边。三个假设按序排查：① **离线分布陈旧**：production mix 漂移了——拿最近 90 天线上 traffic 的 family 分布对离线结果**重新加权**（不动 held-out 本身，保持冻结），加权后矛盾消失就是分布问题，触发 registry 整版本升级；② **线上 proxy 有偏**：legal 场景错误被发现的延迟极长，'线上变好'可能只是 escalation 少了、用户没发现错——查 SME 抽查分和 delayed correction 率，别拿 thumbs-up 当 ground truth；③ **slice 抵消**：总分背后新模型可能 A slice 大涨 B slice 大跌，paired 报告直接看 slice 级 delta。行动：冻结发布，抽两边 disagreement 最大的 20 条 trace 人工裁决，裁决结果决定是修 eval（换权重/补 task）还是信 eval（挡发布）。高分句：离线 eval 是 production 的预测器，预测失灵先修预测器的分布和标签，而不是把预测器扔了。"

**2）LLM judge 与被测模型同源有什么风险？**——"三层。① **self-enhancement bias**：MT-bench 实测 judge 偏好自己家族的输出，同源时 candidate 分数系统性虚高；② **correlated blind spot**：同源意味着同训练分布、同类幻觉——被测模型编造的'看似合理条款引用'，同源 judge 同样看不出来，两个模型一起错且方向一致，这比随机噪声危险得多；③ **训练侧放大**：如果 checkpoint 做过 RL、reward 里有同族 judge，policy 已经学会讨好这个家族的表面特征（自信语气、特定格式），发布 eval 再用同族 judge 等于让出题人和阅卷人是同一个被优化目标。防线：judge 异族 + judge ensemble（分歧大的样本转人工）+ deterministic grader 承担 outcome/policy（judge 只管模糊质量，缩小暴露面）+ κ 对 SME gold set 持续监控、漂移即重校准；换 judge 版本时用同一 gold set 重跑，保历史分数可比。高分句：judge 本身是一个需要 eval 的模型——先校准 agreement 再上岗。"

**3）失败 trace 怎么变训练信号又不污染 test？**——"核心是**单向流动 + lineage**。一条 production 失败 trace 进 curation 后只能去一边：进 held-out（从此训练管线永远不可见）或进训练池（从此永远不能再变 eval task），分配记录进 lineage，没有第三条路。三道防线兜底：① 权限——训练管线物理读不到 held-out bucket；② 指纹——训练数据入库前对 held-out 全量做 n-gram+embedding near-dup 扫描，同一事故的姊妹 trace（同客户同合同模板）会被指纹抓住剔除，这是最容易漏的泄漏路径；③ canary——事后检测。另外进 held-out 的事故不进'原样'，写成去 secret 的最小复现 + 2–3 个邻近变体的 family：既防只修单例，也让 memorization 更难。高分句：production trace 先变成 versioned、可复现的 eval case，才有资格变成训练信号。"

## 失败模式与恢复（本题具体场景）

- **grader 太松比太严危险**：string match 放过错误等价形式 = 假阳性 reward，训练侧会被 policy 大规模利用——verifier 本身当攻击面做 red team，定期拿已知坏输出打它。
- **judge/user-sim 噪声**：τ-bench 教训——user simulator 是 LLM，会给错信息或过度配合；pin simulator 模型版本进 EvalTask，抽查 simulator 行为本身。
- **结果不可复现**：全部版本（model/tool/snapshot/policy/grader/judge/seed）进 TrialResult；复跑 = 同幂等 key 命中缓存或严格重放。
- **trial 间环境残留**：见主线红线；上线前用"空 agent"跑 registry 两遍，第二遍分数异动即 reset 有漏。
- **registry 腐化**：只增不改、deprecate 不 delete；每季度审计 task 存活度（production 还出现这类任务吗），死 task 降权不删。
- **canary 误报**：canary GUID 被 agent 检索到再输出是正常路径——告警条件是"未检索而输出"，需要 trace 联查而不是 grep 输出。
- **honeypot 误伤**：agent 只是 `ls` 看到诱饵文件名不算 flag，读内容/引用它才算；flag 进人工审计队列而非直接 fail，防误杀。

## Trade-offs 三条（主动说）

1. **deterministic 优先，judge 只兜模糊质量**：牺牲"评估维度全面性"换可信度与成本——outcome/policy 可机械验证的绝不上 judge。信号：judge κ 连续稳定 ≥ human-human κ − margin，且人工抽查与 judge 分歧率低 → 扩大 judge 覆盖面。
2. **held-out 冻结 vs 分布新鲜度**：冻结保可比性但会陈旧。折中：日常用 traffic 重加权解释结果，分布漂移超阈值时做**整版本 registry 升级**（新旧版本并行跑一个周期校准），绝不零散改单条 task。
3. **paired 多 trial 成本高**：全量 k=8 太贵。分层预算：高风险 slice k=8，长尾 family k=2 + 顺序检验（paired delta 的 CI 一旦排除 0 就停，省 40%+ 算力）；结果缓存让"多 checkpoint 对同一 baseline"只跑增量。

## 现实参照（只引本地已有链接）

- [Demystifying evals for AI agents](https://www.anthropic.com/engineering/demystifying-evals-for-ai-agents)（Anthropic）：task/trial/transcript/grader 词汇 + code/model/human 三类 grader 排序 + transcript 与 outcome 分开采集——本解骨架的对齐基准。
- [Inspect AI](https://inspect.aisi.org.uk/)（UK AISI）：Dataset→Solver→Scorer + per-sample Docker sandbox + epochs=k，"trial runner + 环境隔离"的最接近生产的开源实现。
- [τ-bench](https://github.com/sierra-research/tau-bench)：DB 终态比对 + required outputs 双达成、pass^k 组合数无偏估计 `C(c,k)/C(n,k)`——统计节的直接出处。
- [MT-Bench / LLM-as-judge](https://arxiv.org/abs/2306.05685)：position/verbosity/self-enhancement bias 与 Cohen κ 校准，深挖 2 的证据链。
- [AgentDojo](https://arxiv.org/abs/2406.13352)：utility vs attack-success 双指标——本解 adversarial task 与"注入指令被执行即 fail"的原型。
- [Anthropic emergent misalignment from reward hacking](https://www.anthropic.com/research/emergent-misalignment-reward-hacking)：生产 RL 环境里 hack 会泛化成恶性行为的实证——防 hack 不只是指标卫生，是安全问题。
- [OpenAI CoT monitoring](https://openai.com/index/chain-of-thought-monitoring/)：monitor 信号并进 reward → obfuscated hacking 的负结果，"监控归监控、训练归训练"的出处。
- [Applied Compute](https://www.appliedcompute.com/)：题目公司本尊——custom harness/graders/traces/reward hacking detection 是其公开卖点，答题词汇直接对齐。

> 收尾高分句（可背）：eval harness 是 agent 系统的 CI，而 policy 是一个会主动攻击 CI 的对手——所以 grader 要藏在环境外、held-out 要物理隔离、判分要用环境终态而不是模型自述；**自动分和人工抽查一旦散开，涨的那条线就不是能力，是 hack**。
