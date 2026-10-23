# AI Engineering learning repo

I'm following a 16-week plan to become an AI engineer (Oct 23, 2026 → Feb 11, 2027).
Each phase gets its own project folder in this repo.

## Where things live

- Plan (full text): Notion "AI Engineer Learning Plan": https://app.notion.com/p/40138b12c9fb817b87e1e14b9cf41ecf
- Daily agenda + Done checkboxes: Notion "Agenda" database on that page (Calendar and To-do list views)
- Same plan as a Claude doc: https://claude.ai/artifact/RkejWztJuDAGK1UhTJUvtq
- Each project folder has its own `README.md`, `CLAUDE.md` and `LEARNING_LOG.md`

## Ground rules for Claude

- I'm learning. Explain, hint and point me to docs; **don't fill in my `# TODO`s** unless I explicitly ask for the answer.
- When I'm stuck, give the smallest hint that unblocks me first, then more if I ask.
- Use AI to explain errors, not to write the exercise code.
- Keep weeks small and buildable; every week ends with code pushed to GitHub.

## Setup facts

- Python: use `python3.13` (the default `python3` on this Mac is 3.7, too old). Each project has its own `.venv`.
- Anthropic Python SDK 2.x (`anthropic>=2`). Default model `claude-opus-5-5`; `claude-haiku-5-5` for cheap experiments.
- `temperature` / `top_p` were removed from the API (Oct 2026); use `output_config={"effort": ...}`.
- API key lives in each project's `.env` (gitignored). Never print or commit it.

## Schedule

| Weeks | Dates | Phase | Folder |
| --- | --- | --- | --- |
| 1–2 | Oct 23 – Nov 5 | 1 LLM API fundamentals | `llm-basics/` |
| 3–5 | Nov 6 – Nov 26 | 2 Agent loop from scratch | `mini-agent/` |
| 6–7 | Nov 27 – Dec 10 | 3 Evals and observability | `mini-agent/evals/` |
| 8 | Dec 11 – Dec 17 | 4 MCP servers + client | `mcp-servers/` |
| 9 | Dec 18 – Dec 24 | 5 Skills and context engineering | `skills/` |
| 10–11 | Dec 25 – Jan 7 | 6 RAG + one framework | `docs-qa-agent/` |
| 12–13 | Jan 8 – Jan 21 | 7 Multi-agent + production | `multi-agent/` |
| 14–16 | Jan 22 – Feb 11 | 8 Capstone + job search | `research-agent/` |

## Current status

- Current week: **Week 1** (Phase 1, Oct 23 – Oct 29), working in `llm-basics/`. Started Fri Oct 23.
- Update this line at the start of every week.

## Starting a new week or phase (Claude: do this every time)

When I start a new week or phase, before anything else:

1. Update "Current status" above.
2. If the phase needs a new folder, create it with a skeleton (README, functions with `# TODO`s, a `check()` per task, `LEARNING_LOG.md`), like `llm-basics/`.
3. **Create or update that folder's `CLAUDE.md`** for the week: its goal, the daily tasks and dates (from the Notion Agenda), docs to read, gotchas, and what "done" means. Copy the shape of `llm-basics/CLAUDE.md`.
4. Check the Notion Agenda for which tasks are done and mention any that slipped.
5. Suggest starting a fresh Claude session for the new week so the context stays small.
