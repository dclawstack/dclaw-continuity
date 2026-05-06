from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    app_name: str = "DClaw Continuity"
    database_url: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/dclaw_continuity"
    cors_origins: str = "*"

    class Config:
        env_prefix = "CONTINUITY_"

settings = Settings()
