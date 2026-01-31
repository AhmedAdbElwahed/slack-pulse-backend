from sqlmodel import create_engine, Session
from pydantic_settings import BaseSettings
import os


# 1. Define Settings to load from .env
class Settings(BaseSettings):
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL", "postgresql://postgres:password@localhost:5432/pulse_db"
    )
    REDIS_DB_URL: str = os.getenv("REDIS_DB_URL", "redis://localhost:6379/0")
    OLLAMA_BASE_URL: str = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434/v1")
    OLLAMA_MODEL: str = os.getenv("OLLAMA_MODEL", "llama3")

    class Config:
        env_file = ".env"


settings = Settings()

# 2. Create the Engine
# echo=True prints SQL queries to console (useful for debugging Phase 1)
engine = create_engine(settings.DATABASE_URL, echo=True)


# 3. Dependency for API endpoints
def get_session():
    with Session(engine) as session:
        yield session
