"""Authentication controller for handling user login,
registration, profile retrieval, and password management."""

# pylint:disable=too-few-public-methods,import-error
from odoo import http
from odoo.exceptions import AccessDenied, ValidationError
from odoo.http import request

from ..schemas.auth_schema import AuthResponse
from ..services.auth_service import AuthService
from ..services.token_service import JWTService
from .base import BaseAPI


class AuthController(BaseAPI):
    """Controller for authentication-related endpoints"""

    @http.route(
        "/api/auth/login", type="http", auth="public", methods=["POST"], csrf=False
    )
    def login(self):
        """Authenticate user and return JWT token"""
        user = AuthService().authenticate_user()

        if not user:
            return self._error(message="Login & Password Incorrect!", code=401)

        token = JWTService.generate_token(user=user)
        return self._success(AuthResponse(token=token))

    @http.route(
        "/api/auth/register", type="http", auth="public", methods=["POST"], csrf=False
    )
    def register(self):
        """Create a new user and return JWT token"""
        try:
            user = AuthService().create_user()

            token = JWTService.generate_token(user=user)

            return self._success(
                AuthResponse(
                    token=token,
                )
            )
        except ValidationError as e:
            return self._error(message=str(e), code=400)
        except Exception as e:
            return self._error(message=str(e), code=500)

    @http.route(
        "/api/auth/logout", type="http", auth="public", methods=["POST"], csrf=False
    )
    @JWTService.jwt_required
    def logout(self):
        """Logout endpoint"""
        return self._success(message="Logout successful")

    @http.route(
        "/api/auth/refresh", type="http", auth="public", methods=["POST"], csrf=False
    )
    @JWTService.jwt_required
    def refresh_token(self):
        """Refresh JWT token"""
        try:
            user = request.authenticated_user

            token = JWTService.generate_token(
                user={"uid": user.id, "login": user.login}
            )
            data = AuthResponse(token=token)
            return self._success(data)

        except ValidationError as e:
            return self._error(message=str(e), code=400)

    @http.route(
        "/api/auth/change-password",
        type="http",
        auth="public",
        methods=["POST"],
        csrf=False,
    )
    @JWTService.jwt_required
    def change_password(self):
        """Change user password"""
        try:
            AuthService().change_user_password()
            return self._success(message="Password changed successfully.")

        except AccessDenied as _:
            return self._error(
                message="The old password you provided is incorrect.", code=403
            )
        except ValidationError as e:
            return self._error(message=str(e), code=400)
        except Exception as e:
            return self._error(
                message=f"An unexpected error occurred. {str(e)}", code=500
            )
