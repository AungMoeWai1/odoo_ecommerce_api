"""Schema definitions for Product model."""

from dataclasses import dataclass, field
from typing import Dict, List, Optional

from .pagination import PaginatedResponse


@dataclass
class BaseProductData:
    """Base schema with common fields for both product and variant"""

    id: int
    name: str
    description: Optional[str] = None
    price: Optional[float] = None
    sale_price: Optional[float] = None
    discount_amount: Optional[float] = None
    discount_type: Optional[str] = None
    currency: Optional[str] = None
    currency_id: Optional[int] = None
    category_id: Optional[int] = None
    rating: Optional[float] = 0.0
    review_count: Optional[int] = 0


@dataclass
class ProductVariantData(BaseProductData):
    """Schema for individual product variant data"""

    attributes: Dict[str, str] = None
    stock_qty: Optional[float] = None
    images: Optional[List[str]] = field(default_factory=list)


@dataclass
class ProductData(BaseProductData):
    """Schema for individual product data"""

    images: Optional[str] = None


@dataclass
class DetailProductData:
    """Schema for individual product data"""

    id: int
    variants: List[ProductVariantData] = field(default_factory=list)


@dataclass
class ProductResponse(PaginatedResponse[ProductData]):
    """Response schema for Product model"""
