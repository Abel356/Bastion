from fastapi import FastAPI

from app.api.actions import router as actions_router
from app.api.audit import router as audit_router
from app.api.chat import router as chat_router
from app.api.session import router as session_router
from app.config import settings
from app.startup import initialize_application

app = FastAPI(title=settings.app_name, version="0.1.0")
app.add_event_handler("startup", initialize_application)
app.include_router(actions_router)
app.include_router(audit_router)
app.include_router(chat_router)
app.include_router(session_router)
@app.get("/health")
def health() -> dict[str, str]: return {"status": "ok"}
@app.get("/")
def root() -> dict[str, str]: return {"name": settings.app_name, "docs": "/docs"}
