"""Controller for handling product reviews in the e-commerce API."""

# pylint: disable=import-error,too-few-public-methods
import json
from odoo import http
from odoo.http import request
from odoo.exceptions import ValidationError
from ..services.token_service import JWTService
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

    @http.route(
        "/api/product/<int:product_template_id>/reviews",
        type="http",
        auth="user",
        methods=["POST"],
        csrf=False,
    )
    @JWTService.jwt_required()
    def post_rating_comment(self, product_template_id):
        """Fetch reviews for a given product template"""

        try:
            user = request.authenticated_user
            data = json.loads(request.httprequest.data or "{}")
            return self._success(
                ReviewService().post_rating_comment(
                    kwargs=data, product_template_id=product_template_id, user=user
                )
            )
        except ValidationError as e:
            return self._error(message=str(e), code=400)
