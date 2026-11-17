from enum import StrEnum
from pydantic import BaseModel

class TrustLevel(StrEnum):
    INTERNAL = "internal"
