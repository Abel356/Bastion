from collections.abc import Iterator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

import app.api.chat as chat_api
from app.database import get_session
from app.governance.tools import ToolCall, ToolName
from app.main import app
from app.personas import MAYA
from app.providers.local import LocalProvider
from app.repositories.actions import create_pending_action
from app.repositories.audit import append_event, start_run


@pytest.fixture
def api_client(session: Session) -> Iterator[TestClient]:
    def override_session() -> Iterator[Session]:
        yield session

    app.dependency_overrides[get_session] = override_session
    client = TestClient(app)
    yield client
    app.dependency_overrides.clear()


def select(client: TestClient, persona_id: str) -> None:
    response = client.post(f"/api/session/{persona_id}")
    assert response.status_code == 200
