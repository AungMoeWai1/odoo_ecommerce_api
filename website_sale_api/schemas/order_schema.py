"""Schema definitions for Sale Order models."""

# pylint: disable=too-few-public-methods,too-many-instance-attributes
from dataclasses import dataclass
from datetime import datetime
from typing import List

from .pagination import PaginatedResponse


@dataclass
class OrderLineData:
    """Schema for individual order line data."""

    product_name: str
    # variant: str
    quantity: int
    price: float
    # image_url: str
    subtotal: float


@dataclass
class OrderData:
    """Schema for individual sale order data."""

    id: int
    reference: str
    date_order: datetime
    name: str
    status: str
    currency: str
    delivery_status: str
    total: float
    item_count: int


@dataclass
class OrderDetailData(OrderData):
    """Schema for individual sale order data."""

    customer_id: int
    billing_address_id: int
    shipping_address_id: int
    line: List[OrderLineData]


@dataclass
class OrderDataResponse(PaginatedResponse[OrderData]):
    """Paginated response schema for sale orders."""
