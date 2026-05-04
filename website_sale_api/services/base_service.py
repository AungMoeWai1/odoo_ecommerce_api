"""Base service for common functionalities across services."""

# pylint:disable=too-few-public-methods,import-error
from odoo.http import request


class BaseService:
    """Base service"""

    def __init__(self, env=None):
        self.env = env or request.env

    def _get_base_url(self):
        """Return current base url"""
        return request.httprequest.host_url.rstrip("/")
