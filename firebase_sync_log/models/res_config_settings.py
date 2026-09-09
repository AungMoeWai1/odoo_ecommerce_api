"""Res Config Settings Inherit to add max users field"""

# pylint: disable=import-error,too-few-public-methods
from odoo import fields, models


class Company(models.Model):
    """Company Inherit to add notification send"""

    _inherit = "res.company"

    enable_notification = fields.Boolean(string="Enable Notification")


class ResConfigSettings(models.TransientModel):
    """Notification Setting on/off to send messages"""

    _inherit = "res.config.settings"

    enable_notification = fields.Boolean(
        related="company_id.enable_notification",
        string="Enable Notification",
        readonly=False,
    )
