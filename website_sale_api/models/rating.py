"""Models for rating"""

# pylint: disable=too-few-public-methods,protected-access,import-error

from odoo import models


class Rating(models.Model):
    """Model for rating"""

    _inherit = "rating.rating"

    def create_product_rating(self, user, product, rating_value):
        """Create product rating"""
        return self.sudo().create(
            {
                "partner_id": user.partner_id.id,
                "rated_partner_id": user.partner_id.id,
                "res_model_id": self.env["ir.model"]._get_id("product.template"),
                "res_id": product.id,
                "rating": rating_value,
            }
        )
