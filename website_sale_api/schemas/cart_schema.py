"""Schema for cart-related operations"""

# pylint:disable=too-many-instance-attributes
from dataclasses import dataclass
from typing import List


@dataclass
class CartItemResponse:
    """Response schema for cart item"""

    line_id: int
    product_id: int
    product_variant_id: int
    variant_name: str
    product_name: str
    image_url: str
    quantity: int
    unit_price: float
    subtotal: float


@dataclass
class CartResponse:
    """Response schema for cart details"""

    order_id: int
    items: List[CartItemResponse]
    total: float
    untax_total: float
    currency: str
    items_count: int
    discount: float
    shipping_fee: float
