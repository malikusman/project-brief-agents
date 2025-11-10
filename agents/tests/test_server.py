"""API tests for agents service."""

from fastapi.testclient import TestClient

from project_agents.server import app

client = TestClient(app)


def test_live_health() -> None:
    response = client.get("/health/live")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_workflow_endpoint_returns_summary() -> None:
    payload = {"prompt": "Build a productivity tool for designers."}
    response = client.post("/workflow/run", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "summary" in data
    assert "brief" in data

