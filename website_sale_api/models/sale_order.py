"""Inherit Sale order to add shipping status"""

# pylint:disable=import-error,too-few-public-methods,protected-access
from odoo import fields, models
from odoo.addons.firebase_sync_log.models import message_notifications


class SaleOrder(models.Model):
    """Shipping Status to sale order of ecommerce"""

    _inherit = "sale.order"

    shipping_status = fields.Selection(
        [
            ("draft", "Draft"),
            ("confirm", "Order Confirmed"),
            ("pick", "Picked"),
            ("pack", "Packed"),
            ("out", "Delivered"),
            ("cancel", "Cancelled"),
        ],
        default="draft",
        string="Shipping Status",
    )

    def action_confirm(self):
        """Action confirm the order"""
        if self.website_id:
            self.write({"shipping_status": "confirm"})

            message_notifications.send_message_notification(
                self.partner_id.user_ids[:1],
                self,
                "Sale order has Confirmed",
                f"Your order {self.name} has been confirmed!",
            )
        return super().action_confirm()

    def write(self, vals):
        """Send noti when shipping status change"""
        shipping_status = vals.get("shipping_status")
        res = super().write(vals)
        if shipping_status and (vals.get("state") == "sale" or self.state == "sale"):
            message_notifications.send_message_notification(
                self.partner_id.user_ids[:1],
                self,
                "Sale order has change delivery status",
                f"Your order {self.name} is change to {self.shipping_status}!",
            )
        return res

    def action_cancel(self):
        """Action cancel order"""
        res = super().action_cancel()
        self.write({"shipping_status": "cancel"})
        if self.shipping_status:
            message_notifications.send_message_notification(
                self.partner_id.user_ids[:1],
                self,
                "Sale order has canceled",
                f"Your order {self.name} is change to {self.shipping_status}!",
            )
        return res
