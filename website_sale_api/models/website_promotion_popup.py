"""
Website Promotion Popup"""

# pylint:disable=import-error,too-few-public-methods
from odoo import fields, models


class WebsitePromotionPopup(models.Model):
    """Website Promotion Popup"""

    _name = "website.promotion.popup"
    _description = "Website Promotion Popup"
    _inherit = ["image.mixin"]

    product_id = fields.Many2one(
        "product.template",
        string="Product",
        domain=[("sale_ok", "=", True), ("is_published", "=", True)],
    )
    description = fields.Text(string="Description")
    is_published = fields.Boolean(string="Is Published", default=False)

    def action_toggle_is_published(self):
        """Toggle the field `is_published`."""
        self.is_published = not self.is_published

    def _can_return_content(self, field_name=None, access_token=None):
        """Field to allow to read without login"""
        if field_name in [
            "image_128",
            "image_1920",
            "image_512",
            "image_1024",
            "image_256",
        ]:
            return True
        return super()._can_return_content(field_name, access_token)
