from typing import Any, Protocol

from pydantic import BaseModel, Field


class RerankItem(BaseModel):
    index: int
    score: float


