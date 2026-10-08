"""Add Township field to store the address"""

# pylint:disable=import-error,too-few-public-methods
from odoo import fields, models


class ResCompany(models.Model):
    """Modify the township of address for Company"""

    _inherit = "res.company"

    township_id = fields.Many2one(
        "res.township", string="Township", domain="[('state_id', '=?', state_id)]"
    )
