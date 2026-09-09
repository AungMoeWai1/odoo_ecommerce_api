"""Schema definitions for Product model."""

# pylint:disable=too-many-instance-attributes
from dataclasses import dataclass
from typing import Optional

from .pagination import PaginatedResponse


@dataclass
class NotificationData:
    """Base schema with common fields for both product and variant"""

    id: int
    name: str
    receiver_id: int
    receiver_name: str
    read_status: str
    status: str
    create_date: Optional[str]
    title: Optional[str] = None
    body: Optional[str] = None


@dataclass
class NotificationResponse(PaginatedResponse[NotificationData]):
    """Response schema for Product model"""
