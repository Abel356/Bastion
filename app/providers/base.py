from typing import Any, Protocol

from pydantic import BaseModel, Field


class RerankItem(BaseModel):
    index: int
    score: float


class Citation(BaseModel):
    start: int
    end: int
    text: str
    source_ids: list[str] = Field(default_factory=list)
