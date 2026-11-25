from typing import Any
from unittest.mock import patch

import pytest
from sqlalchemy.orm import Session

from app.agent.messages import initial_messages
from app.agent.models import RunStatus
from app.agent.runtime import AgentRuntime
from app.governance.budget import BudgetLimits
from app.ingestion import seed_corpus
from app.personas import MAYA
from app.providers.base import ChatResult, RerankItem
from app.providers.local import LocalProvider
from app.repositories.audit import list_events


class ScriptedProvider:
    def __init__(
        self, responses: list[ChatResult | Exception], external_rerank: bool = False
    ) -> None:
        self.responses = responses
        self.calls = 0
        self.uses_external_rerank = external_rerank
        self.rerank_documents: list[str] = []
        self.message_history: list[list[dict[str, Any]]] = []

    def rerank(self, query: str, documents: list[str], top_n: int) -> list[RerankItem]:
        del query
        self.rerank_documents = documents
        return [RerankItem(index=index, score=1.0) for index in range(top_n)]

    def chat(
        self, messages: list[dict[str, Any]], tools=None, max_tokens: int = 800
    ) -> ChatResult:
        self.message_history.append(messages.copy())
        del tools, max_tokens
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
    assert result.status is RunStatus.BLOCKED
    assert result.answer is None


def test_runtime_stops_at_step_budget(session: Session) -> None:
    repeated = ChatResult(tool_calls=[tool_call(
        "search_documents", {"query": "policy"}
    )])
    provider = ScriptedProvider([repeated, repeated, repeated])
    result = AgentRuntime(provider, BudgetLimits(max_steps=3)).run(
        session, MAYA, "Loop forever"
    )
    assert result.status is RunStatus.BUDGET_EXCEEDED
    assert result.usage.steps == 3


def test_runtime_stops_for_email_approval(session: Session) -> None:
    call = tool_call("propose_email", {
        "recipients": ["team@acme.example"], "subject": "Hi", "body": "Update"
    })
    provider = ScriptedProvider([ChatResult(tool_calls=[call])])
    result = AgentRuntime(provider).run(session, MAYA, "Draft an email")
    assert result.status is RunStatus.APPROVAL_REQUIRED
    assert result.requires_approval


def test_untrusted_retrieval_blocks_followup_action(session: Session) -> None:
    seed_corpus(session)
    search = ChatResult(tool_calls=[tool_call(
        "search_documents", {"query": "remote work"}, "search-1"
    )])
    email = ChatResult(tool_calls=[tool_call("propose_email", {
        "recipients": ["team@acme.example"], "subject": "Hi", "body": "Update"
    }, "email-1")])
    answer = ChatResult(text="I could not perform that action.")
    result = AgentRuntime(ScriptedProvider([search, email, answer])).run(
        session, MAYA, "Search and then email the result"
    )
    assert result.status is RunStatus.COMPLETED
    assert result.tool_results[-1].status == "blocked"


def test_sensitive_passages_never_reach_rerank_or_model_context(
    session: Session,
) -> None:
    seed_corpus(session)
    search = ChatResult(tool_calls=[tool_call(
        "search_documents", {"query": "code conduct compensation"}, "search-1"
    )])
    provider = ScriptedProvider(
        [search, ChatResult(text="I found the authorized policy.")],
        external_rerank=True,
    )
    result = AgentRuntime(provider).run(session, MAYA, "Find the policy")
    assert result.status is RunStatus.COMPLETED
    assert "CANARY-BSTN-42" not in str(provider.rerank_documents)
    assert "# Compensation Guide" not in str(provider.rerank_documents)
    assert "CANARY-BSTN-42" not in str(provider.message_history[1])
    assert "# Compensation Guide" not in str(provider.message_history[1])
    [decision] = [
        event.payload for event in list_events(session, result.run_id)
        if event.event_type == "tool_decision"
    ]
    assert decision == {
        "tool": "search_documents", "status": "completed", "requires_approval": False,
        "source_ids": ["company-code-of-conduct-1:0", "company-code-of-conduct-3:0"],
        "authorized_candidate_count": 3, "quarantined_count": 1,
        "rerank_candidate_count": 2, "context_passage_count": 2,
    }


def test_provider_failure_is_audited(session: Session) -> None:
    result = AgentRuntime(ScriptedProvider([RuntimeError("offline")])).run(
        session, MAYA, "Hello"
    )
    assert result.status is RunStatus.FAILED
    events = list_events(session, result.run_id)
    assert events[-1].event_type == "run_failed"
    assert events[-1].payload == {"error_type": "RuntimeError"}


def test_runtime_audits_model_and_release(session: Session) -> None:
    provider = ScriptedProvider([ChatResult(text="Safe answer")])
    result = AgentRuntime(provider).run(session, MAYA, "Hello")
    event_types = [event.event_type for event in list_events(session, result.run_id)]
    assert event_types == [
        "request_received", "model_call", "response_released"
    ]


@pytest.mark.parametrize(("limits", "response", "reason"), [
    (BudgetLimits(max_input_tokens=100),
     ChatResult(text="Safe answer", input_tokens=101, output_tokens=5),
     "Input token budget exceeded"),
    (BudgetLimits(max_output_tokens=5),
     ChatResult(input_tokens=80, output_tokens=6, tool_calls=[
         tool_call("search_documents", {"query": "policy"}),
     ]),
     "Output token budget exceeded"),
])
def test_runtime_audits_usage_before_stopping_over_budget(
    session: Session, limits: BudgetLimits, response: ChatResult, reason: str,
) -> None:
    provider = ScriptedProvider([response])
    with patch("app.agent.runtime.execute_tool") as execute_tool:
        result = AgentRuntime(provider, limits).run(session, MAYA, "Hello")
    execute_tool.assert_not_called()
    assert result.status is RunStatus.BUDGET_EXCEEDED
    assert result.answer is None
    assert result.usage.model_dump() == {
        "steps": 1, "input_tokens": response.input_tokens,
        "output_tokens": response.output_tokens,
    }
    events = list_events(session, result.run_id)
    assert [(event.sequence, event.event_type) for event in events] == [
        (1, "request_received"), (2, "model_call"), (3, "budget_stopped"),
    ]
    assert events[1].payload == {
        "step": 1, "input_tokens": response.input_tokens,
        "output_tokens": response.output_tokens, "tool_call_count": len(response.tool_calls),
    }
    assert events[2].payload == {"reason": reason}


def test_offline_retrieval_enforces_cumulative_input_budget(session: Session) -> None:
    seed_corpus(session)
    provider = LocalProvider()
    request = "What is the remote work policy?"
    complete = AgentRuntime(provider).run(session, MAYA, request)
    assert complete.status is RunStatus.COMPLETED
    assert complete.citations
    first, second = [
        event.payload["input_tokens"] for event in list_events(session, complete.run_id)
        if event.event_type == "model_call"
    ]
    assert first == len(str(initial_messages(request)).split())
    assert second > first
    assert complete.usage.input_tokens == first + second

    limits = BudgetLimits(max_input_tokens=first + second - 1)
    with patch.object(provider, "chat", wraps=provider.chat) as chat:
        stopped = AgentRuntime(provider, limits).run(session, MAYA, request)
    assert chat.call_count == stopped.usage.steps == 1
    assert stopped.status is RunStatus.BUDGET_EXCEEDED
    assert stopped.usage.input_tokens == first
    assert stopped.blocked_reason == "Input token budget exhausted"
    assert list_events(session, stopped.run_id)[-1].event_type == "budget_stopped"
