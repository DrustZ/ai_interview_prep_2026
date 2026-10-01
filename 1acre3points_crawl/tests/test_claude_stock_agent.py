import copy
import json
import unittest
from dataclasses import dataclass
from typing import Any, List

from practice.anthropic.agent_tool_use import (
    AgentProtocolError,
    MaxStepsExceeded,
    StaticStockPriceService,
    ToolDefinition,
    ToolUseAgent,
    build_stock_price_tool,
)


@dataclass
class Block:
    type: str
    text: str = ""
    id: str = ""
    name: str = ""
    input: Any = None


@dataclass
class Response:
    stop_reason: str
    content: List[Block]


class FakeMessages:
    def __init__(self, responses):
        self.responses = list(responses)
        self.requests = []

    def create(self, **request):
        # The real SDK serializes the request during this call. Preserve the
        # same snapshot behavior instead of retaining the mutable messages list.
        self.requests.append(copy.deepcopy(request))
        if not self.responses:
            raise AssertionError("fake client has no response left")
        return self.responses.pop(0)


class FakeClient:
    def __init__(self, responses):
        self.messages = FakeMessages(responses)


def tool_call(call_id, ticker, name="get_stock_price"):
    return Block(
        type="tool_use",
        id=call_id,
        name=name,
        input={"ticker": ticker},
    )


def make_prices():
    return StaticStockPriceService(
        {
            "AAPL": {
                "price": 210.25,
                "currency": "USD",
                "as_of": "2026-07-13T14:30:00Z",
                "source": "test_feed",
            },
            "MSFT": {
                "price": 505.50,
                "currency": "USD",
                "as_of": "2026-07-13T14:30:00Z",
                "source": "test_feed",
            },
        }
    )


class ClaudeStockAgentTests(unittest.TestCase):
    def test_single_tool_call_then_final_answer(self):
        client = FakeClient(
            [
                Response("tool_use", [tool_call("toolu_1", "AAPL")]),
                Response("end_turn", [Block("text", text="AAPL is 210.25 USD.")]),
            ]
        )
        agent = ToolUseAgent(client, [build_stock_price_tool(make_prices())])

        result = agent.run("What is the sample AAPL price?")

        self.assertEqual(result.answer, "AAPL is 210.25 USD.")
        self.assertEqual(result.model_steps, 2)
        self.assertEqual(result.tool_calls, 1)
        second_request_messages = client.messages.requests[1]["messages"]
        tool_results = second_request_messages[-1]["content"]
        self.assertEqual(tool_results[0]["tool_use_id"], "toolu_1")
        self.assertNotIn("is_error", tool_results[0])
        self.assertEqual(json.loads(tool_results[0]["content"])["ticker"], "AAPL")

    def test_parallel_calls_return_together_in_original_order(self):
        client = FakeClient(
            [
                Response(
                    "tool_use",
                    [tool_call("toolu_a", "AAPL"), tool_call("toolu_m", "MSFT")],
                ),
                Response("end_turn", [Block("text", text="Both quotes are available.")]),
            ]
        )
        agent = ToolUseAgent(client, [build_stock_price_tool(make_prices())])

        agent.run("Compare AAPL and MSFT.")

        result_message = client.messages.requests[1]["messages"][-1]
        self.assertEqual(result_message["role"], "user")
        self.assertEqual(
            [block["tool_use_id"] for block in result_message["content"]],
            ["toolu_a", "toolu_m"],
        )

    def test_tool_exception_is_returned_to_model(self):
        client = FakeClient(
            [
                Response("tool_use", [tool_call("toolu_bad", "UNKNOWN")]),
                Response(
                    "end_turn",
                    [Block("text", text="That quote is currently unavailable.")],
                ),
            ]
        )
        agent = ToolUseAgent(client, [build_stock_price_tool(make_prices())])

        result = agent.run("Price UNKNOWN.")

        error = client.messages.requests[1]["messages"][-1]["content"][0]
        self.assertTrue(error["is_error"])
        self.assertIn("LookupError", error["content"])
        self.assertIn("unavailable", result.answer)

    def test_model_can_retry_after_a_tool_error(self):
        client = FakeClient(
            [
                Response("tool_use", [tool_call("toolu_bad", "UNKNOWN")]),
                Response("tool_use", [tool_call("toolu_retry", "AAPL")]),
                Response("end_turn", [Block("text", text="AAPL is 210.25 USD.")]),
            ]
        )
        agent = ToolUseAgent(client, [build_stock_price_tool(make_prices())])

        result = agent.run("Find the intended price.")

        self.assertEqual(result.model_steps, 3)
        self.assertEqual(result.tool_calls, 2)
        first_result = client.messages.requests[1]["messages"][-1]["content"][0]
        second_result = client.messages.requests[2]["messages"][-1]["content"][0]
        self.assertTrue(first_result["is_error"])
        self.assertNotIn("is_error", second_result)

    def test_unknown_tool_becomes_error_result(self):
        client = FakeClient(
            [
                Response("tool_use", [tool_call("toolu_x", "AAPL", "buy_stock")]),
                Response("end_turn", [Block("text", text="I cannot perform that action.")]),
            ]
        )
        agent = ToolUseAgent(client, [build_stock_price_tool(make_prices())])
        agent.run("Buy AAPL.")

        error = client.messages.requests[1]["messages"][-1]["content"][0]
        self.assertTrue(error["is_error"])
        self.assertIn("unknown tool", error["content"])

    def test_max_steps_prevents_an_infinite_loop(self):
        executions = []
        tool = ToolDefinition(
            name="get_stock_price",
            description="test",
            input_schema={"type": "object"},
            handler=lambda **kwargs: executions.append(kwargs),
            parallel_safe=True,
        )
        client = FakeClient([Response("tool_use", [tool_call("toolu_1", "AAPL")])])
        agent = ToolUseAgent(client, [tool], max_steps=1)

        with self.assertRaises(MaxStepsExceeded):
            agent.run("Loop forever.")
        self.assertEqual(executions, [])

    def test_max_tokens_is_not_treated_as_a_complete_answer(self):
        client = FakeClient(
            [Response("max_tokens", [Block("text", text="A truncated answer")])]
        )
        agent = ToolUseAgent(client, [build_stock_price_tool(make_prices())])

        with self.assertRaises(AgentProtocolError):
            agent.run("What is AAPL?")


if __name__ == "__main__":
    unittest.main()
