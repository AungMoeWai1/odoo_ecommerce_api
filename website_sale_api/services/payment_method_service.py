"""Service for handling cart-related business logic."""

# pylint:disable=import-error,broad-exception-caught,protected-access

from odoo.exceptions import ValidationError

from ..schemas.payment_methods_schema import PaymentMethodData, PaymentMethodsResponse
from .base_service import BaseService


class PaymentMethodService(BaseService):
    """Service for cart-related operations"""

    def __init__(self, env=None):
        super().__init__(env)
        self.model_name = "payment.method"
        self.website = self._get_current_website()

    def get_website_payment_methods(self, user):
        """Get current cart/sale order for the user"""
        sale_order = self._get_sale_order(self.website.id, user)
        payment_methods = self._get_model()._get_payment_methods(
            sale_order, website_id=self.website.id
        )
        if not payment_methods:
            raise ValidationError("No payment methods found")
        payment_list = []
        for method in payment_methods:
            payment_list.append(PaymentMethodData(id=method["id"], name=method["name"]))
        return PaymentMethodsResponse(
            data=payment_list,
        )
