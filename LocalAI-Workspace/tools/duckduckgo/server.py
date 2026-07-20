"""
DuckDuckGo web search MCP server. No API key required.
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from mcp.server.fastmcp import FastMCP  # noqa: E402
from ddgs import DDGS  # noqa: E402
from config.logger import get_logger  # noqa: E402

log = get_logger("tools.duckduckgo")
mcp = FastMCP("duckduckgo")


@mcp.tool()
def web_search(query: str, max_results: int = 5) -> str:
    """Search the web via DuckDuckGo and return titles + URLs + snippets."""
    try:
        with DDGS() as ddgs:
            results = list(ddgs.text(query, max_results=max_results))
        if not results:
            return f"No results for '{query}'."
        lines = []
        for r in results:
            lines.append(f"- {r.get('title')}\n  {r.get('href')}\n  {r.get('body', '')[:200]}")
        return "\n".join(lines)
    except Exception as e:  # network errors, rate limits, etc.
        log.warning(f"web_search failed: {e}")
        return f"Search failed: {e}"


if __name__ == "__main__":
    log.info("DuckDuckGo MCP server starting.")
    mcp.run(transport="stdio")
