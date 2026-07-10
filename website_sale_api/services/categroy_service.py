"""Service for handling category-related business logic."""

# pylint:disable=too-few-public-methods,import-error, too-many-locals

from ..schemas.category_schema import (
    CategoryData,
    CategoryResponse,
    ChildCategoryData,
    ProductData,
)
from .base_service import BaseService
from .pagination_service import PaginationService


class CategoryService(BaseService):
    """Service for category-related operations"""

    model_name = "product.public.category"

    fields = [
        "id",
        "name",
        "parent_id",
        "image_256",
        "child_id",
    ]

    def get_categories(self, kwargs):
        """Retrieve paginated product categories"""

        pager = PaginationService(kwargs)

        domain = self._get_category_domain()

        sort_order = kwargs.get("sort", "id")

        paginated_result = pager.get_paginated_records(
            model_name=self.model_name,
            fields=self.fields,
            domain=domain,
            sort=sort_order,
        )

        category_list = []

        image_base_url = f"{self._get_base_url()}/web/image/product.public.category"

        for category in paginated_result["data"]:

            current_category_id = category["id"]

            all_category_ids = self._get_all_child_category_ids(current_category_id)

            all_category_ids.append(current_category_id)

            total_product_count = (
                self.env["product.template"]
                .sudo()
                .search_count([("public_categ_ids", "in", all_category_ids)])
            )

            child_categories = []

            for child_id in category["child_id"]:

                child_all_ids = self._get_all_child_category_ids(child_id)
                child_all_ids.append(child_id)

                products = (
                    self.env["product.template"]
                    .sudo()
                    .search([("public_categ_ids", "in", child_all_ids)])
                )

                child_product_count = len(products)

                product_list = []

                for product in products:
                    product_list.append(
                        ProductData(
                            id=product.id,
                            name=product.name,
                        )
                    )

                child_categories.append(
                    ChildCategoryData(
                        id=child_id,
                        parent_id=current_category_id,
                        product_count=child_product_count,
                        products=product_list,
                    )
                )

            category_list.append(
                CategoryData(
                    id=current_category_id,
                    name=category["name"],
                    parent_id=category["parent_id"],
                    image_256=(f"{image_base_url}/" f"{current_category_id}/image_256"),
                    child_ids=child_categories,
                    product_count=total_product_count,
                )
            )

        return CategoryResponse(
            data=category_list,
            size=paginated_result["size"],
            total=paginated_result["total"],
            page=paginated_result["page"],
            has_prev=paginated_result["has_prev"],
            total_pages=paginated_result["total_pages"],
            has_next=paginated_result["has_next"],
        )

    def _get_category_domain(self):
        """Return domain for top-level categories"""

        return [("parent_id", "=", False)]

    def _get_all_child_category_ids(self, category_id):
        """Recursively get all descendant category IDs"""

        category = self.env["product.public.category"].sudo().browse(category_id)

        all_child_ids = []

        for child in category.child_id:

            all_child_ids.append(child.id)

            all_child_ids.extend(self._get_all_child_category_ids(child.id))

        return all_child_ids


def get_category_service():
    """Factory function to get an instance of CategoryService"""

    return CategoryService()
