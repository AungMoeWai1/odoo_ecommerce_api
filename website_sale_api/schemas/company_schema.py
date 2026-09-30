"""Schema definitions for Company model."""

# pylint:disable=too-few-public-methods
from dataclasses import dataclass
from typing import Optional


@dataclass
class SocialSchema:
    """Schema for Social data."""
    social_twitter: Optional[str] = None
    social_facebook: Optional[str] = None
    social_github: Optional[str] = None
    social_linkedin: Optional[str] = None
    social_youtube: Optional[str] = None
    social_tiktok: Optional[str] = None
    social_discourse: Optional[str] = None


@dataclass
class CompanyResponse:
    """Schema for individual company data"""

    id: int
    name: str
    logo: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    website: Optional[str] = None
    address: Optional[str] = None
    social: SocialSchema = None
