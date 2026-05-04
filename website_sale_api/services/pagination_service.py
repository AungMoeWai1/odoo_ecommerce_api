"""pagination"""

# pylint:disable=import-error,too-few-public-methods
from odoo.http import request


class PaginationService:
    """Service for handling pagination logic"""

    def __init__(self, params):
        self.page = int(params.get("page", 1))
        self.size = int(params.get("size", 10))
        self.offset = (self.page - 1) * self.size
        self.limit = self.size

    def get_paginated_records(
        self,
        model_name,
        domain=None,
        fields=None,
        sort=None,
    ):
        """Retrieve paginated records from the specified model
        based on the initialized pagination parameters."""
        domain = domain or []

        model = request.env[model_name].sudo()

        total = model.search_count(domain)

        records = model.search_read(
            domain, fields, limit=self.limit, offset=self.offset, order=sort
        )

        if records:
            return self._build_response(records, total)
        return self._build_response([], total)

    def _build_response(self, data, total):
        """Build the pagination response structure based on the retrieved data and total count."""
        total_pages = (total + self.size - 1) // self.size

        return {
            "data": data,
            "total": total,
            "page": self.page,
            "size": self.size,
            "total_pages": total_pages,
            "has_next": self.page < total_pages,
            "has_prev": self.page > 1,
        }
