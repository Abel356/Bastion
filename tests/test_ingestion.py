from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.ingestion import chunk_text, load_manifest, seed_corpus, seed_personas
from app.models import ChunkRow, DemoUserRow, DocumentRow
from app.personas import MAYA
from app.repositories.documents import list_authorized_chunks


def test_manifest_contains_sixty_documents() -> None:
