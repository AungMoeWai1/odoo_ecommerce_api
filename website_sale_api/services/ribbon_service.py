"""RibbonService"""

from .base_service import BaseService
from ..schemas.ribbon_schema import BadgeSchema


class RibbonService(BaseService):
    """RibbonService"""

    def __init__(self, env=None):
        super().__init__(env)
        self.model_name = "product.ribbon"
        self.fields = [
            "id",
            "name",
            "text_color",
            "bg_color",
            "position",
            "style",
            "assign",
        ]

    def fetch_all_ribbons(self):
        """Fetch all ribbons"""
        ribbons = self.search()

        return [
            BadgeSchema(
                id=ribbon.id,
                name=ribbon.name,
                text_color=ribbon.text_color,
                bg_color=ribbon.bg_color,
                position=ribbon.position,
                style=ribbon.style,
                assign=ribbon.assign,
            )
            for ribbon in ribbons
        ]
