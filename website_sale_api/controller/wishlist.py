"""API controller for handling wishlist-related requests."""

# pylint: disable=import-error

import json

from odoo import http
from odoo.http import request
from odoo.exceptions import ValidationError
from .base import BaseAPI
from ..services.token_service import jwt_required, get_current_user
from ..services.wishlist_service import get_wishlist_service


class WishlistAPI(BaseAPI):
    """API controller for wishlist-related operations"""

    @http.route(
        "/api/websites/<int:website_id>/wishlists",
        type="http",
        auth="none",
        methods=["GET"],
        csrf=False,
    )
    @jwt_required
    def get_wishlists(self, website_id):
        """Fetch wishlist items for the current user"""
        user = get_current_user()

        return self.handle(
            lambda: get_wishlist_service().get_wishlists(
                user=user, website_id=website_id
            )
        )

    @http.route(
        "/api/websites/<int:website_id>/wishlists",
        type="http",
        auth="none",
        methods=["POST"],
        csrf=False,
    )
    @jwt_required
    def add_to_wishlist(self, website_id):
        """Create a wishlist item for the current user"""
        try:
            user = get_current_user()
            params = json.loads(request.httprequest.data or "{}")
            product_id = params.get("product_id")

            wishlist_item = get_wishlist_service().add_to_wishlist(
                user=user, product_id=product_id, website_id=website_id
            )

            if wishlist_item:
                return self._success(message="Wishlist created successfully")

            return self._error(message="Wishlist not found", code=400)

        except ValidationError as e:
            return self._error(message=str(e), code=400)

    @http.route(
        "/api/websites/<int:website_id>/wishlists/<int:product_id>/",
        type="http",
        auth="none",
        methods=["DELETE"],
        csrf=False,
    )
    @jwt_required
    def remove_from_wishlist(self, website_id, product_id):
        """Delete a wishlist item for the current user"""
        try:
            user = get_current_user()
            success = get_wishlist_service().remove_from_wishlist(
                user=user, website_id=website_id, product_id=product_id
            )

            if success:
                return self._success(message="WishList deleted successfully")

            return self._error(message="Wishlist not found", code=400)

        except ValidationError as e:
            return self._error(message=str(e), code=400)
