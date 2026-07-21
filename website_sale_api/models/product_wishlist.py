"""product wishlist"""

# pylint:disable=import-error,too-few-public-methods
from odoo import models


class ProductWishlist(models.Model):
    """Product wishlist"""

    _inherit = "product.wishlist"

    def get_partner_wishlist(self, user, website_id, wishlist_id=None):
        """Get wishlist for partner base on website"""
        domain = [
            ("partner_id", "=", user.partner_id.id),
            ("website_id", "=", website_id),
        ]

        if wishlist_id:
            domain.append(("id", "=", wishlist_id))

        return self.search(domain)
