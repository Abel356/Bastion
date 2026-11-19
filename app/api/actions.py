from collections.abc import Callable

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel

from app.api.dependencies import SecurityDependency, SessionDependency
from app.models import PendingActionRow
from app.repositories.actions import approve_action, list_pending_actions, reject_action

router = APIRouter(prefix="/api/actions", tags=["actions"])
