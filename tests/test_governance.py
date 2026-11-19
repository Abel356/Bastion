import pytest

from app.governance.budget import BudgetExceeded, BudgetLimits, RunBudget
from app.governance.policy import PolicyStatus, decide_tool
from app.governance.scanner import FindingType, scan_output, scan_untrusted
from app.governance.tools import ToolCall, ToolName
from app.personas import MAYA, PRIYA


def email(recipients: list[str]) -> ToolCall:
    return ToolCall(
        name=ToolName.PROPOSE_EMAIL,
        arguments={"recipients": recipients, "subject": "Update", "body": "Hello"},
    )

