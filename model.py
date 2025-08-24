"""Data models for ads."""
from dataclasses import dataclass
from typing import Optional


@dataclass
class Ad:
    """Represents a single eBay Kleinanzeigen advertisement."""
    id: str
    title: str
    price: Optional[int]
    location: Optional[str]
    date_posted: Optional[str]
    link: str
    image: Optional[str]
    body_text: Optional[str]
    first_seen: str
    last_seen: str
    is_active: bool = True
