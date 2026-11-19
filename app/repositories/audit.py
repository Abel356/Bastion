from typing import Any

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models import AgentRunRow, RunEventRow


def start_run(
    session: Session, user_id: str, request: str,
