"""Schemas for product reviews in the e-commerce API."""

# pylint: disable=too-few-public-methods

from datetime import datetime
from dataclasses import dataclass
from typing import Optional
from .pagination import PaginatedResponse


@dataclass
class ReviewLineData:
    """Schema for individual review data"""

    id: int
    customer_name: str
    rating: float
    comment: Optional[str] = None
    date: Optional[datetime] = None
    is_verified_purchase: Optional[bool] = None


@dataclass
class ReviewDataResponse(PaginatedResponse[ReviewLineData]):
    """Schema for paginated review data response"""

    average_rating: float
