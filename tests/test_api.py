from collections.abc import Iterator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

import app.api.chat as chat_api
from app.database import get_session
from app.governance.tools import ToolCall, ToolName
from app.main import app
