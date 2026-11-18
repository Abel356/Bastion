from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.ingestion import chunk_text, load_manifest, seed_corpus, seed_personas
from app.models import ChunkRow, DemoUserRow, DocumentRow
from app.personas import MAYA
from app.repositories.documents import list_authorized_chunks


def test_manifest_contains_sixty_documents() -> None:
    manifest = load_manifest()
    assert len(manifest) == 60
    assert len({item["department"] for item in manifest}) == 5


def test_manifest_labels_poisoned_documents() -> None:
    poisoned = [item for item in load_manifest() if item["contains_test_payload"]]
    assert len(poisoned) == 3
    assert all(item["trust_level"] == "external" for item in poisoned)


def test_chunk_text_preserves_content() -> None:
    text = "First paragraph.\n\nSecond paragraph."
    chunks = chunk_text(text, max_chars=20)
    assert chunks == ["First paragraph.", "Second paragraph."]


def test_seed_is_idempotent(session: Session) -> None:
    assert seed_personas(session) == 3
    assert seed_corpus(session) == 60
