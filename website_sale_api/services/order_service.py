"""Service for handling order-related business logic."""

# pylint: disable=import-error, too-few-public-methods

from dataclasses import asdict

from odoo.exceptions import ValidationError
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

    def _get_selection_map(self, field):
        """Return {key: label} for a selection field of the current model."""
        return dict(self._get_model().fields_get([field])[field]["selection"])

    def get_orders(self, user, kwargs):
        """Retrieve a list of sale orders with pagination."""
        partner = user.partner_id

        self.default_domain = self._get_order_domain(partner, self.website.id)

        paginated_data = self.get_paginated_from_kwargs(kwargs)
        shipping_map = self._get_selection_map("shipping_status")

        return OrderDataResponse(
            data=[self._format_order(o, shipping_map) for o in paginated_data["data"]],
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

        self.default_domain = self._get_order_domain(partner, self.website.id) + [
            ("id", "=", order_id),
            ("state", "=", "sale"),
        ]
        order = self.search()
        if order:
            return self.format_order_detail(order)
        raise ValidationError("Order not found")

    def _get_order_domain(self, partner, website_id):
        domain = [
            ("partner_id", "=", partner.id),
            ("website_id", "=", website_id),
            ("state", "!=", "draft"),
        ]
        return domain

    def format_order_detail(self, order):
        """Format order detail data."""
        shipping_map = self._get_selection_map("shipping_status")
        order_data = self._format_order(order, shipping_map)
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

    def _format_order(self, order, shipping_map) -> OrderData:
        """Convert raw product data to ProductData schema."""

        def get_field(field):
            """Return (id, name) for a m2o field, or (None, None)."""
            if isinstance(order, dict):
                value = order.get(field)
                return value if isinstance(value, (tuple, list)) else (None, None)

            obj = getattr(order, field, None)
            return (obj.id, obj.name) if obj else (None, None)

        _, currency_name = get_field("currency_id")
        return OrderData(
            id=order["id"],
            name=order["name"],
            reference=order["reference"],
            date_order=order["date_order"],
            status=order["state"],
            currency=currency_name,
            shipping_status=order["shipping_status"],
            shipping_status_value=shipping_map.get(order["shipping_status"], ""),
            total=order["amount_total"],
            item_count=len(order["order_line"]),
        )
