"""Authentication and user management service for the e-commerce API."""

# pylint:disable=import-error,broad-exception-caught
import json

from odoo.exceptions import ValidationError
from odoo.http import request


class AuthService:
    """Service for handling user authentication, registration, and profile management"""

    def authenticate_user(self):
        """Authenticate user and return user record"""
        try:
            data = json.loads(request.httprequest.data)
            auth = self._authenticate(data["login"], data["password"])
            return {"uid": auth["uid"], "login": data["login"]}
        except Exception:
            return False

    def create_user(self):
        """Create a new portal user and authenticate"""
        try:
            data = json.loads(request.httprequest.data)
            self._create_user(data)
            auth = self._authenticate(data["login"], data["password"])
            return {"uid": auth["uid"], "login": data["login"]}
        except Exception as e:
            return ValidationError(str(e))

    def _create_user(self, data):
        """Create a new user"""
        return (
            request.env["res.users"]
            .sudo()
            .signup(
                {
                    "name": data["name"],
                    "login": data["login"],
                    "password": data["password"],
                }
            )
        )

    def _authenticate(self, login, password):
        """Authenticate user"""
        return request.session.authenticate(
            request.env, {"login": login, "password": password, "type": "password"}
        )

    def change_user_password(self):
        """Change password after validating old password"""
        payload = json.loads(request.httprequest.data)

        # Check if passwords are identical
        if self._check_password_identity(payload):
            raise ValidationError(
                "The old password and new password must not be identical."
            )

        # Change password (raises exceptions on failure)
        user = request.authenticated_user
        user.sudo().with_env(request.env(user=user)).change_password(
            payload.get("old_password"), payload.get("new_password")
        )
        return True

    def _check_password_identity(self, payload):
        return payload.get("new_password") == payload.get("old_password")
