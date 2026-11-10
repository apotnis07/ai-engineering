"""Day 7: Write the tool-call cycle by hand.

Read first: docs.claude.com → "Tool use" → "Handle tool calls".

Things to notice while you read:
- The cycle: you send tools → model says stop_reason "tool_use" → you run the tool →
  you send a USER message of `tool_result` blocks → model answers (or asks for more).
- Each tool_result carries the tool_use_id of the call it answers.
- Append the whole `response.content` as the assistant turn, as on Day 1. Thinking
  blocks and tool_use blocks have to go back exactly as they came.
- Keep going until stop_reason is no longer "tool_use", but cap the rounds. A loop that
  pays per iteration needs a limit. This is next week's agent in miniature.

Done when: PASS prints and you can explain each message in the printed history.
"""

import json
from email import message
from re import M
from common import MODEL, client, failed, passed
from day4_cost import log_call
from day6_tools import TOOLS, run_tool
from day1_messages import get_text

MAX_ROUNDS = 5


def run_tools_in_order(tool_uses: list) -> list[dict]:
    """Run each tool_use block and return one tool_result dict per block, in the same order."""
    results = []
    for tool_use in tool_uses:
        content = run_tool(tool_use.name, tool_use.input)
        results.append(
            {"type": "tool_result", "tool_use_id": tool_use.id, "content": content}
        )
    return results


def run_tool_cycle(
    question: str, run_tools=run_tools_in_order
) -> tuple[str, list[dict]]:
    """Answer a question with tools. Return (final text, full messages list).

    - Call the API with tools=TOOLS, and log_call() every response.
    - Print each tool the model asks for, its input and the result.
    - Use the `run_tools` argument, not run_tools_in_order directly: Days 8 and 9 pass
      their own versions in.
    - Stop when stop_reason isn't "tool_use". Raise RuntimeError after MAX_ROUNDS.
    """
    messages = [{"role": "user", "content": question}]

    for _ in range(MAX_ROUNDS):
        response = client.messages.create(
            model=MODEL,
            max_tokens=1024,
            tools=TOOLS,
            tool_choice={"type": "auto"},
            messages=messages,
        )
        log_call("tool_call", response)

        messages += [{"role": "assistant", "content": response.content}]
        if response.stop_reason != "tool_use":
            return (get_text(response), messages)

        tool_uses = [block for block in response.content if block.type == "tool_use"]

        results = run_tools(tool_uses)
        messages += [{"role": "user", "content": results}]

        for tool_use, res in zip(tool_uses, results):
          print(f"Claude called {tool_use.name} with {json.dumps(tool_use.input)} and got the result {res['content'][:80]!r}")

    raise RuntimeError(f"no final answer after {MAX_ROUNDS} rounds")

def check() -> None:
    answer, messages = run_tool_cycle("Use the calculator tool: what is 1234 * 5678?")
    print(answer)

    roles = [message["role"] for message in messages]
    print(roles)
    if roles != ["user", "assistant", "user", "assistant"]:
        return failed(
            "cycle",
            "expected user → assistant (tool_use) → user (tool_result) → assistant",
        )
    result = messages[2]["content"][0]
    if not isinstance(result, dict) or result.get("type") != "tool_result":
        return failed(
            "tool_result", "the third message should hold a tool_result block"
        )
    if "7006652" not in answer.replace(",", ""):
        return failed(
            "answer", "1234 * 5678 = 7006652 should appear in the final answer"
        )
    passed("Day 7 tool cycle")


if __name__ == "__main__":
    check()
