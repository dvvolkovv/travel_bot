from __future__ import annotations

from dataclasses import dataclass, field
from decimal import Decimal


@dataclass
class PriceOriginal:
    amount: Decimal
    currency: str


@dataclass
class HotelOffer:
    offer_id: str
    hotel_name: str
    stars: int
    rating: float
    rating_label: str
    price_per_night_usd: Decimal
    price_per_night_original: PriceOriginal
    total_usd: Decimal
    discount_pct: int | None
    original_price_usd: Decimal | None
    amenities: list[str]
    distance_to_center_km: float | None
    distance_to_beach_km: float | None
    photo_url: str | None
    booking_url: str


@dataclass
class SearchResult:
    offers: list[HotelOffer]
    total_found: int
    source: str = "booking.com"
    fallback_used: bool = False
    warnings: list[str] = field(default_factory=list)


@dataclass
class HotelDetails:
    offer_id: str
    hotel_name: str
    description: str
    amenities: list[str]
    room_types: list[dict]
    cancellation_policy: str | None
    photos: list[str]
    address: str | None
