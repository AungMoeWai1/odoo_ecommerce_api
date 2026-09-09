"""Inherit Sale order to add shipping status"""

# pylint:disable=import-error,too-few-public-methods,protected-access
from odoo import api, fields, models
from odoo.addons.firebase_sync_log.models import message_notifications


class SaleOrder(models.Model):
    """Shipping Status to sale order of ecommerce"""

    _inherit = "sale.order"

    shipping_status_id = fields.Many2one(
        "shipping.status",
        string="Shipping Status",
    )

    @api.model_create_multi
    def create(self, vals_list):
        """Create sale order"""
        for vals in vals_list:
            if vals.get("website_id"):
                vals["shipping_status_id"] = self.env.ref(
                    "website_sale_api.shipping_status_draft"
                ).id
        return super().create(vals_list)

    def action_confirm(self):
        """Action confirm the order"""
        if self.website_id:
            self.write(
                {
                    "shipping_status_id": self.env.ref(
                        "website_sale_api.shipping_status_order_confirmed"
                    ).id
                }
            )

            message_notifications.send_message_notification(
                self.partner_id.user_ids[:1],
                self,
                "Sale order has Confirmed",
                f"Your order {self.name} has been confirmed!",
            )
        return super().action_confirm()

    def write(self, vals):
        """Send noti when shipping status change"""
        shipping_status = vals.get("shipping_status_id")
        if shipping_status and (vals.get("state") == "sale" or self.state == "sale"):
            message_notifications.send_message_notification(
                self.partner_id.user_ids[:1],
                self,
                "Sale order has change delivery status",
                f"Your order {self.name} is change to {self.shipping_status_id.name}!",
            )
        res = super().write(vals)
        return res
