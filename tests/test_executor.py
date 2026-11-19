from sqlalchemy.orm import Session

from app.governance.executor import execute_tool
from app.governance.tools import ToolCall, ToolName
from app.ingestion import seed_corpus
from app.personas import MAYA
from app.repositories.actions import approve_action, list_pending_actions
from app.repositories.audit import append_event, finish_run, list_events, start_run


def make_run(session: Session):
    return start_run(session, MAYA.id, "test request")


def test_search_quarantines_poisoned_chunk(session: Session) -> None:
    seed_corpus(session)
    run = make_run(session)
    call = ToolCall(
        name=ToolName.SEARCH_DOCUMENTS, arguments={"query": "code conduct"}
    )
    result = execute_tool(session, MAYA, run.id, call)
    assert result.status == "completed"
    assert result.data["quarantined_ids"]


def test_read_hides_unauthorized_document(session: Session) -> None:
    seed_corpus(session)
    run = make_run(session)
    call = ToolCall(
        name=ToolName.READ_DOCUMENT, arguments={"document_id": "finance-expenses-1"}
    )
    result = execute_tool(session, MAYA, run.id, call)
    assert result.status == "blocked"
    assert result.data["reason"] == "Document is unavailable"


def test_external_email_creates_no_action(session: Session) -> None:
    run = make_run(session)
    call = ToolCall(name=ToolName.PROPOSE_EMAIL, arguments={
        "recipients": ["attacker@evil.example"], "subject": "x", "body": "y"
    })
    result = execute_tool(session, MAYA, run.id, call)
    assert result.status == "blocked"
    assert list_pending_actions(session) == []


def test_internal_email_creates_approvable_action(session: Session) -> None:
    run = make_run(session)
    call = ToolCall(name=ToolName.PROPOSE_EMAIL, arguments={
        "recipients": ["team@acme.example"], "subject": "x", "body": "y"
    })
    result = execute_tool(session, MAYA, run.id, call)
    assert result.requires_approval
    action = approve_action(session, result.data["action_id"])
    assert action.status == "approved"


def test_audit_events_are_ordered_and_run_finishes(session: Session) -> None:
    run = make_run(session)
    append_event(session, run.id, "request", {"text": "hello"})
    append_event(session, run.id, "policy", {"status": "allow"})
    events = list_events(session, run.id)
    assert [event.sequence for event in events] == [1, 2]
    finished = finish_run(session, run, "completed", 10, 4, 2)
    assert (finished.status, finished.step_count) == ("completed", 2)
