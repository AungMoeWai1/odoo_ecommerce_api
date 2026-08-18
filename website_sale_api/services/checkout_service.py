"""Service for handling cart-related business logic."""

# pylint:disable=import-error,broad-exception-caught,protected-access,too-few-public-methods
import json
from typing import Any, Dict

from odoo.addons.payment.controllers import post_processing
from odoo.addons.payment_custom.controllers import main
from odoo.addons.website_sale.controllers import main as website_sale_main
from odoo.exceptions import ValidationError
from odoo.http import request

from ..controllers import payment
from .base_service import BaseService


class CheckoutService(BaseService):
    """Service for cart-related operations"""

    def __init__(self, env=None):
        super().__init__(env)
        self.model_name = "sale.order"
        self.website = self._get_current_website()

        self._payment_service = PaymentService()
        self._order_validation_service = OrderValidationService()
        self._order_finalization_service = OrderFinalizationService()

    def process_checkout(self, user) -> Dict[str, Any]:
        """
        Process checkout for a user.

        Step by step:
        1. Get the sale order
        2. Process payment
        3. Validate the order
        4. Finalize the order
        5. Return success response
        """
        # Step 1: Get the sale order
        order = self._get_sale_order(self.website.id, user)
        if not order:
            raise ValidationError("Your Cart is Empty!")

        # Step 2: Process payment
        self._payment_service.process_payment(order)

        # Step 3: Validate the order
        self._order_validation_service.validate_order(order)

        # Step 4: Finalize the order
        self._order_finalization_service.finalize_order(order)

        # Step 5: Return success response
        return {
            "status": "success",
            "id": order.id,
            "message": "Checkout successfully",
        }


class PaymentService:
    """Handles all payment-related operations."""

    def __init__(self):
        self._payment_controller = None
        self._custom_controller = None
        self._post_processing_controller = None

    def process_payment(self, order) -> None:
        """
        Process payment for the order.

        Step by step:
        1. Create payment transaction
        2. Process custom transaction
        3. Monitor transaction
        4. Poll payment status
        5. Complete payment transaction
        """
        transaction = self._create_payment_transaction(order)

        # Step 2: Process custom transaction
        self._process_custom_transaction(order)

        # Step 3: Monitor transaction
        self._monitor_transaction(transaction)

        # Step 4: Poll payment status
        self._poll_payment_status()

        # Step 5: Complete payment transaction
        self._complete_payment_transaction()

    def _create_payment_transaction(self, order):
        """Step 1: Create payment transaction."""
        params = self._get_request_params()
        payment_controller = self._get_payment_controller()

        params.update(
            {
                "provider_id": self._get_provider(params.get("payment_method_id")),
            }
        )
        result = payment_controller.order_payment_transaction(order, **params)

        transaction = request.env["payment.transaction"].sudo().browse(result.get("id"))
        return transaction

    def _get_provider(self, payment_method_id):
        """Get the lowest provider ID from a payment method."""
        pm_id = request.env["payment.method"].sudo().browse(payment_method_id)
        lowest_provider = pm_id.provider_ids.sorted(key="id")[0]
        return lowest_provider.id

    def _process_custom_transaction(self, order):
        """Step 2: Process custom transaction."""
        custom_controller = self._get_custom_controller()
        post_data = {"reference": order.name}
        custom_controller.custom_process_transaction(**post_data)

    def _monitor_transaction(self, transaction):
        """Step 3: Monitor the transaction."""
        post_processing.PaymentPostProcessing.monitor_transaction(transaction)

    def _poll_payment_status(self):
        """Step 4: Poll payment status."""

        payment_controller = post_processing.PaymentPostProcessing()
        payment_controller.poll_status()

    def _complete_payment_transaction(self):
        """Step 5: Complete payment transaction."""
        request.env["payment.transaction"].sudo()._process("custom", {})

    def _get_request_params(self) -> Dict[str, Any]:
        """Extract request parameters from HTTP request."""
        return json.loads(request.httprequest.data)

    def _get_payment_controller(self):
        """Lazy load payment controller."""
        if self._payment_controller is None:
            self._payment_controller = payment.PaymentPortal()
        return self._payment_controller

    def _get_custom_controller(self):
        """Lazy load custom controller."""
        if self._custom_controller is None:
            self._custom_controller = main.CustomController()
        return self._custom_controller


class OrderValidationService:
    """Handles order validation logic."""

    def __init__(self):
        self._website_sale_controller = None

    def validate_order(self, order) -> None:
        """
        Validate the order.

        Step by step:
        1. Check for payment errors
        2. Validate transaction amount
        """
        # Step 1: Check for payment errors
        self._check_payment_errors(order)

        # Step 2: Validate transaction amount
        self._validate_transaction_amount(order)

    def _check_payment_errors(self, order) -> None:
        """Step 1: Check for payment errors."""
        if order.state == "sale":
            return

        errors = self._get_payment_errors(order)
        if errors:
            first_error = errors[0]
            error_msg = f"{first_error[0]}\n{first_error[1]}"
            raise ValidationError(error_msg)

    def _get_payment_errors(self, order):
        """
        Get payment errors for the order.
        Handles the case where the controller method might fail.
        """
        try:
            # Try to call as instance method
            website_sale = self._get_website_sale_controller()
            return website_sale._get_shop_payment_errors(order)
        except TypeError:
            # Fallback: Call as class method
            return website_sale_main.WebsiteSale._get_shop_payment_errors(order)
        except Exception as _:
            return []

    def _get_website_sale_controller(self):
        """Lazy load website sale controller."""
        if self._website_sale_controller is None:
            self._website_sale_controller = website_sale_main.WebsiteSale()
        return self._website_sale_controller

    def _validate_transaction_amount(self, order) -> None:
        """Step 2: Validate transaction amount."""
        tx_sudo = order.get_portal_last_transaction()
        if order.amount_total and not tx_sudo:
            raise ValidationError("Amount is not match!")


class OrderFinalizationService:
    """Handles order finalization logic."""

    def finalize_order(self, order) -> None:
        """
        Finalize the order after successful validation.

        Step by step:
        1. Check if order is ready to be paid (for zero amount orders)
        2. Validate the order
        """
        tx_sudo = order.get_portal_last_transaction()
        if not order.amount_total and not tx_sudo and order.state != "sale":
            order._check_cart_is_ready_to_be_paid()
            # Only confirm the order if it wasn't already confirmed.
            order._validate_order()
