from enum import StrEnum
from pydantic import BaseModel


class Role(StrEnum):
    EMPLOYEE = "employee"
    DEPARTMENT_LEAD = "department_lead"
    SECURITY = "security"

class Persona(BaseModel):
