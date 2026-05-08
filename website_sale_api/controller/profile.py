"""Controller for user profile related operations"""

# pylint:disable=too-few-public-methods,import-error,broad-exception-caught
import json
from odoo import http
from odoo.http import request
from .base import BaseAPI
from ..services.profile_service import get_profile_service
from ..services.token_service import get_current_user, jwt_required


class ProfileController(BaseAPI):
    """Controller for handling user profile operations"""

    @http.route(
        "/api/auth/profile", type="http", auth="public", methods=["GET"], csrf=False
    )
    @jwt_required
    def get_profile(self):
        """Get current user profile"""

        user = get_current_user()
        return self.handle(lambda: get_profile_service().get_profile(user=user))

    @http.route(
        "/api/auth/profile", methods=["PUT"], type="http", auth="none", csrf=False
    )
    @jwt_required
    def update_profile(self):
        """Update current user profile"""

        user = get_current_user()
        data = json.loads(request.httprequest.data or "{}")
        return self.handle(
            lambda: get_profile_service().update_profile(user=user, data=data)
        )

    @http.route(
        "/api/auth/profile/image", methods=["PUT"], type="http", auth="none", csrf=False
    )
    @jwt_required
    def upload_profile_image(self):
        """Upload profile image for the current user"""

        user = get_current_user()
        file = request.httprequest.files.get("image_url")
        return self.handle(
            lambda: get_profile_service().upload_profile_image(user=user, file=file)
        )
