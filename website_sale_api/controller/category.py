"""Category controller for handling category-related API endpoints."""

# pylint:disable=too-few-public-methods,import-error
from odoo import http

from ..services.categroy_service import get_category_service
from .base import BaseAPI


class CategoryAPI(BaseAPI):
    """Controller for category-related endpoints"""

    @http.route(
        "/api/v1/categories", type="http", auth="public", methods=["GET"], csrf=False
    )
    def get_categories(self, **kwargs):
        """Retrieve a list of product categories with pagination and sorting"""
        result = get_category_service().get_categories(kwargs)

        return self._success(data=result.model_dump())
