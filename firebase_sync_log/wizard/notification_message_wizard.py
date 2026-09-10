"""Noti Message Wizard"""

# pylint: disable=import-error
from odoo import _, fields, models

from ..models import message_notifications


class NotiMessageWizard(models.TransientModel):
    """Wizard for selecting and applying loyalty rewards to a sale order."""

    _name = "notification.message.wizard"
    _description = "Compose notification message Wizard"
    name = fields.Char(string="Notification Name")
    send_by = fields.Selection(
        [("by_user", "By User"), ("all", "All Users")],
        default="all",
    )
    send_to = fields.Many2many("res.users", string="Send To")
    title = fields.Char(string="Title")
    message = fields.Char(string="Message", required=True)

    def action_send(self):
        """Send notifications to selected users."""
        # Initialize empty recordset, not null
        users = self.env["res.users"].browse()

        if self.send_by == "all":
            users = self.get_all_portal_users()
        elif self.send_by == "by_user":
            users = self.send_to

        # If no users found, do nothing or raise warning
        if not users:
            return {
                "warning": {
                    "title": _("No Users Selected"),
                    "message": _("Please select users to send the notification."),
                }
            }

        # Send notification to each user
        for user in users:
            message_notifications.send_message_notification(
                user,
                self,
                self.title,
                self.message,
            )

        return {
            "type": "ir.actions.act_window_close",
        }

    def get_all_portal_users(self):
        """Get all portal users"""
        return self.env["res.users"].search([("share", "=", True)])
