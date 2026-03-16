"""
Application settings.
"""
from __future__ import annotations

import json
from typing import List, Optional

from pydantic import AliasChoices, Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Runtime settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=True,
        extra="ignore",
    )

    LLM_API_KEY: str = ""
    LLM_BASE_URL: str = Field(
        default="https://api-inference.modelscope.cn/v1",
        validation_alias=AliasChoices("LLM_BASE_URL", "LLM_API_BASE_URL", "DOUBAO_API_URL"),
    )
    MODEL_NAME: str = "Qwen/Qwen3.5-35B-A3B"
    IMAGE_MODEL_NAME: str = ""

    DATABASE_URL: str = "sqlite:///./dev.db"
    DB_POOL_SIZE: int = 5
    DB_MAX_OVERFLOW: int = 10
    DB_POOL_TIMEOUT: int = 30
    DB_POOL_RECYCLE: int = 1800

    UPLOAD_DIR: str = "./uploads"
    MAX_UPLOAD_SIZE: int = 10 * 1024 * 1024

    SECRET_KEY: str = "change-me-in-production"

    CORS_ORIGINS: List[str] = ["http://localhost:3000", "http://localhost:5173"]

    SESSION_COOKIE_NAME: str = "session_id"
    SESSION_COOKIE_DOMAIN: Optional[str] = None
    SESSION_COOKIE_SECURE: bool = False
    SESSION_COOKIE_SAMESITE: str = "lax"
    SESSION_COOKIE_MAX_AGE: int = 30 * 24 * 60 * 60

    LOG_LEVEL: str = "INFO"
    API_TIMEOUT: int = 120
    API_MAX_RETRIES: int = 2
    APP_ENV: str = "development"
    UVICORN_WORKERS: int = 2

    @field_validator("LLM_BASE_URL", mode="before")
    @classmethod
    def normalize_llm_base_url(cls, value: object) -> str:
        if not value:
            return "https://api-inference.modelscope.cn/v1"
        return str(value).strip().rstrip("/")

    @field_validator("CORS_ORIGINS", mode="before")
    @classmethod
    def parse_cors_origins(cls, value: object) -> List[str]:
        if value is None:
            return []

        if isinstance(value, list):
            return [str(item).strip() for item in value if str(item).strip()]

        if isinstance(value, str):
            raw_value = value.strip()
            if not raw_value:
                return []
            if raw_value.startswith("["):
                parsed = json.loads(raw_value)
                return [str(item).strip() for item in parsed if str(item).strip()]
            return [item.strip() for item in raw_value.split(",") if item.strip()]

        raise ValueError("Unsupported CORS_ORIGINS format")

    @field_validator("SESSION_COOKIE_SAMESITE")
    @classmethod
    def validate_samesite(cls, value: str) -> str:
        normalized = value.lower()
        if normalized not in {"lax", "strict", "none"}:
            raise ValueError("SESSION_COOKIE_SAMESITE must be lax, strict, or none")
        return normalized


settings = Settings()
