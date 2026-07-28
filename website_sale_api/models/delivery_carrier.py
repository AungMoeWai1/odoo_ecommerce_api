"""Add township for the delivery carrier model."""

# pylint:disable=import-error,too-few-public-methods
from odoo import fields, models


class DeliveryCarrier(models.Model):
    """Add township for the delivery carrier model."""

    _inherit = "delivery.carrier"

    township_ids = fields.Many2many("res.township", string="Townships")
