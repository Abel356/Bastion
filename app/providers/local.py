from hashlib import sha256
from typing import Any

from app.providers.base import ChatResult, RerankItem


class LocalProvider:
    """Deterministic offline provider for tests and recorded demos."""

    def _embedding(self, text: str) -> list[float]:
