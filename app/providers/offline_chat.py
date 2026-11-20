from app.providers.base import ChatResult

DRAFT_PROMPT = "Draft an internal email to team@acme.example about tomorrow's review."


def offline_request(prompt: str) -> ChatResult:
    if prompt == DRAFT_PROMPT:
        return tool_request("propose_email", {"recipients": ["team@acme.example"], "subject": "Tomorrow’s review", "body": "Please bring your notes to tomorrow’s review."})
    return tool_request("search_documents", {"query": prompt})

def tool_request(name: str, arguments: dict) -> ChatResult:
    return ChatResult(tool_calls=[{"id": f"offline-{name}", "name": name, "arguments": arguments}])
