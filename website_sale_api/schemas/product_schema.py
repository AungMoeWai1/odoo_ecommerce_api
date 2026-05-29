"""Schema definitions for Product model."""

# pylint:disable=too-few-public-methods
from typing import Optional, List, Dict
from pydantic import BaseModel, field_validator

from .pagination import PaginatedResponse


class ProductVariantData(BaseModel):
    """Schema for individual product variant data"""
    id: int
    name: str
    price: float
    stock_qty: Optional[int] = None
    attributes: Dict[str, str]


class ProductData(BaseModel):
    """Schema for individual product data"""

    id: int
    name: str
    description: Optional[str] = None

    price: float = 0.0
    sale_price: Optional[float] = None
    discounted_unit_price: Optional[float] = None
    discount_amount: Optional[float] = None

    currency: Optional[str] = None

    category_id: Optional[int] = None
    category_name: Optional[str] = None

    stock_qty: Optional[int] = None
    is_in_stock: Optional[bool] = None

    rating: Optional[float] = 0.0
    review_count: Optional[int] = 0

    attributes: List[str] = []

    images: List[str] = []

    variants: List[ProductVariantData] = []

    @field_validator("*", mode="before")
    @classmethod
    def false_to_none(cls, v):
        """
        Converts a value of False to None, otherwise returns the original value."""

        return None if v is False else v


class ProductResponse(PaginatedResponse[ProductData]):
    """Response schema for Product model"""
