"""Inherit Sale order to add shipping status"""

# pylint:disable=import-error,too-few-public-methods,protected-access
from odoo import api, fields, models


class SaleOrder(models.Model):
    """Shipping Status to sale order of ecommerce"""

    _inherit = "sale.order"

    shipping_status_id = fields.Many2one(
        "shipping.status",
        string="Shipping Status",
    )

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('website_id'):
                vals['shipping_status_id'] = self.env.ref("website_sale_api.shipping_status_draft"
                                                          ).id
        return super().create(vals_list)

    def action_confirm(self):
        """Action confirm the order"""
        if self.website_id:
            self.write({"shipping_status_id": self.env.ref(
                "website_sale_api.shipping_status_order_confirmed"
            ).id})
        return super().action_confirm()
