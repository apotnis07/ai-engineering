"""Shared setup. You don't need to edit this file (except to change MODEL)."""

import anthropic
from dotenv import load_dotenv

load_dotenv()

# Claude Opus 5.5 is the current default model.
# For cheaper experiments, switch to "claude-haiku-5-5" (about 40x cheaper per token).
MODEL = "claude-haiku-5-5"

# USD per 1M tokens (Oct 2026). Verify against the pricing page before trusting your cost log.
# cache_write = 5-minute cache write (1.25x input); cache_read = cache hit (0.05-0.1x input).
PRICES = {
    "claude-opus-5-5": {"input": 4.00, "output": 20.00, "cache_write": 5.00, "cache_read": 0.20},
    "claude-haiku-5-5": {"input": 0.10, "output": 0.50, "cache_write": 0.125, "cache_read": 0.01},
}

# Reads ANTHROPIC_API_KEY from the environment (.env is loaded above).
client = anthropic.Anthropic()


def passed(name: str) -> None:
    print(f"\n✅ PASS: {name}")


def failed(name: str, why: str) -> None:
    print(f"\n❌ FAIL: {name}: {why}")


if __name__ == "__main__":
    reply = client.messages.create(
        model=MODEL,
        max_tokens=1000,
        messages=[{"role": "user", "content": "Say 'ready' and nothing else."}],
    )
    print([block.type for block in reply.content], reply.stop_reason)
    print("Setup OK")
