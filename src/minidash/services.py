"""Ordering business logic. Routes call these; these call the repository."""

import sqlite3
from datetime import datetime

from minidash import repository
from minidash.errors import NotFoundError, ValidationFailedError
from minidash.scheduling import release_cutoff, to_db, validate_schedule
from minidash.schemas import OrderIn, OrderStatus


def list_menu(conn: sqlite3.Connection, restaurant_id: int) -> list[sqlite3.Row]:
    if repository.get_restaurant(conn, restaurant_id) is None:
        raise NotFoundError("RESTAURANT_NOT_FOUND", f"Restaurant {restaurant_id} does not exist.")
    return repository.list_menu(conn, restaurant_id)


def place_order(conn: sqlite3.Connection, order: OrderIn, now: datetime) -> dict:
    restaurant = repository.get_restaurant(conn, order.restaurant_id)
    if restaurant is None:
        raise NotFoundError(
            "RESTAURANT_NOT_FOUND", f"Restaurant {order.restaurant_id} does not exist."
        )
    menu = repository.list_menu(conn, order.restaurant_id)
    prices = {row["id"]: row["price_cents"] for row in menu}
    lines = []
    for item in order.items:
        if item.menu_item_id not in prices:
            raise ValidationFailedError(
                "ITEM_NOT_ON_MENU",
                f"Menu item {item.menu_item_id} is not on restaurant {order.restaurant_id}'s menu.",
            )
        lines.append((item.menu_item_id, item.quantity, prices[item.menu_item_id]))

    if order.scheduled_for is None:
        status, scheduled_for = OrderStatus.PLACED, None
    else:
        when = validate_schedule(
            order.scheduled_for, now, restaurant["opens_at"], restaurant["closes_at"]
        )
        status, scheduled_for = OrderStatus.SCHEDULED, to_db(when)

    with conn:
        order_id = repository.insert_order(
            conn,
            restaurant_id=order.restaurant_id,
            status=status,
            total_cents=sum(qty * price for _, qty, price in lines),
            address=order.address,
            created_at=to_db(now),
            scheduled_for=scheduled_for,
            items=lines,
        )
    return get_order(conn, order_id)


def get_order(conn: sqlite3.Connection, order_id: int) -> dict:
    row = repository.get_order(conn, order_id)
    if row is None:
        raise NotFoundError("ORDER_NOT_FOUND", f"Order {order_id} does not exist.")
    return {**dict(row), "items": [dict(r) for r in repository.get_order_items(conn, order_id)]}


def release_due_orders(conn: sqlite3.Connection, now: datetime) -> list[int]:
    """Send every SCHEDULED order due within 30 minutes to the kitchen (status PLACED)."""
    with conn:
        return repository.release_scheduled_orders(conn, to_db(release_cutoff(now)))


def update_status(conn: sqlite3.Connection, order_id: int, status: OrderStatus) -> dict:
    get_order(conn, order_id)  # raises if missing
    with conn:
        repository.set_status(conn, order_id, status)
    return get_order(conn, order_id)
