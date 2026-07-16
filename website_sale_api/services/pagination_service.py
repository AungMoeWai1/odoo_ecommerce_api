"""pagination"""

# pylint:disable=import-error
from typing import Any, Dict, Optional

from .base_service import BaseService


class PaginationService(BaseService):
    """Generic service for handling pagination logic."""

    def __init__(self, env=None):
        super().__init__(env)
        self.fields = []
        self.default_domain = []
        self.default_sort = "id"

    def get_paginated_records(
        self,
        sort: Optional[str] = None,
        page: int = 1,
        size: int = 10,
    ) -> Dict[str, Any]:
        """
        Retrieve paginated records.

        Args:
            domain: Domain filter (default: self.default_domain)
            fields: Fields to fetch (default: self.fields)
            sort: Sort order (default: self.default_sort)
            page: Page number (1-indexed)
            size: Items per page

        Returns:
            Dict with paginated data including metadata
        """
        sort = sort if sort else self.default_sort

        # Calculate pagination
        offset = (page - 1) * size

        # Get total and records
        total = self.search_count()
        records = self.search_read(limit=size, offset=offset, order=sort)

        # Build response
        total_pages = (total + size - 1) // size if size > 0 else 0

        return {
            "data": records,
            "total": total,
            "page": page,
            "size": size,
            "total_pages": total_pages,
            "has_next": page < total_pages,
            "has_prev": page > 1,
        }

    def get_paginated_from_kwargs(
        self,
        kwargs: Dict[str, Any],
        sort: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Get paginated records with parameters from kwargs."""
        page = int(kwargs.get("page", 1))
        size = int(kwargs.get("size", 10))

        return self.get_paginated_records(sort=sort, page=page, size=size)
