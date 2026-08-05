"""Schema definition for shipping methods in the Odoo eCommerce API."""

from dataclasses import dataclass
from typing import Optional


@dataclass
class DeliveryMethodSchema:
    """Response schema for representing a delivery method"""

    id: int
    name: str
    website_description: Optional[str | bool]
    carrier_description: Optional[str | bool]
    price: float
    currency_id: int
