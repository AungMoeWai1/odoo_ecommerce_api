"""Service for handling product reviews in the e-commerce API."""

# pylint: disable=too-few-public-methods,import-error,protected-access
from typing import Any, Dict

from odoo import tools

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
            "message_id",
        ]
        self.website = self._get_current_website()

    def get_rating_comment(
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

    def post_rating_comment(self, data, product_template_id, user):
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
        rating_value = float(data["rating_value"])
        feedback = data.get("feedback")

        rating = product.sudo()._create_review(
            user=user, rating_value=rating_value, feedback=feedback
        )

        return {
            "id": rating.id,
            "message": "Comment created successfully",
        }

    def update_rating_comment(self, data, user, rating_id):
        """Update an existing product review owned by the authenticated user."""

        rating = self.get_record_by_id(rating_id)

        # A user can only modify their own review.
        if rating.partner_id != user.partner_id:
            raise ValueError("You can only edit your own review.")

        # Delegate review-specific update logic to the product model.
        product = self._get_product(rating.res_id)
        product._update_review(
            rating=rating,
            feedback=data.get("feedback"),
        )
        return {
            "id": rating.id,
            "message": "Comment updated successfully",
        }

    def delete_rating_comment(self, user, rating_id):
        """Delete an existing product review owned by the authenticated user."""
        rating = self.get_record_by_id(rating_id)
        if rating.partner_id != user.partner_id:
            raise ValueError("You can only edit your own review.")

        rating.unlink()

        return {
            "id": rating_id,
            "message": "Comment deleted successfully",
        }

    def _format_review(self, review: Dict[str, Any]) -> ReviewLineData:
        comment = review["feedback"] or ""
        if review.get("message_id"):
            message = self.env["mail.message"].browse(review["message_id"][0])
            comment = tools.mail.html_to_inner_content(message.body or "").strip()

        return ReviewLineData(
            id=review["id"],
            customer_id=review["partner_id"][0],
            customer_name=review["partner_id"][1],
            rating=review["rating"],
            date=review["create_date"],
            comment=comment,
        )

    def _get_product(self, product_template_id):
        """Return the requested product template."""
        return self.env["product.template"].browse(product_template_id)
