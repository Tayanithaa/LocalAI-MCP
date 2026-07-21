"""
Google Drive service layer.
"""
from __future__ import annotations

from typing import Any

from tools.gdrive.auth import get_gdrive_service, GDriveAuthError

__all__ = [
    "GDriveAuthError",
    "list_drive_files",
]


def list_drive_files(query: str = "", max_results: int = 10) -> list[dict[str, Any]]:
    """
    Search for files in Google Drive.
    """
    service = get_gdrive_service()
    
    # query is something like "name contains 'Project'"
    results = service.files().list(
        q=query if query else None,
        pageSize=max_results,
        fields="nextPageToken, files(id, name, mimeType)"
    ).execute()
    
    return results.get('files', [])
