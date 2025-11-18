"""
Конфигурация приложения
"""
from typing import List, Optional, Union
from pydantic import AnyHttpUrl, field_validator
from pydantic_settings import BaseSettings
import secrets


class Settings(BaseSettings):
    # Основные настройки
    PROJECT_NAME: str = "AI Sales Assistant"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"
    
    # Безопасность
    SECRET_KEY: str = secrets.token_urlsafe(32)
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    ALGORITHM: str = "HS256"
    
    # CORS (можно переопределить через переменную окружения)
    BACKEND_CORS_ORIGINS: str = "http://localhost:3000,http://localhost:8000,https://*.ngrok.io,https://*.ngrok-free.app,https://*.trycloudflare.com"
    
    # База данных
    DATABASE_URL: str = "sqlite:///./data/ai_sales.db"
    REDIS_URL: Optional[str] = None  # Опционально, можно не использовать
    AUTO_CREATE_TABLES: bool = True
    
    # AI настройки
    OPENAI_API_KEY: Optional[str] = ""
    OPENAI_MODEL: str = "gpt-4"
    OPENAI_MAX_TOKENS: int = 2000
    
    # CRM интеграции
    HUBSPOT_API_KEY: Optional[str] = None
    PIPEDRIVE_API_KEY: Optional[str] = None
    SALESFORCE_CLIENT_ID: Optional[str] = None
    SALESFORCE_CLIENT_SECRET: Optional[str] = None
    
    # Телефония
    TWILIO_ACCOUNT_SID: Optional[str] = None
    TWILIO_AUTH_TOKEN: Optional[str] = None
    TWILIO_PHONE_NUMBER: Optional[str] = None
    
    # Email
    SMTP_HOST: Optional[str] = None
    SMTP_PORT: int = 587
    SMTP_USER: Optional[str] = None
    SMTP_PASSWORD: Optional[str] = None
    
    # Файловое хранилище
    AWS_ACCESS_KEY_ID: Optional[str] = None
    AWS_SECRET_ACCESS_KEY: Optional[str] = None
    AWS_BUCKET_NAME: Optional[str] = None
    AWS_REGION: str = "eu-central-1"
    
    # Мониторинг
    SENTRY_DSN: Optional[str] = None
    LOG_LEVEL: str = "INFO"
    
    # Ограничения
    MAX_LEADS_PER_USER: int = 10000
    MAX_MESSAGES_PER_DAY: int = 1000
    RATE_LIMIT_PER_MINUTE: int = 60
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
