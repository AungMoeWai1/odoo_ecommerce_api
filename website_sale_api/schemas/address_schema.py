"""Schemas for shipping address responses in the Odoo e-commerce API."""

# pylint:disable=too-many-instance-attributes
from dataclasses import dataclass
from typing import Optional


@dataclass
class State:
    """Schema for state"""

    id: int
    name: str


@dataclass
class StateResponse:
    """Schema for state response"""

    country_id: int
    states: list[State]


@dataclass
class Township:
    """Schema for state"""

    id: int
    name: str
    state_id: int


@dataclass
class TownshipResponse:
    """Schema for state response"""

    country_id: int
    townships: list[Township]


@dataclass
class AddressLine:
    """Schema for individual address line information"""

    id: int
    name: str
    email: str
    phone: Optional[str] = None
    street: Optional[str] = None
    city: Optional[str] = None
    zip: Optional[str] = None
    type: Optional[str] = None
    country: Optional[int] = None
    state: Optional[int] = None
    township: Optional[int] = None


@dataclass
class ShippingAddressResponse:
    """Schema for shipping address response"""

    addresses: list[AddressLine]
