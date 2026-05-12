"""Service class for handling wishlist-related operations in the Odoo e-commerce API."""

# pylint: disable=too-few-public-methods, import-error

from odoo.http import request
from odoo.exceptions import ValidationError
from ..schemas.wishlist_schema import WishlistData, WishlistResponse


class WishlistService:
    """Service class for handling wishlist-related operations"""

    def get_wishlist(self, user, website_id):
        """Fetches the wishlist items for the current user and specified website"""
        partner = user.partner_id
        if not partner:
            raise ValidationError("Partner not found")

        website = request.env["website"].sudo().browse(website_id)
        if not website.exists():
            raise ValidationError("Website not found")

        wishlists = (
            request.env["product.wishlist"]
            .sudo()
            .search(
                [
                    ("partner_id", "=", partner.id),
                ]
            )
        )

        data = []

        for wishlist in wishlists:
            data.append(WishlistData(product_id=wishlist.product_id.id))

        return WishlistResponse(data=data)

    def create_wishlist(self, user, product_id, website_id):
        """Creates a wishlist item for the current user, specified product, and website"""

        partner = user.partner_id
        if not partner:
            raise ValidationError("Partner not found")

        if not product_id:
            raise ValidationError("Product not found")

        website = request.env["website"].sudo().browse(website_id)

        if not website:
            raise ValidationError("Website not found")

        product = request.env["product.product"].sudo().browse(product_id)

        if not product.exists():
            raise ValidationError("Product does not exist")

        existing = (
            request.env["product.wishlist"]
            .sudo()
            .search(
                [
                    ("partner_id", "=", partner.id),
                    ("product_id", "=", product.id),
                    ("website_id", "=", website.id),
                ],
                limit=1,
            )
        )

        if existing:
            return WishlistData(
                product_id=existing.product_id.id,
            )

        wishlist = (
            request.env["product.wishlist"]
            .sudo()
            .create(
                {
                    "partner_id": partner.id,
                    "product_id": product.id,
                    "website_id": website.id,
                }
            )
        )

        return WishlistData(product_id=wishlist.product_id.id)

    def delete_wishlist(self, user, website_id, product_id):
        """Deletes a wishlist item for the current user, specified product, and website"""

        partner = user.partner_id

        if not partner:
            raise ValidationError("Partner not found")

        website = request.env["website"].sudo().browse(website_id)

        if not website.exists():
            raise ValidationError("Website not found")

        wishlist = (
            request.env["product.wishlist"]
            .sudo()
            .search(
                [
                    ("partner_id", "=", partner.id),
                    ("website_id", "=", website.id),
                    ("product_id", "=", product_id),
                ],
                limit=1,
            )
        )

        if not wishlist:
            raise ValidationError("Wishlist item not found")

        wishlist.unlink()

        return self.get_wishlist(user, website_id)


def get_wishlist_service():
    """Factory function to get an instance of WishlistService"""
    return WishlistService()
