from typing import Any

import cohere
import httpx
from cohere.core.api_error import ApiError
from pydantic import ValidationError

from app.config import settings
from app.providers.base import (
    ChatResult,
    Citation,
    InvalidRerankResponse,
    RerankItem,
    RerankTimeout,
)


class CohereProvider:
    uses_external_rerank = True

    def __init__(self, api_key: str | None = None, client: Any = None) -> None:
        key = api_key or settings.cohere_api_key
        if client is None and not key:
            raise ValueError("COHERE_API_KEY is required for the Cohere provider")
        self.client = client or cohere.ClientV2(key)

    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        response = self.client.embed(
            model=settings.cohere_embed_model,
            input_type="search_document",
            texts=texts,
            embedding_types=["float"],
            output_dimension=1024,
        )
        if response.embeddings.float_ is None:
            raise RuntimeError("Cohere returned no float embeddings")
        return response.embeddings.float_

    def embed_query(self, text: str) -> list[float]:
        response = self.client.embed(
            model=settings.cohere_embed_model,
            input_type="search_query",
            texts=[text],
            embedding_types=["float"],
            output_dimension=1024,
        )
        if not response.embeddings.float_:
            raise RuntimeError("Cohere returned no query embedding")
        return response.embeddings.float_[0]

    def rerank(
        self, query: str, documents: list[str], top_n: int
    ) -> list[RerankItem]:
        try:
            response = self.client.with_raw_response.rerank(
                model=settings.cohere_rerank_model,
                query=query,
                documents=documents,
                top_n=top_n,
            )
            # The SDK can coerce fractional and boolean indices to integers.
            http_response = getattr(response, "response", None)
            if http_response is None:
                # Cohere 5.20 only exposes the underlying response via this attribute.
                http_response = response._response
            return [
                RerankItem(index=item["index"], score=item["relevance_score"])
                for item in http_response.json()["results"]
            ]
        except httpx.TimeoutException as exc:
            raise RerankTimeout("Cohere rerank timed out") from exc
        except ApiError as exc:
            if exc.status_code is None or not 200 <= exc.status_code < 300:
                raise
            raise InvalidRerankResponse("Malformed Cohere rerank response") from exc
        except (AttributeError, KeyError, TypeError, ValidationError) as exc:
            raise InvalidRerankResponse("Malformed Cohere rerank response") from exc

    def chat(
        self, messages: list[dict[str, Any]],
        tools: list[dict[str, Any]] | None = None,
        max_tokens: int = 800,
    ) -> ChatResult:
        response = self.client.chat(
            model=settings.cohere_chat_model,
            messages=messages,
            tools=tools,
            strict_tools=bool(tools),
            max_tokens=max_tokens,
            temperature=0.0,
        )
        content = response.message.content or []
        text = "".join(getattr(item, "text", "") for item in content)
        citations = [self._citation(item) for item in (response.message.citations or [])]
        tool_calls = [call.model_dump(mode="json") for call in (response.message.tool_calls or [])]
        tokens = response.usage.tokens if response.usage else None
        finish_reason = getattr(response.finish_reason, "value", response.finish_reason)
        return ChatResult(
            text=text, citations=citations, tool_calls=tool_calls,
            input_tokens=getattr(tokens, "input_tokens", 0),
            output_tokens=getattr(tokens, "output_tokens", 0),
            finish_reason=finish_reason,
        )

    @staticmethod
    def _citation(item: Any) -> Citation:
        source_ids = [getattr(source, "id", "") for source in item.sources]
        return Citation(
            start=item.start, end=item.end, text=item.text, source_ids=source_ids
        )
