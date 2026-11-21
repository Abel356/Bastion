import pytest
from sqlalchemy import text
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, sessionmaker

from app.governance.executor import execute_tool
from app.governance.tools import ToolCall, ToolName
from app.ingestion import seed_corpus
from app.personas import MAYA
from app.repositories.actions import (
    create_pending_action,
    get_action,
    list_pending_actions,
    review_action,
)
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
    action_id = result.data["action_id"]
    session.execute(text("CREATE TEMP TRIGGER fail_audit BEFORE INSERT ON run_events "
                         "BEGIN SELECT RAISE(ABORT, 'audit unavailable'); END"))
    with pytest.raises(IntegrityError, match="audit unavailable"):
        review_action(session, action_id, "approved", "priya")
    assert [action.id for action in list_pending_actions(session)] == [action_id]
    assert list_events(session, run.id) == []
    session.execute(text("DROP TRIGGER fail_audit"))
    action = review_action(session, action_id, "approved", "priya")
    assert action.status == "approved"


def test_audit_events_are_ordered_and_run_finishes(session: Session) -> None:
    run = make_run(session)
    append_event(session, run.id, "request", {"text": "hello"})
    append_event(session, run.id, "policy", {"status": "allow"})
    events = list_events(session, run.id)
    assert [event.sequence for event in events] == [1, 2]
    finished = finish_run(session, run, "completed", 10, 4, 2)
    assert (finished.status, finished.step_count) == ("completed", 2)


def test_review_persists_with_audit_evidence(file_sessions: sessionmaker[Session]) -> None:
    call = ToolCall(name=ToolName.PROPOSE_EMAIL, arguments={
        "recipients": ["team@acme.example"], "subject": "Update", "body": "Hello"
    })
    with file_sessions() as session:
        run_id = make_run(session).id
        action_id = create_pending_action(session, run_id, call).id
    with file_sessions() as session:
        review_action(session, action_id, "approved", "priya")
    with file_sessions() as session:
        action = get_action(session, action_id)
        assert action is not None and action.status == "approved"
        assert len(list_events(session, run_id)) == 1
