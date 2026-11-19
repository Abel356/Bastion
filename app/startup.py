from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.database import SessionLocal, create_schema
from app.ingestion import seed_corpus, seed_personas


def initialize_application() -> None:
    create_schema()
    with SessionLocal() as session:
        seed_personas(session)
        seed_corpus(session)
