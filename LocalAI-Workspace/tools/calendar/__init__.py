"""
tools.calendar -- Google Calendar integration.

- auth.py:     OAuth credential loading/caching (get_calendar_service).
- services.py: Plain functions wrapping Calendar API calls, importable
               and testable without MCP.
- server.py:   MCP tool server -- thin @mcp.tool() wrappers around
               services.py, run as a stdio subprocess by the tool registry.
"""
from tools.calendar.services import (
    CalendarAuthError,
    list_upcoming_events,
    create_calendar_event,
    delete_calendar_event,
)

__all__ = [
    "CalendarAuthError",
    "list_upcoming_events",
    "create_calendar_event",
    "delete_calendar_event",
]
