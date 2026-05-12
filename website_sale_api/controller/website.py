"""API controller for website-related requests."""

# pylint: disable=import-error,

from odoo import http
from odoo.exceptions import ValidationError
from .base import BaseAPI
from ..services.website_service import get_website_service


class WebsiteAPI(BaseAPI):
    """API controller for handling website-related requests"""

    @http.route("/api/website", type="http", auth="public", methods=["GET"], csrf=False)
    def get_websites(self):
        """Endpoint to fetch the list of websites available in the Odoo instance"""
        try:
            result = get_website_service().get_websites()
            return self._success(**result.model_dump())

        except ValidationError as e:
            return self._error(message=str(e), code=400)
