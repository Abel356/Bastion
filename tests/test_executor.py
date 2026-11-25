import sqlite3
from concurrent.futures import ThreadPoolExecutor
from contextlib import closing
from pathlib import Path
from threading import Barrier

import pytest
from sqlalchemy import text
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, sessionmaker

from app import database
from app.governance.executor import execute_tool, search_documents
from app.governance.tools import ToolCall, ToolName
from app.ingestion import seed_corpus
from app.personas import MAYA
from app.providers.base import RerankItem
from app.repositories.actions import (
    ReviewDecision,
    create_pending_action,
    get_action,
    list_pending_actions,
    review_action,
)
from app.repositories.audit import append_event, finish_run, list_events, start_run


def make_run(session: Session):
    return start_run(session, MAYA.id, "test request")


class CapturingReranker:
    def __init__(self) -> None:
        self.documents: list[str] = []

    def rerank(self, query: str, documents: list[str], top_n: int) -> list[RerankItem]:
        del query
        self.documents = documents
        return [
            RerankItem(index=index, score=float(index))
            for index in reversed(range(len(documents)))
        ][:top_n]


def test_search_uses_provider_result_order(session: Session) -> None:
    seed_corpus(session)
    reranker = CapturingReranker()
    result = search_documents(session, MAYA, "remote work", reranker)
    texts = [item["text"] for item in result.data["results"]]
    assert texts == list(reversed(reranker.documents))[:4]


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


def test_fresh_sqlite_audit_events_are_append_only(file_sessions: sessionmaker[Session]) -> None:
    with file_sessions() as session:
        run_id = make_run(session).id
        append_event(session, run_id, "original", {"preserved": True})
        for statement in (
            "UPDATE run_events SET event_type = 'modified'",
            "DELETE FROM run_events",
            "REPLACE INTO run_events SELECT * FROM run_events",
        ):
            with pytest.raises(IntegrityError, match="Run events are append-only"):
                session.execute(text(statement))
            session.rollback()
        append_event(session, run_id, "next", {})
        assert [(event.sequence, event.event_type, event.payload) for event in list_events(session, run_id)] == [
            (1, "original", {"preserved": True}), (2, "next", {}),
        ]


def test_existing_sqlite_audit_log_is_guarded_on_startup(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch,
) -> None:
    path = tmp_path / "legacy.db"
    engine = database.build_engine(f"sqlite:///{path.as_posix()}")
    try:
        database.Base.metadata.create_all(engine)
        with Session(engine) as session:
            run_id = make_run(session).id
            original_id = append_event(session, run_id, "legacy", {"version": 1}).id
        monkeypatch.setattr(database, "engine", engine)
        database.create_schema()
        database.create_schema()

        with closing(sqlite3.connect(path)) as connection:
            for statement in ("UPDATE run_events SET sequence = 99", "DELETE FROM run_events"):
                with pytest.raises(sqlite3.IntegrityError, match="Run events are append-only"):
                    connection.execute(statement)

        with Session(engine) as session:
            append_event(session, run_id, "after_restart", {})
            original, latest = list_events(session, run_id)
            assert (original.id, original.sequence, original.event_type, original.payload) == (
                original_id, 1, "legacy", {"version": 1},
            )
            assert (latest.sequence, latest.event_type) == (2, "after_restart")
    finally:
        engine.dispose()


def review_from_session(file_sessions: sessionmaker[Session], action_id: str, decision: ReviewDecision) -> str:
    with file_sessions() as session:
        try:
            return review_action(session, action_id, decision, "priya").status
        except ValueError as exc:
            assert str(exc) == "Action is no longer pending"
            return "conflict"


def test_review_persists_with_audit_evidence(file_sessions: sessionmaker[Session]) -> None:
    call = ToolCall(name=ToolName.PROPOSE_EMAIL, arguments={
        "recipients": ["team@acme.example"], "subject": "Update", "body": "Hello"
    })
    with file_sessions() as session:
        run_id = make_run(session).id
        action_id = create_pending_action(session, run_id, call).id
    ready = Barrier(2)

    def compete(decision: ReviewDecision) -> str:
        ready.wait(timeout=5)
        return review_from_session(file_sessions, action_id, decision)

    with ThreadPoolExecutor(max_workers=2) as pool:
        outcomes = set(pool.map(compete, ("approved", "rejected")))
    assert "conflict" in outcomes
    [winner] = outcomes - {"conflict"}
    with file_sessions() as session:
        action = get_action(session, action_id)
        assert action is not None and action.status == winner
        assert len(list_events(session, run_id)) == 1
