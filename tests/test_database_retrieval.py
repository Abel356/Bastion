from sqlalchemy.orm import Session

from app.models import ChunkRow, DocumentRow
from app.personas import MAYA
from app.repositories.documents import (
    authorized_chunk_statement,
    list_authorized_chunks,
    retrieve_authorized,
)


def add_document(
    session: Session, identifier: str, department: str, text: str,
    clearance: int = 1, active: bool = True
) -> str:
    document = DocumentRow(
        id=identifier, title=identifier, department=department,
        clearance=clearance, active=active, content=text
    )
    chunk = ChunkRow(id=f"{identifier}-0", document_id=identifier, ordinal=0, text=text)
    session.add_all([document, chunk])
    session.commit()
    return chunk.id


def test_statement_contains_acl_predicates() -> None:
    sql = str(authorized_chunk_statement(MAYA))
    assert "documents.active" in sql
    assert "documents.clearance" in sql
    assert "documents.department" in sql


def test_sql_filters_before_candidates(session: Session) -> None:
    allowed_id = add_document(session, "eng", "Engineering", "incident policy")
    company_id = add_document(session, "all", "Company", "holiday policy")
    add_document(session, "fin", "Finance", "compensation canary")
    add_document(session, "high", "Engineering", "restricted", clearance=2)
    add_document(session, "off", "Engineering", "revoked", active=False)
    ids = {chunk.id for chunk in list_authorized_chunks(session, MAYA)}
    assert ids == {allowed_id, company_id}


def test_restricted_query_cannot_promote_sql_row(session: Session) -> None:
    allowed_id = add_document(session, "eng", "Engineering", "incident policy")
    add_document(session, "fin", "Finance", "secret compensation canary")
    results = retrieve_authorized(session, MAYA, "secret compensation")
    assert [chunk.id for chunk in results] == [allowed_id]


def test_company_evidence_can_rank_first(session: Session) -> None:
    add_document(session, "eng", "Engineering", "office parking")
    company_id = add_document(session, "all", "Company", "remote work policy")
    results = retrieve_authorized(session, MAYA, "remote work")
    assert results[0].id == company_id
