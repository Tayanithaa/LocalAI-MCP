"""
OAuth handling for Google Meet.
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

SCOPES = [
    "https://www.googleapis.com/auth/meetings.space.created"
]

class GMeetAuthError(RuntimeError):
    pass

def get_gmeet_service():
    """Return an authenticated Google Meet API service object."""
    if not CREDENTIALS_PATH.exists():
        raise GMeetAuthError(
            f"Missing {CREDENTIALS_PATH}. Please copy credentials.json here."
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

    # Note: Meet REST API is 'meet', 'v2'
    return build("meet", "v2", credentials=creds)
