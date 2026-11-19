from typing import Any

from sqlalchemy.orm import Session

from app.agent.messages import assistant_message, initial_messages, parse_tool_call, tool_message
