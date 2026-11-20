from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)
def test_health() -> None: assert client.get("/health").json() == {"status": "ok"}


def test_runtime_reports_offline_provider(monkeypatch):
    monkeypatch.setattr("app.main.settings.cohere_api_key", None)
    assert client.get("/api/runtime").json() == {"provider": "offline"}
