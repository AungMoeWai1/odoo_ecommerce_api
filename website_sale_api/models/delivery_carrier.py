"""Add township for the delivery carrier model."""

# pylint:disable=import-error,too-few-public-methods, protected-access
from odoo import Command, api, fields, models
from odoo.addons.website_sale.controllers.delivery import Delivery


class DeliveryCarrier(models.Model):
    """Add township for the delivery carrier model."""

    _inherit = "delivery.carrier"

    township_ids = fields.Many2many("res.township", string="Townships")
    free_township_amount = fields.Boolean(string="Free Township Amount")

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

    def rate_shipment(self, order):
        """Modify shipment rate to add amount of township for delivery carrier"""
        result = super().rate_shipment(order)

        if result.get("success", False) and order.partner_shipping_id:
            # Add township price
            township_price = order.partner_shipping_id.township_id.price or 0.0
            if not self.free_township_amount:
                result["price"] += township_price
                # Update carrier_price to reflect the change
                if "carrier_price" in result:
                    result["carrier_price"] += township_price

        return result

    def _match_address(self, partner):
        self.ensure_one()
        if self.township_ids and partner.township_id not in self.township_ids:
            return False
        return super()._match_address(partner)

    @api.onchange("country_ids")
    def _onchange_country_ids(self):
        # Call parent method first
        super()._onchange_country_ids()
        # Clear all townships if no countries or no states
        self.township_ids = [Command.clear()]
