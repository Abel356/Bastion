from collections.abc import Iterator
from unittest.mock import Mock

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

import app.api.chat as chat_api
from app.database import get_session
from app.governance.tools import ToolCall, ToolName
from app.ingestion import seed_corpus
from app.main import app
from app.personas import MAYA
from app.providers.base import RerankItem
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


def test_employee_cannot_request_baseline(api_client: TestClient) -> None:
    select(api_client, "maya")
    assert api_client.post("/api/chat", json={"message": "Hello", "mode": "baseline"}).status_code == 403
    select(api_client, "priya")
    assert api_client.post("/api/chat", json={"message": "Hello", "mode": "baseline"}).status_code == 403


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


@pytest.mark.parametrize(("query", "candidates", "quarantined", "selected"), [
    ("Code of conduct", 3, 1, ["company-code-of-conduct-1:0", "company-code-of-conduct-3:0"]),
    ("zxqvnomatch", 0, 0, []),
])
def test_offline_search_counts_are_visible_to_security(
    api_client: TestClient, session: Session, monkeypatch: pytest.MonkeyPatch,
    query: str, candidates: int, quarantined: int, selected: list[str],
) -> None:
    seed_corpus(session)
    monkeypatch.setattr(chat_api, "get_provider", LocalProvider)
    select(api_client, "maya")
    response = api_client.post("/api/chat", json={"message": query})
    assert response.status_code == 200
    run = response.json()
    assert "search_counts" not in run["tool_results"][0]
    url = f"/api/audit/runs/{run['run_id']}/events"
    assert api_client.get(url).status_code == 403
    select(api_client, "priya")
    timeline = api_client.get(url)
    assert timeline.status_code == 200
    [decision] = [event["payload"] for event in timeline.json() if event["event_type"] == "tool_decision"]
    assert decision == {
        "tool": "search_documents", "status": "completed", "requires_approval": False,
        "source_ids": selected, "authorized_candidate_count": candidates,
        "quarantined_count": quarantined, "rerank_candidate_count": 0,
        "context_passage_count": len(selected),
    }


def test_security_sees_malformed_rerank_fallback(
    api_client: TestClient, session: Session, monkeypatch: pytest.MonkeyPatch,
) -> None:
    seed_corpus(session)
    provider = Mock(wraps=LocalProvider(), uses_external_rerank=True)
    provider.rerank.return_value = [RerankItem(index=4, score=1)] * 2
    monkeypatch.setattr(chat_api, "get_provider", lambda: provider)
    select(api_client, "maya")
    response = api_client.post("/api/chat", json={"message": "code conduct compensation remote work"})
    assert response.status_code == 200
    run = response.json()
    assert run["status"] == "completed"
    provider.rerank.assert_called_once()
    _, candidates, requested = provider.rerank.call_args.args
    assert (len(candidates), requested) == (5, 4)
    selected = [
        "company-code-of-conduct-1:0", "company-code-of-conduct-3:0",
        "company-remote-work-1:0", "company-remote-work-2:0",
    ]
    assert run["tool_results"][0]["source_ids"] == selected
    assert "search_counts" not in run["tool_results"][0]
    assert run["citations"][0]["source_ids"] == selected[:1]
    url = f"/api/audit/runs/{run['run_id']}/events"
    assert api_client.get(url).status_code == 403
    select(api_client, "priya")
    timeline = api_client.get(url)
    assert timeline.status_code == 200
    [decision] = [event["payload"] for event in timeline.json() if event["event_type"] == "tool_decision"]
    assert decision == {
        "tool": "search_documents", "status": "completed", "requires_approval": False,
        "source_ids": selected, "authorized_candidate_count": 6,
        "quarantined_count": 1, "rerank_candidate_count": 5,
        "context_passage_count": 4, "rerank_fallback": True,
        "rerank_fallback_reason": "invalid_response",
    }


def pending_email(session: Session) -> str:
    run = start_run(session, MAYA.id, "Draft email")
    call = ToolCall(name=ToolName.PROPOSE_EMAIL, arguments={
        "recipients": ["team@acme.example"], "subject": "Hi", "body": "Update"
    })
    return create_pending_action(session, run.id, call).id


@pytest.mark.parametrize(("operation", "decision"), [("approve", "approved"), ("reject", "rejected")])
def test_security_can_review_action(
    api_client: TestClient, session: Session, operation: str, decision: str,
) -> None:
    action_id = pending_email(session)
    select(api_client, "priya")
    url = f"/api/actions/{action_id}/{operation}"
    response = api_client.post(url)
    assert response.status_code == 200
    assert response.json()["status"] == decision
    assert api_client.post(url).status_code == 409
    run_id = response.json()["run_id"]
    timeline = api_client.get(f"/api/audit/runs/{run_id}/events")
    assert timeline.status_code == 200
    [event] = timeline.json()
    assert event["event_type"] == "action_reviewed"
    assert event["payload"] == {"action_id": action_id, "reviewer_id": "priya", "decision": decision}


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
