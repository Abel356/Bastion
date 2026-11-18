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
