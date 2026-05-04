"""JWT Token Service - Handle all token operations and
authentication middleware."""

# pylint:disable=import-error,raise-missing-from,broad-exception-caught
from datetime import datetime, timedelta
from functools import wraps

import jwt
from odoo.exceptions import AccessDenied
from odoo.http import request
from odoo.tools import config


def _get_secret():
    """Return secret key for JWT encoding/decoding"""
    return config.get(
        "jwt_secret_key",
        "9f3a8c2e7b6a1d4f9e3c8a2b7c6d5e4f9a8b7c6d5e4f3a2b1c0d9e8f7a6b5c4",
    )


def _get_algorithm():
    """Return algorithm for JWT encoding/decoding"""
    return config.get("jwt_algorithm", "HS256")


def _get_expiry_minutes():
    """Return expiry time for JWT tokens"""
    return int(config.get("jwt_ expiry_minutes", 60))


# ============ TOKEN OPERATIONS ============
class JWTService:
    """JWT Token Service - Handle all token operations"""

    @staticmethod
    def generate_token(user):
        """Generate JWT token for authenticated user"""
        payload = {
            "uid": user.id,
            "email": user.email,
            "exp": datetime.utcnow() + timedelta(minutes=_get_expiry_minutes()),
            "iat": datetime.utcnow(),
        }

        return jwt.encode(payload, _get_secret(), algorithm=_get_algorithm())

    @staticmethod
    def verify_token(token):
        """Verify and decode JWT token"""
        try:
            return jwt.decode(token, _get_secret(), algorithms=[_get_algorithm()])
        except jwt.ExpiredSignatureError:
            raise AccessDenied("Token has expired")
        except jwt.InvalidTokenError:
            raise AccessDenied("Invalid token")

    @staticmethod
    def get_user_from_token(token):
        """Extract user ID and payload from token"""
        payload = JWTService.verify_token(token)
        uid = payload.get("uid")
        if not uid:
            raise AccessDenied("Invalid token payload: missing user ID")
        return uid, payload


def jwt_required(func):
    """Decorator to protect routes with JWT authentication"""

    @wraps(func)
    def wrapper(*args, **kwargs):
        """Decorator to protect routes with JWT authentication"""
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
            uid, payload = JWTService.get_user_from_token(token)

            user = request.env["res.users"].sudo().browse(uid)
            if not user.exists():
                return request.make_json_response(
                    {"status": "fail", "message": "User no longer exists"}, status=401
                )

            # Attach user
            request.authenticated_user = user
            request.token_payload = payload

            request.update_env(user=uid)

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


# ============ HELPER FUNCTIONS ============
def get_current_user():
    """Get currently authenticated user"""
    return getattr(request, "authenticated_user", None)
