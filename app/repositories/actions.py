from typing import Literal

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.governance.tools import ToolCall
from app.models import PendingActionRow

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


def reject_action(session: Session, action_id: str) -> PendingActionRow:
    action = session.get(PendingActionRow, action_id)
    if action is None:
        raise LookupError("Pending action not found")
    if action.status != "pending":
        raise ValueError("Action is no longer pending")
    action.status = "rejected"
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


def approve_action(session: Session, action_id: str) -> PendingActionRow:
    return review_action(session, action_id, "approved")


def review_action(
    session: Session, action_id: str, decision: ReviewDecision,
) -> PendingActionRow:
    action = session.get(PendingActionRow, action_id)
    if action is None:
        raise LookupError("Pending action not found")
    if action.status != "pending":
        raise ValueError("Action is no longer pending")
    action.status = decision
    session.commit()
    session.refresh(action)
    return action


