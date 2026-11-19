from typing import Any

from pydantic import ValidationError
from sqlalchemy.orm import Session

from app.domain.document import DocumentLabel, TrustLevel
from app.domain.identity import Persona
from app.domain.policy import can_read
from app.governance.policy import PolicyStatus, decide_tool
from app.governance.scanner import scan_untrusted
