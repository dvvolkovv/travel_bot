from decimal import Decimal
from pathlib import Path

import pytest

from scraper.booking_parse import parse_search_html
from scraper.types import HotelOffer

FIXTURES = Path(__file__).parent.parent / "fixtures"


def test_parse_barcelona_fixture_returns_enough_hotels() -> None:
    html = (FIXTURES / "barcelona.html").read_text()
    offers = parse_search_html(html, source_currency="EUR")
    assert len(offers) >= 15, f"Expected >=15 offers, got {len(offers)}"


def test_parse_barcelona_every_offer_has_required_fields() -> None:
    html = (FIXTURES / "barcelona.html").read_text()
    offers = parse_search_html(html, source_currency="EUR")
    assert len(offers) > 0
    for offer in offers:
        assert isinstance(offer, HotelOffer)
        assert offer.hotel_name, "hotel_name empty"
        assert offer.booking_url.startswith("https://"), f"bad URL: {offer.booking_url}"
        assert offer.price_per_night_original.amount > Decimal("0")
        assert 0 <= offer.rating <= 10


def test_parse_empty_html_returns_empty_list() -> None:
    offers = parse_search_html("<html><body>No results</body></html>", source_currency="USD")
    assert offers == []


def test_parse_html_with_captcha_raises() -> None:
    captcha_html = "<html><body>Please complete the captcha to continue</body></html>"
    with pytest.raises(ValueError, match="blocked"):
        parse_search_html(captcha_html, source_currency="EUR")
