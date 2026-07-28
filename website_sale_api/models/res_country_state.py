"""Add township for the country state model."""

# pylint:disable=import-error,too-few-public-methods
from odoo import fields, models


class ResCountryState(models.Model):
    """Add township for the country state model."""

    _inherit = "res.country.state"

    township_ids = fields.One2many("res.township", "state_id", string="Townships")
