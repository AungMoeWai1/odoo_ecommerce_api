"""Schema definitions for Product model."""

# pylint:disable=too-many-instance-attributes
from dataclasses import dataclass, field
from typing import Dict, Generic, List, Optional, TypeVar

from .pagination import PaginatedResponse

ProductItem = TypeVar("ProductItem")


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
    allow_out_of_stock_order: Optional[bool] = False
    stock_qty: Optional[float] = None


@dataclass
class ProductVariantData(BaseProductData):
    """Schema for individual product variant data"""

    attributes: Dict[str, str] = None
    images: Optional[List[str]] = field(default_factory=list)


@dataclass
class ProductData(BaseProductData):
    """Schema for individual product data"""

    website_ribbon_id: Optional[int] = None
    images: Optional[str] = None


@dataclass
class DetailProductData:
    """Schema for individual product data"""

    id: int
    alternative_products: List[int]
    variants: List[ProductVariantData] = field(default_factory=list)


@dataclass
class ProductResponse(PaginatedResponse[ProductItem], Generic[ProductItem]):
    """Paginated response schema for product and variant data."""
