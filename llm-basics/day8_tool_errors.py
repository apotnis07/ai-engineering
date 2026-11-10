"""Day 8: Return tool errors so the model can recover.

Read first: docs.claude.com → "Tool use" → "Handle tool calls" (the errors part).

Things to notice while you read:
- A failing tool shouldn't crash your program. It's information for the model.
- Send the error back as a normal tool_result with "is_error": True and text the model
  can act on. "File not found: data/email.txt" helps. "Error" doesn't.
- Every tool_use needs a tool_result, even when it failed. Dropping one is a 400.

Done when: PASS prints and the printed run shows the model hitting an error, then fixing it.
"""

from types import SimpleNamespace

from common import failed, passed
from day6_tools import run_tool
from day7_tool_cycle import run_tool_cycle


def run_one_safely(tool_use) -> dict:
    """Run one tool_use block and return a tool_result dict. Never raises.

    On failure set "is_error": True, with content naming what went wrong.
    """
    # TODO
    raise NotImplementedError


def run_tools_safely(tool_uses: list) -> list[dict]:
    """run_one_safely for each block, in order."""
    # TODO
    raise NotImplementedError


def fake_call(call_id: str, name: str, tool_input: dict):
    """A stand-in for a tool_use block, so tests don't need the API."""
    return SimpleNamespace(id=call_id, name=name, input=tool_input)


def check() -> None:
    good = run_one_safely(fake_call("a", "calculator", {"expression": "1 + 1"}))
    if good.get("tool_use_id") != "a" or good.get("is_error"):
        return failed("success", f"a working call shouldn't be an error: {good}")

    bad_calls = [
        fake_call("b", "read_file", {"path": "nope.txt"}),
        fake_call("c", "read_file", {"path": "../.env"}),
        fake_call("d", "calculator", {"expression": "not maths"}),
        fake_call("e", "no_such_tool", {}),
    ]
    results = run_tools_safely(bad_calls)
    for call, result in zip(bad_calls, results):
        if not result.get("is_error") or result.get("tool_use_id") != call.id or not result.get("content"):
            return failed("errors", f"{call.name} should give an is_error result with a message: {result}")

    answer, messages = run_tool_cycle(
        "Use read_file to open email.txt. If that fails, try emails.txt, then tell me how many lines it has.",
        run_tools=run_tools_safely,
    )
    print(answer)

    results = [
        block
        for message in messages
        if message["role"] == "user" and isinstance(message["content"], list)
        for block in message["content"]
    ]
    print([bool(result.get("is_error")) for result in results])
    if not any(result.get("is_error") for result in results):
        return failed("recovery", "the model never hit an error; read_file('email.txt') should fail")
    if results[-1].get("is_error"):
        return failed("recovery", "the model's last tool call should have worked")
    passed("Day 8 tool errors")


if __name__ == "__main__":
    check()
