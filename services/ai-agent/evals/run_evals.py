from __future__ import annotations

import asyncio
import sys
from dataclasses import dataclass
from pathlib import Path

import yaml

from ai_agent.agent import run_turn
from ai_agent.config import Config

CASES_DIR = Path(__file__).parent


@dataclass
class CaseResult:
    case_id: str
    passed: bool
    failures: list[str]


async def run_one(case: dict, client, model: str) -> CaseResult:
    events: list = []
    tool_context = _stub_tool_context()
    async for ev in run_turn(
        client=client, model=model,
        user_message=case["user_message"],
        history=case.get("history", []),
        lang=case["lang"], currency=case["currency"],
        tool_context=tool_context,
    ):
        events.append(ev)
    return _check(case, events)


def _check(case: dict, events) -> CaseResult:
    failures = []
    for assertion in case["assertions"]:
        if not _assertion_passes(assertion, events):
            failures.append(f"{assertion.get('type')}: {assertion}")
    return CaseResult(case_id=case["id"], passed=not failures, failures=failures)


def _assertion_passes(a: dict, events) -> bool:
    t = a.get("type")
    if t == "tool_called":
        return any(e.type == "tool_call" and e.data.get("name") == a.get("name") for e in events)
    if t == "tool_input_contains":
        return any(e.type == "tool_call" and e.data.get("name") == a.get("name") for e in events)
    if t == "has_cards_event":
        for e in events:
            if e.type == "cards" and len(e.data.get("offers", [])) >= a.get("min_offers", 1):
                return True
        return False
    if t == "response_contains_any":
        text = "".join(e.data.get("text", "") for e in events if e.type == "token")
        lower = text.lower()
        return any(v.lower() in lower for v in a.get("values", []))
    if t == "response_not_contains":
        text = "".join(e.data.get("text", "") for e in events if e.type == "token")
        lower = text.lower()
        return not any(v.lower() in lower for v in a.get("values", []))
    if t == "response_length_max_chars":
        text = "".join(e.data.get("text", "") for e in events if e.type == "token")
        return len(text) <= a.get("max", 10**9)
    return False


def _stub_tool_context():
    from scraper.fx import FxConverter
    from scraper.proxy_pool import ProxyPool

    class FakeRedis:
        async def get(self, k): return None
        async def set(self, k, v, ex=None): return None

    return {
        "fx": FxConverter(redis=FakeRedis(), api_key=None),
        "proxy_pool": ProxyPool(urls=[]),
        "persist": _noop_persist,
        "session_id": "eval",
        "lookup_url": _noop_lookup,
    }


async def _noop_persist(*_a, **_kw):
    return None


async def _noop_lookup(_offer_id: str):
    return None


async def main(lang: str = "en") -> int:
    config = Config.from_env()
    client = config.make_anthropic_client()
    cases_file = CASES_DIR / f"cases_{lang}.yaml"
    cases = yaml.safe_load(cases_file.read_text())

    results = []
    for c in cases:
        try:
            r = await run_one(c, client, config.anthropic_model)
        except Exception as e:  # noqa: BLE001
            r = CaseResult(case_id=c["id"], passed=False, failures=[f"exception: {e}"])
        results.append(r)
        print(f"{'PASS' if r.passed else 'FAIL'} {r.case_id}")
        for f in r.failures:
            print(f"    {f}")

    passed = sum(1 for r in results if r.passed)
    total = len(results)
    pass_rate = passed / total if total else 0
    threshold = 0.90 if lang == "en" else 0.85
    print(f"\n{lang}: {passed}/{total} passed ({pass_rate:.1%}, threshold {threshold:.0%})")
    return 0 if pass_rate >= threshold else 1


if __name__ == "__main__":
    lang = sys.argv[1] if len(sys.argv) > 1 else "en"
    sys.exit(asyncio.run(main(lang)))
