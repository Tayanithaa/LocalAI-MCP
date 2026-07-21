"""
Google Drive MCP server.
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from mcp.server.fastmcp import FastMCP  # noqa: E402
from config.logger import get_logger  # noqa: E402
from tools.gdrive.services import (  # noqa: E402
    GDriveAuthError,
    list_drive_files,
)

log = get_logger("tools.gdrive")
mcp = FastMCP("gdrive")


@mcp.tool()
def search_files(query: str = "", max_results: int = 10) -> str:
    """
    Search for files in Google Drive.
    query should follow Google Drive API syntax, e.g. "name contains 'hello'" or "mimeType='application/pdf'".
    If query is empty, lists the most recent files.
    """
    try:
        files = list_drive_files(query=query, max_results=max_results)
    except GDriveAuthError as e:
        return str(e)
    except Exception as e:
        return f"Failed to search Google Drive: {e}"

    if not files:
        return "No files found."

    lines = []
    for f in files:
        lines.append(f"- {f['name']} (ID: {f['id']}, Type: {f['mimeType']})")
    return "\n".join(lines)


if __name__ == "__main__":
    log.info("Google Drive MCP server starting.")
    mcp.run(transport="stdio")
