from datetime import UTC, datetime, time, timedelta, timezone

import pytest

from minidash.errors import ValidationFailedError
from minidash.scheduling import is_open_at, validate_schedule

DAY = ("11:00", "22:00")
OVERNIGHT = ("18:00", "02:00")
ALL_DAY = ("00:00", "00:00")


@pytest.mark.parametrize(
    "hours, t, expected",
    [
        (DAY, time(10, 59, 59), False),
        (DAY, time(11, 0), True),  # opening time is included
        (DAY, time(21, 59, 59), True),
        (DAY, time(22, 0), False),  # closing time is excluded
        (OVERNIGHT, time(17, 59, 59), False),
        (OVERNIGHT, time(18, 0), True),
        (OVERNIGHT, time(23, 59, 59), True),
        (OVERNIGHT, time(0, 0), True),  # past midnight, still open
        (OVERNIGHT, time(1, 59, 59), True),
        (OVERNIGHT, time(2, 0), False),
        (OVERNIGHT, time(12, 0), False),
        (ALL_DAY, time(0, 0), True),
        (ALL_DAY, time(12, 0), True),
        (ALL_DAY, time(23, 59, 59), True),
    ],
)
def test_ac6_is_open_at(hours, t, expected):
    assert is_open_at(*hours, t) is expected


NOW = datetime(2026, 11, 2, 12, 0, tzinfo=UTC)


def test_ac6_closed_delivery_time_is_rejected():
    with pytest.raises(ValidationFailedError) as exc:
        validate_schedule(datetime(2026, 11, 2, 22, 0, tzinfo=UTC), NOW, *DAY)
    assert exc.value.code == "RESTAURANT_CLOSED"


def test_ac6_open_delivery_time_is_accepted():
    when = datetime(2026, 11, 2, 21, 59, tzinfo=UTC)
    assert validate_schedule(when, NOW, *DAY) == when


def test_ac6_hours_are_checked_in_utc_not_the_callers_offset():
    # 17:30 in New York looks like dinner time, but it is 22:30 UTC: after closing.
    new_york = timezone(timedelta(hours=-5))
    with pytest.raises(ValidationFailedError) as exc:
        validate_schedule(datetime(2026, 11, 2, 17, 30, tzinfo=new_york), NOW, *DAY)
    assert exc.value.code == "RESTAURANT_CLOSED"


def test_lead_time_is_checked_before_opening_hours():
    # Too soon AND closed: the customer should hear about the earlier problem first.
    with pytest.raises(ValidationFailedError) as exc:
        validate_schedule(NOW + timedelta(minutes=10), NOW, "00:00", "12:05")
    assert exc.value.code == "SCHEDULE_TOO_SOON"
