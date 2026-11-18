"""Model provider interfaces and implementations."""

from app.config import settings
from app.providers.base import ModelProvider
from app.providers.cohere import CohereProvider
from app.providers.local import LocalProvider


def get_provider() -> ModelProvider:
    if settings.cohere_api_key:
        return CohereProvider()
