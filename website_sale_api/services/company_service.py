"""Profile Service for handling company in Odoo eCommerce API.1"""

# pylint: disable=import-error

from ..schemas.company_schema import CompanyResponse, SocialSchema
from .base_service import BaseService


class CompanyService(BaseService):
    """Service class for managing Company"""

    def __init__(self, env=None):
        super().__init__(env)
        self.model_name = "res.company"
        self.website = self._get_current_website()

    def get_company_information(self):
        """Get company information"""
        self.default_domain = ([("id", "=", self.website.company_id.id)])
        company = self.search()

        address = ", ".join(filter(None, [
            company.street,
            company.township_id.name,
            company.city,
            company.country_id.name,
        ]))

        return CompanyResponse(
            id=company.id,
            name=company.name,
            logo=self._get_image_url(self.model_name, company.id, size="logo"),
            phone=company.phone,
            email=company.email,
            website=company.website,
            address=address,
            social=SocialSchema(social_twitter=company.social_twitter,
                                social_facebook=company.social_facebook,
                                social_github=company.social_github,
                                social_linkedin=company.social_linkedin,
                                social_youtube=company.social_youtube,
                                social_tiktok=company.social_tiktok,
                                social_discourse=company.social_discord)
        )
