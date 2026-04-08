"""
AEGIS Database Session Management
Provides session factory and context managers.
"""

from sqlalchemy.orm import sessionmaker, Session
from contextlib import contextmanager
from src.db.engine import engine

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@contextmanager
def get_db_session() -> Session:
    """Context manager for database sessions."""
    session = SessionLocal()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


def get_db():
    """FastAPI dependency injection compatible session getter."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
