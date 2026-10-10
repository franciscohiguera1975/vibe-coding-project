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

    # --- Narracion TTS (ver docs/ai.md) ---
    # NARRATION_PROVIDER=mock habilita MockNarrationAdapter sin consumir servicios
    # externos (valor por defecto en dev/test, igual que AI_PROVIDER=mock).
    narration_provider: Literal["mock", "elevenlabs"] = "mock"
    elevenlabs_api_key: str = ""
    elevenlabs_voice_id: str = "JBFqnCBsd6RMkjVDRZzb"
    elevenlabs_model_id: str = "eleven_multilingual_v2"

    # --- RAG de validacion de silabos (ver docs/saturdays_ai/00-plan.md) ---
    # Generacion y embeddings son proveedores INDEPENDIENTES entre si y de
    # AI_PROVIDER (el del tutor) — ver docs/saturdays_ai/00-plan.md §3 y §5.
    # *_PROVIDER=mock habilita los adaptadores mock sin consumir servicios
    # externos (valor por defecto en dev/test, igual que AI_PROVIDER/
    # NARRATION_PROVIDER). El proveedor real por defecto es un vLLM + TEI
    # corridos en el HPC de CEDIA y tunelados al VPS via SSH inverso (no un
    # servicio permanente); RAG_BASE_URL/EMBEDDING_BASE_URL apuntan a esos
    # puertos tunelados. GitHub Models (u otro endpoint compatible con la API
    # de OpenAI) sirve de respaldo intercambiable cambiando solo esas dos
    # variables, sin tocar codigo.
    rag_llm_provider: Literal["mock", "openai_compatible"] = "mock"
    rag_base_url: str = ""
    rag_api_key: str = ""
    rag_chat_model: str = "Qwen/Qwen2.5-7B-Instruct"

    embedding_provider: Literal["mock", "tei"] = "mock"
    embedding_base_url: str = ""
    embedding_model: str = "intfloat/multilingual-e5-large"

    # Chunks + embeddings de la normativa viven en una tabla LanceDB embebida
    # (co-ubicada con este proceso, no en el HPC — ver docs/saturdays_ai/00-plan.md
    # §5) en vez de Postgres JSONB; mismo patron que storage_local_path.
    lancedb_path: str = "./storage/lancedb"

    storage_provider: Literal["local", "minio", "s3"] = "local"
    storage_local_path: str = "./storage/uploads"
    storage_minio_endpoint: str = ""
    storage_minio_access_key: str = ""
    storage_minio_secret_key: str = ""
    storage_minio_bucket: str = "vibe-coding"
    storage_s3_bucket: str = ""
    storage_max_upload_mb: int = 10

    cors_allowed_origins: str = "http://localhost:5173"

    email_provider: Literal["console", "smtp"] = "console"
    smtp_host: str = ""
    smtp_port: int = 587
    smtp_user: str = ""
    smtp_password: str = ""
    smtp_from: str = "no-reply@vibecoding-platform.dev"
    smtp_use_tls: bool = True
    password_reset_token_expires_in: str = "1h"

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

    @property
    def password_reset_token_expires_seconds(self) -> int:
        return self.jwt_expires_seconds(self.password_reset_token_expires_in)


@lru_cache
def get_settings() -> Settings:
    return Settings()
