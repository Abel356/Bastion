from collections.abc import Generator
from sqlite3 import Connection

from sqlalchemy import create_engine, event
from sqlalchemy.engine import Engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker
from sqlalchemy.pool import StaticPool

from app.config import settings


class Base(DeclarativeBase):
    pass


def enable_sqlite_recursive_triggers(connection: Connection, _: object) -> None:
    # SQLite fires the audit delete guard during REPLACE only with this enabled.
    connection.execute("PRAGMA recursive_triggers = ON").close()


def build_engine(url: str) -> Engine:
    connect_args = {"check_same_thread": False} if url.startswith("sqlite") else {}
    if url.endswith("/:memory:"):
        database_engine = create_engine(url, connect_args=connect_args, poolclass=StaticPool)
    else:
        database_engine = create_engine(url, connect_args=connect_args, pool_pre_ping=True)
    if database_engine.dialect.name == "sqlite":
        event.listen(database_engine, "connect", enable_sqlite_recursive_triggers)
    return database_engine


engine = build_engine(settings.database_url)
SessionLocal = sessionmaker(bind=engine, expire_on_commit=False)


def get_session() -> Generator[Session, None, None]:
    with SessionLocal() as session:
        yield session


def create_schema() -> None:
    from app import models  # noqa: F401

    with engine.begin() as connection:
        Base.metadata.create_all(connection)
        if connection.dialect.name == "sqlite":
            for operation in ("UPDATE", "DELETE"):
                connection.exec_driver_sql(f"""
                    CREATE TRIGGER IF NOT EXISTS run_events_no_{operation.lower()}
                    BEFORE {operation} ON run_events
                    BEGIN
                        SELECT RAISE(ABORT, 'Run events are append-only');
                    END
                """)
