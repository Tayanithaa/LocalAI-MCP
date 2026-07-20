"""
OAuth handling for Google Calendar, kept separate from server.py so the
credential flow can be reused/tested independently of the MCP tool
definitions.

First run: opens a browser for you to log in and grant calendar access,
then caches the resulting token in token.json so subsequent runs are
silent (auto-refreshing when the access token expires).
"""
from __future__ import annotations

from pathlib import Path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

HERE = Path(__file__).resolve().parent
CREDENTIALS_PATH = HERE / "credentials.json"
TOKEN_PATH = HERE / "token.json"

# Read-only isn't enough since we also create events; this is the minimum
# scope that covers both listing and creating.
SCOPES = ["https://www.googleapis.com/auth/calendar"]


class CalendarAuthError(RuntimeError):
    pass


def get_calendar_service():
    """Return an authenticated Google Calendar API service object."""
    if not CREDENTIALS_PATH.exists():
        raise CalendarAuthError(
            f"Missing {CREDENTIALS_PATH}. Download an OAuth 'Desktop app' "
            f"client ID from Google Cloud Console and save it there as "
            f"'credentials.json'."
        )

    creds: Credentials | None = None
    if TOKEN_PATH.exists():
        creds = Credentials.from_authorized_user_file(str(TOKEN_PATH), SCOPES)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(str(CREDENTIALS_PATH), SCOPES)
            creds = flow.run_local_server(port=0)
        TOKEN_PATH.write_text(creds.to_json())

    return build("calendar", "v3", credentials=creds)
