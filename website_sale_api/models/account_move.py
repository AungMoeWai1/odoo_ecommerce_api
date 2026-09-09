"""Account Move Model"""

# pylint:disable=import-error,too-few-public-methods
from odoo import models
from odoo.addons.firebase_sync_log.models import message_notifications


class AccountMove(models.Model):
    """Modify Account Move for invoice confirm & payment paid"""

    _inherit = "account.move"

    def action_post(self):
        """Send notification when invoice is confirmed/posted"""
        # First, call super to post the invoice
        result = super().action_post()

        # Then send notifications for each confirmed invoice
        for invoice in self:
            if (
                invoice.state == "posted"
                and invoice.payment_state != "paid"
                and invoice.move_type == "out_invoice"
            ):
                # Get the user to notify
                user = (
                    invoice.partner_id.parent_id.user_ids[:1]
                    or invoice.partner_id.user_ids[:1]
                )
                if user:
                    message_notifications.send_message_notification(
                        user,
                        invoice,
                        "Invoice Confirmed",
                        f"Your Invoice {invoice.name} has been confirmed/posted!",
                    )

        return result

    def _track_subtype(self, init_values):
        """Send payment notification when invoice is fully paid"""
        # Check if payment_state changed to 'paid' and invoice is fully paid
        if (
            "payment_state" in init_values
            and self.payment_state == "paid"
            and self.amount_residual <= 0
        ):

            # Get the user to notify
            user = (
                self.partner_id.parent_id.user_ids[:1] or self.partner_id.user_ids[:1]
            )
            if user:
                message_notifications.send_message_notification(
                    user,
                    self,
                    "Invoice Fully Paid",
                    f"Your Invoice {self.name} has been fully paid!",
                )

        return super()._track_subtype(init_values)
