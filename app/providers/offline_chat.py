from app.providers.base import ChatResult

DRAFT_PROMPT = "Draft an internal email to team@acme.example about tomorrow's review."


def tool_request(name: str, arguments: dict) -> ChatResult:
    return ChatResult(tool_calls=[{"id": f"offline-{name}", "name": name, "arguments": arguments}])
