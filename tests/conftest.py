from collections.abc import Iterator

import pytest
from sqlalchemy.orm import Session

from app import models  # noqa: F401
from app.database import Base, build_engine


@pytest.fixture
