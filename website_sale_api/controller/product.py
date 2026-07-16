"""Controller for handling product-related API endpoints."""

# pylint: disable=too-few-public-methods,import-error

from odoo import http

from ..services.product_service import ProductService
from ..services.product_variant_service import ProductVariantService
from .base import BaseAPI


class ProductAPI(BaseAPI):
    """Controller for product-related endpoints"""

    @http.route(
        "/api/products", type="http", auth="public", methods=["GET"], csrf=False
    )
    def get_products(self, **kwargs):
        """Retrieve a list of products with pagination and sorting"""
        result = ProductService().get_products(kwargs)

        return self._success(result, wrap_in_data=True)

    @http.route(
        "/api/products/<int:product_id>",
        type="http",
        auth="public",
        methods=["GET"],
        csrf=False,
    )
    def get_product(self, product_id):
        """Retrieve product details by ID"""
        result = ProductVariantService().get_product_by_id(product_id)
        return self._success(data=result, wrap_in_data=True)
