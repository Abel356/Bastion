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

    def chat(self, **kwargs):
        self.last_chat = kwargs
        citation = NS(start=0, end=4, text="fact", sources=[NS(id="doc-1")])
        message = NS(content=[NS(text="fact")], citations=[citation], tool_calls=[])
        usage = NS(tokens=NS(input_tokens=3, output_tokens=1))
        return NS(message=message, usage=usage, finish_reason="COMPLETE")


def test_document_embeddings_use_search_document() -> None:
    client = FakeClient()
    result = CohereProvider(client=client).embed_documents(["policy"])
    assert result == [[0.1, 0.2]]
    assert client.last_embed["input_type"] == "search_document"


def test_query_embeddings_use_search_query() -> None:
    client = FakeClient()
    result = CohereProvider(client=client).embed_query("policy")
    assert result == [0.1, 0.2]
    assert client.last_embed["input_type"] == "search_query"


def test_rerank_maps_scores_and_indexes() -> None:
    client = FakeClient()
    results = CohereProvider(client=client).rerank("query", ["a", "b"], 2)
    assert [(item.index, item.score) for item in results] == [(1, 0.9), (0, 0.2)]
    assert client.last_rerank["top_n"] == 2


def test_chat_preserves_citations_and_usage() -> None:
    client = FakeClient()
    tools = [{"type": "function", "function": {"name": "search"}}]
    result = CohereProvider(client=client).chat([{"role": "user", "content": "hi"}], tools)
    assert result.text == "fact"
    assert result.citations[0].source_ids == ["doc-1"]
