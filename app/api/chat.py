from fastapi import APIRouter
from pydantic import BaseModel, Field

from app.agent.models import AgentRunResult
from app.agent.runtime import AgentRuntime
from app.api.dependencies import PersonaDependency, SessionDependency, require_security
from app.providers import get_provider

router = APIRouter(prefix="/api", tags=["agent"])


class ChatRequest(BaseModel):
    message: str = Field(min_length=1, max_length=4000)
    mode: str = Field(default="governed", pattern="^(governed|baseline)$")


@router.post("/chat", response_model=AgentRunResult)
def chat(
    request: ChatRequest, session: SessionDependency, persona: PersonaDependency
) -> AgentRunResult:
    if request.mode == "baseline":
        require_security(persona)
    runtime = AgentRuntime(get_provider())
    return runtime.run(session, persona, request.message, request.mode)
