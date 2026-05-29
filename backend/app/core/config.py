from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

# Repo-root .env wins over backend/.env so a single file at the repo root works
# regardless of whether uvicorn is launched from backend/ or the repo root.
_REPO_ROOT_ENV = Path(__file__).resolve().parents[3] / ".env"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=(str(_REPO_ROOT_ENV), ".env"),
        case_sensitive=False,
        extra="ignore",
    )

    app_name: str = "DClaw Continuity"
    app_env: str = "dev"
    debug: bool = True

    database_url: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/dclaw_continuity"

    # Auth — JWT-signed sessions with bcrypt-hashed passwords.
    # AUTH_DEV_MODE accepts DEV_AUTH_TOKEN as a bypass; useful in tests/dev.
    auth_dev_mode: bool = True
    dev_auth_token: str = "dev-token"
    secret_key: str = "change-me-in-production-32-byte-dev-only-secret!"
    access_token_expire_minutes: int = 60 * 24  # 24h
    jwt_algorithm: str = "HS256"

    # LLM
    openrouter_api_key: str = ""
    openrouter_base_url: str = "https://openrouter.ai/api/v1"
    openrouter_model: str = "moonshotai/kimi-k2"

    ollama_base_url: str = "http://localhost:11434"
    ollama_model: str = "llama3.1"
    ollama_embed_model: str = "nomic-embed-text"

    llm_request_timeout: int = 60

    # RAG
    embedding_dim: int = 768
    rag_top_k: int = 5

    # Redis (cache / bus)
    # Disable by leaving redis_url empty — callers fall back to no-cache.
    redis_url: str = "redis://localhost:6379/0"
    redis_embed_cache_ttl_seconds: int = 60 * 60 * 24 * 7  # 7 days

    # Object storage (S3-compatible: MinIO locally, AWS S3 in prod).
    # Leave s3_endpoint_url empty to disable; attachment routes will return 503.
    s3_endpoint_url: str = "http://localhost:9000"
    s3_region: str = "us-east-1"
    s3_access_key_id: str = "minioadmin"
    s3_secret_access_key: str = "minioadmin"
    s3_bucket: str = "dclaw-continuity"
    s3_force_path_style: bool = True  # required for MinIO
    s3_presigned_url_ttl_seconds: int = 60 * 60  # 1 hour
    s3_max_upload_bytes: int = 20 * 1024 * 1024  # 20 MB


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
