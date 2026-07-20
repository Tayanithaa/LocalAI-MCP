"""
Smoke test for the MCP plumbing, independent of Ollama. Run with:
    python3 -m tests.test_registry
"""
import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from registry.tool_registry import ToolRegistry  # noqa: E402


async def main() -> None:
    async with ToolRegistry() as registry:
        tools = registry.list_tools()
        assert tools, "No tools discovered -- MCP servers failed to start."
        print(f"Discovered {len(tools)} tools:")
        print(registry.describe_tools_for_prompt())

        # filesystem.list_files should work with zero real state
        result = await registry.call("filesystem.list_files", {"subdirectory": "."})
        print("\nfilesystem.list_files(.) ->", repr(result))

        # duckduckgo.web_search hits the network; skip assertion on content,
        # just confirm the round trip doesn't crash.
        result = await registry.call("duckduckgo.web_search", {"query": "MCP protocol", "max_results": 2})
        print("\nduckduckgo.web_search(...) ->", result[:200])

    print("\nOK: registry connected, discovered tools, and executed calls.")


if __name__ == "__main__":
    asyncio.run(main())
