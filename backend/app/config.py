"""Application configuration using pydantic-settings."""

from pydantic import model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings."""

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    database_url: str = "sqlite+aiosqlite:///./todos.db"
    cors_origins: list[str] = ["http://localhost:5173", "http://localhost:3000"]

    auth_enabled: bool = False
    auth_username: str = "admin"
    auth_password: str = ""
    session_secret: str = ""
    session_ttl_minutes: int = 60
    session_cookie_secure: bool = True

    @model_validator(mode="after")
    def _require_credentials_when_auth_enabled(self) -> "Settings":
        if self.auth_enabled and not (self.auth_password and self.session_secret):
            raise ValueError("AUTH_PASSWORD and SESSION_SECRET must be set when AUTH_ENABLED is true")
        return self


settings = Settings()
