from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from app.api.actions import router as actions_router
from app.api.audit import router as audit_router
from app.api.chat import router as chat_router
from app.api.session import router as session_router
from app.config import settings
from app.startup import lifespan

WEB_DIST = Path(__file__).resolve().parents[1] / "web" / "dist"

app = FastAPI(title=settings.app_name, version="0.1.0", lifespan=lifespan)
app.include_router(actions_router)
app.include_router(audit_router)
app.include_router(chat_router)
app.include_router(session_router)
@app.get("/health")
def health() -> dict[str, str]: return {"status": "ok"}
@app.get("/api/runtime")
def runtime_info() -> dict[str, str]:
    return {"provider": "cohere" if settings.cohere_api_key else "offline"}

@app.get("/", response_model=None)
def root() -> FileResponse | dict[str, str]:
    return FileResponse(WEB_DIST / "index.html") if (WEB_DIST / "index.html").is_file() else {"name": settings.app_name, "docs": "/docs"}
