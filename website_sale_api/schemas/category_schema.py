"""Schema definitions for Category model."""

# pylint:disable=too-few-public-methods
from typing import List, Optional

from pydantic import BaseModel

from .pagination import PaginatedResponse


class CategoryData(BaseModel):
    """Schema for individual category data"""

    id: int
    name: str
    parent_id: Optional[int] = None
    child_id: Optional[List[int]] = None
    image_256: Optional[str] = None


class CategoryResponse(PaginatedResponse[CategoryData]):
    """Response schema for Category model"""
