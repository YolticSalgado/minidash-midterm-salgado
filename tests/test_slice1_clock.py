from datetime import UTC, datetime, timedelta, timezone

import pytest

from minidash.clock import SystemClock
from minidash.scheduling import to_db

ORDER = {"restaurant_id": 1, "items": [{"menu_item_id": 1, "quantity": 1}], "address": "1 Main St"}


def test_ac12_created_at_comes_from_injected_clock(client, clock):
    clock.current = datetime(2026, 11, 2, 13, 15, 30, tzinfo=UTC)
    body = client.post("/orders", json=ORDER).json()
    assert body["created_at"] == "2026-11-02T13:15:30.000000+00:00"


def test_to_db_uses_fixed_width_utc_text():
    assert to_db(datetime(2026, 11, 2, 12, 0, tzinfo=UTC)) == "2026-11-02T12:00:00.000000+00:00"


def test_to_db_converts_other_offsets_to_utc():
    new_york = timezone(timedelta(hours=-5))
    assert to_db(datetime(2026, 11, 2, 7, 0, tzinfo=new_york)) == "2026-11-02T12:00:00.000000+00:00"


def test_to_db_rejects_naive_datetime():
    with pytest.raises(ValueError):
        to_db(datetime(2026, 11, 2, 12, 0))


def test_system_clock_returns_aware_utc():
    assert SystemClock().now().utcoffset() == timedelta(0)
