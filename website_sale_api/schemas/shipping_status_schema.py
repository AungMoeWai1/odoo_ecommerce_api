"""shipping status schema to define the response body"""

from dataclasses import dataclass


@dataclass
class ShippingStatusSchema:
    """Schema for shipping status response"""

    id: int
    name: str
