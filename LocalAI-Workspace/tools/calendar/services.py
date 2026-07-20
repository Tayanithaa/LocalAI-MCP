"""
Google Calendar service layer.

Plain functions that talk to the Calendar API, with no MCP/@mcp.tool
decoration here. server.py wraps these as MCP tools; tests or other code
can import and call them directly without spinning up an MCP server.
"""
from __future__ import annotations

from datetime import datetime, timedelta
from typing import Any

from tools.calendar.auth import get_calendar_service, CalendarAuthError

__all__ = [
    "CalendarAuthError",
    "list_upcoming_events",
    "create_calendar_event",
    "delete_calendar_event",
]


def list_upcoming_events(max_results: int = 10, days_ahead: int = 7) -> list[dict[str, Any]]:
    """
    Return upcoming events on the primary calendar within the next
    `days_ahead` days, as a list of raw event dicts from the Calendar API.
    Raises CalendarAuthError if credentials aren't set up.
    """
    service = get_calendar_service()

    now = datetime.utcnow().isoformat() + "Z"
    time_max = (datetime.utcnow() + timedelta(days=days_ahead)).isoformat() + "Z"

    events_result = service.events().list(
        calendarId="primary",
        timeMin=now,
        timeMax=time_max,
        maxResults=max_results,
        singleEvents=True,
        orderBy="startTime",
    ).execute()

    return events_result.get("items", [])


def create_calendar_event(
    summary: str,
    start_datetime: str,
    end_datetime: str,
    description: str = "",
    timezone: str = "UTC",
) -> dict[str, Any]:
    """
    Create an event on the primary calendar. start_datetime / end_datetime
    must be ISO 8601 (e.g. '2026-07-20T15:00:00'). Returns the raw created
    event dict from the Calendar API (includes 'id' and 'htmlLink').
    """
    service = get_calendar_service()

    event_body = {
        "summary": summary,
        "description": description,
        "start": {"dateTime": start_datetime, "timeZone": timezone},
        "end": {"dateTime": end_datetime, "timeZone": timezone},
    }
    return service.events().insert(calendarId="primary", body=event_body).execute()


def delete_calendar_event(event_id: str) -> None:
    """Delete an event by id from the primary calendar. Raises on failure."""
    service = get_calendar_service()
    service.events().delete(calendarId="primary", eventId=event_id).execute()
