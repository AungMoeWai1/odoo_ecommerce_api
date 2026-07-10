"""Schema definitions for Product model."""

# pylint:disable=too-few-public-methods
from dataclasses import dataclass, field
from typing import Dict, List, Optional

from .pagination import PaginatedResponse


@dataclass
class ProductVariantData:
    """Schema for individual product variant data"""

    id: int
    name: str
    price: float
    attributes: Dict[str, str]
    stock_qty: Optional[int] = None


@dataclass
class ProductData:
    """Schema for individual product data"""

    id: int
    name: str
    description: Optional[str] = None

    price: float = 0.0
    sale_price: Optional[float] = None
    discounted_unit_price: Optional[float] = None
    discount_amount: Optional[float] = None

    currency: Optional[str] = None
    currency_id: Optional[int] = None

    category_id: Optional[int] = None
    category_name: Optional[str] = None

    stock_qty: Optional[int] = None
    is_in_stock: Optional[bool] = None

    rating: Optional[float] = 0.0
    review_count: Optional[int] = 0

    attributes: List[str] = field(default_factory=list)
    images: List[str] = field(default_factory=list)
    variants: List[ProductVariantData] = field(default_factory=list)


@dataclass
class ProductResponse(PaginatedResponse[ProductData]):
    """Response schema for Product model"""
