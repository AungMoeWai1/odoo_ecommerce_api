"""Schema definitions for invoice models."""

# pylint: disable=too-few-public-methods,too-many-instance-attributes
from dataclasses import dataclass
from datetime import datetime
from typing import List

from .pagination import PaginatedResponse


@dataclass
class InvoiceLineData:
    """Schema for individual invoice line data."""

    name: str
    price: float
    quantity: int
    subtotal: float


@dataclass
class InvoiceData:
    """Schema for individual invoice data."""

    id: int
    name: str
    reference: str
    customer_id: int
    invoice_date: datetime
    currency: str
    total: float
    due_amount: float
    due_date: datetime
    payment_status: str


@dataclass
class InvoiceDetailData(InvoiceData):
    """Schema for individual invoice data."""

    shipping_address_id: int
    line: List[InvoiceLineData]


@dataclass
class InvoiceDataResponse(PaginatedResponse[InvoiceData]):
    """Paginated response schema for invoices."""
