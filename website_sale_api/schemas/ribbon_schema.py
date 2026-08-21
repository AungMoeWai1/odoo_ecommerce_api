"""ribbon_schema.py"""

from dataclasses import dataclass


@dataclass
class BadgeSchema:
    """Schema for badges"""

    id: int
    name: str
    text_color: str
    bg_color: str
    position: str
    style: str
    assign: str
