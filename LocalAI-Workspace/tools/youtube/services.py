"""
YouTube service layer.
"""
from __future__ import annotations

from typing import Any

from tools.youtube.auth import get_youtube_service, YouTubeAuthError

__all__ = [
    "YouTubeAuthError",
    "search_youtube",
]


def search_youtube(query: str, max_results: int = 5) -> list[dict[str, Any]]:
    """
    Search for videos on YouTube.
    """
    service = get_youtube_service()
    
    # query the YouTube Data API
    request = service.search().list(
        part="snippet",
        maxResults=max_results,
        q=query,
        type="video"
    )
    response = request.execute()
    
    return response.get('items', [])
