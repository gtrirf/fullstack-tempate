from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field
from typing import List
from zoneinfo import ZoneInfo

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    bot_token: str = Field(alias="BOT_TOKEN")
    admins: List[int] = Field(default_factory=list, alias="ADMINS")
    timezone: str = Field(default="UTC", alias="TIMEZONE")

    backend_url: str = Field(default="http://backend:8000", alias="BACKEND_URL")
    bot_secret: str = Field(default="", alias="BOT_SECRET")
    redis_url: str = Field(default="redis://redis:6379/0", alias="REDIS_URL")

    @property
    def tz(self) -> ZoneInfo:
        return ZoneInfo(self.timezone)

settings = Settings()