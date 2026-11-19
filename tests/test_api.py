from collections.abc import Iterator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

import app.api.chat as chat_api
from app.database import get_session
from app.governance.tools import ToolCall, ToolName
from app.main import app
from app.personas import MAYA
from app.providers.local import LocalProvider
from app.repositories.actions import create_pending_action
from app.repositories.audit import append_event, start_run


@pytest.fixture
def api_client(session: Session) -> Iterator[TestClient]:
    def override_session() -> Iterator[Session]:
        yield session

    app.dependency_overrides[get_session] = override_session
    client = TestClient(app)
    yield client
    app.dependency_overrides.clear()


def select(client: TestClient, persona_id: str) -> None:
    response = client.post(f"/api/session/{persona_id}")
    assert response.status_code == 200


def test_chat_requires_session(api_client: TestClient) -> None:
    response = api_client.post("/api/chat", json={"message": "Hello"})
    assert response.status_code == 401


def test_chat_runs_with_selected_persona(
    api_client: TestClient, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(chat_api, "get_provider", LocalProvider)
    select(api_client, "maya")
    response = api_client.post("/api/chat", json={"message": "Hello"})
    assert response.status_code == 200
    assert response.json()["status"] == "completed"
    assert response.json()["answer"].startswith("Offline demo response:")


def test_chat_validates_message_length(api_client: TestClient) -> None:
    select(api_client, "maya")
    response = api_client.post("/api/chat", json={"message": ""})
    assert response.status_code == 422


def test_employee_cannot_view_audit(api_client: TestClient) -> None:
    select(api_client, "maya")
    assert api_client.get("/api/audit/runs").status_code == 403


def test_security_can_view_runs(
    api_client: TestClient, session: Session
) -> None:
    start_run(session, MAYA.id, "Inspect me")
    select(api_client, "priya")
    response = api_client.get("/api/audit/runs")
    assert response.status_code == 200
    assert response.json()[0]["request"] == "Inspect me"


def test_security_can_view_ordered_events(
    api_client: TestClient, session: Session
) -> None:
    run = start_run(session, MAYA.id, "Inspect events")
    append_event(session, run.id, "first", {})
    append_event(session, run.id, "second", {})
    select(api_client, "priya")
    response = api_client.get(f"/api/audit/runs/{run.id}/events")
    assert [event["sequence"] for event in response.json()] == [1, 2]


def pending_email(session: Session) -> str:
    run = start_run(session, MAYA.id, "Draft email")
    call = ToolCall(name=ToolName.PROPOSE_EMAIL, arguments={
        "recipients": ["team@acme.example"], "subject": "Hi", "body": "Update"
    })
    return create_pending_action(session, run.id, call).id


def test_security_can_approve_action(
    api_client: TestClient, session: Session
) -> None:
    action_id = pending_email(session)
    select(api_client, "priya")
    response = api_client.post(f"/api/actions/{action_id}/approve")
    assert response.status_code == 200
    assert response.json()["status"] == "approved"


def test_employee_cannot_approve_action(
    api_client: TestClient, session: Session
) -> None:
    action_id = pending_email(session)
    select(api_client, "maya")
    response = api_client.post(f"/api/actions/{action_id}/approve")
    assert response.status_code == 403


def test_missing_action_returns_not_found(api_client: TestClient) -> None:
    select(api_client, "priya")
    response = api_client.post("/api/actions/missing/approve")
    assert response.status_code == 404
