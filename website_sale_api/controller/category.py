"""Category controller for handling category-related API endpoints."""

# pylint:disable=too-few-public-methods,import-error
from odoo import http

from ..services.categroy_service import CategoryService
from .base import BaseAPI


class CategoryAPI(BaseAPI):
    """Controller for category-related endpoints"""

    @http.route(
        "/api/categories", type="http", auth="public", methods=["GET"], csrf=False
    )
    def get_categories(self, **kwargs):
        """Retrieve a list of product categories with pagination and sorting"""
        result = CategoryService().get_categories(kwargs)

        return self._success(result)
