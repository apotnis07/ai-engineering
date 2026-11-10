"""Day 9: Run parallel tool calls.

Read first: docs.claude.com → "Tool use" → "Parallel tool use".

Things to notice while you read:
- One assistant turn can hold several tool_use blocks. You've been handling that since
  Day 7 without seeing it. Today you run them at the same time.
- ALL the tool_results go back in ONE user message. Splitting them across messages
  quietly teaches the model to stop calling tools in parallel.
- One tool failing must not lose the results of the others.
- Tools waiting on the network fit threads well: see concurrent.futures.ThreadPoolExecutor.
  `asyncio` comes in week 5.

Done when: PASS prints and the 3-city run shows several tool_use blocks in one turn.
"""

import time

from common import failed, passed
from day6_tools import TOOL_FUNCTIONS
from day7_tool_cycle import run_tool_cycle
from day8_tool_errors import fake_call, run_one_safely


def run_tools_parallel(tool_uses: list) -> list[dict]:
    """Run all blocks at once with run_one_safely. Results stay in the same order as tool_uses."""
    # TODO: executor.submit finishes in any order. Which executor method keeps order?
    raise NotImplementedError


def slow_tool(seconds: float) -> str:
    time.sleep(seconds)
    return f"slept {seconds}"


def check() -> None:
    TOOL_FUNCTIONS["slow_tool"] = slow_tool
    calls = [fake_call(f"call_{seconds}", "slow_tool", {"seconds": seconds}) for seconds in (0.6, 0.1, 0.3)]
    start = time.perf_counter()
    results = run_tools_parallel(calls)
    elapsed = time.perf_counter() - start
    del TOOL_FUNCTIONS["slow_tool"]
    print(f"3 sleeps totalling 1.0s took {elapsed:.2f}s")

    if elapsed > 0.9:
        return failed("parallel", "these ran one after another")
    if [result.get("tool_use_id") for result in results] != [call.id for call in calls]:
        return failed("order", "results should line up with the tool_use blocks")

    mixed = run_tools_parallel(
        [fake_call("ok", "calculator", {"expression": "1 + 1"}), fake_call("bad", "read_file", {"path": "nope.txt"})]
    )
    if mixed[0].get("is_error") or not mixed[1].get("is_error"):
        return failed("errors", "one failure shouldn't affect the other result")

    answer, messages = run_tool_cycle(
        "Use get_weather for Tokyo, Paris and Cairo, all at once. Which is warmest?",
        run_tools=run_tools_parallel,
    )
    print(answer)

    turns = [
        sum(getattr(block, "type", "") == "tool_use" for block in message["content"])
        for message in messages
        if message["role"] == "assistant"
    ]
    print("tool_use blocks per assistant turn:", turns)
    if max(turns) < 2:
        return failed("model", "the model made its calls one at a time; check how you return tool_results")
    passed("Day 9 parallel tools")


if __name__ == "__main__":
    check()
