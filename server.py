"""your-first-instrument — a sense of time for a model that has none.

Why time? Ask your Claude "how long have we been talking?" WITHOUT this
connected. It can only guess: no clock lives in a context window. This
server is the smallest honest fix — and the pattern generalizes to any
instrument you can imagine. See docs/adr/ for every choice made here.
"""
import os
from datetime import datetime, timezone
from mcp.server.fastmcp import FastMCP

mcp = FastMCP(
    "your-first-instrument",
    host="0.0.0.0",
    port=int(os.environ.get("PORT", 8000)),
)

@mcp.tool()
def current_time() -> str:
    """The current date and time (UTC and local)."""
    now = datetime.now(timezone.utc)
    return f"UTC: {now.isoformat()} · local: {datetime.now().isoformat()}"

@mcp.tool()
def seconds_since(iso_timestamp: str) -> str:
    """Seconds elapsed since an ISO timestamp (e.g. '2026-09-10T17:15:00')."""
    then = datetime.fromisoformat(iso_timestamp)
    if then.tzinfo is None:
        then = then.replace(tzinfo=timezone.utc)
    delta = datetime.now(timezone.utc) - then
    return f"{delta.total_seconds():.0f} seconds ({delta})"

# Add entries as (name, ISO 8601 timestamp with UTC offset) once real
# deadlines are known — COURSE-STEPS.md doesn't list any yet.
DEADLINES: list[tuple[str, str]] = []

@mcp.tool()
def next_deadline() -> str:
    """The nearest upcoming course deadline and time remaining until it."""
    now = datetime.now(timezone.utc)
    upcoming = []
    for name, iso_timestamp in DEADLINES:
        due = datetime.fromisoformat(iso_timestamp)
        if due.tzinfo is None:
            due = due.replace(tzinfo=timezone.utc)
        if due >= now:
            upcoming.append((due, name))
    if not upcoming:
        return "No deadlines configured"
    due, name = min(upcoming)
    delta = due - now
    return f"{name}: due {due.isoformat()} ({delta} remaining)"

if __name__ == "__main__":
    mcp.run(transport="streamable-http")
