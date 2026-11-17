from fastapi import APIRouter, HTTPException, Response, status
from pydantic import BaseModel
from app.personas import PERSONAS
from app.security import create_token
router = APIRouter(prefix="/api", tags=["session"])
class PersonaView(BaseModel):
    id: str
    name: str
    departments: frozenset[str]
    clearance: int
    role: str

@router.get("/personas", response_model=list[PersonaView])
def list_personas() -> list: return list(PERSONAS.values())
@router.post("/session/{persona_id}")
def select_persona(persona_id: str, response: Response) -> dict[str, str]:
    if persona_id not in PERSONAS:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Persona not found")
    response.set_cookie("bastion_session", create_token(persona_id), httponly=True, samesite="lax")
    return {"persona_id": persona_id}
