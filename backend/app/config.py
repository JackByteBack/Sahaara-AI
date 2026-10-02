"""Application configuration (Feature 1.10: privacy-first defaults)."""
from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    app_name: str = "Sahaara AI"
    database_url: str = "sqlite:///./sahaara.db"
    secret_key: str = "sahaara-dev-secret-change-me-0123456789abcdef-please-change"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 480

    # Generative AI (primary pipeline). Absent => rule-based fallback (Feature 1.14)
    openai_api_key: str = ""
    openai_model: str = "gpt-4o-mini"
    openai_base_url: str = "https://api.openai.com/v1"

    seed_demo_users: bool = True

    # Feature 1.10: raw audio is never retained in the default privacy workflow
    retain_raw_audio: bool = False


@lru_cache
def get_settings() -> Settings:
    return Settings()
