from datetime import datetime

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel

from app.api.dependencies import SecurityDependency, SessionDependency
from app.models import AgentRunRow, RunEventRow
from app.repositories.audit import list_events, list_recent_runs

router = APIRouter(prefix="/api/audit", tags=["audit"])


class RunView(BaseModel):
    id: str
    user_id: str
    request: str
    status: str
    mode: str
    model_id: str | None
    input_tokens: int
    output_tokens: int
    step_count: int
    created_at: datetime

    @classmethod
    def from_row(cls, row: AgentRunRow) -> "RunView":
        return cls.model_validate(row, from_attributes=True)


class EventView(BaseModel):
    sequence: int
    event_type: str
    payload: dict
    created_at: datetime

    @classmethod
    def from_row(cls, row: RunEventRow) -> "EventView":
        return cls.model_validate(row, from_attributes=True)


@router.get("/runs", response_model=list[RunView])
def runs(
    session: SessionDependency, security: SecurityDependency
) -> list[RunView]:
    del security
    return [RunView.from_row(row) for row in list_recent_runs(session)]


@router.get("/runs/{run_id}/events", response_model=list[EventView])
def events(
    run_id: str, session: SessionDependency, security: SecurityDependency
) -> list[EventView]:
    del security
    rows = list_events(session, run_id)
    if not rows:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Run not found")
    return [EventView.from_row(row) for row in rows]
