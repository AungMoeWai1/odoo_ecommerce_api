"""RibbonService"""

from ..schemas.promotion_schema import PromotionSchema
from .base_service import BaseService


class PromotionService(BaseService):
    """BannerService"""

    def __init__(self, env=None):
        super().__init__(env)
        self.model_name = "website.promotion.popup"
        self.fields = [
            "id",
            "product_id",
            "description",
            "image_1024",
            "image_256",
            "image_1920",
            "image_128",
        ]

    def fetch_all_promotions(self):
        """Fetch all promotions"""
        self.default_domain = [("is_published", "=", True)]
        promotions = self.search()

        return [
            PromotionSchema(
                id=promotion.id,
                product_tmpl_id=promotion.product_id.id,
                description=promotion.description,
                image_1920=self._get_image_url(
                    self.model_name,
                    promotion.id,
                    size="image_1920",
                ),
            )
            for promotion in promotions
        ]
