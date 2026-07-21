"""Service class for handling wishlist-related operations in the Odoo e-commerce API."""

# pylint: disable=too-few-public-methods, import-error,protected-access

from odoo.exceptions import ValidationError
from odoo.http import request

from ..schemas.wishlist_schema import WishlistData, WishlistResponse
from .base_service import BaseService


class WishlistService(BaseService):
    """Service class for handling wishlist-related operations"""

    def __init__(self, env=None):
        super().__init__(env)
        self.model_name = "product.wishlist"
        self.website = self._get_current_website()

    def get_wishlists(self, user) -> WishlistResponse:
        """Fetches the wishlist items for the current user and specified website"""

        wishlists = self._wishlist_env().get_partner_wishlist(user, self.website.id)

        wishlist_data = []
        for wish in wishlists:
            wishlist_data.append(
                WishlistData(
                    id=wish.id,
                    product_id=wish.product_id.product_tmpl_id.id,
                    product_variant_id=wish.product_id.id,
                )
            )

        return WishlistResponse(data=wishlist_data)

    def add_to_wishlist(self, user, product_id):
        """Creates a wishlist item for the current user, specified product, and website"""

        product = request.env["product.product"].browse(product_id)
        price = product.with_context(
            website=self.website
        )._get_combination_info_variant()["price"]

        wishlist = request.env["product.wishlist"]

        wish = wishlist._add_to_wishlist(
            self.website.pricelist_ids[0].id,
            self.website.currency_id.id,
            self.website.id,
            price,
            product_id,
            user.partner_id.id,
        )
        return {
            "id": wish.id,
            "message": "Wishlist added",
        }

    def delete_wishlist(self, user, wishlist_id):
        """Deletes a wishlist item for the current user"""
        wishlist = self._wishlist_env().get_partner_wishlist(
            user, self.website.id, wishlist_id
        )

        if not wishlist:
            raise ValidationError("Wishlist not found")

        # Store id before deletion for response
        wishlist_id = wishlist.id

        # Delete the wishlist
        wishlist.unlink()

        return {
            "id": wishlist_id,
            "message": "Wishlist deleted successfully",
        }

    def _wishlist_env(self):
        return request.env[self.model_name].sudo()
