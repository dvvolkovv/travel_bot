from __future__ import annotations

import asyncio
import random
from datetime import date
from decimal import Decimal
from pathlib import Path
from urllib.parse import urlencode

from .booking_parse import parse_search_html
from .fx import FxConverter
from .proxy_pool import ProxyPool
from .types import HotelOffer, SearchResult

FIXTURES_DIR = Path(__file__).parent.parent.parent / "fixtures"
CONCURRENCY = asyncio.Semaphore(2)
NAV_TIMEOUT_MS = 30_000


def build_search_url(
    destination: str,
    checkin: date,
    checkout: date,
    adults: int,
    children: int,
) -> str:
    params = {
        "ss": destination,
        "checkin": checkin.isoformat(),
        "checkout": checkout.isoformat(),
        "group_adults": adults,
        "group_children": children,
        "no_rooms": 1,
    }
    return f"https://www.booking.com/searchresults.html?{urlencode(params)}"


async def search(
    destination: str,
    checkin: date,
    checkout: date,
    adults: int = 2,
    children: int = 0,
    max_price_per_night_usd: float | None = None,
    min_rating: float | None = None,
    must_have_amenities: list[str] | None = None,
    near: str | None = None,
    limit: int = 5,
    *,
    fx: FxConverter,
    proxy_pool: ProxyPool | None = None,
) -> SearchResult:
    warnings: list[str] = []
    fallback_used = False
    try:
        async with CONCURRENCY:
            html = await _fetch_live(destination, checkin, checkout, adults, children, proxy_pool)
            offers = parse_search_html(html, source_currency="EUR")
            if len(offers) == 0:
                raise RuntimeError("live fetch returned 0 offers")
    except Exception as e:
        warnings.append(f"live fetch failed: {type(e).__name__}: {e}")
        html = await _load_fixture(destination)
        offers = parse_search_html(html, source_currency="EUR") if html else []
        fallback_used = True

    offers = await _enrich_with_fx(offers, fx)
    nights = max((checkout - checkin).days, 1)
    for o in offers:
        o.total_usd = (o.price_per_night_usd * nights).quantize(Decimal("0.01"))
        if o.discount_pct:
            try:
                o.original_price_usd = (
                    o.price_per_night_usd
                    / (Decimal("1") - Decimal(o.discount_pct) / Decimal("100"))
                ).quantize(Decimal("0.01"))
            except (ZeroDivisionError, ArithmeticError):
                o.original_price_usd = None

    filtered = _apply_filters(offers, max_price_per_night_usd, min_rating, must_have_amenities)
    filtered.sort(key=_score_offer(near), reverse=True)

    return SearchResult(
        offers=filtered[:limit],
        total_found=len(offers),
        source="booking.com",
        fallback_used=fallback_used,
        warnings=warnings,
    )


async def _fetch_live(
    destination: str,
    checkin: date,
    checkout: date,
    adults: int,
    children: int,
    proxy_pool: ProxyPool | None,
) -> str:
    # Imports inside so tests that mock _fetch_live don't trigger Playwright bootstrap.
    from playwright.async_api import async_playwright
    try:
        from playwright_stealth import stealth_async  # type: ignore
    except ImportError:
        stealth_async = None  # type: ignore

    url = build_search_url(destination, checkin, checkout, adults, children)
    proxy = proxy_pool.pick() if proxy_pool else None
    proxy_arg = {"server": proxy.url} if proxy else None

    async with async_playwright() as pw:
        browser = await pw.chromium.launch(headless=True, proxy=proxy_arg)
        try:
            context = await browser.new_context(
                user_agent=_pick_ua(),
                viewport=_pick_viewport(),
                locale="en-US",
            )
            page = await context.new_page()
            if stealth_async is not None:
                await stealth_async(page)
            await page.goto(url, wait_until="networkidle", timeout=NAV_TIMEOUT_MS)
            try:
                await page.wait_for_selector('[data-testid="property-card"]', timeout=15_000)
            except Exception:
                pass  # page may be a block page — parse will detect
            await asyncio.sleep(random.uniform(1.0, 2.0))
            html = await page.content()
            return html
        finally:
            await browser.close()


async def _load_fixture(destination: str) -> str | None:
    slug = destination.lower().split(",")[0].strip().replace(" ", "_")
    candidate = FIXTURES_DIR / f"{slug}.html"
    if candidate.exists():
        return candidate.read_text()
    return None


async def _enrich_with_fx(offers: list[HotelOffer], fx: FxConverter) -> list[HotelOffer]:
    for o in offers:
        per_night_usd = await fx.to_usd(
            o.price_per_night_original.amount, o.price_per_night_original.currency
        )
        o.price_per_night_usd = per_night_usd.quantize(Decimal("0.01"))
    return offers


def _apply_filters(
    offers: list[HotelOffer],
    max_price: float | None,
    min_rating: float | None,
    amenities: list[str] | None,
) -> list[HotelOffer]:
    result = offers
    if max_price is not None:
        result = [o for o in result if o.price_per_night_usd <= Decimal(str(max_price))]
    if min_rating is not None:
        result = [o for o in result if o.rating >= min_rating]
    if amenities:
        result = [o for o in result if all(a in o.amenities for a in amenities)]
    return result


def _score_offer(near: str | None):
    def score(o: HotelOffer) -> float:
        s = float(o.rating or 0)
        if near == "beach" and o.distance_to_beach_km is not None:
            s += max(0.0, 3.0 - o.distance_to_beach_km)
        elif near == "center" and o.distance_to_center_km is not None:
            s += max(0.0, 3.0 - o.distance_to_center_km)
        if o.discount_pct:
            s += o.discount_pct * 0.05
        return s
    return score


_UAS = [
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Safari/605.1.15",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36",
]
_VIEWPORTS = [{"width": 1920, "height": 1080}, {"width": 1440, "height": 900}]


def _pick_ua() -> str:
    return random.choice(_UAS)


def _pick_viewport() -> dict:
    return random.choice(_VIEWPORTS)
