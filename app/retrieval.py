from pydantic import BaseModel
from app.domain.document import DocumentLabel
class Chunk(BaseModel):
    id: str
    text: str
