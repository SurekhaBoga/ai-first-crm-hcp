"""SQLAlchemy engine + session factory, and the FastAPI `get_db` dependency."""

from collections.abc import Generator

from sqlalchemy import create_engine, event
from sqlalchemy.orm import Session, sessionmaker

from app.core.config import settings

_is_sqlite = settings.DATABASE_URL.startswith("sqlite")

# SQLite needs check_same_thread=False to be used across FastAPI's request
# threads; Postgres (the production target) doesn't use this argument at all.
_connect_args = {"check_same_thread": False} if _is_sqlite else {}

engine = create_engine(
    settings.DATABASE_URL,
    echo=settings.DB_ECHO,
    pool_pre_ping=True,
    connect_args=_connect_args,
)

if _is_sqlite:
    # Unlike Postgres, SQLite doesn't enforce foreign keys (or their
    # ON DELETE CASCADE/SET NULL/RESTRICT clauses) unless told to per
    # connection. Without this, local/dev runs would silently behave
    # differently from production.
    @event.listens_for(engine, "connect")
    def _enable_sqlite_foreign_keys(dbapi_connection, _):
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
