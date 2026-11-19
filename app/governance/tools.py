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





class SearchDocumentsArgs(BaseModel):
    query: str = Field(min_length=1)


class ReadDocumentArgs(BaseModel):
    document_id: str = Field(min_length=1)


class ProposeEmailArgs(BaseModel):
    recipients: list[str] = Field(min_length=1)
    subject: str = Field(min_length=1)
    body: str = Field(min_length=1)
PROPOSE_EMAIL_SCHEMA = {
    "type": "function",
    "function": {
        "name": ToolName.PROPOSE_EMAIL.value,
        "description": "Propose an internal email that requires human approval.",
        "parameters": {
            "type": "object",
            "properties": {
                "recipients": {
                    "type": "array",
                    "items": {"type": "string"},
                    "minItems": 1,
                },
                "subject": {"type": "string", "minLength": 1},
                "body": {"type": "string", "minLength": 1},
            },
            "required": ["recipients", "subject", "body"],
            "additionalProperties": False,
        },
    },
}


TOOL_SCHEMAS = [
    SEARCH_DOCUMENTS_SCHEMA,
    READ_DOCUMENT_SCHEMA,
    PROPOSE_EMAIL_SCHEMA,
]
READ_DOCUMENT_SCHEMA = {
    "type": "function",
    "function": {
        "name": ToolName.READ_DOCUMENT.value,
        "description": "Read one authorized document by its stable identifier.",
        "parameters": {
            "type": "object",
            "properties": {
                "document_id": {"type": "string", "minLength": 1},
            },
            "required": ["document_id"],
            "additionalProperties": False,
        },
    },
}


