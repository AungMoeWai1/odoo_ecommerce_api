"""Service for handling product-related business logic."""

# pylint:disable=import-error,protected-access
from typing import Any, Dict, List

from odoo import fields
from odoo.tools import html2plaintext

from ..schemas.product_schema import (
    ProductData,
    ProductResponse,
    ProductVariantData,
)
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
            "allow_out_of_stock_order",
            "website_ribbon_id",
            "uom_id",
        ]
        self.website = self._get_current_website()
        self.default_domain = self.build_product_domain()
        self.default_sort = "id"

    def get_products(self, kwargs: Dict[str, Any]) -> ProductResponse[ProductData]:
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

    def get_discounted_products(
        self, kwargs: Dict[str, Any]
    ) -> ProductResponse[ProductData]:
        """Retrieve product templates with discounted variants."""
        rules = self._get_website_pricelist_rules()
        discounted_templates = self._get_discounted_template_prices(rules)
        self.default_domain = [("id", "in", list(discounted_templates))]
        paginated = self.get_paginated_from_kwargs(kwargs)
        return ProductResponse(
            data=[
                self._format_product(product, discounted_templates[product["id"]])
                for product in paginated["data"]
            ],
            total=paginated["total"],
            page=paginated["page"],
            size=paginated["size"],
            total_pages=paginated["total_pages"],
            has_next=paginated["has_next"],
            has_prev=paginated["has_prev"],
        )

    def _get_website_pricelist_rules(self):
        """Return the pricing rules for the current website pricelist."""
        pricelist = self._get_price_list(self.website)
        return self.env["product.pricelist.item"].sudo().search(
            [("pricelist_id", "=", pricelist.id)]
        )

    def _get_discounted_template_prices(self, rules) -> Dict[int, Dict[str, Any]]:
        """Return the lowest discounted variant price for each product template."""
        if not rules:
            return {}

        domain = self._get_pricelist_candidate_domain(rules)
        templates = self.env["product.template"].sudo().search(domain)
        variants = self.env["product.product"].sudo().search(
            [("product_tmpl_id", "in", templates.ids)]
        )
        pricelist = self._get_price_list(self.website)
        currency = self.website.currency_id.with_context(self.env.context)
        prices_and_rules = pricelist._compute_price_rule(
            variants,
            quantity=1.0,
            currency=currency,
        )
        rule_model = self.env["product.pricelist.item"]
        rules_by_id = {
            rule.id: rule
            for rule in rule_model.browse(
                list({rule_id for _, rule_id in prices_and_rules.values()} - {False})
            )
        }

        template_prices = {}
        for variant in variants:
            price, rule_id = prices_and_rules[variant.id]
            pricelist_info = self._build_pricelist_info(
                variant,
                price,
                rules_by_id.get(rule_id, rule_model.browse()),
                currency,
            )
            if pricelist_info["discount_amount"] <= 0:
                continue

            template_id = variant.product_tmpl_id.id
            current = template_prices.get(template_id)
            if current is None or pricelist_info["price"] < current["price"]:
                template_prices[template_id] = pricelist_info
        return template_prices

    def _get_pricelist_candidate_domain(self, rules):
        """Build the product-template domain covered by the supplied rules."""
        domain = self.build_product_domain()
        if any(rule.applied_on == "3_global" for rule in rules):
            return domain

        template_ids = rules.mapped("product_tmpl_id").ids
        template_ids += rules.mapped("product_id.product_tmpl_id").ids
        category_ids = rules.filtered(
            lambda rule: rule.applied_on == "2_product_category"
        ).mapped("categ_id").ids

        candidate_domains = []
        if template_ids:
            candidate_domains.append([("id", "in", list(set(template_ids)))])
        if category_ids:
            candidate_domains.append([("categ_id", "child_of", category_ids)])
        candidate_domain = (
            fields.Domain.OR(candidate_domains)
            if candidate_domains
            else [("id", "=", 0)]
        )
        return fields.Domain.AND([domain, candidate_domain])

    def _format_variant_data(
        self, variant, pricelist_info: Dict[str, Any], currency
    ) -> ProductVariantData:
        """Serialize a variant with its calculated price and related data."""
        return ProductVariantData(
            id=variant.id,
            name=variant.display_name,
            description=html2plaintext(variant.description_ecommerce),
            allow_out_of_stock_order=variant.allow_out_of_stock_order,
            price=variant.lst_price,
            sale_price=pricelist_info["price"],
            discount_amount=pricelist_info["discount_amount"],
            discount_type=pricelist_info["discount_type"],
            currency=currency.name,
            currency_id=currency.id,
            category_id=variant.public_categ_ids.ids,
            rating=variant.rating_avg or 0.0,
            review_count=variant.rating_count or 0,
            stock_qty=variant.qty_available or 0.0,
            attributes=self.get_attributes_dict(variant),
            images=self._get_variant_image_urls(variant),
        )

    def _get_variant_image_urls(self, variant) -> List[str]:
        """Build image URLs for all images associated with a variant."""
        return [
            self._get_image_url(record._name, record.id, size="image_1024")
            for record in variant._get_images()
        ]

    def _format_product(
        self, product: Dict, pricelist_info: Dict[str, Any] = None
    ) -> ProductData:
        """Convert raw product data to ProductData schema."""
        if pricelist_info is None:
            product_tmpl = self.env["product.template"].browse(product["id"])
            pricelist_info = self.get_pricelist_info(product_tmpl)

        return ProductData(
            id=product["id"],
            name=product["name"],
            description=product.get("description"),
            allow_out_of_stock_order=product["allow_out_of_stock_order"],
            stock_qty=product["qty_available"],
            price=product["list_price"],
            sale_price=pricelist_info["price"],
            discount_amount=pricelist_info["discount_amount"],
            discount_type=pricelist_info["discount_type"],
            currency=self.website.currency_id.name,
            currency_id=self.website.currency_id.id,
            category_id=product.get("public_categ_ids"),
            website_ribbon_id=(
                product["website_ribbon_id"][0]
                if product["website_ribbon_id"]
                else None
            ),
            rating=product.get("rating_avg", 0.0),
            review_count=product.get("rating_count", 0),
            images=self._get_image_url(self.model_name, product["id"]),
        )

    def get_pricelist_info(self, product) -> Dict[str, Any]:
        """Get pricelist price and rule for a product."""
        pricelist = self._get_price_list(self.website)
        currency = self.website.currency_id.with_context(self.env.context)
        price, rule_id = pricelist._get_product_price_rule(
            product=product,
            quantity=1.0,
            uom=product.uom_id,
            currency=currency,
        )
        rule = self.env["product.pricelist.item"].browse(rule_id)
        return self._build_pricelist_info(product, price, rule, currency)

    def _build_pricelist_info(
        self, product, price: float, rule, currency
    ) -> Dict[str, Any]:
        """Build displayed price and discount details from a matched rule."""
        price_before_discount = price
        if (
            rule
            and rule.compute_price == "formula"
            and rule._show_discount_on_shop()
        ):
            price_before_discount = rule._compute_price_before_discount(
                product=product,
                quantity=1.0,
                date=fields.Date.context_today(product),
                uom=product.uom_id,
                currency=currency,
            )
        if rule and rule.compute_price == "percentage":
            discount_amount = rule.percent_price
        elif rule and rule.compute_price == "fixed":
            original_price = product.currency_id._convert(
                product.lst_price,
                currency,
                company=self.env.company,
                date=fields.Date.context_today(product),
            )
            discount_amount = max(original_price - price, 0.0)
        else:
            discount_amount = (
                price_before_discount - price
                if currency.compare_amounts(price_before_discount, price) == 1
                else 0.0
            )

        return {
            "price": round(price, 2),
            "discount_amount": round(discount_amount, 2),
            "discount_type": rule.compute_price if rule else None,
        }

    def get_attributes_dict(self, variant) -> Dict[str, str]:
        """Get variant attributes as dictionary."""
        result = {}
        for value in variant.product_template_attribute_value_ids:
            result[value.attribute_id.name] = value.name
            if value.display_type == "color" and value.html_color:
                result[value.attribute_id.name] += "," + value.html_color
        return result

    def build_product_domain(self) -> List:
        """Build standard product domain with website and published filters."""
        return [
            "|",
            ("website_id", "=", self.website.id),
            ("website_id", "=", False),
            ("website_published", "=", True),
        ]
