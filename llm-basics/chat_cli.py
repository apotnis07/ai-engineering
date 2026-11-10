"""Phase 1 deliverable (due Thu Nov 5): one CLI chatbot built from the week's pieces.

It should have:
- Streaming replies (Day 2)
- All 3 tools, run in parallel, with errors sent back to the model (Days 6–9)
- A cost log, plus a running total for the session (Day 4)
- Structured output: `/extract <file>` prints a Contact as JSON (Day 3)

Things to notice:
- Streaming and tools meet here. Print text as it streams, then look at the final
  message for tool_use blocks. One user turn can be several API calls.
- Reuse what you wrote. If this file is getting long, something should be imported.

Done when: PASS prints, then `python chat_cli.py` lets you chat. Type "quit" to exit.
"""

from common import MODEL, client, failed, passed
from day3_structured import extract_contact
from day4_cost import cost_usd, log_call
from day6_tools import TOOLS, read_file
from day9_parallel_tools import run_tools_parallel

SYSTEM = "You are a concise assistant with a calculator, live weather and files in data/."
MAX_ROUNDS = 5


def chat_turn(history: list[dict], label: str = "chat") -> tuple[str, float]:
    """Handle one user turn, whose message is already in history. Return (reply text, cost in USD).

    Stream each API call to the terminal and log_call() every response. Run tools and
    loop until the model is done, capped at MAX_ROUNDS. Append everything to history.
    """
    # TODO
    raise NotImplementedError


def handle_extract(path: str) -> str:
    """Read a file from data/, split it on "\\n---\\n" like Day 3 and return one Contact per email as JSON lines."""
    # TODO
    raise NotImplementedError


def main() -> None:
    """The input loop: "quit", "/extract <file>" or a chat message. Print the session cost after each turn."""
    # TODO
    raise NotImplementedError


def check() -> None:
    history = [{"role": "user", "content": "Use the calculator tool: what is 1234 * 5678?"}]
    reply, cost = chat_turn(history)
    print()
    if "7006652" not in reply.replace(",", ""):
        return failed("tools", "1234 * 5678 = 7006652 should appear in the reply")
    if cost <= 0:
        return failed("cost", "chat_turn should return the cost of all its API calls")
    if len(history) < 4:
        return failed("history", "history should hold the tool call, its result and the answer")

    extracted = handle_extract("emails.txt")
    print(extracted)
    if "Priya" not in extracted or "Ana" not in extracted:
        return failed("extract", "every email in data/emails.txt should give a Contact")
    passed("Phase 1 chat CLI")


if __name__ == "__main__":
    check()
    main()
