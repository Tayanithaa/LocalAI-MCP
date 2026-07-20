"""
Google Calendar MCP server. Thin @mcp.tool() wrappers around
tools.calendar.services -- the actual Calendar API logic lives there so it
can be tested independently of MCP. See tools/filesystem/server.py and
tools/duckduckgo/server.py for the same pattern.
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from mcp.server.fastmcp import FastMCP  # noqa: E402
from config.logger import get_logger  # noqa: E402
from tools.calendar.services import (  # noqa: E402
    CalendarAuthError,
    list_upcoming_events,
    create_calendar_event,
    delete_calendar_event,
)

log = get_logger("tools.calendar")
mcp = FastMCP("calendar")


@mcp.tool()
def list_events(max_results: int = 10, days_ahead: int = 7) -> str:
    """List upcoming calendar events within the next `days_ahead` days."""
    try:
        events = list_upcoming_events(max_results=max_results, days_ahead=days_ahead)
    except CalendarAuthError as e:
        return str(e)

    if not events:
        return f"No events in the next {days_ahead} day(s)."

    lines = []
    for e in events:
        start = e["start"].get("dateTime", e["start"].get("date"))
        lines.append(f"- [{e['id']}] {start}: {e.get('summary', '(no title)')}")
    return "\n".join(lines)


@mcp.tool()
def create_event(
    summary: str,
    start_datetime: str,
    end_datetime: str,
    description: str = "",
    timezone: str = "UTC",
) -> str:
    """
    Create a calendar event.
    start_datetime / end_datetime must be ISO 8601, e.g. '2026-07-20T15:00:00'.
    """
    try:
        created = create_calendar_event(
            summary=summary,
            start_datetime=start_datetime,
            end_datetime=end_datetime,
            description=description,
            timezone=timezone,
        )
    except CalendarAuthError as e:
        return str(e)
    return f"Created event '{summary}' (id: {created['id']}): {created.get('htmlLink')}"


@mcp.tool()
def delete_event(event_id: str) -> str:
    """Delete a calendar event by its id (as returned by list_events)."""
    try:
        delete_calendar_event(event_id)
    except CalendarAuthError as e:
        return str(e)
    except Exception as e:
        return f"Failed to delete event {event_id}: {e}"
    return f"Deleted event {event_id}."


if __name__ == "__main__":
    log.info("Google Calendar MCP server starting.")
    mcp.run(transport="stdio")
