from enum import StrEnum
from pydantic import BaseModel

class TrustLevel(StrEnum):
    INTERNAL = "internal"
    EXTERNAL = "external"
    QUARANTINED = "quarantined"

class DocumentLabel(BaseModel):
    id: str
