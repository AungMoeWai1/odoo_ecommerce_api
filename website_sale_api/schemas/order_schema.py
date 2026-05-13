"""Schema definitions for Sale Order models."""

# pylint: disable=too-few-public-methods
from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel
from .pagination import PaginatedResponse


class CurrencyData(BaseModel):
    """Schema for currency data."""

    id: int
    name: str
    symbol: Optional[str] = None


class OrderLineData(BaseModel):
    """Schema for individual order line data."""

    product_name: Optional[str | bool] = None
    variant: Optional[str | bool] = None
    quantity: int
    price: float


class OrderData(BaseModel):
    """Schema for individual sale order data."""

    id: int
    name: str
    date_order: Optional[datetime]
    order_status: str
    delivery_status: str
    amount_total: float
    item_count: int
    currency: CurrencyData
    items: List[OrderLineData]


class OrderDataResponse(PaginatedResponse[OrderData]):
    """Paginated response schema for sale orders."""
