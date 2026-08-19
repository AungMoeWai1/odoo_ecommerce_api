"""Service for handling order-related business logic."""

# pylint: disable=import-error, too-few-public-methods

from dataclasses import asdict

from odoo.http import request

from ..schemas.order_schema import (
    OrderData,
    OrderDataResponse,
    OrderDetailData,
    OrderLineData,
)
from .pagination_service import PaginationService


class OrderService(PaginationService):
    """Service for order-related operations."""

    def __init__(self, env=None):
        super().__init__(env)
        self.model_name = "sale.order"
        self.website = self._get_current_website()

    def get_orders(self, user, kwargs):
        """Retrieve a list of sale orders with pagination."""
        partner = user.partner_id

        self.default_domain = self._get_order_domain(partner, self.website.id)

        paginated_data = self.get_paginated_from_kwargs(kwargs)

        return OrderDataResponse(
            data=[self._format_order(o) for o in paginated_data["data"]],
            size=paginated_data["size"],
            total=paginated_data["total"],
            page=paginated_data["page"],
            total_pages=paginated_data["total_pages"],
            has_next=paginated_data["has_next"],
            has_prev=paginated_data["has_prev"],
        )

    def get_order_detail(self, user, order_id):
        """Retrieve a single sale order by ID."""
        partner = user.partner_id

        self.default_domain = self._get_order_domain(partner, self.website.id)
        self.default_domain.append(("id", "=", order_id))
        order = self.search()
        return self.format_order_detail(order)

    def _get_order_domain(self, partner, website_id):
        domain = [
            ("partner_id", "=", partner.id),
            ("website_id", "=", website_id),
            ("state", "=", "sale"),
        ]
        return domain

    def format_order_detail(self, order):
        """Format order detail data."""
        order_data = self._format_order(order)
        return OrderDetailData(
            **asdict(order_data),
            customer_id=order.partner_id.id,
            billing_address_id=order.partner_invoice_id.id,
            shipping_address_id=order.partner_shipping_id.id,
            line=self.getorderline(order)
        )

    def getorderline(self, order):
        """Format order line data."""
        orderlines = []
        for line in order["order_line"]:
            line_data = request.env["sale.order.line"].sudo().browse(line["id"])
            orderlines.append(
                OrderLineData(
                    product_name=line_data.product_template_id.name,
                    quantity=line_data.product_uom_qty,
                    price=line_data.price_unit,
                    subtotal=line_data.price_subtotal,
                )
            )
        return orderlines

    def _format_order(self, order) -> OrderData:
        """Convert raw product data to ProductData schema."""

        def get_field(field, index=1):
            """Extract field value from dict or object."""
            if isinstance(order, dict):
                value = order.get(field)
                return value[index] if value else None
            obj = getattr(order, field, None)
            return obj.name if obj else None

        return OrderData(
            id=order["id"],
            name=order["name"],
            reference=order["reference"],
            date_order=order["date_order"],
            status=order["state"],
            currency=get_field("currency_id"),
            delivery_status=get_field("shipping_status_id"),
            total=order["amount_total"],
            item_count=len(order["order_line"]),
        )
