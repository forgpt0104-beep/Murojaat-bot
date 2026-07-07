"""Application configuration loaded from environment variables (.env)."""

from __future__ import annotations

from pathlib import Path

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).resolve().parent.parent.parent


class Settings(BaseSettings):
    """Strongly typed application settings, populated from environment variables."""

    model_config = SettingsConfigDict(
        env_file=BASE_DIR / ".env",
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=False,
    )

    # --- Telegram ---
    BOT_TOKEN: str
    GROUP_ID: int
    SUPER_ADMIN_ID: int

    # --- Database ---
    DATABASE_URL: str

    # --- Logging ---
    LOG_LEVEL: str = "INFO"
    LOG_DIR: str = "logs"

    # --- Docker/Postgres bootstrap (not used directly by the bot) ---
    POSTGRES_USER: str = "support_bot"
    POSTGRES_PASSWORD: str = "support_bot_password"
    POSTGRES_DB: str = "support_bot"

    # --- Behaviour ---
    THROTTLE_RATE_LIMIT: float = 0.7
    MAX_ATTACHMENTS_PER_APPEAL: int = 20
    TIMEZONE: str = "Asia/Tashkent"

    @field_validator("LOG_LEVEL")
    @classmethod
    def validate_log_level(cls, value: str) -> str:
        allowed = {"DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"}
        upper = value.upper()
        if upper not in allowed:
            raise ValueError(f"LOG_LEVEL must be one of {allowed}, got {value!r}")
        return upper

    @property
    def logs_path(self) -> Path:
        path = BASE_DIR / self.LOG_DIR
        path.mkdir(parents=True, exist_ok=True)
        return path

    @property
    def exports_path(self) -> Path:
        path = BASE_DIR / "exports"
        path.mkdir(parents=True, exist_ok=True)
        return path


settings = Settings()
