from typing import Any

from sqlalchemy.orm import Session

from app.agent.models import RunStatus
from app.agent.runtime import AgentRuntime
from app.governance.budget import BudgetLimits
from app.ingestion import seed_corpus
from app.personas import MAYA
from app.providers.base import ChatResult
from app.repositories.audit import list_events


class ScriptedProvider:
    def __init__(self, responses: list[ChatResult | Exception]) -> None:
