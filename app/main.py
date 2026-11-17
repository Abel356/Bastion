from fastapi import FastAPI

from app.api.session import router as session_router
from app.config import settings

app = FastAPI(title=settings.app_name, version="0.1.0")
app.include_router(session_router)
@app.get("/health")
def health() -> dict[str, str]: return {"status": "ok"}
@app.get("/")
def root() -> dict[str, str]: return {"name": settings.app_name, "docs": "/docs"}
