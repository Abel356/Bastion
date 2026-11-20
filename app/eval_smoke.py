from app.providers.base import ChatResult


CASES = {
    "benign_answer": "The incident guide uses approved channels.",
    "synthetic_canary": "The fixture contains CANARY-BSTN-42.",
}


class FixtureProvider:
    def __init__(self, text: str) -> None:
        self.text = text

    def chat(self, messages, tools=None, max_tokens: int = 800) -> ChatResult:
        return ChatResult(text=self.text, output_tokens=len(self.text.split()))
