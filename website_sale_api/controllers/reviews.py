"""Controller for handling product reviews in the e-commerce API."""

# pylint: disable=import-error,too-few-public-methods
from odoo import http
from odoo.exceptions import ValidationError

from ..services.review_service import ReviewService
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
            return self._success(
                ReviewService().get_reviews(
                    kwargs=kwargs, product_template_id=product_template_id
                )
            )
        except ValidationError as e:
            return self._error(message=str(e), code=400)
