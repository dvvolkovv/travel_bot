from pathlib import Path

from scraper.booking_parse import parse_details_html
from scraper.types import HotelDetails

FIXTURES = Path(__file__).parent.parent / "fixtures"


def test_parse_details_returns_populated_fields() -> None:
    html = (FIXTURES / "details_example.html").read_text()
    details = parse_details_html(html, offer_id="test123")
    assert isinstance(details, HotelDetails)
    assert details.hotel_name, "hotel_name empty"
    assert len(details.amenities) >= 3, f"need >=3 amenities, got {len(details.amenities)}"
    assert len(details.photos) >= 1, "no photos extracted"


def test_parse_details_empty_html_returns_empty_fields() -> None:
    details = parse_details_html("<html><body></body></html>", offer_id="empty")
    assert details.hotel_name == ""
    assert details.amenities == []
    assert details.photos == []
