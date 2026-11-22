from collections.abc import Iterator
from pathlib import Path

import pytest
from sqlalchemy.orm import Session, sessionmaker

from app import (
    database,
    models,  # noqa: F401
)
from app.database import Base, build_engine


@pytest.fixture
def session() -> Iterator[Session]:
    engine = build_engine("sqlite+pysqlite:///:memory:")
    Base.metadata.create_all(engine)
    with Session(engine) as database_session:
        yield database_session
    Base.metadata.drop_all(engine)


@pytest.fixture
def file_sessions(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> Iterator[sessionmaker[Session]]:
    engine = build_engine(f"sqlite:///{(tmp_path / 'bastion.db').as_posix()}")
    monkeypatch.setattr(database, "engine", engine)
    try:
        database.create_schema()
        yield sessionmaker(engine)
    finally:
        engine.dispose()
