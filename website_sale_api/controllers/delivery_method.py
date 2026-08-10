"""Controller for handling shipping method related API endpoints in the Odoo eCommerce API."""

# pylint: disable=import-error,broad-exception-caught,protected-access
import json

from odoo import http
from odoo.exceptions import ValidationError
from odoo.http import request

from ..services.delivery_method_service import DeliveryMethodService
from ..services.token_service import JWTService
from .base import BaseAPI


class DeliveryMethodAPI(BaseAPI):
    """Controller class for handling delivery method related API endpoints"""

    @http.route(
        "/api/delivery-methods", type="http", auth="public", methods=["GET"], csrf=False
    )
    @JWTService.jwt_required()
    def get_shipping_methods(self):
        """Endpoint to retrieve available shipping methods"""
        try:
            user = request.authenticated_user
            return self._success(
                DeliveryMethodService().get_delivery_methods(user=user)
            )
        except ValidationError as e:
            return self._error(message=str(e), code=400)
        except Exception as e:
            return self._error(message=str(e), code=400)

    @http.route(
        "/api/delivery-methods",
        type="http",
        auth="public",
        methods=["POST"],
        csrf=False,
    )
    @JWTService.jwt_required()
    def set_shipping_method(self):
        """Endpoint to retrieve available shipping methods"""
        try:
            user = request.authenticated_user
            params = json.loads(request.httprequest.data or "{}")
            dm_id = params.get("delivery_method_id")
            return self._success(
                DeliveryMethodService()._set_order_delivery_method(dm_id, user=user)
            )
        except ValidationError as e:
            return self._error(message=str(e), code=400)
        except Exception as e:
            return self._error(message=str(e), code=400)
