"""Service for handling invoice-related business logic."""

# pylint: disable=import-error, too-few-public-methods

from dataclasses import asdict

from odoo.exceptions import ValidationError
from odoo.http import request

from ..schemas.invoice_schema import (
    InvoiceData,
    InvoiceDataResponse,
    InvoiceDetailData,
    InvoiceLineData,
)
from .pagination_service import PaginationService


class InvoiceService(PaginationService):
    """Service for invoice-related operations."""

    def __init__(self, env=None):
        super().__init__(env)
        self.model_name = "account.move"
        self.website = self._get_current_website()

    def get_invoices(self, user, kwargs):
        """Retrieve a list of invoice with pagination."""
        partner = user.partner_id

        self.default_domain = self._get_invoice_domain(partner, self.website.id)
        paginated_data = self.get_paginated_from_kwargs(kwargs)

        return InvoiceDataResponse(
            data=[self._format_invoice(invoice) for invoice in paginated_data["data"]],
            size=paginated_data["size"],
            page=paginated_data["page"],
            total=paginated_data["total"],
            has_next=paginated_data["has_next"],
            total_pages=paginated_data["total_pages"],
            has_prev=paginated_data["has_prev"],
        )

    def get_invoice_detail(self, user, invoice_id):
        """Retrieve a single sale order by ID."""
        partner = user.partner_id

        self.default_domain = self._get_invoice_domain(partner, self.website.id)
        self.default_domain.append(("id", "=", invoice_id))
        invoice = self.search()
        if invoice:
            return self.format_invoice_detail(invoice)
        raise ValidationError("Invoice not found")

    def _get_invoice_domain(self, partner, website_id):
        domain = [
            ("partner_id", "child_of", partner.id),
            ("website_id", "=", website_id),
            ("move_type", "=", "out_invoice"),
        ]
        return domain

    def format_invoice_detail(self, invoice):
        """Format order detail data."""
        order_data = self._format_invoice(invoice)
        return InvoiceDetailData(
            **asdict(order_data),
            shipping_address_id=invoice.partner_shipping_id.id,
            line=self.get_invoice_line(invoice)
        )

    def get_invoice_line(self, order):
        """Format order line data."""
        invoice_lines = []
        for line in order["invoice_line_ids"]:
            line_data = request.env["account.move.line"].sudo().browse(line["id"])
            invoice_lines.append(
                InvoiceLineData(
                    name=line_data.name,
                    quantity=line_data.quantity,
                    price=line_data.price_unit,
                    subtotal=line_data.price_subtotal,
                )
            )
        return invoice_lines

    def _format_invoice(self, invoice) -> InvoiceData:
        """Convert raw product data to ProductData schema."""

        def get_field(field, index=1):
            """Extract field value from dict or object."""
            if isinstance(invoice, dict):
                value = invoice.get(field)
                return value[index] if value else None
            obj = getattr(invoice, field, None)
            return obj.name if obj else None

        return InvoiceData(
            id=invoice["id"],
            name=invoice["name"],
            reference=invoice["ref"],
            invoice_date=invoice["invoice_date"],
            payment_status=invoice["payment_state"],
            total=invoice["amount_total"],
            due_amount=invoice["amount_residual"],
            due_date=invoice["invoice_date_due"],
            customer_id=get_field("partner_id", 0),
            currency=get_field("currency_id"),
        )
