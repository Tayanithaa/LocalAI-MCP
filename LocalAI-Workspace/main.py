"""
CLI entry point.

    python3 main.py "list the files in my sandbox folder"
    python3 main.py "search the web for the MCP python sdk docs"

Requires a local Ollama server running (`ollama serve`) with the configured
model pulled. See .env.example for configuration.
"""
from __future__ import annotations

import asyncio
import sys

from config.logger import get_logger
from core.orchestrator import Orchestrator
from registry.tool_registry import ToolRegistry

log = get_logger("main")


async def run_once(query: str) -> None:
    async with ToolRegistry() as registry:
        if not registry.list_tools():
            print("No tools connected -- check the logs above for errors.")
            return
        orchestrator = Orchestrator(registry)
        answer = await orchestrator.run(query)
        print("\n=== ANSWER ===")
        print(answer)


async def repl() -> None:
    async with ToolRegistry() as registry:
        orchestrator = Orchestrator(registry)
        print("Local AI Workspace ready. Type 'exit' to quit.\n")
        while True:
            try:
                query = input("you> ").strip()
            except (EOFError, KeyboardInterrupt):
                break
            if query.lower() in {"exit", "quit"}:
                break
            if not query:
                continue
            answer = await orchestrator.run(query)
            print(f"\nassistant> {answer}\n")


if __name__ == "__main__":
    if len(sys.argv) > 1:
        asyncio.run(run_once(" ".join(sys.argv[1:])))
    else:
        asyncio.run(repl())
