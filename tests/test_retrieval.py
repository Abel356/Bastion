from unittest.mock import Mock

import pytest

from app.domain.document import DocumentLabel
from app.domain.identity import Persona, Role
from app.providers.base import InvalidRerankResponse, RerankItem
from app.retrieval import Chunk, authorized_candidates, rerank_chunks, retrieve

persona = Persona(id="maya", name="Maya", departments=frozenset({"Engineering"}), clearance=1, role=Role.EMPLOYEE)
def chunk(identifier: str, department: str, text: str) -> Chunk:
    label = DocumentLabel(id=identifier, department=department, clearance=1)
    return Chunk(id=identifier, text=text, label=label)
allowed = chunk("eng", "Engineering", "incident response policy")
irrelevant = chunk("other", "Engineering", "office parking guide")
third = chunk("travel", "Engineering", "travel guide")
restricted = chunk("fin", "Finance", "secret compensation canary")


class ReverseReranker:
    def rerank(self, query: str, documents: list[str], top_n: int) -> list[RerankItem]:
        del query
        return [
            RerankItem(index=index, score=float(index))
            for index in reversed(range(len(documents)))
        ][:top_n]


def test_maps_provider_order_back_to_chunks() -> None:
    results = rerank_chunks(
        "policy", [allowed, irrelevant], ReverseReranker(), limit=2
    )
    assert [item.id for item in results] == ["other", "eng"]


@pytest.mark.parametrize("indices", [[], [-1], [3], [1, 1], [0, 1, 2]])
def test_rejects_invalid_rankings_before_mapping(indices: list[int]) -> None:
    provider = Mock()
    provider.rerank.return_value = [RerankItem(index=index, score=1) for index in indices]
    with pytest.raises(InvalidRerankResponse):
        rerank_chunks("policy", [allowed, irrelevant, third], provider, limit=2)


def test_rerank_accepts_a_shorter_valid_ranking() -> None:
    provider = Mock()
    provider.rerank.return_value = [RerankItem(index=2, score=1)]
    results = rerank_chunks("policy", [allowed, irrelevant, third], provider, limit=2)
    assert results == [third]


def test_rerank_skips_empty_candidates() -> None:
    provider = Mock()
    assert rerank_chunks("policy", [], provider, limit=2) == []
    provider.rerank.assert_not_called()


def test_filters_before_ranking() -> None:
    candidate_ids = {item.id for item in authorized_candidates(persona, [restricted, allowed])}
    assert candidate_ids == {"eng"}
def test_query_cannot_promote_restricted_chunk() -> None:
    results = retrieve(persona, "secret compensation", [allowed, restricted])
    assert [item.id for item in results] == ["eng"]
def test_ranks_authorized_evidence() -> None:
    results = retrieve(persona, "incident response", [irrelevant, allowed])
    assert results[0].id == "eng"
