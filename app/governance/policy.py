from enum import StrEnum

from pydantic import BaseModel

from app.domain.identity import Persona, Role
from app.governance.tools import ToolCall, ToolName

INTERNAL_DOMAIN = "@acme.example"


class PolicyStatus(StrEnum):
    ALLOW = "allow"
    DENY = "deny"
    APPROVAL = "approval_required"

