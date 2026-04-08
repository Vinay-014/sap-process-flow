"""
AEGIS Database Engine
"""

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from src.config import settings
import logging

logger = logging.getLogger("aegis.db")

# Get the dynamically constructed URL
_db_url = settings.DATABASE_URL

# Determine if we are in Cloud Run
is_cloud_run = "cloudsql" in _db_url

if is_cloud_run:
    # Cloud Run: Smaller pool, pg8000 driver
    engine = create_engine(
        _db_url,
        pool_size=5,
        max_overflow=10,
        pool_timeout=30,
        pool_recycle=300,
        pool_pre_ping=True,
        echo=False,
    )
else:
    # Local: Larger pool, psycopg2 driver
    engine = create_engine(
        _db_url,
        pool_size=20,
        max_overflow=40,
        pool_timeout=30,
        pool_recycle=1800,
        pool_pre_ping=True,
        echo=False,
    )

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def init_db():
    from src.db.models import Base
    try:
        with engine.begin() as conn:
            result = conn.execute(text(
                "SELECT extname FROM pg_extension WHERE extname IN ('vector', 'postgis', 'uuid-ossp')"
            ))
            found = [row[0] for row in result.fetchall()]
            missing = set(['vector', 'postgis', 'uuid-ossp']) - set(found)
            if missing:
                logger.warning(f"Missing extensions: {missing}. Skipping tables that require them.")
                # If extensions are missing, we can't create all tables. 
                # For local dev without pgvector/postgis, we might need to skip specific tables
                # or just warn and hope the user doesn't use those features.
                # However, SQLAlchemy will fail on create_all if the type doesn't exist.
            else:
                logger.info("All PostgreSQL extensions verified.")

        # If extensions are missing, create_all will fail on vector columns.
        # To support local dev without extensions, we would need conditional table creation.
        # For now, we raise the error so the user knows to install extensions or use Docker.
        Base.metadata.create_all(bind=engine)
        logger.info("Database initialized successfully")
        return True
    except Exception as e:
        logger.error(f"Database init failed: {e}")
        # Don't raise, allow app to start (but DB will be broken for some features)
        return False

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

async def health_check() -> dict:
    try:
        with engine.connect() as conn:
            result = conn.execute(text("SELECT 1"))
            result.fetchone()
        return {"status": "healthy", "database": "connected"}
    except Exception as e:
        return {"status": "unhealthy", "error": str(e)}