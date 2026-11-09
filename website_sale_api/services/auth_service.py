"""Authentication and user management service for the e-commerce API."""

# pylint:disable=import-error,broad-exception-caught,protected-access
import json
from datetime import datetime

from odoo.exceptions import ValidationError
from odoo.http import request

from .base_service import BaseService


class AuthService(BaseService):
    """Service for handling user authentication, registration, and profile management"""

    def __init__(self):
        super().__init__()
        self.model_name = "res.users"

    def authenticate_user(self):
        """Authenticate user and return user record"""
        try:
            data = json.loads(request.httprequest.data)
            login = data.get("login")
            password = data.get("password")

            if not login or not password:
                return "Login and password are required"
            # Check whether the user exists
            user = self._get_user_by_login(login)

            if not user:
                return "User does not exist"
            auth = self._authenticate(data["login"], data["password"])
            self.update_mobile_token(data, auth["uid"])
            return {"uid": auth["uid"], "login": data["login"]}
        except Exception as ex:
            return ex

    def create_user(self):
        """Create a new portal user and authenticate"""

        data = json.loads(request.httprequest.data)
        self._create_user(data)
        auth = self._authenticate(data["login"], data["password"])
        self.update_mobile_token(data, auth["uid"])
        return {"uid": auth["uid"], "login": data["login"]}

    def update_mobile_token(self, data, uid):
        """Update mobile token"""
        if data.get("mobile_device_token"):
            user = self.get_record_by_id(uid)
            user.sudo().write(
                {
                    "mobile_device_token": data["mobile_device_token"],
                    "last_login": datetime.now(),
                }
            )

    def request_code(self):
        """Request code"""
        data = json.loads(request.httprequest.data)
        user = self._validate_user(data.get("login"))
        user.create_reset_code()
        return {"message": f"OTP code is sent to this email {data['login']}"}

    def check_otp_password(self):
        """Request code and check otp password"""
        data = json.loads(request.httprequest.data)
        user = self._validate_user(data.get("login"))
        valid, message = user.is_reset_code_valid(data.get("code"))
        if valid:
            return {"message": message}
        raise ValidationError(message)

    def reset_user_password(self):
        """Reset user password"""
        data = json.loads(request.httprequest.data)
        user = self._validate_user(data.get("login"))
        user._change_password(data["password"])
        return {"message": "Password changed successfully"}

    def _validate_user(self, login):
        """Validate user exists and return user"""
        user = self._get_user_by_login(login)
        if not user:
            raise ValidationError("User does not exist")
        return user

    def _get_user_by_login(self, login):
        """Helper method to get user by login/email"""
        self.default_domain = [("login", "=", login)]
        user = self.search()
        return user

    def _validate_user_exists(self, login):
        """Helper method to validate user exists"""
        user = self._get_user_by_login(login)
        if not user:
            return None, {"message": "User does not exist"}
        return user, None

    def _create_user(self, data):
        """Create a new user"""
        return self._get_model().signup(
            {
                "name": data["name"],
                "login": data["login"],
                "password": data["password"],
            }
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
