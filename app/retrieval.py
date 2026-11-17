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
