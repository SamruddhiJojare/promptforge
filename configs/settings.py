"""
Centralized app configuration, loaded from .env via pydantic-settings.
Import `settings` anywhere you need a config value instead of reading
os.environ directly — keeps everything in one place.
"""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    groq_api_key: str = ""
    llm_model: str = "llama-3.3-70b-versatile"

    database_url: str = "sqlite:///./promptforge.db"

    api_host: str = "127.0.0.1"
    api_port: int = 8000

    backend_url: str = "http://127.0.0.1:8000"


settings = Settings()