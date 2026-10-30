"""Scheduled-order rules. Pure functions: no I/O and no real clock."""

from datetime import UTC, datetime


def to_db(dt: datetime) -> str:
    """Format an aware datetime as fixed-width UTC text, so SQLite can compare it as a string."""
    if dt.tzinfo is None or dt.utcoffset() is None:
        raise ValueError("to_db() needs a timezone-aware datetime")
    return dt.astimezone(UTC).isoformat(timespec="microseconds")
