"""Service for handling category-related business logic."""

# pylint:disable=too-few-public-methods,import-error

from ..schemas.category_schema import CategoryData, CategoryResponse
from .base_service import BaseService


class CategoryService(BaseService):
    """Service for category-related operations"""

    def __init__(self, env=None):
        super().__init__(env)
        self.model_name = "product.public.category"
        self.fields = [
            "id",
            "name",
            "parent_id",
            "image_256",
            "child_id",
        ]
        self.website = self._get_current_website()
        self.default_domain = self._get_category_domain()

    def get_categories(self, kwargs):
        """Retrieve paginated product categories"""
        categories = self.search_read(kwargs)

        category_list = []

        for category in categories:
            category_list.append(
                CategoryData(
                    id=category["id"],
                    name=category["name"],
                    parent_id=(
                        category["parent_id"][0] if category["parent_id"] else False
                    ),
                    image_256=self._get_image_url(self.model_name, category["id"]),
                    child_ids=category["child_id"],
                )
            )

        return CategoryResponse(data=category_list)

    def _get_category_domain(self):
        """Return domain for top-level categories"""

        return ["|", ("website_id", "=", self.website.id), ("website_id", "=", False)]
