from typing import Literal

from sqlalchemy import select, update
from sqlalchemy.orm import Session

from app.governance.tools import ToolCall
from app.models import PendingActionRow
from app.repositories.audit import stage_event

ReviewDecision = Literal["approved", "rejected"]


def create_pending_action(
    session: Session, run_id: str, call: ToolCall
) -> PendingActionRow:
    action = PendingActionRow(
        run_id=run_id, kind=call.name.value, payload=call.arguments
    )
    session.add(action)
    session.commit()
    session.refresh(action)
    return action


def list_pending_actions(session: Session) -> list[PendingActionRow]:
    statement = select(PendingActionRow).where(
        PendingActionRow.status == "pending"
    ).order_by(PendingActionRow.created_at)
    return list(session.scalars(statement))
def get_action(session: Session, action_id: str) -> PendingActionRow | None:
    return session.get(PendingActionRow, action_id)


def review_action(
    session: Session, action_id: str, decision: ReviewDecision, reviewer_id: str,
) -> PendingActionRow:
    try:
        statement = update(PendingActionRow).where(
            PendingActionRow.id == action_id, PendingActionRow.status == "pending"
        ).values(status=decision)
        updated = session.execute(statement).rowcount
        action = session.get(PendingActionRow, action_id)
        if action is None:
            raise LookupError("Pending action not found")
        if updated != 1:
            raise ValueError("Action is no longer pending")
        stage_event(
            session, action.run_id, "action_reviewed",
            {"action_id": action.id, "reviewer_id": reviewer_id, "decision": decision},
        )
        session.commit()
    except Exception:
        session.rollback()
        raise
    return action


