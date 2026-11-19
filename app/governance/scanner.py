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


