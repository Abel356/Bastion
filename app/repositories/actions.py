from sqlalchemy import select
from sqlalchemy.orm import Session

from app.governance.tools import ToolCall
from app.models import PendingActionRow


def create_pending_action(
    session: Session, run_id: str, call: ToolCall
) -> PendingActionRow:
    action = PendingActionRow(
        run_id=run_id, kind=call.name.value, payload=call.arguments
    )
    session.add(action)
    session.commit()
