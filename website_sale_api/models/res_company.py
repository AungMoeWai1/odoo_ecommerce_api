from odoo import fields, models


class ResCompany(models.Model):
    _inherit = "res.company"

    township_id = fields.Many2one(
        "res.township", string="Township", domain="[('state_id', '=?', state_id)]"
    )
