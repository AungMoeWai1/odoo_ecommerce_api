"""Schemas for authentication-related API responses"""

# pylint:disable=too-few-public-methods
from dataclasses import dataclass
from typing import Optional


@dataclass
class UserData:
    """Basic user data for API responses"""

    id: int
    name: str
    login: str


@dataclass
class UpdateUserData:
    """Basic user data for API responses"""

    name: str
    login: str


@dataclass
class AuthResponse:
    """Response schema for authentication endpoints"""

    token: Optional[str] = None
