from app.providers.local import LocalProvider


def test_local_embeddings_are_deterministic() -> None:
    provider = LocalProvider()
