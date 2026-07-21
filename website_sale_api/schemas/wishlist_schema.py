"""Data schemas for wishlist-related responses in the Odoo e-commerce API."""

from dataclasses import dataclass
from typing import List


@dataclass
class WishlistData:
    """Pydantic schema for representing a wishlist item"""

    id: int
    product_id: int
    product_variant_id: int


@dataclass
class WishlistResponse:
    """Pydantic schema for representing a wishlist response"""

    data: List[WishlistData]
