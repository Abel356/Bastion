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


def scan_rules(text: str, rules: dict[FindingType, tuple[str, ...]]) -> ScanResult:
    findings: list[ScanFinding] = []
    for kind, patterns in rules.items():
        for pattern in patterns:
            match = re.search(pattern, text, flags=re.IGNORECASE)
            if match:
                findings.append(ScanFinding(
                    kind=kind, rule=pattern, matched_text=match.group(0)
                ))
    return ScanResult(safe=not findings, findings=findings)


def scan_untrusted(text: str) -> ScanResult:
    return scan_rules(text, INJECTION_RULES)


def scan_output(text: str, restricted_markers: tuple[str, ...] = ()) -> ScanResult:
    result = scan_rules(text, OUTPUT_RULES)
    for marker in restricted_markers:
        if marker and marker.lower() in text.lower():
            result.findings.append(ScanFinding(
                kind=FindingType.EXFILTRATION,
                rule="restricted_marker",
                matched_text=marker,
            ))
    result.safe = not result.findings
    return result
