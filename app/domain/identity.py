from enum import StrEnum
from pydantic import BaseModel

class Role(StrEnum):
    EMPLOYEE = "employee"
