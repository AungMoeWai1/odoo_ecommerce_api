"""Controller for handling product reviews in the e-commerce API."""

# pylint: disable=import-error,too-few-public-methods
import json

from odoo import http
from odoo.exceptions import ValidationError
from odoo.http import request

from ..services.review_service import ReviewService
from ..services.token_service import JWTService
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
                ReviewService().get_rating_comment(
                    kwargs=kwargs, product_template_id=product_template_id
                )
            )
        except ValidationError as e:
            return self._error(message=str(e), code=400)

    @http.route(
        "/api/product/<int:product_template_id>/reviews",
        type="http",
        auth="public",
        methods=["POST"],
        csrf=False,
    )
    @JWTService.jwt_required()
    def post_rating(self, product_template_id):
        """Fetch reviews for a given product template"""

        try:
            user = request.authenticated_user
            data = json.loads(request.httprequest.data or "{}")
            return self._success(
                ReviewService().post_rating_comment(
                    data=data, product_template_id=product_template_id, user=user
                )
            )
        except ValidationError as e:
            return self._error(message=str(e), code=400)

    @http.route(
        "/api/reviews/<int:rating_id>",
        type="http",
        auth="public",
        methods=["PUT"],
        csrf=False,
    )
    @JWTService.jwt_required()
    def update_rating(self, rating_id):
        """Fetch reviews for a given product template"""

        try:
            user = request.authenticated_user
            data = json.loads(request.httprequest.data or "{}")
            return self._success(
                ReviewService().update_rating_comment(
                    data=data, user=user, rating_id=rating_id
                )
            )
        except ValidationError as e:
            return self._error(message=str(e), code=400)

    @http.route(
        "/api/reviews/<int:rating_id>",
        type="http",
        auth="public",
        methods=["DELETE"],
        csrf=False,
    )
    @JWTService.jwt_required()
    def delete_rating(self, rating_id):
        """Fetch reviews for a given product template"""

        try:
            user = request.authenticated_user
            return self._success(
                ReviewService().delete_rating_comment(user=user, rating_id=rating_id)
            )
        except ValidationError as e:
            return self._error(message=str(e), code=400)
