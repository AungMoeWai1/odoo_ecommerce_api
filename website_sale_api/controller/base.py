"""Base API controller module providing common response handling functionality."""

# pylint:disable=too-few-public-methods,import-error,broad-exception-caught,unused-variable
import logging
from odoo import http
from odoo.http import request
from odoo.exceptions import ValidationError

_logger = logging.getLogger(__name__)


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

    def handle(self, func):
        """Centralized exception handler for API endpoints"""
        try:
            result = func()

            if hasattr(result, "model_dump"):
                result = result.model_dump()

            return self._success(data=result)

        except ValidationError as e:
            return self._error(str(e), 400)

        except Exception as e:
            _logger.exception("API error: %s", e)
            return self._error("Internal server error", 500)
