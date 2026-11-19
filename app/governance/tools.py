from enum import StrEnum
from typing import Any

from pydantic import BaseModel, Field


class ToolName(StrEnum):
    SEARCH_DOCUMENTS = "search_documents"
    READ_DOCUMENT = "read_document"
    PROPOSE_EMAIL = "propose_email"
