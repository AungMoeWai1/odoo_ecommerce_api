"""Data schemas for wishlist-related responses in the Odoo e-commerce API."""

from typing import List
from pydantic import BaseModel


class WishlistData(BaseModel):
    """Pydantic schema for representing a wishlist item"""

    product_id: int


class WishlistResponse(BaseModel):
    """Pydantic schema for representing a wishlist response"""

    data: List[WishlistData]
