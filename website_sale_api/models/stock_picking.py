"""Stock Picking API"""

# pylint:disable=import-error,too-few-public-methods
from odoo import models


class StockPicking(models.Model):
    """Add action button to write the sale order of picking type"""

    _inherit = "stock.picking"

    def button_validate(self):
        """Validate the picking type on sale order"""
        res = super().button_validate()
        if self.picking_type_id.sequence_code and self.sale_id:
            sequence_code = self.picking_type_id.sequence_code.lower()
            if sequence_code in ("pick", "pack", "out"):
                self.sale_id.shipping_status = sequence_code
        return res
