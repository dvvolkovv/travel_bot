from __future__ import annotations

import json
from typing import Any

import asyncpg

from scraper.types import HotelOffer

INSERT_OFFER_SQL = """
INSERT INTO offer_snapshot
  (id, "sessionId", source, "hotelId", "hotelName", checkin, checkout, guests,
   "priceUsd", "priceOrig", "bookingUrl", "rawJson")
VALUES ($1,$2,$3,$4,$5,$6,$7,$8,$9,$10,$11,$12)
ON CONFLICT (id) DO NOTHING;
"""


async def persist_offers(
    pool: asyncpg.Pool,
    session_id: str,
    query_args: dict[str, Any],
    offers: list[HotelOffer],
) -> None:
    if not offers:
        return
    rows = []
    for o in offers:
        rows.append((
            o.offer_id,
            session_id,
            "booking.com",
            o.offer_id,
            o.hotel_name,
            query_args["checkin"],
            query_args["checkout"],
            query_args.get("guests_adults", 2),
            float(o.price_per_night_usd),
            json.dumps({
                "amount": float(o.price_per_night_original.amount),
                "currency": o.price_per_night_original.currency,
            }),
            o.booking_url,
            json.dumps({"offer_id": o.offer_id, "hotel_name": o.hotel_name}),
        ))

    async with pool.acquire() as conn:
        await conn.executemany(INSERT_OFFER_SQL, rows)


async def lookup_booking_url(pool: asyncpg.Pool, offer_id: str) -> str | None:
    async with pool.acquire() as conn:
        row = await conn.fetchrow('SELECT "bookingUrl" FROM offer_snapshot WHERE id = $1', offer_id)
        return row["bookingUrl"] if row else None
