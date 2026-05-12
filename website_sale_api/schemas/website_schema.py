"""This module defines the data schemas for website-related responses in the Odoo e-commerce API."""

from typing import List
from pydantic import BaseModel


class WebsiteData(BaseModel):
    """Pydantic schema for representing a website item"""

    id: int
    name: str


class WebsiteResponse(BaseModel):
    """Pydantic schema for representing a website response"""

    data: List[WebsiteData]
