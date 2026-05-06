"""Profile Service for handling user profile operations in Odoo eCommerce API.1"""

# pylint:disable=too-few-public-methods,import-error

import base64
from odoo.exceptions import ValidationError
from ..schemas.profile_schema import ProfileResponse


class ProfileService:
    """Service class for managing user profiles"""

    def get_profile(self, user):
        """Get user profile information"""
        partner = user.partner_id

        if not partner or not partner.exists():
            raise ValidationError("Partner not found")

        data = ProfileResponse(
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
        return data

    def update_profile(self, user, data):
        """Update user profile with the provided data"""

        partner = user.partner_id

        if not partner or not partner.exists():
            raise ValidationError("Partner not found")

        partner_vals = {}

        for field in ["name", "email", "phone", "street", "city"]:
            if field in data:
                partner_vals[field] = data[field]

        if partner_vals:
            user.sudo().write(partner_vals)

        return self.get_profile(user)

    def upload_profile_image(self, user, file, max_size_mb=5):
        """Upload profile image for the user"""

        partner = user.partner_id

        if not partner or not partner.exists():
            raise ValidationError("Partner not found")

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

        return self.get_profile(user)


def get_profile_service():
    """Factory method to get ProfileService instance"""
    return ProfileService()
