"""Controller for handling term and conditions API endpoints."""

# pylint: disable=too-few-public-methods,import-error

from odoo import http

from ..services.api_key_service import ApiKeyService
from ..services.term_condition_service import TermConditionService
from .base import BaseAPI


class ProductAPI(BaseAPI):
    """Controller for term and condition endpoints"""

    @http.route(
        "/api/term_and_conditions",
        type="http",
        auth="public",
        methods=["GET"],
        csrf=False,
    )
    @ApiKeyService.api_key_required()
    def get_term_condition(self):
        """Retrieve term and condition for the current website domain"""
        result = TermConditionService().get_term_string()

        return self._success(result, wrap_in_data=True)
