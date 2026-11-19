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
