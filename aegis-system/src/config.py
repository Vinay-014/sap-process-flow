import os
from pydantic_settings import BaseSettings
from pydantic import ConfigDict

class Settings(BaseSettings):
    model_config = ConfigDict(extra="ignore")

    GOOGLE_API_KEY: str = os.getenv("GOOGLE_API_KEY", "").strip()
    GROQ_API_KEY: str = os.getenv("GROQ_API_KEY", "").strip()
    TOGETHER_API_KEY: str = os.getenv("TOGETHER_API_KEY", "").strip()

    LLM_MODEL: str = os.getenv("LLM_MODEL", "gemini-2.5-flash").strip()
    RED_TEAM_THRESHOLD: float = float(os.getenv("RED_TEAM_THRESHOLD", "0.65").strip())

    @property
    def DATABASE_URL(self) -> str:
        # 1. If DATABASE_URL is explicitly set in env, use it
        env_url = os.getenv("DATABASE_URL", "").strip()
        if env_url:
            return env_url
            
        # 2. Otherwise, construct from parts (for Cloud Run secrets)
        db_user = os.getenv("DB_USER", "aegis").strip()
        db_pass = os.getenv("DB_PASSWORD", "aegis_secure_2024").strip()
        db_name = os.getenv("DB_NAME", "aegis_db").strip()
        db_host = os.getenv("DB_HOST", "127.0.0.1:5433").strip()

        # Cloud SQL uses Unix Sockets and requires pg8000 driver
        if "/cloudsql/" in db_host:
            return f"postgresql+pg8000://{db_user}:{db_pass}@/{db_name}?unix_sock={db_host}/.s.PGSQL.5432"
        else:
            # Local TCP connection
            return f"postgresql+psycopg2://{db_user}:{db_pass}@{db_host}/{db_name}"

settings = Settings()
