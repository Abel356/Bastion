import json
from sqlalchemy.orm import Session
from app.agent.runtime import AgentRuntime
from app.database import Base, build_engine
from app.personas import MAYA
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


def compare(session: Session, name: str, text: str) -> dict[str, str]:
    runtime = AgentRuntime(FixtureProvider(text))
    return {mode: runtime.run(session, MAYA, name, mode).status.value for mode in ("baseline", "governed")}
