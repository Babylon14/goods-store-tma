from pydantic import PostgresDsn, RedisDsn, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # --- DATABASE ---
    POSTGRES_DB: str
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_HOST: str
    POSTGRES_PORT: str

    # Автоматическая сборка DATABASE_URL, если его нет в .env,
    # или используем готовый из файла.
    DATABASE_URL: str

    # --- REDIS & CELERY ---
    REDIS_URL: str

    # --- FASTAPI SETTINGS ---
    PROJECT_NAME: str
    SECRET_KEY: str
    ALGORITHM: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int

    # --- TELEGRAM ---
    BOT_TOKEN: str
    PAYMENT_PROVIDER_TOKEN: str
    MANAGER_ID: int

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"  # Игнорируем неизвестные ключи
    )

settings = Settings()

