"""
Database engine and session helpers.
"""
from __future__ import annotations

import logging
import os

from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

from app.core.config import settings

logger = logging.getLogger(__name__)


def _normalize_database_url(database_url: str) -> str:
    if database_url.startswith("postgres://"):
        return database_url.replace("postgres://", "postgresql+psycopg://", 1)
    if database_url.startswith("postgresql://") and "+psycopg" not in database_url:
        return database_url.replace("postgresql://", "postgresql+psycopg://", 1)
    return database_url


DATABASE_URL = _normalize_database_url(settings.DATABASE_URL)

engine_kwargs = {
    "echo": False,
    "pool_pre_ping": True,
}

if DATABASE_URL.startswith("sqlite"):
    engine_kwargs["connect_args"] = {"check_same_thread": False}

    db_path = DATABASE_URL.replace("sqlite:///", "", 1)
    db_dir = os.path.dirname(db_path)
    if db_dir:
        os.makedirs(db_dir, exist_ok=True)
else:
    engine_kwargs.update(
        pool_size=settings.DB_POOL_SIZE,
        max_overflow=settings.DB_MAX_OVERFLOW,
        pool_timeout=settings.DB_POOL_TIMEOUT,
        pool_recycle=settings.DB_POOL_RECYCLE,
    )

engine = create_engine(DATABASE_URL, **engine_kwargs)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

POSTGRES_INIT_LOCK_ID = 42857831


def get_db():
    """Provide a request-scoped database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """Initialize database tables and local directories."""
    try:
        from app.models import recipe, user  # noqa: F401

        if DATABASE_URL.startswith("postgresql"):
            # Multiple Uvicorn workers can run startup concurrently. Serialize
            # table creation with a PostgreSQL advisory lock to avoid duplicate
            # catalog entries during first boot.
            with engine.begin() as connection:
                connection.exec_driver_sql(f"SELECT pg_advisory_lock({POSTGRES_INIT_LOCK_ID})")
                try:
                    Base.metadata.create_all(bind=connection)
                finally:
                    connection.exec_driver_sql(f"SELECT pg_advisory_unlock({POSTGRES_INIT_LOCK_ID})")
        else:
            Base.metadata.create_all(bind=engine)

        logger.info("Database tables are ready")

        os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
    except Exception as exc:
        logger.error("Database initialization failed: %s", exc)
        raise
