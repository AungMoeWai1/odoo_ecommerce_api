"""API controller for handling wishlist-related requests."""

# pylint: disable=import-error

import json

from odoo import http
from odoo.http import request
from .base import BaseAPI
from ..services.token_service import jwt_required, get_current_user
from ..services.wishlist_service import get_wishlist_service


class WishlistAPI(BaseAPI):
    """API controller for wishlist-related operations"""

    @http.route(
        "/api/<int:website_id>/wihslists",
        type="http",
        auth="none",
        methods=["GET"],
        csrf=False,
    )
    @jwt_required
    def get_wishlist(self, website_id):
        """Fetch wishlist items for the current user"""
        user = get_current_user()

        return self.handle(
            lambda: get_wishlist_service().get_wishlist(
                user=user, website_id=website_id
            )
        )

    @http.route("/api/wihslist", type="http", auth="none", methods=["POST"], csrf=False)
    @jwt_required
    def create_wishlist(self):
        """Create a wishlist item for the current user"""
        user = get_current_user()
        params = json.loads(request.httprequest.data or "{}")
        product_id = params.get("product_id")
        website_id = params.get("website_id")

        return self.handle(
            lambda: get_wishlist_service().create_wishlist(
                user=user, product_id=product_id, website_id=website_id
            )
        )

    @http.route(
        "/api/<int:website_id>/wihslists/<int:product_id>/",
        type="http",
        auth="none",
        methods=["DELETE"],
        csrf=False,
    )
    @jwt_required
    def delete_wishlist(self, website_id, product_id):
        """Delete a wishlist item for the current user"""
        user = get_current_user()

        return self.handle(
            lambda: get_wishlist_service().delete_wishlist(
                user=user, website_id=website_id, product_id=product_id
            )
        )
