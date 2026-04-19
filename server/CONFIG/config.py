from pydantic_settings import BaseSettings
from datetime import timedelta
import os


class Settings(BaseSettings):
    """Конфигурация приложения"""
    
    # Database
    DATABASE_URL: str = "sqlite:///./lms.db"
    
    # JWT
    SECRET_KEY: str = os.getenv("SECRET_KEY", "your-secret-key-change-in-production")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    REFRESH_TOKEN_EXPIRE_DAYS: int = 30
    
    # CORS
    ALLOWED_ORIGINS: list = ["*"]
    
    # App
    APP_NAME: str = "LMS API"
    DEBUG: bool = os.getenv("DEBUG", "False") == "True"
    
    # Rate limiting
    RATE_LIMIT_ENABLED: bool = True
    RATE_LIMIT_REQUESTS: int = 100
    RATE_LIMIT_PERIOD: int = 60  # секунды
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
