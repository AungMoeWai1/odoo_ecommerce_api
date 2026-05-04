"""Service for handling product-related business logic."""

# pylint:disable=import-error
from odoo.http import request

from ..schemas.product_schema import ProductData, ProductResponse
from .base_service import BaseService
from .pagination_service import PaginationService


class ProductService(BaseService):
    """Service for product-related operations"""

    model_name = "product.template"
    fields = [
        "id",
        "name",
        "default_code",
        "list_price",
        "standard_price",
        "sale_ok",
        "website_published",
        "image_256",
    ]

    def get_products(self, kwargs):
        """Retrieve a list of products with pagination and sorting"""
        pager = PaginationService(kwargs)
        domain = self._get_product_domain()
        sort = kwargs.get("sort")
        # Default is sort with id
        if not sort:
            sort = "id"

        paginated_data = pager.get_paginated_records(
            model_name=self.model_name, domain=domain, fields=self.fields, sort=sort
        )

        base_url = self._get_base_url()
        products = []
        for product in paginated_data["data"]:
            products.append(
                ProductData(
                    id=product["id"],
                    name=product["name"],
                    default_code=product["default_code"] or "",
                    list_price=product["list_price"],
                    image_256=f"{base_url}/web/image/product.template/{product['id']}/image_256",
                )
            )

        return ProductResponse(
            data=products,
            total=paginated_data["total"],
            page=paginated_data["page"],
            size=paginated_data["size"],
            total_pages=paginated_data["total_pages"],
            has_next=paginated_data["has_next"],
            has_prev=paginated_data["has_prev"],
        )

    def get_product_by_id(self, product_id):
        """Retrieve product details by ID"""
        model = request.env[self.model_name].sudo()

        record = model.search_read(
            [("id", "=", product_id), ("website_published", "=", True)],
            self.fields,
            limit=1,
        )

        if not record:
            return {"data": None}

        product = record[0]

        base_url = self._get_base_url()

        if product.get("image_256"):
            product["image_256"] = (
                f"{base_url}/web/image/product.template/{product['id']}/image_256"
            )
            product.pop("image_256", None)

        return ProductData(**product)

    def _get_product_domain(self):
        """Get the domain for retrieving products.
        By default, it retrieves only published products."""
        domain = [("website_published", "=", True)]

        return domain


def get_product_service():
    """Factory function to get an instance of ProductService"""
    return ProductService()
