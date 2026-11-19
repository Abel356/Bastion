from enum import StrEnum
from typing import Any

from pydantic import BaseModel, Field


class ToolName(StrEnum):
    SEARCH_DOCUMENTS = "search_documents"
    READ_DOCUMENT = "read_document"
    PROPOSE_EMAIL = "propose_email"


class ToolCall(BaseModel):
    name: ToolName
    arguments: dict[str, Any] = Field(default_factory=dict)


class ToolResult(BaseModel):
    name: ToolName
    status: str
    data: dict[str, Any] = Field(default_factory=dict)
    source_ids: list[str] = Field(default_factory=list)
    trust_level: str = "internal"
    requires_approval: bool = False


SEARCH_DOCUMENTS_SCHEMA = {
    "type": "function",
    "function": {
        "name": ToolName.SEARCH_DOCUMENTS.value,
        "description": "Search only documents authorized for the active persona.",
        "parameters": {
            "type": "object",
            "properties": {
                "query": {"type": "string", "minLength": 1},
            },
            "required": ["query"],
            "additionalProperties": False,
        },
    },
}


READ_DOCUMENT_SCHEMA = {
    "type": "function",
    "function": {
        "name": ToolName.READ_DOCUMENT.value,
        "description": "Read one authorized document by its stable identifier.",
        "parameters": {
            "type": "object",
