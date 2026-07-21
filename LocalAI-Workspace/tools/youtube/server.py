"""
YouTube MCP server.
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from mcp.server.fastmcp import FastMCP  # noqa: E402
from config.logger import get_logger  # noqa: E402
from tools.youtube.services import (  # noqa: E402
    YouTubeAuthError,
    search_youtube,
)

log = get_logger("tools.youtube")
mcp = FastMCP("youtube")


@mcp.tool()
def search_youtube_videos(query: str, max_results: int = 5) -> str:
    """
    Search for videos on YouTube.
    Returns the title, channel name, and link for each result.
    """
    try:
        videos = search_youtube(query=query, max_results=max_results)
    except YouTubeAuthError as e:
        return str(e)
    except Exception as e:
        return f"Failed to search YouTube: {e}"

    if not videos:
        return f"No YouTube videos found for '{query}'."

    lines = []
    for i, video in enumerate(videos):
        title = video['snippet']['title']
        channel = video['snippet']['channelTitle']
        video_id = video['id']['videoId']
        lines.append(f"{i+1}. {title} (by {channel}) - https://www.youtube.com/watch?v={video_id}")
        
    return "\n".join(lines)


if __name__ == "__main__":
    log.info("YouTube MCP server starting.")
    mcp.run(transport="stdio")
