import json
from types import SimpleNamespace as NS

import cohere
import httpx
import pytest
from cohere.core.api_error import ApiError

from app.providers.base import InvalidRerankResponse, RerankTimeout
from app.providers.cohere import CohereProvider


class FakeClient:
    def __init__(self) -> None:
        self.last_embed: dict = {}
        self.last_chat: dict = {}

    def embed(self, **kwargs):
        self.last_embed = kwargs
        return NS(embeddings=NS(float_=[[0.1, 0.2]]))

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
    def rerank(request: httpx.Request) -> httpx.Response:
        assert request.url.path == "/v2/rerank"
        assert json.loads(request.content)["top_n"] == 2
        return httpx.Response(200, json={"results": [
            {"index": 1, "relevance_score": 0.9},
            {"index": 0, "relevance_score": 0.2},
        ]})

    with httpx.Client(transport=httpx.MockTransport(rerank)) as http_client:
        client = cohere.ClientV2("fixture-key", httpx_client=http_client)
        results = CohereProvider(client=client).rerank("query", ["a", "b"], 2)
    assert [(item.index, item.score) for item in results] == [(1, 0.9), (0, 0.2)]


@pytest.mark.parametrize("body", [
    b'{"results":[{"index":true,"relevance_score":1}]}',
    b'{"results":[{"index":0.9,"relevance_score":1}]}',
    b'{"results":[{"index":"0","relevance_score":1}]}',
    b'{"results":[{"relevance_score":1}]}',
    b'{"results":[4]}',
    b'{"results":null}',
    b'null',
    b'not JSON',
])
def test_rerank_reports_malformed_success_response(body: bytes) -> None:
    transport = httpx.MockTransport(lambda request: httpx.Response(200, content=body))
    with httpx.Client(transport=transport) as http_client:
        client = cohere.ClientV2("fixture-key", httpx_client=http_client)
        with pytest.raises(InvalidRerankResponse, match="Malformed Cohere rerank response"):
            CohereProvider(client=client).rerank("query", ["a"], 1)


def test_rerank_preserves_http_failures() -> None:
    transport = httpx.MockTransport(lambda request: httpx.Response(401, json={}))
    with httpx.Client(transport=transport) as http_client:
        client = cohere.ClientV2("fixture-key", httpx_client=http_client)
        with pytest.raises(ApiError) as failure:
            CohereProvider(client=client).rerank("query", ["a"], 1)
        assert failure.value.status_code == 401


@pytest.mark.parametrize("status", [408, 504])
def test_rerank_reports_http_timeouts_without_retry(status: int) -> None:
    requests = []

    def timeout(request: httpx.Request) -> httpx.Response:
        requests.append(request)
        return httpx.Response(status, json={"message": "Request timed out"})

    with httpx.Client(transport=httpx.MockTransport(timeout)) as http_client:
        client = cohere.ClientV2("fixture-key", httpx_client=http_client)
        with pytest.raises(RerankTimeout, match="Cohere rerank timed out"):
            CohereProvider(client=client).rerank("query", ["a"], 1)
    assert len(requests) == 1


def test_chat_preserves_citations_and_usage() -> None:
    client = FakeClient()
    tools = [{"type": "function", "function": {"name": "search"}}]
    result = CohereProvider(client=client).chat([{"role": "user", "content": "hi"}], tools)
    assert result.text == "fact"
    assert result.citations[0].source_ids == ["doc-1"]
    assert (result.input_tokens, result.output_tokens) == (3, 1)
    assert client.last_chat["strict_tools"] is True
