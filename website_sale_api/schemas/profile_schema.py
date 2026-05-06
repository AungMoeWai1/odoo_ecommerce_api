"""Profile schema for user profile endpoint"""

# pylint: disable=no-self-argument

from typing import Optional
from pydantic import field_validator
from .auth_schema import UserData


class ProfileResponse(UserData):
    """Response schema for user profile endpoint"""

    street: Optional[str] = None
    city: Optional[str] = None
    company_id: Optional[int] = None
    company_name: Optional[str] = None
    image_url: Optional[str] = None

    """Validators"""

    @field_validator("*", mode="before")
    def clean(cls, v):
        """Clean the field values"""
        return v or None
