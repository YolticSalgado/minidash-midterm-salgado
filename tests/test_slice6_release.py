from contextlib import closing
from datetime import UTC, datetime

import pytest

from minidash.db import connect
from minidash.services import release_due_orders

ORDER = {"restaurant_id": 1, "items": [{"menu_item_id": 1, "quantity": 1}], "address": "1 Main St"}


@pytest.fixture
def release(db_path):
    """Run one release pass at the given UTC time, like the background loop does."""

    def run(hh, mm, ss=0):
        with closing(connect(db_path)) as conn:
            return release_due_orders(conn, datetime(2026, 11, 2, hh, mm, ss, tzinfo=UTC))

    return run


def schedule(client, when):
    return client.post("/orders", json={**ORDER, "scheduled_for": when}).json()["id"]


def status(client, order_id):
    return client.get(f"/orders/{order_id}").json()["status"]


def test_ac8_not_released_one_second_early(client, release):
    order_id = schedule(client, "2026-11-02T18:00:00Z")
    assert release(17, 29, 59) == []
    assert status(client, order_id) == "SCHEDULED"


def test_ac7_released_at_exactly_30_minutes_before(client, release):
    order_id = schedule(client, "2026-11-02T18:00:00Z")
    assert release(17, 30) == [order_id]
    assert status(client, order_id) == "PLACED"


def test_ac7_second_run_releases_nothing(client, release):
    order_id = schedule(client, "2026-11-02T18:00:00Z")
    assert release(17, 30) == [order_id]
    assert release(17, 30) == []
    assert release(17, 45) == []
    assert status(client, order_id) == "PLACED"


def test_ac7_only_due_scheduled_orders_move(client, release):
    due = schedule(client, "2026-11-02T18:00:00Z")
    later = schedule(client, "2026-11-02T20:00:00Z")
    preparing = client.post("/orders", json=ORDER).json()["id"]
    client.patch(f"/orders/{preparing}/status", json={"status": "PREPARING"})

    assert release(17, 30) == [due]
    assert status(client, later) == "SCHEDULED"
    assert status(client, preparing) == "PREPARING"


def test_ac8_sub_second_boundary_compares_correctly(client, release):
    # Fixed-width UTC text must order correctly even with microseconds.
    order_id = schedule(client, "2026-11-02T18:00:00.000001Z")
    assert release(17, 30) == []
    assert status(client, order_id) == "SCHEDULED"
