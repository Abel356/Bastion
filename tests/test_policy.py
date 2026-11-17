from app.domain.document import DocumentLabel
from app.domain.identity import Persona, Role
from app.domain.policy import can_read

engineer = Persona(id="maya", name="Maya", departments=frozenset({"Engineering"}), clearance=1, role=Role.EMPLOYEE)
