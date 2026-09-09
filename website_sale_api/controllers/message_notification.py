"""Controller for managing shipping addresses in the Odoo e-commerce API."""

# pylint: disable=too-few-public-methods, import-error,too-many-arguments,too-many-positional-arguments,redefined-builtin,raise-missing-from,consider-using-in,broad-exception-caught
import json

from odoo import http
from odoo.http import request

from ..services.api_key_service import ApiKeyService
from ..services.noti_message_service import NotiMessageService
from ..services.token_service import JWTService
from .base import BaseAPI


class MessageNotiAPI(BaseAPI):
    """Controller class for handling Notification Message log related API endpoints"""

    @http.route(
        "/api/noti_messages",
        type="http",
        auth="public",
        methods=["GET"],
        csrf=False,
    )
    @ApiKeyService.api_key_required()
    @JWTService.jwt_required()
    def get_state(self, **kwargs):
        """Get the state of the authenticated user"""
        user = request.authenticated_user
        return self._success(NotiMessageService().get_noti_list(user, kwargs))

    @http.route(
        "/api/noti_messages/bulk",
        type="http",
        auth="public",
        methods=["PUT"],
        csrf=False,
    )
    @ApiKeyService.api_key_required()
    @JWTService.jwt_required()
    def update_noti_status(self):
        """Bulk update notification status"""
        data = json.loads(request.httprequest.data or "{}")
        result = NotiMessageService().bulk_mark_as_read(ids=data["ids"])
        if result:
            return self._success(
                ids=data["ids"],
                message="Successfully marked as read",
            )
        return self._error(
            message="Failed to update notification status",
        )
