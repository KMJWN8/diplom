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

    # Session
    SESSION_NAME: str = "telegram_parser"

    model_config = SettingsConfigDict(
        env_file="../.env"
    )

settings = Settings()
