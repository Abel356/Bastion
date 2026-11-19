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
) -> Persona:
    if not bastion_session:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Demo session required")
    persona_id = decode_token(bastion_session)
    return PERSONAS[persona_id]


PersonaDependency = Annotated[Persona, Depends(current_persona)]


def require_security(persona: PersonaDependency) -> Persona:
    if persona.role is not Role.SECURITY:
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Security role required")
    return persona


SecurityDependency = Annotated[Persona, Depends(require_security)]
