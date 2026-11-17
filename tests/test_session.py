from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)
def test_lists_personas() -> None: assert len(client.get("/api/personas").json()) == 3
def test_selects_persona() -> None:
    response = client.post("/api/session/maya")
    assert response.status_code == 200
    assert response.cookies.get("bastion_session")
