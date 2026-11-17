from app.domain.document import DocumentLabel
from app.domain.identity import Persona, Role
from app.retrieval import Chunk, authorized_candidates, retrieve

persona = Persona(id="maya", name="Maya", departments=frozenset({"Engineering"}), clearance=1, role=Role.EMPLOYEE)
def chunk(identifier: str, department: str, text: str) -> Chunk:
    label = DocumentLabel(id=identifier, department=department, clearance=1)
    return Chunk(id=identifier, text=text, label=label)
allowed = chunk("eng", "Engineering", "incident response policy")
irrelevant = chunk("other", "Engineering", "office parking guide")
restricted = chunk("fin", "Finance", "secret compensation canary")
def test_filters_before_ranking() -> None:
    candidate_ids = {item.id for item in authorized_candidates(persona, [restricted, allowed])}
    assert candidate_ids == {"eng"}
def test_query_cannot_promote_restricted_chunk() -> None:
    results = retrieve(persona, "secret compensation", [allowed, restricted])
    assert [item.id for item in results] == ["eng"]
def test_ranks_authorized_evidence() -> None:
    results = retrieve(persona, "incident response", [irrelevant, allowed])
    assert results[0].id == "eng"
