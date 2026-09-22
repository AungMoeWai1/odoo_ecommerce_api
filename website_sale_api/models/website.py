"""website_sale_api.models.website"""

# pylint:disable=import-error,too-few-public-methods
from odoo import fields, models


class Website(models.Model):
    """Added Website of term and conditions"""

    _inherit = "website"

    term_and_condition = fields.Html(string="Term and Condition")
