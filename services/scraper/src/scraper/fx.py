from __future__ import annotations

from decimal import Decimal
from typing import Protocol

import httpx

FALLBACK_RATES: dict[str, float] = {
    "USD": 1.0,
    "EUR": 1.08,
    "GBP": 1.27,
    "RUB": 0.011,
    "TRY": 0.031,
    "AED": 0.27,
    "JPY": 0.0068,
    "THB": 0.028,
}

CACHE_TTL_SECONDS = 6 * 60 * 60


class RedisLike(Protocol):
    async def get(self, key: str) -> bytes | None: ...
    async def set(self, key: str, value: bytes, ex: int | None = None) -> None: ...


class FxConverter:
    def __init__(self, redis: RedisLike, api_key: str | None) -> None:
        self._redis = redis
        self._api_key = api_key

    async def to_usd(self, amount: Decimal, currency: str) -> Decimal:
        currency = currency.upper()
        if currency == "USD":
            return amount
        rate = await self._rate_to_usd(currency)
        return amount * Decimal(str(rate))

    async def _rate_to_usd(self, currency: str) -> float:
        cached = await self._redis.get(f"fx:{currency}")
        if cached is not None:
            return float(cached.decode())

        rate = await self._fetch_live(currency) or FALLBACK_RATES.get(currency)
        if rate is None:
            raise ValueError(f"unknown currency: {currency}")
        await self._redis.set(f"fx:{currency}", str(rate).encode(), ex=CACHE_TTL_SECONDS)
        return rate

    async def _fetch_live(self, currency: str) -> float | None:
        if not self._api_key:
            return None
        url = f"https://openexchangerates.org/api/latest.json?app_id={self._api_key}"
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                r = await client.get(url)
                r.raise_for_status()
                data = r.json()
                rate_usd_to_cur = data["rates"].get(currency)
                if rate_usd_to_cur:
                    return 1.0 / rate_usd_to_cur
        except (httpx.HTTPError, KeyError, ZeroDivisionError):
            return None
        return None
