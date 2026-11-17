from pydantic import BaseModel

from app.domain.document import DocumentLabel
from app.domain.identity import Persona
from app.domain.policy import can_read


class Chunk(BaseModel):
    id: str
    text: str
    label: DocumentLabel


def authorized_candidates(persona: Persona, chunks: list[Chunk]) -> list[Chunk]:
    return [chunk for chunk in chunks if can_read(persona, chunk.label)]


def lexical_score(query: str, chunk: Chunk) -> int:
    return sum(term in chunk.text.lower() for term in set(query.lower().split()))

def retrieve(persona: Persona, query: str, chunks: list[Chunk], limit: int = 4) -> list[Chunk]:
    candidates = authorized_candidates(persona, chunks)
    ranked = sorted(candidates, key=lambda chunk: lexical_score(query, chunk), reverse=True)
    return ranked[:limit]
