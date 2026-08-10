"""Payment Method extension to add business logic"""

# pylint:disable=import-error,protected-access,too-few-public-methods
from odoo import models


class PaymentMethod(models.Model):
    """Payment Method extension get payment methods"""

    _inherit = "payment.method"

    def _get_payment_methods(self, order_sudo, **kwargs):
        """Return the payment-specific QWeb context values.

        :param sale.order order_sudo: The sales order being paid.
        :param bool is_down_payment: Whether the current payment is a down payment.
        :param float payment_amount: The amount suggested in the payment link.
        :param dict kwargs: Locally unused data passed to `_get_compatible_providers` and
                            `_get_available_tokens`.
        :return: The payment-specific values.
        :rtype: dict
        """
        partner_sudo = order_sudo.partner_id
        currency = order_sudo.currency_id
        # Select all the payment methods and tokens that match the payment context.
        providers_sudo = (
            self.env["payment.provider"]
            .sudo()
            ._get_compatible_providers(
                order_sudo.company_id.id,
                partner_sudo.id,
                order_sudo.amount_total,
                currency_id=currency.id,
                sale_order_id=order_sudo.id,
                report={},
                **kwargs,
            )
        )
        payment_methods_sudo = self.sudo()._get_compatible_payment_methods(
            providers_sudo.ids,
            partner_sudo.id,
            currency_id=currency.id,
            sale_order_id=order_sudo.id,
            report={},
            **kwargs,
        )
        return [
            {"id": method.id, "name": method.name} for method in payment_methods_sudo
        ]
