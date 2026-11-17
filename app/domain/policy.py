from app.domain.document import DocumentLabel
from app.domain.identity import Persona


def can_read(persona: Persona, document: DocumentLabel) -> bool:
    department_allowed = document.department == "Company" or document.department in persona.departments
    return document.active and department_allowed and document.clearance <= persona.clearance
