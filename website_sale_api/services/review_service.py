"""Service for handling product reviews in the e-commerce API."""

# pylint: disable=too-few-public-methods

from ..schemas.review_schema import ReviewDataResponse, ReviewLineData
from .base_service import BaseService
from .pagination_service import PaginationService


class ReviewService(BaseService):
    """Service class for handling product reviews in the e-commerce API"""

    model_name = "rating.rating"
    fields = [
        "id",
        "consumed",
        "feedback",
        "partner_id",
        "create_date",
        "rating",
        "res_id",
    ]

    def get_reviews(self, params, product_template_id):
        """Retrieve a list of products with pagination and sorting"""
        pager = PaginationService(params)
        domain = self._build_review_domain(product_template_id)
        sort = params.get("sort", "id")

        reviews_data = pager.get_paginated_records(
            model_name=self.model_name, domain=domain, fields=self.fields, sort=sort
        )

        reviews = [
            ReviewLineData(
                id=review["id"],
                customer_name=(
                    review["partner_id"][1] if review.get("partner_id") else "Unknown"
                ),
                rating=review["rating"],
                comment=review["feedback"],
                date=review["create_date"],
                is_verified_purchase=review["consumed"],
            )
            for review in reviews_data["data"]
        ]

        avg_data = (
            self.env[self.model_name]
            .sudo()
            .formatted_read_group(domain, [], ["rating:avg"])
        )

        average_rating = 0.0
        if avg_data:
            average_rating = avg_data[0].get("rating", 0.0) or 0.0

        return ReviewDataResponse(
            average_rating=round(average_rating, 1),
            data=reviews,
            total=reviews_data["total"],
            page=reviews_data["page"],
            size=reviews_data["size"],
            total_pages=reviews_data["total_pages"],
            has_next=reviews_data["has_next"],
            has_prev=reviews_data["has_prev"],
        )

    def _build_review_domain(self, product_template_id):
        """Construct the domain for fetching reviews based on product template ID"""
        return [
            ("res_model", "=", "product.template"),
            ("res_id", "=", product_template_id),
        ]


def get_review_service():
    """Factory method to get an instance of ReviewService"""
    return ReviewService()
