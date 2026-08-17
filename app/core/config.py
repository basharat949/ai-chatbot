from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables and the local env file."""

    database_url: str

    jwt_secret_key: str
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 15
    refresh_token_expire_days: int = 7
    llm_provider: str = "groq"
    groq_api_key: str
    groq_model: str = "openai/gpt-oss-120b"
    google_api_key: str
    gemini_model: str = "gemini-2.5-flash"
    chat_history_limit: int = 20

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings = Settings()
