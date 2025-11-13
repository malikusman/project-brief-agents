"""Tests for upload endpoint."""

from io import BytesIO
from tempfile import TemporaryDirectory

from fastapi.testclient import TestClient

from app.dependencies.mongo import get_database
from app.main import app
from app.core.config import get_settings


class StubCollection:
    def __init__(self) -> None:
        self.documents = []

    async def insert_one(self, document: dict) -> None:
        self.documents.append(document)


class StubDatabase(dict):
    def __getitem__(self, item: str) -> StubCollection:
        if item not in self:
            self[item] = StubCollection()
        return super().__getitem__(item)


def test_upload_document(monkeypatch):
    settings = get_settings()
    with TemporaryDirectory() as tmpdir:
        settings.uploads_dir = tmpdir
        stub_db = StubDatabase()

        async def override_db():
            return stub_db

        app.dependency_overrides[get_database] = override_db

        client = TestClient(app)
        response = client.post(
            "/api/uploads",
            files={"file": ("notes.txt", BytesIO(b"hello world"), "text/plain")},
        )
        assert response.status_code == 200
        data = response.json()["document"]
        assert data["name"] == "notes.txt"
        assert data["id"]
        assert "hello world" in stub_db["documents"].documents[0]["text"]

        app.dependency_overrides.clear()
