from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Bastion"
    environment: str = "development"
    cohere_api_key: str | None = None
    database_url: str = "sqlite:///./bastion.db"
    jwt_secret: str = "development-only-change-me-32-bytes"
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

settings = Settings()
