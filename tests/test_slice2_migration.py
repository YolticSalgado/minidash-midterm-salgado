import sqlite3
from contextlib import closing

from fastapi.testclient import TestClient

from minidash.app import create_app
from minidash.db import SCHEMA, init_db

ORDER = {"restaurant_id": 1, "items": [{"menu_item_id": 1, "quantity": 1}], "address": "1 Main St"}


def make_baseline_db(path):
    """A database as the baseline app left it: no scheduled_for column, one existing order."""
    with closing(sqlite3.connect(path)) as conn, conn:
        conn.executescript(SCHEMA)
        conn.execute("INSERT INTO restaurants VALUES (1, 'Old', 'Thai', '10:00', '20:00', 15)")
        conn.execute("INSERT INTO menu_items VALUES (1, 1, 'Pad Thai', 1100)")
        conn.execute(
            "INSERT INTO orders (id, restaurant_id, status, total_cents, address, created_at)"
            " VALUES (7, 1, 'DELIVERED', 1100, '9 Elm St', '2026-10-01T18:00:00+00:00')"
        )
        conn.execute("INSERT INTO order_items VALUES (1, 7, 1, 1, 1100)")


def order_columns(path):
    with closing(sqlite3.connect(path)) as conn:
        return [row[1] for row in conn.execute("PRAGMA table_info(orders)")]


def test_migration_adds_column_and_keeps_existing_orders(db_path, clock):
    make_baseline_db(db_path)
    assert "scheduled_for" not in order_columns(db_path)

    with TestClient(create_app(db_path, clock=clock)) as client:
        old = client.get("/orders/7").json()

    assert "scheduled_for" in order_columns(db_path)
    assert old["status"] == "DELIVERED"
    assert old["total_cents"] == 1100
    assert old["scheduled_for"] is None


def test_migration_is_safe_to_run_twice(db_path):
    make_baseline_db(db_path)
    init_db(db_path)
    init_db(db_path)
    assert order_columns(db_path).count("scheduled_for") == 1


def test_ac1_order_without_schedule_has_null_scheduled_for(client):
    body = client.post("/orders", json=ORDER).json()
    assert body["status"] == "PLACED"
    assert body["scheduled_for"] is None
