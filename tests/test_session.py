from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)
def test_lists_personas() -> None: assert len(client.get("/api/personas").json()) == 3
