"""HTTP routes. Thin: parse input, call a service, return the result."""

import sqlite3
from collections.abc import Iterator
from typing import Annotated

from fastapi import APIRouter, Depends, Request

from minidash import repository, services
from minidash.db import connect
from minidash.schemas import MenuItemOut, OrderIn, OrderOut, RestaurantOut, StatusUpdate

router = APIRouter()


def get_conn(request: Request) -> Iterator[sqlite3.Connection]:
    conn = connect(request.app.state.db_path)
    try:
        yield conn
    finally:
        conn.close()


Conn = Annotated[sqlite3.Connection, Depends(get_conn)]


@router.get("/restaurants", response_model=list[RestaurantOut])
def list_restaurants(conn: Conn):
    return [dict(row) for row in repository.list_restaurants(conn)]


@router.get("/restaurants/{restaurant_id}/menu", response_model=list[MenuItemOut])
def get_menu(restaurant_id: int, conn: Conn):
    return [dict(row) for row in services.list_menu(conn, restaurant_id)]


@router.post("/orders", status_code=201, response_model=OrderOut)
def place_order(order: OrderIn, conn: Conn):
    return services.place_order(conn, order)


@router.get("/orders/{order_id}", response_model=OrderOut)
def get_order(order_id: int, conn: Conn):
    return services.get_order(conn, order_id)


@router.patch("/orders/{order_id}/status", response_model=OrderOut)
def update_status(order_id: int, body: StatusUpdate, conn: Conn):
    return services.update_status(conn, order_id, body.status)
