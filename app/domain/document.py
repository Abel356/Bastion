from enum import StrEnum
from pydantic import BaseModel

class TrustLevel(StrEnum):
    INTERNAL = "internal"
    EXTERNAL = "external"
    QUARANTINED = "quarantined"

class DocumentLabel(BaseModel):
    id: str
    department: str
    clearance: int
    trust_level: TrustLevel = TrustLevel.INTERNAL
    active: bool = True
