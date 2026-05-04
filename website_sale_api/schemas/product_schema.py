"""Schema definitions for Product model."""

# pylint:disable=too-few-public-methods
from typing import Optional

from pydantic import BaseModel

from .pagination import PaginatedResponse


class ProductData(BaseModel):
    """Schema for individual product data"""

    id: int
    name: str
    default_code: Optional[str] = None
    list_price: float = 0.0
    image_256: Optional[str] = None


class ProductResponse(PaginatedResponse[ProductData]):
    """Response schema for Product model"""
