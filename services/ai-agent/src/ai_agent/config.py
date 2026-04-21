from __future__ import annotations

import os
from dataclasses import dataclass

import anthropic


@dataclass(frozen=True)
class Config:
    anthropic_api_key: str | None
    anthropic_auth_token: str | None
    anthropic_model: str
    openexchangerates_api_key: str | None
    proxy_urls: str
    database_url: str
    redis_url: str
    booking_affiliate_id: str | None

    @classmethod
    def from_env(cls) -> "Config":
        return cls(
            anthropic_api_key=os.environ.get("ANTHROPIC_API_KEY") or None,
            anthropic_auth_token=os.environ.get("ANTHROPIC_AUTH_TOKEN") or None,
            anthropic_model=os.environ.get("ANTHROPIC_MODEL", "claude-sonnet-4-6"),
            openexchangerates_api_key=os.environ.get("OPENEXCHANGERATES_API_KEY") or None,
            proxy_urls=os.environ.get("PROXY_URLS", ""),
            database_url=os.environ.get("DATABASE_URL", ""),
            redis_url=os.environ.get("REDIS_URL", "redis://localhost:6379"),
            booking_affiliate_id=os.environ.get("BOOKING_AFFILIATE_ID") or None,
        )

    def make_anthropic_client(self) -> anthropic.AsyncAnthropic:
        """Create an Async Anthropic client using OAuth (auth_token) if available,
        else falling back to API key. This lets local/dev users plug in their
        Claude Code OAuth bearer token and production run with a long-lived API key.
        """
        if self.anthropic_auth_token:
            return anthropic.AsyncAnthropic(auth_token=self.anthropic_auth_token)
        if self.anthropic_api_key:
            return anthropic.AsyncAnthropic(api_key=self.anthropic_api_key)
        raise RuntimeError(
            "Anthropic client needs either ANTHROPIC_AUTH_TOKEN or ANTHROPIC_API_KEY",
        )
