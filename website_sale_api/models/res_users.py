"""Override read access field to read without login"""

# pylint:disable=import-error,too-few-public-methods
from odoo import models


class ResUsers(models.Model):
    """Override read access field to read without login"""

    _inherit = "res.users"

    def _can_return_content(self, field_name=None, access_token=None):
        """Field to allow to read without login"""
        if field_name in [
            "image_1920",
            "image_1024",
            "image_512",
            "image_256",
            "image_128",
        ]:
            return True
        return super()._can_return_content(field_name, access_token)
