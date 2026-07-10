"""Profile Service for handling user profile operations in Odoo eCommerce API.1"""

# pylint:disable=too-few-public-methods,import-error

import base64
from dataclasses import fields
from typing import Any, Dict, Tuple

from odoo.exceptions import ValidationError

from ..schemas.auth_schema import UpdateUserData
from ..schemas.profile_schema import ProfileResponse, UpdateProfile


class ProfileService:
    """Service class for managing user profiles"""

    def get_profile(self, user):
        """Get user profile information"""
        partner = user.partner_id

        return ProfileResponse(
            id=user.id,
            login=user.login,
            name=user.name,
            email=user.email,
            phone=user.phone,
            street=partner.street,
            city=partner.city,
            company_id=partner.company_id.id,
            company_name=partner.company_id.name,
            image_url=f"/web/image/res.users/{user.id}/image_128",
        )

    def update_profile(self, user, data):
        """Update user profile with the provided data"""

        user_fields, partner_fields = self._separate_fields(data)
        if user_fields:
            user.write(user_fields)
        if partner_fields:
            user.partner_id.write(partner_fields)

        return {
            "id": user.id,
            "message": "User profile updated successfully",
        }

    def _separate_fields(
        self, data: Dict[str, Any]
    ) -> Tuple[Dict[str, Any], Dict[str, Any]]:
        """Separate fields into user and partner fields using dataclass definitions."""
        user_fields = {
            k: v
            for k, v in data.items()
            if k in {f.name for f in fields(UpdateUserData)} and v
        }

        partner_fields = {
            k: v
            for k, v in data.items()
            if k in {f.name for f in fields(UpdateProfile)} and v
        }

        if data.get("email"):
            user_fields["login"] = partner_fields["email"] = data["email"]

        return user_fields, partner_fields

    def upload_profile_image(self, user, file, max_size_mb=5):
        """Upload profile image for the user"""

        partner = user.partner_id
        if not file:
            raise ValidationError("No image uploaded")

        content_type = file.mimetype
        if not content_type or not content_type.startswith("image/"):
            raise ValidationError("Invalid image file")

        allowed_types = ["image/jpeg", "image/png", "image/gif", "image/webp"]
        if content_type not in allowed_types:
            raise ValidationError("Only JPEG, PNG, GIF, WEBP images are allowed")

        file_data = file.read()
        if len(file_data) > max_size_mb * 1024 * 1024:
            raise ValidationError(f"Image must be smaller than {max_size_mb}MB")

        image_base64 = base64.b64encode(file_data)

        partner.sudo().write({"image_1920": image_base64})
        user.sudo().write({"image_1920": image_base64})

        return {
            "id": user.id,
            "message": "Profile Image updated successfully",
        }
