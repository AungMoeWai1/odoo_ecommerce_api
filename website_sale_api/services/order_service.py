"""Service for handling order-related business logic."""

# pylint: disable=import-error, too-few-public-methods

from odoo.exceptions import ValidationError
from ..schemas.order_schema import (
    OrderData,
    OrderLineData,
    OrderDataResponse,
    CurrencyData,
)
from .base_service import BaseService
from .pagination_service import PaginationService


class OrderService(BaseService):
    """Service for order-related operations."""

    model_name = "sale.order"
    fields = [
        "id",
        "name",
        "date_order",
        "amount_total",
        "delivery_status",
        "state",
        "currency_id",
    ]

    def get_orders(self, user, params, website_id):
        """Retrieve a list of sale orders with pagination."""
        partner = user.partner_id
        if not partner:
            raise ValidationError("Partner not found")

        pager = PaginationService(params)

        website = self._get_website(website_id)

        domain = self._get_order_domain(partner, website)

        sort = params.get("sort", "id")

        paginated_data = pager.get_paginated_records(
            model_name=self.model_name,
            domain=domain,
            fields=self.fields,
            sort=sort,
        )

        order_ids = [item["id"] for item in paginated_data["data"]]
        order_records = (
            self.env[self.model_name]
            .sudo()
            .search(
                [("id", "in", order_ids)],
                order=sort,
            )
        )
        orders = [self._prepare_order_data(order) for order in order_records]

        return OrderDataResponse(
            data=orders,
            size=paginated_data["size"],
            total=paginated_data["total"],
            page=paginated_data["page"],
            total_pages=paginated_data["total_pages"],
            has_next=paginated_data["has_next"],
            has_prev=paginated_data["has_prev"],
        )

    def get_order(self, user, website_id, order_id):
        """Retrieve a single sale order by ID."""
        partner = user.partner_id

        if not partner:
            raise ValidationError("Partner not found")

        website = self._get_website(website_id)

        model = self.env[self.model_name].sudo()

        order = model.search(
            [
                ("id", "=", order_id),
                ("website_id", "=", website.id),
                ("partner_id", "=", partner.id),
            ],
            limit=1,
        )

        if not order:
            raise ValidationError("Order not found")
        return self._prepare_order_data(order)

    def _prepare_order_data(self, order):
        """Prepare sale order response data."""

        order_lines = []

        for line in order.order_line:
            if line.display_type:
                continue

            order_lines.append(self._prepare_order_line_data(line))

        return OrderData(
            id=order.id,
            name=order.name,
            date_order=order.date_order,
            order_status=order.state,
            delivery_status=order.delivery_status or "",
            amount_total=order.amount_total,
            currency=CurrencyData(
                id=order.currency_id.id,
                name=order.currency_id.name,
                symbol=order.currency_id.symbol,
            ),
            item_count=len(order_lines),
            items=order_lines,
        )

    def _prepare_order_line_data(self, line):
        """Prepare sale order line response data."""

        product = line.product_id

        return OrderLineData(
            product_name=product.name,
            variant=product.display_name,
            quantity=int(line.product_uom_qty),
            price=line.price_unit,
        )

    def _get_order_domain(self, partner, website):
        domain = [("partner_id", "=", partner.id), ("website_id", "=", website.id)]
        return domain

    def _get_website(self, website_id):
        website = self.env["website"].sudo().browse(website_id)

        if not website.exists():
            raise ValidationError("Website not found")

        return website


def get_order_service():
    """Return OrderService instance."""

    return OrderService()
