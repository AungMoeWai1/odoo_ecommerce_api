"""Service for handling product variant-related business logic."""

# pylint:disable=import-error,protected-access
from typing import List

from odoo.exceptions import ValidationError

from ..schemas.product_schema import DetailProductData, ProductVariantData
from .product_service import ProductService


class ProductVariantService(ProductService):
    """Service for product variant operations."""

    def __init__(self, env=None):
        super().__init__(env)
        self.model_name = "product.product"
        self.fields = [
            "id",
            "name",
            "description",
            "lst_price",
            "currency_id",
            "qty_available",
            "rating_avg",
            "rating_count",
            "product_template_attribute_value_ids",
            "product_tmpl_id",
            "allow_out_of_stock_order",
            "image_1024",
        ]

    def get_product_by_id(self, product_id: int) -> DetailProductData:
        """Retrieve product details by ID."""
        product = (
            self.env["product.template"]
            .sudo()
            .search(self.default_domain + [("id", "=", product_id)])
        )
        if not product:
            raise ValidationError("No Product found!")

        return DetailProductData(
            id=product["id"],
            variants=self.get_variants_by_template_id(product_id),
        )

    def get_variants_by_template_id(
        self, prod_tmpl_id: int
    ) -> List[ProductVariantData]:
        """Get all variants for a product template."""
        variants = (
            self.env["product.product"]
            .sudo()
            .search([("product_tmpl_id", "=", prod_tmpl_id)])
        )

        return [self._format_variant_as_dataclass(v) for v in variants]

    def _format_variant_as_dataclass(self, variant) -> ProductVariantData:
        """Format a single variant as ProductVariantData."""
        pricelist_info = self.get_pricelist_info(variant)
        return ProductVariantData(
            id=variant.id,
            name=variant.display_name,
            description=variant.description,
            allow_out_of_stock_order=variant.allow_out_of_stock_order,
            price=variant.lst_price,
            sale_price=pricelist_info["price"],
            discount_amount=pricelist_info["discount_amount"],
            discount_type=pricelist_info["discount_type"],
            currency=variant.currency_id.name,
            currency_id=variant.currency_id.id,
            category_id=variant.public_categ_ids.mapped("id"),
            stock_qty=variant.qty_available or 0.0,
            rating=variant.rating_avg or 0.0,
            review_count=variant.rating_count or 0,
            attributes=self.get_attributes_dict(variant),
            images=self._get_product_images(variant),
        )

    def _get_product_images(self, variant):
        """Get all product images and convert to URLs."""
        image_records = variant._get_images()

        return [
            self._get_image_url(record._name, record.id, size="image_1024")
            for record in image_records
        ]
