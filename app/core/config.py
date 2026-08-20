from functools import lru_cache
from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

from app.core.db_url import normalize_database_url


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", case_sensitive=True, extra="ignore")

    APP_ENV: str = "development"
    APP_NAME: str = "Portfolio CMS API"
    DATABASE_URL: str
    # auto = SSL for remote/Supabase, off for localhost/docker; require | disable to force
    DATABASE_SSL: str = "auto"
    DB_POOL_SIZE: int = 5
    DB_MAX_OVERFLOW: int = 5
    JWT_SECRET_KEY: str = Field(min_length=32)
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    FRONTEND_URL: str = "http://localhost:5173"
    CORS_ORIGINS: str = "http://localhost:5173,http://localhost:3000,http://127.0.0.1:5173"
    ALLOWED_HOSTS: str = "localhost,127.0.0.1"

    @field_validator("DATABASE_URL", mode="before")
    @classmethod
    def normalize_db_url(cls, value):
        if isinstance(value, str):
            return normalize_database_url(value)
        return value

    @property
    def async_database_url(self) -> str:
        return normalize_database_url(self.DATABASE_URL)

    @property
    def cors_origins(self) -> list[str]:
        values = [self.FRONTEND_URL, *[x.strip() for x in self.CORS_ORIGINS.split(",")]]
        return list(dict.fromkeys([x for x in values if x]))

    IMAGEKIT_PUBLIC_KEY: str = ""
    IMAGEKIT_PRIVATE_KEY: str = ""
    IMAGEKIT_URL_ENDPOINT: str = ""

    EMAIL_PROVIDER: str = "smtp"
    EMAIL_API_KEY: str = ""
    EMAIL_FROM: str = ""
    ADMIN_EMAIL: str = ""
    SMTP_HOST: str = ""
    SMTP_PORT: int = 587
    SMTP_USERNAME: str = ""
    SMTP_PASSWORD: str = ""
    SMTP_USE_TLS: bool = True

    @field_validator("SMTP_USERNAME", "EMAIL_FROM", "ADMIN_EMAIL", mode="before")
    @classmethod
    def strip_email_fields(cls, value):
        return value.strip() if isinstance(value, str) else value

    @field_validator("SMTP_PASSWORD", mode="before")
    @classmethod
    def normalize_smtp_password(cls, value):
        if isinstance(value, str):
            return value.replace(" ", "")
        return value

    OTP_LENGTH: int = 6
    OTP_EXPIRE_MINUTES: int = 10
    OTP_MAX_ATTEMPTS: int = 5
    EMAIL_VERIFICATION_TOKEN_MINUTES: int = 30
    MAX_IMAGE_SIZE_MB: int = 10
    MAX_IMAGE_WIDTH: int = 2400
    MAX_IMAGE_HEIGHT: int = 2400
    IMAGE_QUALITY: int = 85

    OPENAI_API_KEY: str = ""
    OPENAI_CHAT_MODEL: str = "gpt-4o-mini"
    OPENAI_EMBEDDING_MODEL: str = "text-embedding-3-small"
    ANTHROPIC_API_KEY: str = ""
    GOOGLE_API_KEY: str = ""
    GROQ_API_KEY: str = ""
    MISTRAL_API_KEY: str = ""
    MISTRAL_EMBEDDING_MODEL: str = "mistral-embed"
    MISTRAL_EMBEDDING_DIMENSION: int = 1024
    PINECONE_API_KEY: str = ""
    PINECONE_INDEX_NAME: str = "portfolio-chatbot"
    PINECONE_NAMESPACE: str = "chatbot"
    PINECONE_CLOUD: str = "aws"
    PINECONE_REGION: str = "us-east-1"
    OPENROUTER_API_KEY: str = ""
    CHATBOT_STORAGE_DIR: str = "storage/chatbot"
    CHATBOT_MAX_FILE_MB: int = 25
    CHATBOT_CHUNK_SIZE: int = 800
    CHATBOT_CHUNK_OVERLAP: int = 120
    CHATBOT_TOP_K: int = 5
    CHATBOT_TEMPERATURE: float = 0.2
    CHATBOT_MAX_HISTORY_TURNS: int = 8
    CHATBOT_DEFAULT_PROVIDER: str = "openai"

    @field_validator(
        "OPENAI_API_KEY",
        "ANTHROPIC_API_KEY",
        "GOOGLE_API_KEY",
        "GROQ_API_KEY",
        "MISTRAL_API_KEY",
        "PINECONE_API_KEY",
        "OPENROUTER_API_KEY",
        mode="before",
    )
    @classmethod
    def strip_api_keys(cls, value):
        return value.strip() if isinstance(value, str) else value

    @property
    def allowed_hosts(self) -> list[str]:
        return [x.strip() for x in self.ALLOWED_HOSTS.split(",") if x.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
