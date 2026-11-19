from collections.abc import Callable

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel

from app.api.dependencies import SecurityDependency, SessionDependency
from app.models import PendingActionRow
from app.repositories.actions import approve_action, list_pending_actions, reject_action

router = APIRouter(prefix="/api/actions", tags=["actions"])


class ActionView(BaseModel):
    id: str
    run_id: str
    kind: str
    status: str
    payload: dict

    @classmethod
    def from_row(cls, row: PendingActionRow) -> "ActionView":
        return cls(
            id=row.id, run_id=row.run_id, kind=row.kind,
            status=row.status, payload=row.payload
        )


def transition(
    action_id: str, session: SessionDependency,
    operation: Callable,
) -> ActionView:
    try:
        action = operation(session, action_id)
    except LookupError as exc:
        raise HTTPException(status.HTTP_404_NOT_FOUND, str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status.HTTP_409_CONFLICT, str(exc)) from exc
    return ActionView.from_row(action)


@router.get("", response_model=list[ActionView])
def pending_actions(
    session: SessionDependency, security: SecurityDependency
) -> list[ActionView]:
    del security
