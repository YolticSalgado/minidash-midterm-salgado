import asyncio
import time
from datetime import UTC, datetime

from fastapi.testclient import TestClient

from minidash.app import create_app
from minidash.worker import run_release_loop

ORDER = {
    "restaurant_id": 1,
    "items": [{"menu_item_id": 1, "quantity": 1}],
    "address": "1 Main St",
    "scheduled_for": "2026-11-02T18:00:00Z",
}
DUE = datetime(2026, 11, 2, 17, 30, tzinfo=UTC)


def run_loop(release_once, interval, stop):
    asyncio.run(asyncio.wait_for(run_release_loop(release_once, interval, stop), timeout=2))


def test_loop_calls_release_every_interval_until_stopped():
    stop = asyncio.Event()
    calls = []

    def release_once():
        calls.append(1)
        if len(calls) == 3:
            stop.set()

    run_loop(release_once, 0.01, stop)
    assert len(calls) == 3


def test_loop_survives_a_failing_pass():
    stop = asyncio.Event()
    calls = []

    def release_once():
        calls.append(1)
        if len(calls) == 1:
            raise RuntimeError("database busy")
        stop.set()

    run_loop(release_once, 0.01, stop)
    assert len(calls) == 2


def test_loop_exits_without_waiting_a_full_interval_when_stopped():
    stop = asyncio.Event()
    stop.set()
    started = time.monotonic()
    run_loop(lambda: None, 60, stop)
    assert time.monotonic() - started < 1


def test_ac7_startup_catches_up_on_orders_that_came_due_while_down(db_path, clock):
    with TestClient(create_app(db_path, clock=clock)) as client:
        order_id = client.post("/orders", json=ORDER).json()["id"]

    clock.current = DUE  # the app was "down" until 17:30
    with TestClient(create_app(db_path, clock=clock)) as client:
        assert client.get(f"/orders/{order_id}").json()["status"] == "PLACED"


def test_ac7_running_app_releases_when_order_comes_due(db_path, clock):
    with TestClient(create_app(db_path, clock=clock, release_interval_seconds=0.05)) as client:
        order_id = client.post("/orders", json=ORDER).json()["id"]
        assert client.get(f"/orders/{order_id}").json()["status"] == "SCHEDULED"

        clock.current = DUE
        deadline = time.monotonic() + 2
        while time.monotonic() < deadline:
            if client.get(f"/orders/{order_id}").json()["status"] == "PLACED":
                break
            time.sleep(0.02)
        assert client.get(f"/orders/{order_id}").json()["status"] == "PLACED"
