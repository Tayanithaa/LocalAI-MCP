# Local AI Workspace (MVP)

A working slice of the "local AI OS via MCP + Ollama" architecture:
Ollama (planning) → tool registry → MCP tool servers (filesystem, web search)
→ Ollama (summarization), looped until the task is done.

## What's actually implemented here

- `core/planner.py` — asks the local LLM for one JSON action at a time
  (`call_tool` or `final_answer`).
- `core/orchestrator.py` — the plan/execute/observe loop (multi-step tasks).
- `registry/tool_registry.py` — spawns MCP servers over stdio, discovers
  their tools, exposes `registry.call("server.tool", {...})`.
- `tools/filesystem/server.py` — sandboxed list/read/search, real MCP server.
- `tools/duckduckgo/server.py` — real web search MCP server, no API key.
- `ollama/client.py` — minimal async client for a local Ollama instance.

This is intentionally **two tools deep, not eight**. The registry pattern is
what makes the rest cheap: adding GitHub/Gmail/Docker/etc. is "write one more
`tools/<name>/server.py` with `@mcp.tool()` functions, add one line to
`TOOL_SERVERS`" — no changes to the planner, orchestrator, or main.py.

## Setup

```bash
pip install -r requirements.txt
ollama serve                     # in another terminal
ollama pull llama3.1              # or your model of choice
cp .env.example .env              # adjust OLLAMA_MODEL if needed
```

## Run

```bash
# One-shot
python3 main.py "list the files in my sandbox"

# Interactive
python3 main.py
```

## Verify the MCP plumbing without Ollama running

```bash
python3 -m tests.test_registry
```

This starts both tool servers, lists their tools, and calls each one once —
useful for isolating "is Ollama broken" from "is MCP broken" when debugging.

## Known constraints / honest notes

- The filesystem tool is hard-sandboxed to `FS_SANDBOX_ROOT` (default
  `./sandbox`) — it refuses any path that resolves outside that folder.
  Don't loosen this without adding real access control; giving an LLM
  unrestricted filesystem access based on prompt instructions alone is not
  a safe boundary.
- Local models (7B–8B via Ollama) are noticeably less reliable at strict
  JSON planning than hosted frontier models. Expect to tune the system
  prompt and add retry/repair logic for `Planner._parse` if you see
  malformed JSON in practice — the current fallback just treats bad JSON as
  a final answer rather than crashing.
- No GitHub/Gmail/Calendar/Docker servers are included yet. They're the
  same ~40-line pattern as `tools/duckduckgo/server.py`, but each needs real
  OAuth/API-key handling, which is where the actual engineering time in this
  project will go — not the orchestration layer, which is done.
