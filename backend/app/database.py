"""SQLAlchemy engine/session setup. Works with SQLite (dev) and PostgreSQL (prod)."""
from sqlalchemy import JSON, create_engine
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import DeclarativeBase, sessionmaker

from .config import get_settings

settings = get_settings()

# JSONB on PostgreSQL, generic JSON elsewhere (tech-specs.md §2)
JSONType = JSON().with_variant(JSONB, "postgresql")

connect_args = {"check_same_thread": False} if settings.database_url.startswith("sqlite") else {}
engine = create_engine(settings.database_url, connect_args=connect_args, future=True)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, expire_on_commit=False)


class Base(DeclarativeBase):
    pass


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db() -> None:
    from . import models  # noqa: F401

    Base.metadata.create_all(bind=engine)
    _ensure_columns()


def _ensure_columns() -> None:
    """Lightweight migrations for columns added after a table was first created."""
    from sqlalchemy import inspect, text

    inspector = inspect(engine)
    try:
        existing = {col["name"] for col in inspector.get_columns("cases")}
    except Exception:
        return
    with engine.begin() as conn:
        if "assigned_to" not in existing:
            conn.execute(text("ALTER TABLE cases ADD COLUMN assigned_to VARCHAR(32)"))
