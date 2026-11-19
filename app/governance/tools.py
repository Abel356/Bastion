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
