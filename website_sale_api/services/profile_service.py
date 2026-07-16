"""Profile Service for handling user profile operations in Odoo eCommerce API.1"""

# pylint: disable=import-error
from dataclasses import fields
from typing import Any, Dict, Tuple

from ..schemas.auth_schema import UpdateUserData
from ..schemas.profile_schema import ProfileResponse, UpdateProfile
from .base_service import BaseService


class ProfileService(BaseService):
    """Service class for managing user profiles"""

    def __init__(self, env=None):
        super().__init__(env)
        self.model_name = "res.users"

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
            image_url=self._get_image_url(self.model_name, user.id),
        )

    def update_profile_value(self, user, data):
        """Update user profile with the provided data"""

        user_fields, partner_fields = self._separate_fields(data)
        if user_fields:
            self._write(user, user_fields)
        if partner_fields:
            self._write(user.partner_id, partner_fields)

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
        if data.get("name"):
            user_fields["name"] = partner_fields["name"] = data["name"]

        if data.get("email"):
            user_fields["login"] = partner_fields["email"] = data["email"]

        return user_fields, partner_fields

    def upload_profile_image(self, user, file, max_size_mb=5):
        """
        Upload profile image for the user.
        """

        image_base64 = self._upload_image(
            record=user.partner_id,  # Pass the record object
            file=file,
            max_size_mb=max_size_mb,
            field="image_1920",
        )

        # Also update user with same image (optional if user has image field)
        if hasattr(user, "image_1920"):
            self._write(user, {"image_1920": image_base64})

        return {"id": user.id, "message": "Profile Image updated successfully"}
