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
        select(func.max(RunEventRow.sequence)).where(RunEventRow.run_id == run_id)
    )
    event = RunEventRow(
        run_id=run_id, sequence=(current or 0) + 1,
        event_type=event_type, payload=payload
    )
    session.add(event)
    session.commit()
    session.refresh(event)
    return event


def finish_run(
    session: Session, run: AgentRunRow, status: str,
    input_tokens: int, output_tokens: int, step_count: int
) -> AgentRunRow:
    run.status = status
    run.input_tokens = input_tokens
    run.output_tokens = output_tokens
    run.step_count = step_count
