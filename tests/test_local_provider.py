from app.providers.local import LocalProvider


def test_local_embeddings_are_deterministic() -> None:
    provider = LocalProvider()
    first = provider.embed_documents(["policy"])[0]
    second = provider.embed_query("policy")
    assert first == second
    assert len(first) == 32


def test_local_rerank_orders_matching_text() -> None:
    provider = LocalProvider()
    results = provider.rerank(
        "incident response", ["parking guide", "incident response policy"], 2
    )
    assert [item.index for item in results] == [1, 0]


def test_local_chat_is_clearly_labeled() -> None:
    provider = LocalProvider()
    messages = [
        {"role": "system", "content": "You are Bastion."},
        {"role": "user", "content": "hello"},
    ]
    result = provider.chat(messages)
    assert result.text.startswith("Offline demo response:")
    assert result.finish_reason == "COMPLETE"
    assert result.input_tokens == len(str(messages).split())
