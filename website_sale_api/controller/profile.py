"""Controller for user profile related operations"""

# pylint:disable=too-few-public-methods,import-error,broad-exception-caught
import json
from odoo import http
from odoo.http import request
from odoo.exceptions import ValidationError
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
        try:
            user = get_current_user()
            data = get_profile_service().get_profile(user=user)

            return self._success(data=data.model_dump())
        except ValidationError as e:
            return self._error(message=str(e), code=400)
        except Exception as e:
            return self._error(message=str(e), code=500)

    @http.route(
        "/api/auth/profile", methods=["PUT"], type="http", auth="none", csrf=False
    )
    @jwt_required
    def update_profile(self):
        """Update current user profile"""
        try:
            user = get_current_user()
            body = json.loads(request.httprequest.data or "{}")
            data = get_profile_service().update_profile(user=user, data=body)

            return self._success(data=data.model_dump())
        except ValidationError as e:
            return self._error(message=str(e), code=400)
        except Exception as e:
            return self._error(message=str(e), code=500)

    @http.route(
        "/api/auth/profile/image", methods=["PUT"], type="http", auth="none", csrf=False
    )
    @jwt_required
    def upload_profile_image(self):
        """Upload profile image for the current user"""
        try:
            user = get_current_user()
            file = request.httprequest.files.get("image_url")

            data = get_profile_service().upload_profile_image(user=user, file=file)

            return self._success(data=data.model_dump())
        except ValidationError as e:
            return self._error(message=str(e), code=400)
        except Exception as e:
            return self._error(message=str(e), code=500)
