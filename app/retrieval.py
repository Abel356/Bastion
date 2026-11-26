import re

from pydantic import BaseModel

from app.domain.document import DocumentLabel
from app.domain.identity import Persona
from app.domain.policy import can_read
from app.providers.base import InvalidRerankResponse, ModelProvider


class Chunk(BaseModel):
    id: str
    text: str
    label: DocumentLabel


def authorized_candidates(persona: Persona, chunks: list[Chunk]) -> list[Chunk]:
    return [chunk for chunk in chunks if can_read(persona, chunk.label)]


def lexical_score(query: str, chunk: Chunk) -> int:
    terms = set(re.findall(r"[a-z0-9]+", query.lower())) - {"a", "about", "are", "for", "is", "of", "on", "the", "to", "what"}
    return len(terms.intersection(re.findall(r"[a-z0-9]+", chunk.text.lower())))

def retrieve(persona: Persona, query: str, chunks: list[Chunk], limit: int = 4) -> list[Chunk]:
    candidates = authorized_candidates(persona, chunks)
    ranked = sorted(candidates, key=lambda chunk: lexical_score(query, chunk), reverse=True)
    return ranked[:limit]


def rerank_chunks(
    query: str, chunks: list[Chunk], provider: ModelProvider, limit: int
) -> list[Chunk]:
    requested = min(limit, len(chunks))
    if requested <= 0:
        return []
    rankings = provider.rerank(query, [chunk.text for chunk in chunks], requested)
    if not 1 <= len(rankings) <= requested:
        raise InvalidRerankResponse("Unexpected rerank result count")
    indices = [item.index for item in rankings]
    if any(type(index) is not int or not 0 <= index < len(chunks) for index in indices):
        raise InvalidRerankResponse("Invalid rerank index")
    if len(set(indices)) != len(indices):
        raise InvalidRerankResponse("Duplicate rerank index")
    return [chunks[index] for index in indices]
