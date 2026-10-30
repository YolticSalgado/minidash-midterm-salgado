from datetime import UTC, datetime, timedelta, timezone

import pytest

from minidash.errors import ValidationFailedError
from minidash.scheduling import validate_schedule

NOW = datetime(2026, 11, 2, 12, 0, tzinfo=UTC)
ALWAYS_OPEN = ("00:00", "00:00")  # keep opening hours out of these lead-time tests


def error_code(scheduled_for):
    with pytest.raises(ValidationFailedError) as exc:
        validate_schedule(scheduled_for, NOW, *ALWAYS_OPEN)
    return exc.value.code


@pytest.mark.parametrize(
    "lead",
    [
        timedelta(minutes=44, seconds=59),
        timedelta(minutes=44),
        timedelta(0),
        timedelta(hours=-1),  # in the past
    ],
)
def test_ac3_less_than_45_minutes_is_too_soon(lead):
    assert error_code(NOW + lead) == "SCHEDULE_TOO_SOON"


@pytest.mark.parametrize(
    "lead",
    [
        timedelta(minutes=45),  # lower bound, inclusive
        timedelta(minutes=46),
        timedelta(days=3),
        timedelta(days=7),  # upper bound, inclusive
    ],
)
def test_ac2_lead_between_45_minutes_and_7_days_is_accepted(lead):
    assert validate_schedule(NOW + lead, NOW, *ALWAYS_OPEN) == NOW + lead


@pytest.mark.parametrize("lead", [timedelta(days=7, seconds=1), timedelta(days=8)])
def test_ac4_more_than_7_days_is_too_far(lead):
    assert error_code(NOW + lead) == "SCHEDULE_TOO_FAR"


def test_ac5_naive_time_is_rejected():
    assert error_code(datetime(2026, 11, 2, 18, 0)) == "SCHEDULE_TIMEZONE_REQUIRED"


def test_other_offset_is_returned_as_utc():
    new_york = timezone(timedelta(hours=-5))
    result = validate_schedule(datetime(2026, 11, 2, 13, 0, tzinfo=new_york), NOW, *ALWAYS_OPEN)
    assert result == datetime(2026, 11, 2, 18, 0, tzinfo=UTC)
    assert result.utcoffset() == timedelta(0)
