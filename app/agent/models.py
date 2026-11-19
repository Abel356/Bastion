from enum import StrEnum

from pydantic import BaseModel, Field

from app.governance.budget import BudgetUsage
from app.governance.tools import ToolResult
from app.providers.base import Citation


class RunStatus(StrEnum):
    COMPLETED = "completed"
    BLOCKED = "blocked"
    APPROVAL_REQUIRED = "approval_required"
    BUDGET_EXCEEDED = "budget_exceeded"
    FAILED = "failed"


class AgentRunResult(BaseModel):
    run_id: str
    status: RunStatus
    answer: str | None = None
    citations: list[Citation] = Field(default_factory=list)
    tool_results: list[ToolResult] = Field(default_factory=list)
    usage: BudgetUsage = Field(default_factory=BudgetUsage)
    blocked_reason: str | None = None

    @property
    def requires_approval(self) -> bool:
        return self.status is RunStatus.APPROVAL_REQUIRED
