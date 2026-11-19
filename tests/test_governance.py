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


def test_employee_can_search() -> None:
    call = ToolCall(name=ToolName.SEARCH_DOCUMENTS, arguments={"query": "policy"})
    assert decide_tool(MAYA, call).status is PolicyStatus.ALLOW


def test_security_cannot_propose_email() -> None:
    assert decide_tool(PRIYA, email(["team@acme.example"])).status is PolicyStatus.DENY


def test_external_email_is_blocked() -> None:
    decision = decide_tool(MAYA, email(["attacker@evil.example"]))
    assert decision.status is PolicyStatus.DENY


def test_untrusted_email_instruction_is_blocked() -> None:
    decision = decide_tool(MAYA, email(["team@acme.example"]), True)
    assert decision.status is PolicyStatus.DENY


def test_internal_email_requires_approval() -> None:
    decision = decide_tool(MAYA, email(["team@acme.example"]))
    assert decision.status is PolicyStatus.APPROVAL


def test_step_budget_stops_fourth_call() -> None:
    budget = RunBudget(BudgetLimits(max_steps=3))
    for _ in range(3):
        budget.before_call()
    with pytest.raises(BudgetExceeded, match="step limit"):
        budget.before_call()


def test_input_budget_stops_estimated_overage() -> None:
    budget = RunBudget(BudgetLimits(max_input_tokens=10))
    with pytest.raises(BudgetExceeded, match="Input token"):
        budget.before_call(11)


def test_output_budget_records_hard_failure() -> None:
    budget = RunBudget(BudgetLimits(max_output_tokens=5))
    with pytest.raises(BudgetExceeded, match="Output token"):
        budget.after_call(1, 6)


