"""Scheduled-order rules. Pure functions: no I/O and no real clock."""

from datetime import UTC, datetime, time, timedelta

from minidash.errors import ValidationFailedError

MIN_LEAD = timedelta(minutes=45)
MAX_LEAD = timedelta(days=7)
RELEASE_BEFORE = timedelta(minutes=30)


def to_db(dt: datetime) -> str:
    """Format an aware datetime as fixed-width UTC text, so SQLite can compare it as a string."""
    if dt.tzinfo is None or dt.utcoffset() is None:
        raise ValueError("to_db() needs a timezone-aware datetime")
    return dt.astimezone(UTC).isoformat(timespec="microseconds")


def release_cutoff(now: datetime) -> datetime:
    """Orders scheduled at or before this time are due for the kitchen."""
    return now + RELEASE_BEFORE


def is_open_at(opens_at: str, closes_at: str, t: time) -> bool:
    """True if `t` (UTC) is within [opens_at, closes_at).

    Hours wrap past midnight when closes_at < opens_at (e.g. 18:00-02:00);
    equal times mean the restaurant is open 24 hours.
    """
    opens, closes = time.fromisoformat(opens_at), time.fromisoformat(closes_at)
    if opens == closes:
        return True
    if opens < closes:
        return opens <= t < closes
    return t >= opens or t < closes


def validate_schedule(
    scheduled_for: datetime, now: datetime, opens_at: str, closes_at: str
) -> datetime:
    """Return scheduled_for in UTC if it is an allowed delivery time; otherwise raise.

    Allowed: has a UTC offset, is at least 45 minutes and at most 7 days after `now`
    (both bounds inclusive), and the restaurant is open at that time.
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
    utc = scheduled_for.astimezone(UTC)
    if not is_open_at(opens_at, closes_at, utc.time()):
        raise ValidationFailedError(
            "RESTAURANT_CLOSED",
            f"The restaurant is closed at that time (open {opens_at}-{closes_at} UTC).",
        )
    return utc
