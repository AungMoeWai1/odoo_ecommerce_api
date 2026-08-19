"""Inherit Sale order to add shipping status"""

# pylint:disable=import-error,too-few-public-methods,protected-access
from odoo import fields, models


class SaleOrder(models.Model):
    """Shipping Status to sale order of ecommerce"""

    _inherit = "sale.order"

    shipping_status_id = fields.Many2one(
        "shipping.status",
        string="Shipping Status",
        default=lambda self: self._get_default_shipping_status(),
    )

    def _get_default_shipping_status(self):
        """Get default shipping status (Draft)"""
        if not self.website_id:
            return self.env.ref("website_sale_api.shipping_status_draft").id
        return False

    def action_confirm(self):
        """Action confirm the order"""
        if self.website_id:
            self.shipping_status_id = self.env.ref(
                "website_sale_api.shipping_status_order_confirmed"
            ).id
        return super().action_confirm()
