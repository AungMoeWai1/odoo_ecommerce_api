"""Schema definitions for Category model."""

# pylint:disable=too-few-public-methods
from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class CategoryData:
    """Schema for individual category data"""

    id: int
    name: str
    parent_id: Optional[int] = None
    image_256: Optional[str] = None
    child_ids: List[int] = field(default_factory=list)


@dataclass
class CategoryResponse:
    """Response schema for Category model"""

    data: List[CategoryData]
