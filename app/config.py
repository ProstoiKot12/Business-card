from functools import lru_cache

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

from app.bot.text_catalog import text


class Settings(BaseSettings):
    bot_token: str = Field(alias="BOT_TOKEN")
    database_url: str = Field(alias="DATABASE_URL")
    redis_url: str = Field(alias="REDIS_URL")
    admin_ids: list[int] = Field(default_factory=list, alias="ADMIN_IDS")
    owner_id: int = Field(alias="OWNER_ID")
    owner_name: str = Field(default=text("system.owner_name.default"), alias="OWNER_NAME")
    owner_telegram_url: str = Field(default="", alias="OWNER_TELEGRAM_URL")
    owner_github_url: str = Field(default="", alias="OWNER_GITHUB_URL")
    owner_phone: str = Field(default="", alias="OWNER_PHONE")
    owner_max_url: str = Field(default="", alias="OWNER_MAX_URL")
    webapp_url: str = Field(default="https://localhost:8000/webapp", alias="WEBAPP_URL")
    log_level: str = Field(default="INFO", alias="LOG_LEVEL")

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    @field_validator("admin_ids", mode="before")
    @classmethod
    def parse_admin_ids(cls, value: object) -> list[int]:
        if value is None or value == "":
            return []
        if isinstance(value, list):
            return [int(item) for item in value]
        if isinstance(value, str):
            return [int(item.strip()) for item in value.split(",") if item.strip()]
        return [int(value)]


@lru_cache
def get_settings() -> Settings:
    return Settings()
