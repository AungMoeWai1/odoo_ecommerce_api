"""Service for handling product-related business logic."""

# pylint:disable=import-error,protected-access
from typing import Any, Dict, List

from ..schemas.product_schema import ProductData, ProductResponse
from .pagination_service import PaginationService


class ProductService(PaginationService):
    """Service for product-related operations."""

    def __init__(self, env=None):
        super().__init__(env)
        self.model_name = "product.template"
        self.fields = [
            "id",
            "name",
            "description",
            "currency_id",
            "categ_id",
            "rating_avg",
            "list_price",
            "attribute_line_ids",
            "product_variant_ids",
            "standard_price",
            "sale_ok",
            "website_published",
            "image_256",
            "qty_available",
            "public_categ_ids",
            "rating_count",
            "product_template_image_ids",
            "uom_id",
        ]
        self.website = self._get_current_website()
        self.default_domain = self.build_product_domain()
        self.default_sort = "id"

    def get_products(self, kwargs: Dict[str, Any]) -> ProductResponse:
        """Retrieve a list of products with pagination."""
        paginated = self.get_paginated_from_kwargs(kwargs)

        return ProductResponse(
            data=[self._format_product(p) for p in paginated["data"]],
            total=paginated["total"],
            page=paginated["page"],
            size=paginated["size"],
            total_pages=paginated["total_pages"],
            has_next=paginated["has_next"],
            has_prev=paginated["has_prev"],
        )

    def _format_product(self, product: Dict) -> ProductData:
        """Convert raw product data to ProductData schema."""
        product_tmpl = self.env["product.template"].browse(product["id"])
        pricelist_info = self.get_pricelist_info(product_tmpl)

        return ProductData(
            id=product["id"],
            name=product["name"],
            description=product.get("description"),
            price=product["list_price"],
            sale_price=pricelist_info["price"],
            discount_amount=pricelist_info["discount_amount"],
            discount_type=pricelist_info["discount_type"],
            currency=self.website.currency_id.name,
            currency_id=self.website.currency_id.id,
            category_id=product.get("public_categ_ids"),
            rating=product.get("rating_avg", 0.0),
            review_count=product.get("rating_count", 0),
            images=self._get_image_url("product.template", product["id"]),
        )

    def get_pricelist_info(self, product) -> Dict[str, Any]:
        """Get pricelist price and rule for a product."""
        pricelist = self.website.pricelist_ids[0]
        price, rule_id = pricelist._get_product_price_rule(
            product=product, quantity=1.0, uom=product.uom_id
        )
        rule = self.env["product.pricelist.item"].browse(rule_id)
        discount_info = self._calculate_discount(rule)

        return {
            "price": round(price, 2),
            "discount_amount": discount_info["amount"],
            "discount_type": discount_info["type"],
        }

    def _calculate_discount(self, rule) -> Dict[str, Any]:
        """Calculate discount information from pricelist rule."""
        compute_type = rule.compute_price
        discount_map = {
            "percentage": rule.percent_price,
            "formula": rule.price_discount,
            "fixed": rule.fixed_price,
        }

        return {"amount": discount_map.get(compute_type, 0.0), "type": compute_type}

    def get_product_images(
        self, model_name: str, record_id: int, field: str = "image_256"
    ) -> str:
        """Get product images URL."""
        return self._get_image_url(model_name, record_id, field)

    def get_variant_images(self, variant) -> List[str]:
        """Get images for a variant with fallback hierarchy."""
        product_image = self.env["product.image"].sudo()

        # Get variant images first, then template images
        images = product_image.search(
            [
                "|",
                ("product_variant_id", "=", variant.id),
                ("product_tmpl_id", "=", variant.product_tmpl_id.id),
            ],
            order="product_variant_id DESC, sequence",
        )

        # Return image URLs or fallback to template main image
        return [
            self._get_image_url("product.image", img.id, "image_256") for img in images
        ] or [
            self._get_image_url(
                "product.template", variant.product_tmpl_id.id, "image_256"
            )
        ]

    def get_attributes_dict(self, variant) -> Dict[str, str]:
        """Get variant attributes as dictionary."""
        return {
            value.attribute_id.name: value.name
            for value in variant.product_template_attribute_value_ids
        }

    def build_product_domain(self) -> List:
        """Build standard product domain with website and published filters."""
        return [
            "|",
            ("website_id", "=", self.website.id),
            ("website_id", "=", False),
            ("website_published", "=", True),
        ]
