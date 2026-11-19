from enum import StrEnum

from pydantic import BaseModel, Field

from app.governance.budget import BudgetUsage
from app.governance.tools import ToolResult
from app.providers.base import Citation


class RunStatus(StrEnum):
