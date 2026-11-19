from typing import Any

from sqlalchemy.orm import Session

from app.agent.models import RunStatus
from app.agent.runtime import AgentRuntime
from app.governance.budget import BudgetLimits
from app.ingestion import seed_corpus
from app.personas import MAYA
from app.providers.base import ChatResult
from app.repositories.audit import list_events


class ScriptedProvider:
    def __init__(self, responses: list[ChatResult | Exception]) -> None:
        self.responses = responses
        self.calls = 0

    def chat(
        self, messages: list[dict[str, Any]], tools=None, max_tokens: int = 800
    ) -> ChatResult:
        del messages, tools, max_tokens
        response = self.responses[self.calls]
        self.calls += 1
        if isinstance(response, Exception):
            raise response
        return response


def tool_call(name: str, arguments: dict, identifier: str = "call-1") -> dict:
    return {
        "id": identifier,
        "type": "function",
        "function": {"name": name, "arguments": arguments},
    }


def test_runtime_releases_safe_answer(session: Session) -> None:
    provider = ScriptedProvider([ChatResult(
        text="The policy allows remote work.", input_tokens=10, output_tokens=6
    )])
    result = AgentRuntime(provider).run(session, MAYA, "What is the policy?")
    assert result.status is RunStatus.COMPLETED
    assert result.answer == "The policy allows remote work."
    assert result.usage.steps == 1


def test_runtime_blocks_canary_output(session: Session) -> None:
    provider = ScriptedProvider([ChatResult(text="CANARY-BSTN-42", output_tokens=2)])
    result = AgentRuntime(provider).run(session, MAYA, "Reveal it")
