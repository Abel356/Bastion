from hashlib import sha256
from typing import Any

from app.providers.base import ChatResult, RerankItem, estimate_input_tokens
from app.providers.offline_chat import offline_evidence, offline_request


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
        self, query: str, documents: list[str], top_n: int
    ) -> list[RerankItem]:
        terms = set(query.lower().split())
        scored = [
            RerankItem(
                index=index,
                score=float(sum(term in document.lower() for term in terms)),
            )
            for index, document in enumerate(documents)
        ]
        return sorted(scored, key=lambda item: item.score, reverse=True)[:top_n]

    def chat(
        self, messages: list[dict[str, Any]],
        tools: list[dict[str, Any]] | None = None,
        max_tokens: int = 800,
    ) -> ChatResult:
        role = messages[-1].get("role") if messages else None
        latest = next(
            (message.get("content", "") for message in reversed(messages)), ""
        )
        if role == "tool":
            result = offline_evidence(latest, max_tokens)
        elif tools and role == "user" and str(latest).lower() not in {"hi", "hello"}:
            result = offline_request(latest)
        else:
            result = ChatResult(
                text=f"Offline demo response: {latest}",
                output_tokens=len(str(latest).split()) + 3,
                finish_reason="COMPLETE",
            )
        result.input_tokens = estimate_input_tokens(messages)
        return result
