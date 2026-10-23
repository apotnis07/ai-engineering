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
| Tue Oct 27 | `day5_caching.py` | Prompt caching savings (needs `data/long_doc.txt`, 6k+ words; not added yet) | Prompt caching |
| Wed Oct 28 – Thu Oct 29 | — | Buffer: catch up on slipped days, try a stretch goal, push to GitHub | — |

Done = each file prints `✅ PASS`, has 2–3 lines in `LEARNING_LOG.md`, and the folder is pushed to GitHub by Thu Oct 29 (the repo isn't a git repo yet: `git init` first, and confirm `.env` is gitignored before the first commit).
Tick each day's Done checkbox in the Notion Agenda.

## Week 2 (Oct 30 – Nov 5): tool calling by hand

Not scaffolded yet. At the start of week 2, create `day6_tools.py` … with TODOs for:
define 3 tools as JSON schemas (calculator, weather API, file read) → hand-written tool-call cycle →
return tool errors with `is_error: true` → parallel tool calls (all results in ONE user message).
Then update this file with week 2's dates and tasks.

## Gotchas found so far

- `response.content` is a list of blocks. With adaptive thinking there may be a `thinking` block before `text`, or not (trivial prompts skip thinking).
- No `temperature`; use `output_config={"effort": "low" | "medium" | "high" | "xhigh" | "max"}`. Opus 5.5 defaults to `medium`.
- Structured outputs: `client.messages.parse(..., output_format=Model)` → `response.parsed_output`. Don't use the deprecated top-level `output_format` on `create`.
- Caching only kicks in above a minimum prefix length; verify with `usage.cache_read_input_tokens`.
- Run with the project venv: `source .venv/bin/activate` (Python 3.13).

## How to help me here

Hints before answers. Don't fill in the TODOs. Point me to the specific docs section.
