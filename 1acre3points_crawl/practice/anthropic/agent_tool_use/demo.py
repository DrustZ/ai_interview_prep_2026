"""Run the stock agent against the real Claude API and a deterministic quote tool."""

import os
import sys

from .agent import StaticStockPriceService, ToolUseAgent, build_stock_price_tool


def main() -> int:
    try:
        from anthropic import Anthropic
    except ImportError:
        print("Install the optional SDK first: python3 -m pip install anthropic")
        return 1

    question = " ".join(sys.argv[1:]) or "Compare the sample prices for AAPL and MSFT."
    # These are deliberately labelled mock quotes, not claimed current prices.
    prices = StaticStockPriceService(
        {
            "AAPL": {
                "price": 210.25,
                "currency": "USD",
                "as_of": "2026-07-13T14:30:00Z",
                "source": "interview_mock",
            },
            "MSFT": {
                "price": 505.50,
                "currency": "USD",
                "as_of": "2026-07-13T14:30:00Z",
                "source": "interview_mock",
            },
        }
    )
    agent = ToolUseAgent(
        Anthropic(),
        [build_stock_price_tool(prices)],
        model=os.environ.get("CLAUDE_MODEL", "claude-sonnet-4-6"),
    )
    print(agent.run(question).answer)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
