"""Day 1: Messages, roles, system prompts and stop reasons.

Read first: docs.claude.com → "Messages API" and "Getting started".

Things to notice while you read:
- `response.content` is a LIST of blocks, not a string. Current models think before
  answering, so there may be a `thinking` block before the `text` block.
- The API is stateless: for a multi-turn chat YOU resend the whole history every time.
- `stop_reason` tells you why the model stopped: end_turn, max_tokens, refusal, tool_use...
- Sampling knobs (`temperature`, `top_p`) were removed from the API in Oct 2026.
  The knob that exists now is `output_config={"effort": "low" | "medium" | "high" | ...}`.

Done when: `python day1_messages.py` prints PASS, then you can chat in the terminal.
"""

from anthropic import Omit, omit
from common import MODEL, client, failed, passed


def get_text(response) -> str:
    """Return the text of a response, skipping any non-text blocks."""
    return ''.join(res.text for res in response.content if res.type == "text")

def ask(question: str, system: str | None = None, max_tokens: int = 2000, effort: str | None = None):
    """Send ONE user message and return the full response object (not just the text).

    - Pass `system` only when it's given (a top-level parameter, not a message role).
    - Pass `output_config={"effort": effort}` only when effort is given.
    """
    message = client.messages.create(
        model=MODEL,
        max_tokens=max_tokens,
        system=system if system else omit,
        output_config={"effort" : effort} if effort else omit,
        messages=[{"role": "user", "content": question}]
    )
    return message

def chat() -> None:
    """A terminal chat loop that remembers the conversation.

    - Keep a `history` list of {"role": ..., "content": ...} dicts.
    - Each turn: append the user's message, call the API with the whole history,
      print the reply text, append the assistant's reply to history.
    - Type "quit" to exit. Print stop_reason and usage after each reply.
    Hint: appending `response.content` (the list of blocks) as the assistant content keeps
    thinking blocks intact, which is what the API expects on the next turn.
    """
    system = "You are a concise tutor helping someone learn AI engineering."
    history: list[dict] = []
    while True:
        user_input = input(">")
        if user_input == "quit":
            return
        else:
            history.append({"role": "user", "content": user_input})
            message = client.messages.create(
                model=MODEL,
                max_tokens=500,
                system=system,
                messages=history
            )
            print(get_text(message))
            print(message.stop_reason)
            print(message.usage)
            history.append({"role": "assistant", "content": message.content})

def check() -> None:
    r = ask("What is 2 + 2? Reply with just the number.")
    if "4" not in get_text(r):
        return failed("basic ask", f"expected 4, got {get_text(r)!r}")
    if r.stop_reason != "end_turn":
        return failed("stop_reason", f"expected end_turn, got {r.stop_reason}")

    r = ask("Name a color.", system="Always answer in French, one word.")
    print("System prompt test:", get_text(r))

    r = ask("Write a 500-word essay about rivers.", max_tokens=300)
    if r.stop_reason != "max_tokens":
        return failed("max_tokens", f"expected max_tokens, got {r.stop_reason}")

    r = ask("Is 97 prime?", effort="low")
    print("Low effort answer:", get_text(r)[:120], "| output tokens:", r.usage.output_tokens)

    passed("Day 1 functions")


if __name__ == "__main__":
    check()
    chat()
