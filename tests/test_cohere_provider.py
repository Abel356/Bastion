from types import SimpleNamespace as NS

from app.providers.cohere import CohereProvider


class FakeClient:
    def __init__(self) -> None:
        self.last_embed: dict = {}
        self.last_rerank: dict = {}
        self.last_chat: dict = {}

    def embed(self, **kwargs):
        self.last_embed = kwargs
        return NS(embeddings=NS(float_=[[0.1, 0.2]]))

    def rerank(self, **kwargs):
        self.last_rerank = kwargs
        results = [NS(index=1, relevance_score=0.9), NS(index=0, relevance_score=0.2)]
        return NS(results=results)

