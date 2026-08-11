"""Controller for managing shipping addresses in the Odoo e-commerce API."""

# pylint: disable=too-few-public-methods, import-error,too-many-arguments,too-many-positional-arguments,redefined-builtin,raise-missing-from,consider-using-in,broad-exception-caught
import json

from odoo import http
from odoo.exceptions import ValidationError
from odoo.http import request

from ..services.address_service import ShippingAddressService
from ..services.token_service import JWTService
from .base import BaseAPI


class AddressAPI(BaseAPI):
    """Controller class for handling shipping address related API endpoints"""

    @http.route(
        "/api/countries/<int:cid>/states",
        type="http",
        auth="public",
        methods=["GET"],
        csrf=False,
    )
    @JWTService.jwt_required()
    def get_state(self, cid):
        """Get the state of the authenticated user"""
        return self._success(ShippingAddressService().get_state(country_id=cid))

    @http.route(
        "/api/countries/<int:cid>/townships",
        type="http",
        auth="public",
        methods=["GET"],
        csrf=False,
    )
    @JWTService.jwt_required()
    def get_township(self, cid):
        """Get the state of the authenticated user"""
        return self._success(
            ShippingAddressService().get_state_townships(country_id=cid)
        )

    @http.route(
        "/api/my/address", type="http", auth="public", methods=["GET"], csrf=False
    )
    @JWTService.jwt_required()
    def get_shipping_address(self):
        """Retrieve the authenticated user's shipping address information"""
        user = request.authenticated_user
        return self._success(ShippingAddressService().get_partner_addresses(user=user))

    @http.route(
        "/api/my/address", type="http", auth="public", methods=["POST"], csrf=False
    )
    @JWTService.jwt_required()
    def create_shipping_address(self):
        """Create a new shipping address for the authenticated user"""

        user = request.authenticated_user
        data = json.loads(request.httprequest.data or "{}")

        return self._success(
            ShippingAddressService().create_address(user=user, data=data)
        )

    @http.route(
        "/api/my/address/<int:address_id>",
        type="http",
        auth="public",
        methods=["PUT"],
        csrf=False,
    )
    @JWTService.jwt_required()
    def update_shipping_address(self, address_id):
        """Update the authenticated user's shipping address information"""

        user = request.authenticated_user

        data = json.loads(request.httprequest.data or "{}")

        try:
            return self._success(
                ShippingAddressService().update_address(
                    user=user, partner_id=address_id, data=data
                )
            )
        except ValidationError as ve:
            return self._error(str(ve))

    @http.route(
        "/api/my/address/<int:partner_id>",
        type="http",
        auth="public",
        methods=["DELETE"],
        csrf=False,
    )
    @JWTService.jwt_required()
    def delete_shipping_address(self, partner_id):
        """Update the authenticated user's shipping address information"""

        user = request.authenticated_user

        try:
            return self._success(
                ShippingAddressService().delete_address(
                    user=user, partner_id=partner_id
                )
            )
        except ValidationError as ve:
            return self._error(str(ve))