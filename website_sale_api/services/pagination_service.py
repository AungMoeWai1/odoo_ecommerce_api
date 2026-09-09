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

    def get_paginated_from_kwargs(self, kwargs: Dict[str, Any]) -> Dict[str, Any]:
        """Get paginated records with parameters from kwargs."""
        page = int(kwargs.pop("page", 1))
        size = int(kwargs.pop("size", 10))
        sort = str(kwargs.pop("sort", "id desc"))

        # Build domain from range filter and remaining kwargs
        filter_domain = self._range_filter(
            kwargs.pop("filter_field", "create_date"),
            kwargs.pop("filter_from", None),
            kwargs.pop("filter_to", None),
        )
        filter_domain += self._build_domain_from_kwargs(kwargs)

        self.default_domain += filter_domain
        return self.get_paginated_records(sort=sort, page=page, size=size)

    def _range_filter(self, field: str, from_val: Any, to_val: Any) -> list:
        """Build domain for range filtering."""
        range_domain = []
        if from_val:
            range_domain.append((field, ">=", from_val))
        if to_val:
            range_domain.append((field, "<=", to_val))
        return range_domain

    def _build_domain_from_kwargs(self, kwargs: Dict[str, Any]) -> list:
        """Build Odoo domain from remaining kwargs dynamically."""
        domain = []
        for key, value in kwargs.items():
            if value is None or value == "":
                continue
            domain.append((key, "ilike" if isinstance(value, str) else "=", value))
        return domain
