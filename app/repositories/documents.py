from sqlalchemy import Select, or_, select
from sqlalchemy.orm import Session

from app.domain.document import DocumentLabel, TrustLevel
from app.domain.identity import Persona
