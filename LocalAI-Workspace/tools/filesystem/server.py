"""
Filesystem MCP server.

Exposes three tools over MCP (stdio transport): list_files, read_file,
search_files. Everything is sandboxed to config.settings.fs_sandbox_root so a
bad plan from the LLM can't walk the tool outside the intended folder --
this is the one piece of "AI assistant touches your disk" that actually
needs a hard boundary, not just a prompt asking it to behave.
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))  # repo root

from mcp.server.fastmcp import FastMCP  # noqa: E402
from config.settings import settings  # noqa: E402
from config.logger import get_logger  # noqa: E402

log = get_logger("tools.filesystem")
mcp = FastMCP("filesystem")

ROOT = settings.fs_sandbox_root


def _resolve_safe(relative_path: str) -> Path:
    """Resolve a path and guarantee it stays inside ROOT. Raises on escape."""
    candidate = (ROOT / relative_path).resolve()
    if ROOT not in candidate.parents and candidate != ROOT:
        raise ValueError(
            f"Path '{relative_path}' resolves outside the sandboxed root. Refused."
        )
    return candidate


@mcp.tool()
def list_files(subdirectory: str = ".") -> str:
    """List files and folders under the given subdirectory of the sandbox root."""
    try:
        target = _resolve_safe(subdirectory)
        if not target.exists():
            return f"'{subdirectory}' does not exist under the sandbox root."
        entries = sorted(p.name + ("/" if p.is_dir() else "") for p in target.iterdir())
        return "\n".join(entries) if entries else "(empty directory)"
    except ValueError as e:
        return str(e)


@mcp.tool()
def read_file(relative_path: str, max_chars: int = 4000) -> str:
    """Read a text file's contents (truncated to max_chars) from the sandbox root."""
    try:
        target = _resolve_safe(relative_path)
        if not target.is_file():
            return f"'{relative_path}' is not a file under the sandbox root."
        text = target.read_text(errors="replace")
        return text[:max_chars] + ("... [truncated]" if len(text) > max_chars else "")
    except ValueError as e:
        return str(e)


@mcp.tool()
def search_files(query: str, subdirectory: str = ".") -> str:
    """Recursively search filenames under subdirectory for a substring match."""
    try:
        target = _resolve_safe(subdirectory)
        matches = [
            str(p.relative_to(ROOT))
            for p in target.rglob("*")
            if query.lower() in p.name.lower()
        ]
        return "\n".join(matches) if matches else f"No filenames matched '{query}'."
    except ValueError as e:
        return str(e)


if __name__ == "__main__":
    log.info(f"Filesystem MCP server starting. Sandbox root: {ROOT}")
    mcp.run(transport="stdio")
