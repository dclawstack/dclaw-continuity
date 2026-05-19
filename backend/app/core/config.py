from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=False,
        extra="ignore",
    )

    app_name: str = "DClaw Continuity"
    app_env: str = "dev"
    debug: bool = True

    database_url: str = (
        "postgresql+asyncpg://postgres:postgres@localhost:5432/dclaw_continuity"
    )

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


@lru_cache()
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
