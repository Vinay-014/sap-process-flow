"""
AEGIS Calendar MCP Server
Simulates Google Calendar integration for Overt plan execution.
"""

from fastmcp import FastMCP
import datetime
import random
import json

app = FastMCP("Calendar-Server")

@app.tool()
def schedule_event(
    title: str,
    start_iso: str,
    end_iso: str,
    location: str = "Remote",
    sensitive: bool = False,
    priority: str = "medium"
) -> str:
    """Schedule an event on the calendar. Returns event ID and status."""
    payload_id = f"cal_{title.lower().replace(' ', '_')}_{random.randint(1000, 9999)}"
    status = "DRAFT" if sensitive else "CONFIRMED"
    return json.dumps({
        "event_id": payload_id,
        "title": title,
        "start": start_iso,
        "end": end_iso,
        "location": location,
        "status": status,
        "priority": priority,
        "timestamp": datetime.datetime.utcnow().isoformat()
    })

@app.tool()
def list_upcoming_events(hours: int = 48) -> str:
    """List upcoming events within the specified time window."""
    now = datetime.datetime.utcnow()
    window_end = now + datetime.timedelta(hours=hours)
    return json.dumps({
        "query_window": {"start": now.isoformat(), "end": window_end.isoformat()},
        "events": [],
        "conflicts": [],
        "system_status": "NOMINAL",
        "message": f"No events in next {hours}h. Calendar clear."
    })

@app.tool()
def get_events() -> str:
    """Get all active calendar events."""
    return json.dumps({
        "status": "ACTIVE",
        "sync_established": True,
        "ready_for_orchestration": True,
        "timestamp": datetime.datetime.utcnow().isoformat()
    })

@app.tool()
def check_availability(start_iso: str, end_iso: str) -> str:
    """Check calendar availability for a time slot."""
    return json.dumps({
        "slot": {"start": start_iso, "end": end_iso},
        "available": True,
        "conflicts": [],
        "recommendation": "Slot is clear for scheduling"
    })
