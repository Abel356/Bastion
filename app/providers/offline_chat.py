import json

from app.providers.base import ChatResult, Citation

DRAFT_PROMPT = "Draft an internal email to team@acme.example about tomorrow's review."


def offline_request(prompt: str) -> ChatResult:
    if prompt == DRAFT_PROMPT:
        return tool_request("propose_email", {"recipients": ["team@acme.example"], "subject": "Tomorrow’s review", "body": "Please bring your notes to tomorrow’s review."})
    return tool_request("search_documents", {"query": prompt})

def offline_evidence(content: list[dict], max_tokens: int) -> ChatResult:
    documents = [json.loads(item["document"]["data"]) for item in content if item["type"] == "document"]
    if not documents:
        return ChatResult(text="Offline demo: No authorized evidence matched this request.")
    return summarize(documents[0], max_tokens)
def tool_request(name: str, arguments: dict) -> ChatResult:
    return ChatResult(tool_calls=[{"id": f"offline-{name}", "name": name, "arguments": arguments}])
