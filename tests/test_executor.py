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


