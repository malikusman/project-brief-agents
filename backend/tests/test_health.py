"""Health endpoint tests."""

from fastapi.testclient import TestClient

from app.main import create_app

client = TestClient(create_app())


def test_live_endpoint_returns_ok() -> None:
    """The live endpoint should indicate service health."""

    response = client.get("/api/health/live")
    assert response.status_code == 200
    payload = response.json()
    assert payload["status"] == "ok"
    assert "app" in payload


def test_ready_endpoint_returns_ready() -> None:
    """The readiness endpoint should respond with ready status."""

    response = client.get("/api/health/ready")
    assert response.status_code == 200
    assert response.json() == {"status": "ready"}


