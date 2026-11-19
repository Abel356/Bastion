from datetime import datetime

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel

from app.api.dependencies import SecurityDependency, SessionDependency
from app.models import AgentRunRow, RunEventRow
from app.repositories.audit import list_events, list_recent_runs

router = APIRouter(prefix="/api/audit", tags=["audit"])
