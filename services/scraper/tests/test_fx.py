from decimal import Decimal

import pytest

from scraper.fx import FxConverter, FALLBACK_RATES


class FakeRedis:
    def __init__(self) -> None:
        self.store: dict[str, bytes] = {}

    async def get(self, key: str) -> bytes | None:
        return self.store.get(key)

    async def set(self, key: str, value: bytes, ex: int | None = None) -> None:
        self.store[key] = value


@pytest.mark.asyncio
async def test_convert_usd_to_usd_is_identity() -> None:
    fx = FxConverter(redis=FakeRedis(), api_key=None)
    result = await fx.to_usd(Decimal("100"), "USD")
    assert result == Decimal("100")


@pytest.mark.asyncio
async def test_convert_eur_to_usd_uses_fallback_when_no_api_key() -> None:
    fx = FxConverter(redis=FakeRedis(), api_key=None)
    result = await fx.to_usd(Decimal("100"), "EUR")
    expected = Decimal("100") * Decimal(str(FALLBACK_RATES["EUR"]))
    assert result == expected


@pytest.mark.asyncio
async def test_convert_rub_to_usd() -> None:
    fx = FxConverter(redis=FakeRedis(), api_key=None)
    result = await fx.to_usd(Decimal("5000"), "RUB")
    expected = Decimal("5000") * Decimal(str(FALLBACK_RATES["RUB"]))
    assert result == expected


@pytest.mark.asyncio
async def test_unknown_currency_raises() -> None:
    fx = FxConverter(redis=FakeRedis(), api_key=None)
    with pytest.raises(ValueError, match="unknown currency"):
        await fx.to_usd(Decimal("1"), "XYZ")
