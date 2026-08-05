"""Controller for handling shipping method related API endpoints in the Odoo eCommerce API."""

# pylint: disable=too-few-public-methods, import-error,too-many-arguments,line-too-long
from odoo import http
from odoo.exceptions import ValidationError
from odoo.http import request

from ..services.delivery_method_service import DeliveryMethodService
from ..services.token_service import JWTService
from .base import BaseAPI


class DeliveryMethodAPI(BaseAPI):
    """Controller class for handling delivery method related API endpoints"""

    @http.route(
        "/api/delivery-methods", type="http", auth="none", methods=["GET"], csrf=False
    )
    @JWTService.jwt_required()
    def get_shipping_methods(self):
        """Endpoint to retrieve available shipping methods for the current user's latest sale order."""
        try:
            user = request.authenticated_user
            return self._success(
                DeliveryMethodService().get_delivery_methods(user=user)
            )
        except ValidationError as e:
            return self._error(message=str(e), code=400)
