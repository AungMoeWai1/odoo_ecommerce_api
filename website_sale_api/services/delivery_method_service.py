"""Service class for managing shipping methods in the Odoo eCommerce API."""

# pylint: disable=too-few-public-methods, import-error,protected-access

from ..schemas.delivery_method_schema import DeliveryMethodSchema
from .base_service import BaseService


class DeliveryMethodService(BaseService):
    """Service class for managing shipping methods"""

    def __init__(self, env=None):
        super().__init__(env)
        self.model_name = "delivery.carrier"
        self.fields = [
            "id",
            "name",
            "website_description",
            "carrier_description",
            "currency_id",
        ]
        self.website = self._get_current_website()

    def get_delivery_methods(self, user) -> list[DeliveryMethodSchema]:
        """Get available delivery methods for the user's latest sale order"""
        order_sudo = self._get_sale_order(self.website.id, user)
        order_sudo = order_sudo.with_context(website_id=order_sudo.website_id.id)
        available_dms = self._get_model().get_delivery_method(order_sudo)

        return [DeliveryMethodSchema(**dm) for dm in available_dms]

    def _set_order_delivery_method(self, delivery_method_id, user):
        order_sudo = self._get_sale_order(self.website.id, user)
        delivery_method_sudo = (
            self.env["delivery.carrier"].sudo().browse(delivery_method_id).exists()
        )
        order_sudo._set_delivery_method(delivery_method_sudo)
        return {
            "order_id": order_sudo.id,
            "delivery_amount": order_sudo.amount_delivery,
            "total_amount": order_sudo.amount_total,
            "message": "Delivery method has been added.",
        }
