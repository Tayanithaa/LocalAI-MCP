"""
Google Docs MCP server.
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from mcp.server.fastmcp import FastMCP  # noqa: E402
from config.logger import get_logger  # noqa: E402
from tools.gdocs.services import (  # noqa: E402
    GDocsAuthError,
    read_document,
    create_document,
)

log = get_logger("tools.gdocs")
mcp = FastMCP("gdocs")


@mcp.tool()
def get_document_text(document_id: str) -> str:
    """
    Read all the text content from a Google Document given its ID.
    """
    try:
        text = read_document(document_id)
    except GDocsAuthError as e:
        return str(e)
    except Exception as e:
        return f"Failed to read document: {e}"

    if not text.strip():
        return "Document is empty."
    
    # Truncate if insanely large to save context
    max_chars = 10000
    if len(text) > max_chars:
        return text[:max_chars] + "... [truncated]"
    return text


@mcp.tool()
def create_new_document(title: str) -> str:
    """
    Create a new blank Google Document and return its ID and URL.
    """
    try:
        doc = create_document(title)
    except GDocsAuthError as e:
        return str(e)
    except Exception as e:
        return f"Failed to create document: {e}"

    return f"Created document '{title}'.\nID: {doc.get('documentId')}"


if __name__ == "__main__":
    log.info("Google Docs MCP server starting.")
    mcp.run(transport="stdio")
