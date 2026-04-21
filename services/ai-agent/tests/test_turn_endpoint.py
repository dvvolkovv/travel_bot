from fastapi.testclient import TestClient

from ai_agent.main import app


def test_turn_endpoint_exists() -> None:
    client = TestClient(app)
    r = client.post("/agent/turn", json={})
    # 422 = validation error (missing session_id/message)
    # 503 = anthropic not configured
    # 200 SSE stream = happy path (requires real anthropic creds, won't hit in tests)
    assert r.status_code in (422, 503)


def test_health_still_works() -> None:
    client = TestClient(app)
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json() == {"status": "ok", "service": "ai-agent"}
