"""Day 4: Count tokens and log the cost of every call.

Read first: docs.claude.com → "Token counting" and the Pricing page.

Things to notice while you read:
- Every response has `response.usage` with input_tokens, output_tokens,
  cache_creation_input_tokens and cache_read_input_tokens.
- `client.messages.count_tokens(model=..., messages=..., system=...)` tells you the input
  size BEFORE you send. Use the API for this, not tiktoken (different tokenizer).
- Output tokens cost 5x input tokens. Thinking tokens are billed as output.

Done when: PASS prints and cost_log.csv has one row per call.
"""

import csv
from datetime import datetime
from pathlib import Path

from anthropic import omit

from common import MODEL, PRICES, client, failed, passed

LOG_PATH = Path("cost_log.csv")


def cost_usd(usage, model: str = MODEL) -> float:
    """Dollar cost of one call from its usage object and the PRICES table.

    Remember all four token kinds. Some usage fields can be None: treat None as 0.
    """
    model_prices = PRICES[model]

    input_cost = model_prices["input"] * (usage.input_tokens or 0)
    output = model_prices["output"] * (usage.output_tokens or 0)
    cache_creation = model_prices["cache_write"] * (usage.cache_creation_input_tokens or 0)
    cache_read = model_prices["cache_read"] * (usage.cache_read_input_tokens or 0)

    total_per_million_tokens = input_cost + output + cache_creation + cache_read
    total_usd = total_per_million_tokens / 1000000.0

    return total_usd

def log_call(label: str, response) -> None:
    """Append one row to cost_log.csv: timestamp, label, model, input, output,
    cache_write, cache_read, cost_usd. Write a header row if the file is new."""

    file_path = LOG_PATH   
    fieldnames = ["timestamp", "label", "model", "input", "output", "cache_write", "cache_read", "cost_usd"]
    usage = response.usage
    new_row = {
        "timestamp": datetime.now().isoformat(timespec="seconds"), 
        "label": label,
        "model": response.model, 
        "input": usage.input_tokens, 
        "output": usage.output_tokens, 
        "cache_write": usage.cache_creation_input_tokens or 0, 
        "cache_read": usage.cache_read_input_tokens or 0, 
        "cost_usd": cost_usd(usage, MODEL),
    }

    file_is_new = not file_path.exists()

    with open(file_path, "a", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)

        if file_is_new:
            writer.writeheader()

        writer.writerow(new_row)



def estimate_input_tokens(messages: list[dict], system: str | None = None) -> int:
    """Use client.messages.count_tokens to count input tokens before sending."""
    response = client.messages.count_tokens(
        model=MODEL,
        system=system or omit,
        messages=messages,
    )
    return response.input_tokens


def tracked_ask(label: str, question: str, system: str | None = None):
    """Estimate tokens, make the call, log it, print 'estimated X / actual Y / $Z'. Return the response."""
    messages = [{"role": "user", "content": question}]
    estimated_input = estimate_input_tokens(messages, system)

    response = client.messages.create(
        model=MODEL,
        max_tokens=1024,
        system=system or omit,
        messages=messages,
    )
    actual_input = response.usage.input_tokens

    log_call(label, response)
    print(f"estimated {estimated_input} / actual {actual_input} / ${cost_usd(response.usage, MODEL):.5f}")

    return response

def check() -> None:
    LOG_PATH.unlink(missing_ok=True)
    short = tracked_ask("short", "Say hi.")
    long = tracked_ask("long", "Explain transformers in 300 words.")
    if not (0 < cost_usd(short.usage) < cost_usd(long.usage)):
        return failed("cost", "long answer should cost more than short answer")
    rows = list(csv.DictReader(LOG_PATH.open()))
    if len(rows) != 2:
        return failed("log", f"expected 2 rows in {LOG_PATH}, found {len(rows)}")
    total = sum(float(r["cost_usd"]) for r in rows)
    print(f"Logged {len(rows)} calls, total ${total:.5f} at {datetime.now():%H:%M}")
    passed("Day 4 cost tracking")


if __name__ == "__main__":
    check()
