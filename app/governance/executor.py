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
        return read_document(session, persona, arguments["document_id"])
    action = create_pending_action(session, run_id, call)
    return ToolResult(
        name=call.name, status=PolicyStatus.APPROVAL.value,
        data={"action_id": action.id}, requires_approval=True
    )


def search_documents(
    session: Session, persona: Persona, query: str
) -> ToolResult:
    chunks = retrieve_authorized(session, persona, query, limit=6)
    safe_chunks = []
    blocked_ids = []
    for chunk in chunks:
        scan = scan_untrusted(chunk.text)
        if scan.safe:
            safe_chunks.append(chunk)
        else:
            blocked_ids.append(chunk.id)
    data = {
        "results": [
            {"id": chunk.id, "text": chunk.text, "document_id": chunk.label.id}
            for chunk in safe_chunks
        ],
        "quarantined_ids": blocked_ids,
    }
    return ToolResult(
        name=ToolName.SEARCH_DOCUMENTS, status="completed", data=data,
        source_ids=[chunk.id for chunk in safe_chunks],
        trust_level="untrusted",
    )


def read_document(
    session: Session, persona: Persona, document_id: str
) -> ToolResult:
    document = session.get(DocumentRow, document_id)
    if document is None:
        return blocked(
            ToolCall(name=ToolName.READ_DOCUMENT), "Document is unavailable"
        )
    label = DocumentLabel(
        id=document.id, department=document.department,
        clearance=document.clearance,
        trust_level=TrustLevel(document.trust_level), active=document.active
    )
    if not can_read(persona, label):
        return blocked(
            ToolCall(name=ToolName.READ_DOCUMENT), "Document is unavailable"
        )
    scan = scan_untrusted(document.content)
    if not scan.safe:
        return blocked(
            ToolCall(name=ToolName.READ_DOCUMENT), "Document was quarantined"
        )
    return ToolResult(
        name=ToolName.READ_DOCUMENT, status="completed",
        data={"document_id": document.id, "content": document.content},
        source_ids=[document.id], trust_level=document.trust_level
    )
