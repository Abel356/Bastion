from hashlib import sha256
from typing import Any

from app.providers.base import ChatResult, RerankItem


class LocalProvider:
    """Deterministic offline provider for tests and recorded demos."""

    def _embedding(self, text: str) -> list[float]:
        digest = sha256(text.encode("utf-8")).digest()
        return [byte / 255 for byte in digest]

    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        return [self._embedding(text) for text in texts]

    def embed_query(self, text: str) -> list[float]:
        return self._embedding(text)

    def rerank(
