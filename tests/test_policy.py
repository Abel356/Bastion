from app.domain.document import DocumentLabel
from app.domain.identity import Persona, Role
from app.domain.policy import can_read

engineer = Persona(id="maya", name="Maya", departments=frozenset({"Engineering"}), clearance=1, role=Role.EMPLOYEE)
def label(department: str, clearance: int = 1, active: bool = True) -> DocumentLabel:
    return DocumentLabel(id="doc", department=department, clearance=clearance, active=active)

def test_allows_department_document() -> None:
    assert can_read(engineer, label("Engineering"))
def test_allows_company_document() -> None:
    assert can_read(engineer, label("Company"))
def test_denies_other_department() -> None:
    assert not can_read(engineer, label("Finance"))
