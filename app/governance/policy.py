from enum import StrEnum

from pydantic import BaseModel

from app.domain.identity import Persona, Role
from app.governance.tools import ToolCall, ToolName

INTERNAL_DOMAIN = "@acme.example"


class PolicyStatus(StrEnum):
    ALLOW = "allow"
    DENY = "deny"
    APPROVAL = "approval_required"


class PolicyDecision(BaseModel):
    status: PolicyStatus
    reason: str


ALLOWED_TOOLS = {
    Role.EMPLOYEE: {
        ToolName.SEARCH_DOCUMENTS, ToolName.READ_DOCUMENT, ToolName.PROPOSE_EMAIL
    },
    Role.DEPARTMENT_LEAD: {
        ToolName.SEARCH_DOCUMENTS, ToolName.READ_DOCUMENT, ToolName.PROPOSE_EMAIL
    },
    Role.SECURITY: {ToolName.SEARCH_DOCUMENTS, ToolName.READ_DOCUMENT},
}


def recipient_is_internal(recipient: str) -> bool:
    return recipient.lower().endswith(INTERNAL_DOMAIN)


def decide_tool(
    persona: Persona, call: ToolCall, from_untrusted_content: bool = False
) -> PolicyDecision:
    if call.name not in ALLOWED_TOOLS.get(persona.role, set()):
        return PolicyDecision(status=PolicyStatus.DENY, reason="Tool is not allowed for role")
    if call.name is not ToolName.PROPOSE_EMAIL:
        return PolicyDecision(status=PolicyStatus.ALLOW, reason="Role permits read-only tool")
    recipients = call.arguments.get("recipients", [])
    if not recipients or not all(isinstance(item, str) for item in recipients):
        return PolicyDecision(status=PolicyStatus.DENY, reason="Recipients are invalid")
    if not all(recipient_is_internal(item) for item in recipients):
        return PolicyDecision(status=PolicyStatus.DENY, reason="External recipients are blocked")
    if from_untrusted_content:
        return PolicyDecision(status=PolicyStatus.DENY, reason="Untrusted content requested action")
