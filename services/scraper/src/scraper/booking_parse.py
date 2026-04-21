from __future__ import annotations

import hashlib
import re
from decimal import Decimal

from lxml import html as lxml_html

from .booking_selectors import (
    AMENITY_KEYWORDS,
    CARD_AMENITIES,
    CARD_DISTANCE,
    CARD_LINK,
    CARD_NAME,
    CARD_PHOTO,
    CARD_PRICE,
    CARD_PRICE_ORIGINAL,
    CARD_RATING,
    CARD_RATING_LABEL,
    CARD_ROOT,
    CARD_STARS,
    DETAILS_ADDRESS,
    DETAILS_AMENITIES,
    DETAILS_DESCRIPTION,
    DETAILS_NAME,
    DETAILS_PHOTOS,
)
from .types import HotelDetails, HotelOffer, PriceOriginal

_PRICE_RE = re.compile(r"(?P<currency>[€£$]|US\$|RUB|₽)\s*(?P<amount>[\d\s,.]+)")
_DISTANCE_RE = re.compile(r"(?P<km>[\d.]+)\s*km", re.IGNORECASE)
_RATING_RE = re.compile(r"\d+(?:[.,]\d+)?")


def parse_search_html(html: str, source_currency: str) -> list[HotelOffer]:
    if _looks_blocked(html):
        raise ValueError("blocked: captcha or access-denied page")

    doc = lxml_html.fromstring(html)
    cards = doc.cssselect(CARD_ROOT)
    offers: list[HotelOffer] = []
    for card in cards:
        offer = _parse_card(card, source_currency)
        if offer is not None:
            offers.append(offer)
    return offers


def _looks_blocked(html: str) -> bool:
    lower = html.lower()
    markers = ["captcha", "access denied", "unusual traffic", "are you a robot"]
    return any(m in lower for m in markers) and len(html) < 50_000


def _parse_card(card, source_currency: str):
    name = _text(card, CARD_NAME)
    link_el = card.cssselect(CARD_LINK)
    if not name or not link_el:
        return None
    booking_url = link_el[0].get("href", "")
    if not booking_url.startswith("https://"):
        booking_url = "https://www.booking.com" + booking_url

    rating_raw = _text(card, CARD_RATING) or ""
    rating = _parse_rating(rating_raw)

    rating_label = _text(card, CARD_RATING_LABEL) or ""

    price_amount = _parse_price(_text(card, CARD_PRICE))
    if price_amount is None:
        return None
    original_amount = _parse_price(_text(card, CARD_PRICE_ORIGINAL))

    photo_el = card.cssselect(CARD_PHOTO)
    photo_url = photo_el[0].get("src") if photo_el else None

    stars = len(card.cssselect(CARD_STARS))

    distance_text = _text(card, CARD_DISTANCE) or ""
    dist_match = _DISTANCE_RE.search(distance_text)
    distance_center = float(dist_match.group("km")) if dist_match else None

    amenities_text = (_text(card, CARD_AMENITIES) or "").lower()
    amenities = [
        key for key, keywords in AMENITY_KEYWORDS.items()
        if any(kw in amenities_text for kw in keywords)
    ]

    offer_id = hashlib.sha256(f"booking:{booking_url}".encode()).hexdigest()[:12]

    discount_pct = None
    if original_amount and price_amount and original_amount > price_amount:
        discount_pct = int(round((1 - price_amount / original_amount) * 100))

    return HotelOffer(
        offer_id=offer_id,
        hotel_name=name.strip(),
        stars=stars,
        rating=rating,
        rating_label=rating_label.strip(),
        price_per_night_usd=Decimal("0"),
        price_per_night_original=PriceOriginal(amount=price_amount, currency=source_currency),
        total_usd=Decimal("0"),
        discount_pct=discount_pct,
        original_price_usd=None,
        amenities=amenities,
        distance_to_center_km=distance_center,
        distance_to_beach_km=None,
        photo_url=photo_url,
        booking_url=booking_url,
    )


def _text(card, selector: str) -> str | None:
    els = card.cssselect(selector)
    if not els:
        return None
    return els[0].text_content().strip() or None


def _parse_rating(text: str) -> float:
    if not text:
        return 0.0
    m = _RATING_RE.search(text)
    if not m:
        return 0.0
    try:
        return float(m.group(0).replace(",", "."))
    except ValueError:
        return 0.0


def _parse_price(text: str | None) -> Decimal | None:
    if not text:
        return None
    m = _PRICE_RE.search(text)
    if not m:
        return None
    amount_str = m.group("amount").replace(" ", "").replace(",", "").strip(".")
    try:
        return Decimal(amount_str)
    except (ValueError, ArithmeticError):
        return None


def parse_details_html(html: str, offer_id: str) -> HotelDetails:
    doc = lxml_html.fromstring(html)

    name_el = doc.cssselect(DETAILS_NAME)
    name = name_el[0].text_content().strip() if name_el else ""

    desc_el = doc.cssselect(DETAILS_DESCRIPTION)
    description = desc_el[0].text_content().strip() if desc_el else ""

    amenities: list[str] = []
    seen: set[str] = set()
    for el in doc.cssselect(DETAILS_AMENITIES):
        t = el.text_content().strip()
        if t and t not in seen:
            seen.add(t)
            amenities.append(t)
        if len(amenities) >= 20:
            break

    photos: list[str] = []
    seen_urls: set[str] = set()
    for el in doc.cssselect(DETAILS_PHOTOS):
        src = el.get("src", "")
        if src.startswith("https://") and src not in seen_urls:
            seen_urls.add(src)
            photos.append(src)
        if len(photos) >= 10:
            break

    addr_el = doc.cssselect(DETAILS_ADDRESS)
    address = addr_el[0].text_content().strip() if addr_el else None

    return HotelDetails(
        offer_id=offer_id,
        hotel_name=name,
        description=description,
        amenities=amenities,
        room_types=[],
        cancellation_policy=None,
        photos=photos,
        address=address,
    )
