import re
from enum import StrEnum

from pydantic import BaseModel, Field


class FindingType(StrEnum):
    INSTRUCTION_OVERRIDE = "instruction_override"
    TOOL_INJECTION = "tool_injection"
    EXFILTRATION = "exfiltration"
    CANARY = "canary"


class ScanFinding(BaseModel):
    kind: FindingType
    rule: str
    matched_text: str
    severity: str = "high"


class ScanResult(BaseModel):
    safe: bool
    findings: list[ScanFinding] = Field(default_factory=list)


INJECTION_RULES = {
    FindingType.INSTRUCTION_OVERRIDE: (
        r"ignore\s+(all|any|the)?\s*(previous|prior|system)\s*(rules|instructions)?",
        r"override\s+(the\s+)?(system|developer|policy)",
        r"reveal\s+(the\s+)?system\s+prompt",
    ),
    FindingType.TOOL_INJECTION: (
        r"propose_email\s*\(",
        r"call\s+(the\s+)?(email|tool|function)",
        r"send\s+.*@",
    ),
    FindingType.EXFILTRATION: (
        r"https?://[^\s]+\?.*(data|secret|token)=",
        r"!\[[^\]]*\]\(https?://",
    ),
}

OUTPUT_RULES = {
    FindingType.CANARY: (r"CANARY-[A-Z0-9-]+",),
    FindingType.EXFILTRATION: (
        r"!\[[^\]]*\]\(https?://",
        r"https?://[^\s]+\?.*(data|secret|token)=",
    ),
}

