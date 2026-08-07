"""Controller for cart-related API endpoints"""

# pylint:disable=import-error,broad-exception-caught
from odoo import http
from odoo.http import request

from ..services.cart_service import CartService
from ..services.token_service import JWTService
from .base import BaseAPI


class CartController(BaseAPI):
    """Cart API Controller"""

    @http.route("/api/cart", methods=["GET"], type="http", auth="public", csrf=False)
    @JWTService.jwt_required()
    def get_cart(self):
        """Get current cart details"""
        try:
            user = request.authenticated_user
            result = CartService().get_current_cart(user)

            return self._success(data=result)
        except Exception as e:
            return {"error": str(e)}

    @http.route("/api/cart", methods=["POST"], type="http", auth="public", csrf=False)
    @JWTService.jwt_required()
    def add_to_cart(self):
        """Add item to cart"""
        try:
            user = request.authenticated_user
            result = CartService().add_to_cart(user)

            return self._success(result)
        except Exception as e:
            return self._error(str(e))

    @http.route(
        "/api/cart/line/<int:line_id>",
        methods=["DELETE"],
        type="http",
        auth="public",
        csrf=False,
    )
    @JWTService.jwt_required()
    def delete_cart_item(self, line_id):
        """Delete item from cart"""
        try:
            user = request.authenticated_user

            result = CartService().delete_cart_item(line_id=line_id, user=user)

            return self._success(result)

        except Exception as e:
            return self._error(message=str(e))
