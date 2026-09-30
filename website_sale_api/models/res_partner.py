"""Add township for the res.partner model."""

# pylint:disable=import-error,too-few-public-methods
from odoo import api, fields, models


class ResPartner(models.Model):
    """Add township for the res.partner model."""

    _inherit = "res.partner"

    township_id = fields.Many2one(
        "res.township", string="Township", domain="[('state_id', '=?', state_id)]"
    )

    @api.model
    def _get_frontend_writable_fields(self):
        """Return the list of fields that can be written from the frontend."""
        result = super()._get_frontend_writable_fields()
        # Add township_id to the list of writable fields
        result.update({"township_id"})
        return result

    def _can_return_content(self, field_name=None, access_token=None):
        """Field to allow to read without login"""
        if field_name in [
            "image_256"
        ]:
            return True
        return super()._can_return_content(field_name, access_token)
