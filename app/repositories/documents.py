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
        DocumentRow.active.is_(True),
        DocumentRow.clearance <= persona.clearance,
        or_(
            DocumentRow.department == "Company",
            DocumentRow.department.in_(departments),
        ),
    ).order_by(DocumentRow.id, ChunkRow.ordinal)


def row_to_chunk(chunk: ChunkRow, document: DocumentRow) -> Chunk:
    label = DocumentLabel(
        id=document.id,
        department=document.department,
        clearance=document.clearance,
        trust_level=TrustLevel(document.trust_level),
        active=document.active,
    )
    return Chunk(id=chunk.id, text=chunk.text, label=label)


def list_authorized_chunks(session: Session, persona: Persona) -> list[Chunk]:
    rows = session.execute(authorized_chunk_statement(persona)).all()
    return [row_to_chunk(chunk, document) for chunk, document in rows]


def retrieve_authorized(
    session: Session, persona: Persona, query: str, limit: int = 4
) -> list[Chunk]:
    chunks = list_authorized_chunks(session, persona)
    return retrieve(persona, query, chunks, limit)
