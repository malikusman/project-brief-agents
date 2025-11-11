"""Tests for brief generation endpoint."""

from uuid import uuid4

from fastapi.testclient import TestClient

from app.dependencies.mongo import get_database
from app.main import app
from app.services.agents_client import AgentsClient, get_agents_client


class StubAgentsClient(AgentsClient):
    def __init__(self, response: dict) -> None:
        self._response = response

    async def run_workflow(self, conversation, documents=None, thread_id=None) -> dict:
        self.last_conversation = list(conversation)  # type: ignore[attr-defined]
        self.last_documents = list(documents or [])  # type: ignore[attr-defined]
        return self._response


class StubCollection:
    def __init__(self) -> None:
        self.documents: list[dict] = []

    async def insert_one(self, document: dict) -> type:
        self.documents.append(document)

        class Result:
            inserted_id = uuid4()

        return Result()


class StubDatabase(dict):
    def __getitem__(self, item: str) -> StubCollection:
        if item not in self:
            self[item] = StubCollection()
        return super().__getitem__(item)


def test_run_brief_generation_endpoint_returns_brief(monkeypatch):
    response_payload = {
        "summary": {"project_title": "Test Project"},
        "brief": {"project_description": "Details"},
        "follow_up_questions": ["What is the timeline?"],
        "thread_id": "thread-123",
    }
    agents_stub = StubAgentsClient(response=response_payload)
    db_stub = StubDatabase()

    async def override_agents() -> AgentsClient:
        return agents_stub

    async def override_db():
        return db_stub

    app.dependency_overrides[get_agents_client] = override_agents
    app.dependency_overrides[get_database] = override_db

    client = TestClient(app)
    payload = {
        "prompt": "Launch a new app for remote teams to stay organized.",
        "documents": [{"id": "1", "name": "Discovery Doc"}],
    }
    resp = client.post("/api/briefs/run", json=payload)

    assert resp.status_code == 200
    data = resp.json()
    assert data["summary"] == response_payload["summary"]
    assert data["brief"] == response_payload["brief"]
    assert data["follow_up_questions"] == response_payload["follow_up_questions"]
    assert data["thread_id"] == response_payload["thread_id"]
    assert "run_id" in data

    stored_docs = db_stub["brief_runs"].documents
    assert stored_docs[0]["conversation"][0]["content"].startswith("Launch a new app")

    app.dependency_overrides.clear()

