"""
Tool registry.

Each entry in TOOL_SERVERS points at a standalone MCP server script
(tools/<name>/server.py). The registry launches each one as a subprocess
over stdio, asks it what tools it exposes, and gives the planner/executor a
single flat namespace like "filesystem.read_file" to call.

Adding a new integration (GitHub, Gmail, Docker, ...) means writing one more
tools/<name>/server.py following the same @mcp.tool() pattern used in
tools/filesystem/server.py and tools/duckduckgo/server.py, then adding one
line here. Nothing else in the codebase changes.
"""
from __future__ import annotations

import sys
from contextlib import AsyncExitStack
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

from config.logger import get_logger

log = get_logger("registry.tool_registry")

REPO_ROOT = Path(__file__).resolve().parents[1]

# name -> path to the server script. Extend this dict to add new plugins.
TOOL_SERVERS: dict[str, Path] = {
    #"filesystem": REPO_ROOT / "tools" / "filesystem" / "server.py",
    #"duckduckgo": REPO_ROOT / "tools" / "duckduckgo" / "server.py",
    "calendar": REPO_ROOT / "tools" / "calendar" / "server.py",
    "github": REPO_ROOT / "tools" / "github" / "server.py",
    "gmail": REPO_ROOT / "tools" / "gmail" / "server.py",
    "gdrive": REPO_ROOT / "tools" / "gdrive" / "server.py",
    "gdocs": REPO_ROOT / "tools" / "gdocs" / "server.py",
    "gmeet": REPO_ROOT / "tools" / "gmeet" / "server.py",
    "spotify": REPO_ROOT / "tools" / "spotify" / "server.py",
    "youtube": REPO_ROOT / "tools" / "youtube" / "server.py",
    # "docker": REPO_ROOT / "tools" / "docker" / "server.py",
}


@dataclass
class ToolSpec:
    server: str
    name: str
    description: str
    input_schema: dict[str, Any]

    @property
    def qualified_name(self) -> str:
        return f"{self.server}.{self.name}"


class ToolRegistry:
    """
    Owns one live MCP ClientSession per configured server for the lifetime
    of the process. Use as an async context manager:

        async with ToolRegistry() as registry:
            tools = registry.list_tools()
            result = await registry.call("filesystem.list_files", {})
    """

    def __init__(self, servers: dict[str, Path] | None = None):
        self._server_paths = servers or TOOL_SERVERS
        self._stack = AsyncExitStack()
        self._sessions: dict[str, ClientSession] = {}
        self._tools: dict[str, ToolSpec] = {}

    async def __aenter__(self) -> "ToolRegistry":
        for server_name, script_path in self._server_paths.items():
            if not script_path.exists():
                log.warning(f"Skipping '{server_name}': {script_path} not found.")
                continue
            try:
                await self._connect(server_name, script_path)
            except Exception as e:
                log.error(f"Failed to start MCP server '{server_name}': {e}")
        return self

    async def __aexit__(self, *exc):
        await self._stack.aclose()

    async def _connect(self, server_name: str, script_path: Path) -> None:
        params = StdioServerParameters(command=sys.executable, args=[str(script_path)])
        read, write = await self._stack.enter_async_context(stdio_client(params))
        session = await self._stack.enter_async_context(ClientSession(read, write))
        await session.initialize()

        listing = await session.list_tools()
        for tool in listing.tools:
            spec = ToolSpec(
                server=server_name,
                name=tool.name,
                description=tool.description or "",
                input_schema=tool.inputSchema or {},
            )
            self._tools[spec.qualified_name] = spec

        self._sessions[server_name] = session
        log.info(f"Connected '{server_name}': {[t.name for t in listing.tools]}")

    def list_tools(self) -> list[ToolSpec]:
        return list(self._tools.values())

    def describe_tools_for_prompt(self) -> str:
        """Render available tools as a compact block for the planner prompt."""
        lines = []
        for spec in self._tools.values():
            props = spec.input_schema.get("properties", {})
            args = ", ".join(props.keys()) if props else "(no arguments)"
            lines.append(f"- {spec.qualified_name}({args}): {spec.description}")
        return "\n".join(lines) if lines else "(no tools available)"

    async def call(self, qualified_name: str, arguments: dict[str, Any]) -> str:
        spec = self._tools.get(qualified_name)

        if spec is None:
            # Common failure mode with small local models: they name the
            # server ("calendar") instead of the full "server.tool" name.
            # Give back something the planner can actually correct itself
            # from, instead of a bare "unknown tool" that just repeats.
            same_server = [n for n in self._tools if n.startswith(f"{qualified_name}.")]
            if len(same_server) == 1:
                spec = self._tools[same_server[0]]  # unambiguous -- just resolve it
            elif same_server:
                return (
                    f"Error: '{qualified_name}' is a server name, not a tool name. "
                    f"That server has multiple tools -- call one of these exact "
                    f"names instead: {', '.join(same_server)}"
                )
            else:
                return (
                    f"Error: unknown tool '{qualified_name}'. Valid tool names are: "
                    f"{', '.join(sorted(self._tools.keys()))}"
                )

        session = self._sessions[spec.server]
        result = await session.call_tool(spec.name, arguments)
        parts = [c.text for c in result.content if hasattr(c, "text")]
        return "\n".join(parts) if parts else "(tool returned no content)"