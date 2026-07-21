"""
Google Meet MCP server.
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from mcp.server.fastmcp import FastMCP  # noqa: E402
from config.logger import get_logger  # noqa: E402
from tools.gmeet.services import (  # noqa: E402
    GMeetAuthError,
    create_meet_space,
)

log = get_logger("tools.gmeet")
mcp = FastMCP("gmeet")


@mcp.tool()
def create_meet_link() -> str:
    """
    Create a new standalone Google Meet meeting link.
    """
    try:
        space = create_meet_space()
    except GMeetAuthError as e:
        return str(e)
    except Exception as e:
        return f"Failed to create Google Meet: {e}"

    return f"Created meeting space.\nJoin Link: {space.get('meetingUri')}\nMeeting Code: {space.get('meetingCode')}"


if __name__ == "__main__":
    log.info("Google Meet MCP server starting.")
    mcp.run(transport="stdio")
