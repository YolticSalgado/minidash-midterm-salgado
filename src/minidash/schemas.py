"""Request and response models."""

from datetime import datetime
from enum import StrEnum

from pydantic import BaseModel, Field


class OrderStatus(StrEnum):
    SCHEDULED = "SCHEDULED"
    PLACED = "PLACED"
    PREPARING = "PREPARING"
    READY = "READY"
    PICKED_UP = "PICKED_UP"
    DELIVERED = "DELIVERED"
    CANCELLED = "CANCELLED"


class RestaurantOut(BaseModel):
    id: int
    name: str
    cuisine: str
    opens_at: str
    closes_at: str
    avg_prep_minutes: int


class MenuItemOut(BaseModel):
    id: int
    name: str
    price_cents: int


class OrderItemIn(BaseModel):
    menu_item_id: int
    quantity: int = Field(ge=1)


class OrderIn(BaseModel):
    restaurant_id: int
    items: list[OrderItemIn] = Field(min_length=1)
    address: str = Field(min_length=1)
    # Optional delivery time; omitted or null means "as soon as possible".
    scheduled_for: datetime | None = None


class OrderItemOut(BaseModel):
    menu_item_id: int
    name: str
    quantity: int
    price_cents: int


class OrderOut(BaseModel):
    id: int
    restaurant_id: int
    status: OrderStatus
    total_cents: int
    address: str
    created_at: str
    scheduled_for: str | None
    items: list[OrderItemOut]


class StatusUpdate(BaseModel):
    status: OrderStatus
