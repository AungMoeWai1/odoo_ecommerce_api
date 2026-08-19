"""Controller for handling order-related API endpoints in the Odoo eCommerce module."""

# pylint: disable=too-few-public-methods,import-error

from odoo import http
from odoo.exceptions import ValidationError
from odoo.http import request

from ..services.order_service import OrderService
from ..services.token_service import JWTService
from .base import BaseAPI


class OrderController(BaseAPI):
    """API controller for handling order-related requests"""

    @http.route(
        "/api/orders",
        type="http",
        auth="public",
        methods=["GET"],
        csrf=False,
    )
    @JWTService.jwt_required()
    def get_orders(self, **kwargs):
        """Retrieve a list of orders with pagination and sorting"""
        try:
            user = request.authenticated_user
            result = OrderService().get_orders(user=user, kwargs=kwargs)
            return self._success(result)
        except ValidationError as e:
            return self._error(message=str(e), code=400)

    @http.route(
        "/api/orders/<int:order_id>",
        type="http",
        auth="public",
        methods=["GET"],
        csrf=False,
    )
    @JWTService.jwt_required()
    def get_order(self, order_id):
        """Retrieve an order with pagination and sorting"""
        try:
            user = request.authenticated_user
            result = OrderService().get_order_detail(user=user, order_id=order_id)
            return self._success(result, wrap_in_data=True)
        except ValidationError as e:
            return self._error(message=str(e), code=400)
