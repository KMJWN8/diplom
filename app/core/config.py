from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # Telegram API
    API_ID: int
    API_HASH: str
    PHONE_NUMBER: str

    # Postgres
    DB_HOST: str
    DB_PORT: int
    DB_USER: str
    DB_PASS: str
    DB_NAME: str

    REDIS_URL: str

    # Session
    SESSION_NAME: str = "telegram_parser"
    TG_SESSION_STRING: str | None = None

    model_config = SettingsConfigDict(
        env_file="/home/saryglar311/Projects/diplom-fastapi-refactored/.env"
    )


settings = Settings()
