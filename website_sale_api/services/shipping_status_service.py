"""Shipping Status Service To Fetch all to show as filter bar"""

# pylint:disable=protected-access
from ..schemas.shipping_status_schema import ShippingStatusSchema
from .base_service import BaseService


class ShippingStatusService(BaseService):
    """Shipping Status Service"""

    def __init__(self, env=None):
        super().__init__(env)
        self.model_name = "sale.order"
        self.fields = ["id", "shipping_status"]

    def fetch_all_shipping_status(self):
        """Fetch all shipping status options from sale.order"""
        selection = (
            self._get_model()
            ._fields["shipping_status"]
            ._description_selection(self.env)
        )

        return [
            ShippingStatusSchema(key=key, name=label)
            for key, label in selection
            if key != "draft"
        ]
