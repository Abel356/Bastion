from sqlalchemy import Select, or_, select
from sqlalchemy.orm import Session

from app.domain.document import DocumentLabel, TrustLevel
from app.domain.identity import Persona
from app.models import ChunkRow, DocumentRow
from app.retrieval import Chunk, retrieve


def authorized_chunk_statement(persona: Persona) -> Select:
    departments = tuple(persona.departments)
    statement = select(ChunkRow, DocumentRow).join(
        DocumentRow, ChunkRow.document_id == DocumentRow.id
    )
    return statement.where(
