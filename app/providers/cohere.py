from typing import Any

import cohere

from app.config import settings
from app.providers.base import ChatResult, Citation, RerankItem


class CohereProvider:
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
