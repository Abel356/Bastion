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
