from pydantic import BaseModel
from app.domain.document import DocumentLabel
from app.domain.identity import Persona
from app.domain.policy import can_read
class Chunk(BaseModel):
    id: str
    text: str
    label: DocumentLabel
