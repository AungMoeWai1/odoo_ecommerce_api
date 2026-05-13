"""Service class for handling wishlist-related operations in the Odoo e-commerce API."""

# pylint: disable=too-few-public-methods, import-error

from odoo.http import request
from odoo.exceptions import ValidationError
from ..schemas.wishlist_schema import WishlistData, WishlistResponse


class WishlistService:
    """Service class for handling wishlist-related operations"""

    def get_wishlists(self, user, website_id) -> WishlistResponse:
        """Fetches the wishlist items for the current user and specified website"""
        partner = self._get_partner(user)
        website = self._get_website(website_id)

        wishlists = self._wishlist_env().search(
            self._wishlist_domain(partner, website=website)
        )

        data = [WishlistData(product_id=w.product_id.id) for w in wishlists]

        return WishlistResponse(data=data)

    def add_to_wishlist(self, user, product_id, website_id) -> WishlistData:
        """Creates a wishlist item for the current user, specified product, and website"""

        partner = self._get_partner(user)
        product = self._get_product(product_id)
        website = self._get_website(website_id)
        existing = self._wishlist_env().search(
            self._wishlist_domain(partner, website=website, product=product)
        )

        if existing:
            return WishlistData(product_id=existing.product_id.id)

        w = self._wishlist_env().create(
            {
                "partner_id": partner.id,
                "product_id": product.id,
                "website_id": website.id,
            }
        )

        return WishlistData(product_id=w.product_id.id)

    def remove_from_wishlist(self, user, website_id, product_id) -> bool:
        """Deletes a wishlist item for the current user, specified product, and website"""

        partner = self._get_partner(user)
        website = self._get_website(website_id)
        product = self._get_product(product_id)
        wishlist = self._wishlist_env().search(
            self._wishlist_domain(partner, website=website, product=product)
        )
        if not wishlist:
            raise ValidationError("Wishlist not found")

        wishlist.unlink()
        return True

    def _wishlist_domain(self, partner, product=None, website=None):
        domain = [("partner_id", "=", partner.id), ("website_id", "=", website.id)]
        if product:
            domain.append(("product_id", "=", product.id))

        return domain

    def _wishlist_env(self):
        return request.env["product.wishlist"].sudo()

    def _get_partner(self, user):
        partner = user.partner_id
        if not partner:
            raise ValidationError("Partner not found")
        return partner

    def _get_website(self, website_id):
        if not website_id:
            raise ValidationError("Website ID not found")
        website = request.env["website"].sudo().browse(website_id)
        if not website.exists():
            raise ValidationError("Website not found")
        return website

    def _get_product(self, product_id):
        if not product_id:
            raise ValidationError("Product not found")
        product = request.env["product.product"].sudo().browse(product_id)
        if not product.exists():
            raise ValidationError("Product not found")
        return product


def get_wishlist_service():
    """Factory function to get an instance of WishlistService"""
    return WishlistService()
