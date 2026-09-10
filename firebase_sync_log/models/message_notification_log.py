"""Notification Log Module"""

# pylint:disable=import-error,too-few-public-methods,protected-access
from odoo import api, fields, models


class MessageNotificationLog(models.Model):
    """
    Common field for the log
    """

    _name = "message.notification.log"
    _description = "Message Notification Log"
    _order = "create_date desc"

    name = fields.Char(string="Notification Name", compute="_compute_name")

    receiver_id = fields.Many2one("res.users", string="Receiver", ondelete="cascade")

    model_name = fields.Char(string="Model")
    record_id = fields.Many2oneReference(
        model_field="model_name",
        help="Reference to the record in the model",
    )
    reference = fields.Char(string="Record", compute="_compute_ref")
    status = fields.Selection(
        [("fail", "Fail"), ("success", "Success")],
        string="Status",
        readonly=True,
        copy=False,
        default="fail",
    )
    read_status = fields.Selection(
        [
            ("unread", "Unread"),
            ("read", "Read"),
        ],
        string="Read Status",
        default="unread",
        copy=False,
    )
    title = fields.Char(string="Title")
    body = fields.Char(string="Body")

    @api.depends("model_name", "record_id")
    def _compute_ref(self):
        """Compute reference field."""
        for record in self:
            if record.model_name and record.record_id:
                record.reference = f"{record.model_name},{record.record_id}"
            else:
                record.reference = False

    @api.depends("record_id", "model_name")
    def _compute_name(self):
        """Compute name field."""
        for record in self:
            name = self.env[record.model_name].browse(record.record_id).name
            record.name = name if name else "Publish Message"

    def action_send_message(self):
        """Show message wizard"""
        return self.env["ir.actions.actions"]._for_xml_id(
            "firebase_sync_log.noti_message_wizard_action"
        )
