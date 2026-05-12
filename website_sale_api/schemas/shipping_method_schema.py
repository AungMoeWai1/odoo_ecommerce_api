"""Schema definition for shipping methods in the Odoo eCommerce API."""

from typing import Optional
from pydantic import BaseModel


class ShippingMethodSchema(BaseModel):
    """Pydantic schema for representing a shipping method"""

    id: int
    name: str
    website_description: Optional[str | bool]
    carrier_description: Optional[str | bool]
    price: float
    currency: str
