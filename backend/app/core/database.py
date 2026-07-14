"""SQLAlchemy engine, session factory and declarative base."""
import uuid

from sqlalchemy import create_engine
from sqlalchemy import Enum as SAEnum
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy.types import CHAR, TypeDecorator

from app.core.config import settings

connect_args = {"check_same_thread": False} if settings.DATABASE_URL.startswith("sqlite") else {}
engine = create_engine(settings.DATABASE_URL, pool_pre_ping=True, future=True, connect_args=connect_args)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine, future=True)

Base = declarative_base()


def pg_enum(enum_class, name: str):
    """Builds a SQLAlchemy Enum column type that stores each Python enum
    member's *value* (e.g. "user") rather than its *name* (e.g. "USER").

    SQLAlchemy's default behaviour is to persist the member name, which
    silently breaks the moment the Postgres ENUM type (created in Alembic
    migrations using lowercase values) doesn't contain that name -- exactly
    the "invalid input value for enum" error this fixes. Every enum column
    in the app should use this helper instead of a bare Enum(...) so the
    Python-side and database-side representations always agree.
    """
    return SAEnum(enum_class, name=name, values_callable=lambda enum: [member.value for member in enum])


class GUID(TypeDecorator):
    """Platform-independent UUID column: uses PostgreSQL's native UUID type
    in production, and a 32-char hex string in SQLite (used by the test
    suite), so the same models work against both without changes."""

    impl = CHAR
    cache_ok = True

    def load_dialect_impl(self, dialect):
        if dialect.name == "postgresql":
            return dialect.type_descriptor(PG_UUID(as_uuid=True))
        return dialect.type_descriptor(CHAR(32))

    def process_bind_param(self, value, dialect):
        if value is None:
            return value
        if dialect.name == "postgresql":
            return str(value)
        if not isinstance(value, uuid.UUID):
            return uuid.UUID(value).hex
        return value.hex

    def process_result_value(self, value, dialect):
        if value is None:
            return value
        if isinstance(value, uuid.UUID):
            return value
        return uuid.UUID(value)


def get_db():
    """FastAPI dependency that yields a DB session and always closes it."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
