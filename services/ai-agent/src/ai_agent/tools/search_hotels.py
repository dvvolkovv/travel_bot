from __future__ import annotations

from dataclasses import asdict
from datetime import date
from typing import Any, Awaitable, Callable

from scraper.booking import search as booking_search
from scraper.fx import FxConverter
from scraper.proxy_pool import ProxyPool
from scraper.types import HotelOffer

SEARCH_HOTELS_SCHEMA = {
    "name": "search_hotels",
    "description": (
        "Search hotels in a destination. Returns a list of ranked offers with prices, "
        "ratings, amenities, and discount info. Use this when the user asks for hotel options. "
        "Re-call this when the user refines the search (cheaper, closer to X, different dates)."
    ),
    "input_schema": {
        "type": "object",
        "required": ["destination", "checkin", "checkout"],
        "properties": {
            "destination": {"type": "string"},
            "checkin": {"type": "string", "format": "date"},
            "checkout": {"type": "string", "format": "date"},
            "guests_adults": {"type": "integer", "minimum": 1, "default": 2},
            "guests_children": {"type": "integer", "minimum": 0, "default": 0},
            "max_price_per_night_usd": {"type": "number"},
            "min_rating": {"type": "number"},
            "near": {"type": "string"},
            "must_have_amenities": {
                "type": "array",
                "items": {"enum": ["wifi", "pool", "breakfast", "parking", "gym", "pet_friendly"]},
            },
            "limit": {"type": "integer", "default": 5, "maximum": 10},
        },
    },
}


async def execute_search_hotels(
    args: dict[str, Any],
    *,
    fx: FxConverter,
    proxy_pool: ProxyPool,
    persist: Callable[[str, dict, list[HotelOffer]], Awaitable[None]],
    session_id: str,
    **_unused,
) -> dict[str, Any]:
    result = await booking_search(
        destination=args["destination"],
        checkin=date.fromisoformat(args["checkin"]),
        checkout=date.fromisoformat(args["checkout"]),
        adults=args.get("guests_adults", 2),
        children=args.get("guests_children", 0),
        max_price_per_night_usd=args.get("max_price_per_night_usd"),
        min_rating=args.get("min_rating"),
        must_have_amenities=args.get("must_have_amenities"),
        near=args.get("near"),
        limit=args.get("limit", 5),
        fx=fx,
        proxy_pool=proxy_pool,
    )

    await persist(session_id, args, result.offers)
    return {
        "offers": [_offer_to_dict(o) for o in result.offers],
        "total_found": result.total_found,
        "source": result.source,
        "fallback_used": result.fallback_used,
        "warnings": result.warnings,
    }


def _offer_to_dict(o: HotelOffer) -> dict[str, Any]:
    d = asdict(o)
    for k in ("price_per_night_usd", "total_usd", "original_price_usd"):
        if d.get(k) is not None:
            d[k] = float(d[k])
    d["price_per_night_original"]["amount"] = float(d["price_per_night_original"]["amount"])
    return d
