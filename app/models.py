from datetime import UTC, datetime
from uuid import uuid4

from pgvector.sqlalchemy import Vector
from sqlalchemy import JSON, Boolean, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


def new_id() -> str:
    return str(uuid4())


def utc_now() -> datetime:
    return datetime.now(UTC)


class DemoUserRow(Base):
    __tablename__ = "demo_users"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    name: Mapped[str] = mapped_column(String(128))
    departments: Mapped[list[str]] = mapped_column(JSON)
    clearance: Mapped[int] = mapped_column(Integer)
    role: Mapped[str] = mapped_column(String(64))


class DocumentRow(Base):
    __tablename__ = "documents"

    id: Mapped[str] = mapped_column(String(64), primary_key=True, default=new_id)
    title: Mapped[str] = mapped_column(String(256))
    department: Mapped[str] = mapped_column(String(64), index=True)
    clearance: Mapped[int] = mapped_column(Integer, index=True)
    trust_level: Mapped[str] = mapped_column(String(32), default="internal")
    active: Mapped[bool] = mapped_column(Boolean, default=True, index=True)
    content: Mapped[str] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)


class ChunkRow(Base):
    __tablename__ = "chunks"

    id: Mapped[str] = mapped_column(String(64), primary_key=True, default=new_id)
    document_id: Mapped[str] = mapped_column(ForeignKey("documents.id"), index=True)
    ordinal: Mapped[int] = mapped_column(Integer)
    text: Mapped[str] = mapped_column(Text)
    embedding: Mapped[list[float] | None] = mapped_column(
        Vector(1024).with_variant(JSON, "sqlite"), nullable=True
    )


class AgentRunRow(Base):
    __tablename__ = "agent_runs"

    id: Mapped[str] = mapped_column(String(64), primary_key=True, default=new_id)
    user_id: Mapped[str] = mapped_column(String(64), index=True)
    request: Mapped[str] = mapped_column(Text)
    status: Mapped[str] = mapped_column(String(32), default="running")
    mode: Mapped[str] = mapped_column(String(32), default="governed")
    model_id: Mapped[str | None] = mapped_column(String(128), nullable=True)
    input_tokens: Mapped[int] = mapped_column(Integer, default=0)
    output_tokens: Mapped[int] = mapped_column(Integer, default=0)
    step_count: Mapped[int] = mapped_column(Integer, default=0)
