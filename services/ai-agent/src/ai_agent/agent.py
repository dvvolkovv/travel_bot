from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any, AsyncIterator

import anthropic

from .system_prompt import build_system_prompt
from .tools import TOOLS, TOOL_HANDLERS

MAX_ITERATIONS = 5


@dataclass
class AgentEvent:
    type: str
    data: dict[str, Any]


async def run_turn(
    client: anthropic.AsyncAnthropic,
    model: str,
    user_message: str,
    history: list[dict],
    lang: str,
    currency: str,
    tool_context: dict[str, Any],
) -> AsyncIterator[AgentEvent]:
    messages = history + [{"role": "user", "content": user_message}]
    system = build_system_prompt(lang=lang, currency=currency)

    for iteration in range(MAX_ITERATIONS):
        yield AgentEvent("thinking", {"text": "analyzing" if iteration == 0 else "refining"})

        async with client.messages.stream(
            model=model,
            max_tokens=4096,
            messages=messages,
            tools=TOOLS,
            system=system,
        ) as stream:
            async for event in stream:
                et = getattr(event, "type", "")
                if et == "content_block_delta":
                    delta = getattr(event, "delta", None)
                    if delta is not None and getattr(delta, "type", "") == "text_delta":
                        yield AgentEvent("token", {"text": delta.text})
                elif et == "content_block_start":
                    block = getattr(event, "content_block", None)
                    if block is not None and getattr(block, "type", "") == "tool_use":
                        yield AgentEvent("tool_call", {"name": block.name, "input": {}})
            final = await stream.get_final_message()

        messages.append({"role": "assistant", "content": final.content})

        if final.stop_reason != "tool_use":
            yield AgentEvent("done", {"message_id": final.id})
            return

        tool_results = []
        for block in final.content:
            if getattr(block, "type", "") != "tool_use":
                continue
            handler = TOOL_HANDLERS.get(block.name)
            if handler is None:
                result: dict[str, Any] = {"error": f"unknown tool {block.name}"}
            else:
                try:
                    result = await handler(dict(block.input), **tool_context)
                except Exception as e:  # noqa: BLE001
                    result = {"error": f"{type(e).__name__}: {e}"}
            yield AgentEvent("tool_result", {
                "name": block.name,
                "summary": _summarize(block.name, result),
                "fallback_used": bool(result.get("fallback_used", False)),
            })
            if block.name == "search_hotels" and result.get("offers"):
                yield AgentEvent("cards", {"offers": result["offers"]})
            tool_results.append({
                "type": "tool_result",
                "tool_use_id": block.id,
                "content": json.dumps(result, default=str),
            })

        messages.append({"role": "user", "content": tool_results})

    yield AgentEvent("error", {"message": "max_iterations_reached"})


def _summarize(tool_name: str, result: dict[str, Any]) -> str:
    if "error" in result:
        return f"error: {result['error']}"
    if tool_name == "search_hotels":
        n = len(result.get("offers", []))
        total = result.get("total_found", 0)
        fb = " (cached)" if result.get("fallback_used") else ""
        return f"Found {total} hotels, top {n}{fb}"
    if tool_name == "get_hotel_details":
        return f"Loaded details for {result.get('hotel_name', 'hotel')}"
    return "done"
