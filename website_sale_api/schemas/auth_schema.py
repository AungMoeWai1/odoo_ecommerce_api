"""Schemas for authentication-related API responses"""

# pylint:disable=too-few-public-methods,import-error
from typing import Optional

from pydantic import BaseModel


class UserData(BaseModel):
    """Basic user data for API responses"""

    id: int
    name: str
    email: str
    login: str


class AuthResponse(BaseModel):
    """Response schema for authentication endpoints"""

    token: Optional[str] = None
    user: Optional[UserData] = None


class ProfileResponse(UserData):
    """Response schema for user profile endpoint"""

    active: Optional[bool] = False
    company_id: Optional[int] = None
    company_name: Optional[str] = None
