"""Profile Service for handling user profile operations in Odoo eCommerce API.1"""

# pylint: disable=import-error

from odoo.exceptions import ValidationError

from ..schemas.profile_schema import ProfileResponse
from .base_service import BaseService


class ProfileService(BaseService):
    """Service class for managing user profiles"""

    def __init__(self, env=None):
        super().__init__(env)
        self.model_name = "res.users"
        self.fields = ["image_512"]

    def get_profile(self, user):
        """Get user profile information"""
        p = user.partner_id

        def get(obj, attr):
            return getattr(getattr(obj, attr, None), "id", None)

        return ProfileResponse(
            id=user.id,
            login=user.login,
            name=user.name,
            email=p.email,
            phone=p.phone or None,
            street=p.street or None,
            city=p.city or None,
            country_id=get(p, "country_id"),
            state_id=get(p, "state_id"),
            township_id=get(p, "township_id"),
            partner_id=p.id,
            company_id=p.company_id.name or None,
            company_name=p.company_id.name or None,
            image_url=self._get_image_url(self.model_name, user.id, size="image_1024"),
        )

    def update_partner_country(self, uid):
        """Update user profile information"""
        try:
            user = self.env["res.users"].browse(uid)

            country = self.env["res.country"].search([("code", "=", "MM")], limit=1)

            if country:
                user.sudo().write({"country_id": country.id})
        except Exception as e:
            raise ValidationError(f"Modify user country fail: {str(e)}") from e

    def upload_profile_image(self, user, file, max_size_mb=5):
        """
        Upload profile image for the user.
        """

        image_base64 = self._upload_image(
            record=user.partner_id,
            file=file,
            max_size_mb=max_size_mb,
            field="image_1920",
        )

        # Also update user with same image (optional if user has image field)
        if hasattr(user, "image_1920"):
            self._write(user, {"image_1920": image_base64})

        return {"id": user.id, "message": "Profile Image updated successfully"}
