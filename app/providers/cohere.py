from typing import Any

import cohere

from app.config import settings
from app.providers.base import ChatResult, Citation, RerankItem


class CohereProvider:
    def __init__(self, api_key: str | None = None, client: Any = None) -> None:
