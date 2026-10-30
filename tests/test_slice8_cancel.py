from contextlib import closing
from datetime import UTC, datetime

from minidash.db import connect
from minidash.services import release_due_orders

ORDER = {"restaurant_id": 1, "items": [{"menu_item_id": 1, "quantity": 1}], "address": "1 Main St"}
SCHEDULED = {**ORDER, "scheduled_for": "2026-11-02T18:00:00Z"}
DUE = datetime(2026, 11, 2, 17, 30, tzinfo=UTC)


def release_at_due_time(db_path):
    with closing(connect(db_path)) as conn:
        return release_due_orders(conn, DUE)


def status(client, order_id):
    return client.get(f"/orders/{order_id}").json()["status"]


def test_ac9_cancel_scheduled_order_and_it_is_never_released(client, db_path):
    order_id = client.post("/orders", json=SCHEDULED).json()["id"]

    resp = client.post(f"/orders/{order_id}/cancel")
    assert resp.status_code == 200
    assert resp.json()["status"] == "CANCELLED"

    assert release_at_due_time(db_path) == []
    assert status(client, order_id) == "CANCELLED"


def test_ac10_cancel_after_release_is_409_and_order_unchanged(client, db_path):
    order_id = client.post("/orders", json=SCHEDULED).json()["id"]
    release_at_due_time(db_path)

    resp = client.post(f"/orders/{order_id}/cancel")
    assert resp.status_code == 409
    assert resp.json()["error"]["code"] == "ORDER_NOT_CANCELLABLE"
    assert status(client, order_id) == "PLACED"


def test_ac10_cancel_immediate_order_is_409(client):
    order_id = client.post("/orders", json=ORDER).json()["id"]
    assert client.post(f"/orders/{order_id}/cancel").status_code == 409
    assert status(client, order_id) == "PLACED"


def test_ac10_cancelling_twice_is_409(client):
    order_id = client.post("/orders", json=SCHEDULED).json()["id"]
    assert client.post(f"/orders/{order_id}/cancel").status_code == 200
    assert client.post(f"/orders/{order_id}/cancel").status_code == 409


def test_cancel_unknown_order_is_404(client):
    resp = client.post("/orders/999/cancel")
    assert resp.status_code == 404
    assert resp.json()["error"]["code"] == "ORDER_NOT_FOUND"


def test_ac11_status_update_cannot_change_a_scheduled_order(client):
    order_id = client.post("/orders", json=SCHEDULED).json()["id"]
    for new_status in ["PLACED", "PREPARING", "CANCELLED"]:
        resp = client.patch(f"/orders/{order_id}/status", json={"status": new_status})
        assert resp.status_code == 409
        assert resp.json()["error"]["code"] == "STATUS_CHANGE_NOT_ALLOWED"
    assert status(client, order_id) == "SCHEDULED"


def test_ac11_status_update_cannot_set_scheduled(client):
    order_id = client.post("/orders", json=ORDER).json()["id"]
    resp = client.patch(f"/orders/{order_id}/status", json={"status": "SCHEDULED"})
    assert resp.status_code == 409
    assert status(client, order_id) == "PLACED"


def test_released_order_follows_normal_status_flow(client, db_path):
    order_id = client.post("/orders", json=SCHEDULED).json()["id"]
    release_at_due_time(db_path)
    resp = client.patch(f"/orders/{order_id}/status", json={"status": "PREPARING"})
    assert resp.status_code == 200
    assert resp.json()["status"] == "PREPARING"
