"""Controller for company information"""

# pylint:disable=too-few-public-methods,import-error

from odoo import http
from odoo.http import request

from ..services.api_key_service import ApiKeyService
from ..services.company_service import CompanyService
from ..services.token_service import JWTService
from .base import BaseAPI


class CompanyController(BaseAPI):
    """Controller for handling company information"""

    @http.route(
        "/api/company/info", type="http", auth="public", methods=["GET"], csrf=False
    )
    @ApiKeyService.api_key_required()
    @JWTService.jwt_required()
    def get_company_info(self):
        """Get current company informations"""

        return self._success(
            data=CompanyService().get_company_information(), wrap_in_data=True
        )