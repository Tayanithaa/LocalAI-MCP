"""
Google Meet service layer.
"""
from __future__ import annotations

from typing import Any

from tools.gmeet.auth import get_gmeet_service, GMeetAuthError

__all__ = [
    "GMeetAuthError",
    "create_meet_space",
]


def create_meet_space() -> dict[str, Any]:
    """
    Create a new empty Google Meet space.
    """
    service = get_gmeet_service()
    # Provide an empty body to create a space
    space = service.spaces().create(body={}).execute()
    return space
