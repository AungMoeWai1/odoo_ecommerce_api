"""Service for handling category-related business logic."""

# pylint:disable=too-few-public-methods,import-error
from ..schemas.category_schema import CategoryData, CategoryResponse
from .base_service import BaseService
from .pagination_service import PaginationService


class CategoryService(BaseService):
    """Service for category-related operations"""

    model_name = "product.public.category"
    fields = ["id", "name", "parent_id", "image_256", "child_id"]

    def get_categories(self, kwargs):
        """Retrieve a list of product categories with pagination and sorting"""
        pager = PaginationService(kwargs)

        domain = self._get_category_domain()

        sort = kwargs.get("sort")
        if not sort:
            sort = "id"

        paginated_data = pager.get_paginated_records(
            model_name=self.model_name, fields=self.fields, domain=domain, sort=sort
        )

        categories = []
        categ_url = f"{self._get_base_url()}/web/image/product.public.category"
        for category in paginated_data["data"]:
            categories.append(
                CategoryData(
                    id=category["id"],
                    name=category["name"],
                    parent_id=category["parent_id"],
                    image_256=f"{categ_url}/{category['id']}/image_256",
                    child_id=category["child_id"],
                    # parent_name=category["parent_id"].
                )
            )

        return CategoryResponse(
            data=categories,
            size=paginated_data["size"],
            total=paginated_data["total"],
            page=paginated_data["page"],
            has_prev=paginated_data["has_prev"],
            total_pages=paginated_data["total_pages"],
            has_next=paginated_data["has_next"],
        )

    def _get_category_domain(self):
        """Get the domain for retrieving categories.
        By default, it retrieves top-level categories."""
        domain = [("parent_id", "=", False)]

        return domain


def get_category_service():
    """Factory function to get an instance of CategoryService"""
    return CategoryService()
