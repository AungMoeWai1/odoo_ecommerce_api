"""Authentication and user management service for the e-commerce API."""

# pylint:disable=import-error,broad-exception-caught
import json

from odoo.exceptions import ValidationError
from odoo.http import request


class AuthService:
    """Service for handling user authentication, registration, and profile management"""

    def authenticate_user(self):
        """Authenticate user and return user record"""
        params = json.loads(request.httprequest.data)
        login = params.get("login")
        password = params.get("password")

        if not login or not password:
            raise ValidationError("login and password are required")

        try:
            credential = {"login": login, "password": password, "type": "password"}

            auth_info = request.session.authenticate(request.env, credential)
            uid = auth_info.get("uid")

            if uid:
                user = request.env["res.users"].sudo().browse(uid)
            else:
                raise ValidationError("Invalid login or password")

        except Exception as e:
            raise ValidationError("login and password are incorrect") from e

        return user

    def create_user(self):
        """Create a new portal user"""
        params = json.loads(request.httprequest.data)
        name = params.get("name")
        login = params.get("login")
        email = params.get("email")
        password = params.get("password")

        if not all([name, login, email, password]):
            raise ValidationError("Missing required fields")
        res_users = request.env["res.users"].sudo()
        self._check_existing_user(res_users, login, email)
        try:
            # Create portal user using signup
            res_users.signup(
                {
                    "name": name,
                    "login": login,
                    "email": email,
                    "password": password,
                }
            )
            return res_users.search([("login", "=", login)], limit=1)

        except Exception as e:
            return ValidationError(e)

    def _check_existing_user(self, users, login, email):
        """Check existing user"""

        existing = users.search(
            ["|", ("login", "=", login), ("email", "=", email)], limit=1
        )

        if existing:
            raise ValidationError("User already exists")

    def change_user_password(self, user, old_password, new_password):
        """Change password after validating old password"""

        if not old_password or not new_password:
            raise ValidationError("Old password and new password are required")

        try:
            # verify old password
            request.session.authenticate(
                request.env,
                {"login": user.login, "password": old_password, "type": "password"},
            )

            # update new password
            user.sudo().write({"password": new_password})

            return True

        except Exception:
            return False

    # def validate_user_token(self, token):
    #     """Validate refresh token and get user"""
    #     # Import here to avoid circular imports
    #     from ..services.token_service import JWTService
    #
    #     try:
    #         uid, payload = JWTService.get_user_from_token(token)
    #         user = request.env['res.users'].sudo().browse(uid)
    #
    #         if user.exists():
    #             return user, None
    #         return None, "User not found"
    #
    #     except Exception as e:
    #         return None, "Invalid or expired refresh token"


def get_auth_service():
    """Factory method to get AuthService instance"""
    return AuthService()
