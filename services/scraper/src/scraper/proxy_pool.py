from __future__ import annotations

import itertools
import os
import time
from dataclasses import dataclass


@dataclass
class Proxy:
    url: str
    blocked_until: float = 0.0


class ProxyPool:
    """Round-robin pool. Blocked proxies cool down for N seconds."""

    def __init__(self, urls: list[str], cooldown_seconds: int = 600) -> None:
        self._proxies = [Proxy(url=u) for u in urls]
        self._cycle = itertools.cycle(self._proxies) if self._proxies else None
        self._cooldown = cooldown_seconds

    @classmethod
    def from_env(cls, env_var: str = "PROXY_URLS") -> "ProxyPool":
        raw = os.environ.get(env_var, "")
        urls = [u.strip() for u in raw.split(",") if u.strip()]
        return cls(urls=urls)

    def pick(self) -> Proxy | None:
        if not self._cycle:
            return None
        now = time.time()
        for _ in range(len(self._proxies)):
            candidate = next(self._cycle)
            if candidate.blocked_until <= now:
                return candidate
        return None

    def report_blocked(self, proxy: Proxy) -> None:
        proxy.blocked_until = time.time() + self._cooldown
