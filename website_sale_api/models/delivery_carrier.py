"""Add township for the delivery carrier model."""

# pylint:disable=import-error,too-few-public-methods, protected-access
from odoo import fields, models
from odoo.addons.website_sale.controllers.delivery import Delivery


class DeliveryCarrier(models.Model):
    """Add township for the delivery carrier model."""

    _inherit = "delivery.carrier"

    township_ids = fields.Many2many("res.township", string="Townships")

    def get_delivery_method(self, order_sudo):
        """Get wishlist for partner base on website"""

        result = []
        for dm in order_sudo._get_delivery_methods():
            rate = Delivery._get_rate(dm, order_sudo, is_express_checkout_flow=True)

            result.append(
                {
                    "id": dm.id,
                    "name": dm.name,
                    "price": rate.get("price", 0.0) if rate.get("success") else 0.0,
                    "website_description": dm.website_description,
                    "carrier_description": dm.carrier_description,
                    "currency_id": dm.currency_id.id,
                }
            )

        return result
