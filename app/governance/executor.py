from typing import Any

from pydantic import ValidationError
from sqlalchemy.orm import Session

from app.domain.document import DocumentLabel, TrustLevel
from app.domain.identity import Persona
from app.domain.policy import can_read
from app.governance.policy import PolicyStatus, decide_tool
from app.governance.scanner import scan_untrusted
from app.governance.tools import ARGUMENT_MODELS, ToolCall, ToolName, ToolResult
from app.models import DocumentRow
from app.repositories.actions import create_pending_action
from app.repositories.documents import retrieve_authorized


def blocked(call: ToolCall, reason: str, status: str = "blocked") -> ToolResult:
    return ToolResult(name=call.name, status=status, data={"reason": reason})


def validate_arguments(call: ToolCall) -> dict[str, Any]:
    model = ARGUMENT_MODELS[call.name]
    validated = model.model_validate(call.arguments)
    return validated.model_dump()


def execute_tool(
    session: Session, persona: Persona, run_id: str, call: ToolCall,
    from_untrusted_content: bool = False,
) -> ToolResult:
    decision = decide_tool(persona, call, from_untrusted_content)
    if decision.status is PolicyStatus.DENY:
        return blocked(call, decision.reason)
    try:
        arguments = validate_arguments(call)
    except ValidationError as exc:
        return blocked(call, str(exc), status="invalid")
    if call.name is ToolName.SEARCH_DOCUMENTS:
        return search_documents(session, persona, arguments["query"])
    if call.name is ToolName.READ_DOCUMENT:
