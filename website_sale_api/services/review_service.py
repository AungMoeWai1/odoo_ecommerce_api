"""Service for handling product reviews in the e-commerce API."""

# pylint: disable=too-few-public-methods,import-error,protected-access
from typing import Any, Dict

from ..schemas.review_schema import ReviewDataResponse, ReviewLineData
from .pagination_service import PaginationService


class ReviewService(PaginationService):
    """Service class for handling product reviews in the e-commerce API"""

    def __init__(self, env=None):
        super().__init__(env)
        self.model_name = "rating.rating"
        self.fields = [
            "id",
            "feedback",
            "partner_id",
            "create_date",
            "rating",
            "res_id",
        ]
        self.website = self._get_current_website()

    def get_reviews(
        self, kwargs: Dict[str, Any], product_template_id
    ) -> ReviewDataResponse:
        """Retrieve a list of products with pagination and sorting"""
        self.default_domain = [
            ("res_model", "=", "product.template"),
            ("res_id", "=", product_template_id),
        ]
        paginated = self.get_paginated_from_kwargs(kwargs)
        product_tmpl = self._get_product(product_template_id).sudo()
        average_rating = product_tmpl.rating_avg

        return ReviewDataResponse(
            average_rating=average_rating,
            data=[self._format_review(rv) for rv in paginated["data"]],
            total=paginated["total"],
            size=paginated["size"],
            page=paginated["page"],
            total_pages=paginated["total_pages"],
            has_next=paginated["has_next"],
            has_prev=paginated["has_prev"],
        )

    def post_rating_comment(self, kwargs, product_template_id, user):
        """Create a product review for the given user.

        The review consists of:
        - a rating record
        - updated product rating statistics
        - an optional chatter message when feedback is provided

        :param dict kwargs: Review payload.
        :param int product_template_id: Product template ID.
        :param res.users user: Authenticated user.
        :return: API response containing the created review ID.
        :rtype: dict
        """
        product = self._get_product(product_template_id)
        rating_value = float(kwargs["rating_id"])
        feedback = kwargs.get("feedback")

        rating = product.sudo()._create_review(
            user=user, rating_value=rating_value, feedback=feedback
        )

        return {
            "id": rating.id,
            "message": "Comment created successfully",
        }

    def _format_review(self, review: Dict[str, Any]) -> ReviewLineData:
        return ReviewLineData(
            id=review["id"],
            customer_id=review["partner_id"][0],
            customer_name=review["partner_id"][1],
            rating=review["rating"],
            date=review["create_date"],
            comment=review["feedback"],
        )

    def _get_product(self, product_template_id):
        """Return the requested product template."""
        return self.env["product.template"].browse(product_template_id)
