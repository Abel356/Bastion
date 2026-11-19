from typing import Any

from sqlalchemy.orm import Session

from app.agent.messages import assistant_message, initial_messages, parse_tool_call, tool_message
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
