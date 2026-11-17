from app.domain.document import DocumentLabel
from app.domain.identity import Persona, Role
from app.retrieval import Chunk, authorized_candidates, retrieve

persona = Persona(id="maya", name="Maya", departments=frozenset({"Engineering"}), clearance=1, role=Role.EMPLOYEE)
