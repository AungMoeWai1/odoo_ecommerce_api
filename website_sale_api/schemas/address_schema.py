"""Schemas for shipping address responses in the Odoo e-commerce API."""

from typing import Optional
from pydantic import BaseModel


class Country(BaseModel):
    """Schema for country information"""

    id: Optional[int] = None
    name: Optional[str] = None


class AddressLine(BaseModel):
    """Schema for individual address line information"""

    id: int
    name: str
    phone: Optional[str | bool] = None
    street: Optional[str] = None
    city: Optional[str] = None
    zip: Optional[str] = None
    type: Optional[str | bool] = None
    is_parent: bool = False
    country: Optional[Country] = None


class ShippingAddressResponse(BaseModel):
    """Schema for shipping address response"""

    partner_id: int
    addresses: list[AddressLine]
