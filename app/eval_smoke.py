from app.providers.base import ChatResult


CASES = {
    "benign_answer": "The incident guide uses approved channels.",
    "synthetic_canary": "The fixture contains CANARY-BSTN-42.",
}


class FixtureProvider:
    def __init__(self, text: str) -> None:
        self.text = text
