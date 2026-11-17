from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    app_name: str = "Bastion"
    environment: str = "development"
