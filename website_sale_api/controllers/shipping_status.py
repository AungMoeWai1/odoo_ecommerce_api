"""Controller for handling shipping status in the e-commerce API."""

# pylint: disable=import-error,too-few-public-methods
from odoo import http
from odoo.exceptions import ValidationError

from ..services.api_key_service import ApiKeyService
from ..services.token_service import JWTService
from ..services.shipping_status_service import ShippingStatusService
from .base import BaseAPI


class DeliveryStatusController(BaseAPI):
    """API controller for shipping status."""

    @http.route(
        "/api/shipping_status",
        type="http",
        auth="public",
        methods=["GET"],
        csrf=False,
    )
    @ApiKeyService.api_key_required()
    @JWTService.jwt_required()
    def get_shipping_status(self):
        """Fetch all shipping statuses."""

        try:
            return self._success(ShippingStatusService().fetch_all_shipping_status())

        except ValidationError as e:
            return self._error(
                message=str(e),
                code=400,
            )
