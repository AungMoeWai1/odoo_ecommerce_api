"""Township to define the amount of delivery charge for ecommerce order"""

# pylint:disable=import-error,too-few-public-methods
from odoo import fields, models


class ResTownship(models.Model):
    """Township to define the amount of delivery charge for ecommerce order"""

    _name = "res.township"
    _description = "Township"

    name = fields.Char(string="Township Name", required=True)
    price = fields.Float(string="Price", required=True, default=0)
    state_id = fields.Many2one(
        comodel_name="res.country.state", string="State", required=True
    )
