"""SQLite connection, schema, and seed data."""

import sqlite3
from contextlib import closing
from pathlib import Path

SCHEMA = """
CREATE TABLE IF NOT EXISTS restaurants (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    cuisine TEXT NOT NULL,
    opens_at TEXT NOT NULL,   -- "HH:MM"
    closes_at TEXT NOT NULL,  -- "HH:MM"
    avg_prep_minutes INTEGER NOT NULL
);
CREATE TABLE IF NOT EXISTS menu_items (
    id INTEGER PRIMARY KEY,
    restaurant_id INTEGER NOT NULL REFERENCES restaurants(id),
    name TEXT NOT NULL,
    price_cents INTEGER NOT NULL CHECK (price_cents >= 0)
);
CREATE TABLE IF NOT EXISTS orders (
    id INTEGER PRIMARY KEY,
    restaurant_id INTEGER NOT NULL REFERENCES restaurants(id),
    status TEXT NOT NULL,
    total_cents INTEGER NOT NULL,
    address TEXT NOT NULL,
    created_at TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS order_items (
    id INTEGER PRIMARY KEY,
    order_id INTEGER NOT NULL REFERENCES orders(id),
    menu_item_id INTEGER NOT NULL REFERENCES menu_items(id),
    quantity INTEGER NOT NULL CHECK (quantity > 0),
    price_cents INTEGER NOT NULL
);
"""

RESTAURANTS = [
    (1, "Bella Napoli", "Italian", "11:00", "22:00", 20),
    (2, "Tokyo Bento", "Japanese", "11:30", "21:30", 15),
    (3, "Taqueria Sol", "Mexican", "10:00", "23:00", 12),
    (4, "Night Owl Diner", "American", "18:00", "02:00", 18),
    (5, "Always Open Noodles", "Chinese", "00:00", "00:00", 10),
]

MENU_ITEMS = [
    (1, 1, "Margherita Pizza", 1299),
    (2, 1, "Lasagna", 1499),
    (3, 2, "Salmon Bento", 1399),
    (4, 2, "Miso Soup", 399),
    (5, 3, "Carnitas Tacos", 1099),
    (6, 3, "Chips & Guacamole", 599),
    (7, 4, "Cheeseburger", 1199),
    (8, 4, "Milkshake", 549),
    (9, 5, "Beef Noodle Soup", 1249),
    (10, 5, "Pork Dumplings", 799),
]


def connect(db_path: str | Path) -> sqlite3.Connection:
    conn = sqlite3.connect(db_path, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db(db_path: str | Path) -> None:
    """Create tables and seed restaurants/menus if the database is empty."""
    with closing(connect(db_path)) as conn, conn:
        conn.executescript(SCHEMA)
        if conn.execute("SELECT COUNT(*) FROM restaurants").fetchone()[0] == 0:
            conn.executemany("INSERT INTO restaurants VALUES (?, ?, ?, ?, ?, ?)", RESTAURANTS)
            conn.executemany("INSERT INTO menu_items VALUES (?, ?, ?, ?)", MENU_ITEMS)
