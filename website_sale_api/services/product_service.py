"""Service for handling product-related business logic."""

# pylint:disable=import-error
from odoo.http import request

from ..schemas.product_schema import ProductData, ProductResponse
from .base_service import BaseService
from .pagination_service import PaginationService


class ProductService(BaseService):
    """Service for product-related operations"""

    model_name = "product.template"
    fields = [
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
        "rating_count",
        "product_template_image_ids",
    ]

    def get_products(self, kwargs):
        """Retrieve a list of products with pagination and sorting"""
        pager = PaginationService(kwargs)
        domain = self._get_product_domain()
        sort = kwargs.get("sort")
        # Default is sort with id
        if not sort:
            sort = "id"

        paginated_data = pager.get_paginated_records(
            model_name=self.model_name, domain=domain, fields=self.fields, sort=sort
        )

        products = []
        for product in paginated_data["data"]:
            pricing = self._compute_pricing(product)
            products.append(
                ProductData(
                    id=product["id"],
                    name=product["name"],
                    description=product["description"],
                    price=pricing["price"],
                    sale_price=pricing["sale_price"],
                    discounted_unit_price=pricing["discounted_unit_price"],
                    discount_amount=pricing["discount_amount"],
                    currency=product["currency_id"][1],
                    currency_id=product["currency_id"],
                    category_name=product["categ_id"][1],
                    stock_qty=product["qty_available"],
                    rating=product["rating_avg"],
                    review_count=product["rating_count"],
                    attributes=self._get_product_attribute_names(
                        product["attribute_line_ids"]
                    ),
                    images=self.get_product_images(
                        product["product_variant_ids"], product["id"]
                    ),
                    variants=self._get_product_variants(product["product_variant_ids"]),
                )
            )

        return ProductResponse(
            data=products,
            total=paginated_data["total"],
            page=paginated_data["page"],
            size=paginated_data["size"],
            total_pages=paginated_data["total_pages"],
            has_next=paginated_data["has_next"],
            has_prev=paginated_data["has_prev"],
        )

    def get_product_images(self, product_variant_ids, template_id):
        """
        Optimized retrieval of product images including main template image,
        variant-specific images, and extra template images.
        """
        base_url = self._get_base_url()
        # 1. Initialize with the main template image
        images = [f"{base_url}/web/image/product.template/{template_id}/image_256"]

        # 2. Batch fetch all related images in ONE database query
        # This avoids the N+1 problem and handles both variants and template images
        image_records = (
            self.env["product.image"]
            .sudo()
            .search(
                [
                    "|",
                    ("product_variant_id", "in", product_variant_ids),
                    ("product_tmpl_id", "=", template_id),
                ],
                order="sequence",
            )
        )

        # 3. Efficiently map record IDs to URLs using list comprehension
        images.extend(
            [
                f"{base_url}/web/image/product.image/{img.id}/image_256"
                for img in image_records
            ]
        )

        return images

    def _compute_pricing(self, product):
        """
        Compute pricing fields for API response
        """

        price = product["list_price"]

        # default (no pricelist logic yet)
        sale_price = price

        discounted_unit_price = sale_price
        discount_amount = price - sale_price

        return {
            "price": price,
            "sale_price": sale_price,
            "discounted_unit_price": discounted_unit_price,
            "discount_amount": discount_amount,
        }

    def _get_product_attribute_names(self, attribute_line_ids):
        """
        Return list of attribute names from product.template.attribute.line
        Example: ["Storage", "Color"]
        """

        if not attribute_line_ids:
            return []

        lines = self.env["product.template.attribute.line"].browse(attribute_line_ids)

        return list({line.attribute_id.name for line in lines if line.attribute_id})

    def _get_product_variants(self, variant_ids):
        """Get formatted product variants"""

        variants = self.env["product.product"].browse(variant_ids)

        formatted_variants = []

        for variant in variants:
            attributes = {}

            for value in variant.product_template_attribute_value_ids:
                attributes[value.attribute_id.name] = value.name

            formatted_variants.append(
                {
                    "id": variant.id,
                    "name": variant.display_name,
                    "price": variant.lst_price,
                    "stock_qty": variant.qty_available,
                    "attributes": attributes,
                }
            )

        return formatted_variants

    def get_product_by_id(self, product_id):
        """Retrieve product details by ID"""
        model = request.env[self.model_name].sudo()

        record = model.search_read(
            [("id", "=", product_id), ("website_published", "=", True)],
            self.fields,
            limit=1,
        )

        if not record:
            return {"data": None}

        product = record[0]

        # Get pricing information
        pricing = self._compute_pricing(product)

        return ProductData(
            id=product["id"],
            name=product["name"],
            description=product.get("description"),
            price=pricing["price"],
            sale_price=pricing["sale_price"],
            discounted_unit_price=pricing["discounted_unit_price"],
            discount_amount=pricing["discount_amount"],
            currency=product["currency_id"][1] if product.get("currency_id") else None,
            currency_id=product.get("currency_id"),
            category_name=product["categ_id"][1] if product.get("categ_id") else None,
            stock_qty=product.get("qty_available", 0),
            rating=product.get("rating_avg"),
            review_count=product.get("rating_count", 0),
            attributes=self._get_product_attribute_names(
                product.get("attribute_line_ids", [])
            ),
            images=self.get_product_images(
                product.get("product_variant_ids", []), product["id"]
            ),
            variants=self._get_product_variants(product.get("product_variant_ids", [])),
        )

    def _get_product_domain(self):
        """Get the domain for retrieving products.
        By default, it retrieves only published products."""
        domain = [("website_published", "=", True)]

        return domain


def get_product_service():
    """Factory function to get an instance of ProductService"""
    return ProductService()
