"""
Gmail service layer.

Plain functions that talk to the Gmail API, with no MCP/@mcp.tool
decoration here. server.py wraps these as MCP tools; tests or other code
can import and call them directly without spinning up an MCP server.
"""
from __future__ import annotations

import base64
from email.message import EmailMessage
from typing import Any

from tools.gmail.auth import get_gmail_service, GmailAuthError

__all__ = [
    "GmailAuthError",
    "list_recent_emails",
    "send_email",
]


def list_recent_emails(max_results: int = 5) -> list[dict[str, Any]]:
    """
    Return recent emails from the primary inbox as a list of parsed dictionaries.
    Raises GmailAuthError if credentials aren't set up.
    """
    service = get_gmail_service()

    # Get a list of recent message IDs
    results = service.users().messages().list(userId='me', maxResults=max_results).execute()
    messages = results.get('messages', [])

    if not messages:
        return []

    parsed_emails = []
    for msg in messages:
        # Fetch the full message detail
        msg_detail = service.users().messages().get(userId='me', id=msg['id'], format='full').execute()
        headers = msg_detail.get("payload", {}).get("headers", [])
        
        subject = next((h["value"] for h in headers if h["name"].lower() == "subject"), "(no subject)")
        sender = next((h["value"] for h in headers if h["name"].lower() == "from"), "(unknown sender)")
        date = next((h["value"] for h in headers if h["name"].lower() == "date"), "(unknown date)")
        
        # Simple extraction of body (first plain text part)
        snippet = msg_detail.get("snippet", "")
        
        parsed_emails.append({
            "id": msg['id'],
            "subject": subject,
            "sender": sender,
            "date": date,
            "snippet": snippet
        })

    return parsed_emails


def send_email(to: str, subject: str, body: str) -> dict[str, Any]:
    """
    Drafts and sends an email. 
    Returns the raw created message dict from the Gmail API.
    """
    service = get_gmail_service()

    message = EmailMessage()
    message.set_content(body)
    message["To"] = to
    message["From"] = "me"
    message["Subject"] = subject

    encoded_message = base64.urlsafe_b64encode(message.as_bytes()).decode()
    create_message = {"raw": encoded_message}

    send_message = (
        service.users().messages().send(userId="me", body=create_message).execute()
    )
    
    return send_message
