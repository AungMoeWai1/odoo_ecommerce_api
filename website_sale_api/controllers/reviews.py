"""Controller for handling product reviews in the e-commerce API."""

# pylint: disable=import-error
from odoo import http
from odoo.exceptions import ValidationError

from ..services.review_service import get_review_service
from .base import BaseAPI


class ReviewController(BaseAPI):
    """API controller for product reviews"""

    @http.route(
        "/api/product/<int:product_template_id>/reviews",
        type="http",
        auth="public",
        methods=["GET"],
        csrf=False,
    )
    def get_reviews(self, product_template_id, **kwargs):
        """Fetch reviews for a given product template"""

        try:
            result = get_review_service().get_reviews(
                params=kwargs, product_template_id=product_template_id
            )
            return self._success(**result.model_dump())
        except ValidationError as e:
            return self._error(str(e))
