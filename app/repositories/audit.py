from typing import Any

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models import AgentRunRow, RunEventRow


def start_run(
    session: Session, user_id: str, request: str,
    mode: str = "governed", model_id: str | None = None
) -> AgentRunRow:
    run = AgentRunRow(
        user_id=user_id, request=request, mode=mode, model_id=model_id
    )
    session.add(run)
    session.commit()
    session.refresh(run)
    return run


def append_event(
    session: Session, run_id: str, event_type: str, payload: dict[str, Any]
) -> RunEventRow:
    current = session.scalar(
