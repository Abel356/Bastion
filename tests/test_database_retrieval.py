from sqlalchemy.orm import Session

from app.models import ChunkRow, DocumentRow
from app.personas import MAYA
from app.repositories.documents import authorized_chunk_statement, list_authorized_chunks, retrieve_authorized


def add_document(
    session: Session, identifier: str, department: str, text: str,
    clearance: int = 1, active: bool = True
) -> str:
    document = DocumentRow(
        id=identifier, title=identifier, department=department,
        clearance=clearance, active=active, content=text
    )
