# llm-basics — Week 1

Week 1 of the AI Engineer Learning Plan: talk to the Claude API directly, with no framework.

Each `dayN_*.py` file has function signatures, a docstring that explains the goal, and `# TODO` blocks.
You write the code. Running a file calls your functions and then runs a `check()` that tells you whether you're done.

## Setup (once)

```bash
cd llm-basics
python3.13 -m venv .venv    # your default python3 is 3.7, which is too old; 3.10+ is required
source .venv/bin/activate
pip install -e .
cp .env.example .env        # then paste your API key into .env
python common.py            # prints "Setup OK" when the key works
```

Get an API key at https://console.anthropic.com (Settings → API Keys) and add $5–10 of credit.
Week 1 costs well under $2 if you use the default model.

## The week

| Day | File | You learn | Read first (docs.claude.com) |
| --- | --- | --- | --- |
| Fri Oct 23 | `day1_messages.py` | Messages, roles, system prompts, stop reasons, multi-turn chat | Messages API, Getting started |
| Sat Oct 24 | `day2_stream.py` | Streaming text to the terminal, time to first token | Streaming messages |
| Sun Oct 25 | `day3_structured.py` | JSON that matches a Pydantic schema | Structured outputs |
| Mon Oct 26 | `day4_cost.py` | Token counting, cost per call, a CSV cost log | Token counting, Pricing |
| Tue Oct 27 | `day5_caching.py` | Prompt caching and measuring the savings | Prompt caching |

Run a day with `python day1_messages.py`.

## Rules for the week

1. Read the docs page (~20 min) and run its example once.
2. Close the docs. Fill in the TODOs from memory. Reopen the docs only when stuck.
3. Run the file until `check()` prints PASS.
4. Compare with the Anthropic cookbook (github.com/anthropics/anthropic-cookbook) and note what's different.
5. Write 2–3 lines in `LEARNING_LOG.md`.

Use AI to **explain errors**, not to write the TODOs. Turn off autocomplete this week.

## Files you don't need to edit

- `common.py`: the client, the model name and the price table
- `data/`: sample inputs

## Stretch goals (only if you finish early)

- Day 1: Add a `/system` command that changes the system prompt mid-chat.
- Day 2: Show a spinner until the first token arrives.
- Day 3: Make the model extract a *list* of contacts from one email.
- Day 4: Print a running session total after every chat turn.
- Day 5: Cache a multi-turn conversation, not just the system prompt.
