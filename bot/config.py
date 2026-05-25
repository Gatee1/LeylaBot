from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import SecretStr

class Settings(BaseSettings):
    BOT_TOKEN: SecretStr
    DATABASE_URL: str = "sqlite+aiosqlite:///db.sqlite3"
    
    # Timezone for reminders
    DEFAULT_TIMEZONE: str = "Europe/Moscow"
    
    # Goals
    DAILY_GOAL: int = 3
    
    API_BASE: str = "https://leyla.bothost.tech"
    
    model_config = SettingsConfigDict(
        env_file=".env", 
        env_file_encoding="utf-8",
        extra="ignore"
    )

config = Settings()
