from collections.abc import Iterator

import pytest
from sqlalchemy.orm import Session

from app import models  # noqa: F401
from app.database import Base, build_engine


@pytest.fixture
def session() -> Iterator[Session]:
    engine = build_engine("sqlite+pysqlite:///:memory:")
    Base.metadata.create_all(engine)
    with Session(engine) as database_session:
        yield database_session
    Base.metadata.drop_all(engine)
