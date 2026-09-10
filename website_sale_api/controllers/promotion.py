"""Controller for handling promotion popup in the e-commerce API."""

# pylint: disable=import-error,too-few-public-methods
from odoo import http
from odoo.exceptions import ValidationError

from ..services.api_key_service import ApiKeyService
from ..services.promotion_service import PromotionService
from .base import BaseAPI


class Promotion(BaseAPI):
    """API controller for Promotion Popup."""

    @http.route(
        "/api/promotions",
        type="http",
        auth="public",
        methods=["GET"],
        csrf=False,
    )
    @ApiKeyService.api_key_required()
    def get_promotion_popup(self):
        """Fetch all promotion popup."""

        try:
            return self._success(PromotionService().fetch_all_promotions())

        except ValidationError as e:
            return self._error(
                message=str(e),
                code=400,
            )
