from __future__ import annotations

from dataclasses import asdict
from typing import Any, Awaitable, Callable

from scraper.proxy_pool import ProxyPool

# Task 6 (parallel) is adding `get_details` to scraper.booking. Until it lands,
# we degrade gracefully so this module still imports and the agent keeps
# functioning for `search_hotels`. Once Task 6 merges, this import will resolve
# and the handler will start returning real details.
try:
    from scraper.booking import get_details as booking_get_details  # type: ignore
except ImportError:  # pragma: no cover — transient until Task 6 merges
    booking_get_details = None  # type: ignore

GET_HOTEL_DETAILS_SCHEMA = {
    "name": "get_hotel_details",
    "description": (
        "Fetch additional details for a specific hotel (description, full amenities, photos, address). "
        "Use when user asks specific questions about a hotel from the search results."
    ),
    "input_schema": {
        "type": "object",
        "required": ["offer_id"],
        "properties": {"offer_id": {"type": "string"}},
    },
}


async def execute_get_hotel_details(
    args: dict[str, Any],
    *,
    lookup_url: Callable[[str], Awaitable[str | None]],
    proxy_pool: ProxyPool,
    **_unused,
) -> dict[str, Any]:
    offer_id = args["offer_id"]
    if booking_get_details is None:
        return {"error": "get_details not yet implemented", "offer_id": offer_id}
    booking_url = await lookup_url(offer_id)
    if not booking_url:
        return {"error": "offer not found", "offer_id": offer_id}
    details = await booking_get_details(booking_url, offer_id=offer_id, proxy_pool=proxy_pool)
    return asdict(details)
