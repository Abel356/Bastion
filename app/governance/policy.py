from enum import StrEnum

from pydantic import BaseModel

from app.domain.identity import Persona, Role
from app.governance.tools import ToolCall, ToolName

INTERNAL_DOMAIN = "@acme.example"


