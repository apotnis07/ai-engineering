# llm-basics: Weeks 1–2 (Phase 1: LLM API fundamentals)

Goal: call the Claude API directly and run tool calls by hand, with no framework.
Deliverable (Nov 5): this repo pushed to GitHub: CLI chat with streaming, 3 tools, a cost log and structured output.

## Week 1 (Oct 23 – Oct 29): the API itself

| Date | File | Task | Docs to read (docs.claude.com) |
| --- | --- | --- | --- |
| Fri Oct 23 | `day1_messages.py` | Messages, roles, system prompts, stop reasons, chat loop | Messages API, Getting started |
| Sat Oct 24 | `day2_stream.py` | Streaming, time to first token | Streaming messages |
| Sun Oct 25 | `day3_structured.py` | Structured outputs with Pydantic | Structured outputs |
| Mon Oct 26 | `day4_cost.py` | Token counting, cost per call, CSV log | Token counting, Pricing |
| Tue Oct 27 | `day5_caching.py` | Prompt caching savings (uses `data/long_doc.txt`) | Prompt caching |
| Wed Oct 28 – Thu Oct 29 | — | Buffer: catch up on slipped days, try a stretch goal, push to GitHub | — |

Done = each file prints `✅ PASS`, has 2–3 lines in `LEARNING_LOG.md`, and the folder is pushed to GitHub by Thu Oct 29 (this is part of the `ai-engineering` git repo, already initialized with commits for each day; keep `.env` gitignored).
Tick each day's Done checkbox in the Notion Agenda.

## Week 2 (Oct 30 – Nov 5): tool calling by hand

| Date | File | Task | Docs to read (docs.claude.com) |
| --- | --- | --- | --- |
| Fri Oct 30 | `day6_tools.py` | Define 3 tools as JSON schemas (calculator, weather, file read) and write their Python | Tool use: overview, Define tools; open-meteo.com docs |
| Sat Oct 31 | `day7_tool_cycle.py` | Hand-write the tool-call cycle | Tool use: Handle tool calls |
| Sun Nov 1 | `day8_tool_errors.py` | Return tool errors with `is_error: true` so the model can recover | Tool use: Handle tool calls |
| Mon Nov 2 | `day9_parallel_tools.py` | Run parallel tool calls, all results in ONE user message | Tool use: Parallel tool use |
| Tue Nov 3 – Wed Nov 4 | `chat_cli.py` | Buffer, then build the deliverable from the week's pieces | Streaming messages (again) |
| Thu Nov 5 | `README.md` | Deliverable: chat CLI working, README updated, pushed to GitHub | — |

Done = each file prints `✅ PASS`, has 2–3 lines in `LEARNING_LOG.md`, and `chat_cli.py` is pushed to GitHub by Thu Nov 5.
Tick each day's Done checkbox in the Notion Agenda.

The days build on each other: Day 7's `run_tool_cycle` takes a `run_tools` argument, and Days 8 and 9 pass in better versions.

Gotchas for this week:

- `tool_choice` `any` / `tool` is a 400 on Opus 5.5. Use the default `auto` and ask for the tool in the prompt.
- Every `tool_use` needs a `tool_result` with its `tool_use_id`, or the next call is a 400.
- `read_file` takes a path chosen by the model. It must not reach `.env`.
- `httpx` isn't installed (SDK 2.x uses `httpx2`). Use `urllib.request` for the weather call.

## Gotchas found so far

- `response.content` is a list of blocks. With adaptive thinking there may be a `thinking` block before `text`, or not (trivial prompts skip thinking).
- No `temperature`; use `output_config={"effort": "low" | "medium" | "high" | "xhigh" | "max"}`. Opus 5.5 defaults to `medium`.
- Structured outputs: `client.messages.parse(..., output_format=Model)` → `response.parsed_output`. Don't use the deprecated top-level `output_format` on `create`.
- Caching only kicks in above a minimum prefix length; verify with `usage.cache_read_input_tokens`.
- Run with the project venv: `source .venv/bin/activate` (Python 3.13).

## How to help me here

Hints before answers. Don't fill in the TODOs. Point me to the specific docs section.
