"""Controller for managing shipping addresses in the Odoo e-commerce API."""

# pylint: disable=too-few-public-methods, import-error,too-many-arguments,too-many-positional-arguments,redefined-builtin,raise-missing-from,consider-using-in,broad-exception-caught
import json

from odoo import http
from odoo.exceptions import ValidationError
from odoo.http import request

from ..services.address_service import get_shipping_address_service
from ..services.token_service import JWTService
from .base import BaseAPI


class AddressAPI(BaseAPI):
    """Controller class for handling shipping address related API endpoints"""

    @http.route(
        "/api/address", type="http", auth="none", methods=["POST"], csrf=False
    )
    @JWTService.jwt_required
    def create_shipping_address(self):
        """Create a new shipping address for the authenticated user"""

        user = request.authenticated_user
        params = json.loads(request.httprequest.data or "{}")
        name = params.get("name")
        email = params.get("email")
        phone = params.get("phone")
        street = params.get("street")
        city = params.get("city")
        zip = params.get("zip")
        country = params.get("country")

        return self.handle(
            lambda: get_shipping_address_service().create_shipping_address(
                user=user,
                name=name,
                email=email,
                phone=phone,
                street=street,
                city=city,
                zip=zip,
                country=country,
            )
        )

    @http.route(
        "/api/address", type="http", auth="none", methods=["GET"], csrf=False
    )
    @JWTService.jwt_required
    def get_shipping_address(self):
        """Retrieve the authenticated user's shipping address information"""
        user = request.authenticated_user
        return self.handle(
            lambda: get_shipping_address_service().get_shipping_address(user=user)
        )

    @http.route(
        "/api/address", type="http", auth="none", methods=["PUT"], csrf=False
    )
    @JWTService.jwt_required
    def update_shipping_address(self, **kwargs):
        """Update the authenticated user's shipping address information"""

        user = request.authenticated_user
        partner_id = kwargs.get("partner_id")

        if not partner_id:
            raise ValidationError("Partner ID is required")

        params = json.loads(request.httprequest.data or "{}")

        name = params.get("name")
        email = params.get("email")
        phone = params.get("phone")
        street = params.get("street")
        city = params.get("city")
        zip = params.get("zip")
        country = params.get("country")

        return self.handle(
            lambda: get_shipping_address_service().update_shipping_address(
                user=user,
                partner_id=partner_id,
                name=name,
                email=email,
                phone=phone,
                street=street,
                city=city,
                zip=zip,
                country=country,
            )
        )

    @http.route(
        "/api/address/<int:partner_id>",
        type="http",
        auth="none",
        methods=["DELETE"],
        csrf=False,
    )
    @JWTService.jwt_required
    def delete_shipping_address(self, partner_id):
        """Update the authenticated user's shipping address information"""

        user = request.authenticated_user

        return self.handle(
            lambda: get_shipping_address_service().delete_shipping_address(
                user=user, partner_id=partner_id
            )
        )
