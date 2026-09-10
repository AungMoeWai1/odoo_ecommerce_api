"""promotion schema"""

from dataclasses import dataclass


@dataclass
class PromotionSchema:
    """Schema for promotions"""

    id: int
    product_tmpl_id: int
    description: str
    image_1920: str
