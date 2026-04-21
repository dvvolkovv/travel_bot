from __future__ import annotations

import json
from typing import AsyncIterator

import asyncpg
import redis.asyncio as aioredis
from fastapi import FastAPI
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from scraper.fx import FxConverter
from scraper.proxy_pool import ProxyPool

from .agent import run_turn
from .config import Config
from .db import lookup_booking_url, persist_offers

app = FastAPI(title="ai-agent")

_config: Config | None = None
_pg_pool: asyncpg.Pool | None = None
_redis: aioredis.Redis | None = None
_anthropic = None  # type: ignore


@app.on_event("startup")
async def startup() -> None:
    global _config, _pg_pool, _redis, _anthropic
    _config = Config.from_env()
    if _config.database_url:
        _pg_pool = await asyncpg.create_pool(_config.database_url, min_size=1, max_size=5)
    _redis = aioredis.from_url(_config.redis_url)
    try:
        _anthropic = _config.make_anthropic_client()
    except RuntimeError:
        # No Anthropic credentials configured — /agent/turn will return 503.
        _anthropic = None


@app.on_event("shutdown")
async def shutdown() -> None:
    if _pg_pool:
        await _pg_pool.close()
    if _redis:
        await _redis.aclose()


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok", "service": "ai-agent"}


class TurnRequest(BaseModel):
    session_id: str
    message: str
    history: list[dict] = []
    lang: str = "en"
    currency: str = "USD"


@app.post("/agent/turn")
async def agent_turn(body: TurnRequest) -> StreamingResponse:
    if _anthropic is None or _config is None:
        return StreamingResponse(
            iter([b'event: error\ndata: {"message":"anthropic_not_configured"}\n\n']),
            media_type="text/event-stream",
            status_code=503,
        )

    async def generate() -> AsyncIterator[bytes]:
        assert _config is not None
        fx = FxConverter(redis=_redis, api_key=_config.openexchangerates_api_key)
        proxy_pool = ProxyPool.from_env("PROXY_URLS")

        async def persist(session_id: str, query_args: dict, offers: list) -> None:
            if _pg_pool is not None:
                await persist_offers(_pg_pool, session_id, query_args, offers)

        async def url_lookup(offer_id: str) -> str | None:
            if _pg_pool is None:
                return None
            return await lookup_booking_url(_pg_pool, offer_id)

        tool_context = {
            "fx": fx,
            "proxy_pool": proxy_pool,
            "persist": persist,
            "session_id": body.session_id,
            "lookup_url": url_lookup,
        }

        try:
            async for event in run_turn(
                client=_anthropic,
                model=_config.anthropic_model,
                user_message=body.message,
                history=body.history,
                lang=body.lang,
                currency=body.currency,
                tool_context=tool_context,
            ):
                payload = json.dumps(event.data)
                yield f"event: {event.type}\ndata: {payload}\n\n".encode()
        except Exception as e:  # noqa: BLE001
            err_payload = json.dumps({"message": str(e), "code": type(e).__name__})
            yield f"event: error\ndata: {err_payload}\n\n".encode()

    return StreamingResponse(generate(), media_type="text/event-stream")
