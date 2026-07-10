"""Schemas for product reviews in the e-commerce API."""

# pylint: disable=too-few-public-methods

from datetime import datetime
from typing import Optional
from .pagination import PaginatedResponse

class ReviewLineData(BaseModel):
    """Schema for individual review data"""

    id: int
    customer_name: str
    rating: float
    comment: Optional[str] = None
    date: Optional[datetime] = None
    is_verified_purchase: Optional[bool] = None


class ReviewDataResponse(PaginatedResponse[ReviewLineData]):
    """Schema for paginated review data response"""

    average_rating: float
