"""Service layer for handling website-related business logic in the Odoo e-commerce API."""

# pylint: disable=too-few-public-methods,
# pylint: disable=import-error,line-too-long

from odoo.http import request
from ..schemas.website_schema import WebsiteData, WebsiteResponse


class WebsiteService:
    """Service class for handling website-related operations"""

    def get_websites(self):
        """Fetches the list of websites available in the Odoo instance"""
        websites = request.env["website"].sudo().search([])

        result = []
        for w in websites:
            result.append(
                WebsiteData(
                    id=w.id,
                    name=w.name,
                )
            )

        return WebsiteResponse(
            data=result
        )


def get_website_service():
    """Factory function to get an instance of the WebsiteService"""
    return WebsiteService()
