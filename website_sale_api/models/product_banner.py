"""Product Banner Model"""

# pylint:disable=import-error,too-few-public-methods
from odoo import fields, models


class ProductBanner(models.Model):
    """Product Banner Model"""

    _name = "product.banner"
    _description = "Product Banner"
    _inherit = ["image.mixin"]

    description = fields.Text(string="Description")

    def _can_return_content(self, field_name=None, access_token=None):
        """Field to allow to read without login"""
        if field_name in [
            "image_1024",
            "image_1920",
            "image_256",
            "image_512",
            "image_128",
        ]:
            return True
        return super()._can_return_content(field_name, access_token)
