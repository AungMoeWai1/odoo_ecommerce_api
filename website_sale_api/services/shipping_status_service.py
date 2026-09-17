"""Shipping Status Service To Fetch all to show as filter bar"""

from ..schemas.shipping_status_schema import ShippingStatusSchema
from .base_service import BaseService


class ShippingStatusService(BaseService):
    """Shipping Status Service"""

    def __init__(self, env=None):
        super().__init__(env)
        self.model_name = "shipping.status"
        self.fields = [
            "id",
            "name"
        ]

    def fetch_all_shipping_status(self):
        """Fetch all shipping statuses"""
        shipping_states = self.search()

        return [
            ShippingStatusSchema(
                id=state.id,
                name=state.name
            )
            for state in shipping_states
        ]
