# 01_core · Agentic Systems 核心笔记索引

⏱ 约 2 分钟读完 ｜ 面试前只看 ⭐⭐⭐ 部分

蒸馏自 [CORE_NOTES.md](../../agentic/content/CORE_NOTES.md)（12 节）与 [SYSTEM_DESIGN_PLAYBOOK.md](../../agentic/content/SYSTEM_DESIGN_PLAYBOOK.md) 第五节的六类题高分句。所有代码块、dataclass、表格原样保留。

| 文件 | 主题 | 优先级 | 预计分钟 |
|---|---|---|---|
| [01_loop_and_tools.md](./01_loop_and_tools.md) | control plane 分界、agent loop 五边界、Claude tool-use 协议 7 步；ToolSpec + retry matrix | ⭐⭐⭐（tool design 部分 ⭐⭐） | 8 |
| [02_state_and_memory.md](./02_state_and_memory.md) | 三种状态、状态机、crash window、worker lease；context vs memory、四层 tiers、MemoryRecord | ⭐⭐⭐（memory 部分 ⭐⭐） | 8 |
| [03_harness_env_swe.md](./03_harness_env_swe.md) | harness 七要素、coding agent 五点、侦察→回归流程；TaskSpec 与分解原则 | ⭐ | 6 |
| [04_multi_agent.md](./04_multi_agent.md) | workflow/single/multi 怎么选、orchestration/fan-in/verifier、动态停止 | ⭐ | 5 |
| [05_reliability.md](./05_reliability.md) | 七类 failure taxonomy、Detection/Containment/Recovery/Prevention 四问、budget | ⭐⭐⭐ | 6 |
| [06_eval_security.md](./06_eval_security.md) | eval 对象与四层、pass@k vs pass^k、judge 校准、事故转 eval；security；五个高频为什么 | ⭐⭐⭐（security 部分 ⭐⭐） | 9 |

## 优先级规则

- ⭐⭐⭐：control plane、agent loop + tool-use 协议、state/durable、failure taxonomy、eval
- ⭐⭐：tool design、memory、security
- ⭐：workflow/single/multi 选择、harness/env、task decomposition

## 时间紧的读法

01 → 02 → 05 → 06，只读文内标 ⭐⭐⭐ 的小节 + 每节末尾的「高分句」引用块，约 25 分钟。
