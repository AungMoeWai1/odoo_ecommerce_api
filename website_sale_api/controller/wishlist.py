"""API controller for handling wishlist-related requests."""

# pylint: disable=import-error,broad-exception-caught

import json

from odoo import http
from odoo.exceptions import ValidationError
from odoo.http import request

from ..services.token_service import JWTService
from ..services.wishlist_service import WishlistService
from .base import BaseAPI


class WishlistAPI(BaseAPI):
    """API controller for wishlist-related operations"""

    @http.route(
        "/api/wishlists",
        type="http",
        auth="public",
        methods=["GET"],
        csrf=False,
    )
    @JWTService.jwt_required
    def get_wishlists(self):
        """Fetch wishlist items for the current user"""
        user = request.authenticated_user
        return self._success(WishlistService().get_wishlists(user=user))

    @http.route(
        "/api/wishlists",
        type="http",
        auth="public",
        methods=["POST"],
        csrf=False,
    )
    @JWTService.jwt_required
    def add_to_wishlist(self):
        """Create a wishlist item for the current user"""
        try:
            user = request.authenticated_user
            params = json.loads(request.httprequest.data or "{}")
            product_id = params.get("product_id")

            wishlist_item = WishlistService().add_to_wishlist(
                user=user, product_id=product_id
            )
            return self._success(data=wishlist_item)

        except ValidationError as e:
            return self._error(message=str(e), code=400)

    @http.route(
        "/api/wishlists/<int:wishlist_id>",
        type="http",
        auth="public",
        methods=["DELETE"],
        csrf=False,
    )
    @JWTService.jwt_required
    def remove_from_wishlist(self, wishlist_id: int):
        """Delete a wishlist item for the current user"""
        try:
            user = request.authenticated_user
            result = WishlistService().delete_wishlist(
                user=user, wishlist_id=wishlist_id
            )
            return self._success(data=result)

        except ValidationError as e:
            return self._error(message=str(e), code=400)
        except Exception as e:
            return self._error(message=str(e), code=500)
