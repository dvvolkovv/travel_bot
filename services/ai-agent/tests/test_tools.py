from ai_agent.tools import TOOLS, TOOL_HANDLERS


def test_tools_registered() -> None:
    names = [t["name"] for t in TOOLS]
    assert "search_hotels" in names
    assert "get_hotel_details" in names


def test_search_hotels_schema_requires_destination() -> None:
    schema = next(t for t in TOOLS if t["name"] == "search_hotels")
    assert "destination" in schema["input_schema"]["required"]
    assert "checkin" in schema["input_schema"]["required"]
