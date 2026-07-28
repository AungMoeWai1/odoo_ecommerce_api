"""Controller for handling shipping method related API endpoints in the Odoo eCommerce API."""

# pylint: disable=too-few-public-methods, import-error,too-many-arguments,line-too-long
from odoo import http

from ..services.shipping_method_service import get_shipping_method_service
from ..services.token_service import get_current_user, jwt_required
from .base import BaseAPI


class ShippingMethodAPI(BaseAPI):
    """Controller class for handling shipping method related API endpoints"""

    @http.route(
        "/api/shipping-methods", type="http", auth="none", methods=["GET"], csrf=False
    )
    @jwt_required
    def get_shipping_methods(self):
        """Endpoint to retrieve available shipping methods for the current user's latest sale order."""

        user = get_current_user()
        return self.handle(
            lambda: get_shipping_method_service().get_shipping_methods(user=user)
        )
