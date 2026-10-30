"""Scheduled-order rules. Pure functions: no I/O and no real clock."""

from datetime import UTC, datetime, timedelta

from minidash.errors import ValidationFailedError

MIN_LEAD = timedelta(minutes=45)
MAX_LEAD = timedelta(days=7)


def to_db(dt: datetime) -> str:
    """Format an aware datetime as fixed-width UTC text, so SQLite can compare it as a string."""
    if dt.tzinfo is None or dt.utcoffset() is None:
        raise ValueError("to_db() needs a timezone-aware datetime")
    return dt.astimezone(UTC).isoformat(timespec="microseconds")


def validate_schedule(scheduled_for: datetime, now: datetime) -> datetime:
    """Return scheduled_for in UTC if it is an allowed delivery time; otherwise raise.

    Allowed: has a UTC offset, and is at least 45 minutes and at most 7 days after `now`
    (both bounds inclusive).
    """
    if scheduled_for.tzinfo is None or scheduled_for.utcoffset() is None:
        raise ValidationFailedError(
            "SCHEDULE_TIMEZONE_REQUIRED",
            "scheduled_for must include a UTC offset, e.g. 2026-11-01T18:00:00Z.",
        )
    lead = scheduled_for - now
    if lead < MIN_LEAD:
        raise ValidationFailedError(
            "SCHEDULE_TOO_SOON", "scheduled_for must be at least 45 minutes from now."
        )
    if lead > MAX_LEAD:
        raise ValidationFailedError(
            "SCHEDULE_TOO_FAR", "scheduled_for must be at most 7 days from now."
        )
    return scheduled_for.astimezone(UTC)
