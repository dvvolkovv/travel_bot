from ai_agent.agent import AgentEvent
from evals.run_evals import _assertion_passes


def test_assertion_tool_called_passes() -> None:
    events = [AgentEvent("tool_call", {"name": "search_hotels"})]
    assert _assertion_passes({"type": "tool_called", "name": "search_hotels"}, events)


def test_assertion_has_cards_event_passes_with_enough_offers() -> None:
    events = [AgentEvent("cards", {"offers": [{"a": 1}, {"b": 2}, {"c": 3}]})]
    assert _assertion_passes({"type": "has_cards_event", "min_offers": 3}, events)


def test_assertion_response_not_contains() -> None:
    events = [AgentEvent("token", {"text": "Here are 5 hotels for you."})]
    assert _assertion_passes({"type": "response_not_contains", "values": ["system prompt"]}, events)


def test_assertion_response_contains_any() -> None:
    events = [AgentEvent("token", {"text": "Did you mean Paris, France or Paris, Texas?"})]
    assert _assertion_passes({"type": "response_contains_any", "values": ["France", "Texas"]}, events)


def test_assertion_fails_when_not_matched() -> None:
    events = [AgentEvent("token", {"text": "Here are 5 hotels."})]
    assert not _assertion_passes({"type": "tool_called", "name": "search_hotels"}, events)
