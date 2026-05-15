import os
from typing import ClassVar
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", extra="ignore"
    )
    DATABASE_URL: str = (
        "postgresql+asyncpg://user:password@localhost:5432/abuela_empanadas"
    )
    SECRET_KEY: ClassVar[str] = os.getenv("SECRET_KEY", "changeme")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 480
    PROJECT_NAME: str = "Abuela Empanadas API"
    DEBUG: bool = False
    TEST_DATABASE_URL: str | None = None


settings = Settings()
