from fastapi import APIRouter
from pydantic import BaseModel, Field

from app.agent.models import AgentRunResult
from app.agent.runtime import AgentRuntime
from app.api.dependencies import PersonaDependency, SessionDependency
from app.providers import get_provider

router = APIRouter(prefix="/api", tags=["agent"])

