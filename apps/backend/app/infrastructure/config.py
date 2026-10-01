"""Configuracion de la aplicacion via variables de entorno (ver .env.example)."""

from functools import lru_cache
from typing import Literal

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=("../../.env", ".env"),
        env_file_encoding="utf-8",
        extra="ignore",
    )

    environment: str = "development"
    deploy_mode: Literal["docker", "native"] = "native"

    backend_port: int = 3000
    backend_url: str = "http://localhost:3000"
    frontend_url: str = "http://localhost:5173"

    database_url: str = (
        "postgresql+psycopg://vibe_coding:vibe_coding@localhost:5433/vibe_coding_dev"
    )

    jwt_secret: str = "change-me-in-dev"
    jwt_algorithm: str = "HS256"
    jwt_access_expires_in: str = "15m"
    jwt_refresh_expires_in: str = "7d"

    ai_provider: Literal["mock", "anthropic"] = "mock"
    ai_api_key: str = ""
    ai_model: str = "claude-sonnet-5"
    ai_agent_max_iterations: int = 8
    ai_agent_max_tokens: int = 4000

    storage_provider: Literal["local", "minio", "s3"] = "local"
    storage_local_path: str = "./storage/uploads"
    storage_minio_endpoint: str = ""
    storage_minio_access_key: str = ""
    storage_minio_secret_key: str = ""
    storage_minio_bucket: str = "vibe-coding"
    storage_s3_bucket: str = ""
    storage_max_upload_mb: int = 10

    cors_allowed_origins: str = "http://localhost:5173"

    @field_validator("database_url")
    @classmethod
    def _normalize_database_url(cls, value: str) -> str:
        # Acepta DATABASE_URL=postgresql://... (formato comun en .env.example) y lo
        # normaliza al dialecto psycopg3 que usa SQLAlchemy en este proyecto.
        if value.startswith("postgresql://"):
            return value.replace("postgresql://", "postgresql+psycopg://", 1)
        return value

    @property
    def cors_origins_list(self) -> list[str]:
        return [o.strip() for o in self.cors_allowed_origins.split(",") if o.strip()]

    def jwt_expires_seconds(self, spec: str) -> int:
        """Convierte '15m' / '7d' / '3600s' a segundos."""
        unit = spec[-1]
        value = int(spec[:-1])
        factor = {"s": 1, "m": 60, "h": 3600, "d": 86400}.get(unit)
        if factor is None:
            raise ValueError(f"Formato de duracion invalido: {spec!r}")
        return value * factor

    @property
    def jwt_access_expires_seconds(self) -> int:
        return self.jwt_expires_seconds(self.jwt_access_expires_in)

    @property
    def jwt_refresh_expires_seconds(self) -> int:
        return self.jwt_expires_seconds(self.jwt_refresh_expires_in)


@lru_cache
def get_settings() -> Settings:
    return Settings()
