"""Portal controller for the website_sale_api module."""

# pylint:disable=import-error,too-few-public-methods,protected-access
from odoo import http
from odoo.addons.portal.controllers.portal import CustomerPortal
from odoo.http import request


class CustomCustomerPortal(CustomerPortal):
    """Custom Customer Portal to include township information in the address form."""

    def _prepare_address_form_values(
        self,
        partner_sudo,
        address_type="billing",
        use_delivery_as_billing=False,
        callback="",
        **kwargs
    ):
        """Prepare the values for the address form, including township information."""
        result = super()._prepare_address_form_values(
            partner_sudo,
            address_type=address_type,
            use_delivery_as_billing=use_delivery_as_billing,
            callback=callback,
            **kwargs
        )

        current_partner = request.env["res.partner"]._get_current_partner(**kwargs)

        if partner_sudo:
            state_sudo = partner_sudo.state_id
            township_id = (
                partner_sudo.township_id.id if partner_sudo.township_id else False
            )
        else:
            state_sudo = current_partner.state_id or self._get_default_state(**kwargs)
            township_id = (
                current_partner.township_id.id if current_partner.township_id else False
            )
        result["township_id"] = township_id
        result["state_townships"] = state_sudo.township_ids

        return result

    @http.route("/my/address/townships", type="jsonrpc", auth="user", methods=["POST"])
    def get_townships(self, **kwargs):
        """Get townships for a given state"""
        state_id = kwargs.get("state_id")
        if not state_id:
            return []

        townships = (
            request.env["res.township"].sudo().search([("state_id", "=", state_id)])
        )

        return [
            {
                "id": t.id,
                "name": t.name,
                "price": t.price,
            }
            for t in townships
        ]

    @http.route(
        '/my/address/state_info/<model("res.country.state"):state>',
        type="jsonrpc",
        auth="public",
        methods=["POST"],
        website=True,
        readonly=True,
    )
    def portal_address_state_info(self, state):
        """Return the townships for a given state."""
        return {
            "townships": [(tsp.id, tsp.name) for tsp in state.sudo().township_ids],
        }
