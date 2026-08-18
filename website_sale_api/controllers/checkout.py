"""Controller for handling checkout method related API endpoints in the Odoo eCommerce API."""

# pylint: disable=import-error,broad-exception-caught,protected-access,too-few-public-methods

from odoo import http
from odoo.exceptions import ValidationError
from odoo.http import request

from ..services.checkout_service import CheckoutService
from ..services.token_service import JWTService
from .base import BaseAPI


class CheckoutAPI(BaseAPI):
    """Controller class for handling Checkout related API endpoints"""

    @http.route(
        "/api/checkout", type="http", auth="public", methods=["POST"], csrf=False
    )
    @JWTService.jwt_required()
    def process_checkout(self):
        """Endpoint to retrieve available shipping methods"""
        try:
            user = request.authenticated_user
            return self._success(CheckoutService().process_checkout(user=user))
        except ValidationError as e:
            return self._error(message=str(e), code=400)
        except Exception as e:
            return self._error(message=str(e), code=400)
