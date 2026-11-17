from datetime import UTC, datetime, timedelta
import jwt
from fastapi import HTTPException, status
from app.config import settings
from app.personas import PERSONAS
def create_token(persona_id: str) -> str:
    expires = datetime.now(UTC) + timedelta(hours=1)
    payload = {"sub": persona_id, "exp": expires}
    return jwt.encode(payload, settings.jwt_secret, algorithm="HS256")
