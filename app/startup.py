from app.database import SessionLocal, create_schema
from app.ingestion import seed_corpus, seed_personas


def initialize_application() -> None:
