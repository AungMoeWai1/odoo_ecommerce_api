"""Payment controller"""

# pylint:disable=import-error,too-few-public-methods,protected-access,E0611,W0613,W0707
from odoo import _
from odoo.addons.payment.controllers import portal as payment_portal
from odoo.exceptions import AccessError, MissingError, UserError, ValidationError
from odoo.fields import Command
from odoo.http import request
from odoo.tools import SQL
from psycopg2.errors import LockNotAvailable


class PaymentPortal(payment_portal.PaymentPortal):
    """
    The Custom Payment Portal API enables third-party applications to initiate payments,
    retrieve transaction history, validate payment methods,
    and handle webhook notifications.
    """

    def _validate_transaction_for_order(self, transaction, sale_order):
        """
        Perform final checks against the transaction & sale_order.
        Override me to apply payment unrelated checks & processing
        """
        return

    def order_payment_transaction(self, order, **kwargs):
        """Display the checkout page.

        :param str try_skip_step: Whether the user should immediately be redirected to the next step
                                  if no additional information (i.e., address or delivery method) is
                                  required on the checkout page. 'true' or 'false'.
        :param dict query_params: The additional query string parameters.
        :return: The rendered checkout page.
        :rtype: str
        """
        try:
            order_sudo = order
            request.env.cr.execute(
                SQL(
                    "SELECT 1 FROM sale_order WHERE id = %s FOR NO KEY UPDATE NOWAIT",
                    order.id,
                )
            )
        except MissingError:
            raise
        except AccessError as e:
            raise ValidationError(_("The access token is invalid.")) from e
        except LockNotAvailable:
            raise UserError(_("Payment is already being processed."))

        if order_sudo.state == "cancel":
            raise ValidationError(_("The order has been cancelled."))

        order_sudo._check_cart_is_ready_to_be_paid()

        self._validate_transaction_kwargs(kwargs)
        kwargs.update(
            {
                "partner_id": order_sudo.partner_invoice_id.id,
                "currency_id": order_sudo.currency_id.id,
                "sale_order_id": order.id,
                "landing_route": "/shop/payment/validate",
                "token_id": None,
                "flow": "redirect",
                "tokenization_requested": False,
                "is_validation": False,
            }
        )

        if not kwargs.get("amount"):
            kwargs["amount"] = order_sudo.amount_total

        compare_amounts = order_sudo.currency_id.compare_amounts
        if compare_amounts(kwargs["amount"], order_sudo.amount_total):
            raise ValidationError(
                _("The cart has been updated. Please refresh the page.")
            )
        if compare_amounts(order_sudo.amount_paid, order_sudo.amount_total) == 0:
            raise UserError(
                _("The cart has already been paid. Please refresh the page.")
            )

        if delay_token_charge := kwargs.get("flow") == "token":
            request.update_context(
                delay_token_charge=True
            )  # wait until after tx validation
        print("Kwargs:", kwargs)
        tx_sudo = self._create_transaction(
            custom_create_values={"sale_order_ids": [Command.set([order.id])]},
            **kwargs,
        )

        # Store the new transaction into the transaction list and if there's an old one, we remove
        # it until the day the ecommerce supports multiple orders at the same time.
        request.session["__website_sale_last_tx_id"] = tx_sudo.id

        self._validate_transaction_for_order(tx_sudo, order_sudo)
        if delay_token_charge:
            tx_sudo._charge_with_token()

        processing_values = tx_sudo._get_processing_values()
        processing_values["id"] = tx_sudo.id
        return processing_values
