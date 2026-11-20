from app.providers.base import ChatResult


def tool_request(name: str, arguments: dict) -> ChatResult:
    return ChatResult(tool_calls=[{"id": f"offline-{name}", "name": name, "arguments": arguments}])
