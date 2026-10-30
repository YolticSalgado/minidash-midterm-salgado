"""Data access: every SQL statement in the app lives here."""

import sqlite3


def list_restaurants(conn: sqlite3.Connection) -> list[sqlite3.Row]:
    return conn.execute("SELECT * FROM restaurants ORDER BY id").fetchall()


def get_restaurant(conn: sqlite3.Connection, restaurant_id: int) -> sqlite3.Row | None:
    return conn.execute("SELECT * FROM restaurants WHERE id = ?", (restaurant_id,)).fetchone()


def list_menu(conn: sqlite3.Connection, restaurant_id: int) -> list[sqlite3.Row]:
    return conn.execute(
        "SELECT id, name, price_cents FROM menu_items WHERE restaurant_id = ? ORDER BY id",
        (restaurant_id,),
    ).fetchall()


def insert_order(
    conn: sqlite3.Connection,
    *,
    restaurant_id: int,
    status: str,
    total_cents: int,
    address: str,
    created_at: str,
    items: list[tuple[int, int, int]],
) -> int:
    """Insert an order and its items. `items` holds (menu_item_id, quantity, price_cents)."""
    cur = conn.execute(
        "INSERT INTO orders (restaurant_id, status, total_cents, address, created_at)"
        " VALUES (?, ?, ?, ?, ?)",
        (restaurant_id, status, total_cents, address, created_at),
    )
    order_id = cur.lastrowid
    conn.executemany(
        "INSERT INTO order_items (order_id, menu_item_id, quantity, price_cents)"
        " VALUES (?, ?, ?, ?)",
        [(order_id, item_id, qty, price) for item_id, qty, price in items],
    )
    return order_id


def get_order(conn: sqlite3.Connection, order_id: int) -> sqlite3.Row | None:
    return conn.execute("SELECT * FROM orders WHERE id = ?", (order_id,)).fetchone()


def get_order_items(conn: sqlite3.Connection, order_id: int) -> list[sqlite3.Row]:
    return conn.execute(
        "SELECT oi.menu_item_id, m.name, oi.quantity, oi.price_cents"
        " FROM order_items oi JOIN menu_items m ON m.id = oi.menu_item_id"
        " WHERE oi.order_id = ? ORDER BY oi.id",
        (order_id,),
    ).fetchall()


def set_status(conn: sqlite3.Connection, order_id: int, status: str) -> None:
    conn.execute("UPDATE orders SET status = ? WHERE id = ?", (status, order_id))
