from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Bastion"
    environment: str = "development"
    cohere_api_key: str | None = None
    cohere_chat_model: str = "command-a-plus-05-2026"
    cohere_embed_model: str = "embed-v4.0"
    cohere_rerank_model: str = "rerank-v5.0-fast"
    database_url: str = "sqlite:///./bastion.db"
    jwt_secret: str = "development-only-change-me-32-bytes"
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

settings = Settings()
