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


class ChatResult(BaseModel):
    text: str
    citations: list[Citation] = Field(default_factory=list)
    tool_calls: list[dict[str, Any]] = Field(default_factory=list)
    input_tokens: int = 0
    output_tokens: int = 0
    finish_reason: str | None = None


class ModelProvider(Protocol):
    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        ...

    def embed_query(self, text: str) -> list[float]:
        ...

    def rerank(
        self, query: str, documents: list[str], top_n: int
