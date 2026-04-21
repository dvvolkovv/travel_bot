from datetime import date
from decimal import Decimal
from unittest.mock import AsyncMock, patch

import pytest

from scraper.booking import build_search_url, search
from scraper.fx import FxConverter


class FakeRedis:
    async def get(self, key):
        return None

    async def set(self, key, value, ex=None):
        return None


def test_build_search_url_contains_destination_and_dates() -> None:
    url = build_search_url("Barcelona", date(2026, 6, 10), date(2026, 6, 15), 2, 0)
    assert "ss=Barcelona" in url
    assert "checkin=2026-06-10" in url
    assert "checkout=2026-06-15" in url
    assert "group_adults=2" in url


@pytest.mark.asyncio
async def test_search_falls_back_to_fixture_on_live_failure() -> None:
    fx = FxConverter(redis=FakeRedis(), api_key=None)

    with patch("scraper.booking._fetch_live", new=AsyncMock(side_effect=RuntimeError("blocked"))):
        result = await search(
            "Barcelona",
            date(2026, 6, 10),
            date(2026, 6, 15),
            fx=fx,
        )

    assert result.fallback_used is True
    assert len(result.warnings) >= 1
    assert len(result.offers) >= 1
    assert result.offers[0].price_per_night_usd > Decimal("0")


@pytest.mark.asyncio
async def test_search_applies_max_price_filter() -> None:
    fx = FxConverter(redis=FakeRedis(), api_key=None)

    with patch("scraper.booking._fetch_live", new=AsyncMock(side_effect=RuntimeError("blocked"))):
        result = await search(
            "Barcelona",
            date(2026, 6, 10),
            date(2026, 6, 15),
            max_price_per_night_usd=50,
            fx=fx,
        )

    assert all(o.price_per_night_usd <= Decimal("50") for o in result.offers)
