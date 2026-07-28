"""Base API controller module providing common response handling functionality."""

# pylint:disable=too-few-public-methods,import-error
from dataclasses import asdict, is_dataclass

from odoo import http
from odoo.http import request


class BaseAPI(http.Controller):
    """Base controller with common functionality"""

    def _success(self, data=None, wrap_in_data=False, **kwargs):
        """
        Success response with automatic dataclass conversion.

        Args:
            data: The data to return
            wrap_in_data: If True, wraps data in 'data' key. If False, data is merged directly.
            **kwargs: Additional key-value pairs to add to response
        """
        response = {"status": "success"}

        if data is not None:
            # Convert dataclass to dict
            if is_dataclass(data):
                data = asdict(data)
            elif isinstance(data, (list, tuple)) and data and is_dataclass(data[0]):
                data = [asdict(item) for item in data]

            # Conditionally wrap in "data" key
            if wrap_in_data:
                response["data"] = data
            else:
                # Merge data directly into response
                if isinstance(data, dict):
                    response.update(data)
                else:
                    response["data"] = data

        # Add any additional kwargs to response
        response.update(kwargs)
        return request.make_json_response(response, status=200)

    def _error(self, message="Error", code=400):
        """Error response with message and status code"""
        return request.make_json_response(
            {"status": "fail", "message": message}, status=code
        )
