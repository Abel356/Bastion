from fastapi import APIRouter, HTTPException, Response, status
from pydantic import BaseModel
from app.personas import PERSONAS
from app.security import create_token
router = APIRouter(prefix="/api", tags=["session"])
