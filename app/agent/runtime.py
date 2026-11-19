from typing import Any

from sqlalchemy.orm import Session

from app.agent.messages import (
    assistant_message,
    initial_messages,
    parse_tool_call,
    tool_message,
)
from app.agent.models import AgentRunResult, RunStatus
from app.domain.identity import Persona
from app.governance.budget import BudgetExceeded, BudgetLimits, RunBudget
from app.governance.executor import execute_tool
from app.governance.scanner import scan_output
from app.governance.tools import TOOL_SCHEMAS, ToolResult
from app.providers.base import ChatResult, ModelProvider
from app.repositories.audit import append_event, finish_run, start_run


class AgentRuntime:
    def __init__(
        self, provider: ModelProvider, limits: BudgetLimits | None = None
    ) -> None:
        self.provider = provider
        self.limits = limits or BudgetLimits()

    def run(
        self, session: Session, persona: Persona, request: str,
        mode: str = "governed",
    ) -> AgentRunResult:
        run = start_run(
            session, persona.id, request, mode, self.provider.__class__.__name__
        )
        append_event(session, run.id, "request_received", {"request": request})
        budget = RunBudget(self.limits)
        messages = initial_messages(request)
        tool_results: list[ToolResult] = []
        untrusted_seen = False
        try:
            while not budget.exhausted:
                estimated = len(str(messages).split())
                budget.before_call(estimated)
                response = self.provider.chat(
                    messages, TOOL_SCHEMAS,
                    max_tokens=min(800, budget.remaining_output_tokens),
                )
                budget.after_call(response.input_tokens, response.output_tokens)
                self._record_model_call(session, run.id, response, budget)
                if not response.tool_calls:
                    return self._release(
                        session, run, response, budget, tool_results
                    )
                messages.append(assistant_message(response))
                for payload in response.tool_calls:
                    call_id, call = parse_tool_call(payload)
                    result = execute_tool(
                        session, persona, run.id, call, untrusted_seen
                    )
                    tool_results.append(result)
                    self._record_tool(session, run.id, call.name.value, result)
                    untrusted_seen = untrusted_seen or result.trust_level == "untrusted"
                    messages.append(tool_message(call_id, result))
                    if result.requires_approval:
                        return self._finish(
                            session, run, RunStatus.APPROVAL_REQUIRED,
                            budget, tool_results=tool_results
                        )
            raise BudgetExceeded("Agent budget exhausted")
        except BudgetExceeded as exc:
            append_event(session, run.id, "budget_stopped", {"reason": str(exc)})
            return self._finish(
                session, run, RunStatus.BUDGET_EXCEEDED, budget,
                tool_results=tool_results, blocked_reason=str(exc)
            )
        except Exception as exc:  # noqa: BLE001 - provider failures become audited run failures
            append_event(session, run.id, "run_failed", {"error": str(exc)})
            return self._finish(
                session, run, RunStatus.FAILED, budget,
                tool_results=tool_results, blocked_reason="Agent execution failed"
            )

    def _record_model_call(
        self, session: Session, run_id: str, response: ChatResult,
        budget: RunBudget,
    ) -> None:
        append_event(session, run_id, "model_call", {
            "input_tokens": response.input_tokens,
            "output_tokens": response.output_tokens,
            "tool_call_count": len(response.tool_calls),
            "step": budget.usage.steps,
        })

    def _record_tool(
        self, session: Session, run_id: str, tool_name: str, result: ToolResult
    ) -> None:
        append_event(session, run_id, "tool_decision", {
            "tool": tool_name,
            "status": result.status,
            "source_ids": result.source_ids,
            "requires_approval": result.requires_approval,
        })

    def _release(
        self, session: Session, run: Any, response: ChatResult,
        budget: RunBudget, tool_results: list[ToolResult],
    ) -> AgentRunResult:
        scan = scan_output(response.text, ("CANARY-BSTN-42",))
        if not scan.safe:
            append_event(session, run.id, "output_blocked", {
                "rules": [finding.rule for finding in scan.findings]
            })
            return self._finish(
                session, run, RunStatus.BLOCKED, budget,
                tool_results=tool_results, blocked_reason="Output policy blocked response"
            )
        append_event(session, run.id, "response_released", {
            "citation_count": len(response.citations)
        })
        return self._finish(
            session, run, RunStatus.COMPLETED, budget,
            answer=response.text, citations=response.citations,
            tool_results=tool_results
        )

    def _finish(
        self, session: Session, run: Any, status: RunStatus, budget: RunBudget,
        answer: str | None = None, citations: list | None = None,
        tool_results: list[ToolResult] | None = None,
        blocked_reason: str | None = None,
    ) -> AgentRunResult:
        usage = budget.usage
        finish_run(
            session, run, status.value, usage.input_tokens,
            usage.output_tokens, usage.steps
        )
        return AgentRunResult(
            run_id=run.id, status=status, answer=answer,
            citations=citations or [], tool_results=tool_results or [],
            usage=usage, blocked_reason=blocked_reason
        )
