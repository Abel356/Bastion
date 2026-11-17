from app.domain.identity import Persona, Role
MAYA = Persona(id="maya", name="Maya Chen", departments=frozenset({"Engineering"}), clearance=1, role=Role.EMPLOYEE)
JONAH = Persona(id="jonah", name="Jonah Reed", departments=frozenset({"HR"}), clearance=2, role=Role.DEPARTMENT_LEAD)
PRIYA = Persona(id="priya", name="Priya Shah", departments=frozenset({"Security", "Engineering", "HR", "Finance"}), clearance=3, role=Role.SECURITY)
PERSONAS = {persona.id: persona for persona in (MAYA, JONAH, PRIYA)}
