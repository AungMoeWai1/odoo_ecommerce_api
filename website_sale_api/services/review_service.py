"""Service for handling product reviews in the e-commerce API."""

# pylint: disable=too-few-public-methods
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
            "consumed",
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
        product_tmpl = self.env["product.template"].browse(product_template_id)
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

    def _format_review(self, review: Dict[str, Any]) -> ReviewLineData:
        return ReviewLineData(
            id=review["id"],
            customer_name=(
                review["partner_id"][1] if review.get("partner_id") else "Unknown"
            ),
            rating=review["rating"],
            date=review["create_date"],
            comment=review["feedback"],
            is_verified_purchase=review["consumed"],
        )
