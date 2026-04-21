from unittest.mock import MagicMock

import pytest

from ai_agent.agent import run_turn, AgentEvent


class FakeStream:
    def __init__(self, deltas: list, final_content: list, stop_reason: str, msg_id: str = "msg_1") -> None:
        self._deltas = deltas
        self._final = MagicMock(id=msg_id, content=final_content, stop_reason=stop_reason)

    async def __aenter__(self):
        return self

    async def __aexit__(self, *a):
        return None

    async def __aiter__(self):
        for d in self._deltas:
            yield d

    async def get_final_message(self):
        return self._final


def _text_delta(text: str):
    return MagicMock(type="content_block_delta", delta=MagicMock(type="text_delta", text=text))


@pytest.mark.asyncio
async def test_run_turn_emits_done_when_stop_reason_end_turn() -> None:
    client = MagicMock()
    client.messages.stream = MagicMock(return_value=FakeStream(
        deltas=[_text_delta("Hello.")],
        final_content=[MagicMock(type="text", text="Hello.")],
        stop_reason="end_turn",
    ))
    events: list[AgentEvent] = []
    async for ev in run_turn(
        client=client, model="test", user_message="hi",
        history=[], lang="en", currency="USD",
        tool_context={},
    ):
        events.append(ev)

    types = [e.type for e in events]
    assert "thinking" in types
    assert "token" in types
    assert types[-1] == "done"
