"""Schema for paginated responses."""

from dataclasses import dataclass
from typing import Generic, List, TypeVar

T = TypeVar("T")


@dataclass
class PaginatedResponse(Generic[T]):
    """Generic schema for paginated responses"""

    data: List[T]
    total: int
    page: int
    size: int
    total_pages: int
    has_next: bool
    has_prev: bool
