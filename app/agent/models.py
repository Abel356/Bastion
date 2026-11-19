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
