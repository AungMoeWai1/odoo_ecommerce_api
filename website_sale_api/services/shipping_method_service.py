"""Service class for managing shipping methods in the Odoo eCommerce API."""

# pylint: disable=too-few-public-methods, import-error,too-many-arguments,line-too-long,broad-exception-caught
import logging
from odoo.http import request
from odoo.exceptions import ValidationError
from ..schemas.shipping_method_schema import ShippingMethodSchema

_logger = logging.getLogger(__name__)


class ShippingMethodService:
    """Service class for managing shipping methods"""

    def get_shipping_method(self, user):
        """Get available shipping methods for the user's latest sale order"""

        partner = user.partner_id
        if not partner:
            raise ValidationError("User not found")

        order = (
            request.env["sale.order"]
            .sudo()
            .search(
                [("partner_id", "=", user.partner_id.id)],
                order="create_date desc",
                limit=1,
            )
        )

        if not order:
            raise ValidationError("Sale Order not found")

        shipping_methods = (
            request.env["delivery.carrier"]
            .sudo()
            .search(
                [
                    ("is_published", "=", True),
                ]
            )
        )

        result = []

        for carrier in shipping_methods:
            price = 0.0
            try:
                if carrier.delivery_type in ["fixed", "base_on_rule"]:
                    rate = carrier.rate_shipment(order)
                    if rate.get("success"):
                        price = rate.get("price", 0.0)

            except Exception:
                _logger.exception(
                    "Failed to calculate shipping price for carrier %s", carrier.name
                )

            result.append(
                ShippingMethodSchema(
                    id=carrier.id,
                    name=carrier.name,
                    website_description=carrier.website_description,
                    carrier_description=carrier.carrier_description,
                    price=price,
                    currency=carrier.currency_id.name,
                ).model_dump()
            )

        return result


def get_shipping_method_service():
    """Factory method to get an instance of ShippingAddressService"""
    return ShippingMethodService()
