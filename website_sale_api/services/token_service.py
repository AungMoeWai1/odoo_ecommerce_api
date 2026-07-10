"""JWT Token Service - Handle all token operations and authentication middleware."""

# pylint:disable=import-error,raise-missing-from,broad-exception-caught
from datetime import datetime, timedelta
from functools import wraps

import jwt
from odoo.exceptions import AccessDenied
from odoo.http import request

JWT_EXPIRY_MINUTES = 60
JWT_ALGORITHM = "HS256"
JWT_SECRET_KEY = "9f3a8c2e7b6a1d4f9e3c8a2b7c6d5e4f9a8b7c6d5e4f3a2b1c0d9e8f7a6b5c4"


# ============ TOKEN OPERATIONS ============
class JWTService:
    """JWT Token Service - Handle all token operations"""

    def _verify_token(self, token):
        """
        Verify and decode JWT token (INSTANCE METHOD)
        - Only called internally within this class
        - Uses self for potential future extensions
        """
        try:
            return jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
        except jwt.ExpiredSignatureError:
            raise AccessDenied("Token has expired")
        except jwt.InvalidTokenError:
            raise AccessDenied("Invalid token")

    def get_user_from_token(self, token):
        """
        Extract user ID from token (INSTANCE METHOD)
        - Called by jwt_required decorator
        - Can be called by other classes if needed
        - Uses self._verify_token()
        """
        payload = self._verify_token(token)
        uid = payload.get("uid")
        if not uid:
            raise AccessDenied("Invalid token payload: missing user ID")
        return uid

    # ============ CLASS METHODS (Need class access) ============

    @classmethod
    def generate_token(cls, user):
        """
        Generate JWT token (CLASS METHOD)
        - Called by controllers to create new tokens
        - Uses class constants and class methods
        """
        payload = {
            "uid": user["uid"],
            "login": user["login"],
            "website_id": cls._get_website_id(),
            "exp": datetime.utcnow() + timedelta(minutes=JWT_EXPIRY_MINUTES),
            "iat": datetime.utcnow(),
        }
        return jwt.encode(payload, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)

    @classmethod
    def _get_website_id(cls):
        """
        Get current website ID (INTERNAL CLASS METHOD)
        - Only called internally by generate_token
        - Not intended for external use
        """
        website = cls._get_current_website()
        return website.id if website else False

    @classmethod
    def _get_current_website(cls):
        """
        Fetch current website (INTERNAL CLASS METHOD)
        - Only called internally by _get_website_id
        - Not intended for external use
        """
        domain = request.httprequest.host
        return (
            request.env["website"]
            .sudo()
            .search(["|", ("domain", "=", f"http://{domain}"), (1, "=", 1)], limit=1)
        )

    # ============ STATIC METHODS (Don't need class or instance) ============

    @staticmethod
    def jwt_required(func):
        """
        JWT Authentication Decorator (STATIC METHOD)
        - Used as decorator on routes
        - Doesn't need class or instance state
        - Creates instance internally when needed
        """

        @wraps(func)
        def wrapper(*args, **kwargs):
            auth_header = request.httprequest.headers.get("Authorization", "")

            if not auth_header or not auth_header.startswith("Bearer "):
                return request.make_json_response(
                    {
                        "status": "fail",
                        "message": "Missing or invalid Authorization header",
                    },
                    status=401,
                )

            token = auth_header.split(" ")[1]

            try:
                # Create instance to use get_user_from_token
                uid = JWTService().get_user_from_token(token)

                user = request.env["res.users"].sudo().browse(uid)
                if not user.exists():
                    return request.make_json_response(
                        {"status": "fail", "message": "User no longer exists"},
                        status=401,
                    )

                # Attach user and payload
                request.authenticated_user = user

            except AccessDenied as e:
                return request.make_json_response(
                    {"status": "fail", "message": str(e)}, status=401
                )
            except Exception as e:
                return request.make_json_response(
                    {"status": "fail", "message": f"Authentication failed: {str(e)}"},
                    status=401,
                )

            return func(*args, **kwargs)

        return wrapper
