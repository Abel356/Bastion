from app.providers.local import LocalProvider


def test_local_embeddings_are_deterministic() -> None:
    provider = LocalProvider()
    first = provider.embed_documents(["policy"])[0]
    second = provider.embed_query("policy")
    assert first == second
    assert len(first) == 32

