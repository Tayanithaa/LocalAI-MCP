"""
Gmail MCP server. Thin @mcp.tool() wrappers around
tools.gmail.services -- the actual Gmail API logic lives there so it
can be tested independently of MCP.
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from mcp.server.fastmcp import FastMCP  # noqa: E402
from config.logger import get_logger  # noqa: E402
from tools.gmail.services import (  # noqa: E402
    GmailAuthError,
    list_recent_emails,
    send_email,
)

log = get_logger("tools.gmail")
mcp = FastMCP("gmail")


@mcp.tool()
def list_emails(max_results: int = 5) -> str:
    """List recent emails from your primary inbox."""
    try:
        emails = list_recent_emails(max_results=max_results)
    except GmailAuthError as e:
        return str(e)

    if not emails:
        return f"No recent emails found."

    lines = []
    for e in emails:
        lines.append(f"- [{e['date']}] From: {e['sender']}")
        lines.append(f"  Subject: {e['subject']}")
        lines.append(f"  Snippet: {e['snippet']}...")
    return "\n".join(lines)


@mcp.tool()
def send_new_email(to: str, subject: str, body: str) -> str:
    """
    Drafts and sends a new email.
    """
    try:
        sent = send_email(to=to, subject=subject, body=body)
    except GmailAuthError as e:
        return str(e)
    except Exception as e:
        return f"Failed to send email: {e}"
        
    return f"Successfully sent email to '{to}' (id: {sent.get('id')})."


if __name__ == "__main__":
    log.info("Gmail MCP server starting.")
    mcp.run(transport="stdio")
