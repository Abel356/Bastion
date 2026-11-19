from typing import Annotated

from fastapi import Cookie, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_session
from app.domain.identity import Persona, Role
from app.personas import PERSONAS
from app.security import decode_token

SessionDependency = Annotated[Session, Depends(get_session)]


def current_persona(
    bastion_session: Annotated[str | None, Cookie()] = None,
