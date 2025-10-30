import os

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # MongoDB
    mongodb_url: str = "mongodb://localhost:27017"
    mongodb_db_name: str = "telegram_parser"

    # Telegram API
    api_id: int
    api_hash: str
    phone_number: str

    # Session
    session_name: str = "telegram_parser"

    model_config = SettingsConfigDict(
        env_file="/home/saryglar311/Projects/diplom-fastapi/.env"
    )


settings = Settings()
