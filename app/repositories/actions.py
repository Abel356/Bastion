from sqlalchemy import select
from sqlalchemy.orm import Session

from app.governance.tools import ToolCall
from app.models import PendingActionRow


def create_pending_action(
    session: Session, run_id: str, call: ToolCall
) -> PendingActionRow:
