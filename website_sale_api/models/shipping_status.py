"""Shipping Status For ecommerce orders"""

# pylint:disable=import-error,too-few-public-methods
from odoo import fields, models


class ShippingStatus(models.Model):
    """Shipping Status for ecommerce order"""

    _name = "shipping.status"
    _description = "Shipping Status"
    _order = "sequence asc"

    name = fields.Char(string="Name")
    sequence = fields.Integer(string="Sequence")
