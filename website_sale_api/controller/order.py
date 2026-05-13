"""Controller for handling order-related API endpoints in the Odoo eCommerce module."""

# pylint: disable=too-few-public-methods,import-error

from odoo import http
from odoo.exceptions import ValidationError
from ..services.order_service import get_order_service
from .base import BaseAPI
from ..services.token_service import jwt_required, get_current_user


class OrderController(BaseAPI):
    """API controller for handling order-related requests"""

    @http.route(
        "/api/<int:website_id>/orders",
        type="http",
        auth="none",
        methods=["GET"],
        csrf=False,
    )
    @jwt_required
    def get_orders(self, website_id, **kwargs):
        """Retrieve a list of orders with pagination and sorting"""
        try:
            user = get_current_user()
            result = get_order_service().get_orders(
                user=user, params=kwargs, website_id=website_id
            )
            return self._success(**result.model_dump())
        except ValidationError as e:
            return self._error(message=str(e), code=400)

    @http.route(
        "/api/<int:website_id>/orders/<int:order_id>",
        type="http",
        auth="none",
        methods=["GET"],
        csrf=False,
    )
    @jwt_required
    def get_order(self, website_id, order_id):
        """Retrieve an order with pagination and sorting"""
        try:
            user = get_current_user()
            result = get_order_service().get_order(
                user=user, website_id=website_id, order_id=order_id
            )
            return self._success(**result.model_dump())
        except ValidationError as e:
            return self._error(message=str(e), code=400)
