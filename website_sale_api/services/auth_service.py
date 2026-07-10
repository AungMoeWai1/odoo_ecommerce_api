"""Authentication and user management service for the e-commerce API."""

import json

from odoo.exceptions import AccessDenied, ValidationError
from odoo.http import request


class AuthService:
    """Service for handling user authentication, registration, and profile management"""

    def authenticate_user(self):
        """Authenticate user and return user record"""
        try:
            credential = json.loads(request.httprequest.data)
            credential["type"] = "password"

            auth_info = request.session.authenticate(request.env, credential)
            return {"uid": auth_info["uid"], "login": credential["login"]}

        except (json.JSONDecodeError, KeyError, Exception):
            return False

    def create_user(self):
        """Create a new portal user"""
        params = json.loads(request.httprequest.data)

        try:
            # Create portal user using signup
            request.env["res.users"].sudo().signup(
                {
                    "name": params["name"],
                    "login": params["login"],
                    "password": params["password"],
                }
            )
            user = request.env["res.users"].search(
                [("login", "=", params["login"])], limit=1
            )
            return {"uid": user.id, "login": user.login}

        except Exception as e:
            return ValidationError(e)

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
        user.sudo().change_password(
            payload.get("old_password"), payload.get("new_password")
        )
        return True

    def _check_password_identity(self, payload):
        return payload.get("new_password") == payload.get("old_password")
