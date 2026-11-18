from sqlalchemy.orm import Session

from app.models import ChunkRow, DocumentRow
from app.personas import MAYA
from app.repositories.documents import authorized_chunk_statement, list_authorized_chunks, retrieve_authorized
