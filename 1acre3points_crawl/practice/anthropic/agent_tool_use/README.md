# Claude Stock Tool-Use Agent

这是 `Agents Coding LLM Tool Use` 的最小可运行练习项目。完整题面写在
[`agent.py`](./agent.py) 顶部；[`SYSTEM_DESIGN.md`](./SYSTEM_DESIGN.md) 单独回答
“能适应新任务的 agentic AI system”设计题，避免把两道题混成同一题。

## 离线测试

```bash
cd /Users/mingrui/Documents/codes/interview/1acre3points
python3 -m unittest tests/test_claude_stock_agent.py -v
```

测试使用 fake Claude client 和 mock 股票工具，不需要 API key、Anthropic SDK 或网络。

## 调用真实 Claude API

```bash
python3 -m pip install anthropic
export ANTHROPIC_API_KEY='...'
export CLAUDE_MODEL='claude-sonnet-4-6'  # 可换成账户可用的当前模型
python3 -m practice.anthropic.agent_tool_use.demo \
  'Compare the sample prices for AAPL and MSFT.'
```

Demo 的股票数字是明确标注的固定 mock 数据。面试中可把
`StaticStockPriceService` 换成真实行情 API adapter；agent loop 无需修改。

## 目录

```text
agent_tool_use/
├── agent.py          # 题面、tool schema、manual agent loop、错误与并行处理
├── demo.py           # 可选的真实 Claude API 入口
├── SYSTEM_DESIGN.md  # 独立的 adaptive-agent system design 答案
└── README.md
```
