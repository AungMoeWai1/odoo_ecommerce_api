"""Base API controller module providing common response handling functionality."""

# pylint:disable=too-few-public-methods,import-error
from odoo import http
from odoo.http import request


class BaseAPI(http.Controller):
    """Base controller with common functionality"""

    def _success(self, **data):
        """Success response with optional data"""
        return request.make_json_response({"status": "success", **data}, status=200)

    def _error(self, message="Error", code=400):
        """Error response with message and status code"""
        return request.make_json_response(
            {"status": "fail", "message": message}, status=code
        )
