"""Authentication controller for handling user login,
registration, profile retrieval, and password management."""

# pylint:disable=too-few-public-methods,import-error,broad-exception-caught

import json

from odoo import http
from odoo.exceptions import ValidationError
from odoo.http import request

from ..schemas.auth_schema import AuthResponse, UserData
from ..services.auth_service import get_auth_service
from ..services.token_service import JWTService, get_current_user, jwt_required
from .base import BaseAPI


class AuthController(BaseAPI):
    """Controller for authentication-related endpoints"""

    @http.route(
        "/api/auth/login", type="http", auth="public", methods=["POST"], csrf=False
    )
    def login(self):
        """Authenticate user and return JWT token"""
        try:
            user = get_auth_service().authenticate_user()

            token = JWTService.generate_token(user=user)

            data = AuthResponse(
                token=token,
                user=UserData(
                    id=user.id, name=user.name, email=user.email, login=user.login
                ),
            )
            return self._success(**data.model_dump())

        except ValidationError as e:
            return self._error(message=str(e), code=400)
        except Exception as e:
            return self._error(message=e, code=500)

    @http.route(
        "/api/auth/register", type="http", auth="public", methods=["POST"], csrf=False
    )
    def register(self):
        """Create a new user and return JWT token"""
        try:
            user = get_auth_service().create_user()

            token = JWTService.generate_token(user=user)

            data = AuthResponse(
                token=token,
                user=UserData(
                    id=user.id, name=user.name, email=user.email, login=user.login
                ),
            )
            return self._success(**data.model_dump())
        except ValidationError as e:
            return self._error(message=str(e), code=400)
        except Exception as e:
            return self._error(message=str(e), code=500)

    @http.route(
        "/api/auth/logout", type="http", auth="public", methods=["POST"], csrf=False
    )
    @jwt_required
    def logout(self):
        """Logout endpoint"""
        return self._success(message="Logout successful")

    @http.route(
        "/api/auth/refresh", type="http", auth="public", methods=["POST"], csrf=False
    )
    @jwt_required
    def refresh_token(self):
        """Refresh JWT token"""
        try:
            user = get_current_user()

            token = JWTService.generate_token(user=user)
            data = AuthResponse(
                token=token,
                user=UserData(
                    id=user.id, name=user.name, email=user.email, login=user.login
                ),
            )
            return self._success(**data.model_dump())

        except ValidationError as e:
            return self._error(message=str(e), code=400)

    @http.route(
        "/api/auth/change-password",
        type="http",
        auth="public",
        methods=["POST"],
        csrf=False,
    )
    @jwt_required
    def change_password(self):
        """Change user password after validating old password"""
        user = get_current_user()

        try:
            params = json.loads(request.httprequest.data or "{}")
            old_password = params.get("old_password")
            new_password = params.get("new_password")

            success = get_auth_service().change_user_password(
                user=user, old_password=old_password, new_password=new_password
            )

            if success:
                return self._success(message="Password updated successfully")

            return self._error(message="Old password is incorrect", code=400)

        except ValidationError as e:
            return self._error(message=str(e), code=400)

        except Exception:
            return self._error(message="Something went wrong", code=500)
