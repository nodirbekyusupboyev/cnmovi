from typing import List
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    APP_NAME: str = "CNMOVI Cinema Ecosystem"
    ENVIRONMENT: str = "development"
    DEBUG: bool = True
    SECRET_KEY: str = "cnmovi-ultra-secret-jwt-key-change-in-production"

    # Dual-Engine Database: SQLite locally (0MB overhead) or PostgreSQL 16 in production
    DATABASE_URL: str = "sqlite+aiosqlite:///./cnmovi.db"
    REDIS_URL: str = ""

    # Telegram Bot & Mini App
    BOT_TOKEN: str = ""
    BOT_USERNAME: str = "cnmovi_bot"
    WEBAPP_URL: str = "http://localhost:5173"
    ADMIN_IDS: str = "123456789"

    # Telegram MTProto Streaming Bridge
    TG_API_ID: int = 0
    TG_API_HASH: str = ""
    STORAGE_CHANNEL_ID: int = -1001234567890

    # AI & External Metadata Parser
    GEMINI_API_KEY: str = ""
    TMDB_API_KEY: str = ""

    # Monetization & Growth
    STARS_ENABLED: bool = True
    PAYME_MERCHANT_ID: str = ""
    PAYME_SECRET_KEY: str = ""
    CLICK_SERVICE_ID: str = ""
    CLICK_MERCHANT_ID: str = ""
    CLICK_SECRET_KEY: str = ""
    INSTAGRAM_URL: str = "https://instagram.com/cnmovi_uz"

    model_config = SettingsConfigDict(
        env_file=(".env", "../.env"),
        env_file_encoding="utf-8",
        extra="ignore",
    )

    @property
    def admin_id_list(self) -> List[int]:
        result: List[int] = []
        for item in self.ADMIN_IDS.split(","):
            item = item.strip()
            if item.isdigit():
                result.append(int(item))
        return result


settings = Settings()
