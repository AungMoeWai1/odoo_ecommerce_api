"""Authentication controller for handling user login,
registration, profile retrieval, and password management."""

# pylint:disable=too-few-public-methods,import-error,broad-exception-caught,protected-access
import json
from odoo import http
from odoo.exceptions import AccessDenied, ValidationError
from odoo.http import request

from ..schemas.auth_schema import AuthResponse
from ..services.api_key_service import ApiKeyService
from ..services.auth_service import AuthService
from ..services.profile_service import ProfileService
from ..services.token_service import JWTService
from .base import BaseAPI


class AuthController(BaseAPI):
    """Controller for authentication-related endpoints"""

    @http.route(
        "/api/auth/login", type="http", auth="public", methods=["POST"], csrf=False
    )
    @ApiKeyService.api_key_required()
    def login(self):
        """Authenticate user and return JWT token"""
        user = AuthService().authenticate_user()

        if not user:
            return self._error(message="Login & Password Incorrect!", code=401)

        token = JWTService.generate_token(user=user)
        return self._success(AuthResponse(token=token))

    @http.route(
        "/api/auth/device_token",
        type="http",
        auth="public",
        methods=["POST"],
        csrf=False,
    )
    @ApiKeyService.api_key_required()
    @JWTService.jwt_required()
    def update_device_token(self):
        """Authenticate user and return JWT token"""
        user = request.authenticated_user
        data = json.loads(request.httprequest.data)
        try:
            AuthService().update_mobile_token(data, user.id)
            return self._success(message="Mobile token updated successfully.")
        except Exception as ex:
            return self._error(message=str(ex), code=400)

    @http.route(
        "/api/auth/register", type="http", auth="public", methods=["POST"], csrf=False
    )
    @ApiKeyService.api_key_required()
    def register(self):
        """Create a new user and return JWT token"""

        user = AuthService().create_user()

        ProfileService().update_partner_country(user["uid"])

        token = JWTService.generate_token(user=user)

        return self._success(
            AuthResponse(
                token=token,
            )
        )

    @http.route(
        "/api/auth/request_reset_password",
        type="http",
        auth="public",
        methods=["POST"],
        csrf=False,
    )
    @ApiKeyService.api_key_required()
    def request_reset_code(self):
        """Create a new user and return JWT token"""
        try:
            code = AuthService().request_code()

            return self._success(code)
        except ValidationError as e:
            return self._error(message=str(e), code=400)
        except Exception as e:
            return self._error(message=str(e), code=500)

    @http.route(
        "/api/auth/reset_password",
        type="http",
        auth="public",
        methods=["POST"],
        csrf=False,
    )
    @ApiKeyService.api_key_required()
    def reset_password(self):
        """Create a new user and return JWT token"""
        try:
            msg = AuthService().reset_user_password()

            return self._success(msg)
        except ValidationError as e:
            return self._error(message=str(e), code=400)
        except Exception as e:
            return self._error(message=str(e), code=500)

    @http.route(
        "/api/auth/otp_verity", type="http", auth="public", methods=["POST"], csrf=False
    )
    @ApiKeyService.api_key_required()
    def verify_otp(self):
        """Verify OTP code to change user password"""
        try:
            msg = AuthService().check_otp_password()

            return self._success(msg)
        except ValidationError as e:
            return self._error(message=str(e), code=400)
        except Exception as e:
            return self._error(message=str(e), code=500)

    @http.route(
        "/api/auth/logout", type="http", auth="public", methods=["POST"], csrf=False
    )
    @ApiKeyService.api_key_required()
    @JWTService.jwt_required()
    def logout(self):
        """Logout endpoint"""
        return self._success(message="Logout successful")

    @http.route(
        "/api/auth/refresh", type="http", auth="public", methods=["POST"], csrf=False
    )
    @ApiKeyService.api_key_required()
    @JWTService.jwt_required(skip_expiry=True)
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
        "/api/auth/change_password",
        type="http",
        auth="public",
        methods=["POST"],
        csrf=False,
    )
    @ApiKeyService.api_key_required()
    @JWTService.jwt_required()
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
