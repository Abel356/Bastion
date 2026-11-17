from app.domain.document import DocumentLabel
from app.domain.identity import Persona, Role
from app.retrieval import Chunk, authorized_candidates, retrieve

persona = Persona(id="maya", name="Maya", departments=frozenset({"Engineering"}), clearance=1, role=Role.EMPLOYEE)
def chunk(identifier: str, department: str, text: str) -> Chunk:
    label = DocumentLabel(id=identifier, department=department, clearance=1)
    return Chunk(id=identifier, text=text, label=label)
allowed = chunk("eng", "Engineering", "incident response policy")
restricted = chunk("fin", "Finance", "secret compensation canary")
