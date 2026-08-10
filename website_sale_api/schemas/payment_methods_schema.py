"""Schemas for authentication-related API responses"""

# pylint:disable=too-few-public-methods
from dataclasses import dataclass


@dataclass
class PaymentMethodData:
    """Basic Payment method data"""

    id: int
    name: str


@dataclass
class PaymentMethodsResponse:
    """Response data of payment methods"""

    data: list[PaymentMethodData]
