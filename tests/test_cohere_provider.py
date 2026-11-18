from types import SimpleNamespace as NS

from app.providers.cohere import CohereProvider


class FakeClient:
    def __init__(self) -> None:
        self.last_embed: dict = {}
        self.last_rerank: dict = {}
        self.last_chat: dict = {}
