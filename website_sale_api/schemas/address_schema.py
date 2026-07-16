"""Schemas for shipping address responses in the Odoo e-commerce API."""

from dataclasses import dataclass
from typing import Optional


@dataclass
class Country:
    """Schema for country information"""

    id: Optional[int] = None
    name: Optional[str] = None


@dataclass
class AddressLine:
    """Schema for individual address line information"""

    id: int
    name: str
    phone: Optional[str] = None
    street: Optional[str] = None
    city: Optional[str] = None
    zip: Optional[str] = None
    type: Optional[str | bool] = None
    is_parent: bool = False
    country: Optional[Country] = None


@dataclass
class ShippingAddressResponse:
    """Schema for shipping address response"""

    partner_id: int
    addresses: list[AddressLine]
